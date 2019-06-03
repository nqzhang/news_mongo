from pymongo import MongoClient
import config
from bson import ObjectId
from utils.hot import hot
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import motor.motor_asyncio
db = motor.motor_asyncio.AsyncIOMotorClient(config.mongo['url'],maxPoolSize=200)[config.mongo['db_name']]

async def calc1():
    cursor = await db.posts.find({"type":0,"is_recommend":{"$ne":False}},{"_id":1}).sort([("score",-1)]).limit(10000).to_list(length=None)
    for document in cursor:
        await hot(db,document['_id'])
async def calc2():
    cursor = await db.posts.find({"type":0,"is_recommend":{"$ne":False}},{"_id":1}).sort([("_id",-1)]).limit(10000).to_list(length=None)
    for document in cursor:
        await hot(db,document['_id'])
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(calc1, 'interval', hours=1)
    scheduler.add_job(calc2, 'interval', hours=1)
    scheduler.start()
loop = asyncio.get_event_loop()
asyncio.ensure_future(main())
loop.run_forever()