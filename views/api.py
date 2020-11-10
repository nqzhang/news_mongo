from views.index import *
from bson.json_util import dumps
from utils.tools import post_time_format
from .base import UserHander,DBMixin
from tornado.web import authenticated
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MoreLikeThis
import json
from models import join
import tornado.web

class ApiListHandler(DBMixin):
    async def get(self):
        path = self.get_argument('path')
        postoffset = self.get_argument('postoffset')
        if path == 'index':
            list_path = 'index'
            posts =  await self.db.posts.find({"_id":{"$lt":ObjectId(postoffset)},"type":0}).sort([("post_date",-1)]).limit(self.articles_per_page).to_list(length=self.articles_per_page)
            posts = await join.post_user(posts,self.db)
            self.render('component/list-page/content-list.html',posts=posts,list_path=list_path)
            #self.write('')
        if path=='category':
            c_id = self.get_argument('id')
            list_path = 'category&id={}'.format(c_id)
            posts = await self.db.posts.find({"_id":{"$lt":ObjectId(postoffset)},"type":0,"category": ObjectId(c_id)}).sort([("post_date", -1)]).limit(self.articles_per_page).to_list(length=self.articles_per_page)
            posts = await join.post_user(posts,self.db)
            self.render('component/list-page/content-list.html', posts=posts,list_path=list_path)
        if path=="tag":
            t_id = self.get_argument('id')
            list_path = 'tag&id={}'.format(t_id)
            posts = await self.db.posts.find({"_id":{"$lt":ObjectId(postoffset)},"type":0,"tags": ObjectId(t_id)}).sort([("post_date", -1)]).limit(self.articles_per_page).to_list(length=self.articles_per_page)
            posts = await join.post_user(posts,self.db)
            self.render('component/list-page/content-list.html', posts=posts,list_path=list_path)
        if path=="recommend":
            list_path = 'recommend'
            posts = await self.db.posts.find({"score":{"$lt": float(postoffset)},"type":0}).sort([("score", -1)]).limit(self.articles_per_page).to_list(length=self.articles_per_page)

            posts = await join.post_user(posts,self.db)
            self.render('component/list-page/content-list.html', posts=posts,list_path=list_path)

class ApiCommentsGetAllHandler(UserHander,DBMixin):
    def check_xsrf_cookie(self):
        if 'Googlebot' not in self.request.headers["User-Agent"]:
            RequestHandler.check_xsrf_cookie(self)
    async def post(self):
        post_id = self.get_argument('post_id')
        comments_data={}
        if self.current_user:
            article_user_comment_vote = await self.db.like.find({"type":"comment_like","user_id":self.current_user.decode(),"post_id":post_id},{"comment_id":1,"_id":0,"value":1}).to_list(length=None)
            comments_data['article_user_comment_vote'] = article_user_comment_vote
        comments_data['comments'] = await self.db.comments.find({"post_id":post_id}).to_list(length=None)
        self.write(dumps(comments_data))

class ApiAuthorHandler(UserHander,DBMixin):
    async def get(self):
        page = self.get_argument('page')
        author_id = self.get_argument('author')
        posts = await self.db.posts.find({"user": ObjectId(author_id), "type": 0}).sort(
            [("post_date", -1)]).skip(
            self.articles_per_page * (int(page) - 1)).limit(self.articles_per_page).to_list(
            length=self.articles_per_page)
        posts = await self.get_posts_desc(posts)
        posts = map(post_time_format, posts)
        data={}
        data['page'] = page
        self.render('component/author/author_list.html',posts=posts,data=data)

class ApiArticleHandler(UserHander,DBMixin):
    @authenticated
    async def post(self):
        #print(self.request.body.decode('utf-8'))
        user_id = self.get_argument('user_id')
        post_id = self.get_argument('post_id')
        action = self.get_argument('action')
        if action == 'article_like':
            x = await self.db.like.find_one_and_update({"type":"article_like","user_id":user_id,"post_id":post_id},{"$set":{"value":1}},upsert=True)
            if x:
                if x.get('value',None) == 0:
                        await self.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_unlike":-1}})
                if x.get('value',None) != 1:
                    await self.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_like":1}})
            else:
                await self.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_like":1}})
        elif action == 'article_unlike':
            x = await self.db.like.find_one_and_update({"type":"article_like","user_id":user_id,"post_id":post_id},{"$set":{"value":0}},upsert=True)
            if x:
                if x.get('value',None) == 1:
                    await self.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_like":-1}})
                if x.get('value',None) != 0:
                    await self.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_unlike":1}})
            else:
                await self.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_unlike":1}})
        elif action == 'undo_article_like':
            await self.db.like.delete_one({"type":"article_like","user_id":user_id,"post_id":post_id})
            await self.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_like":-1}})
        elif action == 'undo_article_unlike':
            await self.db.like.delete_one({"type":"article_like","user_id":user_id,"post_id":post_id})
            await self.db.posts.update_one({"_id":ObjectId(post_id)},{"$inc":{"like.article_unlike":-1}})
        if action == 'comment_like':
            comment_id = self.get_argument('comment_id')
            x= await self.db.like.find_one_and_update({"type":"comment_like","user_id":user_id,"post_id":post_id,"comment_id":comment_id},{"$set":{"value":1}},upsert=True)
            if x:
                if x.get('value',None) == 0:
                    await self.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_unlike":-1}})
                if x.get('value',None) != 1:
                    await self.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_like":1}})
            else:
                await self.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_like":1}})
        elif action == 'comment_unlike':
            comment_id = self.get_argument('comment_id')
            x= await self.db.like.find_one_and_update({"type":"comment_like","user_id":user_id,"post_id":post_id,"comment_id":comment_id},{"$set":{"value":0}},upsert=True)
            if x:
                if x.get('value',None) == 1:
                    await self.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_like":-1}})
                if x.get('value',None) != 0:
                    await self.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_unlike":1}})
            else:
                await self.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_unlike":1}})

        elif action == 'undo_comment_like':
            comment_id = self.get_argument('comment_id')
            await self.db.like.delete_one({"type":"comment_like","user_id":user_id,"post_id":post_id,"comment_id":comment_id})
            await self.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_like":-1}})
        elif action == 'undo_comment_unlike':
            comment_id = self.get_argument('comment_id')
            await self.db.like.delete_one({"type":"comment_like","user_id":user_id,"post_id":post_id,"comment_id":comment_id})
            await self.db.comments.update_one({"_id":ObjectId(comment_id)},{"$inc":{"like.comment_unlike":-1}})
        """
        if action == 'get_article_user_comment_vote':
            x = await self.db.like.find({"type":"comment_like","user_id":user_id,"post_id":post_id},{"comment_id":1,"_id":0,"value":1}).to_list(length=None)
            print(dumps(x))
            self.finish(dumps(x))
        """

class ApiRelatedEsHandler(UserHander,DBMixin):
    async def get(self):
        if 'Googlebot' in self.request.headers["User-Agent"]:
            raise tornado.web.HTTPError(404,"Shit! Don't crawl me anymore.")
            return
        post_id = self.get_argument('post_id')
        category_info = self.get_argument('category_info','0')
        if self.es:
            post = await self.db.posts.find_one({"_id": ObjectId(post_id)})
            s = Search(index=self.es_index)
            s = s.filter("term", site_id=self.site_id)
            # s = s.query("match", title={"query": post['title']})
            # s = s.query("match", title= {"query": post['title'],"analyzer":"hanlp"})
            s = s.query(MoreLikeThis(like=post['title'], fields=['title'], min_term_freq=1,min_word_length=1,
                                     max_query_terms=12,minimum_should_match="40%"))
            # s = s.query(MoreLikeThis(like=post['title'], fields=['title']))
            s = s.exclude('term', post_id=str(post_id))
            #print(json.dumps(s[0:8].to_dict()))
            response = await self.es.search(s[0:self.articles_per_page].to_dict())
            related_posts_id = [ObjectId(i['_source']['post_id']) for i in response['hits']['hits']]
            related_posts = await self.db.posts.find({'_id': {'$in': related_posts_id}},{"_id":1,"title":1,"user":1}).to_list(
                length=None)
            index_map = {v: i for i, v in enumerate(related_posts_id)}
            related_posts = sorted(related_posts, key=lambda related_post: index_map[related_post['_id']])
            related_posts = await join.post_user(related_posts, self.db)
            related_posts = await self.get_posts_desc(related_posts)
            # if category_info == '1':
            #     related_posts = await self.get_posts_category_info(related_posts)
            for x in related_posts:
                await self.generate_post_link([x])
                if self.data['lang'] in ["zh-tw", "zh-hk"]:
                    # x['content'] = await self.cc_async_s2t(x['content'])
                    x['title'] = await self.cc_async_s2t(x['title'])
                elif self.data['lang'] == 'zh-cn':
                    x['title'] = await self.cc_async(x['title'])
            s_related_posts = [{"title":x['title'],"post_link":x['post_link']} for x in related_posts]
            self.write(dumps(s_related_posts))

