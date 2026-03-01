import psycopg2
import psycopg2.extras
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def clean_data():
	# Connect to db
	conn = psycopg2.connect(
		host=os.getenv('HOST'),
		database=os.getenv('DATABASE'),
		user=os.getenv('USER'),
		password=os.getenv('PASSWORD'),
		port=5432
		)
	cur = conn.cursor()

	try:
		print("Extracting Data")
		# Read from the staging table
		raw_data = pd.read_sql("SELECT * FROM raw_data;", con=conn)

		print("Transforming Data")
		# Format the date to database format
		raw_data['date_of_listing'] = pd.to_datetime(raw_data['date_of_listing'], errors='coerce').dt.date

		# Clean the price
		raw_data['listing_price'] = raw_data['listing_price'].astype(str).str.strip()
		raw_data['listing_price'] = pd.to_numeric(raw_data['listing_price'], errors='coerce')

		# Clean bedrooms and bathrooms
		for col in ['bedroom_count', 'bathroom_count']:
			if col in raw_data.columns:
				raw_data[col] = raw_data[col].astype(str).str.split(' ').str[0]
				raw_data[col] = pd.to_numeric(raw_data[col], errors='coerce').astype('Int64')

		# Convert null values to database format
		data = raw_data.astype(object).where(pd.notna(raw_data), None)

		# Loading clean data to db
		print("Loading Data")
		table_name = "cleaned_data"

		# Define the new database schema
		create_table_query = f"""
		CREATE TABLE {table_name}(
			listing_id INTEGER,
			listing VARCHAR(100),
			category TEXT,
			bedroom_count INTEGER,
			bathroom_count INTEGER,
			offer_type TEXT,
			location TEXT,
			listing_price NUMERIC,
			agency TEXT,
			url TEXT,
			phone_number VARCHAR(50),
			listing_description TEXT,
			date_of_listing DATE
			);
			"""

		# Drop and recreate the clean table
		cur.execute(f"DROP TABLE IF EXISTS {table_name};")
		cur.execute(create_table_query)

		# Generate placeholders for the bulk insert
		cols = ", ".join([f'"{col}"' for col in data.columns])
		placeholders = ", ".join(["%s"] * len(data.columns))
		insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

		# Convert the data into a list of tuples
		data_tuples = [tuple(row) for row in data.to_numpy()]
		cur.executemany(insert_query, data_tuples)

		# Commit the transaction
		conn.commit()
		print(f"Data successfully cleaned: {len(data)} for {table_name}")

	except Exceptions as e:
		conn.rollback()
		print(f"Data cleaning failed: {e}")
		raise e
	finally:
		cur.close()
		conn.close()

if __name__ == "__main__":
	clean_data()
