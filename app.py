import tornado
from views import index,backend,article,category,tag,static,account,user
import config
from tornado.ioloop import IOLoop, PeriodicCallback
import aioredis
#client = motor_tornado.MotorClient('mongodb://192.168.99.12:27017')
#db = client.test

class Application(tornado.web.Application):
    def __init__(self,db):
        #tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
        handlers = [
            (r'/?',index.IndexPageHandler),
            (r'/page/(\d*)/?', index.IndexPageHandler),
            (r'/a/(.*?)/(.*?)/?', article.ArticleHandler),
            (r'/a/(.*?)/?', article.ArticleHandler),
            (r'/c/(.*?)/page/(\d*)/?', category.CategoryPageHandler),
            (r'/c/(.*?)/?', category.CategoryPageHandler),
            (r'/t/(.*?)/page/(\d*)/?', tag.TagPageHandler),
            (r'/t/(.*?)/?', tag.TagPageHandler),
            (r'/backend/newpost', backend.NewPostHandler),
            (r'/views', backend.ViewsHandler),
            (r'/account/login.*?', account.LoginHandler),
            (r'/account/register.*?', account.RegisterHandler),
            (r'/account/is_email_exist/(.*?)', account.IsEmailExistHandler),
            (r'/u/postedit/.*?', user.PostEditHandler),
            (r'/u/postajax/.*?', user.PostAjaxHandler),
            (r"/sitemap/(.*)", static.SitemapStaticFileHandler, {"path": "./sitemap"},),
        ]
        self.db = db
        super(Application, self).__init__(handlers, **config.settings)

    def init_with_loop(self, loop):
       self.redis = loop.run_until_complete(aioredis.create_redis((config.redis['host'], config.redis['port']), loop=loop))






