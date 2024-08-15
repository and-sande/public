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
import undetected_chromedriver as uc 
# import zipfile
import os
# import subprocess
from ftplib import FTP
from prefect import flow

@flow(log_prints=True, name="Finn.no Electric Cars Scrape - Audi")
def main_flow():
    # Variables for car brand and models
    car_brand = "audi"
    models = [
        {"name": "Q4_e-tron", "url": "https://www.finn.no/car/used/search.html?model=1.744.2000541&page="},
        {"name": "Q8_e-tron", "url": "https://www.finn.no/car/used/search.html?model=1.744.2000617&page="},
        {"name": "e-tron", "url": "https://www.finn.no/car/used/search.html?model=1.744.2000503&page="},
        {"name": "e-tron_GT", "url": "https://www.finn.no/car/used/search.html?model=1.744.2000540&page="},
        {"name": "e-tron_Sportback", "url": "https://www.finn.no/car/used/search.html?model=1.744.8373&page="},
    ]
    # PythonAnywhere credentials
    username = os.getenv('PYTHONANYWHERE_USERNAME')
    api_token = os.getenv('PYTHONANYWHERE_API')
    pythonanywhere_path = f'/home/{username}/mysite/templates/{car_brand}.xlsx'

    # Download the Excel file from PythonAnywhere
    download_url = f'https://www.pythonanywhere.com/api/v0/user/{username}/files/path{pythonanywhere_path}'
    headers = {'Authorization': f'Token {api_token}'}

    response = requests.get(download_url, headers=headers)
    if response.status_code == 200:
        with open(f'{car_brand}.xlsx', 'wb') as file:
            file.write(response.content)
        print('File downloaded successfully.')
    else:
        print('Failed to download the file.')


    listed_cars_data = {}
    sold_cars_data = {}

    # Initialize WebDriver
    chromedriver_autoinstaller.install()
    # Chrome options
    chrome_options = webdriver.ChromeOptions()
    options = ["--headless", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage", "--disable-search-engine-choice-screen"]
    for option in options:
        chrome_options.add_argument(option)

    # Initialize driver
    driver = uc.Chrome(options=chrome_options)

    for model in models:
        model_name = model["name"]
        model_url = model["url"]

        # Navigate to the first page of the model
        driver.get(model_url + "1")
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
            print(f"No cookies button for {model_name}. Continuing without accepting cookies.")

        driver.switch_to.default_content()

        # Read existing data from Excel
        excel_path = f"{car_brand}.xlsx"
        try:
            existing_df = pd.read_excel(excel_path, sheet_name=model_name)
        except FileNotFoundError:
            existing_df = pd.DataFrame(columns=["Name", "Year", "Mileage", "Price", "Timestamp"])

        data_element1, data_element2, data_element3, data_element4 = [], [], [], []
        click_count = 0

        # Scraping logic for each page
        while True:
            driver.get(f"{model_url}{click_count + 1}")
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, f"//article[2]/div[3]/h2[1]/a[1]"))
                )
            except TimeoutException:
                print(f"Reached last page for {model_name}.")
                break

            for article_nr in range(2, 99):
                try:
                    # Extract the name and details
                    element1 = driver.find_element(By.XPATH, f"//article[{article_nr}]/div[3]/h2[1]/a[1]")
                    text1 = element1.text

                    try:
                        element2 = driver.find_element(By.XPATH, f"//article[{article_nr}]/div[3]/div[3]")
                        text2 = element2.text.split('\n')
                        if len(text2) == 3:
                            year, mileage, price = text2
                            element2_successful = True
                        else:
                            raise NoSuchElementException
                    except NoSuchElementException:
                        try:
                            element3 = driver.find_element(By.XPATH, f"//article[{article_nr}]/div[3]/div[4]")
                            text2 = element3.text.split('\n')
                            if len(text2) == 3:
                                year, mileage, price = text2
                                element2_successful = True
                            else:
                                print("Error: No data found")
                                continue
                        except NoSuchElementException:
                            continue
                    
                    element4 = driver.find_element(By.XPATH, f"(//div[contains(@class,'flex flex-col text-12')])[{article_nr}]")
                    text3 = element4.text

                    data_element1.append(text1)
                    data_element2.append((year, mileage, price))
                    data_element3.append(text3)

                except (NoSuchElementException, StaleElementReferenceException):
                    continue

            # Check for more pages
            try:
                click_count += 1
                driver.find_element(By.CSS_SELECTOR, ".icon.icon--chevron-right")
            except NoSuchElementException:
                print(f"Reached last page for {model_name}.")
                break

        # Listed cars for different models 
        WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='flex-shrink-0']"))
                    )
        listed_cars = driver.find_element(By.CSS_SELECTOR, "div[class='flex-shrink-0']")
        cars = listed_cars.text
        integer_part = re.search(r'\d+', cars).group()

        # Convert the integer part to an actual integer
        listed_cars = int(integer_part)
        data_element4.append(listed_cars)
        listed_cars_data[model_name] = listed_cars

        # Process data into DataFrame
        if data_element2:
            year, mileage, price = zip(*data_element2)
            df1 = pd.DataFrame({"Name": data_element1})
            df2 = pd.DataFrame({"Year": year, "Mileage": mileage, "Price": price})
            df3 = pd.DataFrame({"Retailer": data_element3})
            df = pd.concat([df1, df2, df3], axis=1)
            df['Timestamp'] = datetime.now().strftime('%d/%m/%Y')

            if 'Updated Price' not in existing_df.columns:
                existing_df['Updated Price'] = None

            df[['Year', 'Mileage', 'Price']] = df[['Year', 'Mileage', 'Price']].astype(str)
            existing_df[['Year', 'Mileage', 'Price']] = existing_df[['Year', 'Mileage', 'Price']].astype(str)

            existing_df['Year'] = existing_df['Year'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x.replace('.', '', 1).isdigit() else x)
            df['Year'] = df['Year'].apply(lambda x: str(int(float(x))) if pd.notnull(x) and x.replace('.', '', 1).isdigit() else x)

            # Update existing data with new data
            for index, new_row in df.iterrows():
                match = existing_df[(existing_df['Name'] == new_row['Name']) & (existing_df['Year'] == new_row['Year']) & (existing_df['Mileage'] == new_row['Mileage'])]
                if not match.empty:
                    price_update_condition = (match['Price'] != new_row['Price']) & (match['Updated Price'] != new_row['Price'])
                    if price_update_condition.any():
                        existing_df.loc[match.index, 'Updated Price'] = new_row['Price']
                        existing_df.loc[match.index, 'Date Price Change'] = datetime.now().strftime('%d/%m/%Y')
                else:
                    existing_df = pd.concat([existing_df, pd.DataFrame([new_row]).reset_index(drop=True)], ignore_index=True)

            existing_df.drop_duplicates(subset=['Name', 'Year', 'Mileage', 'Price', 'Updated Price'], keep='first', inplace=True)

        # Write the updated data to the Excel file
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            existing_df.to_excel(writer, sheet_name=model_name, index=False)
        
        # Car models sold logic
        today = datetime.now().strftime('%d/%m/%Y')
        # Filter DataFrame for entries with 'Solgt' in 'Price' and 'Updated Price' as today's date
        solgt_today_price = existing_df[(existing_df['Price'] == 'Solgt') & (existing_df['Timestamp'] == today)]
        solgt_today_updated_price = existing_df[(existing_df['Updated Price'] == 'Solgt') & (existing_df['Date Price Change'] == today)]

        # Count these entries
        solgt_count_price = solgt_today_price.shape[0]
        solgt_count_updated_price = solgt_today_updated_price.shape[0]

        # Store counts in a variable
        models_solgt_today = solgt_count_price + solgt_count_updated_price
        sold_cars_data[model_name] = models_solgt_today

        # Optional: You can use this variable 'total_solgt_today' as needed
        print(f"Total 'Solgt' entries in Price and Updated Price columns for today: {models_solgt_today}")

    # Scrape Cars Listed from all models
    # Initialize existing_df as an empty DataFrame
    try:
        existing_df_listed = pd.read_excel(excel_path, sheet_name=f'{car_brand}_listed')
    except FileNotFoundError:
        existing_df_listed = pd.DataFrame(columns=["Date"] + [model["name"] for model in models])

    # Get today's date
    today_date = datetime.now().strftime('%d/%m/%Y')

    # Check if today's date is in the "Date" column
    if today_date in existing_df_listed['Date'].values:
        # If today's date is present, check if the corresponding columns are empty
        empty_columns = existing_df_listed.loc[existing_df_listed['Date'] == today_date, [model["name"] for model in models]].isnull().all()
        
        # If any of the corresponding columns are empty, append the data to those columns
        if empty_columns.any():
            empty_columns = empty_columns[empty_columns].index  # Get names of empty columns
            for column in empty_columns:
                existing_df_listed.loc[existing_df_listed['Date'] == today_date, column] = listed_cars_data.get(column)
    else:
        # If today's date is not present, create a new row and concat it
        new_row = {'Date': today_date}
        new_row.update({model: listed_cars_data.get(model, 0) for model in [model["name"] for model in models]})
        existing_df_listed = pd.concat([existing_df_listed, pd.DataFrame([new_row])], ignore_index=True)

    # Save the updated DataFrame back to Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        existing_df_listed.to_excel(writer, sheet_name=f'{car_brand}_listed', index=False)

    # Scrape Cars sold from all models
    driver.quit()

    # Initialize existing_df as an empty DataFrame
    try:
        existing_df_listed = pd.read_excel(excel_path, sheet_name=f'{car_brand}_listed')
    except FileNotFoundError:
        existing_df_listed = pd.DataFrame(columns=["Date"] + [f"{model['name']} Sold" for model in models])

    # Get today's date
    today_date = datetime.now().strftime('%d/%m/%Y')

    # Check if today's date is in the "Date" column
    if today_date in existing_df_listed['Date'].values:
        # If today's date is present, check if the corresponding columns are empty
        empty_columns = existing_df_listed.loc[existing_df_listed['Date'] == today_date, [f"{model['name']} Sold" for model in models]].isnull().all()
        
        # If any of the corresponding columns are empty, append the data to those columns
        if empty_columns.any():
            empty_columns = empty_columns[empty_columns].index  # Get names of empty columns
            for column in empty_columns:
                model_name = column.replace(' Sold', '')  # Remove ' Sold' to get the model name
                existing_df_listed.loc[existing_df_listed['Date'] == today_date, column] = sold_cars_data.get(model_name, 0)

    else:
        # If today's date is not present, create a new row and concat it
        new_row = {'Date': today_date}
        new_row.update({f"{model['name']} Sold": sold_cars_data.get(model['name'], 0) for model in models})
        existing_df_listed = pd.concat([existing_df_listed, pd.DataFrame([new_row])], ignore_index=True)

    # Save the updated DataFrame back to Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        existing_df_listed.to_excel(writer, sheet_name=f'{car_brand}_listed', index=False)

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
            
            # Convert DataFrame to JSON
            json_data = df.to_json(orient='records')
            
            # Write JSON data to file
            output_json_file = f"{sheet_name.lower()}.json"  # Output JSON file name based on sheet name
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

    input_excel_file = f'{car_brand}.xlsx'  # Provide the path to your Excel file

    excel_to_json(input_excel_file)

    # Upload the updated file to PythonAnywhere
    upload_url = f'https://www.pythonanywhere.com/api/v0/user/{username}/files/path{pythonanywhere_path}'

    for attempt in range(3):
        with open(excel_path, 'rb') as file:
            files = {'content': (excel_path, file, 'application/octet-stream')}
            response = requests.post(upload_url, headers=headers, files=files)
        if response.status_code == 200:
            print('File uploaded successfully to PythonAnywhere.')
            break
        else:
            print(f'Error uploading file to PythonAnywhere: {response.text}')
            if attempt == 2:
                print("Max attempts reached, exiting loop.")

if __name__ == "__main__":
    main_flow()