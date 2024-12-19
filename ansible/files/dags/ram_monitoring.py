from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.smtp.operators.smtp import EmailOperator
import psutil
from datetime import datetime, timedelta

def check_ram_usage():
    ram = psutil.virtual_memory()
    if ram.percent > 80:  # if RAM usage is over 80%
        return f"WARNING: High RAM usage detected: {ram.percent}%"
    return f"RAM usage normal: {ram.percent}%"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['your_email@example.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ram_monitoring',
    default_args=default_args,
    description='Monitor RAM usage and send email alerts',
    schedule_interval=timedelta(minutes=30),
) as dag:

    monitor_ram = PythonOperator(
        task_id='check_ram',
        python_callable=check_ram_usage,
    )

    send_email = EmailOperator(
        task_id='send_notification',
        to='your_email@example.com',
        subject='RAM Usage Alert',
        html_content="{{ task_instance.xcom_pull(task_ids='check_ram') }}",
    )

    monitor_ram >> send_email