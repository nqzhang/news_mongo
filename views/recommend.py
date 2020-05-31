from tornado.web import RequestHandler
from .base import BaseHandler,DBMixin
from config import articles_per_page,hot_news_num
from models import join,sidebar
import config

class recommendPageHandler(BaseHandler,DBMixin):
    async def get(self,page=1):
        user = await self.get_user()
        #posts =  await self.db.posts.find({"is_real_user": 1,"type":0,"is_recommend":{"$ne":False}}).sort([("score",-1)]).skip(articles_per_page * (int(page) - 1)).limit(articles_per_page).to_list(length=articles_per_page)
        posts =  await self.db.posts.find({"type":0,"is_recommend":{"$ne":False},"score" : { "$exists" : True }}).sort([("score",-1)]).skip(articles_per_page * (int(page) - 1)).limit(articles_per_page).to_list(length=articles_per_page)
        posts = await join.post_user(posts,self.db)
        #posts = await self.get_thumb_image(posts)
        hot_posts = await sidebar.hot_posts(self)
        #self.write('ok')
        path = self.request.path
        list_path = 'recommend'
        await self.get_menu()
        self.render('page/index.html',menus=self.data['menus'],posts=posts,config=config,page=page,hot_posts=hot_posts,user=user,path=path,list_path=list_path)
