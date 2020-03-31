from views.index import *
from bson.json_util import dumps
from utils.tools import post_time_format
from .base import UserHander,DBMixin
from tornado.web import authenticated

class ApiListHandler(DBMixin):
    async def get(self):
        path = self.get_argument('path')
        postoffset = self.get_argument('postoffset')
        if path == 'index':
            list_path = 'index'
            posts =  await self.application.db.posts.find({"_id":{"$lt":ObjectId(postoffset)},"type":0}).sort([("post_date",-1)]).limit(articles_per_page).to_list(length=articles_per_page)
            posts = await join.post_user(posts,self.application.db)
            self.render('component/list-page/content-list.html',posts=posts,list_path=list_path)
            #self.write('')
        if path=='category':
            c_id = self.get_argument('id')
            list_path = 'category&id={}'.format(c_id)
            posts = await self.application.db.posts.find({"_id":{"$lt":ObjectId(postoffset)},"type":0,"category": ObjectId(c_id)}).sort([("post_date", -1)]).limit(articles_per_page).to_list(length=articles_per_page)
            posts = await join.post_user(posts,self.application.db)
            self.render('component/list-page/content-list.html', posts=posts,list_path=list_path)
        if path=="tag":
            t_id = self.get_argument('id')
            list_path = 'tag&id={}'.format(t_id)
            posts = await self.application.db.posts.find({"_id":{"$lt":ObjectId(postoffset)},"type":0,"tags": ObjectId(t_id)}).sort([("post_date", -1)]).limit(articles_per_page).to_list(length=articles_per_page)
            posts = await join.post_user(posts,self.application.db)
            self.render('component/list-page/content-list.html', posts=posts,list_path=list_path)
        if path=="recommend":
            list_path = 'recommend'
            posts = await self.application.db.posts.find({"score":{"$lt": float(postoffset)},"type":0}).sort([("score", -1)]).limit(articles_per_page).to_list(length=articles_per_page)

            posts = await join.post_user(posts,self.application.db)
            self.render('component/list-page/content-list.html', posts=posts,list_path=list_path)

class ApiCommentsGetAllHandler(UserHander,DBMixin):
    def check_xsrf_cookie(self):
        if 'Googlebot' not in self.request.headers["User-Agent"]:
            RequestHandler.check_xsrf_cookie(self)
    async def post(self):
        post_id = self.get_argument('post_id')
        comments_data={}
        if self.current_user:
            article_user_comment_vote = await self.application.db.like.find({"type":"comment_like","user_id":self.current_user.decode(),"post_id":post_id},{"comment_id":1,"_id":0,"value":1}).to_list(length=None)
            comments_data['article_user_comment_vote'] = article_user_comment_vote
        comments_data['comments'] = await self.application.db.comments.find({"post_id":post_id}).to_list(length=None)
        self.write(dumps(comments_data))

class ApiAuthorHandler(UserHander,DBMixin):
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

class ApiArticleHandler(UserHander,DBMixin):
    @authenticated
    async def post(self):
        print(self.request.body.decode('utf-8'))
        user_id = self.get_argument('user_id')
        post_id = self.get_argument('post_id')
        action = self.get_argument('action')
        if action == 'article_like':
            x = await self.application.db.like.find_one_and_update({"type":"article_like","user_id":user_id,"post_id":post_id},{"$set":{"value":1}},upsert=True)
            if x:
                if x.get('value',None) == 0:
                        await self.application.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_unlike":-1}})
                if x.get('value',None) != 1:
                    await self.application.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_like":1}})
            else:
                await self.application.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_like":1}})
        elif action == 'article_unlike':
            x = await self.application.db.like.find_one_and_update({"type":"article_like","user_id":user_id,"post_id":post_id},{"$set":{"value":0}},upsert=True)
            if x:
                if x.get('value',None) == 1:
                    await self.application.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_like":-1}})
                if x.get('value',None) != 0:
                    await self.application.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_unlike":1}})
            else:
                await self.application.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_unlike":1}})
        elif action == 'undo_article_like':
            await self.application.db.like.remove({"type":"article_like","user_id":user_id,"post_id":post_id})
            await self.application.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_like":-1}})
        elif action == 'undo_article_unlike':
            await self.application.db.like.remove({"type":"article_like","user_id":user_id,"post_id":post_id})
            await self.application.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_unlike":-1}})
        if action == 'comment_like':
            comment_id = self.get_argument('comment_id')
            x= await self.application.db.like.find_one_and_update({"type":"comment_like","user_id":user_id,"post_id":post_id,"comment_id":comment_id},{"$set":{"value":1}},upsert=True)
            if x:
                if x.get('value',None) == 0:
                    await self.application.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_unlike":-1}})
                if x.get('value',None) != 1:
                    await self.application.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_like":1}})
            else:
                await self.application.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_like":1}})
        elif action == 'comment_unlike':
            comment_id = self.get_argument('comment_id')
            x= await self.application.db.like.find_one_and_update({"type":"comment_like","user_id":user_id,"post_id":post_id,"comment_id":comment_id},{"$set":{"value":0}},upsert=True)
            if x:
                if x.get('value',None) == 1:
                    await self.application.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_like":-1}})
                if x.get('value',None) != 0:
                    await self.application.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_unlike":1}})
            else:
                await self.application.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_unlike":1}})

        elif action == 'undo_comment_like':
            comment_id = self.get_argument('comment_id')
            await self.application.db.like.remove({"type":"comment_like","user_id":user_id,"post_id":post_id,"comment_id":comment_id})
            await self.application.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_like":-1}})
        elif action == 'undo_comment_unlike':
            comment_id = self.get_argument('comment_id')
            await self.application.db.like.remove({"type":"comment_like","user_id":user_id,"post_id":post_id,"comment_id":comment_id})
            await self.application.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_unlike":-1}})
        """
        if action == 'get_article_user_comment_vote':
            x = await self.application.db.like.find({"type":"comment_like","user_id":user_id,"post_id":post_id},{"comment_id":1,"_id":0,"value":1}).to_list(length=None)
            print(dumps(x))
            self.finish(dumps(x))
        """


