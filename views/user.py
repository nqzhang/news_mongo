from views.base import UserHander
import tornado.web
from views.base import authenticated_async
from pymongo import ReturnDocument
import datetime
from bson import ObjectId

class PostEditHandler(UserHander):
    @authenticated_async
    async def get(self):
        #print(self.current_user)
        self.render('user/postedit.html')


class PostAjaxHandler(UserHander):
    @authenticated_async
    async def post(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        u_id =  self.current_user.decode()
        content = self.get_argument('content')
        title = self.get_argument('title')
        tags = self.get_argument('tags').split(',')
        category = [i.lower() for i in self.get_argument('category').split(',')]
        category_site = category[0:1]
        category_person = category[1:]
        # 如果不存在category_site,创建
        category_site_ids = []
        for c_name in category_site:
            c = await self.application.db.terms.find_one({"name": c_name, "type": "0"})
            if c:
                c_id = c['_id']
            else:
                c = await self.application.db.terms.insert_one({"name": c_name, "type": "0"})
                c_id = c.inserted_id
            category_site_ids.append(c_id)
        category_person_ids = []
        for c_name in category_person:
            c = await self.application.db.terms.find_one({"name": c_name, "type": "2"})
            if c:
                c_id = c['_id']
            else:
                c = await self.application.db.terms.insert_one({"name": c_name, "type": "2"})
                c_id = c.inserted_id
            category_person_ids.append(c_id)
        category_ids = category_site_ids + category_person_ids
        # 如果不存在tag,创建
        # 无论是否存在,都返回tag_id
        t_ids = []
        for t_name in tags:
            t = await self.application.db.terms.find_one({"name": t_name, "type": "1"})
            if t:
                t_id = t['_id']
            else:
                t = await self.application.db.terms.insert_one({"name": t_name, "type": "1"})
                t_id = t.inserted_id
            t_ids.append(t_id)
        post_id = await self.application.db.posts.insert_one(
            {"title": title, "content": content, "user": ObjectId(u_id), "category": category_ids, "tags": t_ids,
             "post_date": datetime.datetime.now()})

