import os
import sqlite3
import pandas as pd

def import_csv_to_sqlite(db_path, table_name, csv_path):
    try:
        df = pd.read_csv(csv_path)
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Imported {len(df)} rows into '{table_name}' table.")
        conn.close()

    except Exception as e:
        print(f"Error importing {csv_path} into {table_name}: {e}")

def main():
    db_path = os.path.abspath(os.path.join("..", "db", "mlb_data.db"))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #Drop old tables to fully reset
    tables_to_drop = ["events", "statistics"]
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
        except Exception as e:
            print(f"Couldn't drop {table}: {e}")

    # Load cleaned data
    data_dir = os.path.abspath(os.path.join("..", "data"))
    events_df = pd.read_csv(os.path.join(data_dir, "events_cleaned.csv"))
    stats_df = pd.read_csv(os.path.join(data_dir, "statistics_cleaned.csv"))

    # Input the cleaned data to the database
    events_df.to_sql("events_cleaned", conn, if_exists="replace", index=False)
    stats_df.to_sql("statistics_cleaned", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
    print("Cleaned data successfully imported into mlb_data.db")

if __name__ == "__main__":
    main()