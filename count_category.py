from pymongo import MongoClient
import config
from bson import ObjectId

client = MongoClient(config.mongo['url'])[config.mongo['db_name']]

excludes_name = ['未分類','推薦']
excludes = client.terms.find({"name":{"$in":excludes_name},"type":"0"})
excludes_ids = []
for x in excludes:
    excludes_ids.append(x['_id'])
print(excludes_ids)
cursor = client.posts.aggregate([
          {"$match":{"category":{ "$nin": excludes_ids }}},
          {"$project": { "_id": 0, "category": 1 } },
          {"$unwind": "$category" },
          {"$group": { "_id": "$category", "count": { "$sum": 1 } }},
          {"$project": { "_id": 0,"category": "$_id", "count": 1 } },
          {"$sort": { "count": -1 } },
          {"$limit": 10 },
      ])
client.menu.drop()
for x in cursor:
    c = client.terms.find_one({"_id":x['category']})
    if c:
        c['type'] = 'left'
        client.menu.insert_one(c)