import tornado
from tornado.web import authenticated
from bson import ObjectId
import config
from models import join,sidebar
from .base import BaseHandler,DBMixin
from utils.base import attrDict
from views.base import UserHander
import datetime
from utils.tools import *
from .account import EmailHandler
from email.header import Header
from utils.hot import hot
from elasticsearch_dsl import Search


comment_notify_text = '''
            有人在{}回复了您<br/>
            請點擊<a href="{}">鏈接</a>查看'''

class ArticleHandler(BaseHandler,DBMixin):
    async def get_post_category_info(self,post):
        if post.get('category',None):
            category_id = [i for i in post.get('category')  if i]
            category = []
            for c_id in post['category']:
                c = await self.application.db.terms.find_one({"_id":ObjectId(c_id)})
                category.append(c)
            post['category'] = category

        else:
            post['category'] = None
            category_id = None
        return post, category_id
    async def get_posts_category_info(self, posts):
        for post in posts:
            post = await self.get_post_category_info(post)
        return posts
    async def get(self, post_id,language='zh-tw'):
        post = await self.application.db.posts.find_one({"_id":ObjectId(post_id)})
        prev_post=  await self.application.db.posts.find({"_id": {"$lt":ObjectId(post_id)}}).sort([("_id", -1)]).limit(1).to_list(length=None)
        next_post = await self.application.db.posts.find({"_id": {"$gt": ObjectId(post_id)}}).sort([("_id", 1)]).limit(1).to_list(length=None)
        post['prev_post'] = prev_post[0] if prev_post else None
        post['next_post'] = next_post[0] if next_post else None
        #cursor = await db.posts.find({"type": 0, "is_recommend": {"$ne": False}}, {"_id": 1}).sort(
        #    [("score", -1)]).limit(10000).to_list(length=None)
        u_id = post['user']
        u = await self.application.db.users.find_one({"_id":ObjectId(u_id)})
        author = attrDict(u)
        post['user'] = u
        tags_id = [i for i in post['tags'] if i]
        post,category_id = await self.get_post_category_info(post)
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
        menus = await self.application.db.menu.find({"type": "left"}).to_list(length=10)
        hot_posts = await sidebar.hot_posts(self)
        u_new_posts = await sidebar.u_new_posts(self,u_id)
        u_categorys =  await sidebar.u_categorys(self,u_id)
        #related_posts =  await self.application.db.posts.find({'tags': {'$in': tags_id},'_id': {'$ne': post['_id']}}).sort([("views",-1)])\
            #.limit(articles_per_page).to_list(length=articles_per_page)
        if self.es:
            s = Search(index=self.db_name) \
                .query("match", title=post['title'])
            s = s.exclude('term', post_id=str(post_id))
            response = await self.es.search(s[0:8].to_dict())
            related_posts_id = [ObjectId(i['_source']['post_id']) for i in response['hits']['hits']]
            related_posts = await self.application.db.posts.find({'_id': {'$in': related_posts_id}}).to_list(
                length=None)
            index_map = {v: i for i, v in enumerate(related_posts_id)}
            related_posts = sorted(related_posts, key=lambda related_post: index_map[related_post['_id']])
        else:
            if tags_id:
                related_posts =  await self.application.db.posts.find({'tags': {'$in': tags_id},'_id': {'$ne': post['_id']}}).sort([("post_date",-1)]) \
                    .limit(8).to_list(length=8)
                related_posts = await related_sort(tags_id,related_posts,related_type='tags')
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
            related_fill_num = 8 - len(related_posts)
            if related_fill_num > 0:
                if category_id:
                    #TODO 先根据日期排序 通过mongodb aggregate 实现速度太慢 以后可以采用elasticsearch 或者google custom search？
                    related_posts_category = await self.application.db.posts.find({'category': {'$in': category_id},'_id': {'$ne': post['_id']}}).sort([("post_date",-1)]) \
                    .limit(related_fill_num).to_list(length=related_fill_num)
                    related_posts_category = await related_sort(category_id, related_posts_category,related_type='category')
                    related_posts += related_posts_category
        related_posts = await join.post_user(related_posts, self.application.db)
        related_posts = await self.get_posts_desc(related_posts)
        related_posts = await self.get_thumb_image(related_posts)
        related_posts = await self.get_posts_category_info(related_posts)
        #print(related_posts)
        # TODO 用户是否登录等个人数据 可以通过js来实时获取，这样就可以在CDN缓存html页面，当前国内文章页速度响应一般在600ms以内，
        #  因此可先不做
        #self.set_header('cache-control',
        #                'public, stale-while-revalidate=120,stale-if-error=3600,max-age=5,s-maxage=600')
        if language == 'zh-cn':
            post['title'] = await self.cc_async(post['title'])
            post['content'] = await self.cc_async(post['content'])
        #post_etree = etree.HTML(post['content'])
        #post_desc = ''.join([i.strip() for i in post_etree.xpath(".//text()")])[:200]
        #post['desc'] = post_desc
        post = await self.get_post_desc(post)
        posts = await self.get_thumb_image([post])
        post=posts[0]
        post = await self.article_img_add_class(post)
    #处理author.user_name为空的情况
        if not author.user_name:
            author.user_name = 'None'
        data={}
        data['author'] = author
        #当前用户是否关注了该文章
        if await self.is_login():
            liked = await self.application.db.like.find({"type":"article_like","user_id":str(self.user['_id']),"post_id":post_id}).to_list(length=None)
            data['liked'] = liked
        else:
            data['liked'] = False
        #print(post)
        data['new_comment_posts'] = await sidebar.new_comment_posts(self)
        self.render('page/article.html', menus=menus, post=post, config=config,hot_posts=hot_posts,related_posts=related_posts,
                        u_new_posts=u_new_posts,u_categorys=u_categorys,author=author,data=data)
        post_score = await hot(self.application.db,post_id)

class ApiCommentsAddHandler(UserHander,EmailHandler,DBMixin):
    @authenticated
    async def post(self):
        post_id = self.get_argument('post_id')
        reply_to = self.get_argument('reply_to')
        comment_content = self.get_argument('comment_content')
        comment_author = await self.get_uid_name()
        comment_author_id = comment_author['_id']
        comment_author_name =  comment_author['user_name']
        comment_date = datetime.datetime.now()
        comment = {}
        if reply_to:
            comment['reply_to'] = reply_to
        comment['post_id'] = post_id
        comment['comment_author_id'] = comment_author_id
        comment['comment_author_name'] = comment_author_name
        comment['comment_date'] =  comment_date
        comment['comment_content'] = comment_content
        comment_id = await self.application.db.comments.insert_one(comment)
        comment_id_str = str(comment_id.inserted_id)
        #print(post_id)
        self.write(comment_id_str)
        post_score = await hot(self.application.db,str(post_id))
        if reply_to:
            self.comment = comment
            self.comment_id = comment_id_str
    def on_finish(self):
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.add_callback(self.sending_notify)


    async def sending_notify(self):
            if hasattr(self,"comment"):
                #print(self.comment['reply_to'])
                reply_to_comment = await self.application.db.comments.find_one({"_id":ObjectId(self.comment['reply_to'])})
                print(reply_to_comment)
                reply_post = await self.application.db.posts.find_one({"_id":ObjectId(reply_to_comment['post_id'])})
                if reply_post['type'] == 0:
                    print(self.comment_id)
                    post_link = '{}/a/{}?commentScrool={}'.format(config.site_domain,str(reply_post['_id']),self.comment_id)
                print(post_link)
                reply_to_user_id = reply_to_comment['comment_author_id']
                reply_to_user = await self.application.db.users.find_one({"_id":ObjectId(reply_to_user_id)})
                email = reply_to_user['email']
                subject = Header('[{}]評論回復'.format(self.site_name), 'utf-8')
                email_text = comment_notify_text.format(self.site_name, post_link)
                await self.send_mail(reply_to_user['email'],subject,email_text)
                print(reply_to_user)
                #else:
                    #print('数据库已存在此图片')

