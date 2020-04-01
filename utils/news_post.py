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
    for n in range(1,100):
        #n = str(n) +   uuid.uuid4().hex
        #body['category'] = ['财经{}'.format(n)]
        body['code'] = 'qtRjhwcGLHnXPQlC'
        body['category'] = ['物联网']
        body['title'] = '大暴雨浇出“前”汛期！华南官宣入汛今明暴雨倾盆{}'.format(n)
        body['content'] = '''<p>中国天气网讯3月以来，我国南方降水逐渐增多，江南、华南一带经历了多轮降水过程，不少地方累计雨量达到100毫米以上。其中广西降水“表现”十分抢眼，于昨天（25日）官宣入汛，这就意味着华南前汛期正式开启。</p><p>广西官宣入汛成为华南开启前汛期的“领头羊”</p><p>3月25日，广西官宣入汛，这也就意味着广西凭借强劲的降水“实力”，带领华南地区正式进入了汛期。根据广西入汛标准监测，截至3月25日20时，广西累计有52个监测站点日降雨量≥38毫米，且25日当日降雨量≥38毫米的站点有18个，达到广西入汛标准，比常年提前29天入汛，为1951年以来第二早。</p><p>中国天气网气象分析师邵鹏介绍，每年的3月份华南地区开启“入汛”进程，广东、广西、福建、海南四省区其中之一入汛，即可宣布华南地区正式进入汛期。1961年以来，广东大部分年份是带领华南入汛的“领头羊”，但今年情况有变，广东入汛可能等到4月初。</p><p>从时间上来看，今年华南入汛的日期比常年平均（4月6日）早了近半个月的时间。不过从历史上来看，今年入汛不算最早的，最早记录出现在1983年，3月1日华南就进入了汛期；而目前最晚的入汛时间则出现在1963年，6月1日才官宣入汛。</p><img alt="大暴雨浇出“前”汛期！华南官宣入汛今明暴雨倾盆" src="https://p9.pstatp.com/large/pgc-image/RuJCk9DBM5blaL"><p>3月以来，广西大部累积降雨达到50毫米以上，其中中北部地区达到100毫米以上，而东北地区局地累积雨量甚至达到200毫米以上。</p><p>从单点上看，桂林和南宁的降雨比较突出，其中桂林的降雨属于“超长待机”型，3月1日至25日，累积降雨量超过了250毫米，降雨日数达到17天，尤其是从16日以来连续9天出现降雨。而南宁的降雨属于“暴力入侵”型，特别是昨天城区1小时雨量突破57毫米，遭遇三波短时强降雨的“洗礼”，24小时的累计降雨量达到了大暴雨的级别，这是南宁自有气象记录以来，首次在3月遭遇大暴雨侵袭。</p><p>数据上可以看出，此时段的雨似乎下得比较“暴力”，这正符合华南前汛期的降水特点，每年3月至4月份，我国频繁有弱冷空气南下，而控制南方，特别是控制华南一带的西南气流十分旺盛，冷暖空气激烈地“碰撞”下，降雨显现出强烈的对流性。</p><img alt="大暴雨浇出“前”汛期！华南官宣入汛今明暴雨倾盆" src="https://p3.pstatp.com/large/pgc-image/RuJCk9wF8wibfY"><p>南方“暴力”降雨还将持续警惕次生灾害及强对流</p><p>华南进入前汛期拉开了我国汛期的序幕，南方大范围的强降雨将频繁“登场”。中央气象台预计，未来10天（3月26日至4月4日），江南、华南中北部、江淮、江汉及重庆和贵州东部累计降水量有50～110毫米，其中江南和华南北部的部分地区有130～180毫米，局地超过200毫米；上述大部分地区较常年同期偏多5～8成，部分地区偏多1倍以上。</p><p>其中，今明天，西南地区东部、江淮、江汉、江南、华南大部等地的部分地区有中到大雨，局地暴雨或大暴雨，并伴有雷暴大风或冰雹等强对流天气。</p><p>从4月上旬、中旬的趋势来看，华南一带仍是重点防汛区域，尤其是广西、广东北部、福建中北部会出现的强降雨和强对流天气，其中广西大部累计降雨可能会比常年同期偏多50%以上。此期间多暴雨，雷暴大风、冰雹、短时强降水等强对流天气，容易引发山洪、滑坡、泥石流等灾害，城乡地区易出现积涝，对于交通、农业生产及居民安全都会带来较大的影响。（策划/江漪设计/陈玉洁数据支持/邵鹏胡啸审核/陈曦张慧）</p>'''
        body['user'] = '898611548@qq.com'
        body['tags'] = ['涉及','爱情']
        body['thumb'] = ''
        #body['content'] = 10 * body['content']
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