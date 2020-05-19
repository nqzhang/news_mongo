from views.base import BlockingHandler,DBMixin
import tornado.escape
import aiomysql
import timeago,datetime
from .base import WpBaseHandler
import json

class AuthorHandler(WpBaseHandler):
    async def get(self,user_nicename,page,language=None):
        lang=language
        if not page:
            page = 1
        async with self.db.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * FROM wp_users WHERE user_nicename = %s LIMIT 1",(user_nicename))
                s = await cur.fetchone()
                #print(s)
                author_id = s['ID']
                #print(page)
                await cur.execute("SELECT * FROM wp_posts WHERE post_author=%s and post_type='post' and "
                                  "post_status='publish' ORDER BY wp_posts.post_date DESC LIMIT %s,15", (author_id,(int(page) -1) * 15))
                posts = await cur.fetchall()
                #print(posts)
                posts_id = [str(post['ID']) for post in posts]
                # meta_sql = "SELECT t.*, tt.*, tr.object_id FROM wp_terms AS t INNER JOIN wp_term_taxonomy AS tt " \
                #        "ON t.term_id = tt.term_id INNER JOIN wp_term_relationships AS tr ON tr.term_taxonomy_id = tt.term_taxonomy_id " \
                #        "WHERE tt.taxonomy IN ('category', 'post_tag', 'post_format') AND tr.object_id IN ({}) " \
                #        "ORDER BY t.name ASC"
                # await cur.execute(meta_sql.format(','.join(posts_id)))
                # r = await cur.fetchall()
                # tmp_d = {}
                # for x in r:
                #     if x['object_id'] not in tmp_d:
                #         tmp_d[x['object_id']] = {}
                #     if x['taxonomy'] == "category":
                #         if "category" in tmp_d[x['object_id']]:
                #             tmp_d[x['object_id']]['category'].append(x)
                #         else:
                #             tmp_d[x['object_id']]['category'] = [x]
                #     elif x['taxonomy'] == "post_tag":
                #         if "post_tag" in tmp_d[x['object_id']]:
                #             tmp_d[x['object_id']]['post_tag'].append(x)
                #         else:
                #             tmp_d[x['object_id']]['post_tag'] = [x]
                # for x in posts:
                #     x['terms'] = tmp_d[x['ID']]
                    #print(json.dumps(x,default=str))
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timeago_language_dict = {"zh-tw": "zh_TW", "zh-cn": "zh_CN", "zh-hk": "zh_TW"}
        timeago_language = timeago_language_dict[self.data['lang']] if self.data['lang'] else "zh_CN"
        for post in posts:
            await self.generate_post_link([post])
            post["content"] = post["post_content"]
            await self.get_thumb_image([post])
            post['friendly_time'] = timeago.format(post['post_date'], now, timeago_language)
            if self.data['lang'] in ["zh-tw", "zh-hk"]:
                # x['content'] = await self.cc_async_s2t(x['content'])
                post['post_title'] = await self.cc_async_s2t(post['post_title'])
        data={}
        data['posts'] = posts
        data['author'] = s
        data['next_page'] = '/author/{}/{}/'.format(data['author']['user_nicename'],int(page) + 1)
        if self.data['lang']:
            data['next_page'] = data['next_page'] + self.data['lang'] + '/'
        data['desc'] = ''
        data["origin_url"] = "/author/{}/".format(user_nicename)
        data["cn_url"] = "{}{}/".format(data["origin_url"], "zh-cn")
        data["tw_url"] = "{}{}/".format(data["origin_url"], "zh-tw")
        data["hk_url"] = "{}{}/".format(data["origin_url"], "zh-hk")
        self.data.update(data)
        self.render("author.html")