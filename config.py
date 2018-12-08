import os
from views import static
BASE_DIR = os.path.dirname(__file__)

mongo = {
    "url":"mongodb://admin:11QQqqWW@192.168.99.12",
    "urlbak": "mongodb://95.216.6.102:27016",
    "db_name":"news"
}
redis ={
    "host":"192.168.99.12",
    "port":6379,
    "db":0,
}

redis_cache ={
    "host":"192.168.99.12",
    "port":6379,
    "db":1
}

settings = {
    "static_path":os.path.join(BASE_DIR,'static'),
    "static_handler_class":static.StaticFileHandler,
    "template_path": os.path.join(BASE_DIR,'template'),
    "debug":True,
    "autoreload":False,
    #"compiled_template_cache": False,
    #"static_hash_cache": False,
    #"serve_traceback": True,
    "cookie_secret":"E2PHKvHUSPeNMz9UgxB2PFaQGi616EAltl7KnSJvH+0=",#base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
    "xsrf_cookies":True,
    "login_url":'/?login=1',
}

redis_cache_ttl = 600
session_ttl = 30 * 24 * 60 * 60
articles_per_page = 15
hot_news_num = 7
site_name = '神馬文庫'
site_domain = 'http://127.0.0.1:48000'
smtp_hostname = 'smtp.mailgun.org'
smtp_login = 'postmaster@www.smwenku.com'
smtp_pass = '9b546fb86ccac1a87b2233aee6c378aa-c9270c97-04d79fc6'

custom_meta = """<meta name="google-site-verification" content="QSl8rlXGYak0SPdlX0r_tMqD7I6XFuWD1JxR_D9PbyM" />
                <meta name="msvalidate.01" content="4775F105590951C69208A1E849EF0F32" />"""
analytics_code = """
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-124635989-1"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'UA-124635989-1');
        </script>"""
adsense_code = """
<script data-cfasync="false" async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<script>
  (adsbygoogle = window.adsbygoogle || []).push({
    google_ad_client: "ca-pub-2073744953016040",
    enable_page_level_ads: true
  });
</script>
"""
