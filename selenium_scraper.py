from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_phone_no(listing_url):
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-dev-shm-usage")

	# Launch the browser
	driver = webdriver.Chrome(options=chrome_options)

