from app.redis.closed_deals import read_closed_deals
from app.redis.client_messages import write_client_msgs
from app.kafka.topics import ensure_topic
from app.config.config import KAFKA_CONFIG_PROD,K_TOPIC,META_APP_SECRET,FLASK_PORT
from app.utils.logger import logger
from confluent_kafka import Producer
from flask import Flask,request,make_response
from datetime import datetime
import time

#make sure the topic exists -----------------------------------------
ensure_topic()   

# Kafka producer instsance and init
producer = Producer(KAFKA_CONFIG_PROD)

if  __name__ == "__main__":
    logger.info("iniciando proceso producer") 
    for i in range(10): 
        logger.info(i) 
        time.sleep(0.3)
        created_at = datetime.now().replace(microsecond=0)
        name = f"test-{i}"
        phone = f"000{i}"
        message = "que servicios tenes?"
        kafka_message = f"{phone}|{message}|{created_at}|{name}"
        producer.produce(K_TOPIC, key=phone, value=kafka_message)
        write_client_msgs(phone,name,message,created_at)
        logger.info(f"Sending to consumer new message from: {phone}") 
    producer.flush() # Ensure all messages are delivered
