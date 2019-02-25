from tornado.web import RequestHandler
import timeago, datetime
from bson import ObjectId
from config import articles_per_page
import config
from models import join
from models import sidebar
from views.base import BaseHandler


class CategoryPageHandler(BaseHandler):
    async def get(self,c_id,page=1):
        menu_left = await self.application.db.menu.find({"type": "left"}).to_list(length=10)
        posts =  await self.application.db.posts.find({"category":ObjectId(c_id),type:0}).sort([("post_date",-1)]).skip(articles_per_page * (int(page) - 1)).limit(articles_per_page).to_list(length=articles_per_page)
        c_hot_posts = await sidebar.c_hot_posts(self.application.db,c_id)
        posts = await join.post_user(posts, self.application.db)
        #posts = await self.get_thumb_image(posts)
        self.render('page/category.html',menu_left=menu_left,posts=posts,c_id=c_id,config=config,page=page,hot_posts=c_hot_posts)
