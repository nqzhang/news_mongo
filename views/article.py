from tornado.web import RequestHandler
import tornado
from bson import ObjectId
import config
from lxml import etree
from models import join,sidebar
from .base import BlockingHandler,BaseHandler
from config import articles_per_page
from utils.base import attrDict
from bson.json_util import dumps
from views.base import authenticated_async
from views.base import UserHander
import datetime

class ArticleHandler(BaseHandler):
    def related_sort(self,terms_id,related_posts,related_type='tags'):
        orders = {}
        for i, term_id in enumerate(terms_id):
            orders[term_id] = i
        sort_key = {}
        for related_post in related_posts:
            order_match_count = -sum(el in  terms_id for el in related_post[related_type])
            order_first = min(orders[t] for t in related_post[related_type] if t in terms_id)
            sort_key[related_post['_id']] = (order_match_count,order_first)
        return sorted(related_posts, key=lambda x: sort_key[x['_id']])

    async def get(self, post_id,language='zh-tw'):
        post = await self.application.db.posts.find_one({"_id":ObjectId(post_id)})
        u_id = post['user']
        u = await self.application.db.users.find_one({"_id":ObjectId(u_id)})
        author = attrDict(u)
        post['user'] = u
        tags_id = [i for i in post['tags'] if i]
        category_id = [i for i in post['category'] if i]
        category = []
        for c_id in post['category']:
            c = await self.application.db.terms.find_one({"_id":ObjectId(c_id)})
            category.append(c)
        post['category'] = category
        tags = []
        #print(tags_id)
        for t_id in tags_id:
            t = await self.application.db.terms.find_one({"_id":ObjectId(t_id)})
            if t:
                tags.append(t)
        post['tags'] = tags
        post['post_date'] = post['post_date'].strftime("%Y-%m-%d %H:%M")
        #post = await self.application.db.posts.find_one({"_id":ObjectId(post_id)})
        #print(post)
        menu_left = await self.application.db.menu.find({"type": "left"}).to_list(length=10)
        hot_posts = await sidebar.hot_posts(self.application.db)
        u_new_posts = await sidebar.u_new_posts(self.application.db,u_id)
        u_categorys =  await sidebar.u_categorys(self.application.db,u_id)
        #related_posts =  await self.application.db.posts.find({'tags': {'$in': tags_id},'_id': {'$ne': post['_id']}}).sort([("views",-1)])\
            #.limit(articles_per_page).to_list(length=articles_per_page)
        if tags_id:
            related_posts =  await self.application.db.posts.find({'tags': {'$in': tags_id},'_id': {'$ne': post['_id']}}).sort([("post_date",-1)]) \
                .limit(articles_per_page).to_list(length=articles_per_page)
            related_posts = self.related_sort(tags_id,related_posts,related_type='tags')
            '''通过mongodb aggregate 实现的tags排序
            related_posts=[]
            replated_posts_cursor =  self.application.db.posts.aggregate([
                {"$match": {"tags": {"$in": tags_id},'_id': {'$ne': post['_id']}}},
                {"$unwind": "$tags"},
                {"$match": {"tags": {"$in": tags_id}}},
                {"$group": {
                    "_id": "$_id",
                    "title": {"$first": "$title"},
                    "user": {"$first": "$user"},
                    "post_date": {"$first": "$post_date"},
                    "content": {"$first": "$content"},
                    "matches": {"$sum": 1},
                }},
                {"$sort": {"matches": -1}},
                {"$limit": articles_per_page},
            ],allowDiskUse=True)
            async for replated_post in replated_posts_cursor:
                related_posts.append(replated_post)
            print(related_posts)
        '''
        else:
            related_posts = []
        related_fill_num = articles_per_page - len(related_posts)
        if related_fill_num > 0:
            if category_id:
                #TODO 先根据日期排序 通过mongodb aggregate 实现速度太慢 以后可以采用elasticsearch 或者google custom search？
                related_posts_category = await self.application.db.posts.find({'category': {'$in': category_id},'_id': {'$ne': post['_id']}}).sort([("post_date",-1)]) \
                .limit(related_fill_num).to_list(length=related_fill_num)
                related_posts_category = self.related_sort(category_id, related_posts_category,related_type='category')
                related_posts += related_posts_category
        #print(related_posts)
        related_posts = await join.post_user(related_posts, self.application.db)
        related_posts = await self.get_posts_desc(related_posts)
        # TODO 用户是否登录等个人数据 可以通过js来实时获取，这样就可以在CDN缓存html页面，当前国内文章页速度响应一般在600ms以内，
        #  因此可先不做
        #self.set_header('cache-control',
        #                'public, stale-while-revalidate=120,stale-if-error=3600,max-age=5,s-maxage=600')
        if language == 'zh-cn':
            post['title'] = await self.cc_async(post['title'])
            post['content'] = await self.cc_async(post['content'])
        post_etree = etree.HTML(post['content'])
        post_desc = ''.join([i.strip() for i in post_etree.xpath(".//text()")])[:200]
        post['desc'] = post_desc
        #处理author.user_name为空的情况
        if not author.user_name:
            author.user_name = 'None'
        self.render('page/article.html', menu_left=menu_left, post=post, config=config,hot_posts=hot_posts,related_posts=related_posts,
                        u_new_posts=u_new_posts,u_categorys=u_categorys,author=author)

class ApiCommentsGetAllHandler(RequestHandler):
    async def post(self):
        post_id = self.get_argument('post_id')
        comments = await self.application.db.comments.find({"post_id":post_id}).to_list(length=None)
        self.write(dumps(comments))

class ApiCommentsAddHandler(UserHander):
    @authenticated_async
    async def post(self):
        post_id = self.get_argument('post_id')
        reply_to = self.get_argument('reply_to')
        comment_content = self.get_argument('comment_content')
        comment_author = await self.get_uid_name()
        comment_author_id = comment_author['_id']
        comment_author_name =  comment_author['user_name']
        comment_date = datetime.datetime.now()
        comment_id = await self.application.db.comments.insert_one(
            {"post_id": post_id, "reply_to": reply_to, "comment_author_id": comment_author_id, "comment_author_name": comment_author_name, "comment_date": comment_date
             })
        comment_id_str = str(comment_id)
        self.write(comment_id_str)

