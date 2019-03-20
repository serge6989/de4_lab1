from datetime import datetime
import elasticsearch
import csv
import unicodedata
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

dag = DAG('Route_to_HDFS', description='no_desc',
          schedule_interval='* 1 * * *',
          start_date=datetime(2017, 3, 20), catchup=False)

b1 = BashOperator(task_id='put_data_to_hdfs',
                  bash_command='hdfs dfs -put /etc/airflow/airflow_home/temp/$(date +%Y-%m-%d)_elastic.file /opt/lab1',
                  dag=dag)
