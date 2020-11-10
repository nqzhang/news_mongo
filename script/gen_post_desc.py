from views.base import BlockingHandler
import tornado.httpclient
import asyncio
import json
from tornado.platform.asyncio import to_asyncio_future, AsyncIOMainLoop
import uuid
import datetime
import sys
import motor
import asyncio
from lxml import etree
from bs4 import BeautifulSoup
import config
from tornado.ioloop import IOLoop
import motor.motor_asyncio
from bson import ObjectId
import concurrent.futures
import aiohttp
from math import floor
from multiprocessing import Process

if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import logging
logging.basicConfig(level=logging.DEBUG)

def get_post_desc( post):
    if not post['content']:
        post['post_desc'] = None
        post['post_thumb'] = None
    else:
        soup = BeautifulSoup(post['content'], "lxml")
        if "desc" not in post:
            if soup is None:
                post_desc = None
            else:
                post_desc = soup.get_text()[:120]
            post['desc'] = post_desc

        if 'post_thumb' not in post:
            post_thumb = ''
            if soup is not None:
                imgs = soup.find_all('img')
                if imgs:
                    post_thumb = imgs[0].get('src')
            # post_desc = post_etree.cssselect('p')[0].text
            post['post_thumb'] = post_thumb

    return post

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def process(sem,sitemaps,loop,db):
    for sitemap in sitemaps:
        async with sem:
        # async with aiohttp.ClientSession() as session:
        #     response = await fetch(session,sitemap)
            http_client = tornado.httpclient.AsyncHTTPClient()
            response = await http_client.fetch(sitemap,connect_timeout=300,request_timeout=300)
            soup = BeautifulSoup(response.body, "lxml")
            elements = soup.findAll("loc")
            for element in elements:
                #print(element)
                post_id = ObjectId(element.text.rsplit('/',1)[1])
                q = await db.posts.find_one({"_id":post_id})
                if q:
                    if "desc" not in q or "post_thumb" not in q:
                        #with concurrent.futures.ProcessPoolExecutor(max_workers=1) as pool:
                            #q  = await loop.run_in_executor(pool, get_post_desc,q)
                        q = get_post_desc(q)
                        print(f'{q["desc"]}__{q["_id"]}__{q["post_thumb"]}')
                        await db.posts.update_one({'_id': ObjectId(post_id)}, {"$set": {"desc": q['desc'],"post_thumb": q['post_thumb']}})

async def get_site_map_index(site_domain,db):
    loop = asyncio.get_running_loop()
    site_domain = site_domain
    http_client = tornado.httpclient.AsyncHTTPClient()
    response = await http_client.fetch('http://{}/sitemap/plauvzepsddkiuvd.xml?type=index'.format(site_domain))
    soup = BeautifulSoup(response.body, "lxml")
    elements = soup.findAll("loc")
    return elements

site_domain = "www.xuehua.us"
db={}
db['host'] = '95.216.78.164'
db['db_name'] = 'news_xuehua_us'





async def start(elements,db):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_running_loop()
    db = motor.motor_asyncio.AsyncIOMotorClient(db['host'], 27017)[db['db_name']]
    sem = asyncio.Semaphore(5)
    tasks = []
    size = 20
    tasks.append(process(sem,elements,loop,db))
    await asyncio.gather(*tasks)


class myprocess(Process):
    def __init__(self, elements):
        self.sitemaps = elements
        super(myprocess, self).__init__()

    def run(self):
        asyncio.run(start(self.sitemaps,db))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    elements = loop.run_until_complete(get_site_map_index(site_domain,db))
    elements = [i.text for  i in elements]
    size = 20
    sitemaps = [elements[i:i + size] for i in range(0, len(elements), floor(len(elements) / size))]

    print(elements)
    process_list = []
    for x,i in enumerate(sitemaps):  # 开启5个子进程执行fun1函数
        p = myprocess(i)  # 实例化进程对象
        p.start()
        process_list.append(p)

    for p in process_list:
        p.join()

    print('结束测试')
