from tornado.web import RequestHandler
import uuid
import datetime
import traceback
import json
from pymongo import ReturnDocument
import datetime
from bson import ObjectId

class NewPostHandler(RequestHandler):
    def check_xsrf_cookie(self):
        pass
    async def post(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(self.request.headers)
        body=json.loads(self.request.body.decode('utf-8'))
        category = body['category']
        tags = body['tags']
        title = body['title']
        content = body['content']
        user = body['user']
        #thumb = body['thumb']
        #guid = uuid.uuid4().hex
        #guid = uuid.uuid3(uuid.NAMESPACE_DNS, title).hex
        try:
            #插入用户
            u = await self.application.db.users.find_one_and_update({"user_name":user},
                                                                    {"$setOnInsert":{"user_name":user}},upsert=True,return_document=ReturnDocument.AFTER)
            u_id = u['_id']
            # 如果不存在category,创建
            #无论是否存在,都返回category_id
            c_ids = []
            for c_name in category:
                c = await self.application.db.terms.find_one_and_update({"name":c_name,"type":"0"},
                                                                             {"$setOnInsert":{"type":"0", "name":c_name}},upsert=True,return_document=ReturnDocument.AFTER)
                c_ids.append(c['_id'])
            print(c_ids)
            # 如果不存在tag,创建
            # 无论是否存在,都返回tag_id
            t_ids = []
            for t_name in tags:
                t = await self.application.db.terms.find_one_and_update({"name": t_name, "type": "1"},
                                                                {"$setOnInsert": {"type": "1", "name": t_name}}, upsert=True,return_document=ReturnDocument.AFTER)
                t_ids.append(t['_id'])
            print(t_ids)

            #插入文章
            await self.application.db.posts.find_one_and_update({"title": title},
                                                                     {"$setOnInsert": {"title":title,"content":content,"user":u_id,"category":c_ids,"tags":t_ids,"post_date":datetime.datetime.now()}},
                                                                     upsert=True)
        except:
            traceback.print_exc()
        else:
            self.write('发布成功')
