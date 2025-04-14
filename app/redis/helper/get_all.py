from app.utils.logger import logger

def get_redis_data(redis_db):    
    keys = redis_db.keys('*')
    messages = []
    try:
        for key in keys:
            data = redis_db.hgetall(key)
            data = {key.decode('utf-8'):value.decode('utf-8') for key, value in data.items()}
            messages.append(data)
        logger.info(f"Succesfully pulled data from redis table{redis_db}")
        return messages

    except:
        logger.error(f"Error pulling data from redis table{redis_db}")

