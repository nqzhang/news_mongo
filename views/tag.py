from tornado.web import RequestHandler
import timeago, datetime
from bson import ObjectId
from config import articles_per_page
import config
from models import join
from views.base import BaseHandler

class TagPageHandler(BaseHandler):
    async def get(self,t_id,page=1):
        user = await self.get_user()
        menu_left = await self.application.db.menu.find({"type": "left"}).to_list(length=10)
        posts =  await self.application.db.posts.find({"tags":ObjectId(t_id)}).sort([("post_date",-1)]).skip(articles_per_page * (int(page) - 1)).limit(articles_per_page).to_list(length=articles_per_page)
        posts = await join.post_user(posts, self.application.db)
        #posts = await self.get_thumb_image(posts)
        self.render('tag.html',menu_left=menu_left,posts=posts,t_id=t_id,config=config,page=page,user=user)
