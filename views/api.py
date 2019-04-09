from views.index import *
from bson.json_util import dumps
from utils.tools import post_time_format
from .base import UserHander

class ApiListHandler(RequestHandler):
    async def get(self):
        path = self.get_argument('path')
        postoffset = self.get_argument('postoffset')
        if path == 'index':
            posts =  await self.application.db.posts.find({"_id":{"$lt":ObjectId(postoffset)},"type":0}).sort([("post_date",-1)]).limit(articles_per_page).to_list(length=articles_per_page)
            posts = await join.post_user(posts,self.application.db)
            self.render('component/list-page/content-list.html',posts=posts)
            #self.write('')
        if path=='category':
            c_id = self.get_argument('id')
            posts = await self.application.db.posts.find({"_id":{"$lt":ObjectId(postoffset)},"type":0,"category": ObjectId(c_id)}).sort([("post_date", -1)]).limit(articles_per_page).to_list(length=articles_per_page)
            posts = await join.post_user(posts,self.application.db)
            self.render('component/list-page/content-list.html', posts=posts)
        if path=="tag":
            t_id = self.get_argument('id')
            posts = await self.application.db.posts.find({"_id":{"$lt":ObjectId(postoffset)},"type":0,"tags": ObjectId(t_id)}).sort([("post_date", -1)]).limit(articles_per_page).to_list(length=articles_per_page)
            posts = await join.post_user(posts,self.application.db)
            self.render('component/list-page/content-list.html', posts=posts)
        if path=="recommend":
            posts = await self.application.db.posts.find({"_id":{"$lt":ObjectId(postoffset)},"type":0,"is_real_user": 1}).sort([("post_date", -1)]).limit(articles_per_page).to_list(length=articles_per_page)
            posts = await join.post_user(posts,self.application.db)
            self.render('component/list-page/content-list.html', posts=posts)

class ApiCommentsGetAllHandler(RequestHandler):
    def check_xsrf_cookie(self):
        if 'Googlebot' not in self.request.headers["User-Agent"]:
            RequestHandler.check_xsrf_cookie(self)
    async def post(self):
        post_id = self.get_argument('post_id')
        comments = await self.application.db.comments.find({"post_id":post_id}).to_list(length=None)
        self.write(dumps(comments))

class ApiAuthorHandler(UserHander):
    async def get(self):
        page = self.get_argument('page')
        author_id = self.get_argument('author')
        posts = await self.application.db.posts.find({"user": ObjectId(author_id), "type": 0}).sort(
            [("post_date", -1)]).skip(
            config.articles_per_page * (int(page) - 1)).limit(config.articles_per_page).to_list(
            length=config.articles_per_page)
        posts = await self.get_posts_desc(posts)
        posts = map(post_time_format, posts)
        data={}
        data['page'] = page
        self.render('component/author/author_list.html',posts=posts,data=data)

