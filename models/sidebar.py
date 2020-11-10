from config import hot_news_num,redis_cache,redis_cache_ttl
from aiocache import cached, RedisCache
#from .cache import MsgPackSerializer
from aiocache.serializers import PickleSerializer,MsgPackSerializer
import datetime
from bson import ObjectId
from .tools import get_tname_by_tid
import re
from bson.json_util import dumps

def build_key(f,*args,**kwargs):
    if args[0].data['lang']:
        r = '{}_{}_{}'.format(args[0].site_name,f.__name__,args[0].data['lang'])
    else:
        r = '{}_{}'.format(args[0].site_name,f.__name__)
    return r

async def hot_black_list(db,hot_posts):
    hot_black_list = await db.config.find({'hot_black_title': {'$exists': True, '$ne': None}},
                                               {"hot_black_title": 1}).to_list(length=None)
    hot_black_list = [b['hot_black_title'] for b in hot_black_list]
    h = '(' + '|'.join(hot_black_list) + ')'
    news_hot_posts = []
    for x in hot_posts:
        filter = re.search(h, x['title'])
        if not filter:
            news_hot_posts.append(x)
    return news_hot_posts
@cached(ttl=redis_cache_ttl, timeout=0,cache=RedisCache, key_builder=build_key, endpoint=redis_cache['host'],
         serializer=PickleSerializer(), port=redis_cache['port'], db=redis_cache['db'],namespace="right_sidebar",pool_max_size=10)
async def hot_posts(self,post_type=0):
    async def process_hot(hot_posts):
        for x in hot_posts:
            x['_id'] = str(x['_id'])
        hot_posts = await self.get_thumb_image(hot_posts)
        for hot_post in hot_posts:
            del hot_post['content']
            if self.data['lang'] in ["zh-tw", "zh-hk"]:
                hot_post['title'] = await self.cc_async_s2t(hot_post['title'])
            elif self.data['lang'] == 'zh-cn':
                hot_post['title'] = await self.cc_async(hot_post['title'])
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    hot_posts_1 = await self.db.posts.find({'post_date': {'$gte': one_day_ago},"type":post_type},{ "_id": 1,"title": 1 ,"content":1}).sort([("views", -1)]).limit(hot_news_num).to_list(length=hot_news_num)
    hot_posts_1 = await hot_black_list(self.db,hot_posts_1)

    await process_hot(hot_posts_1)
    seven_day_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    hot_posts_7 = await self.db.posts.find({'post_date': {'$gte': seven_day_ago},"type":post_type},{ "_id": 1,"title": 1 ,"content":1}).sort([("views", -1)]).limit(hot_news_num).to_list(length=hot_news_num)
    hot_posts_7 = await hot_black_list(self.db, hot_posts_7)
    await process_hot(hot_posts_7)

    hot_posts = {}
    hot_posts['hot_posts_1'] = hot_posts_1
    hot_posts['hot_posts_7'] = hot_posts_7
    return hot_posts

@cached(ttl=redis_cache_ttl, timeout=0,cache=RedisCache, key_builder=build_key, endpoint=redis_cache['host'],
        serializer=PickleSerializer(), port=redis_cache['port'], db=redis_cache['db'],namespace="right_sidebar",pool_max_size=10)
async def new_comment_posts(self,post_type=0):
    new_comment_posts_ids = await self.db.comments.aggregate([
        {
            "$group":
                {
                    "_id": "$post_id",
                    "lastCommentDate": { "$last": "$comment_date" }
                }
        },
        { "$sort": { "lastCommentDate": -1} },
        {"$limit": hot_news_num },
    ]).to_list(length=None)
    new_comment_posts_ids = [ObjectId(i['_id']) for i in new_comment_posts_ids]
    new_comment_posts =  await self.db.posts.find({'_id': {'$in': new_comment_posts_ids}}).to_list(length=None)
    new_comment_posts = sorted(new_comment_posts,key=lambda x:new_comment_posts_ids.index(x['_id']))
    #print(new_comment_posts_ids,new_comment_posts)
    return new_comment_posts

def build_key_with_id(f,*args,**kwargs):
    return  args[0].site_name + '_' + f.__name__ + '_' + str(args[1])

@cached(ttl=redis_cache_ttl, timeout=0,cache=RedisCache, key_builder=build_key_with_id, endpoint=redis_cache['host'],
        serializer=PickleSerializer(), port=redis_cache['port'], db=redis_cache['db'],namespace="right_sidebar",pool_max_size=10)
async def c_hot_posts(self,c_id):
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    hot_posts_list = await self.db.posts.find({'post_date': {'$gte': one_day_ago},"type":0,"category":ObjectId(c_id)},{ "_id": 1,"title": 1 }).sort([("views", -1)]).limit(hot_news_num).to_list(length=hot_news_num)
    print(one_day_ago,ObjectId(c_id))
    for x in hot_posts_list:
        x['_id'] = str(x['_id'])
    hot_posts = dict({"name":await get_tname_by_tid(self.db,c_id)})
    hot_posts['list'] = hot_posts_list
    return hot_posts

@cached(ttl=redis_cache_ttl, timeout=0,cache=RedisCache, key_builder=build_key_with_id, endpoint=redis_cache['host'],
        serializer=PickleSerializer(), port=redis_cache['port'], db=redis_cache['db'],namespace="right_sidebar",pool_max_size=10)
async def u_new_posts(self,u_id,post_type=0):
    u_new_posts = await self.db.posts.find({ "user": u_id,"type":post_type},{ "_id": 1,"title": 1 }).limit(5).to_list(length=5)
    for x in u_new_posts:
        x['_id'] = str(x['_id'])
    return u_new_posts

@cached(ttl=redis_cache_ttl, timeout=0,cache=RedisCache, key_builder=build_key_with_id, endpoint=redis_cache['host'],
        serializer=PickleSerializer(), port=redis_cache['port'], db=redis_cache['db'],namespace="right_sidebar",pool_max_size=10)
async def u_categorys(self,u_id):
    u_categorys = await self.db.terms.find({ "user": u_id,"type":"2"},{ "_id": 1,"name": 1 }).to_list(length=None)
    for x in u_categorys:
        x['_id'] = str(x['_id'])
    return u_categorys