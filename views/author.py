from .base import UserHander,DBMixin
import config
from utils.base import attrDict
from utils.tools import post_time_format
from bson import ObjectId
from models import join,sidebar
import math
import w3lib.url
import json

class AuthorPageHandler(UserHander,DBMixin):
    async def get(self,u_id,u_c_id=None,page=1):
        #print(u_id)
        page = 1 if not page else page
        if u_c_id:
            #print(u_c_id)
            posts = await self.db.posts.find({"user": ObjectId(u_id),"category":ObjectId(u_c_id)}).sort([("post_date", -1)]).skip(
            self.articles_per_page * (int(page) - 1)).limit(self.articles_per_page).to_list(length=self.articles_per_page)
        else:
            posts = await self.db.posts.find({"user": ObjectId(u_id),"type":0}).sort([("post_date", -1)]).skip(
                self.articles_per_page * (int(page) - 1)).limit(self.articles_per_page).to_list(length=self.articles_per_page)
        hot_posts = await sidebar.hot_posts(self)
        posts = await self.get_posts_desc(posts)
        posts = [attrDict(post) for post in posts]
        #print(json.dumps(posts,default=str))
        posts = list(map(post_time_format,posts))
        posts = await self.get_thumb_image(posts)
        author = await self.db.users.find_one({"_id": ObjectId(u_id)})
        if self.data['lang'] == 'zh-cn':
            author['user_name'] = await self.cc_async(author['user_name'])
        if self.data['lang'] in ("zh-tw","zh-hk"):
            author['user_name'] = await self.cc_async_s2t(author['user_name'])
        #处理author.user_name为空的情况
        if not author['user_name']:
            author['user_name'] = 'None'
        await self.generate_post_link(posts)
        for post in posts:
            if self.data['lang'] in ["zh-tw", "zh-hk"]:
                # x['content'] = await self.cc_async_s2t(x['content'])
                post['title'] = await self.cc_async_s2t(post['title'])
            elif self.data['lang'] == 'zh-cn':
                post['title'] = await self.cc_async(post['title'])
        data={}
        data['posts'] = posts
        # data['post_number'] = await self.db.posts.count_documents({"user": ObjectId(u_id),"type":0})
        data['author'] = author
        data['user'] = author
        data['page'] = page
        # data['max_page'] = math.ceil(data['post_number'] / self.articles_per_page)
        # if data['max_page'] <= 0:
        #     data['max_page'] = 1
        u_categorys = list(map(attrDict,await sidebar.u_categorys(self, ObjectId(u_id))))
        self.data.update(data)
        self.data['next_page'] = "/u/{}/page/{}".format(u_id, int(page) + 1)
        if self.data['lang']:
            self.data['next_page'] = w3lib.url.add_or_replace_parameter(self.data['next_page'], 'lang',self.data['lang'])
        self.data['hot_posts'] = hot_posts
        await self.get_menu()
        self.render('page/author.html',posts=posts, config=config, page=page,u_categorys=u_categorys,data=data)