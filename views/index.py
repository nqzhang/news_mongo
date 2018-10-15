from tornado.web import RequestHandler
import timeago, datetime
from config import articles_per_page,hot_news_num
from bson import ObjectId
import config
import time
from models import join,sidebar
from views.base import BaseHandler

class IndexPageHandler(BaseHandler):
    async def get(self,page=1):
        is_login = await self.is_login()
        menu_left = await self.application.db.menu.find({"type": "left"}).to_list(length=10)
        posts =  await self.application.db.posts.find().sort([("post_date",-1)]).skip(articles_per_page * (int(page) - 1)).limit(articles_per_page).to_list(length=articles_per_page)
        posts = await join.post_user(posts,self.application.db)
        hot_posts = await sidebar.hot_posts(self.application.db)
        #self.write('ok')
        self.render('index.html',menu_left=menu_left,posts=posts,config=config,page=page,hot_posts=hot_posts,is_login=is_login)
