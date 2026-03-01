import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium_scraper import sel_scraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# Load environment variables for database connection
load_dotenv()

user=os.getenv('DB_USER')
password=os.getenv('PASSWORD')
host=os.getenv('DB_HOST')
database=os.getenv('DATABASE')


def scraper(driver, url):
	html = requests.get(url).text
	soup = BeautifulSoup(html, "html.parser")

	# Initialize empty list to contain the listings
	listings = []

	# Select listing cards
	cards = soup.select("div.listing-card")

	# Iterate through the listing cards
	for card in cards:
		# Listing id
		listing_id = card.select_one("div.search-listing-open-phone-modal[data-bi-listing-id]")
		listing_id = listing_id['data-bi-listing-id']

		# Property description
		listing = card.select_one("h2.font-semibold")
		listing = listing.text.strip() if listing else None

		# Category
		listing_category = card.select_one("div.relative[data-bi-listing-category]")
		category = listing_category['data-bi-listing-category']

		# Number of bedrooms
		bedroom_count = card.select_one("span.whitespace-nowrap[data-cy='card-bedroom_count']")
		bedroom_count = bedroom_count.text.strip() if bedroom_count else None

		# Number of bathrooms
		bathroom_count = card.select_one("span.whitespace-nowrap[data-cy='card-bathroom_count']")
		bathroom_count = bathroom_count.text.strip() if bathroom_count else None

		# Offer Type
		offer_type = card.select_one("div.search-listing-open-phone-modal[data-bi-listing-offer-type]")
		offer_type = offer_type['data-bi-listing-offer-type']

		# Location
		location = card.select_one("p.w-full")
		location = location.text.strip() if location else None

		# Listing Price
		listing_price = card.select_one("div.relative[data-bi-listing-price]")
		listing_price = listing_price['data-bi-listing-price']

		# Agency
		agency = card.select_one("div.search-listing-open-phone-modal[data-bi-listing-agent]")
		agency = agency["data-bi-listing-agent"]

		# Listing link
		base_url = os.getenv('BASE_URL')

		url = card.select_one("a.absolute")
		url = base_url + url['href'] if url else None

		# Call the selelnium scraper and store the result
		sel_staged_data = sel_scraper(driver, url)

		# Confirm all requred fields exist
		if all([listing_id, listing, category, bedroom_count, bathroom_count, offer_type,location, listing_price, agency, url]):
			current_listings = {
				"listing_id": listing_id,
				"listing": listing,
				"category": category,
				"bedroom_count": bedroom_count,
				"bathroom_count": bathroom_count,
				"offer_type": offer_type,
				"location": location,
				"listing_price": listing_price,
				"agency": agency,
				"url": url
				}
			current_listings.update(sel_staged_data)
			listings.append(current_listings)

	return listings

# I've moved this setup to this function from the selenium_scraper to improve the speed of
# browser connection

def run_pipeline():

	# Initialize postgres connection string
	conn = psycopg2.connect(
		host=host,
		database=database,
		user=user,
		password=password,
		port="5432"
		)
	cur = conn.cursor()

	# Set up selenium's browser options
	chrome_options = Options()
	chrome_options.add_argument("--headless") # run chrome without gui
	chrome_options.add_argument("--no-sandbox") # account for incompatible linux environment
	chrome_options.add_argument("--disable-dev-shm-usage") # account for chrome's memory
	# airflow optimizations
	chrome_options.add_argument("--disable-gpu") # prevents headless chrome from crashing
	chrome_options.add_argument(" --window-size=1920,1080") # define size to avoid unpredictable rendering

	# Launch the browser
	driver = webdriver.Chrome(options=chrome_options)

	# Fetch data from both urls
	try:
		staged_data = []

		# Define urls from the real estate listings
		urls = os.getenv('URLS').split(",")

		for url in urls:
			scraped_data = scraper(driver, url)
			staged_data.append(pd.DataFrame(scraped_data))

			for page in range(2, 21):
				page_url = f"{url}?page={page}"
				page_data = scraper(driver, page_url)
				staged_data.append(pd.DataFrame(page_data))

		# Combine the data
		data = pd.concat(staged_data, ignore_index=True)

		# Transform the data for database upload
		data = data.astype(object).where(pd.notna(data), None)
		columns = ",".join([f'"{col}" TEXT' for col in data.columns])

		# Upload to database
		cur.execute("DROP TABLE IF EXISTS raw_data;") # Remove existing data
		cur.execute(f"CREATE TABLE raw_data ({columns});")

		# Create a string of placeholders
		placeholders = ", ".join(["%s"] * len(data.columns))
		insert = f"INSERT INTO raw_data VALUES ({placeholders})" 

    		# Convert the entire dataframe into a list of tuples for the database
		data_tuples = [tuple(row) for row in data.to_numpy()]

    		# Execute the insert query
		cur.executemany(insert, data_tuples)

		# Confirm database upload
		data_read = pd.read_sql("SELECT * FROM raw_data LIMIT 10;", con=conn)
		print(data_read)

		# Commit changes to database if all the data exists
		conn.commit()
	finally:
		# Close the browser
		driver.quit()
		cur.close()
		conn.close()

if __name__ == "__main__":
	run_pipeline()
