import os

DB_URL = os.getenv('DB_URL', 'mysql://root:@localhost:3306/test?charset=utf8')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
DEBUG = os.getenv('DEBUG', '').lower() in ('true', 'y', 'yes', '1')
WTF_CSRF_SECRET_KEY = 123
AUTH_LOGIN_ENDPOINT = 'index.login'
MEMCACHED_HOST = os.getenv('MEMCACHED_HOST', '127.0.0.1')
MEMCACHED_PORT = 11211

oauth_redirect_path = '/oauth'
redirect_uri = 'http://127.0.0.1:8000/oauth'

client_id = "098a2e6da880878e05da"
client_secret = "854cc0d86e61a83bb1dd00c3b23a3cc5b832d45c"

REACT_PROMPT = '喜欢这篇文章吗? 记得给我留言或订阅哦'
HERE = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(HERE, 'static/upload')
AUTHOR = 'xiaoming'
SITE_TITLE = 'My Blog'
PER_PAGE = 10
GOOGLE_ANALYTICS = ''
SENTRY_DSN = ''
REQUEST_TIMEOUT = 15
SHOW_PAGEVIEW = False
PERMALINK_TYPE = 'slug'  # 可选 id、slug、title

# [(Endpoint, Name, IconName, Color), ...]
SITE_NAV_MENUS = [('blog.index', '首页'), ('blog.topics', '专题'),
                  ('blog.archives', '归档'), ('blog.tags', '标签'),
                  ('index.search', '搜索'), ('/page/aboutme', '关于我'),
                  ('index.feed', 'RSS', 'rss', '#fc6423')]
BEIAN_ID = ''
JWT_SECRET = 'lyanna'
EXPIRATION_DELTA = 60 * 60
WTF_CSRF_ENABLED = False

MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USERNAME = ''
MAIL_PASSWORD = ''

BLOG_URL = 'https://example.com'

# Redis sentinel
REDIS_SENTINEL_SERVICE_HOST = None
REDIS_SENTINEL_SERVICE_PORT = 26379

# AboutMe
INTRO = ''
AVATAR = ''  # 'upload/me.jpg' (= /static/upload/me.jpg)
# Social
# twitter/github/douban/linkedin/instagram/stack-overflow/medium/zhihu/email/wechat/weixingongzhonghao
# you can choose someone to display, the recommend number is 8 icons.
SHOW_PROFILE = []  # e.g. [('twitter', 'example'), ('wechat', 'static/upload/qrcode.jpg')]

try:
    from local_settings import *  # noqa
except ImportError:
    pass

redis_sentinel_host = os.getenv('REDIS_SENTINEL_SVC_HOST') or REDIS_SENTINEL_SERVICE_HOST  # noqa
if redis_sentinel_host:
    redis_sentinel_port = os.getenv('REDIS_SENTINEL_SVC_PORT',
                                    REDIS_SENTINEL_SERVICE_PORT)
    from redis.sentinel import Sentinel
    sentinel = Sentinel([(redis_sentinel_host, redis_sentinel_port)],
                        socket_timeout=0.1)
    redis_host, redis_port = sentinel.discover_master('mymaster')
    REDIS_URL = f'redis://{redis_host}:{redis_port}'
