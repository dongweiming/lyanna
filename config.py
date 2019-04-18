import os

DB_URL = 'mysql://root:@localhost:3306/test?charset=utf8'
REDIS_URL = 'redis://localhost:6379'
DEBUG = False
WTF_CSRF_SECRET_KEY = 123
AUTH_LOGIN_ENDPOINT = 'index.login'
MEMCACHED_HOST = '127.0.0.1'
MEMCACHED_PORT = 11211

oauth_redirect_path = '/oauth'
redirect_uri = 'http://127.0.0.1:8000/oauth'

client_id = "098a2e6da880878e05da"
client_secret = "854cc0d86e61a83bb1dd00c3b23a3cc5b832d45c"

REACT_PROMPT = '喜欢这篇文章吗? 记得给我留言或订阅哦'
HERE = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(HERE, 'static/upload')
SHOW_PROFILE = False
AUTHOR = 'xiaoming'
SITE_TITLE = 'My Blog'
PER_PAGE = 10
GOOGLE_ANALYTICS = ''
SENTRY_DSN = ''
REQUEST_TIMEOUT = 15

SITE_NAV_MENUS = [('blog.index', '首页'), ('blog.archives', '归档'),
                  ('blog.tags', '标签'), ('index.search', '搜索'),
                  ('index.feed', '订阅'), ('/page/aboutme', '关于我')]
BEIAN_ID = ''
JWT_SECRET = 'lyanna'
EXPIRATION_DELTA = 60 * 60
WTF_CSRF_ENABLED = False

MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USERNAME = ''
MAIL_PASSWORD = ''

BLOG_URL = 'https://example.com'

try:
    from local_settings import *  # noqa
except ImportError:
    pass
