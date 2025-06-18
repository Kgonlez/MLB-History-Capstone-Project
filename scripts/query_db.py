import sqlite3
import os

def connect_db():
    db_path = os.path.abspath(os.path.join("..", "db", "mlb_data.db"))
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def show_menu():
    print("\n=== Baseball Stats Query Menu ===")
    print("1. List all years available")
    print("2. Search events by year")
    print("3. Search player statistics by player name")
    print("4. Join: Show player stats with event details by year")
    print("5. Exit")

def list_years(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT year FROM events_cleaned ORDER BY year;")
    years = cursor.fetchall()
    print("\nAvailable Years:")
    for y in years:
        print(f"- {y[0]}")

def search_events_by_year(conn):
    year = input("Enter year: ")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM events_cleaned WHERE year = ?;", (year,))
        rows = cursor.fetchall()
        print(f"\nEvents in {year}:")
        for row in rows:
            print(f"- {row[1]}")
    except Exception as e:
        print("Error:", e)

def search_player_stats(conn):
    name = input("Enter full or partial player name: ")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT year, Statistic, Name, Team, stat_value FROM statistics_cleaned
            WHERE Name LIKE ? ORDER BY year;
        """, (f"%{name}%",))
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"{row['year']} | {row['Statistic']}: {row['Name']} ({row['Team']}) — {row['stat_value']}")
        else:
            print("No results found.")
    except Exception as e:
        print("Error:", e)

def join_stats_with_events(conn):
    year = input("Enter year for join query: ")
    player = input("Enter full or partial player name: ")
    cursor = conn.cursor()
    try:
        # Get stats for that player and year
        cursor.execute("""
            SELECT year, Name, Statistic, stat_value, Team
            FROM statistics_cleaned
            WHERE year = ? AND Name LIKE ?
        """, (year, f"%{player}%"))
        player_rows = cursor.fetchall()

        if not player_rows:
            print(f"No stats found for {player.title()} in {year}.")
            return

        print(f"\n=== Player Stats for {player.title()} in {year} ===")
        teams = set()
        
        for row in player_rows:
            print(f"{row[0]} | {row[1]} - {row[2]}: {row[3]} ({row[4]})")
            teams.add(row[4])  # collect team names

        # Try matching team name in the events' detail text
        print(f"\n=== Related Events in {year} Mentioning Player's Team ===")
        for team in teams:
            cursor.execute("""
                SELECT event_detail FROM events_cleaned
                WHERE year = ? AND event_detail LIKE ?
                LIMIT 5;
            """, (year, f"%{team}%"))
            event_rows = cursor.fetchall()

            if event_rows:
                print(f"\n--- Events mentioning '{team}' ---")
                for i, row in enumerate(event_rows, 1):
                    print(f"{i}. {row[0]}")
            else:
                print(f"\nNo events found mentioning team '{team}' in {year}.")

    except Exception as e:
        print("Error:", e)

def main():
    conn = connect_db()
    while True:
        show_menu()
        choice = input("Choose an option (1–5): ").strip()
        if choice == "1":
            list_years(conn)
        elif choice == "2":
            search_events_by_year(conn)
        elif choice == "3":
            search_player_stats(conn)
        elif choice == "4":
            join_stats_with_events(conn)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid input. Please enter a number from 1–5.")
    conn.close()

if __name__ == "__main__":
    main()
