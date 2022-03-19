import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Optional, Union

import aiohttp
from sanic import Sanic
from sanic.exceptions import FileNotFound, NotFound
from sanic.log import logger
from sanic.response import HTTPResponse, text
from sanic_jwt import Initialize
from sanic_mako import render_string
from sanic_session import AIORedisSessionInterface, Session
from uvloop import Loop
from werkzeug.utils import ImportStringError, find_modules, import_string

import config
from ext import init_db, mako, sentry
from models import User, jwt_authenticate
from models.blog import MC_KEY_SITEMAP, Post, Tag
from models.consts import STATIC_FILE_TYPES
from models.mc import cache
from models.utils import get_redis
from views.request import Request


async def retrieve_user(request: Request, payload: Optional[Any],
                        *args: Any, **kwargs: Any) -> Optional[User]:
    if payload:
        if (user_id := payload.get('user_id', None)) is not None:
            return await User.get_or_404(user_id)


async def store_refresh_token(user_id: int, refresh_token: str,
                              *args, **kwargs) -> None:
    key = f'refresh_token_{user_id}'
    await redis.set(key, refresh_token)  # type: ignore


async def retrieve_refresh_token(user_id: int, *args, **kwargs) -> None:
    key = f'refresh_token_{user_id}'
    return await redis.get(key)  # type: ignore


def register_blueprints(root: str, app: Sanic) -> None:
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
            app.blueprint(mod.bp)


class LyannaSanic(Sanic):
    def url_for(self, view_name: str, **kwargs) -> str:
        url = super().url_for(view_name, **kwargs)
        cdn = config.CDN_DOMAIN
        if cdn and not config.DEBUG and url.split('.')[-1] in STATIC_FILE_TYPES:
            url = f'{cdn}{url}'
        return url


app = LyannaSanic(__name__, request_class=Request)
app.config.update_config(config)
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
async def ignore_404s(request: Request,
                      exception: Union[FileNotFound, NotFound]) -> HTTPResponse:
    return text("Oops, That page couldn't found.")


async def server_error_handler(request, exception):
    return text('Oops, Sanic Server Error! Please contact the blog owner',
                status=500)


@app.listener('before_server_start')
async def setup_db(app: Sanic, loop: Loop) -> None:
    global client, redis
    await init_db()
    redis = await get_redis(loop=loop)
    # init extensions fabrics
    session.init_app(app, interface=AIORedisSessionInterface(redis))
    app.ctx.async_session = aiohttp.ClientSession()
    Path(config.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)


@app.listener('after_server_stop')
async def close_aiohttp_session(sanic_app, _loop) -> None:
    await sanic_app.ctx.async_session.close()


@app.middleware('request')
async def setup_context(request: Request) -> None:
    if config.ENABLE_DEBUG_LOG:
        request.ctx.start_time = time.time()


@app.middleware('response')
async def add_spent_time(request, response):
    if config.ENABLE_DEBUG_LOG:
        spend_time = round((time.time() - request.ctx.start_time) * 1000)
        path = request.path
        if request.query_string:
            path = f'{path}?{request.query_string}'
        logger.info(f'{request.method} {path} {response.status} {spend_time}ms')  # noqa


@cache(MC_KEY_SITEMAP)
async def _sitemap(request):
    ten_days_ago = (datetime.now() - timedelta(days=10)).date().isoformat()
    posts = await Post.get_all()
    tags = await Tag.filter().order_by('-id')
    items: List[List] = []

    for rv in [posts, tags]:
        items.extend([[item.canonical_url, item.created_at] for item in rv])

    for route in app.router.routes:
        uri = route.uri
        if any(endpoint in uri for endpoint in ('/admin', '/j', '/api')):
            continue
        if 'GET' in route.methods and not route._params:
            items.append([uri, ten_days_ago])

    return await render_string('sitemap.xml', request, {'items': items})


@app.route('sitemap.xml')
async def sitemap(request):
    return HTTPResponse(await _sitemap(request), status=200, headers=None,
                        content_type="text/xml")


# app.error_handler.add(Exception, server_error_handler)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=config.DEBUG)
