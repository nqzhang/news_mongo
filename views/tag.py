from tornado.web import RequestHandler
import timeago, datetime
from bson import ObjectId
from config import articles_per_page
import config
from models import join
from .base import BaseHandler,DBMixin
import w3lib.url

class TagPageHandler(BaseHandler,DBMixin):
    async def get(self,t_id,page=1):
        menus = await self.db.menu.find({"type": "left"}).to_list(length=10)
        posts =  await self.db.posts.find({"tags":ObjectId(t_id),"type":0}).sort([("post_date",-1)]).skip(articles_per_page * (int(page) - 1)).limit(articles_per_page).to_list(length=articles_per_page)
        posts = await join.post_user(posts, self.db)
        tag = await self.db.terms.find_one({"_id":ObjectId(t_id)})
        #posts = await self.get_thumb_image(posts)
        list_path = 'tag&id={}'.format(t_id)
        posts = await join.posts_tags(posts, self.db)
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for x in posts:
            await self.generate_post_link([x])
            x['time_ago'] = timeago.format(x['post_date'], now, self.timeago_language)
            await self.get_thumb_image([x])
            if self.data['lang'] in ["zh-tw", "zh-hk"]:
                # x['content'] = await self.cc_async_s2t(x['content'])
                x['title'] = await self.cc_async_s2t(x['title'])
            elif self.data['lang'] == 'zh-cn':
                x['title'] = await self.cc_async(x['title'])
            x['user']['user_link'] = await self.generate_author_link_by_author(x['user'])
        data={}
        data['posts'] = posts
        data['menus'] = menus
        data['tag'] = tag
        self.data.update(data)
        self.data['next_page'] = "/t/{}/page/{}".format(t_id, int(page) + 1)
        if self.data['lang']:
            self.data['next_page'] = w3lib.url.add_or_replace_parameter(self.data['next_page'], 'lang',
                                                                        self.data['lang'])
        self.render('page/tag.html',menus=menus,posts=posts,t_id=t_id,config=config,page=page,list_path=list_path)
