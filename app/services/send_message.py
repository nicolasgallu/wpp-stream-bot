import requests
from app.utils.logger import logger
from app.config.config import WPP_TOKEN,WPP_ID

def enviar_mensaje(destino,mensaje):

    url = f"https://graph.facebook.com/v22.0/{WPP_ID}/messages"

    header = {
      "Authorization":f"Bearer {WPP_TOKEN}",
      "Content-Type":"application/json"}

    texto ={
    "messaging_product": "whatsapp", 
    "recipient_type": "individual",
    "to": destino, 
    "type": "text",
       "text": { 
            "preview_url": False,
            "body": mensaje }}
    try:   
      requests.post(url,headers=header,json=texto)
      logger.info(f"Respuesta enviada al usuario: {destino}")
    except:
       logger.error("error en envio de mensaje")
             


