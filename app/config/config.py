import os
import redis
from dotenv import load_dotenv

load_dotenv()



### WPP ###
WPP_TOKEN = os.getenv("WPP_TOKEN")
WPP_ID = os.getenv("WPP_ID")
META_APP_SECRET = os.getenv("META_APP_SECRET")

### KAFKA ###
K_SERVER = os.getenv("KAFKA_SERVER", "kafka") 
K_PORT   = os.getenv("KAFKA_PORT",   "9092")
K_GROUP  = os.getenv("KAFKA_GROUP",  "user-group")
K_OFFSET = os.getenv("KAFKA_OFFSET", "earliest")
K_TOPIC  = os.getenv("KAFKA_TOPIC",  "orders")

BOOTSTRAP = f"{K_SERVER}:{K_PORT}"
KAFKA_CONFIG_PROD = {"bootstrap.servers": BOOTSTRAP}
KAFKA_CONFIG_CONS = {
    "bootstrap.servers": BOOTSTRAP,
    "group.id":          K_GROUP,
    "auto.offset.reset": K_OFFSET,
}

### REDIS DB ###
R_HOST = os.getenv("R_HOST")
R_PORT = os.getenv("R_PORT")
RDB_CLIENT_MSG = redis.Redis(host=R_HOST, port=R_PORT, db=0)
RDB_BOT_MSG = redis.Redis(host=R_HOST, port=R_PORT, db=1) 
RDB_CLOSED_DEALS = redis.Redis(host=R_HOST, port=R_PORT, db=2) 


### GBQ ACCOUNT SERVICE ###
GBQ_CREEDENTIALS = {
'type': os.getenv("type"),
'project_id': os.getenv("project_id"),
'private_key_id': os.getenv("private_key_id"),
'private_key': os.getenv("private_key"),
'client_email': os.getenv("client_email"),
'client_id': os.getenv("client_id"),
'auth_uri': os.getenv("auth_uri"),
'token_uri': os.getenv("token_uri"),
'auth_provider_x509_cert_url': os.getenv("auth_provider_x509_cert_url"),
'client_x509_cert_url': os.getenv("client_x509_cert_url"),
'universe_domain': os.getenv("universe_domain")
}

# ✅ Reparar la private_key si viene con \n como texto
if GBQ_CREEDENTIALS['private_key'].startswith("-----BEGIN") and "\\n" in GBQ_CREEDENTIALS['private_key']:
    GBQ_CREEDENTIALS['private_key'] = GBQ_CREEDENTIALS['private_key'].replace('\\n', '\n')


### GBQ DATASET PATH ###
DATASET_ID =  "wpp_obra_social"
BQ_TABLE_PROMPTS = "prompts"


### GBQ TABLES SCHEMA ###
GBQ_CLIENT_MSG = {
    'client_messages': {
    'field': ["phone", "customer_name", "message", "created_at"],
    'type': ["STRING", "STRING","STRING","DATETIME"],
    'mode': ["REQUIRED","REQUIRED","REQUIRED","REQUIRED"]}
    }

GBQ_BOT_MSG = {
    'bot_messages': {
    'field': ["phone", "client_questions", "model_bot", "response_bot","cost_bot_usd","model_cop","response_cop","cost_cop_usd","cost_total_usd","created_at"],
    'type': ["STRING", "STRING","STRING","STRING", "FLOAT","STRING","STRING","FLOAT","FLOAT","DATETIME"],
    'mode': ["REQUIRED","REQUIRED","REQUIRED","REQUIRED","REQUIRED","REQUIRED","REQUIRED","REQUIRED","REQUIRED","REQUIRED"]}
    }

GBQ_BOT_CLOSED_DEALS = {
    'bot_closed_deals': {
    'field': ["phone", "created_at"],
    'type': ["STRING", "DATETIME"],
    'mode': ["REQUIRED","REQUIRED"]}
    }



### LLM MODELS ###
COST_1K_TOKENS = {
    "gpt-4": {"costo": {"input": 0.03,"output": 0.06}},
    "deepseek-chat": {"costo": {"input": 0.00027,"output": 0.00110}},
    "deepseek-reasoner": {"costo": {"input": 0.00055,"output": 0.00219}},
}

### PROJECT SETTINGS ###
#time to acumulate messages (seconds)#
TIMER = 5
#notify human & internal#
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


#LLM MODELS AND KEYS
DS_MODEL_R1 = os.getenv("DS_MODEL_REASONER")
DS_MODEL_V3 = os.getenv("DS_MODEL_CHAT")
GPT_MODEL_4 = os.getenv("GPT_MODEL") 
DS_API_KEY = os.getenv("DS_API_KEY")
GPT_API_KEY= os.getenv("GPT_API_KEY")