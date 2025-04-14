from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from app.utils.logger import logger
from app.redis.helper.get_all import get_redis_data
from app.config.config import GBQ_CREEDENTIALS,DATASET_ID


credentials = Credentials.from_service_account_info(GBQ_CREEDENTIALS)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

def create_table(input_schema):

    table_name = list(input_schema)[0]
    table_path = client.dataset(DATASET_ID).table(table_name)
    try:
        client.get_table(table_path)
        logger.info(f"Tabla '{table_name}' already exits.")

    except:
        logger.info(f"Tabla '{table_name}' dont exists, creating now..")
        schema = []
        for i in range(len(input_schema[table_name]['field'])):
            schema.append(
                bigquery.SchemaField(
                    input_schema[table_name]['field'][i], 
                    input_schema[table_name]['type'][i], 
                    mode=input_schema[table_name]['mode'][i])
                    )
        table = bigquery.Table(table_path, schema=schema)
        client.create_table(table)
        logger.info(f"Tabla '{table_name}' creada exitosamente")


def insert_data(input_schema,redis_db):
    
    table_name = list(input_schema)[0]
    table_path = client.dataset(DATASET_ID).table(table_name)
    
    if redis_db.keys('*') == []:
        logger.info(f"There is not data to migrate from table {table_name}")
    else:
        try:
            client.get_table(table_path)
            rows_to_insert = get_redis_data(redis_db) 
            load = client.insert_rows_json(table_path, rows_to_insert)
            if load:
                logger.error(f"Impossible to load rows into table {table_name}")
            else:
                logger.info(f"Succesfuly rows loaded into {table_name}")

        except:
            raise Exception







