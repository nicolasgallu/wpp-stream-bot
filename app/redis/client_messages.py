from datetime import datetime
from app.utils.logger import logger
from app.config.config import RDB_CLIENT_MSG

def write_client_msgs(phone, customer_name, message, created_at):
    """write msgs from customer"""
    try:
        data = {
            'phone': phone, 
            'customer_name': customer_name, 
            'message': message, 
            'created_at': str(created_at)}

        key = f"{data['phone']}|{data['created_at']}"
        RDB_CLIENT_MSG.hset(key, mapping=data)
        logger.info(f"Redis: Customer message saved succesfully") 
    except:
        logger.error(f"Redis: Customer message not saved") 
        raise Exception

def read_client_msgs(phone,created_at=None):
    """return msgs from customer (just the ones previous to the last message.)"""
    previous_chat = []
    try:
        for key in RDB_CLIENT_MSG.scan_iter(match = f'*{phone}*'):
            data = RDB_CLIENT_MSG.hgetall(key)
            data = {key.decode('utf-8'):value.decode('utf-8') for key, value in data.items()}
            if created_at is None:
                data_filt = list(map(data.get, ['created_at','message']))
                data_filt.append(f"client_name: {data['customer_name']}")     
                previous_chat.append(data_filt)         
            if created_at is not None and datetime.strptime(data['created_at'], "%Y-%m-%d %H:%M:%S") < created_at:
                data_filt = list(map(data.get, ['created_at','message']))
                data_filt.append(f"client_name: {data['customer_name']}")  
                previous_chat.append(data_filt)
            else:
                continue
        logger.info(f"Redis: Customer messages readed succesfully") 
        return previous_chat
    except:
        logger.info(f"Redis:Error while reading customer messages") 
        raise Exception

