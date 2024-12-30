import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime

# Define Chrome WebDriver path dynamically based on the current working directory
current_directory = os.getcwd()
chrome_driver_path = os.path.join(current_directory, 'chromedriver')
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()

# Disable images to speed up loading
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

# Run in headless mode for faster scraping
options.add_argument("--headless")
options.add_argument("--log-level=3")  # Suppress most logs
options.page_load_strategy = "eager"

driver = webdriver.Chrome(service=service, options=options)

# Set timeouts
driver.set_script_timeout(500)  # Script execution timeout
driver.set_page_load_timeout(500)  # Page load timeout

# Base URL and data list
base_url = "https://www.willhaben.at/iad/immobilien/eigentumswohnung/wien?page="
data = []
progress_file = "progress.txt"
temp_file = "scraped_properties_temp.csv"

# Save scraped data to a CSV file
def save_scraped_data(data, filename=temp_file):
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

# Read the last progress from the file
def read_progress():
    if os.path.exists(progress_file):
        with open(progress_file, "r") as file:
            return int(file.read().strip())
    return 1  # Start from page 1 if no progress file exists

# Update progress to a file
def update_progress(page):
    with open(progress_file, "w") as file:
        file.write(str(page))

try:
    # Start scraping from where it left off
    start_page = read_progress()
    print(f"Resuming from page {start_page}...")

    for page in range(start_page, 101):  # Scrape up to page 100
        print(f"Scraping page {page}...")
        try:
            driver.get(base_url + str(page))

            # Scroll through the page to load all content
            scroll_pause_time = 0.5  # Pause between scrolls
            total_scrolls = 30  # Number of scrolls based on page length

            for i in range(total_scrolls):
                driver.execute_script(f"window.scrollTo(0, {i * 500});")
                time.sleep(scroll_pause_time)

            # Wait for elements to load
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "hPOcQO"))
            )

            # Collect data from the page
            elements_hPOcQO = driver.find_elements(By.CLASS_NAME, "hPOcQO")
            for element in elements_hPOcQO:
                text = element.text.strip()
                url = element.get_attribute("href")
                if text:
                    data.append({"text": text, "url": url})
            update_progress(page)  # Save progress after successful scrape

        except TimeoutException:
            print(f"Timeout on page {page}. Retrying...")
            continue  # Retry the same page
        except Exception as e:
            print(f"Error on page {page}: {e}")
            save_scraped_data(data)  # Save data before exiting
            break  # Stop the loop for debugging

finally:
    driver.quit()
    save_scraped_data(data)  # Save whatever was scraped

# Extract specific fields from the scraped data
def extract_field(entry):
    text = entry['text']
    title = text.split('\n')[0]  # Title is the first line
    postcode_match = re.search(r'\b\d{4}\b', text)  # Look for a 4-digit postcode
    postcode = postcode_match.group(0) if postcode_match else None
    size_match = re.search(r'\d+\s*m²', text)  # Look for size in m²
    size = size_match.group(0) if size_match else None
    price_match = re.search(r'€\s[\d.,]+', text)  # Look for price
    price = price_match.group(0) if price_match else None
    return {
        "Title": title,
        "Postcode": postcode,
        "Size": size,
        "Price": price,
        "URL": entry['url']
    }

# Process the scraped data with regex
regex_data = [extract_field(entry) for entry in data]

# Create a DataFrame for the cleaned data
df_regex = pd.DataFrame(regex_data)

# Generate a descriptive filename
current_date = datetime.now().strftime("%Y-%m-%d")
first_page = read_progress()
last_page = first_page + len(data) // len(df_regex.columns) - 1  # Estimate the last page
file_name = f"scraped_properties_pages_{first_page}_to_{last_page}_{current_date}.csv"

# Save the final data to the file
df_regex.to_csv(file_name, index=False)
print(f"Scraping complete. Data saved to '{file_name}'.")
