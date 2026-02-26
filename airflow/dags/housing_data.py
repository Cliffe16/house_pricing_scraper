from airflow.operators.python import PythonOperator
from airflow import DAG
from datetime import datetime, timedelta
import sys
import os

# Trace the symlink back to the actual project folder dynamically
current_file_path = os.path.realpath(__file__)
dags_folder = os.path.dirname(current_file_path)
airflow_folder = os.path.dirname(dags_folder)
project_root = os.path.dirname(airflow_folder)

# Inject the paths dynamically
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'venv/lib/python3.12/site-packages'))

from dotenv import load_dotenv
from main_scraper import run_pipeline

# Load the .env file using the dynamic root path
load_dotenv(os.path.join(project_root, '.env'))

with DAG(
	"housing_scraper",
	default_args={
		"depends_on_past": False,
		"email_on_failure": False,
		"retries": 1,
		"retry_delay": timedelta(minutes=5)
		},
	description="BuyRentKenya real estate scraper",
	schedule="@daily",
	start_date=datetime(2026, 2, 25),
	catchup=False

) as dag:
	housing_scraper = PythonOperator(
	task_id='house_scraper',
	python_callable=run_pipeline
	)





