import tornado
from views import index,backend,article,category,tag,static,account,user,author
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
            (r'/u/(.*?)/(\d*)/?', author.AuthorPageHandler),
            (r'/u/(.*?)/?', author.AuthorPageHandler),
            (r'/backend/newpost', backend.NewPostHandler),
            (r'/views', backend.ViewsHandler),
            (r'/account/login.*?', account.LoginHandler),
            (r'/account/logout.*?', account.LogoutHandler),
            (r'/account/register.*?', account.RegisterHandler),
            (r'/account/is_email_exist/(.*?)', account.IsEmailExistHandler),
            (r'/account/email_verify/.*?', account.EmailVerifyHandler),
            (r'/account/email_resend/.*?', account.EmailResendHandler),
            (r'/account/password_forgot/send_mail/.*?', account.PasswordForgotSendMailHandler),
            (r'/account/password_forgot/.*?', account.PasswordForgotHandler),
            (r'/account/password_reset/.*?', account.PasswordResetHandler),
            (r'/api/account/password_reset/.*?', account.ApiPasswordResetHandler),
            (r'/mp/postedit/?', user.PostEditHandler),
            (r'/mp/postedit/(.*)/?', user.PostEditHandler),
            (r'/mp/postajax/.*?', user.PostAjaxHandler),
            (r'/mp/postlist/.*?', user.PostListHandler),
            (r'/mp/postdelete/.*?', user.PostDeleteHandler),
            (r'/mp/ckupload/.*?', user.ckuploadHandeler),
            (r"/sitemap/(.*)", static.SitemapStaticFileHandler, {"path": "./sitemap"},),
            #TODO 管理页面
            #(r"/admin/", admin.AdminHandler ),
            (r"/ads.txt()", tornado.web.StaticFileHandler, {"path": "./ads.txt"},),
        ]
        self.db = db
        super(Application, self).__init__(handlers, **config.settings)

    def init_with_loop(self, loop):
       self.redis = loop.run_until_complete(aioredis.create_redis_pool((config.redis['host'], config.redis['port']),maxsize=20, loop=loop))




