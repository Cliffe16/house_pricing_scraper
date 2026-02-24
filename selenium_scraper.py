from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_phone_no(listing_url):
	chrome_options = Options()
	chrome_options.add_argument("--headless") # run chrome without gui
	chrome_options.add_argument("--no-sandbox") # account for incompatible linux environments
	chrome_options.add_argument("--disable-dev-shm-usage") # account for chrome's memory usage

	# Launch the browser
	driver = webdriver.Chrome(options=chrome_options)
	
	#Navigate to the url
	driver.get(listing_url)

