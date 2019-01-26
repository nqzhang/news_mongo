from views.index import *
class ApiListHandler(RequestHandler):
    async def get(self):
        path = self.get_argument('path')
        postoffset = self.get_argument('postoffset')
        if path == 'index':
            posts =  await self.application.db.posts.find({"_id":{"$lt":ObjectId(postoffset)}}).sort([("post_date",-1)]).limit(articles_per_page).to_list(length=articles_per_page)
            posts = await join.post_user(posts,self.application.db)
            '''
            need_keys = ['_id','title','post_date']
            posts_new = {}
            i = 0
            for post in posts:
                user_need_keys = ['_id','user_name']
                post_new = {key: post.get(key, 0) for key in need_keys}
                post_new['user'] = {key: str(post['user'].get(key, 0)) for key in user_need_keys}
                post_new['url'] = config.site_domain + '/a/' + str(post_new['_id'])
                post_new['_id'] = str(post.get('_id'))
                posts_new[i] = post_new
                i += 1
            self.write(posts_new)
            '''
            self.render('component/list-page/content-list.html',posts=posts)
            #self.write('')