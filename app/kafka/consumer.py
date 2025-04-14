from app.config.config import KAFKA_CONFIG_CONS,K_TOPIC,TIMER, DS_MODEL_R1, DS_MODEL_V3, GPT_MODEL_4
from app.services.send_message import enviar_mensaje
from app.services.bot import llm_switch
from app.redis.client_messages import read_client_msgs
from app.redis.closed_deals import write_closed_deals
from app.redis.bot_messages import read_bot_msgs,write_bot_msgs
from app.utils.prompts import enhancing_json
from app.services.notify_human import notify_human
from app.utils.sched_db import scheduler_loop_migs
from app.utils.logger import logger
from confluent_kafka import Consumer, KafkaException
from datetime import datetime
import asyncio



# Kafka Consumer instsance and init
consumer = Consumer(KAFKA_CONFIG_CONS)
consumer.subscribe([K_TOPIC])

# Temporary storage for messages
base_tmp = {}
base_refresh = []

async def guardar_mensaje(phone, message, created_at, name):
    """guardamos y acumulamos mensajes entrantes por usuario"""
    global base_tmp,base_refresh

    if phone in base_tmp: #acumulamos queue de mensajes by phone.
        base_refresh.append(phone) #flag para refrescar contador
        base_tmp[phone]["message"].append(message)  #acumulamos mensajes
        base_tmp[phone]["created_at"].append(created_at)  
        base_tmp[phone]["name"].append(name)  
        logger.info(f"Gathering new message from current user: {phone}")
    else:
        base_tmp[phone] = {"name": [name],"message": [message],"created_at": [created_at]}
        logger.info(f"Message saved from user: {phone}")



async def check_base_temp():
    """controlamos cada 2 segundos la queue de mensajes en tmp - se responden cumplidos los 'x' segundos"""
    global base_tmp,base_refresh
    while True:
        await asyncio.sleep(2)
        if base_tmp:
            logger.info("Checking temporal base...")            
            for phone in list(base_tmp.keys()):
                time_now = datetime.now().replace(microsecond=0)
                last_message_at = datetime.strptime(base_tmp[phone]["created_at"][-1], "%Y-%m-%d %H:%M:%S")
                secs_passed = round((time_now - last_message_at).total_seconds(),2)
                logger.info(f"{secs_passed} seconds had passed from: {phone}")

                if phone in base_refresh:
                    logger.info(f"Reseting timer from: {phone}...")
                    base_refresh.remove(phone) #flag para refrescar contador, (se resetea).
                    continue

                if secs_passed >= TIMER:
                    ###### cleaning temporal base #######
                    aux_base_tmp = base_tmp.copy()
                    del base_tmp[phone]       
                    logger.info(f"Starting process to reply customer: {phone}...")

                    ###### creating questions variable #######
                    questions = " ".join(aux_base_tmp[phone]["message"])
                    client_name = list(set(aux_base_tmp[phone]["name"]))[0]
                    logger.info("Questions variable created.")

                    ###### previous chat creation #######
                    first_msg_at = datetime.strptime(aux_base_tmp[phone]["created_at"][0], "%Y-%m-%d %H:%M:%S")
                    prev_client_msgs = read_client_msgs(phone,first_msg_at)
                    prev_bot_msgs = read_bot_msgs(phone)
                    chat_previous = prev_client_msgs + prev_bot_msgs
                    chat_previous = sorted(chat_previous, key=lambda x: datetime.fromisoformat(x[0]))
                    print(chat_previous)
                    print(client_name)
                    

                    if len(chat_previous) > 10: 
                        chat_previous_filter = chat_previous[-9:]
                    else:
                        chat_previous_filter = chat_previous
                    logger.info("Previous chat created")

                    ###### system prompts #######
                    prompt_bot = enhancing_json('System_Prompt_Assistant',chat_previous_filter)
                    prompt_cop = enhancing_json('System_Prompt_Cop',chat_previous_filter)
                    prompt_tag = enhancing_json('System_Prompt_Tag')
                    logger.info("Prompts created")

                    try:
                        ###### bot assistant ######
                        question = f"El cliente: {client_name}, realizo la siguiente pregunta: {questions}"
                        bot_msg,bot_reply_at,model_bot,cost_bot = await llm_switch(
                                                        prompt= prompt_bot,
                                                        message= question, 
                                                        ds_first_try= DS_MODEL_R1,
                                                        ds_second_try= DS_MODEL_V3,
                                                        gpt_first_try= GPT_MODEL_4,
                                                        max_tokens=300, 
                                                        temperature=0.55)
                        logger.info("Bot assistant response created")

                        ###### bot cop #######
                        msg_cop,cop_reply_at,model_cop,cost_cop = await llm_switch(
                                                        prompt= prompt_cop,
                                                        message= bot_msg, 
                                                        ds_first_try= DS_MODEL_V3,
                                                        ds_second_try= DS_MODEL_V3,
                                                        gpt_first_try= GPT_MODEL_4,
                                                        max_tokens=300, 
                                                        temperature=0.55)                                                
                        logger.info("Bot cop response created")

                        ###### bot tag #######  
                        last_message_at = last_message_at.strftime("%Y-%m-%d %H:%M:%S")
                        cop_reply_at = cop_reply_at.strftime("%Y-%m-%d %H:%M:%S")
                        chat_complete = str(chat_previous + [[last_message_at,questions,client_name],[cop_reply_at,msg_cop,'bot']])
                        msg_tag,tag_created_at,model,cost = await llm_switch(
                                                            prompt= prompt_tag,
                                                            message= chat_complete, 
                                                            ds_first_try= DS_MODEL_V3,
                                                            ds_second_try= DS_MODEL_V3,
                                                            gpt_first_try= GPT_MODEL_4,
                                                            max_tokens=200, 
                                                            temperature=0.50)
                        logger.info(f"Bot tag response created > {msg_tag}")  



                        ##### filters ####### 
                        logger.info("Conversation Status..")
                        if "cierr" in msg_tag:
                            enviar_mensaje(phone, msg_cop)
                            write_closed_deals(phone,time_now)
                            notify_human(f"Cierre de: {client_name}/{phone[-4:]} (alta)",chat_complete)
                            logger.info("Closed Cause : Afilitation Interest")
                        elif "agresi" in msg_tag:
                            enviar_mensaje(phone, msg_cop)
                            notify_human(f"Cierre de: {client_name}/{phone[-4:]} (agresivo)",chat_complete)
                            write_closed_deals(phone,time_now)
                            logger.info("Closed Cause : Bad Behaviour")
                        elif "frust" in msg_tag:
                            enviar_mensaje(phone, msg_cop)
                            notify_human(f"Cierre de: {client_name}/{phone[-4:]} (frustacion)",chat_complete)
                            write_closed_deals(phone,time_now)
                            logger.info("Closed Cause : Frustration")
                        elif "ayud" in msg_tag:
                            enviar_mensaje(phone, msg_cop)
                            notify_human(f"Cierre de: {client_name}/{phone[-4:]} (ayuda)",chat_complete)
                            write_closed_deals(phone,time_now)
                            logger.info("Closed Cause : Human Help")
                        else:
                            enviar_mensaje(phone, msg_cop)
                            notify_human('conversacion abierta',chat_complete)
                            logger.info("Conversation remains open")


                        ####### REDIS #######
                        write_bot_msgs(phone, questions, model_bot, bot_msg, cost_bot, model_cop, msg_cop, cost_cop, cop_reply_at) 
                        logger.info("Redis - Updating Table Bot Response")    

                    except:
                        logger.info("Failed to answer the customer. going with human.")
                        enviar_mensaje(phone, "En estos momentos nuestro sistema se encuentra saturado, un representante se pondra en contacto en la brevedad. Desde ya muchas Gracias")
                        notify_human(f"Error en nuestro sistema {client_name}/{phone[-4:]}",chat_complete)
                        write_closed_deals(phone,tag_created_at)

                    

async def consume_messages():
    """ Kafka consumer that listens for messages and processes them """
    try:
        while True:
            msg = await asyncio.to_thread(consumer.poll, 1.0)  # ✅ Make polling non-blocking
            if msg is None:
                continue
            if msg.error():
                logger.error(msg.error())
                raise KafkaException(msg.error())    
            else:
                message_data = msg.value().decode('utf-8').split("|")
                if len(message_data) < 3:
                    logger.error(f"Invalid message format: {msg.value().decode('utf-8')}")
                    continue
                else:
                    phone,message,created_at,name = message_data[0], message_data[1], message_data[2], message_data[3]
                    await guardar_mensaje(phone, message, created_at, name)

    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
    finally:
        consumer.close()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    task_consumer = loop.create_task(consume_messages())  # ✅ Start Kafka Consumer
    task_checker = loop.create_task(check_base_temp())  # ✅ Start Checking Timer
    task_migrations = loop.create_task(scheduler_loop_migs())  # ✅ Start Migrations (this is where i believe it should be)

    try:
        loop.run_forever()  # ✅ Keep the event loop running
    except KeyboardInterrupt:
        logger.info("Stopping consumer...")
    finally:
        task_consumer.cancel()
        task_checker.cancel()
        consumer.close()
        loop.close()
