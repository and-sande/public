import os
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
import prefect
import requests
import time
import subprocess
from prefect import flow, task
from datetime import datetime, timedelta
import chromedriver_autoinstaller
# from pyvirtualdisplay import Display
# display = Display(visible=0, size=(800, 800))  
# display.start()

@task
def strompriser_update_price():
# Define the Excel file path

    chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
    chrome_options = webdriver.ChromeOptions()    
    # Add your options as needed    
    options = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1280,800", # Set a standard window size
    "--disable-software-rasterizer"  # Disable software
]

    for option in options:
        chrome_options.add_argument(option)
    
    driver = webdriver.Chrome(options = chrome_options)
    # Set up Selenium WebDriver

    # Ensure the directory exists before saving files
    os.makedirs("Strompriser", exist_ok=True)

    current_date = datetime.now()
    todays_date = current_date.strftime("%Y-%m-%d")
    next_day = current_date + timedelta(days=1)
    next_day = next_day.strftime("%Y-%m-%d")

    excel_today = "./Strompriser/strompriser_today.xlsx"
    excel_yesterday = "./Strompriser/strompriser_yesterday.xlsx"

    # Load the webpage
    wait = WebDriverWait(driver, 30)
    driver.get(f"https://data.nordpoolgroup.com/auction/day-ahead/prices?deliveryDate={next_day}&deliveryAreas=EE,LT,LV,AT,BE,FR,GER,NL,PL,DK1,DK2,FI,NO1,NO2,NO3,NO4,NO5,SE1,SE2,SE3,SE4&currency=EUR&aggregation=Hourly")

    # Wait for the table to load
    table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='presentation'] div[class='dx-scrollable-container']")))
    time.sleep(1)

    # Extract table data
    rows = table.find_elements(By.TAG_NAME, 'tr')
    table_data = []
    for row in rows:
        columns = row.find_elements(By.TAG_NAME, 'td')
        row_data = [column.text for column in columns]
        table_data.append(row_data)

    # Create DataFrame from table data
    df = pd.DataFrame(table_data)

    # Add header row manually
    header_row = ["", "EE", "LT", "LV", "AT", "BE", "FR", "GER", "NL", "PL", "DK1", "DK2", "FI", "NO1", "NO2", "NO3", "NO4", "NO5", "SE1", "SE2", "SE3", "SE4"]

    # Ensure the number of columns matches the number of elements in the header row
    if len(df.columns) != len(header_row):
        raise ValueError("Number of columns in DataFrame doesn't match the number of elements in the header row.")

    # Assign the header row to the DataFrame
    df.columns = header_row

    # Add time periods to the first column
    time_periods = [
        "00:00 - 01:00", "01:00 - 02:00", "02:00 - 03:00", "03:00 - 04:00",
        "04:00 - 05:00", "05:00 - 06:00", "06:00 - 07:00", "07:00 - 08:00",
        "08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00",
        "12:00 - 13:00", "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00",
        "16:00 - 17:00", "17:00 - 18:00", "18:00 - 19:00", "19:00 - 20:00",
        "20:00 - 21:00", "21:00 - 22:00", "22:00 - 23:00", "23:00 - 00:00", ""
    ]

    # Ensure the number of time periods matches the number of rows in the DataFrame
    if len(time_periods) != len(df):
        raise ValueError("Number of time periods doesn't match the number of rows in the DataFrame.")

    # Insert the time periods into the DataFrame
    df.insert(0, "Time Period", time_periods)

    # Replace commas with dots
    df.iloc[:, 1:] = df.iloc[:, 1:].replace(',', '.', regex=True)

    # Convert numeric values to floats
    # Replace empty strings with NaN and then convert to float
    df.iloc[:, 1:] = df.iloc[:, 1:].replace('', np.nan).astype(float)

    # Calculate min, mean, and max for each column (except the first)
    summary_stats = df.iloc[:, 1:].agg(['min', 'mean', 'max'])

    # Export DataFrame and summary statistics to Excel
    with pd.ExcelWriter(excel_today, engine='openpyxl', mode='w') as writer:
        # Write DataFrame to 'Day_ahead' sheet
        df.to_excel(writer, sheet_name="Day_ahead", index=False)

        # Write summary statistics to 'Summary' sheet
        summary_stats.to_excel(writer, sheet_name="Summary", index=True)

    #sheet yesterday's price-----
    # Set up Selenium WebDriver
    driver = webdriver.Chrome(options = chrome_options)
    wait = WebDriverWait(driver, 30)

    # Load the webpage
    driver.get(f"https://data.nordpoolgroup.com/auction/day-ahead/prices?deliveryDate={todays_date}&deliveryAreas=EE,LT,LV,AT,BE,FR,GER,NL,PL,DK1,DK2,FI,NO1,NO2,NO3,NO4,NO5,SE1,SE2,SE3,SE4&currency=EUR&aggregation=Hourly")

    # Wait for the table to load
    table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='presentation'] div[class='dx-scrollable-container']")))
    time.sleep(1)

    # Extract table data
    rows = table.find_elements(By.TAG_NAME, 'tr')
    table_data = []
    for row in rows:
        columns = row.find_elements(By.TAG_NAME, 'td')
        row_data = [column.text for column in columns]
        table_data.append(row_data)

    # Create DataFrame from table data
    df = pd.DataFrame(table_data)

    # Add header row manually
    header_row = ["", "EE", "LT", "LV", "AT", "BE", "FR", "GER", "NL", "PL", "DK1", "DK2", "FI", "NO1", "NO2", "NO3", "NO4", "NO5", "SE1", "SE2", "SE3", "SE4"]

    # Ensure the number of columns matches the number of elements in the header row
    if len(df.columns) != len(header_row):
        raise ValueError("Number of columns in DataFrame doesn't match the number of elements in the header row.")

    # Assign the header row to the DataFrame
    df.columns = header_row

    # Add time periods to the first column
    time_periods = [
        "00:00 - 01:00", "01:00 - 02:00", "02:00 - 03:00", "03:00 - 04:00",
        "04:00 - 05:00", "05:00 - 06:00", "06:00 - 07:00", "07:00 - 08:00",
        "08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00",
        "12:00 - 13:00", "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00",
        "16:00 - 17:00", "17:00 - 18:00", "18:00 - 19:00", "19:00 - 20:00",
        "20:00 - 21:00", "21:00 - 22:00", "22:00 - 23:00", "23:00 - 00:00", ""
    ]

    # Ensure the number of time periods matches the number of rows in the DataFrame
    if len(time_periods) != len(df):
        raise ValueError("Number of time periods doesn't match the number of rows in the DataFrame.")

    # Insert the time periods into the DataFrame
    df.insert(0, "Time Period", time_periods)

    # Replace commas with dots
    df.iloc[:, 1:] = df.iloc[:, 1:].replace(',', '.', regex=True)

    # Convert numeric values to floats
    # Replace empty strings with NaN and then convert to float
    df.iloc[:, 1:] = df.iloc[:, 1:].replace('', np.nan).astype(float)

    # Calculate min, mean, and max for each column (except the first)
    summary_stats = df.iloc[:, 1:].agg(['min', 'mean', 'max'])

    # Export DataFrame and summary statistics to Excel
    with pd.ExcelWriter(excel_yesterday, engine='openpyxl', mode='w') as writer:
        # Write DataFrame to 'Day_ahead' sheet
        df.to_excel(writer, sheet_name="previous_day", index=False)

        # Write summary statistics to 'Summary' sheet
        summary_stats.to_excel(writer, sheet_name="previous_summary", index=True)

    # Close the WebDriver
    driver.quit()

time.sleep(1)

@task
def upload_file_today():
    max_attempts = 3 
    for attempt in range (1, max_attempts + 1):
        # Define PythonAnywhere username and API token
        username = 'andsande'
        api_token = 'f76bb882c94ff3286f770c494534bb03b9ed27a4'

        # Define file path of the Excel file to upload
        excel_today = "./Strompriser/strompriser_today.xlsx"
        file_path = excel_today

        # Define PythonAnywhere file path to upload the file to
        pythonanywhere_file_path = '/home/andsande/mysite/templates/strompriser_today.xlsx'

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

@task
def upload_file_yesterday():
    max_attempts = 3 
    for attempt in range (1, max_attempts + 1):
        # Define PythonAnywhere username and API token
        username = 'andsande'
        api_token = 'f76bb882c94ff3286f770c494534bb03b9ed27a4'

        # Define file path of the Excel file to upload
        excel_yesterday = "./Strompriser/strompriser_yesterday.xlsx"
        file_path = excel_yesterday

        # Define PythonAnywhere file path to upload the file to
        pythonanywhere_file_path = '/home/andsande/mysite/templates/strompriser_yesterday.xlsx'
        
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
            print('excel file yesterday uploaded successfully to PythonAnywhere.')
            break

        print(f'Error uploading excel yesterday file to PythonAnywhere: {response.text}')
        print(response.status_code)
        print(response.text)

        if attempt == max_attempts:
            print("Max attempts reached, exiting loop...")

@task
def Reload_PY_server():
    
    # Replace 'your_username' and 'your_api_token' with your PythonAnywhere username and API token
    username = 'andsande'
    api_token = 'f76bb882c94ff3286f770c494534bb03b9ed27a4'

    # Construct the URL for reloading the website
    url = f'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/andsande.pythonanywhere.com/reload/'

    # Send the POST request with the API token for authentication
    response = requests.post(url, headers={'Authorization': f'Token {api_token}'})

    # Check the response status
    if response.status_code == 200:
        print("Website reloaded successfully!")
    else:
        print(f"Failed to reload website. Status code: {response.status_code}")

@flow(log_prints=True, name="Update Strømpriser App and Reload Server")
def GSP_strompriser_Flow():
    strompriser_update_price()
    upload_file_today()
    upload_file_yesterday()
    Reload_PY_server()

GSP_strompriser_Flow()
