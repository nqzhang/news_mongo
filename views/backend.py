from tornado.web import RequestHandler
import uuid
import datetime
import traceback
import json
from pymongo import ReturnDocument
import datetime
from bson import ObjectId
import tornado
from utils.hot import hot
from .base import UserHander,DBMixin,BlockingHandler


class NewPostHandler(BlockingHandler,DBMixin):
    def check_xsrf_cookie(self):
        pass
    async def post(self):
        body=json.loads(self.request.body.decode('utf-8'))
        code = body['code']
        if code != 'qtRjhwcGLHnXPQlC':
            raise tornado.web.HTTPError(500,reason='wrong password')
        filter_tags = ('',None)
        category = body.get('category',None)
        if category == "None":
            category = None
        tags = body['tags']
        tags = [i for i in tags if i not in filter_tags]
        title = body['title']
        content = body['content']
        user = body['user']
        post_type = body['post_type'] if 'post_type' in body else 'article'
        if post_type=='article':
            if category:
                category = [i.lower() for i in body['category'] if i]
            tag_type_num = 1
            post_type_num = 0
        else:
            category = None
            tag_type_num = 3
            post_type_num = 1
        # 插入文章
        post = await self.db.posts.find_one({"title": title, "type": post_type_num})
        if post:
            exeists = True
            post_id = 0
            self.write(str(post_id))
            return
        else:
            exeists = False
        #thumb = body['thumb']
        #guid = uuid.uuid4().hex
        #guid = uuid.uuid3(uuid.NAMESPACE_DNS, title).hex
        try:
            #插入用户
            u = await self.db.users.find_one({"user_name":user})
            if u:
                u_id = u['_id']
            else:
                u = await self.db.users.insert_one({"user_name":user})
                u_id = u.inserted_id
            # 只有当文章类型为article时，才有分类
            # 并且如果不存在category,创建
            if category:
                c_ids = []
                for c_name in category:
                    c = await self.db.terms.find_one({"name":c_name,"type":"0"})
                    if c:
                        c_id = c['_id']
                    else:
                        c = await self.db.terms.insert_one({"name":c_name,"type":"0"})
                        c_id = c.inserted_id

                    c_ids.append(c_id)
            # 如果不存在tag,创建
            # 无论是否存在,都返回tag_id
            t_ids = []
            for t_name in tags:
                t = await self.db.terms.find_one({"name": t_name, "type": tag_type_num})
                if t:
                    t_id = t['_id']
                else:
                    t = await self.db.terms.insert_one({"name":t_name,"type":tag_type_num})
                    t_id = t.inserted_id
                t_ids.append(t_id)
            #print(exeists)
            if not exeists:
                post_date = body.get('post_date', None)
                if  post_date:
                    post_date = datetime.datetime.strptime(post_date,"%Y-%m-%d %H:%M:%S")
                else:
                    post_date = datetime.datetime.now()
                post_data = {"title": title, "content": content, "user": u_id, "type": post_type_num,
                             "tags": t_ids, "post_date": post_date}
                desc = body.get('desc', None)
                if not desc:
                    await self.get_post_desc(post_data)
                post_thumb = body.get('post_thumb', None)
                if not post_thumb:
                    await self.get_thumb_image([post_data])
                if category:
                    post_data['category'] = c_ids
                post_id = await self.db.posts.insert_one(post_data)
                post_id = post_id.inserted_id
        except:
            traceback.print_exc()
        else:
            self.write(str(post_id))
        if post_id != 0:
            post_score = await hot(self.db,str(post_id))
            if self.es:
                post_es_data = {"site_id":self.site_id,"post_id":str(post_id),"title": title}
                res = await self.es.index(index=self.es_index,body=post_es_data,request_timeout=30)
                #print(res)

class ViewsHandler(DBMixin):
    async def post(self):
        if 'Googlebot' in self.request.headers["User-Agent"]:
            raise tornado.web.HTTPError(404,"Shit! Don't crawl me anymore.")
        post_id = self.get_body_argument('post_id')
        await self.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'views': 1}})
        post = await self.db.posts.find_one({'_id': ObjectId(post_id)})
        current_views = post['views']