import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium_scraper import sel_scraper

# Define urls from the real estate listings
urls = ["https://www.buyrentkenya.com/houses-for-rent",
"https://www.buyrentkenya.com/houses-for-sale"]

def scrape(url):
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
		base_url = "https://www.buyrentkenya.com"

		url = card.select_one("a.absolute")
		url = base_url + url['href'] if url else None

		# Call the selelnium scraper and store the result
		sel_staged_data = sel_scraper(url)

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

# Fetch data from both urls
staged_data = []

for url in urls:
	scraped_data = scrape(url)
	staged_data.append(pd.DataFrame(scraped_data))

	for page in range(2, 21):
		page_url = f"{url}?page={page}"
		page_data = scrape(page_url)
		staged_data.append(pd.DataFrame(page_data))

data = pd.concat(staged_data, ignore_index=True)
print(data)

