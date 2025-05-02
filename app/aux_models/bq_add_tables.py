from app.gbq.writting import *
from app.config.config import GBQ_CLIENT_MSG, GBQ_BOT_MSG, GBQ_BOT_CLOSED_DEALS

create_table(GBQ_BOT_CLOSED_DEALS)
create_table(GBQ_BOT_MSG)
create_table(GBQ_CLIENT_MSG)