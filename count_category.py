from pymongo import MongoClient
import config
from bson import ObjectId

client = MongoClient(config.mongo['url'])[config.mongo['db_name']]

cursor = client.posts.aggregate([
          {"$project": { "_id": 0, "category": 1 } },
          {"$unwind": "$category" },
          {"$group": { "_id": "$category", "count": { "$sum": 1 } }},
          {"$project": { "_id": 0,"category": "$_id", "count": 1 } },
          {"$sort": { "count": -1 } },
          {"$limit": 10 },
      ])
for x in cursor:
    c = client.terms.find_one({"_id":x['category']})
    c['type'] = 'left'
    client.menu.insert_one(c)