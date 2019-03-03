import tornado
import hashlib
from concurrent.futures import ThreadPoolExecutor
from opencc import OpenCC
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
import urllib.parse as urlparse
from urllib.parse import urlencode
from lxml import etree
from bson import ObjectId
import asyncio
from models import sidebar
from config import session_ttl
import config
def authenticated_async(method):
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        self.current_user = yield gen.Task(self.get_current_user_async)
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
            raise tornado.web.HTTPError(403)
        else:
            result = method(self, *args, **kwargs) # updates
            if result is not None:
                yield result
    return wrapper




class BlockingBaseHandler(tornado.web.RequestHandler):
    def __init__(self,application, request, **kwargs):
        self.executor = ThreadPoolExecutor(2)
        super(BlockingBaseHandler, self).__init__(application, request, **kwargs)

class BlockingHandler(BlockingBaseHandler):
    @run_on_executor
    def cc_async(self,text):
        cc = OpenCC('t2s')
        text = cc.convert(text)
        return text

    @run_on_executor
    def get_thumb_image(self,posts):
        for post in posts:
            if 'post_thumb' not in post:
                post_etree = etree.HTML(post['content'])
                if post_etree is not None:
                    img = post_etree.cssselect("img:first-child")
                    if len(img) > 0:
                        post_thumb = img[0].get('src')
                        if post_thumb:
                            post['post_thumb'] = post_thumb
        return posts
    @run_on_executor
    def get_post_desc(self,post):
        if not post['content']:
            post_desc=''
        else:
            post_etree = etree.HTML(post['content'])
            post_desc = ''.join([i.strip() for i in post_etree.xpath(".//text()")])[:200]
            # post_desc = post_etree.cssselect('p')[0].text
        post['desc'] = post_desc
        return post
    async def get_posts_desc(self,posts):
        new_posts = []
        for post in posts:
            post =  await self.get_post_desc(post)
            new_posts.append(post)
        return new_posts


class BaseHandler(BlockingHandler):
    async def prepare(self):
        self.user = await self.get_user()
    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        ns.update({"user": self.user})
        return ns

    async def get_user(self):
        if await self.is_login():
            uid = tornado.escape.native_str(self.get_secure_cookie('uid'))
            user = await self.application.db.users.find_one({'_id':ObjectId(uid)})
            u_categorys = await sidebar.u_categorys(self.application.db,ObjectId(uid))
            need_keys = ['user_name','email','is_active','_id']
            user = {key: user.get(key,0) for key in need_keys}
            user['is_login'] = True
            user['categorys'] = u_categorys
        else:
            user={}
            user['is_login'] = False
        return user
    async def get_uid_name(self):
        if await self.is_login():
            uid = tornado.escape.native_str(self.get_secure_cookie('uid'))
            user = await self.application.db.users.find_one({'_id': ObjectId(uid)})
            need_keys = ['_id','user_name']
            user = {key: user.get(key, 0) for key in need_keys}
        else:
            user = False
        return user
    async def is_login(self):
        sessionid = self.get_secure_cookie('sessionid')
        sig = tornado.escape.native_str(self.get_secure_cookie('sig'))
        uid = self.get_secure_cookie('uid')
        if not (sessionid and sig and uid):
            return False
        user_salt = await self.application.redis.get(uid)
        if not user_salt:
            uid_str = uid.decode()
            user = await self.application.db.users.find_one({'_id':ObjectId(uid_str)})
            user_salt_str = user['password']['salt']
            user_salt = user_salt_str.encode()
            user_id = str(user['_id'])
            await self.application.redis.set(user_id, user_salt, expire=session_ttl)
        hashstr = sessionid + user_salt + uid
        user = {}
        #print(hashlib.sha512(hashstr).hexdigest())
        if sig == hashlib.sha512(hashstr).hexdigest():
            return True
        return False

class UserHander(BaseHandler):
    async def prepare(self):
        self.set_cookie("_xsrf", self.xsrf_token,domain=config.cookie_domain)
        await super(UserHander, self).prepare()
    @gen.coroutine
    def get_current_user_async(self):
        sessionid = self.get_secure_cookie('sessionid')
        sig = tornado.escape.native_str(self.get_secure_cookie('sig'))
        uid = self.get_secure_cookie('uid')
        if not (sessionid and sig and uid):
            return False
        user_salt = yield self.application.redis.get(uid)
        hashstr = sessionid + user_salt + uid
        user = {}
        #print(hashlib.sha512(hashstr).hexdigest())
        print()
        if sig == hashlib.sha512(hashstr).hexdigest():
            return uid
        return False
