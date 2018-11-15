from config import hot_news_num,redis_cache,redis_cache_ttl
from aiocache import cached, RedisCache
from .cache import MsgPackSerializer
import datetime
from bson import ObjectId
from .tools import get_tname_by_tid

@cached(ttl=redis_cache_ttl, cache=RedisCache, key="hot_posts", endpoint=redis_cache['host'],
        serializer=MsgPackSerializer(), port=redis_cache['port'], db=redis_cache['db'],namespace="right_sidebar",pool_max_size=10)
async def hot_posts(db):
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    hot_posts = await db.posts.find({'post_date': {'$gte': one_day_ago}},{ "_id": 1,"title": 1 }).sort([("views", -1)]).limit(hot_news_num).to_list(length=hot_news_num)
    print(hot_posts)
    for x in hot_posts:
        x['_id'] = str(x['_id'])
    print(hot_posts)
    return hot_posts

def build_key_c_hot_posts(*args):
    return "hot_posts_c_{}".format(args[1])
@cached(ttl=redis_cache_ttl, cache=RedisCache, key_builder=build_key_c_hot_posts, endpoint=redis_cache['host'],
        serializer=MsgPackSerializer(), port=redis_cache['port'], db=redis_cache['db'],namespace="right_sidebar",pool_max_size=10)
async def c_hot_posts(db,c_id):
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    hot_posts_list = await db.posts.find({'post_date': {'$gte': one_day_ago},"category":ObjectId(c_id)},{ "_id": 1,"title": 1 }).sort([("views", -1)]).limit(hot_news_num).to_list(length=hot_news_num)
    for x in hot_posts_list:
        x['_id'] = str(x['_id'])
    hot_posts = dict({"name":await get_tname_by_tid(db,c_id)})
    hot_posts['list'] = hot_posts_list
    return hot_posts

def build_key_u_new_posts(*args):
    return "new_posts_u_{}".format(args[1])
@cached(ttl=redis_cache_ttl, cache=RedisCache, key_builder=build_key_u_new_posts, endpoint=redis_cache['host'],
        serializer=MsgPackSerializer(), port=redis_cache['port'], db=redis_cache['db'],namespace="right_sidebar",pool_max_size=10)
async def u_new_posts(db,u_id):
    u_new_posts = await db.posts.find({ "user": u_id},{ "_id": 1,"title": 1 }).limit(hot_news_num).to_list(length=hot_news_num)
    for x in u_new_posts:
        x['_id'] = str(x['_id'])
    return u_new_posts

def build_key_u_categorys(*args):
    return "u_categorys_{}".format(args[1])
@cached(ttl=redis_cache_ttl, cache=RedisCache, key_builder=build_key_u_categorys, endpoint=redis_cache['host'],
        serializer=MsgPackSerializer(), port=redis_cache['port'], db=redis_cache['db'],namespace="right_sidebar",pool_max_size=10)
async def u_categorys(db,u_id):
    u_categorys = await db.terms.find({ "user": u_id,"type":"2"},{ "_id": 1,"name": 1 }).to_list(length=None)
    for x in u_categorys:
        x['_id'] = str(x['_id'])
    return u_categorys