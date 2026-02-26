# Real Estate Housing Scraper

This is a mini project from Lux Dev HQ meant to solidify web scraping and orchestration. The project contains a robust data pipeline that scrapes real estate listings from BuyRent Kenya using a hybrid approach: **Requests/BeautifulSoup** for static content and **Selenium** for dynamic elements with **Airflow** as the orchestrator.

## Tools
* **Orchestration:** Apache Airflow 2.10.0
* **Scraping:** Selenium & BeautifulSoup4
* **Storage:** psql
* **Environment:** Python 3.12 	

## Project Structure
```text
house_pricing_scraper/
├── airflow/
│   └── dags/
│       └── housing_data.py      # The DAG definition
├── main_scraper.py              # extraction logic & BeautifulSoup parser
├── selenium_scraper.py          # Chrome driver interactions
├── requirements.txt             # Project dependencies
└── .env                         # Database & URL credentials
```

## How the pipeline works
The project is designed to run in a background environment:
1. **Airflow trigger:** The `housing_scraper` DAG is triggered daily at midnight
2. **Project paths:** At runtime, the DAG injects the project's virtual environment and directory path into the system's `sys.path`. This allows the Airflow scheduler service to access the project's packages and python functions without altering system-wide Python configurations for this particular project.
3. **Orchestration Function:** Airflow calls `run_pipeline()`, which initializes a headless Chrome browser to avoid system crashes.
4. **Hybrid Scraper:** The script iterates through the 'for-sale' and 'for-rent' URLs and their respective pages(`range(1,21)`)
	* **Requests/BeautifulSoup4:** parses static HTML content(prices, no_bedrooms, no_bathrooms etc.)
	* **Selenium:** parses agency `phone_numbers` hidden behind a contact button and `date_of_listing` both behind the `listing's link`
5. **Data Consolidation & Upload:** The scraped dictionary is converted into a Pandas DataFrame. Using an SQLAlchemy engine, the data is pushed to a PostgreSQL database using `if_exists='replace` to refresh the `raw_data` table daily.


## Setup & Installation
```text
git clone <your-repo-url>
cd house_pricing_scraper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
## Challenges
Building the pipeline required solving some orchestration and environmental issues:
### 1. Airflow Parsing Timeouts 
* **Challenge:** Initially, the browser initialization and scraping loops were written at the script's root level. Because Airflow scans DAG files every 30 seconds to update its UI, it was accidentally executing the web scraper during the parsing phase, leading to timeout errors.
* **Solution:** Wrapped the execution logic into the `run_pipeline()` function. Added an `if __name__ == "__main__":` block to allow local terminal testing while completely hiding the heavy execution logic from Airflow's parsing engine.

### 2. Headless Chrome Hanging in Background Workers
* **Challenge:** Selenium ran perfectly in the foreground terminal but threw `urllib3.exceptions.ReadTimeoutError` when executed by Airflow's background worker due to memory limits and hardware acceleration conflicts.
* **Solution:** Added `--no-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu`, to the ChromeDriver configuration for Linux background processes and forced a standard `--window-size=1920,1080` to prevent unpredictable rendering hangs.

### 3. Dependency Hell 
* **Challenge:** Installing the `apache-airflow-providers-postgres` plugin fractured the virtual environment as `pip` introduced newer, incompatible versions of `pydantic` and `typing_extensions`. This broke Airflow's internal database migrations with a missing `mysql_drop_foreignkey_if_exists` error.
* **Solution:** Executed a clean wipe of the `venv` and rebuilt it using a **strict constraints file** (`constraints-2.10.0/constraints-3.12.txt`). This forced all third-party libraries to align with Airflow's expected dependencies.	

### 4. Systemd vs. Local Virtual Environment Paths
* **Challenge:** The Airflow Scheduler runs as a Linux `systemd` service, meaning it defaulted to the global system Python. It threw `ModuleNotFoundError` for Selenium because it was blind to the project's virtual environment.
* **Solution:** Instead of hardcoding paths into the Linux systemd service (which is hard to maintain), I implemented dynamic path injection (`sys.path.append`) directly at the top of the DAG file.

### 5. Version Control Integration
* **Challenge:** Airflow expects DAGs to live in its global `~/airflow/dags` directory, but the DAG needed to be tracked in the local project's Git repository.
* **Solution:** Kept the master DAG file inside the Git-tracked project directory and created a **symbolic link** (`ln -s`) in the Airflow folder. This allows Git to track changes while Airflow reads the live, updated file seamlessly.

