from airflow.operators.python import PythonOperator
from airflow import DAG
from datetime import datetime, timedelta
import sys
sys.path.append("/home/admin/house_pricing_scraper")
from main_scraper import run_pipeline

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





