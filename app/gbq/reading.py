from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from app.utils.logger import logger
from app.config.config import GBQ_CREEDENTIALS, DATASET_ID, BQ_TABLE_PROMPTS

credentials = Credentials.from_service_account_info(GBQ_CREEDENTIALS)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

def get_prompt(field):
    table_path = f"{client.project}.{DATASET_ID}.{BQ_TABLE_PROMPTS}"
    query = f"SELECT {field} FROM `{table_path}` LIMIT 1"
    
    try:
        result = client.query(query).result()
        row = next(result, None)
        if row:
            logger.info(f"Success pulling data from {field}")
            return str(row[field])
        else:
            logger.warning(f"No data returned from {field}")
            return None
    except Exception as e:
        logger.error(f"Error querying BigQuery: {e}")
        return None