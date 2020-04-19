from bson import ObjectId
import config
from models import join
from models import sidebar
from views.base import BaseHandler
from .base import DBMixin
import math

class CategoryPageHandler(BaseHandler,DBMixin):
    async def get(self,c_id,page=1):
        if not page:
            page=1
        menus = await self.application.db.menu.find({"type": "left"}).to_list(length=10)
        posts =  await self.application.db.posts.find({"category":ObjectId(c_id),"type":0}).sort([("post_date",-1)]).skip(self.articles_per_page * (int(page) - 1)).limit(self.articles_per_page).to_list(length=self.articles_per_page)
        c_hot_posts = await sidebar.c_hot_posts(self,c_id)
        posts = await join.post_user(posts, self.application.db)
        posts = await self.get_thumb_image(posts)
        list_path = 'category&id={}'.format(c_id)
        category = await self.application.db.terms.find_one({"_id":ObjectId(c_id)})
        data={}
        data['category'] = category
        data['page'] = int(page)
        data['post_number'] = await self.application.db.posts.find({"category":ObjectId(c_id),"type":0}).count()
        data['max_page'] = math.ceil(data['post_number'] / self.articles_per_page)
        if data['max_page'] <= 0:
            data['max_page'] = 1
        self.render('page/category.html',menus=menus,posts=posts,c_id=c_id,config=config,page=page,hot_posts=c_hot_posts,list_path=list_path,data=data)
