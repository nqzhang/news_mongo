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
async def qqq():
    post_id = ObjectId("5c6721a67a2ed534b85deb52")
    x = await db.posts.find({"_id":post_id}).to_list(length=None)
    print(x)
async def related():
    x = db.posts.aggregate([
        {"$match": {"tags": {"$in": [ObjectId("5bea62907a2ed52674df4468")]}}},
        {"$unwind": "$tags"},
        {"$match": {"tags": {"$in": [ObjectId("5bea62907a2ed52674df4468")]}}},
        {"$group": {
            "_id": "$_id",
            "matches": {"$sum": 1}
        }},
    {"$sort": {"matches": -1}}])
    async for i in x:
        print(i)
async def main():
    await qqq()
    #await ttt()
    #await related()

import asyncio
loop = asyncio.get_event_loop()
loop.run_until_complete(main())