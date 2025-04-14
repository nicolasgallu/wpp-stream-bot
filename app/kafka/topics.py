import time, logging
from confluent_kafka.admin import AdminClient, NewTopic, KafkaException
from app.config.config import KAFKA_CONFIG_PROD, K_TOPIC

def ensure_topic(partitions=2, rf=1, retries=3, delay=3):
    admin = AdminClient(KAFKA_CONFIG_PROD)

    for attempt in range(1, retries + 1):
        try:
            fs = admin.create_topics([NewTopic(K_TOPIC, partitions, rf)])
            fs[K_TOPIC].result(5)          # wait 5 s
            logging.info("Topic %s ready", K_TOPIC)
            return
        except Exception as e:
            logging.warning("Topic attempt %s/%s failed: %s",
                            attempt, retries, e)
            time.sleep(delay)
    raise RuntimeError("Kafka not ready after retries")
