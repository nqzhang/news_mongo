import tornado
import tornado.web

class SitemapStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        if path == 'sitemap.xml':
        # Disable cache
            self.set_header('cache-control', 'public, stale-while-revalidate=120,stale-if-error=3600,max-age=5,s-maxage=3600')
        else:
            self.set_header('cache-control',
                            'public, stale-while-revalidate=120,stale-if-error=3600,max-age=600,s-maxage=2592000')

class StaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        #if path == 'sitemap.xml':
        self.set_header('cache-control',
                            'public, stale-while-revalidate=120,stale-if-error=3600,max-age=600,s-maxage=86400')