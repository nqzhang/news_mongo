from views.base import BlockingHandler,DBMixin
import tornado.escape
import aiomysql
import timeago,datetime
from urllib.parse import urljoin

from .base import WpBaseHandler
import json

class SitemapHandler(BlockingHandler,DBMixin):
    def reverse_full_url(self, name, *args, **kwargs):
        host_url = "{protocol}://{host}".format(**vars(self.request))
        return urljoin(host_url, self.reverse_url(name, *args, **kwargs))
    async def get(self):
        type = self.get_argument("type",None)
        if type=="sitemap":
            start_id = int(self.get_argument("start_id",None))
            async with self.db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    posts_sql = "select post_name,post_date from wp_posts where id >= {} and id < {} and post_status='publish' and post_type='post'".format(start_id,start_id+50000)
                    #print(posts_sql)
                    await cur.execute('SET SESSION MAX_STATEMENT_TIME=300;')
                    await cur.execute(posts_sql)
                    posts = await cur.fetchall()
            self.data={}
            await self.generate_post_link(posts)
            self.set_header('Content-Type', 'text/xml')
            self.set_header('cache-control',
                            'public, stale-while-revalidate=120,stale-if-error=3600,max-age=300,s-maxage=300')
            self.render('sitemap.xml', posts=posts)
        elif type=="index":
            async with self.db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute("select max(ID) from wp_posts")
                    end_id = (await  cur.fetchone())['max(ID)']
                    await cur.execute("select min(ID) from wp_posts")
                    start_id = (await  cur.fetchone())['min(ID)']
            with open("views/wp/sitemap_lastmod_cache", "r+") as f:
                lastmod_cache = json.load(f)
            executed_sql = 0
            print(end_id)
            async with self.db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                        await cur.execute('SET SESSION MAX_STATEMENT_TIME=300;')
                        while start_id < end_id-50000:
                            start_id += 50000
                            last_mod = lastmod_cache.get(str(start_id),None)
                            if not last_mod:
                                executed_sql += 1
                                print("execute start_id sql",start_id)
                                await cur.execute("select max(ID) from wp_posts where ID >= {} and ID < {} and post_status='publish' and post_type='post'".format(start_id,start_id+50000))
                                post_id = (await cur.fetchone())['max(ID)']
                                print(post_id)
                                await cur.execute("select post_date from wp_posts where ID ={}".format(post_id))
                                lastmod_cache[start_id] = (await cur.fetchone())['post_date'].isoformat()
                                if executed_sql > 10:
                                    with open("views/wp/sitemap_lastmod_cache", "r+") as f:
                                        json.dump(lastmod_cache, f, default=str)
                                    executed_sql = 0
            #print(lastmod_cache)


            self.set_header('Content-Type', 'text/xml')
            self.set_header('cache-control',
                            'public, stale-while-revalidate=120,stale-if-error=3600,max-age=300,s-maxage=300')
            self.render('sitemap_index.xml',lastmod_cache=lastmod_cache)