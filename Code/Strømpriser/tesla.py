import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import chromedriver_autoinstaller
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
from selenium.webdriver.common.keys import Keys
from openpyxl import load_workbook
import requests
from datetime import datetime
# from pyvirtualdisplay import Display
# import logging
from prefect import flow, task
import undetected_chromedriver as uc 
# import zipfile
import os
# import subprocess
from ftplib import FTP

@flow(name="Finn.no Electric Cars Scrape - Tesla")
def main_flow():
    # Configure logging
    # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Download excel file, tesla.xlsx from pythonanywhere
    # URL of the Excel file hosted on PythonAnywhere
    excel_url = "/home/andsande/mysite/templates/tesla.xlsx"

    # Your PythonAnywhere username and API token
    username = os.getenv('PYTHONANYWHERE_USERNAME')
    api_token = os.getenv('PYTHONANYWHERE_API')

    # Define the file path on PythonAnywhere to download
    pythonanywhere_file_path = '/home/andsande/mysite/templates/tesla.xlsx'

    # Define the download URL
    download_url = f'https://www.pythonanywhere.com/api/v0/user/{username}/files/path{pythonanywhere_file_path}'

    # Define headers with API token
    headers = {
        'Authorization': f'Token {api_token}'
    }

    # Make HTTP GET request to download the file
    response = requests.get(download_url, headers=headers)

    # Check if the download was successful
    if response.status_code == 200:
        # Save the downloaded file
        with open('./tesla.xlsx', 'wb') as file:
            file.write(response.content)
        print('File downloaded successfully.')
    else:
        print('Failed to download the file.')

    #Display running
    # display = Display(visible=0, size=(1920, 1080))
    # display.start()
    # -----------------------------------Start data scrape-----------
    #Model 3
    print("Model 3")

    # Install the latest version of ChromeDriver
    chromedriver_autoinstaller.install()

    # Configure Chrome options
    chrome_options = webdriver.ChromeOptions()    

    # Add your options as needed
    options = [
        # "--window-size=1920,1080",
        # '--proxy-server=http://%s' % PROXY,
        # "--ignore-certificate-errors",
        "--headless",
        "--disable-search-engine-choice-screen"
        # "--disable-popup-blocking"
        # "--disable-notifications"
    ]

    for option in options:
        chrome_options.add_argument(option)


        # chrome_options.add_argument('--allow-running-insecure-content')
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--no-sandbox")

    # Create a new instance of the Chrome driver with options
    # driver = webdriver.Chrome(options=chrome_options)
    # Initializing driver 
    driver = uc.Chrome(options=chrome_options) 

    # try:
    #     logging.info("Attempting to load webpage.")
    #     driver.get("https://www.finn.no/car/used/search.html?model=1.8078.2000501&page=1")
    #     logging.info("Webpage loaded successfully.")
    # except TimeoutException:
    #     logging.error("Failed to load webpage due to a timeout.", exc_info=True)
    # except Exception as e:
    #     logging.error(f"An error occurred: {e}", exc_info=True)
    # finally:
    #     driver.quit()
    #     logging.info("WebDriver has been closed.")

    # Navigate to a webpage
    driver.get("https://www.finn.no/car/used/search.html?model=1.8078.2000501&page=1")
    time.sleep(4)
    try:
        # Locate the iframe using an XPath expression that matches IDs starting with "sp_message_iframe_"
        iframe = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//iframe[starts-with(@id, 'sp_message_iframe_')]"))
        )
        driver.switch_to.frame(iframe)

        # Find and click the "Godta alle" button
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Godta alle"]'))
        )
        button.click()
    except TimeoutException:
        print(f"No cookies button found. Continuing without accepting cookies.")

    driver.switch_to.default_content()

    # Step 1: Read Existing Data from Excel
    excel_path = "./tesla.xlsx"
    try:
        existing_df = pd.read_excel(excel_path, sheet_name='model3')
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=["Name", "Year", "Mileage", "Price", "Timestamp"])  # Assuming these are your columns
        
    # Initialize empty lists to store data
    data_element1 = []
    data_element2 = []
    data_element3 = []
    data_element4 = []
    click_count = 0

    while True:
        driver.get(f"https://www.finn.no/car/used/search.html?model=1.8078.2000501&page={click_count + 1}")
        WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, f"//body/div[@id='__next']/main[1]/div[1]/div[2]/section[2]/div[3]/article[2]/div[3]/h2[1]/a[1]"))
        )
        for article_nr in range(2, 99):
            element1_successful = False  # Flag to indicate if element1 is successfully scraped for the current article
            element2_successful = False  # Flag to indicate if element2 is successfully scraped for the current article

            try:
                element1 = driver.find_element(By.XPATH, f"//body/div[@id='__next']/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]")
                # element1 = driver.find_element(By.XPATH, f"/html[1]/body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]/span[1]")
                # element1 = driver.find_element(By.XPATH, f"/html[1]/body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]")
                text1 = element1.text
                element1_successful = True  # Set the flag to True if element1 is successfully scraped
            except (NoSuchElementException, StaleElementReferenceException):
                continue

            try:
                element4 = driver.find_element(By.XPATH, f"(//div[contains(@class,'flex flex-col text-12')])[{article_nr}]")
                text4 = element4.text
            except (NoSuchElementException, StaleElementReferenceException):
                continue

            try:
                # Try finding the element using the first XPath
                element2 = driver.find_element(By.XPATH, f"//body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/div[3]")
                text2 = element2.text.split('\n')
                if len(text2) == 3:
                    year, mileage, price = text2
                    element2_successful = True  # Set the flag to True if element2 is successfully scraped
                else:
                    # Handle , cases where there might be missing data      //body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[46]/div[3]/div[2]/span[1]
                    element3 = driver.find_element(By.XPATH, f"//body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/div[4]")
                    text2 = element3.text.split('\n')
                    if len(text2) == 3:
                        year, mileage, price = text2
                        element2_successful = True  # Set the flag to True if element2 is successfully scraped
                    else:
                        print("Error: No data found")
            except NoSuchElementException:
                continue  # If both XPaths fail, continue to the next article
            
            # Append data only if both elements are successfully scraped
            if element1_successful and element2_successful:
                data_element1.append(text1)
                data_element2.append((year, mileage, price))
                data_element3.append(text4)
                #Scraping number of listed cars
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='flex-shrink-0']"))
                    )
                listed_cars = driver.find_element(By.CSS_SELECTOR, "div[class='flex-shrink-0']")
                cars = listed_cars.text
                integer_part = re.search(r'\d+', cars).group()

                # Convert the integer part to an actual integer
                listed_cars = int(integer_part)
                data_element4.append(listed_cars)
                listed_cars_model3 = listed_cars
                
        try:
            # time.sleep(1)
            click_count += 1  # Increment the click counter
            loop = driver.find_element(By.CSS_SELECTOR, ".icon.icon--chevron-right")
            # loop.click() 
        except NoSuchElementException:
            print("Reached last page.")
            break  # No "Next Page" element found, exit the loop

    # Extract Year, Mileage, and Price from the second element
    year, mileage, price = [], [], []
    for text in data_element2:
        parts = text
        year.append(parts[0])
        mileage.append(parts[1])
        price.append(parts[2])

    # Create a DataFrame
    df1 = pd.DataFrame({"Name": data_element1})
    df2 = pd.DataFrame({"Year": year, "Mileage": mileage, "Price": price})
    df3 = pd.DataFrame({"Retailer": data_element3})
    df4 = pd.DataFrame({"Listed Cars": data_element4})

    df = pd.concat([df1, df2, df3, df4], axis=1)

    # Step 3: Add Timestamp to New Data
    df['Timestamp'] = datetime.now().strftime('%d/%m/%Y')

    # Add a column for price updates if it doesn't exist
    if 'Updated Price' not in existing_df.columns:
        existing_df['Updated Price'] = None

    # Convert relevant columns to strings for consistent comparison
    df[['Year', 'Mileage', 'Price']] = df[['Year', 'Mileage', 'Price']].astype(str)
    existing_df[['Year', 'Mileage', 'Price']] = existing_df[['Year', 'Mileage', 'Price']].astype(str)

    # Existing conversions to strings
    df[['Year', 'Mileage', 'Price']] = df[['Year', 'Mileage', 'Price']].astype(str)
    existing_df[['Year', 'Mileage', 'Price']] = existing_df[['Year', 'Mileage', 'Price']].astype(str)

    # Additional explicit conversion for 'Year' to handle float to string conversion properly
    existing_df['Year'] = existing_df['Year'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x.replace('.', '', 1).isdigit() else x)
    df['Year'] = df['Year'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x.replace('.', '', 1).isdigit() else x)

    # Iterate over new rows to find matches and update if necessary
    for index, new_row in df.iterrows():
        # Find matching rows based on Name, Year, and Mileage
        match = existing_df[(existing_df['Name'] == new_row['Name']) & 
                            (existing_df['Year'] == new_row['Year']) & 
                            (existing_df['Mileage'] == new_row['Mileage'])]

        # If match is found
        if not match.empty:
            # Check if the Price in existing data does NOT equal the new Price (and is not already updated to this new price)
            price_update_condition = (match['Price'] != new_row['Price']) & (match['Updated Price'] != new_row['Price'])
            
            # If the condition is True, update the 'Updated Price'
            if price_update_condition.any():
                existing_df.loc[match.index, 'Updated Price'] = new_row['Price']
                existing_df.loc[match.index, 'Date Price Change'] = datetime.now().strftime('%d/%m/%Y')  # Update the Date Price Change only for the matched rows
            # No else part needed, as we don't do anything if the prices match or if the updated price is already the new price
        else:
            # Append new_row to existing_df if no match found
            existing_df = pd.concat([existing_df, pd.DataFrame([new_row]).reset_index(drop=True)], ignore_index=True)

    # Remove duplicates (entries where name, year, mileage, and both prices match)
    existing_df.drop_duplicates(subset=['Name', 'Year', 'Mileage', 'Price', 'Updated Price'], keep='first', inplace=True)

    # Add a step to count entries with 'Solgt' in Price columns and match today's date
    today = datetime.now().strftime('%d/%m/%Y')

    # Filter DataFrame for entries with 'Solgt' in 'Price' and 'Updated Price' as today's date
    solgt_today_price = existing_df[(existing_df['Price'] == 'Solgt') & (existing_df['Timestamp'] == today)]
    solgt_today_updated_price = existing_df[(existing_df['Updated Price'] == 'Solgt') & (existing_df['Date Price Change'] == today)]

    # Count these entries
    solgt_count_price = solgt_today_price.shape[0]
    solgt_count_updated_price = solgt_today_updated_price.shape[0]

    # Store counts in a variable
    model3_solgt_today = solgt_count_price + solgt_count_updated_price

    # Optional: You can use this variable 'total_solgt_today' as needed
    print(f"Total 'Solgt' entries in Price and Updated Price columns for today: {model3_solgt_today}")

    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        existing_df.to_excel(writer, sheet_name='model3', index=False)

    # #Model Y
    print("Model Y")
    # Navigate to a webpage
    driver.get("https://www.finn.no/car/used/search.html?model=1.8078.2000555")

    time.sleep(3)

    # Step 1: Read Existing Data from Excel
    excel_path = "./tesla.xlsx"
    try:
        existing_df = pd.read_excel(excel_path, sheet_name='modely')
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=["Name", "Year", "Mileage", "Price", "Timestamp"])  # Assuming these are your columns
        
    # Initialize empty lists to store data
    data_element1 = []
    data_element2 = []
    data_element3 = []
    data_element4 = []
    click_count = 0

    while True:
        driver.get(f"https://www.finn.no/car/used/search.html?model=1.8078.2000555&page={click_count + 1}")
        WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, f"//body/div[@id='__next']/main[1]/div[1]/div[2]/section[2]/div[3]/article[2]/div[3]/h2[1]/a[1]"))
        )
        for article_nr in range(2, 99):
            element1_successful = False  # Flag to indicate if element1 is successfully scraped for the current article
            element2_successful = False  # Flag to indicate if element2 is successfully scraped for the current article

            try:
                element1 = driver.find_element(By.XPATH, f"//body/div[@id='__next']/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]")
                # element1 = driver.find_element(By.XPATH, f"/html[1]/body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]/span[1]")
                # element1 = driver.find_element(By.XPATH, f"/html[1]/body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]")
                text1 = element1.text
                element1_successful = True  # Set the flag to True if element1 is successfully scraped
            except (NoSuchElementException, StaleElementReferenceException):
                continue

            try:
                element4 = driver.find_element(By.XPATH, f"(//div[contains(@class,'flex flex-col text-12')])[{article_nr}]")
                text4 = element4.text
            except (NoSuchElementException, StaleElementReferenceException):
                continue

            try:
                # Try finding the element using the first XPath
                element2 = driver.find_element(By.XPATH, f"//body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/div[3]")
                text2 = element2.text.split('\n')
                if len(text2) == 3:
                    year, mileage, price = text2
                    element2_successful = True  # Set the flag to True if element2 is successfully scraped
                else:
                    # Handle , cases where there might be missing data      //body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[46]/div[3]/div[2]/span[1]
                    element3 = driver.find_element(By.XPATH, f"//body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/div[4]")
                    text2 = element3.text.split('\n')
                    if len(text2) == 3:
                        year, mileage, price = text2
                        element2_successful = True  # Set the flag to True if element2 is successfully scraped
                    else:
                        print("Error: No data found")
            except NoSuchElementException:
                continue  # If both XPaths fail, continue to the next article
            
            # Append data only if both elements are successfully scraped
            if element1_successful and element2_successful:
                data_element1.append(text1)
                data_element2.append((year, mileage, price))
                data_element3.append(text4)
                #Scraping number of listed cars
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='flex-shrink-0']"))
                    )
                listed_cars = driver.find_element(By.CSS_SELECTOR, "div[class='flex-shrink-0']")
                cars = listed_cars.text
                integer_part = re.search(r'\d+', cars).group()

                # Convert the integer part to an actual integer
                listed_cars = int(integer_part)
                data_element4.append(listed_cars)
                listed_cars_modely = listed_cars
                
        try:
            # time.sleep(1)
            click_count += 1  # Increment the click counter
            loop = driver.find_element(By.CSS_SELECTOR, ".icon.icon--chevron-right")
            # loop.click() 
        except NoSuchElementException:
            print("Reached last page.")
            break  # No "Next Page" element found, exit the loop

    # Extract Year, Mileage, and Price from the second element
    year, mileage, price = [], [], []
    for text in data_element2:
        parts = text
        year.append(parts[0])
        mileage.append(parts[1])
        price.append(parts[2])

    # Create a DataFrame
    df1 = pd.DataFrame({"Name": data_element1})
    df2 = pd.DataFrame({"Year": year, "Mileage": mileage, "Price": price})
    df3 = pd.DataFrame({"Retailer": data_element3})
    df4 = pd.DataFrame({"Listed Cars": data_element4})

    df = pd.concat([df1, df2, df3, df4], axis=1)

    # Step 3: Add Timestamp to New Data
    df['Timestamp'] = datetime.now().strftime('%d/%m/%Y')

    # Add a column for price updates if it doesn't exist
    if 'Updated Price' not in existing_df.columns:
        existing_df['Updated Price'] = None

    # Convert relevant columns to strings for consistent comparison
    df[['Year', 'Mileage', 'Price']] = df[['Year', 'Mileage', 'Price']].astype(str)
    existing_df[['Year', 'Mileage', 'Price']] = existing_df[['Year', 'Mileage', 'Price']].astype(str)

    # Existing conversions to strings
    df[['Year', 'Mileage', 'Price']] = df[['Year', 'Mileage', 'Price']].astype(str)
    existing_df[['Year', 'Mileage', 'Price']] = existing_df[['Year', 'Mileage', 'Price']].astype(str)

    # Additional explicit conversion for 'Year' to handle float to string conversion properly
    existing_df['Year'] = existing_df['Year'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x.replace('.', '', 1).isdigit() else x)
    df['Year'] = df['Year'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x.replace('.', '', 1).isdigit() else x)

    # Iterate over new rows to find matches and update if necessary
    for index, new_row in df.iterrows():
        # Find matching rows based on Name, Year, and Mileage
        match = existing_df[(existing_df['Name'] == new_row['Name']) & 
                            (existing_df['Year'] == new_row['Year']) & 
                            (existing_df['Mileage'] == new_row['Mileage'])]

        # If match is found
        if not match.empty:
            # Check if the Price in existing data does NOT equal the new Price (and is not already updated to this new price)
            price_update_condition = (match['Price'] != new_row['Price']) & (match['Updated Price'] != new_row['Price'])
            
            # If the condition is True, update the 'Updated Price'
            if price_update_condition.any():
                existing_df.loc[match.index, 'Updated Price'] = new_row['Price']
                existing_df.loc[match.index, 'Date Price Change'] = datetime.now().strftime('%d/%m/%Y')  # Update the Date Price Change only for the matched rows
            # No else part needed, as we don't do anything if the prices match or if the updated price is already the new price
        else:
            # Append new_row to existing_df if no match found
            existing_df = pd.concat([existing_df, pd.DataFrame([new_row]).reset_index(drop=True)], ignore_index=True)

    # Remove duplicates (entries where name, year, mileage, and both prices match)
    existing_df.drop_duplicates(subset=['Name', 'Year', 'Mileage', 'Price', 'Updated Price'], keep='first', inplace=True)

    # Filter DataFrame for entries with 'Solgt' in 'Price' and 'Updated Price' as today's date
    solgt_today_price = existing_df[(existing_df['Price'] == 'Solgt') & (existing_df['Timestamp'] == today)]
    solgt_today_updated_price = existing_df[(existing_df['Updated Price'] == 'Solgt') & (existing_df['Date Price Change'] == today)]

    # Count these entries
    solgt_count_price = solgt_today_price.shape[0]
    solgt_count_updated_price = solgt_today_updated_price.shape[0]

    # Store counts in a variable
    modely_solgt_today = solgt_count_price + solgt_count_updated_price

    # Optional: You can use this variable 'total_solgt_today' as needed
    print(f"Total 'Solgt' entries in Price and Updated Price columns for today: {modely_solgt_today}")

    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        existing_df.to_excel(writer, sheet_name='modely', index=False)


    #Model X
    print("Model X")
    # Navigate to a webpage
    driver.get("https://www.finn.no/car/used/search.html?model=1.8078.2000379")
    time.sleep(3)

    # Step 1: Read Existing Data from Excel
    excel_path = "./tesla.xlsx"
    try:
        existing_df = pd.read_excel(excel_path, sheet_name='modelx')
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=["Name", "Year", "Mileage", "Price", "Timestamp"])  # Assuming these are your columns
        
    # Initialize empty lists to store data
    data_element1 = []
    data_element2 = []
    data_element3 = []
    data_element4 = []
    click_count = 0

    while True:
        driver.get(f"https://www.finn.no/car/used/search.html?model=1.8078.2000379&page={click_count + 1}")
        WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, f"//body/div[@id='__next']/main[1]/div[1]/div[2]/section[2]/div[3]/article[2]/div[3]/h2[1]/a[1]"))
        )
        for article_nr in range(2, 99):
            element1_successful = False  # Flag to indicate if element1 is successfully scraped for the current article
            element2_successful = False  # Flag to indicate if element2 is successfully scraped for the current article

            try:
                element1 = driver.find_element(By.XPATH, f"//body/div[@id='__next']/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]")
                # element1 = driver.find_element(By.XPATH, f"/html[1]/body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]/span[1]")
                # element1 = driver.find_element(By.XPATH, f"/html[1]/body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]")
                text1 = element1.text
                element1_successful = True  # Set the flag to True if element1 is successfully scraped
            except (NoSuchElementException, StaleElementReferenceException):
                continue

            try:
                element4 = driver.find_element(By.XPATH, f"(//div[contains(@class,'flex flex-col text-12')])[{article_nr}]")
                text4 = element4.text
            except (NoSuchElementException, StaleElementReferenceException):
                continue

            try:
                # Try finding the element using the first XPath
                element2 = driver.find_element(By.XPATH, f"//body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/div[3]")
                text2 = element2.text.split('\n')
                if len(text2) == 3:
                    year, mileage, price = text2
                    element2_successful = True  # Set the flag to True if element2 is successfully scraped
                else:
                    # Handle , cases where there might be missing data      //body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[46]/div[3]/div[2]/span[1]
                    element3 = driver.find_element(By.XPATH, f"//body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/div[4]")
                    text2 = element3.text.split('\n')
                    if len(text2) == 3:
                        year, mileage, price = text2
                        element2_successful = True  # Set the flag to True if element2 is successfully scraped
                    else:
                        print("Error: No data found")
            except NoSuchElementException:
                continue  # If both XPaths fail, continue to the next article
            
            # Append data only if both elements are successfully scraped
            if element1_successful and element2_successful:
                data_element1.append(text1)
                data_element2.append((year, mileage, price))
                data_element3.append(text4)
                #Scraping number of listed cars
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='flex-shrink-0']"))
                    )
                listed_cars = driver.find_element(By.CSS_SELECTOR, "div[class='flex-shrink-0']")
                cars = listed_cars.text
                integer_part = re.search(r'\d+', cars).group()

                # Convert the integer part to an actual integer
                listed_cars = int(integer_part)
                data_element4.append(listed_cars)
                listed_cars_modelx = listed_cars
                
        try:
            # time.sleep(1)
            click_count += 1  # Increment the click counter
            loop = driver.find_element(By.CSS_SELECTOR, ".icon.icon--chevron-right")
            # loop.click() 
        except NoSuchElementException:
            print("Reached last page.")
            break  # No "Next Page" element found, exit the loop

    # Extract Year, Mileage, and Price from the second element
    year, mileage, price = [], [], []
    for text in data_element2:
        parts = text
        year.append(parts[0])
        mileage.append(parts[1])
        price.append(parts[2])

    # Create a DataFrame
    df1 = pd.DataFrame({"Name": data_element1})
    df2 = pd.DataFrame({"Year": year, "Mileage": mileage, "Price": price})
    df3 = pd.DataFrame({"Retailer": data_element3})
    df4 = pd.DataFrame({"Listed Cars": data_element4})

    df = pd.concat([df1, df2, df3, df4], axis=1)

    # Step 3: Add Timestamp to New Data
    df['Timestamp'] = datetime.now().strftime('%d/%m/%Y')

    # Add a column for price updates if it doesn't exist
    if 'Updated Price' not in existing_df.columns:
        existing_df['Updated Price'] = None

    # Convert relevant columns to strings for consistent comparison
    df[['Year', 'Mileage', 'Price']] = df[['Year', 'Mileage', 'Price']].astype(str)
    existing_df[['Year', 'Mileage', 'Price']] = existing_df[['Year', 'Mileage', 'Price']].astype(str)

    # Existing conversions to strings
    df[['Year', 'Mileage', 'Price']] = df[['Year', 'Mileage', 'Price']].astype(str)
    existing_df[['Year', 'Mileage', 'Price']] = existing_df[['Year', 'Mileage', 'Price']].astype(str)

    # Additional explicit conversion for 'Year' to handle float to string conversion properly
    existing_df['Year'] = existing_df['Year'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x.replace('.', '', 1).isdigit() else x)
    df['Year'] = df['Year'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x.replace('.', '', 1).isdigit() else x)

    # Iterate over new rows to find matches and update if necessary
    for index, new_row in df.iterrows():
        # Find matching rows based on Name, Year, and Mileage
        match = existing_df[(existing_df['Name'] == new_row['Name']) & 
                            (existing_df['Year'] == new_row['Year']) & 
                            (existing_df['Mileage'] == new_row['Mileage'])]

        # If match is found
        if not match.empty:
            # Check if the Price in existing data does NOT equal the new Price (and is not already updated to this new price)
            price_update_condition = (match['Price'] != new_row['Price']) & (match['Updated Price'] != new_row['Price'])
            
            # If the condition is True, update the 'Updated Price'
            if price_update_condition.any():
                existing_df.loc[match.index, 'Updated Price'] = new_row['Price']
                existing_df.loc[match.index, 'Date Price Change'] = datetime.now().strftime('%d/%m/%Y')  # Update the Date Price Change only for the matched rows
            # No else part needed, as we don't do anything if the prices match or if the updated price is already the new price
        else:
            # Append new_row to existing_df if no match found
            existing_df = pd.concat([existing_df, pd.DataFrame([new_row]).reset_index(drop=True)], ignore_index=True)

    # Remove duplicates (entries where name, year, mileage, and both prices match)
    existing_df.drop_duplicates(subset=['Name', 'Year', 'Mileage', 'Price', 'Updated Price'], keep='first', inplace=True)

    # Filter DataFrame for entries with 'Solgt' in 'Price' and 'Updated Price' as today's date
    solgt_today_price = existing_df[(existing_df['Price'] == 'Solgt') & (existing_df['Timestamp'] == today)]
    solgt_today_updated_price = existing_df[(existing_df['Updated Price'] == 'Solgt') & (existing_df['Date Price Change'] == today)]

    # Count these entries
    solgt_count_price = solgt_today_price.shape[0]
    solgt_count_updated_price = solgt_today_updated_price.shape[0]

    # Store counts in a variable
    modelx_solgt_today = solgt_count_price + solgt_count_updated_price

    # Optional: You can use this variable 'total_solgt_today' as needed
    print(f"Total 'Solgt' entries in Price and Updated Price columns for today: {modelx_solgt_today}")

    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        existing_df.to_excel(writer, sheet_name='modelx', index=False)


    #Model S
    print("Model S")
    # Navigate to a webpage
    driver.get("https://www.finn.no/car/used/search.html?model=1.8078.2000138")
    time.sleep(3)

    # Step 1: Read Existing Data from Excel
    excel_path = "./tesla.xlsx"
    try:
        existing_df = pd.read_excel(excel_path, sheet_name='models')
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=["Name", "Year", "Mileage", "Price", "Timestamp"])  # Assuming these are your columns
        
    # Initialize empty lists to store data
    data_element1 = []
    data_element2 = []
    data_element3 = []
    data_element4 = []
    click_count = 0

    while True:
        driver.get(f"https://www.finn.no/car/used/search.html?model=1.8078.2000138&page={click_count + 1}")
        WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, f"//body/div[@id='__next']/main[1]/div[1]/div[2]/section[2]/div[3]/article[2]/div[3]/h2[1]/a[1]"))
        )
        for article_nr in range(2, 99):
            element1_successful = False  # Flag to indicate if element1 is successfully scraped for the current article
            element2_successful = False  # Flag to indicate if element2 is successfully scraped for the current article

            try:
                element1 = driver.find_element(By.XPATH, f"//body/div[@id='__next']/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]")
                # element1 = driver.find_element(By.XPATH, f"/html[1]/body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]/span[1]")
                # element1 = driver.find_element(By.XPATH, f"/html[1]/body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/h2[1]/a[1]")
                text1 = element1.text
                element1_successful = True  # Set the flag to True if element1 is successfully scraped
            except (NoSuchElementException, StaleElementReferenceException):
                continue

            try:
                element4 = driver.find_element(By.XPATH, f"(//div[contains(@class,'flex flex-col text-12')])[{article_nr}]")
                text4 = element4.text
            except (NoSuchElementException, StaleElementReferenceException):
                continue

            try:
                # Try finding the element using the first XPath
                element2 = driver.find_element(By.XPATH, f"//body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/div[3]")
                text2 = element2.text.split('\n')
                if len(text2) == 3:
                    year, mileage, price = text2
                    element2_successful = True  # Set the flag to True if element2 is successfully scraped
                else:
                    # Handle , cases where there might be missing data      //body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[46]/div[3]/div[2]/span[1]
                    element3 = driver.find_element(By.XPATH, f"//body[1]/div[2]/main[1]/div[1]/div[2]/section[2]/div[3]/article[{article_nr}]/div[3]/div[4]")
                    text2 = element3.text.split('\n')
                    if len(text2) == 3:
                        year, mileage, price = text2
                        element2_successful = True  # Set the flag to True if element2 is successfully scraped
                    else:
                        print("Error: No data found")
            except NoSuchElementException:
                continue  # If both XPaths fail, continue to the next article
            
            # Append data only if both elements are successfully scraped
            if element1_successful and element2_successful:
                data_element1.append(text1)
                data_element2.append((year, mileage, price))
                data_element3.append(text4)
                #Scraping number of listed cars
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='flex-shrink-0']"))
                    )
                listed_cars = driver.find_element(By.CSS_SELECTOR, "div[class='flex-shrink-0']")
                cars = listed_cars.text
                integer_part = re.search(r'\d+', cars).group()

                # Convert the integer part to an actual integer
                listed_cars = int(integer_part)
                data_element4.append(listed_cars)
                listed_cars_models = listed_cars
                
        try:
            # time.sleep(1)
            click_count += 1  # Increment the click counter
            loop = driver.find_element(By.CSS_SELECTOR, ".icon.icon--chevron-right")
            # loop.click() 
        except NoSuchElementException:
            print("Reached last page.")
            break  # No "Next Page" element found, exit the loop

    # Extract Year, Mileage, and Price from the second element
    year, mileage, price = [], [], []
    for text in data_element2:
        parts = text
        year.append(parts[0])
        mileage.append(parts[1])
        price.append(parts[2])

    # Create a DataFrame
    df1 = pd.DataFrame({"Name": data_element1})
    df2 = pd.DataFrame({"Year": year, "Mileage": mileage, "Price": price})
    df3 = pd.DataFrame({"Retailer": data_element3})
    df4 = pd.DataFrame({"Listed Cars": data_element4})

    df = pd.concat([df1, df2, df3, df4], axis=1)

    # Step 3: Add Timestamp to New Data
    df['Timestamp'] = datetime.now().strftime('%d/%m/%Y')

    # Add a column for price updates if it doesn't exist
    if 'Updated Price' not in existing_df.columns:
        existing_df['Updated Price'] = None

    # Convert relevant columns to strings for consistent comparison
    df[['Year', 'Mileage', 'Price']] = df[['Year', 'Mileage', 'Price']].astype(str)
    existing_df[['Year', 'Mileage', 'Price']] = existing_df[['Year', 'Mileage', 'Price']].astype(str)

    # Existing conversions to strings
    df[['Year', 'Mileage', 'Price']] = df[['Year', 'Mileage', 'Price']].astype(str)
    existing_df[['Year', 'Mileage', 'Price']] = existing_df[['Year', 'Mileage', 'Price']].astype(str)

    # Additional explicit conversion for 'Year' to handle float to string conversion properly
    existing_df['Year'] = existing_df['Year'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x.replace('.', '', 1).isdigit() else x)
    df['Year'] = df['Year'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x.replace('.', '', 1).isdigit() else x)

    # Iterate over new rows to find matches and update if necessary
    for index, new_row in df.iterrows():
        # Find matching rows based on Name, Year, and Mileage
        match = existing_df[(existing_df['Name'] == new_row['Name']) & 
                            (existing_df['Year'] == new_row['Year']) & 
                            (existing_df['Mileage'] == new_row['Mileage'])]

        # If match is found
        if not match.empty:
            # Check if the Price in existing data does NOT equal the new Price (and is not already updated to this new price)
            price_update_condition = (match['Price'] != new_row['Price']) & (match['Updated Price'] != new_row['Price'])
            
            # If the condition is True, update the 'Updated Price'
            if price_update_condition.any():
                existing_df.loc[match.index, 'Updated Price'] = new_row['Price']
                existing_df.loc[match.index, 'Date Price Change'] = datetime.now().strftime('%d/%m/%Y')  # Update the Date Price Change only for the matched rows
            # No else part needed, as we don't do anything if the prices match or if the updated price is already the new price
        else:
            # Append new_row to existing_df if no match found
            existing_df = pd.concat([existing_df, pd.DataFrame([new_row]).reset_index(drop=True)], ignore_index=True)

    # Remove duplicates (entries where name, year, mileage, and both prices match)
    existing_df.drop_duplicates(subset=['Name', 'Year', 'Mileage', 'Price', 'Updated Price'], keep='first', inplace=True)

    # Filter DataFrame for entries with 'Solgt' in 'Price' and 'Updated Price' as today's date
    solgt_today_price = existing_df[(existing_df['Price'] == 'Solgt') & (existing_df['Timestamp'] == today)]
    solgt_today_updated_price = existing_df[(existing_df['Updated Price'] == 'Solgt') & (existing_df['Date Price Change'] == today)]

    # Count these entries
    solgt_count_price = solgt_today_price.shape[0]
    solgt_count_updated_price = solgt_today_updated_price.shape[0]

    # Store counts in a variable
    models_solgt_today = solgt_count_price + solgt_count_updated_price

    # Optional: You can use this variable 'total_solgt_today' as needed
    print(f"Total 'Solgt' entries in Price and Updated Price columns for today: {models_solgt_today}")
    driver.quit()

    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        existing_df.to_excel(writer, sheet_name='models', index=False)

    #Scrape Cars Listed from all Tesla models
    # Initialize existing_df as an empty DataFrame
    excel_path = "./tesla.xlsx"
    existing_df = pd.read_excel(excel_path, sheet_name='cars_listed')

    # Define columns if not already
    if existing_df.empty:
        existing_df = pd.DataFrame(columns=["Date", "Model 3", "Model Y", "Model X", "Model S"])

    # Get today's date
    today_date = datetime.now().strftime('%d/%m/%Y')

    # Check if today's date is in the "Date" column
    if today_date in existing_df['Date'].values:
        # If today's date is present, check if the corresponding columns are empty
        empty_columns = existing_df.loc[existing_df['Date'] == today_date, ["Model 3", "Model Y", "Model X", "Model S"]].isnull().all()
        
        # If any of the corresponding columns are empty, append the data to those columns
        if empty_columns.any():
            empty_columns = empty_columns[empty_columns].index  # Get names of empty columns
            existing_df.loc[existing_df['Date'] == today_date, empty_columns] = [listed_cars_model3, listed_cars_modely, listed_cars_modelx, listed_cars_models]
    else:
        # If today's date is not present, create a new row and concat it
        new_row = pd.DataFrame({'Date': [today_date], "Model 3": [listed_cars_model3], "Model Y": [listed_cars_modely], "Model X": [listed_cars_modelx], "Model S": [listed_cars_models]})
        existing_df = pd.concat([existing_df, new_row], ignore_index=True)

    # Save the updated DataFrame back to Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        existing_df.to_excel(writer, sheet_name='cars_listed', index=False)

    #Put Cars Sold Into Cars_listed sheet
    excel_path = "./tesla.xlsx"

    # Load existing data from Excel
    try:
        existing_df = pd.read_excel(excel_path, sheet_name='cars_listed')
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=["Date", "Model 3 Sold", "Model Y Sold", "Model X Sold", "Model S Sold"])

    # Get today's date
    today_date = datetime.now().strftime('%d/%m/%Y')

    # Check if today's date is in the "Date" column
    if today_date in existing_df['Date'].values:
        # If today's date is present, update the row
        idx = existing_df[existing_df['Date'] == today_date].index
        existing_df.loc[idx, "Model 3 Sold"] = model3_solgt_today
        existing_df.loc[idx, "Model Y Sold"] = modely_solgt_today
        existing_df.loc[idx, "Model X Sold"] = modelx_solgt_today
        existing_df.loc[idx, "Model S Sold"] = models_solgt_today

    # Save the updated DataFrame back to Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        existing_df.to_excel(writer, sheet_name='cars_listed', index=False)


    #Upload to PythonAnywhere
    max_attempts = 3 
    for attempt in range (1, max_attempts + 1):
            # Define PythonAnywhere username and API token
            username = os.getenv('PYTHONANYWHERE_USERNAME')
            api_token = os.getenv('PYTHONANYWHERE_API')

            # Define file path of the Excel file to upload
            tesla = "./tesla.xlsx"
            file_path = tesla

            # Define PythonAnywhere file path to upload the file to
            pythonanywhere_file_path = f'/home/{username}/mysite/templates/tesla.xlsx'

            # Define PythonAnywhere upload URL
            upload_url = f'https://www.pythonanywhere.com/api/v0/user/{username}/files/path{pythonanywhere_file_path}'

            # Define headers with API token
            headers = {
                'Authorization': f'Token {api_token}'
            }

            # Open the Excel file
            with open(file_path, 'rb') as file:
                # Create a dictionary with file data
                files = {'content': (file_path, file, 'application/octet-stream')}

                time.sleep(1)
                # Make HTTP POST request to upload the file
                response = requests.post(upload_url, headers=headers, files=files)

            # Check if the upload was successful
            if response.status_code == 200:
                print('excel file today - File uploaded successfully to PythonAnywhere.')
                break

            print(f'excel file today: Error uploading file to PythonAnywhere: {response.text}')
            print(response.status_code)
            print(response.text)

            if attempt == max_attempts:
                print("Max attempts reached, exiting loop...")

    time.sleep(1)

    def clean_data(df):
        # Check if values in 'Mileage' column are strings before applying operations
        if df['Mileage'].dtype == 'object':
            df['Mileage'] = df['Mileage'].str.replace(' km', '').str.replace(' ', '').astype(float).fillna(np.nan).astype('Int64')
        
        # Check if values in 'Price' column are strings before applying operations
        if df['Price'].dtype == 'object':
            df['Price'] = pd.to_numeric(df['Price'].str.replace(' kr', '').str.replace(' ', ''), errors='coerce').astype('Int64')
        
        # Check if values in 'Updated Price' column are strings before applying operations
        if 'Updated Price' in df.columns and df['Updated Price'].dtype == 'object':
            # Create a mask for the "Solgt" entries
            solgt_mask = df['Updated Price'].str.strip().str.lower() == 'solgt'
            
            # Convert numeric entries to integers
            df.loc[~solgt_mask, 'Updated Price'] = pd.to_numeric(
                df.loc[~solgt_mask, 'Updated Price'].str.replace(' kr', '').str.replace(' ', ''), errors='coerce'
            ).astype('Int64')
            
            # Ensure "Solgt" entries remain as strings
            df.loc[solgt_mask, 'Updated Price'] = 'Solgt'
        
        return df

    def excel_to_json(input_excel_file):
        # Read Excel file
        xls = pd.ExcelFile(input_excel_file)
        
        for sheet_name in xls.sheet_names:
            # Read each sheet
            df = pd.read_excel(input_excel_file, sheet_name=sheet_name)
            
            # Clean data
            df = clean_data(df)
            
            # Determine the output JSON file name
            output_json_file = f"{sheet_name.lower()}.json"  # Default JSON file name
            
            # Rename the JSON file specifically for 'cars_listed'
            if sheet_name == 'cars_listed':
                output_json_file = "tesla_listed.json"

            # Write JSON data to file
            json_data = df.to_json(orient='records')
            with open(output_json_file, 'w') as f:
                f.write(json_data)
                
            # Upload JSON file to PythonAnywhere
            upload_json_to_pythonanywhere(output_json_file)

    def upload_json_to_pythonanywhere(json_file):
        for attempt in range(3):
        # Define PythonAnywhere file path to upload the file to
            username = os.getenv('PYTHONANYWHERE_USERNAME')
            api_token = os.getenv('PYTHONANYWHERE_API')
            pythonanywhere_file_path = f'/home/{username}/mysite/static/assets/json/{json_file}'

            # Define PythonAnywhere upload URL
            upload_url = f'https://www.pythonanywhere.com/api/v0/user/{username}/files/path{pythonanywhere_file_path}'

            # Define headers with API token
            headers = {
                'Authorization': f'Token {api_token}'
            }

            # Open the JSON file
            with open(json_file, 'rb') as file:
                # Create a dictionary with file data
                files = {'content': (json_file, file, 'application/octet-stream')}

                # Make HTTP POST request to upload the file
                response = requests.post(upload_url, headers=headers, files=files)

            # Check if the upload was successful
            if response.status_code == 200:
                print(f'{json_file} - File uploaded successfully to PythonAnywhere.')

                # Upload to FTP server
                ftp_server = 'elbilstats.no'
                ftp_username = os.getenv('ELBILSTATS_FTP_USERNAME')
                ftp_password = os.getenv('ELBILSTATS_FTP_PASSWORD')
                ftp_directory = 'public_html/static/assets/json'

                upload_file_to_ftp(ftp_server, ftp_username, ftp_password, ftp_directory, json_file)
                break
            else:
                print(f'{json_file}: Error uploading file to PythonAnywhere: {response.text}')
                if attempt == 2:
                    print("Max attempts reached, exiting loop.")

    def upload_file_to_ftp(ftp_server, username, password, directory, file_to_upload):
        for attempt in range(3):
            try:
                # Establish connection to the FTP server
                ftp = FTP(ftp_server)
                ftp.login(user=username, passwd=password)

                # Change to the target directory
                ftp.cwd(directory)

                # Extract file name from file path
                file_name = os.path.basename(file_to_upload)

                # Open the file to upload
                with open(file_to_upload, 'rb') as file:
                    # Upload the file
                    ftp.storbinary(f'STOR {file_name}', file)

                # List files in the directory to verify upload
                ftp.retrlines('LIST')

                # Close the FTP connection
                ftp.quit()
                print(f"File '{file_name}' successfully uploaded to '{directory}' on '{ftp_server}'.")
                break  # Exit the loop if upload is successful

            except Exception as e:
                print(f"Failed to upload file: {e}")
                if attempt == 2:
                    print("Max attempts reached, exiting loop.")

    # Example usage
    input_excel_file = 'tesla.xlsx'  # Provide the path to your Excel file

    excel_to_json(input_excel_file)

if __name__ == "__main__":
    main_flow()