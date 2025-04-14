from app.utils.logger import logger
from app.config.config import RDB_CLOSED_DEALS


def write_closed_deals(phone,created_at):
    """write cases closed"""
    try:
        data = {
            'phone': phone,
            'created_at': str(created_at)}
        key = f"{data['phone']}|{data['created_at']}"
        RDB_CLOSED_DEALS.hset(key, mapping=data)
        logger.info(f"Redis: Closed Customer saved succesfully") 
    except:
        logger.error(f"Redis: Closed Customer not saved") 
        raise Exception


def read_closed_deals(phone):
    closed_deal = RDB_CLOSED_DEALS.keys(f"*{phone}*")
    if len(closed_deal)>0:
        return True
    else:
        return False


