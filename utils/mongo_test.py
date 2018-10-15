import motor.motor_asyncio
import config
from pymongo import ReturnDocument

db = motor.motor_asyncio.AsyncIOMotorClient(config.mongo['url'])[config.mongo['db_name']]

async def ttt():
    t_name = "t_name"
    x = await db.terms.find_one_and_update({"name": t_name, "type": "1"},
                                                        {"$setOnInsert": {"type": "1", "name": t_name}},
                                                        upsert=True, return_document=ReturnDocument.AFTER)
    print(x)


import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(ttt())