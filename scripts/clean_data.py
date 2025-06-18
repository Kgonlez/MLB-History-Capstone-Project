import pandas as pd
import os

def summarize(df, name):
    print(f"\n--- {name.upper()} SUMMARY ---")
    print("Shape:", df.shape)
    print("Missing values:\n", df.isnull().sum())
    print("Duplicates:", df.duplicated().sum())
    print(df.dtypes)

def clean_events(df):
    # Drop duplicates and missing values
    df = df.drop_duplicates()
    df = df.dropna(subset=["event_detail"])
    
    # Strip whitespace
    df["event_detail"] = df["event_detail"].str.strip()

    # Define filters for known non-event phrases
    def is_valid_event(event):
        summary_keywords = [
            "Statistics League", 
            "Team Standings", 
            "World Series", 
            "All-Star Game",
            "Copyright",
            "All Rights Reserved",
            "Baseball Almanac"
        ]
        
        # Remove events that include any of these summary/footer phrases
        if any(keyword.lower() in event.lower() for keyword in summary_keywords):
            return False
        
        # Remove rows with multiple sections separated by "|"
        if "|" in event and len(event.split("|")) > 1:
            return False
        
        return True

    # Apply filter
    df = df[df["event_detail"].apply(is_valid_event)]

    return df

def clean_statistics(df):
    df = df.drop_duplicates()

    # Filter to only relevant "Player Review" tables
    df = df[df['table_name'].str.contains("player review", case=False, na=False)]

    # Strip whitespace
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # Drop rows that look like headers or footnotes
    df = df[df["Statistic"].str.lower() != "statistic"]
    df = df[~df["Statistic"].str.contains("History|Standings", case=False, na=False)]

    # Remove rows with nulls in key columns
    df = df.dropna(subset=["Statistic", "Name", "Team"])

    # Rename '#' to 'stat_value'
    if "#" in df.columns:
        df = df.rename(columns={"#": "stat_value"})
        df["stat_value"] = pd.to_numeric(df["stat_value"], errors="coerce")

    # Drop rows where stat_value is still NaN (e.g., if malformed)
    df = df.dropna(subset=["stat_value"])

    # Keep only desired columns, dropped Top 25 because it was blank
    keep_cols = ["Statistic", "Name", "Team", "stat_value", "year", "table_name"]
    for col in keep_cols:
        if col not in df.columns:
            df[col] = None  # ensure column exists

    df = df[keep_cols]

    return df

def main():
    data_dir = "../data"

    # Load original CSVs
    events_df = pd.read_csv(os.path.join(data_dir, "events_summary.csv"))
    stats_df = pd.read_csv(os.path.join(data_dir, "statistics_combined.csv"))

    # Show BEFORE cleaning
    summarize(events_df, "events (before)")
    summarize(stats_df, "statistics (before)")

    # CLEAN
    events_clean = clean_events(events_df)
    stats_clean = clean_statistics(stats_df)

    # Show AFTER cleaning
    summarize(events_clean, "events (after)")
    summarize(stats_clean, "statistics (after)")

    # Save to /data
    events_clean.to_csv(os.path.join(data_dir, "events_cleaned.csv"), index=False)
    stats_clean.to_csv(os.path.join(data_dir, "statistics_cleaned.csv"), index=False)

    print(f"\nCleaned data saved in: {data_dir}")

if __name__ == "__main__":
    main()


