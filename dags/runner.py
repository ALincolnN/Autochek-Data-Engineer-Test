import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from datetime import datetime, timedelta

import pendulum

runner_path = '/src/scrapper.py'
local_timezone = pendulum.timezone('Africa/Nairobi')

default_args = {
    'owner': 'airflow',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

dag1 = DAG(
    dag_id='data_scrapper',
    default_args=default_args,
    description='Dag running scrapper file',
    start_date=datetime(2023, 12, 1),
    schedule_interval='0 1,23 * * *',
    catchup=False
)
# run_task = BashOperator(
#     task_id='Task1',
#     dag=dag1,
#     bash_command=f'python {runner_path} get_currency_conversion'
# )


