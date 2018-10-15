from tornado.web import RequestHandler
import tornado
from bson import ObjectId
import config
from lxml import etree
from models import sidebar
from .base import BlockingHandler

class ArticleHandler(BlockingHandler):
    async def get(self, post_id,language='zh-tw'):
        post = await self.application.db.posts.find_one({"_id":ObjectId(post_id)})
        u_id = post['user']
        u = await self.application.db.users.find_one({"_id":ObjectId(u_id)})
        post['user'] = u
        category = []
        for c_id in post['category']:
            c = await self.application.db.terms.find_one({"_id":ObjectId(c_id)})
            category.append(c)
        post['category'] = category
        tags = []
        for t_id in post['tags']:
            t = await self.application.db.terms.find_one({"_id":ObjectId(t_id)})
            tags.append(t)
        post['tags'] = tags
        post['post_date'] = post['post_date'].strftime("%Y-%m-%d %H:%M")
        #post = await self.application.db.posts.find_one({"_id":ObjectId(post_id)})
        #print(post)
        post_etree = etree.HTML(post['content'])
        post_desc = ''.join([i.strip() for i in post_etree.xpath(".//text()")])[:200]
        #post_desc = post_etree.cssselect('p')[0].text
        post['desc'] = post_desc

        menu_left = await self.application.db.menu.find({"type": "left"}).to_list(length=10)
        hot_posts = await sidebar.hot_posts(self.application.db)
        self.set_header('cache-control',
                        'public, stale-while-revalidate=120,stale-if-error=3600,max-age=5,s-maxage=2592000')
        if language == 'zh-cn':
            post['title'] = await self.cc_async(post['title'])
            post['content'] = await self.cc_async(post['content'])
            self.render('article.html',menu_left=menu_left,post=post,config=config,hot_posts=hot_posts)
        else:
            self.render('article.html', menu_left=menu_left, post=post, config=config,hot_posts=hot_posts)

