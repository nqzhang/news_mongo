from views.base import BaseHandler,DBMixin
import tornado.escape
import aiomysql
import timeago,datetime
from .base import WpBaseHandler
import json

class CategoryHandler(WpBaseHandler):
    async def get(self,category,page=1,language=None):
        if not page:
            page = 1
        slug = tornado.escape.url_escape(category.split('/')[-1]).lower()
        category_sql = "SELECT t.*, tt.* FROM wp_terms AS t INNER JOIN wp_term_taxonomy AS tt " \
                       "ON t.term_id = tt.term_id WHERE tt.taxonomy IN ('category') AND t.slug = '{}'".format(slug)
        print(category_sql)
        sub_category_sql = "with recursive cte (term_id, parent) as (select term_id, parent from wp_term_taxonomy where parent = {} " \
                           "union all select p.term_id, p.parent from wp_term_taxonomy p inner join cte on p.parent = cte.term_id) select * from cte;"
        category_post_id_sql= "SELECT  wp_posts.* FROM wp_posts  left jOIN wp_term_relationships ON (wp_posts.ID = wp_term_relationships.object_id) " \
                              "where  wp_term_relationships.term_taxonomy_id IN ({}) AND wp_posts.post_type = 'post' AND " \
                              "wp_posts.post_status = 'publish' ORDER BY wp_posts.ID DESC LIMIT {}, 15;"
        async with self.db.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(category_sql)
                category = await  cur.fetchone()
        if category:
            async with self.db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(sub_category_sql.format(category['term_id']))
                    sub_category = await cur.fetchall()
            sub_category_id = [x['term_id'] for x in sub_category]
            sub_category_id.insert(0,category['term_id'])
            async with self.db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    print('xxxxxxx',category_post_id_sql.format(','.join([str(x) for x in sub_category_id]),(int(page) -1) * 15))
                    await cur.execute(category_post_id_sql.format(','.join([str(x) for x in sub_category_id]),(int(page) -1) * 15))
                    category_post = await cur.fetchall()
            print(sub_category_id)
            authors = [str(post['post_author']) for post in category_post]
            author_dict = {}
            async with self.db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute("SELECT * FROM wp_users WHERE ID in ({})".format(','.join(authors)))
                    authors = await cur.fetchall()
            for author in authors:
                author_dict[author['ID']] = author
            print(author_dict)

            data={}
            data['category'] = category
            data["origin_url"] = "/category/{}/".format(self.path_kwargs['category'])
            if self.path_kwargs['page']:
                data["origin_url"] = "{}{}/".format(data["origin_url"],self.path_kwargs['page'])
            # if self.path_kwargs['language']:
            #     data["origin_url"] = "{}{}/".format(data["origin_url"],self.path_kwargs['language'])
            print(data["origin_url"])
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            timeago_language_dict = {"zh-tw": "zh_TW", "zh-cn": "zh_CN", "zh-hk": "zh_TW"}
            timeago_language = timeago_language_dict[self.data['language']] if self.data['language'] else "zh_CN"
            for post in category_post:
                await self.generate_post_link([post])
                post["content"] = post["post_content"]
                await self.get_thumb_image([post])
                post['friendly_time'] = timeago.format(post['post_date'], now, timeago_language)
                if self.data['language'] in ["zh-tw", "zh-hk"]:
                    # x['content'] = await self.cc_async_s2t(x['content'])
                    post['post_title'] = await self.cc_async_s2t(post['post_title'])
                post['post_author'] = author_dict[post['post_author']]
                post['post_author']['author_link'] = await self.generate_author_link_by_author(post['post_author'])
            data['posts'] = category_post
            data["cn_url"] = "{}{}/".format(data["origin_url"], "zh-cn")
            data["tw_url"] = "{}{}/".format(data["origin_url"], "zh-tw")
            data["hk_url"] = "{}{}/".format(data["origin_url"], "zh-hk")

            data['next_page'] = "/category/{}/{}/".format(self.path_kwargs['category'],int(page) + 1)
            if self.data['language']:
                data['next_page'] = data['next_page'] + self.data['language'] + '/'
            self.data.update(data)
            print(json.dumps(data,default=str))
            self.render("category.html")
        else:
            self.send_error(404, reason="category not found")
