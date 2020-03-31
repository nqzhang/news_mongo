import os
from views import static

BASE_DIR = os.path.dirname(__file__)

is_debug=True
env = 'dev'
if env == 'dev':
    mongo = {
        "url": "mongodb://admin:11QQqqWW@192.168.11.128",
        "urlbak": "mongodb://95.216.6.102:27016",
        "db_name": "news"
    }
    redis_cache = {
        "host": "192.168.11.128",
        "port": 6379,
        "db": 1
    }
    redis = {
        "host": "192.168.11.128",
        "port": 6379,
        "db": 0,
    }
elif env == 'test':
    redis_cache = {
        "host": "176.9.3.102",
        "port": 6379,
        "db": 1
    }
    redis = {
        "host": "176.9.3.102",
        "port": 6379,
        "db": 0,
    }
    mongo = {
        "url": "mongodb://195.201.197.26:27016",
        "urlbak": "mongodb://95.216.6.102:27016",
        "db_name": "www_smwenku_com"
    }
elif env == 'production':
    redis_cache = {
        "host": "176.9.3.102",
        "port": 6379,
        "db": 1
    }
    redis = {
        "host": "176.9.3.102",
        "port": 6379,
        "db": 0,
    }
    mongo = {
        "url": "mongodb://195.201.197.26:27016",
        "urlbak": "mongodb://95.216.6.102:27016",
        "db_name": "www_smwenku_com"
    }
    is_debug = False
settings = {
    "static_path": os.path.join(BASE_DIR, 'static'),
    "static_handler_class": static.StaticFileHandler,
    "template_path": os.path.join(BASE_DIR, 'template'),
    "debug": is_debug,
    "autoreload": False,
    "compress_response": True,
    # "compiled_template_cache": False,
    # "static_hash_cache": False,
    # "serve_traceback": True,
    "cookie_secret": "E2PHKvHUSPeNMz9UgxB2PFaQGi616EAltl7KnSJvH+0=",
    # base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
    "xsrf_cookies": True,
    "login_url": '/?login=1',
}


if env == 'dev':
    site_domain = 'http://127.0.0.1:48000'
elif env == 'production':
    site_domain = 'https://www.twblogs.net'
elif env == 'test':
    site_domain = 'https://test.smwenku.com'

redis_cache_ttl = 600
session_ttl = 30 * 24 * 60 * 60
articles_per_page = 15
hot_news_num = 10
smtp_hostname = 'mail.smwenku.com'
smtp_login = 'postmaster@smwenku.com'
smtp_pass = '11QQqqWW'

custom_meta = """<meta name="google-site-verification" content="QSl8rlXGYak0SPdlX0r_tMqD7I6XFuWD1JxR_D9PbyM" />
                <meta name="msvalidate.01" content="4775F105590951C69208A1E849EF0F32" />"""
analytics_code = """
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-135472877-1"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'UA-135472877-1');
    </script>"""
adsense_code = """<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
        <!--
        <script>
            (adsbygoogle = window.adsbygoogle || []).push({
                google_ad_client: "ca-pub-3219336841483159",
                enable_page_level_ads: false
                    });
        </script>
        -->
        <!-- Google Tag Manager -->
        <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
        new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer','GTM-WV8L3BL');</script>
        <!-- End Google Tag Manager -->
        """
