from datetime import datetime
from urllib.parse import unquote

from sanic import Blueprint, response
from sanic.log import logger
from sanic.response import redirect, text, HTTPResponse
from sanic_mako import render_template
from sanic_oauth.providers import GithubClient, UserInfo
from werkzeug.contrib.atom import AtomFeed

from ext import mako, auth
from forms import LoginForm
from config import AUTHOR, SITE_TITLE
from models.mc import cache
from models.blog import Post, MC_KEY_FEED, MC_KEY_SEARCH
from models.user import validate_login, create_github_user

import config

bp = Blueprint('index', url_prefix='/')


@bp.route('/login', methods=['GET', 'POST'])
async def login(request):
    form = LoginForm(request)
    error = ''
    if request.method == 'POST' and form.validate():
        name = form.name.data
        password = form.password.data
        is_validated, user = await validate_login(name, password)
        if is_validated:
            auth.login_user(request, user)
            return response.redirect(request.app.url_for('admin.index'))
        error = 'Validation failed. Please try again'
    return await render_template('admin/login_user.html', request,
                                 {'form': form, 'error': error})


@bp.route('/logout')
@auth.login_required
async def logout(request):
    auth.logout_user(request)
    return response.redirect(request.app.url_for('index.login'))


@bp.route(config.oauth_redirect_path)
@bp.route(config.oauth_redirect_path + '/post/<post_id>')
async def oauth(request, post_id=None):
    if post_id is None:
        url = '/'
    else:
        url = request.app.url_for('blog.post', ident=post_id)

    user = request['session'].get('user')
    if user:
        return redirect(url)

    client = GithubClient(
        request.app.async_session,
        client_id=config.client_id,
        client_secret=config.client_secret
    )
    if 'error' in request.args:
        return text(request.args.get('error'))

    redirect_uri = config.redirect_uri
    if post_id is not None:
        redirect_uri += f'/post/{post_id}'

    if 'code' not in request.args:
        return redirect(unquote(unquote(client.get_authorize_url(
            scope='email profile', redirect_uri=redirect_uri
        ))))

    token, data = await client.get_access_token(
        request.args.get('code'),
        redirect_uri=redirect_uri
    )

    client = GithubClient(
        request.app.async_session,
        client_id=config.client_id,
        client_secret=config.client_secret,
        access_token=token
    )

    try:
        user, info = await client.user_info()
    except Exception as exc:
        logger.exception(exc)
        return redirect(cfg.oauth_redirect_path)

    user = await create_github_user(user)
    request['session']['user'] = user.to_dict()

    return redirect(url)


@cache(MC_KEY_FEED)
async def _feed(request):
    feed = AtomFeed(title=SITE_TITLE, updated=datetime.now(), feed_url=request.url,
                    url=request.host)
    posts = (await Post.get_all())[:10]
    for post in posts:
        body = post.html_content
        summary = post.excerpt

        feed.add(
            post.title, body, content_type='html', summary=summary,
            summary_type='html', author=AUTHOR, url=post.url,
            id=post.id, updated=post.created_at, published=post.created_at
        )
    return feed.to_string()


@bp.route('atom.xml')
async def feed(request):
    return HTTPResponse(await _feed(request), status=200, headers=None,
                        content_type='text/xml')


@bp.route('/search')
@mako.template('search.html')
async def search(request):
    q = request.args.get('q') or ''
    return {'q': q}


@cache(MC_KEY_SEARCH)
async def _search_json(request):
    posts = await Post.get_all()
    return [{
        'url': post.url,
        'title': post.title,
        'content': post.content
    } for post in posts]


@bp.route('/search.json')
async def search_json(request):
    return response.json(await _search_json(request))
