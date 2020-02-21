import tornado
from views import index,recommend,backend,article,category,tag,static,account,user,author,api,question
import config
from tornado.ioloop import IOLoop, PeriodicCallback
import aioredis
#client = motor_tornado.MotorClient('mongodb://192.168.1.103:27017')
#db = client.test

class Application(tornado.web.Application):
    def __init__(self,db):
        #tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
        handlers = [
            (r'/?',recommend.recommendPageHandler),
            (r'/newest', index.IndexPageHandler),
            (r'/page/(\d*)/?', index.IndexPageHandler),
            (r'/a/(.*?)/(.*?)/?', article.ArticleHandler),
            (r'/a/(.*?)/?', article.ArticleHandler),
            (r'/q/(.*?)/?', question.QuestionHandler),
            (r'/c/(.*?)/page/(\d*)/?', category.CategoryPageHandler),
            (r'/c/(.*?)/?', category.CategoryPageHandler),
            (r'/t/(.*?)/page/(\d*)/?', tag.TagPageHandler),
            (r'/t/(.*?)/?', tag.TagPageHandler),
            (r'/u/(?P<u_id>.*?)/c/(?P<u_c_id>.*?)/(?P<page>\d*)/?', author.AuthorPageHandler),
            (r'/u/(?P<u_id>.*?)/c/(?P<u_c_id>.*?)/?', author.AuthorPageHandler),
            (r'/u/(?P<u_id>.*?)/(?P<page>\d*)/?', author.AuthorPageHandler),
            (r'/u/(?P<u_id>.*?)/?', author.AuthorPageHandler),
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
            (r'/api/article', api.ApiArticleHandler),
            (r'/api/comments/get_all/', api.ApiCommentsGetAllHandler),
            (r'/api/comments/add/', article.ApiCommentsAddHandler),
            (r'/api/list/.*', api.ApiListHandler),
            (r'/api/author/.*', api.ApiAuthorHandler),
            #(r'/api/comments/add/', article.ApiCommentsAddHandler),
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




