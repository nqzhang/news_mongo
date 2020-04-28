from tornado.web import RequestHandler
import timeago, datetime
from bson import ObjectId
from config import articles_per_page
import config
from models import join
from .base import BaseHandler,DBMixin

class TagPageHandler(BaseHandler,DBMixin):
    async def get(self,t_id,page=1):
        menus = await self.db.menu.find({"type": "left"}).to_list(length=10)
        posts =  await self.db.posts.find({"tags":ObjectId(t_id),"type":0}).sort([("post_date",-1)]).skip(articles_per_page * (int(page) - 1)).limit(articles_per_page).to_list(length=articles_per_page)
        posts = await join.post_user(posts, self.db)
        #posts = await self.get_thumb_image(posts)
        list_path = 'tag&id={}'.format(t_id)
        self.render('page/tag.html',menus=menus,posts=posts,t_id=t_id,config=config,page=page,list_path=list_path)
