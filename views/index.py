from tornado.web import RequestHandler
import timeago, datetime
from config import hot_news_num
from bson import ObjectId
import config
import time
from models import join,sidebar
from .base import BaseHandler,DBMixin
import w3lib.url

class IndexPageHandler(BaseHandler,DBMixin):
    async def get(self,page=1):
        user = await self.get_user()
        menus = await self.db.menu.find({"type": "left"}).to_list(length=10)
        posts =  await self.db.posts.find({"type":0}).sort([("post_date",-1)]).skip(self.articles_per_page * (int(page) - 1)).limit(self.articles_per_page).to_list(length=self.articles_per_page)
        posts = await join.post_user(posts,self.db)
        posts = await self.get_thumb_image(posts)
        #print(posts)
        hot_posts = await sidebar.hot_posts(self)
        #self.write('ok')
        path = self.request.path
        list_path = 'index'
        for post in posts:
            post['post_title'] = post['title']
            post['user']['user_link'] = await self.generate_author_link_by_author(post['user'])
        await self.generate_post_link(posts)
        posts = await join.post_user(posts, self.db)
        posts = await join.posts_tags(posts, self.db)
        # print(posts)
        self.data['menus'] = menus
        self.data['posts'] = posts
        self.data['next_page'] = "/page/{}".format(int(page) + 1)
        if self.data['lang']:
            self.data['next_page'] = w3lib.url.add_or_replace_parameter(self.data['next_page'], 'lang', self.data['lang'])

        self.render('page/index.html',menus=menus,posts=posts,config=config,page=page,hot_posts=hot_posts,user=user,path=path,list_path=list_path)
