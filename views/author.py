from .base import UserHander
import config
from utils.base import attrDict
from utils.tools import post_time_format
from bson import ObjectId
from models import join,sidebar

class AuthorPageHandler(UserHander):
    async def get(self,u_id,page=1):
        page = 1 if not page else page
        posts = await self.application.db.posts.find({"user": ObjectId(u_id)}).sort([("post_date", -1)]).skip(
            config.articles_per_page * (int(page) - 1)).limit(config.articles_per_page).to_list(length=config.articles_per_page)
        posts = await self.get_posts_desc(posts)
        posts = [attrDict(post) for post in posts]
        posts = map(post_time_format,posts)
        author = attrDict(await self.application.db.users.find_one({"_id": ObjectId(u_id)}))
        u_categorys = list(map(attrDict,await sidebar.u_categorys(self.application.db, ObjectId(u_id))))
        self.render('page/author.html',posts=posts,author=author, config=config, page=page,u_categorys=u_categorys)