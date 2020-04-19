from views.base import BaseHandler,DBMixin
import tornado
class ArticleHandler(BaseHandler,DBMixin):
    async def get(self, y, m, d, post_title):
        post_title = tornado.escape.url_escape(post_title).lower()
        async with self.application.db.acquire() as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT * from wp_posts where post_name=%s",(post_title))
            # print(cur.description)
            s = await cur.fetchone()
        print(s)
        print( y, m, d, post_title)