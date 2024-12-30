from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.operators.email import EmailOperator
import psutil
from datetime import datetime, timedelta
import logging
import os

def check_ram_usage(**context):
    """
    Check RAM usage and log the results
    """
    try:
        ram = psutil.virtual_memory()

        message = (
            f"\n=== RAM Usage Report ===\n"
            f"Total: {ram.total / (1024 * 1024 * 1024):.2f} GB\n"
            f"Used: {ram.used / (1024 * 1024 * 1024):.2f} GB\n"
            f"Free: {ram.free / (1024 * 1024 * 1024):.2f} GB\n"
            f"Percentage: {ram.percent}%\n"
            f"========================="
        )

        logging.info(message)

        return {
            "ram_percent": ram.percent,
            "message": message,
            "alert": ram.percent > 60
        }

    except Exception as e:
        logging.error(f"Error checking RAM: {str(e)}")
        raise

def should_send_email(**context):
    result = context['task_instance'].xcom_pull(task_ids='check_ram')
    return result['alert']

ALERT_EMAIL = os.getenv('AIRFLOW__SMTP__SMTP_USER')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ram_monitoring',
    default_args=default_args,
    description='Monitor RAM usage',
    schedule_interval=timedelta(minutes=1),
    catchup=False
) as dag:

    monitor_ram = PythonOperator(
        task_id='check_ram',
        python_callable=check_ram_usage,
        provide_context=True,
    )

    check_condition = ShortCircuitOperator(
        task_id='check_condition',
        python_callable=should_send_email,
        provide_context=True,
    )

    send_email = EmailOperator(
        task_id='send_email',
        to=ALERT_EMAIL,
        subject='RAM Usage Alert',
        html_content="""
            {{task_instance.xcom_pull(task_ids='check_ram')['message'] }}
        """,
        trigger_rule='all_success'
    )

    monitor_ram >> check_condition >> send_email