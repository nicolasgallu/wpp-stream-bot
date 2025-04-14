from app.redis.closed_deals import read_closed_deals
from app.redis.client_messages import write_client_msgs
from app.kafka.topics import ensure_topic
from app.config.config import KAFKA_CONFIG_PROD,K_TOPIC,META_APP_SECRET
from app.utils.logger import logger
from confluent_kafka import Producer
from flask import Flask,request,make_response
from datetime import datetime

import hmac
import hashlib

#make sure the topic exists -----------------------------------------
ensure_topic()   

# Kafka producer instsance and init
producer = Producer(KAFKA_CONFIG_PROD)

#####corregir respuesta 500 y otros errores webhook####
app = Flask(__name__)
@app.route("/webhook",methods=["POST","GET"])

def webhook (): 
    if request.method == 'GET': #auth webhook#
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode and token:
            if mode == 'subscribe' and token == "guias2025*":
                logger.info("Succesfull webhook auth")
                return make_response(challenge,200)
            
            
    # Get the signature from the headers (Meta sends it as 'X-Hub-Signature')
    signature = request.headers.get('X-Hub-Signature')
    if signature is None:
        logger.warning("No signature found in request header.")
        return make_response('Forbidden', 403)

        
    if request.method == "POST": #processing customer msgs#
        # Get the body of the POST request (this is the raw data)
        body = request.get_data()
        # Create the hash using HMAC with your app secret
        computed_signature = 'sha1=' + hmac.new(META_APP_SECRET.encode(), body, hashlib.sha1).hexdigest()
        if hmac.compare_digest(computed_signature, signature):
            logger.info("Signature verified: Request is from Meta")
            try:
                response = request.json
                value = response["entry"][0]["changes"][0]["value"]
                contacts = value.get("contacts", [{}])[0]
                messages = value.get("messages", [{}])[0]

                if (
                    "profile" in contacts and
                    "name" in contacts["profile"] and
                    "wa_id" in contacts and
                    "text" in messages and
                    "body" in messages["text"] and
                    "timestamp" in messages
                    ):
                    name = contacts["profile"]["name"]
                    message = messages["text"]["body"]
                    phone = contacts["wa_id"]
                    created_at = datetime.fromtimestamp(int(messages["timestamp"]))

                    if read_closed_deals(phone): 
                        logger.info(f"-Deal {phone} is already closed ")
                        ##AVISAR AL CLIENTE QUE RECIBIMOS UN NUEVO MENSAJE EN EL BOT ASSISTANT
                        return make_response('',200)
                    else:
                        kafka_message = f"{phone}|{message}|{created_at}|{name}"
                        producer.produce(K_TOPIC, key=phone, value=kafka_message)
                        write_client_msgs(phone,name,message,created_at)
                        logger.info(f"Sending to consumer new message from: {phone}") 
                        return make_response('',200)

                return make_response('', 200)  # <- por si no cumple condiciones del if
            
            except Exception as e:
                logger.warning(f"Error en estructura del webhook: {e}")
                return make_response('',400)
        else:
            logger.warning("Invalid signature: Request is not from Meta")
            return make_response('Forbidden', 403)


    else:
        return make_response('',400)
        
if  __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
    producer.flush() # Ensure all messages are delivered
