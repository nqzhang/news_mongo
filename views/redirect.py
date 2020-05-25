import tornado.web
import aiomysql
from .base import BaseHandler,DBMixin
import tornado.escape

class AmpArticleHandler(BaseHandler,DBMixin):
    async def get(self, post_id,language=None):
        #print(post_id)
        if self.site_id == "5":
            m_db = self.application.dbs['by_site_id']['3'].get('db_conn', None)
        elif self.site_id == "6":
            m_db = self.application.dbs['by_site_id']['7'].get('db_conn', None)
        async with m_db.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * from wp_posts where id=%s",(int(post_id)))
                s = await cur.fetchone()
        if s:
            post = await self.db.posts.find_one({"title": s['post_title']})
            if post:
                if language:
                    self.redirect('/a/{}?amp=1?lang={}'.format(str(post['_id']),language), permanent=True)
                else:
                    self.redirect('/a/{}?amp=1'.format(str(post['_id'])), permanent=True)
                return
        self.send_error(404, reason="post not found")

class ArticleHandler(BaseHandler,DBMixin):
    async def get(self, y,m,d,post_name,language=None):
        if self.site_id == "5":
            m_db = self.application.dbs['by_site_id']['3'].get('db_conn',None)
        elif self.site_id == "6":
            m_db = self.application.dbs['by_site_id']['7'].get('db_conn', None)
        async with m_db.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                s= await cur.execute("SELECT * from wp_posts where post_name=%s",(tornado.escape.url_escape(post_name).lower()))
                s = await cur.fetchone()
        if s:

            post = await self.db.posts.find_one({"title": s['post_title']})
            if post:
                if language:
                    self.redirect('/a/{}?lang={}'.format(str(post['_id']),language), permanent=True)
                else:
                    self.redirect('/a/{}'.format(str(post['_id'])), permanent=True)
                return
        self.send_error(404, reason="post not found")
