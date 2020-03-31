from tornado.web import RequestHandler
import timeago, datetime
from config import articles_per_page,hot_news_num
from bson import ObjectId
import config
import time
from models import join,sidebar
from .base import BaseHandler,DBMixin


class IndexPageHandler(BaseHandler,DBMixin):
    async def get(self,page=1):
        user = await self.get_user()
        menus = await self.application.db.menu.find({"type": "left"}).to_list(length=10)
        posts =  await self.application.db.posts.find({"type":0}).sort([("post_date",-1)]).skip(articles_per_page * (int(page) - 1)).limit(articles_per_page).to_list(length=articles_per_page)
        posts = await join.post_user(posts,self.application.db)
        #posts = await self.get_thumb_image(posts)
        hot_posts = await sidebar.hot_posts(self)
        #self.write('ok')
        path = self.request.path
        list_path = 'index'
        self.render('page/index.html',menus=menus,posts=posts,config=config,page=page,hot_posts=hot_posts,user=user,path=path,list_path=list_path)
