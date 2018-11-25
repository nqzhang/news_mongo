import motor.motor_asyncio
import config
from pymongo import ReturnDocument
from bson import ObjectId

db = motor.motor_asyncio.AsyncIOMotorClient(config.mongo['url'])[config.mongo['db_name']]

async def ttt():
    t_name = "t_name"
    x = await db.terms.find_one_and_update({"name": t_name, "type": "1"},
                                                        {"$setOnInsert": {"type": "1", "name": t_name}},
                                                        upsert=True, return_document=ReturnDocument.AFTER)
    print(x)

async def related():
    x = db.posts.aggregate([
          {"$match":{'category': {'$in': [ObjectId('5bea62907a2ed52674df4466')]},'_id': {'$ne': [ObjectId('5bf150977a2ed52af08af738')]}}},
      ])
    async for i in x:
        print(i)
async def main():
    #await ttt()
    await related()

import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(main())