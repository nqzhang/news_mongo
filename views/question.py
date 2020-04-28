from .base import BaseHandler,DBMixin
from bson import ObjectId
from utils.base import attrDict
from models import join,sidebar
from tornado.web import RequestHandler
from config import articles_per_page
from bson.json_util import dumps
import config
from utils.tools import *

class QuestionHandler(BaseHandler,DBMixin):
    async def get(self, question_id,language='zh-tw'):
        post = await self.db.posts.find_one({"_id":ObjectId(question_id)})
        u_id = post['user']
        u = await self.db.users.find_one({"_id":ObjectId(u_id)})
        author = attrDict(u)
        post['user'] = u
        tags_id = [i for i in post['tags'] if i]
        tags = []
        #print(tags_id)
        for t_id in tags_id:
            t = await self.db.terms.find_one({"_id":ObjectId(t_id)})
            if t:
                tags.append(t)
        post['tags'] = tags
        post['post_date'] = post['post_date'].strftime("%Y-%m-%d %H:%M")
        #post = await self.db.posts.find_one({"_id":ObjectId(post_id)})
        #print(post)
        menu = await self.db.menu.find({"type": "left"}).to_list(length=10)
        hot_posts = await sidebar.hot_posts(self,post_type=1)
        u_new_posts = await sidebar.u_new_posts(self,u_id,post_type=1)
        #related_posts =  await self.db.posts.find({'tags': {'$in': tags_id},'_id': {'$ne': post['_id']}}).sort([("views",-1)])\
            #.limit(articles_per_page).to_list(length=articles_per_page)
        if tags_id:
            related_posts =  await self.db.posts.find({'tags': {'$in': tags_id},'_id': {'$ne': post['_id']}}).sort([("post_date",-1)]) \
                .limit(articles_per_page).to_list(length=articles_per_page)
            related_posts = await related_sort(tags_id,related_posts,related_type='tags')
        else:
            related_posts = []
        related_posts = await join.post_user(related_posts, self.db)
        related_posts = await self.get_posts_desc(related_posts)
        # TODO 用户是否登录等个人数据 可以通过js来实时获取，这样就可以在CDN缓存html页面，当前国内文章页速度响应一般在600ms以内，
        #  因此可先不做
        #self.set_header('cache-control',
        #                'public, stale-while-revalidate=120,stale-if-error=3600,max-age=5,s-maxage=600')
        if language == 'zh-cn':
            post['title'] = await self.cc_async(post['title'])
            post['content'] = await self.cc_async(post['content'])
        #post_etree = etree.HTML(post['content'])
        #post_desc = ''.join([i.strip() for i in post_etree.xpath(".//text()")])[:200]
        #post['desc'] = post_desc
        post = await self.get_post_desc(post)
        #处理author.user_name为空的情况
        if not author.user_name:
            author.user_name = 'None'
        data={}
        data['author'] = author
        self.render('page/question.html', menu=menu, post=post, config=config,hot_posts=hot_posts,related_posts=related_posts,
                        u_new_posts=u_new_posts,author=author,data=data)
