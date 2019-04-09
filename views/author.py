from .base import UserHander
import config
from utils.base import attrDict
from utils.tools import post_time_format
from bson import ObjectId
from models import join,sidebar

class AuthorPageHandler(UserHander):
    async def get(self,u_id,u_c_id=None,page=1):
        page = 1 if not page else page
        if u_c_id:
            print(u_c_id)
            posts = await self.application.db.posts.find({"user": ObjectId(u_id),"category":ObjectId(u_c_id)}).sort([("post_date", -1)]).skip(
            config.articles_per_page * (int(page) - 1)).limit(config.articles_per_page).to_list(length=config.articles_per_page)
        else:
            posts = await self.application.db.posts.find({"user": ObjectId(u_id),"type":0}).sort([("post_date", -1)]).skip(
                config.articles_per_page * (int(page) - 1)).limit(config.articles_per_page).to_list(length=config.articles_per_page)
        posts = await self.get_posts_desc(posts)
        posts = [attrDict(post) for post in posts]
        posts = map(post_time_format,posts)
        author = await self.application.db.users.find_one({"_id": ObjectId(u_id)})
        #处理author.user_name为空的情况
        if not author['user_name']:
            author['user_name'] = 'None'
        data={}
        data['post_number'] = await self.application.db.posts.find({"user": ObjectId(u_id),"type":0}).count()
        data['author'] = author
        data['page'] = page
        u_categorys = list(map(attrDict,await sidebar.u_categorys(self.application.db, ObjectId(u_id))))
        self.render('page/author.html',posts=posts, config=config, page=page,u_categorys=u_categorys,data=data)