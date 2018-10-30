from tornado.web import RequestHandler
import tornado
from bson import ObjectId
import config
from lxml import etree
from models import join,sidebar
from .base import BlockingHandler
from config import articles_per_page


class ArticleHandler(BlockingHandler):
    def related_sort(self,terms_id,related_posts):
        orders = {}
        for i, term_id in enumerate(terms_id):
            orders[term_id] = i
        print('ttt',terms_id,orders,related_posts)
        sort_key = {}
        for related_post in related_posts:
            order_match_count = -sum(el in  terms_id for el in related_post['tags'])
            order_first = min(orders[t] for t in related_post['tags'] if t in terms_id)
            sort_key[related_post['_id']] = (order_match_count,order_first)
        return sorted(related_posts, key=lambda x: sort_key[x['_id']])

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
        tags_id = post['tags']
        #print(tags_id)
        for t_id in tags_id:
            t = await self.application.db.terms.find_one({"_id":ObjectId(t_id)})
            if t:
                tags.append(t)
        post['tags'] = tags
        post['post_date'] = post['post_date'].strftime("%Y-%m-%d %H:%M")
        #post = await self.application.db.posts.find_one({"_id":ObjectId(post_id)})
        #print(post)
        post_etree = etree.HTML(post['content'])
        post_desc = ''.join([i.strip() for i in post_etree.xpath(".//text()")])[:200]
        #post_desc = post_etree.cssselect('p')[0].text
        post['desc'] = post_desc
        print(post)
        menu_left = await self.application.db.menu.find({"type": "left"}).to_list(length=10)
        hot_posts = await sidebar.hot_posts(self.application.db)
        #TODO
        # 1.tags_id 为空时 不查询相关文章 并使用category_id 补充相关文章

        #related_posts =  await self.application.db.posts.find({'tags': {'$in': tags_id},'_id': {'$ne': post['_id']}}).sort([("views",-1)])\
            #.limit(articles_per_page).to_list(length=articles_per_page)
        print(tags_id)
        related_posts =  await self.application.db.posts.find({'tags': {'$in': tags_id},'_id': {'$ne': post['_id']}}) \
            .limit(articles_per_page).to_list(length=articles_per_page)
        related_posts = self.related_sort(tags_id,related_posts)
        related_posts = await join.post_user(related_posts, self.application.db)
        related_posts = await self.get_posts_desc(related_posts)
        self.set_header('cache-control',
                        'public, stale-while-revalidate=120,stale-if-error=3600,max-age=5,s-maxage=600')
        if language == 'zh-cn':
            post['title'] = await self.cc_async(post['title'])
            post['content'] = await self.cc_async(post['content'])
            self.render('article.html',menu_left=menu_left,post=post,config=config,hot_posts=hot_posts,related_posts=related_posts)
        else:
            self.render('article.html', menu_left=menu_left, post=post, config=config,hot_posts=hot_posts,related_posts=related_posts)

