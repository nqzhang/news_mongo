from views.base import BaseHandler,DBMixin
import tornado
import aiomysql

class ArticleHandler(BaseHandler,DBMixin):
    async def get(self, y, m, d, post_title):
        post_title = tornado.escape.url_escape(post_title).lower()
        async with self.application.db.acquire() as conn:
            cur = await conn.cursor(aiomysql.DictCursor)
            await cur.execute("SELECT * from wp_posts where post_name=%s",(post_title))
            # print(cur.description)
            s = await cur.fetchone()
        #print( y, m, d, post_title)
        data=s
        data["canonical"] = self.request.full_url().rstrip('amp/') + "/"
        #print(data["canonical"])
        data["content"] = data["post_content"]
        data = await self.get_post_desc(data)
        data = await self.get_thumb_image([data])
        data = data[0]
        data = await self.amp_process(data)
        data["post_title"] = s["post_title"]
        data["site_name"] = self.site_name
        self.render("article_amp.html",data=data)