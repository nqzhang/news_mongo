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
        if language:
            category_url = "/category/{}/".format(category) + language + '/'
        else:
            category_url = "/category/{}/".format(category)
        slug = tornado.escape.url_escape(category.split('/')[-1]).lower()
        category_sql = "/* category_sql */SELECT t.*, tt.* FROM wp_terms AS t INNER JOIN wp_term_taxonomy AS tt " \
                       "ON t.term_id = tt.term_id WHERE tt.taxonomy IN ('category') AND t.slug = '{}'".format(slug)
        # sub_category_sql = "with recursive cte (term_taxonomy_id,term_id, parent) as (select term_taxonomy_id,term_id, parent from wp_term_taxonomy where parent = {} " \
        #                    "union all select p.term_taxonomy_id,p.term_id, p.parent from wp_term_taxonomy p inner join cte on p.parent = cte.term_id) select * from cte;"
        sub_category_sql = "select term_taxonomy_id,term_id, parent from wp_term_taxonomy where parent = {}"
        category_post_sql= "SELECT  wp_posts.* FROM wp_posts  left jOIN wp_term_relationships ON (wp_posts.ID = wp_term_relationships.object_id) " \
                              "where  wp_term_relationships.term_taxonomy_id IN ({}) AND wp_posts.post_type = 'post' AND " \
                              "wp_posts.post_status = 'publish' ORDER BY wp_posts.ID DESC LIMIT {},15;"
        async with self.db.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(category_sql)
                category = await  cur.fetchone()
        if category:
            async with self.db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    # await cur.execute(sub_category_sql.format(category['term_id']))
                    # sub_category = await cur.fetchall()
                    # if sub_category:
                    #     sub_category_taxonomy_id = [x['term_taxonomy_id'] for x in sub_category]
                    #     sub_category_taxonomy_id.insert(0,category['term_taxonomy_id'])
                    # else:
                    sub_category_taxonomy_id = [category['term_taxonomy_id']]
                    await cur.execute(category_post_sql.format(','.join([str(x) for x in sub_category_taxonomy_id]),(int(page) -1) * 15))
                    category_post = await cur.fetchall()
                    authors = [str(post['post_author']) for post in category_post]
                    author_dict = {}
                    await cur.execute("SELECT * FROM wp_users WHERE ID in ({})".format(','.join(authors)))
                    authors = await cur.fetchall()
                    meta_sql = "SELECT t.*, tt.*, tr.object_id FROM wp_terms AS t INNER JOIN wp_term_taxonomy AS tt " \
                           "ON t.term_id = tt.term_id INNER JOIN wp_term_relationships AS tr ON tr.term_taxonomy_id = tt.term_taxonomy_id " \
                           "WHERE tt.taxonomy IN ('category', 'post_tag') AND tr.object_id IN ({}) "
                    await cur.execute(meta_sql.format(','.join([str(post['ID']) for post in category_post])))
                    r = await cur.fetchall()
            tmp_d = {}
            for x in r:
                if x['object_id'] not in tmp_d:
                    tmp_d[x['object_id']] = {}
                if x['taxonomy'] == "category":
                    if "category" in tmp_d[x['object_id']]:
                        tmp_d[x['object_id']]['category'].append(x)
                    else:
                        tmp_d[x['object_id']]['category'] = [x]
                elif x['taxonomy'] == "post_tag":
                    if self.data['lang'] in ["zh-tw", "zh-hk"]:
                        x['name'] = await self.cc_async_s2t(x['name'])
                    if "post_tag" in tmp_d[x['object_id']]:
                        tmp_d[x['object_id']]['post_tag'].append(x)
                    else:
                        tmp_d[x['object_id']]['post_tag'] = [x]
            for x in category_post:
                x['terms'] = tmp_d[x['ID']]
            # print(1111,json.dumps(category_post,default=str))
            for author in authors:
                author_dict[author['ID']] = author
            # print(author_dict)

            data={}
            data['category'] = category
            data["origin_url"] = "/category/{}/".format(self.path_kwargs['category'])
            if self.path_kwargs['page']:
                data["origin_url"] = "{}{}/".format(data["origin_url"],self.path_kwargs['page'])
            # if self.path_kwargs['language']:
            #     data["origin_url"] = "{}{}/".format(data["origin_url"],self.path_kwargs['language'])
            #print(data["origin_url"])
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            timeago_language_dict = {"zh-tw": "zh_TW", "zh-cn": "zh_CN", "zh-hk": "zh_TW"}
            timeago_language = timeago_language_dict[self.data['lang']] if self.data['lang'] else "zh_CN"
            for post in category_post:
                await self.generate_post_link([post])
                post["content"] = post["post_content"]
                await self.get_thumb_image([post])
                post['friendly_time'] = timeago.format(post['post_date'], now, timeago_language)

                post['post_author'] = author_dict[post['post_author']]
                post['post_author']['author_link'] = await self.generate_author_link_by_author(post['post_author'])
                if self.data['lang'] in ["zh-tw", "zh-hk"]:
                    # x['content'] = await self.cc_async_s2t(x['content'])
                    post['post_title'] = await self.cc_async_s2t(post['post_title'])
                    post['post_author']['display_name'] = await self.cc_async_s2t(post['post_author']['display_name'])

            data['posts'] = category_post
            data["cn_url"] = "{}{}/".format(data["origin_url"], "zh-cn")
            data["tw_url"] = "{}{}/".format(data["origin_url"], "zh-tw")
            data["hk_url"] = "{}{}/".format(data["origin_url"], "zh-hk")

            data['next_page'] = "/category/{}/{}/".format(self.path_kwargs['category'],int(page) + 1)
            if self.data['lang']:
                data['next_page'] = data['next_page'] + self.data['lang'] + '/'
            data['category_url'] = category_url
            self.data.update(data)
            print(category)
            #print(json.dumps(data,default=str))
            self.render("category.html")
        else:
            self.send_error(404, reason="category not found")
