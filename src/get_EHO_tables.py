from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By

def extract_tables_with_selenium(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode
    driver = webdriver.Chrome(options=options)  # Make sure you have chromedriver installed

    driver.get(url)
    tables = driver.find_elements(By.CLASS_NAME, 'content')

    dataframes = []
    for table in tables:
        html = table.get_attribute('outerHTML')
        df = pd.read_html(html)[0]
        dataframes.append(df)

    driver.quit()
    return dataframes


webpage_url = 'https://www.arlingtonva.us/Government/Programs/Building/Permits/EHO/Tracker'
dataframes = extract_tables_with_selenium(webpage_url)

for idx, df in enumerate(dataframes):
    print(f"Table {idx + 1}:")
    print(df)
    print("\n")

