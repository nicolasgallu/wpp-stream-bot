# #ESTE CODIGO ES PARA ESCRIBIR EN GBQ LA BASE DE MENSAJES Y LIMPIAR REDIS# 
# TAMBIEN HAY QUE SUMAR JSON UPDATE.
from app.gbq.writting import insert_data
from app.utils.logger import logger
from app.config.config import GBQ_CLIENT_MSG, GBQ_BOT_MSG, GBQ_BOT_CLOSED_DEALS
from app.config.config import RDB_CLIENT_MSG, RDB_BOT_MSG, RDB_CLOSED_DEALS
import schedule
import asyncio


async def migs_db():
    logger.info("Executing Migrations..")
    bq_bases = [GBQ_CLIENT_MSG, GBQ_BOT_MSG, GBQ_BOT_CLOSED_DEALS]
    rd_bases = [RDB_CLIENT_MSG, RDB_BOT_MSG, RDB_CLOSED_DEALS]
    for i, base in enumerate(bq_bases):
        gbq_table = base.keys()
        rd_table = rd_bases[i]
        insert_data(gbq_table, rd_table)
    logger.info("Finished Migrations..")
    RDB_CLIENT_MSG.flushdb()
    RDB_BOT_MSG.flushdb()
    logger.info("Redis bases client & bot erased..")


def schedule_migs():
    # Ejecutar a las 4:00 AM todos los días
    schedule.every().day.at("04:00").do(lambda: asyncio.create_task(migs_db()))

async def scheduler_loop_migs():
    schedule_migs()
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)