from bson import ObjectId
import config
from models import join
from models import sidebar
from views.base import BaseHandler
from .base import DBMixin
import math
import w3lib.url
import timeago
import datetime
import time
class CategoryPageHandler(BaseHandler,DBMixin):
    async def get(self,c_id,page=1):
        if not page:
            page=1
        posts =  await self.db.posts.find({"category":ObjectId(c_id),"type":0}).sort([("post_date",-1)]).skip(self.articles_per_page * (int(page) - 1)).limit(self.articles_per_page).to_list(length=self.articles_per_page)
        c_hot_posts = await sidebar.c_hot_posts(self,c_id)
        hot_posts = await sidebar.hot_posts(self)
        posts = await join.post_user(posts, self.db)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        posts = await join.posts_tags(posts, self.db)
        for post in posts:
            await self.generate_post_link([post])
            post['time_ago'] = timeago.format(post['post_date'], now, self.timeago_language)
            await self.get_thumb_image([post])
            if self.data['lang'] in ["zh-tw", "zh-hk"]:
                # x['content'] = await self.cc_async_s2t(x['content'])
                post['title'] = await self.cc_async_s2t(post['title'])
                post['user']['user_name'] = await self.cc_async_s2t(post['user']['user_name'])
                for tag in post['tags']:
                    tag['name'] = await self.cc_async_s2t(tag['name'])
            elif self.data['lang'] == 'zh-cn':
                post['title'] = await self.cc_async(post['title'])
                post['user']['user_name'] = await self.cc_async(post['user']['user_name'])
                for tag in post['tags']:
                    tag['name'] = await self.cc_async(tag['name'])
        for post in posts:
            post['post_title'] = post['title']
            post['user']['user_link'] = await self.generate_author_link_by_author(post['user'])
        list_path = 'category&id={}'.format(c_id)
        category = await self.db.terms.find_one({"_id":ObjectId(c_id)})
        data={}
        data['category'] = category
        data['next_page'] = "/page/{}".format(int(page) + 1)
        data['page'] = int(page)
        # data['post_number'] = await self.db.posts.count_documents({"category":ObjectId(c_id),"type":0})
        # data['max_page'] = math.ceil(data['post_number'] / self.articles_per_page)
        # if data['max_page'] <= 0:
        #     data['max_page'] = 1
        self.data.update(data)
        self.data['posts'] = posts
        self.data['next_page'] = "/c/{}/page/{}".format(c_id,int(page) + 1)
        if self.data['lang']:
            self.data['next_page'] = w3lib.url.add_or_replace_parameter(self.data['next_page'], 'lang', self.data['lang'])
        self.data['hot_posts'] = hot_posts
        await self.get_menu()
        self.render('page/category.html',menus=self.data['menus'],posts=posts,c_id=c_id,
                    config=config,page=page,hot_posts=c_hot_posts,list_path=list_path,data=data)
