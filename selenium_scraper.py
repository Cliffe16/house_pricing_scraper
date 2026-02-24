from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def sel_scraper(url):
	chrome_options = Options()
	chrome_options.add_argument("--headless") # run chrome without gui
	chrome_options.add_argument("--no-sandbox") # account for incompatible linux environments
	chrome_options.add_argument("--disable-dev-shm-usage") # account for chrome's memory usage

	# Launch the browser
	driver = webdriver.Chrome(options=chrome_options)

	# Navigate to the url
	driver.get(url)

	# 1. Phone number
	# Save the contact button in a variable
	contact_button = driver.find_element(By.CSS_SELECTOR, "button.detail-listing-open-phone-modal")

	# Click the button
	contact_button.click()

	# Wait for the number to render
	phone_number = WebDriverWait(driver, 5). until(EC.presence_of_element_located(By.CSS_SELECTOR, "span.block"))
	phone_number = phone_number.text

	# 2. Property description
	listing_description = driver.find_element(By.ID, "truncatedDescription")
	listing_description = listing_description.text

	# 3. Date of listing
	created_at = driver.find_element(By.CSS_SELECTOR, "span.text-sm")
	created_at = created_at.text

	# Store the data in a dictionary
	sel_data = {
		"phone_number": phone_number,
		"listing_description": listing_description,
		"date_of_listing": created_at
		}

	#Close the browser
	driver.quit()

	return sel_data

