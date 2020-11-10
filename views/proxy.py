#coding=utf8
from tornado.web import RequestHandler
import tornado.httpclient
#from pyquery import PyQuery as pq
from urllib.parse import urlparse,urlunparse,quote,unquote,urlencode
import string
import config
import re,json
from tornado.httputil import url_concat


class ProxyHandler(RequestHandler):
    async def get(self,url):
        #print(url)
        params = { k: self.get_argument(k) for k in self.request.arguments }
        #regex = re.compile("^/proxy/|^/proxy/csdn/|/proxy/360doc/|")
        #url = regex.sub('', url)
        url = quote(url,safe = string.printable)
        url = url_concat(url,params)
        url = tornado.escape.url_unescape(url)
        parsed_uri = urlparse(url)
        headers = {}
        if parsed_uri.netloc.endswith('baidu.com'):
            headers=config.baijia_headers
        if parsed_uri.netloc.endswith('csdn.net'):
            headers=config.csdn_headers
        if parsed_uri.netloc == 'niuerdata.g.com.cn':
            self.set_header('Content-Type','image/gif')
            self.finish(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
            return
        if parsed_uri.netloc.endswith('360doc.com'):
            headers['Referer'] = 'http://www.360doc.com/'
        try:
            #print(headers,url)
            resp = await self.application.http_client.fetch(url, request_timeout=5, connect_timeout=3,validate_cert=False,headers=headers)
        except tornado.httpclient.HTTPError as e:
            #e.response
            print("Error: " + str(e))
            raise tornado.web.HTTPError(500, reason='fetch error')
        except Exception as e:
            print("Error: " + str(e))
            raise tornado.web.HTTPError(500, reason='fetch error')
        resp.headers.pop('Content-Length',None)
        resp.headers.pop('Set-Cookie',None)
        resp.headers.pop('Server', None)
        resp.headers.pop('Transfer-Encoding', None)
        resp.headers['cache-control'] = 'public,max-age=2592000000'
        for x, y in resp.headers.items():
            self.set_header(x, y)
        html = resp.body
        self.write(html)

class ReferHandler(RequestHandler):
    async def get(self,url):
        url = self.request.uri.lstrip('/proxy/refer/')
        parsed_uri = urlparse(url)
        refer = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        if parsed_uri.netloc == 'niuerdata.g.com.cn':
            self.set_header('Content-Type','image/gif')
            self.write(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
            return
        headers = {
            'Referer': refer,
        }
        url = quote(url,safe = string.printable)
        try:
            resp = await self.application.http_client.fetch(url, request_timeout=5, connect_timeout=3,validate_cert=False,headers =headers)
        except tornado.httpclient.HTTPError as e:
            #e.response
            print("Error: " + str(e))
            raise tornado.web.HTTPError(500, reason='fetch error')
        except Exception as e:
            print("Error: " + str(e))
            raise tornado.web.HTTPError(500, reason='fetch error')
        resp.headers.pop('Content-Length',None)
        resp.headers.pop('Set-Cookie',None)
        resp.headers.pop('Server', None)
        resp.headers.pop('Transfer-Encoding', None)
        resp.headers['cache-control'] = 'public,max-age=2592000000'
        for x, y in resp.headers.items():
            self.set_header(x, y)
        html = resp.body
        self.finish(html)


class ProxyBaijiaHandler(RequestHandler):
    async def get(self,url):
        url = self.request.uri.lstrip('/proxy/baijia/')
        url = quote(url,safe = string.printable)
        try:
            resp = await self.application.http_client.fetch(url, request_timeout=5, connect_timeout=3,validate_cert=False,headers=config.baijia_headers)
        except tornado.httpclient.HTTPError as e:
            #e.response
            print("Error: " + str(e))
            raise tornado.web.HTTPError(500, reason='fetch error')
        except Exception as e:
            print("Error: " + str(e))
            raise tornado.web.HTTPError(500, reason='fetch error')
        resp.headers.pop('Content-Length',None)
        resp.headers.pop('Set-Cookie',None)
        resp.headers.pop('Server', None)
        resp.headers.pop('Transfer-Encoding', None)
        resp.headers['cache-control'] = 'public,max-age=2592000000'
        for x, y in resp.headers.items():
            self.set_header(x, y)
        html = resp.body
        self.finish(html)

class Proxy360DocHandler(RequestHandler):
    async def get(self,url):
        url = self.request.uri.lstrip('/proxy/360doc/')
        url = quote(url,safe = string.printable)
        try:
            resp = await self.application.http_client.fetch(url, request_timeout=5, connect_timeout=3,validate_cert=False,headers=config.doc360_headers)
        except tornado.httpclient.HTTPError as e:
            #e.response
            print("Error: " + str(e))
            raise tornado.web.HTTPError(500, reason='fetch error')
        except Exception as e:
            print("Error: " + str(e))
            raise tornado.web.HTTPError(500, reason='fetch error')
        resp.headers.pop('Content-Length',None)
        resp.headers.pop('Set-Cookie',None)
        resp.headers.pop('Server', None)
        resp.headers.pop('Transfer-Encoding', None)
        resp.headers['cache-control'] = 'public,max-age=2592000000'
        for x, y in resp.headers.items():
            self.set_header(x, y)
        html = resp.body
        self.finish(html)

class ProxyCSDNHandler(RequestHandler):
    async def get(self, url):
        url = self.request.uri.lstrip('/proxy/csdn/')
        url = quote(url, safe=string.printable)
        try:
            resp = await self.application.http_client.fetch(url, request_timeout=5, connect_timeout=3,validate_cert=False,headers=config.csdn_headers)
        except tornado.httpclient.HTTPError as e:
            #e.response
            print("Error: " + str(e))
            raise tornado.web.HTTPError(500, reason='fetch error')
        except Exception as e:
            print("Error: " + str(e))
            raise tornado.web.HTTPError(500, reason='fetch error')
        resp.headers.pop('Content-Length',None)
        resp.headers.pop('Set-Cookie',None)
        resp.headers.pop('Server', None)
        resp.headers.pop('Transfer-Encoding', None)
        resp.headers['cache-control'] = 'public,max-age=2592000000'
        for x, y in resp.headers.items():
            pass
            #print(x,y)
            self.set_header(x, y)
        html = resp.body
        #print(html)
        self.finish(html)

