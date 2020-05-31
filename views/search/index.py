from views.base import BaseHandler,DBMixin,BlockingHandler
import tornado
import aiomysql
from elasticsearch_dsl import Search
from bson import ObjectId
class IndexHandler(BaseHandler,DBMixin):
    async def get(self):
        self.render("index.html")


class SearchHandler(BaseHandler,DBMixin):
    async def get(self):
        key = self.get_argument("q")
        p = int(self.get_argument("p",1))
        site_id = self.get_argument("site_id",'')
        start = p * 10 - 10
        end = p * 10
        data={}
        data['next_p'] = int(p) + 1
        data['key'] = key
        data['self'] = self
        if self.es:
            #s = Search(index='_all') \
            s = Search(index=self.es_index) \
                .query("match", title=key)
            if site_id:
                s = s.query("match", site_id=site_id)
            s = s.extra(track_total_hits=True)
            response = await self.es.search(s[start:end].to_dict())
        result = [r['_source'] for r in response['hits']['hits']]
        if site_id:
            self.db = self.application.dbs['by_site_id'][site_id]['db_conn']
            result_id = [ObjectId(i['post_id']) for i in result]
            result = await self.db.posts.find({'_id': {'$in': result_id}}).to_list(length=None)
            index_map = {v: i for i, v in enumerate(result_id)}
            result = sorted(result, key=lambda related_post: index_map[related_post['_id']])
            result = await self.get_posts_desc(result)
            result = await self.get_thumb_image(result)
            result = await self.generate_post_link(result,site_id)
        data["result_count"] = response['hits']['total']['value']
        data['results'] = result
        #print(result)
        if end > data["result_count"]:
            data['next_p'] = None
        #print(response)
        if p > 0:
            data['prev_p'] = p - 1
        else:
            data['prev_p'] = None
        data['site_id'] = site_id
        self.render("search.html",data=data)