from views.base import BlockingHandler,DBMixin
import tornado.escape
import aiomysql
import timeago,datetime
from .base import WpBaseHandler
from collections import OrderedDict

class ArticleHandler(WpBaseHandler):
    async def get(self, y,m,d,post_name,language=None):
        lang=language
        #print(tornado.escape.url_escape(post_name).lower())
        async with self.db.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * from wp_posts where post_name=%s",(tornado.escape.url_escape(post_name).lower()))
                s = await cur.fetchone()
                #print(s)
                await cur.execute("SELECT * FROM wp_users WHERE ID = %s LIMIT 1",(s['post_author']))
                author = await cur.fetchone()
                '''
                post_category_sql = 'SELECT r.term_taxonomy_id,t.taxonomy,wt.* FROM wp_posts p INNER JOIN wp_term_relationships r ON r.object_id = p.ID ' \
                'INNER JOIN wp_term_taxonomy t ON t.term_taxonomy_id = r.term_taxonomy_id ' \
                'INNER JOIN wp_terms wt ON wt.term_id = t.term_id WHERE p.ID = %s'
                await cur.execute(post_category_sql,s['ID'])
                post_terms = await cur.fetchall()
                post_categorys = [i for i in post_terms if i['taxonomy']=="category"]
                post_category_ids = [i['term_taxonomy_id'] for i in post_categorys]
                post_category = post_categorys[0]
                post_tags = [i for i in post_terms if i['taxonomy']=="post_tag"]
                related_post_sql = "SELECT object_id  FROM  wp_term_relationships WHERE wp_term_relationships.term_taxonomy_id in({}) " \
                                   "ORDER BY wp_term_relationships.object_id DESC LIMIT {};"
                # related_post_sql = "SELECT wp_posts.* FROM wp_posts  JOIN  wp_term_relationships ON wp_posts.ID = wp_term_relationships.object_id " \
                #                    "WHERE wp_term_relationships.term_taxonomy_id IN ({}) and wp_term_relationships.object_id not in ({}) " \
                #                    "group by wp_term_relationships.object_id ORDER BY wp_term_relationships.object_id DESC LIMIT {}"
                if post_tags:
                    post_tags_id = [x['term_taxonomy_id'] for x in post_tags]
                    await cur.execute(related_post_sql.format(','.join([str(i) for i in post_tags_id]),10))
                    related_posts_t =  (await cur.fetchall())
                    if not related_posts_t:
                        related_posts_t = []
                else:
                    related_posts_t = []
                if post_category_ids and len(related_posts_t) < 10:
                    await cur.execute(related_post_sql.format(','.join([str(i) for i in post_category_ids]),
                                  10))
                    related_posts_c = await cur.fetchall()
                    if not related_posts_c:
                        related_posts_c = []
                else:
                    related_posts_c = []
                related_posts = related_posts_t + related_posts_c
                related_posts_id = [str(x['object_id']) for x in related_posts if x['object_id'] != s['ID']]
                related_posts_id = list(OrderedDict.fromkeys(related_posts_id))
                related_posts_id = related_posts_id[: 10]
                #print("select * from wp_posts where ID in ({})".format(','.join(related_posts_id)))
                await cur.execute("select * from wp_posts where ID in ({}) order by ID desc".format(','.join(related_posts_id)))
                related_posts = await cur.fetchall()
                '''
                related_post_sql = "SELECT wp_posts.post_title,post_date,post_name,post_content FROM wp_posts  where ID !={} order by ID desc limit 15"
                await cur.execute(related_post_sql.format(s['ID']))
                related_posts = await cur.fetchall()
        if s:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            timeago_language_dict = {"zh-tw":"zh_TW","zh-cn":"zh_CN","zh-hk":"zh_TW"}
            timeago_language = timeago_language_dict[self.data['lang']] if self.data['lang'] else "zh_CN"
            for x in related_posts:
                await self.generate_post_link([x])
                x["content"] = x["post_content"]
                x['friendly_time'] = timeago.format(x['post_date'], now, timeago_language)
                await self.get_thumb_image([x])
                if self.data['lang'] in ["zh-tw","zh-hk"]:
                    #x['content'] = await self.cc_async_s2t(x['content'])
                    x['post_title'] = await self.cc_async_s2t(x['post_title'])
            #related_posts = await self.get_posts_desc(related_posts)
            data=s
            # if post_category:
            #      data['post_category'] = post_category
            # else:
            #     data['post_category'] = None
            # if post_tags:
            #     data['post_tags'] = post_tags
            # else:
            #     data['post_tags'] = None

            #print(self.request.host)
            #print("self.domain", self.domain )
            #print("uri",self.request.uri)
            data["amp_url"] = "/amp/{}/".format(data['ID'])
            data["origin_url"] = "/{}/{}/{}/{}/".format(y,m,d,post_name)
            data["cn_url"] =  "{}{}/".format(data["origin_url"],"zh-cn")
            data["tw_url"] = "{}{}/".format(data["origin_url"], "zh-tw")
            data["hk_url"] = "{}{}/".format(data["origin_url"], "zh-hk")
            if lang:
                data["amp_url"] = data["amp_url"] + lang + '/'
            data['lang'] = lang
            #print(data["canonical"])
            data["content"] = data["post_content"]
            data = await self.get_thumb_image([data])
            data = data[0]
            data = await self.article_img_add_class(data)
            data["site_name"] =self.site_name
            html_lang = "zh-Hans"
            if lang == "zh-tw" or lang == "zh-hk":
                html_lang = "zh-Hant"
                data["site_name"] = await self.cc_async_s2t(data["site_name"])
                data['content'] = await self.cc_async_s2t(data['content'])
                data['post_title'] = await self.cc_async_s2t(data['post_title'])
                #data['desc'] = await self.cc_async_s2t(data['desc'])
                    #x['desc'] = await self.cc_async_s2t(x['desc'])
                #print(data['post_thumb'])
            data = await self.get_post_desc(data)
            data['related_posts'] = related_posts
            data['html_lang'] = html_lang
            data['author'] = author
            data['author']['author_link'] = await self.generate_author_link_by_author(author)
            self.data.update(data)
            self.render("article.html")
        else:
            self.send_error(404,reason="post not found")

class AmpArticleHandler(WpBaseHandler):
    async def get(self, post_id,language):
        #post_title = tornado.escape.url_escape(post_title).lower()
        async with self.db.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * from wp_posts where id=%s",(int(post_id)))
                # print(cur.description)
                s = await cur.fetchone()
                #print(s)
        #print( y, m, d, post_title,language)
        if s:
            data=s
            #print(self.request.host)
            #print("self.domain", self.domain )
            #print("uri",self.request.uri)
            data["canonical"] = "//" + self.request.host + data['post_date'].strftime("/%Y/%m/%d/") + data[
                'post_name'] + '/'
            if language:
                data["canonical"] = data["canonical"] + language + '/'
            #data["canonical"] =  "/" + self.request.uri().rstrip('amp/') + "/"
            #print(data["canonical"])
            data["content"] = data["post_content"]
            data = await self.get_post_desc(data)
            data = await self.get_thumb_image([data])
            data = data[0]
            data = await self.amp_process(data)
            data["site_name"] =self.site_name
            html_lang = "zh-Hans"
            if language == "zh-tw" or language == "zh-hk":
                html_lang = "zh-Hant"
                data["site_name"] = await self.cc_async_s2t(data["site_name"])
                data['content'] = await self.cc_async_s2t(data['content'])
                data['post_title'] = await self.cc_async_s2t(data['post_title'])
                data['desc'] = await self.cc_async_s2t(data['desc'])
                #print(data['post_thumb'])
            data['html_lang'] = html_lang
            self.render("article_amp.html",data=data)
        else:
            self.send_error(404,reason="post not found")