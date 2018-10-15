import pymongo
import tornado
import config
import asyncio
class cron(object):
    def __init__(self,db):
        self.db = db

    async def count_category(self):
        print('开始统计')
        cursor =  self.db.posts.aggregate([
          {"$project": { "_id": 0, "category": 1 } },
          {"$unwind": "$category" },
          {"$group": { "_id": "$category", "tags": { "$sum": 1 } }},
          {"$project": { "_id": 0,"category": "$_id", "tags": 1 } },
          {"$sort": { "tags": -1 } },
          {"$limit": 10 },
      ])

        async for doc in cursor:
            print(doc)
        print("统计结束")
