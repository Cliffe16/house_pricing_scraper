from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def sel_scraper(driver, url):
	# Navigate to the url
	driver.get(url)

	# 1. Phone number
	try:
		# Save the contact button in a variable
		contact_buttons = driver.find_elements(By.CSS_SELECTOR, "button.detail-listing-open-phone-modal")

		# Iterate through the buttons and find the ones displayed to click 
		for contact_button in contact_buttons:
			if contact_button.is_displayed():
				driver.execute_script("arguments[0].click()", contact_button) # Use JS clicks, to bypass .click() element interception error
				break

		# Wait for the number to render
		phone_number = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.block.text-xl")))
		phone_number = phone_number.text

	except TimeoutException:
		print(f"Could not find phone_number for {url}")
		phone_number = None

	# 2. Property description
	listing_description = driver.find_element(By.ID, "truncatedDescription")
	listing_description = listing_description.text

	# 3. Date of listing
	created_at = driver.find_element(By.XPATH, "//span[contains(text(), 'Created At')]") # conuld not find elelment with css selector
	created_at = created_at.text.replace("Created at:", "")

	# Store the data in a dictionary
	sel_data = {
		"phone_number": phone_number,
		"listing_description": listing_description,
		"date_of_listing": created_at
		}

	return sel_data

