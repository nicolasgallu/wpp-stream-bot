from app.utils.logger import logger
from app.config.config import RDB_BOT_MSG

def write_bot_msgs(phone,questions,model_bot,msg_bot,cost_bot, model_cop,msg_cop,cost_cop,created_at):
    """write msgs from bot"""
    try:
        data = {
            'phone': phone, 
            'client_questions': questions, 
            'model_bot': model_bot, 
            'response_bot': msg_bot, 
            'cost_bot_usd': str(cost_bot), 
            'model_cop': model_cop, 
            'response_cop': msg_cop, 
            'cost_cop_usd': str(cost_cop), 
            'cost_total_usd': str(cost_bot + cost_cop), 
            'created_at': str(created_at)}
        key = f"{data['phone']}|{data['created_at']}"
        RDB_BOT_MSG.hset(key, mapping=data)
        logger.info(f"Redis: Bot message saved succesfully") 
    except:
        logger.error(f"Redis: Bot message not saved") 
        raise Exception


def read_bot_msgs(phone):
    """return msgs from Bot """
    previous_chat = []
    try:
        for key in RDB_BOT_MSG.scan_iter(match = f'*{phone}*'):
            data = RDB_BOT_MSG.hgetall(key)
            data = {key.decode('utf-8'):value.decode('utf-8') for key, value in data.items()}
            data = list(map(data.get,['created_at','response_cop']))
            data.append("bot")
            previous_chat.append(data)
        logger.info(f"Redis: Bot messages readed succesfully") 
        return previous_chat
    except:
        logger.info(f"Redis:Error while reading Bot messages") 
        raise Exception


