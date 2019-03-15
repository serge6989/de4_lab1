from datetime import datetime
import elasticsearch
import csv
import unicodedata
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from clickhouse_driver import Client
from datetime import datetime
client = Client('127.0.0.1')


def get_from_elastic():
    es = elasticsearch.Elasticsearch(["localhost:9200"])
    res = es.search(index="sergey.kataev", body={
        "query":{
            "range" : {
                "@timestamp" :{
                    "gte": "now-15m",
                    "lt" : "now",
                }
            }
        }
    },size=500 )
    all_items = res['hits']['hits']
#    task_instance = kwargs['task_instance']
#    task_instace.xcom_push(key='items', vaule = all_items)
    return(all_items)

def put_to_file(**context):
    ymd=datetime.strftime(datetime.now(),'%Y-%m-%d')
    print(ymd)
    hits_list = context['task_instance'].xcom_pull(task_ids='get_elast')
    print(hits_list)
    for el in hits_list:
        with open ('/etc/airflow/airflow_home/temp/'+ymd+'_elastic.file', 'a') as f:
            f.write(el['_source']['message']+'\n')
    return(hits_list)

def put_to_click(**context):
    false = False
    true = True
    hits_list = context['task_instance'].xcom_pull(task_ids='get_elast')
    for el in hits_list:
        d=eval(el['_source']['message'])
        print(d, type(d))
        for val in d:
            if val == 'timestamp':
                d[val]=datetime.utcfromtimestamp(d[val])
            elif val == 'basket_price' and d[val]=='':
                d[val]=0.0
            elif val == "item_price" and type(d[val])!=float:
                d[val]=float(d[val])
        d=[d]
        client.execute('INSERT INTO default.sergey_kataev VALUES',d)
        a = client.execute('SELECT * FROM default.sergey_kataev')

    return(el)

dag = DAG('Route_to_Click', description='no_desc',
          schedule_interval='*/1 * * * *',
          start_date=datetime(2017, 3, 20), catchup=False)


d1 = PythonOperator(task_id='get_elast', python_callable=get_from_elastic, dag=dag)
d2 = PythonOperator(task_id='to_file',provide_context=True,python_callable=put_to_file,dag=dag)
d3 = PythonOperator(task_id='to_click',provide_context=True,python_callable=put_to_click,dag=dag)
d2.set_upstream(d1)
d3.set_upstream(d1)
