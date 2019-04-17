import aiohttp
import asyncio
import aioredis
from pathlib import Path
from datetime import datetime, timedelta

import aiomcache
from sanic import Sanic
from sanic.request import Request as _Request
from sanic.exceptions import NotFound
from sanic.response import HTTPResponse, text
from sanic_mako import render_string
from sanic_jwt import Initialize
from sanic_session import Session, MemcacheSessionInterface

import config
from ext import mako, init_db, sentry
from models.mc import cache
from models import jwt_authenticate, User
from models.var import redis_var, memcache_var
from models.blog import Post, Tag, MC_KEY_SITEMAP

from werkzeug.utils import find_modules, import_string, ImportStringError


async def retrieve_user(request, payload, *args, **kwargs):
    if payload:
        user_id = payload.get('user_id', None)
        if user_id is None:
            return
        return await User.get_or_404(user_id)


async def store_refresh_token(user_id, refresh_token, *args, **kwargs):
    key = f'refresh_token_{user_id}'
    await redis.set(key, refresh_token)


async def retrieve_refresh_token(user_id, *args, **kwargs):
    key = f'refresh_token_{user_id}'
    return await redis.get(key)


def register_blueprints(root, app):
    for name in find_modules(root, recursive=True):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            if mod.bp.name == 'admin':
                Initialize(mod.bp, app=app, authenticate=jwt_authenticate,
                           retrieve_user=retrieve_user,
                           store_refresh_token=store_refresh_token,
                           retrieve_refresh_token=retrieve_refresh_token,
                           secret=config.JWT_SECRET,
                           expiration_delta=config.EXPIRATION_DELTA)
            app.register_blueprint(mod.bp)


class Request(_Request):
    user = None


app = Sanic(__name__, request_class=Request)
app.config.from_object(config)
mako.init_app(app, context_processors=())
if sentry is not None:
    sentry.init_app(app)
register_blueprints('views', app)
try:
    register_blueprints('custom', app)
except ImportStringError:
    ...
app.static('/static', './static')

session = Session()
client = None
redis = None


@app.exception(NotFound)
async def ignore_404s(request, exception):
    return text("Oops, That page couldn't found.")


async def server_error_handler(request, exception):
    return text('Oops, Sanic Server Error! Please contact the blog owner',
                status=500)


@app.listener('before_server_start')
async def setup_db(app, loop):
    global client
    await init_db()
    client = aiomcache.Client(config.MEMCACHED_HOST, config.MEMCACHED_PORT, loop=loop)  # noqa
    session.init_app(app, interface=MemcacheSessionInterface(client))
    app.async_session = aiohttp.ClientSession()
    Path(config.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)


@app.listener('after_server_stop')
async def close_aiohttp_session(sanic_app, _loop) -> None:
    await sanic_app.async_session.close()


@app.middleware('request')
async def setup_context(request):
    global redis
    loop = asyncio.get_event_loop()
    if redis is None:
        redis = await aioredis.create_redis_pool(
            config.REDIS_URL, minsize=5, maxsize=20, loop=loop)
    redis_var.set(redis)
    memcache_var.set(client)


@cache(MC_KEY_SITEMAP)
async def _sitemap(request):
    ten_days_ago = (datetime.now() - timedelta(days=10)).date().isoformat()
    posts = await Post.get_all()
    tags = await Tag.filter().order_by('-id')
    items = []

    for rv in [posts, tags]:
        items.extend([(item.url, item.created_at) for item in rv])

    for _, route in app.router.routes_names.values():
        if any(endpoint in route.uri for endpoint in ('/admin', '/j', '/api')):
            continue
        if 'GET' in route.methods and not route.parameters:
            items.append([route.uri, ten_days_ago])

    return await render_string('sitemap.xml', request, {'items': items})


@app.route('sitemap.xml')
async def sitemap(request):
    return HTTPResponse(await _sitemap(request), status=200, headers=None,
                        content_type="text/xml")


# app.error_handler.add(Exception, server_error_handler)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=config.DEBUG)
