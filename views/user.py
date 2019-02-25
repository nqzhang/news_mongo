from views.base import UserHander
import tornado.web
import tornado
from views.base import authenticated_async
from pymongo import ReturnDocument
import datetime
from bson import ObjectId
import config
from models import join,sidebar
from bson.json_util import dumps
from utils.base import attrDict
from utils.tools import post_time_format
from utils.qetag import get_io_qetag
import os
from tornado.concurrent import run_on_executor
from io import BytesIO

class PostEditHandler(UserHander):
    @authenticated_async
    async def get(self,post_id=0):
        active = 'edit'
        post={}
        if post_id != 0:
            post = await self.application.db.posts.find_one({"_id": ObjectId(post_id),"user":ObjectId(self.current_user.decode())})
            post = await join.post_tags(post, self.application.db)
            post = await join.post_category(post, self.application.db)
            content = post.pop('content')
        else:
            content=''
            #print(post)
        post['post_id'] = post_id
        post_json = dumps(post)
        #print(self.current_user)
        self.render('page/postedit.html',config=config,active=active,post=post,post_json=post_json,content=content)


class PostAjaxHandler(UserHander):
    @authenticated_async
    async def post(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        u_id =  self.current_user.decode()
        content = self.get_argument('content')
        post_id = self.get_argument('post_id')
        if not content.strip():
            raise tornado.web.HTTPError(500, reason='content can not be empty')
        title = self.get_argument('title')
        if not title.strip():
            raise tornado.web.HTTPError(500, reason='title can not be empty')
        tags = [x for x in self.get_argument('tags').split(',') if x]
        category_site = [i.lower() for i in self.get_argument('category_site').split(',') if i]
        if len(category_site) != 1:
            raise tornado.web.HTTPError(500, reason='wrong category_site')
        category_person = [i.lower() for i in self.get_argument('category_person').split(',') if i]
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
            c = await self.application.db.terms.find_one({"name": c_name, "type": "2","user":ObjectId(u_id)})
            if c:
                c_id = c['_id']
            else:
                c = await self.application.db.terms.insert_one({"name": c_name, "type": "2","user":ObjectId(u_id)})
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
        if post_id == '0':
            post_id = await self.application.db.posts.insert_one(
                {"title": title, "content": content, "user": ObjectId(u_id),type:0,"category": category_ids, "tags": t_ids,
                 "post_date": datetime.datetime.now(),"is_real_user":1})
            post_id = str(post_id.inserted_id)
        else:
            await self.application.db.posts.replace_one({'_id': ObjectId(post_id),"user": ObjectId(u_id)},
                {"title": title, "content": content, "user": ObjectId(u_id),type:0,"category": category_ids, "tags": t_ids,
                 "post_date": datetime.datetime.now(),"is_real_user":1})
            post_id = str(post_id)
        publish_success = {}
        publish_success['post_id'] = post_id
        publish_success['title'] = title
        self.write(publish_success)

class PostListHandler(UserHander):
    @authenticated_async
    async def get(self):
        #print(self.current_user)
        active = 'list'
        posts = await self.application.db.posts.find({'user':ObjectId(self.current_user.decode()),type:0}).sort([("post_date", -1)]).to_list(length=None)
        for post in posts:
            post['post_date'] = post['post_date'].strftime("%Y-%m-%d %H:%M:%S")
            views = post.get('views',0)
            post['views'] = views
            #print(post)
        print(posts)
        self.render('page/postlist.html',config=config,active=active,posts=posts)

class PostDeleteHandler(UserHander):
    @authenticated_async
    async def post(self):
        post_id = self.get_argument('post_id')
        result = await self.application.db.posts.delete_one({'_id': ObjectId(post_id),'user': ObjectId(self.current_user.decode())})
        self.write(post_id)

class ckuploadHandeler(UserHander):
    @authenticated_async
    @run_on_executor
    def post(self):

        """CKEditor file upload"""
        error = ''
        url = ''
        self.img_data = None
        #callback = self.get_argument("CKEditorFuncNum")
        print(self.request.arguments)
        if self.request.method == 'POST' and 'upload' in self.request.files:
            fileobj = self.request.files['upload']
            fhash = get_io_qetag(BytesIO(fileobj[0]['body']))
            fbasename, fext = os.path.splitext(fileobj[0]['filename'])
            fname = '%s%s' % (fhash, fext)
            filepath = os.path.join(self.settings['static_path'], 'upload', fname)
            # 检查路径是否存在，不存在则创建
            dirname = os.path.dirname(filepath)
            if not os.path.exists(dirname):
                try:
                    os.makedirs(dirname)
                except:
                    error = 'ERROR_CREATE_DIR'

            elif not os.access(dirname, os.W_OK):
                error = 'ERROR_DIR_NOT_WRITEABLE'
            if not error:
                print(filepath)
                with open(filepath,'wb') as up:      #有些文件需要已二进制的形式存储，实际中可以更改
                    up.write(fileobj[0]['body'])
                    self.img_data = {"u_id": ObjectId(self.current_user.decode()), "fname": fname}
                urlpath ='%s/%s' % ('upload', fname)
                url = self.static_url(urlpath)
        else:
            error = 'post error'
        res = {}
        res['uploaded'] =1
        res['fileName']=fname
        res['url'] = url
        self.write(res)

    def on_finish(self):
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.spawn_callback(self.insert_img_data)

    async def insert_img_data(self):
        if self.img_data:
            exists = await self.application.db.images.find_one({ "fname": self.img_data['fname']})
            if not exists:
                await self.application.db.images.insert_one(self.img_data)
            #else:
                #print('数据库已存在此图片')