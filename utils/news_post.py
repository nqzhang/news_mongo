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
    for n in range(1):
        n = str(n) +   uuid.uuid4().hex
        #body['category'] = ['财经{}'.format(n)]
        body['code'] = 'qtRjhwcGLHnXPQlC'
        body['category'] = ['物联网']
        body['title'] = '財報利多激勵 美股收高道瓊大漲213.519點{}'.format(n)
        body['content'] = '''<section itemprop="articleBody"><p>（中央社紐約17日綜合外電報導）受到企業公布的財報利多激勵,尤其是網飛（Netflix）財報點燃科技股漲勢,華爾街股市今天收高,道瓊工業指數大漲213.59點。網飛狂漲超過9%。<br/><br/>根據路透社,道瓊工業指數大漲213.59點或0.87%,以24786.63點作收。<br/><br/>標準普爾指數大漲28.55點或1.07%,收在2706.39點。<br/><br/>科技股那斯達克指數大漲124.81點或1.74%,收7281.10點。（譯者：陳政一）1070418</p></section>'''
        body['user'] = '898611548@qq.com'
        body['tags'] = ['涉及','爱情']
        body['thumb'] = ''
        body['content'] = 10 * body['content']
        #response = await http_client.fetch('http://127.0.0.1:48000/backend/newpost',method='POST',proxy_host='127.0.0.1', proxy_port=1080,request_timeout=3,connect_timeout=3,body=json.dumps(body, ensure_ascii=False))
        response =  await http_client.fetch('http://127.0.0.2/backend/newpost',method='POST',request_timeout=300,connect_timeout=300,body=json.dumps(body).encode("utf-8"))
        print(response.body)
        #if response.code == 200:
        #print(proxy_host + ':' + str(proxy_port))
    #except Exception as e:
        #pass
AsyncIOMainLoop().install()
loop = asyncio.get_event_loop()
loop.run_until_complete(to_asyncio_future(news_post()))