import distutils.spawn
import os
from pathlib import Path
from typing import List, Tuple

import yaml


class AttrDict(dict):

    def __init__(self, *args, **kwargs) -> None:
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


DB_URL = os.getenv('DB_URL', 'mysql://root:@localhost:3306/test?charset=utf8mb4')  # noqa
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
DEBUG = os.getenv('DEBUG', '').lower() in ('true', 'y', 'yes', '1')
WTF_CSRF_SECRET_KEY = 123
AUTH_LOGIN_ENDPOINT = 'index.login'
MEMCACHED_HOST = os.getenv('MEMCACHED_HOST', '127.0.0.1')
MEMCACHED_PORT = 11211

OAUTH_REDIRECT_PATH = '/oauth'
REDIRECT_URI = 'http://127.0.0.1:8000/oauth'
CLIENT_ID = "098a2e6da880878e05da"
CLIENT_SECRET = "854cc0d86e61a83bb1dd00c3b23a3cc5b832d45c"

REACT_PROMPT = '喜欢这篇文章吗? 记得给我留言或订阅哦'
HERE = Path(__file__).parent.absolute()
UPLOAD_FOLDER = HERE / 'static/upload'
OWNER = 'xiaoming'
SITE_TITLE = 'My Blog'
PER_PAGE = 10
GOOGLE_ANALYTICS = ''
SENTRY_DSN = ''
REQUEST_TIMEOUT = 15
SHOW_PAGEVIEW = False
PERMALINK_TYPE = 'slug'  # 可选 id、slug、title

# [(Endpoint, Name, IconName, Color), ...]
SITE_NAV_MENUS: List[Tuple] = []
BEIAN_ID = ''
JWT_SECRET = 'lyanna'
EXPIRATION_DELTA = 60 * 60
WTF_CSRF_ENABLED = False

MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAKO_STRICT_UNDEFINED = False

BLOG_URL = 'https://example.com'

# Redis sentinel
REDIS_SENTINEL_SERVICE_HOST = None
REDIS_SENTINEL_SERVICE_PORT = 26379

SHOW_AUTHOR = False
COMMENT_REACTIONS = ['heart', 'upvote']

USE_FFMPEG = bool(distutils.spawn.find_executable('ffmpeg'))
CDN_DOMAIN = ''

ACCESS_LOG = True
ENABLE_DEBUG_LOG = False

try:
    from local_settings import *  # noqa
except ImportError:
    ...

try:
    with open(HERE / 'config.yaml') as f:
        config = AttrDict(yaml.safe_load(f))
    partials = config.partials  # type: ignore
    USE_YAML = True
except FileNotFoundError:
    USE_YAML = False
    partials = []
    config = {}  # type: ignore

if USE_YAML:
    for subconfig in [config.common, config.oauth]:  # type: ignore
        globals().update({k.upper(): v for k, v in subconfig.items()})
    globals().update({f'MAIL_{k.upper()}': v for k, v
                      in config.mail.items()})  # type: ignore

if not USE_FFMPEG:
    print('Warning: Cover can be displayed after installing `ffmpeg`')

redis_sentinel_host = os.getenv('REDIS_SENTINEL_SVC_HOST') or REDIS_SENTINEL_SERVICE_HOST  # noqa
if redis_sentinel_host:
    redis_sentinel_port = os.getenv('REDIS_SENTINEL_SVC_PORT',
                                    REDIS_SENTINEL_SERVICE_PORT)
    from redis.sentinel import Sentinel
    sentinel = Sentinel([(redis_sentinel_host, redis_sentinel_port)],
                        socket_timeout=0.1)
    redis_host, redis_port = sentinel.discover_master('mymaster')
    REDIS_URL = f'redis://{redis_host}:{redis_port}'
