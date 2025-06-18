import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

#-----SCRAPING YEARS & URL-----

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_years():
    url="https://www.baseball-almanac.com/yearmenu.shtml"
    driver = create_driver()
    driver.get(url)
    time.sleep(3)

    year_elements = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td a")

    years=[]

    for elem in year_elements:
        year_text = elem.text.strip()
        href= elem.get_attribute("href")
        if year_text.isdigit():
            years.append({
                "year": int(year_text),
                "url":href })
    driver.quit()
    
    os.makedirs("data", exist_ok= True)
    df_years = pd.DataFrame(years)
    df_years.to_csv("../data/years.csv", index= False)
    print(f"Scraped {len(years)} years. Saved to data/years.csv")

if __name__ == "__main__":
    scrape_years()
