import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_year_details(year, url, driver):
    driver.get(url)
    time.sleep(2)

    #-----SCRAPE EVENTS-----
    events = []
    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    for p in paragraphs:
        text = p.text.strip()
        if text:
            events.append({
                "year": year,
                "event_detail": text
            })

    #-----SCRAPE STATISTICS TABLES-----
    tables_data = []
    divs = driver.find_elements(By.CLASS_NAME, "ba-table")

    for div in divs:
        try:
            table_title = div.find_element(By.TAG_NAME, "h2").text.strip()
            table_element = div.find_element(By.TAG_NAME, "table")
            rows = table_element.find_elements(By.TAG_NAME, "tr")

            if len(rows) < 3:
                print(f"Skipping table {table_title} in {year} because not enough rows")
                continue

            # Get header cells from second row
            header_row = rows[1]
            header_cells = header_row.find_elements(By.TAG_NAME, "th")
            if not header_cells:
                header_cells = header_row.find_elements(By.TAG_NAME, "td")

            headers = [cell.text.strip() for cell in header_cells]

            if not headers:
                print(f"Skipping table {table_title} in {year} due to no headers found")
                continue

            # Get data rows starting from third <tr>
            data_rows = rows[2:]

            table = []
            for row in data_rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                table.append([cell.text.strip() for cell in cells])

            df = pd.DataFrame(table, columns=headers)
            df["year"] = year
            df["table_name"] = table_title
            tables_data.append(df)

        except Exception as e:
         print(f"Skipped one table in {year}: {e}")

    return events, tables_data

def main():
    # Load and filter years from 2015 to 2025
    years_df = pd.read_csv("../data/years.csv")
    filtered_df = years_df[years_df["year"].between(2015, 2025)]

    os.makedirs("data", exist_ok=True)

    driver = create_driver()
    all_events = []
    all_stats = []

    for _, row in filtered_df.iterrows():
        year = row["year"]
        url = row["url"]
        print(f"Scraping {year}...")

        try:
            events, stat_tables = scrape_year_details(year, url, driver)
            all_events.extend(events)
            all_stats.extend(stat_tables)
        except Exception as e:
            print(f"Failed to scrape {year}: {e}")

    driver.quit()

    #-----Save Events-----
    if all_events:
        pd.DataFrame(all_events).to_csv("../data/events_summary.csv", index=False)
        print("Saved all events to data/events_summary.csv")

    #-----Save Statistics-----
    if all_stats:
        combined_stats = pd.concat(all_stats, ignore_index=True)
        combined_stats.to_csv("../data/statistics_combined.csv", index=False)
        print("Saved all statistics to data/statistics_combined.csv")

    print("Done scraping all years.")


if __name__ == "__main__":
    main()