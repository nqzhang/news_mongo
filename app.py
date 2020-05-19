import tornado
import tornado.web
from views import index, recommend, backend, article, category, tag, static, account, user, author, api, question
import views.wp as views_wp
import views.search as views_search
import config
import aioredis
from views import redirect
# client = motor_tornado.MotorClient('mongodb://192.168.1.103:27017')
# db = client.test
from opencc import OpenCC


# from lxml.html.clean import Cleaner

class Application(tornado.web.Application):
    def __init__(self, dbs):
        # tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
        handlers = [
            (r'/?', index.IndexPageHandler),
            (r'/newest', index.IndexPageHandler),
            (r'/page/(\d*)/?', index.IndexPageHandler),
            (r'/a/(.*?)/?', article.ArticleHandler),
            (r'/q/(.*?)/?', question.QuestionHandler),
            (r'/c/(.*?)/page/(\d*)/?', category.CategoryPageHandler),
            (r'/c/(?P<c_id>.*?)/(?P<page>\d*)/?', category.CategoryPageHandler),
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
            # (r'/api/comments/add/', article.ApiCommentsAddHandler),
            (r'/mp/postedit/?', user.PostEditHandler),
            (r'/mp/postedit/(.*)/?', user.PostEditHandler),
            (r'/mp/postajax/.*?', user.PostAjaxHandler),
            (r'/mp/postlist/.*?', user.PostListHandler),
            (r'/mp/postdelete/.*?', user.PostDeleteHandler),
            (r'/mp/ckupload/.*?', user.ckuploadHandeler),
            (r"/sitemap/(.*)", static.SitemapStaticFileHandler, {"path": "./sitemap"},),
            # TODO 管理页面
            # (r"/admin/", admin.AdminHandler ),
            (r'/ads.txt()', tornado.web.StaticFileHandler, {"path": "./ads.txt"},),
        ]

        self.dbs = dbs
        self.cc = OpenCC('t2s')
        self.cc_s2t = OpenCC('s2t')
        # self.cleaner = Cleaner(page_structure=True, links=True, javascript=True, style=True, comments=True,
        #                       inline_style=True)
        # self.cleaner.remove_tags = ['a', 'font']
        super(Application, self).__init__(handlers, **config.settings)

        for k, v in dbs['by_domain'].items():
            if v.get('index_page', None) == "recommend":
                self.add_handlers(k, [
                    (r"/?", recommend.recommendPageHandler),
                ])
            views_theme = v.get("views_theme", None)
            if views_theme == "wp":
                self.add_handlers(k, [
                    (r"/amp/(?P<post_id>.*?)/(?P<language>.*?)/?", views_wp.article.AmpArticleHandler),
                    (r"/(?P<y>[0-9]{4})/(?P<m>[0-9]{2})/(?P<d>[0-9]{2})/(?P<post_name>.*?)/(?P<language>.*?)/?",
                     views_wp.article.ArticleHandler),
                    (r"/category/(?P<category>.*?)/(?P<page>\d*)/?(?P<language>zh-hk|zh-cn|zh-tw)?/?",
                     views_wp.category.CategoryHandler),
                    (r"/author/(?P<user_nicename>.*?)/(?P<page>\d*)/?(?P<language>zh-hk|zh-cn|zh-tw)?/?",
                     views_wp.author.AuthorHandler),
                    tornado.web.url(r"/sitemap/plauvzepsddkiuvd.xml", views_wp.sitemap.SitemapHandler,
                                    name="sitemap_wp")
                ])
            print(views_theme)
            if views_theme == "redirect":
                self.add_handlers(k, [
                    (r"/amp/(?P<post_id>.*?)/(?P<language>.*?)/?", redirect.AmpArticleHandler),
                    (r"/(?P<y>[0-9]{4})/(?P<m>[0-9]{2})/(?P<d>[0-9]{2})/(?P<post_name>.*?)/(?P<language>.*?)/?",
                     redirect.ArticleHandler),
                    (r"/category/(?P<category>.*?)/(?P<page>\d*)/?(?P<language>zh-hk|zh-cn|zh-tw)?/?",
                     views_wp.category.CategoryHandler),
                    (r"/author/(?P<user_nicename>.*?)/(?P<page>\d*)/?(?P<language>zh-hk|zh-cn|zh-tw)?/?",
                     views_wp.author.AuthorHandler),
                    tornado.web.url(r"/sitemap/plauvzepsddkiuvd.xml", views_wp.sitemap.SitemapHandler,
                                    name="sitemap_wp")
                ])
            if views_theme == "search":
                self.add_handlers(k, [
                    (r"/?", views_search.index.IndexHandler),
                    (r"^/search", views_search.index.SearchHandler)
                ])

    def init_with_loop(self, loop):
        self.redis = loop.run_until_complete(
            aioredis.create_redis_pool((config.redis['host'], config.redis['port']), maxsize=20, loop=loop))
