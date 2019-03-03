#coding=utf8
import tornado.httpclient
import asyncio
import json
from tornado.platform.asyncio import to_asyncio_future, AsyncIOMainLoop
import uuid

async def news_post():
    #tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = tornado.httpclient.AsyncHTTPClient()
    body = {}
    for n in range(1,2):
        n = str(n) +   uuid.uuid4().hex
        #body['category'] = ['财经{}'.format(n)]
        body['code'] = 'qtRjhwcGLHnXPQlC'
        body['title'] = '问题标题{}'.format(n)
        body['content'] = '''问题描述'''
        body['user'] = '雪花新闻11'
        body['tags'] = ['涉及','爱情']
        body['thumb'] = ''
        body['post_type'] = 'question'
        #response = await http_client.fetch('http://127.0.0.1:48000/backend/newpost',method='POST',proxy_host='127.0.0.1', proxy_port=1080,request_timeout=3,connect_timeout=3,body=json.dumps(body, ensure_ascii=False))
        response =  await http_client.fetch('http://127.0.0.1:48000/backend/newpost',method='POST',request_timeout=300,connect_timeout=300,body=json.dumps(body, ensure_ascii=False).encode("utf-8"))
        print(response.body)
        #if response.code == 200:
        #print(proxy_host + ':' + str(proxy_port))
    #except Exception as e:
        #pass
AsyncIOMainLoop().install()
loop = asyncio.get_event_loop()
loop.run_until_complete(to_asyncio_future(news_post()))