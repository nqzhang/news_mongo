import hashlib
from concurrent.futures import ThreadPoolExecutor
from opencc import OpenCC
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado import gen
from urllib.parse import urlparse,urlencode
from lxml import etree
from bson import ObjectId
import asyncio
from models import sidebar
from config import session_ttl
import config
from pyquery import PyQuery as pq
import logging
import w3lib.url
import os
import tornado.web

class BlockingBaseHandler(tornado.web.RequestHandler):
    def __init__(self,application, request, **kwargs):
        self.executor = ThreadPoolExecutor(2)
        super(BlockingBaseHandler, self).__init__(application, request, **kwargs)

class BlockingHandler(BlockingBaseHandler):
    @run_on_executor
    def cc_async(self,text):
        text = self.application.cc.convert(text)
        return text
    @run_on_executor
    def cc_async_s2t(self,text):
        text = self.application.cc_s2t.convert(text)
        return text
    @run_on_executor
    def get_thumb_image(self,posts):
        for post in posts:
            if 'post_thumb' not in post:
                post['post_thumb'] = ''
                post_etree = etree.HTML(post['content'])
                if post_etree is not None:
                    img = post_etree.cssselect("img")
                    if len(img) > 0:
                        post_thumb = img[0].get('src')
                        if post_thumb:
                            post['post_thumb'] = post_thumb
        return posts

    async def generate_post_link(self,posts,site_id=None):
        if not site_id:
            domain = self.domain
        else:
            domain = self.application.dbs['by_site_id'][site_id]['domain']
        for post in posts:
            if self.views_theme == "wp":
                post['post_link'] = "//{}{}{}/".format(domain, post['post_date'].strftime("/%Y/%m/%d/"),
                                                       post['post_name'])
                if self.data.get('lang',None):
                    post['post_link'] = '{}{}/'.format(post['post_link'],self.data['lang'])
            else:
                post['post_link'] = '//{}/a/{}'.format(domain, str(post['_id']))
                if self.data.get('lang',None):
                    post['post_link'] = w3lib.url.add_or_replace_parameter(post['post_link'], 'lang', self.data['lang'])
        return posts
    async def generate_author_link_by_author(self,author,site_id=None):
        if not site_id:
            domain = self.domain
        else:
            domain = self.application.dbs['by_site_id'][site_id]['domain']
        if self.views_theme == "wp":
            author_link = "//{}/author/{}/".format(domain,author['user_nicename'])
        else:
            author_link = "//{}/u/{}/".format(domain, author['_id'])
        if self.data['lang']:
            author_link = author_link + self.data['lang'] + '/'
        return author_link

    @run_on_executor
    def get_post_desc(self,post):
        if not post['content']:
            post_desc=''
        else:
            post_etree = etree.HTML(post['content'])
            post_desc = ''.join([i.strip() for i in post_etree.xpath(".//text()")])[:120]
            # post_desc = post_etree.cssselect('p')[0].text
        post['desc'] = post_desc
        return post
    async def get_posts_desc(self,posts):
        new_posts = []
        for post in posts:
            post =  await self.get_post_desc(post)
            new_posts.append(post)
        return new_posts
    @run_on_executor
    def article_img_add_class(self,post):
        content_pq = pq(post['content'])
        for i in content_pq('img').items():
            if i.attr.src:
                i.add_class('lazyload')
                parsed_uri = urlparse(i.attr.src)
                domain = parsed_uri.netloc
                if domain.endswith('51cto.com'):
                    i.attr.src = w3lib.url.url_query_cleaner(i.attr.src, ['x-oss-process'], remove=True)
                i.attr('referrerpolicy', 'no-referrer');
                i.attr('data-original',i.attr.src)
                i.remove_attr('src')
        content = content_pq.html(method="html")
        post['content'] = content
        return post

    @run_on_executor
    def amp_process(self, post):
        content_pq = pq(post['content'])
        for i in content_pq('img').items():
            d = pq('<amp-img></amp-img>')
            d.attr["src"] = i.attr["src"]
            d.attr["layout"] = "responsive"
            if i.attr['width'] and '%' not in i.attr['width'] and i.attr['width'] != "auto":
                img_width = i.attr['width']
            else:
                img_width ="350"
            if i.attr['height'] and '%' not in i.attr['height'] and i.attr['width'] != "auto":
                img_height = i.attr['height']
            else:
                img_height ="250"
            d.attr["width"] =  img_width
            d.attr["height"] = img_height
            pq.replace_with(i,d)
        for i in content_pq('script').items():
            i.remove()
        for i in content_pq('style').items():
            i.remove()
        for i in content_pq('video').items():
            d = pq('<amp-video></amp-video>')
            d.attr["src"] = i.attr["src"]
            d.attr["controls"] = ''
            d.attr["layout"] = "responsive"
            if i.attr['width'] and '%' not in i.attr['width']:
                img_width = i.attr['width']
            else:
                img_width ="350"
            if i.attr['height'] and '%' not in i.attr['height']:
                img_height = i.attr['height']
            else:
                img_height ="250"
            d.attr["width"] =  img_width
            d.attr["height"] = img_height
            pq.replace_with(i,d)
        content = content_pq.html(method="html")
        post['content'] = content
        return post

class BaseHandler(BlockingHandler):
    async def prepare(self):
        self.user = await self.get_user()
        lang = self.get_argument("lang",None)
        self.data= {}
        self.data['lang'] = lang
        self.data['site_name'] = self.site_name
        self.data["origin_url"] = self.request.full_url()
        self.data['cn_url']= w3lib.url.add_or_replace_parameter(self.request.full_url(), 'lang', 'zh-cn')
        self.data['tw_url'] = w3lib.url.add_or_replace_parameter(self.request.full_url(), 'lang', 'zh-tw')
        self.data['hk_url'] = w3lib.url.add_or_replace_parameter(self.request.full_url(), 'lang', 'zh-hk')
        self.data['amp_url'] = w3lib.url.add_or_replace_parameter(self.request.full_url(), 'amp', '1')
        self.timeago_language_dict = {"zh-tw":"zh_TW","zh-cn":"zh_CN","zh-hk":"zh_TW"}
        self.timeago_language = self.timeago_language_dict[self.data['lang']] if self.data['lang'] else "zh_CN"
    def get_template_namespace(self):
        ns = super(BaseHandler, self).get_template_namespace()
        ns.update({"user": self.user})
        return ns

    async def get_user(self):
        if await self.is_login():
            uid = tornado.escape.native_str(self.get_secure_cookie('uid'))
            user = await self.db.users.find_one({'_id':ObjectId(uid)})
            u_categorys = await sidebar.u_categorys(self,ObjectId(uid))
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
            user = await self.db.users.find_one({'_id': ObjectId(uid)})
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
            user = await self.db.users.find_one({'_id':ObjectId(uid_str)})
            if not user:
                return False
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
        await super(UserHander, self).prepare()
        await self.check_authentication()

    async def check_authentication(self, optional=False):
        if not hasattr(self, '_current_user'):
            try:
                self._current_user = await self.get_current_user_async()
            except NotImplementedError:
                self._current_user = self.get_current_user()
        if self._current_user is None and not optional:
            login_url = self.get_login_url()
            if login_url:
                self.redirect(login_url)
            else:
                raise tornado.web.HTTPError(403)
    async def get_current_user_async(self):
        sessionid = self.get_secure_cookie('sessionid')
        sig = tornado.escape.native_str(self.get_secure_cookie('sig'))
        uid = self.get_secure_cookie('uid')
        if not (sessionid and sig and uid):
            return False
        user_salt = await self.application.redis.get(uid)
        hashstr = sessionid + user_salt + uid
        #print(hashlib.sha512(hashstr).hexdigest())
        if sig == hashlib.sha512(hashstr).hexdigest():
            return uid
        return False

class DBMixin(tornado.web.RequestHandler):
    def initialize(self):
        #super(DBMixin, self).initialize(application, request, **kwargs)
        self.db =  self.application.dbs['by_domain'][self.request.host].get('db_conn',None)
        self.db_name = self.application.dbs['by_domain'][self.request.host].get('db_name',None)
        self.site_name = self.application.dbs['by_domain'][self.request.host]['site_name']
        self.articles_per_page = self.application.dbs['by_domain'][self.request.host]['articles_per_page']
        self.cookie_domain = self.application.dbs['by_domain'][self.request.host]['domain']
        self.domain = self.application.dbs['by_domain'][self.request.host]['domain']
        self.views_theme = self.application.dbs['by_domain'][self.request.host].get('views_theme',None)
        self.set_cookie("_xsrf", self.xsrf_token)
        #self.es = self.application.dbs['by_domain'][self.request.host].get('es_conn',None)
        self.es = self.application.dbs['all'].get('es_conn',None)
        self.es_index = self.application.dbs['all'].get('es_index', None)
        self.site_id = self.application.dbs['by_domain'][self.request.host]['site_id']
        self.cdn_host =  self.application.dbs['by_site_id']['cdn'].get('domain', None)

    def get_template_path(self):
        return os.path.join(self.application.settings.get("template_path"),self.application.dbs['by_domain'][self.request.host]['theme'])

    def get_template_namespace(self):
        ns = super(DBMixin, self).get_template_namespace()
        ns.update({"site_name": self.site_name,"t_self":self})
        return ns

    def static_url(self, path, include_host=None, **kwargs):
        if self.cdn_host:
            relative_url = super(DBMixin, self).static_url(path, include_host=False, **kwargs)
            return '//' + self.cdn_host + relative_url
        else:
            return super(BaseHandler, self).static_url(path, include_host=include_host, **kwargs)

    #     self.set_header("Access-Control-Allow-Origin", '127.0.0.5')
    #     self.set_header("Access-Control-Allow-Headers", "x-requested-with")
    #     self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
