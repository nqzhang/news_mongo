from views.base import BlockingHandler,DBMixin
import tornado.escape
import tornado.web
import aiomysql
import timeago,datetime
from urllib.parse import urljoin
from bson import ObjectId
import pymongo
import json
import math

class SitemapHandler(BlockingHandler,DBMixin):
    def reverse_full_url(self, name, *args, **kwargs):
        host_url = "{protocol}://{host}".format(**vars(self.request))
        return urljoin(host_url, self.reverse_url(name, *args, **kwargs))
    async def get(self):
        url_per_sitemap = 50000
        type = self.get_argument("type",None)
        self.set_header('Content-Type', 'text/xml')
        self.set_header('cache-control',
                        'public, stale-while-revalidate=120,stale-if-error=3600,max-age=300,s-maxage=300')
        if type=="sitemap":
            day_min = self.get_argument("day_min")
            day_max = self.get_argument("day_max")
            page = int(self.get_argument("page"))
            day_min = datetime.datetime.fromisoformat(day_min)
            day_max = datetime.datetime.fromisoformat(day_max)
            print(day_min,day_max,page)
            if page == 1:
                posts = await self.db.posts.find({"post_date": {"$gte":day_min,"$lte":day_max}}, {"_id": 1,"post_date":1}).limit(
                    url_per_sitemap).to_list(length=None)
            else:
                posts = await self.db.posts.find({"post_date": {"$gte":day_min,"$lte":day_max}}, {"_id": 1,"post_date":1})\
                    .skip(url_per_sitemap *(page-1)).limit(url_per_sitemap).to_list(length=None)
            self.data={}
            await self.generate_post_link(posts)
            self.render("../sitemap.xml",posts=posts)
        elif type=="index":
            min_date = (await self.db.posts.find({}, {"post_date": 1}).sort([("post_date", pymongo.ASCENDING)]).limit(
                1).to_list(length=None))[0]
            max_date = (await self.db.posts.find({}, {"post_date": 1}).sort([("post_date", pymongo.DESCENDING)]).limit(
                1).to_list(length=None))[0]
            max_date,min_date = max_date['post_date'],min_date['post_date']
            today_min = datetime.datetime.combine(datetime.date.today() ,datetime.time.min)
            tmp_d = {}
            tmp_d_lastmod = {}
            post_per_days = self.db.meta.find({"meta_type": "post_per_day"})
            async for post_per_day in post_per_days:
                tmp_d[post_per_day['meta_key']] = post_per_day
            post_last_mods =  self.db.meta.find({"meta_type": "post_per_day_lastmod"})
            async for post_last_mod in post_last_mods:
                tmp_d_lastmod[post_last_mod['meta_key']] = post_last_mod
            #print(tmp_d)
            result = []
            delta_days = math.ceil((max_date - min_date).total_seconds() / 86400)
            for i in range(delta_days + 1):
                day_max = datetime.datetime.combine(min_date + datetime.timedelta(days=i),
                                          datetime.time.max)
                day_min = datetime.datetime.combine(min_date + datetime.timedelta(days=i),
                                          datetime.time.min)
                #print(day_min)
                if day_min == today_min:
                    post_last_mod = (await self.db.posts.find({"post_date": {"$gte": day_min, "$lte": day_max}},{"post_date": 1}) \
                        .sort([("post_date", pymongo.DESCENDING)]).limit(1).to_list(length=1))[0]['post_date']
                else:
                    post_last_mod = tmp_d_lastmod.get(day_min,None)
                    if post_last_mod:
                        post_last_mod = post_last_mod.get('meta_value',None)
                    else:
                        post_last_mod = await self.db.posts.find({"post_date": {"$gte": day_min, "$lte": day_max}},{"post_date": 1}) \
                            .sort([("post_date", pymongo.DESCENDING)]).limit(1).to_list(length=1)
                        if post_last_mod:
                            post_last_mod = post_last_mod[0]['post_date']
                        else:
                            post_last_mod = None
                        await self.db.meta.insert_one(
                            {"meta_type": "post_per_day_lastmod", "meta_key": day_min, "meta_value": post_last_mod})

                if post_last_mod:
                    post_last_mod = post_last_mod.isoformat()
                if day_min == today_min:
                    post_per_day = await self.db.posts.count_documents({"post_date": {"$gte":day_min,"$lte":day_max}})
                else:
                    post_per_day = tmp_d.get(day_min,None)
                    #print(post_per_day)
                    if post_per_day:
                        post_per_day = tmp_d.get(day_min).get('meta_value',None)
                    if not post_per_day and post_per_day != 0:
                        post_per_day = await self.db.posts.count_documents({"post_date": {"$gte":day_min,"$lte":day_max}})
                        await self.db.meta.insert_one({"meta_type": "post_per_day", "meta_key": day_min,"meta_value":post_per_day})
                sitemap_index_num = math.ceil(post_per_day / url_per_sitemap)
                result.append((day_min.isoformat(),day_max.isoformat(),sitemap_index_num,post_last_mod,post_per_day))
            self.render('../sitemap_index.xml',result=result)