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
            raise HTTPError(403)
        else:
            result = method(self, *args, **kwargs) # updates
            if result is not None:
                yield result
    return wrapper


class UserHander(tornado.web.RequestHandler):
    def prepare(self):
        self.set_cookie("_xsrf", self.xsrf_token)
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
class BlockingHandler(tornado.web.RequestHandler):
    def __init__(self,application, request, **kwargs):
        self.executor = ThreadPoolExecutor(2)
        super(BlockingHandler, self).__init__(application, request, **kwargs)

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

class BaseHandler(BlockingHandler):
    async def is_login(self):
        sessionid = self.get_secure_cookie('sessionid')
        sig = tornado.escape.native_str(self.get_secure_cookie('sig'))
        uid = self.get_secure_cookie('uid')
        if not (sessionid and sig and uid):
            return False
        user_salt = await self.application.redis.get(uid)
        hashstr = sessionid + user_salt + uid
        user = {}
        #print(hashlib.sha512(hashstr).hexdigest())
        print()
        if sig == hashlib.sha512(hashstr).hexdigest():
            return True
        return False