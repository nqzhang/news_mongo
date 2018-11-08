from tornado.web import RequestHandler
from bson import ObjectId

class ArticleHandler(RequestHandler):
    async def get(self, post_id):
        cursor = self.application.db.posts.aggregate([
            {"$lookup":
                {"from": "users",
                "localField": "user",
                "foreignField": "_id",
                "as": "u"}
            },
            {"$unwind": "$category"},
            { "$lookup":
                {"from": "terms",
                "localField": "category",
                "foreignField": "_id",
                "as": "c"}
            },
            {"$unwind": "$c"},
            {
              "$group": {
                "_id":"$_id",
                "tags":{"$first":"$tags"},
                "title":{"$first":"$title"},
                "content":{"$first":"$content"},
                "post_date":{"$first":"$post_date"},
                "c": { "$push": "$c" },
                 "u":{"$first":"$u"},
                 }
            },
            {"$unwind": "$tags"},
            { "$lookup":
                {"from": "terms",
                "localField": "tags",
                "foreignField": "_id",
                 "as": "t"}
            },
            {"$unwind": "$t"},
             {
            "$group": {
                    "_id":"$_id",
                    "title":{"$first":"$title"},
                    "content":{"$first":"$content"},
                    "post_date":{"$first":"$post_date"},
                    "category":{"$first":"$c"},
                    "tags": { "$push": "$t" },
                    "user":{"$first":"$u"},
                    }
            }
        ])
        async for doc in cursor:
            print(doc)
        #post = await self.application.db.posts.find_one({"_id":ObjectId(post_id)})
        #print(post)
        categorys = await self.application.db.terms.find({"type": "0"}).to_list(length=100)
        self.render('page/article.html',categorys=categorys,post=post)
