import base64
import copy
import mimetypes
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Optional, Union

import aiohttp
import extraction
from sanic import Blueprint, response
from sanic.response import HTTPResponse
from sanic_jwt import protected
from sanic_jwt.decorators import instant_config
from sanic_jwt.utils import call as jwt_call
from tortoise.expressions import Q

from config import PER_PAGE, UPLOAD_FOLDER, USE_FFMPEG
from ext import mako
from forms import PostForm, TopicForm, UserForm
from models import Post, PostTag, SpecialTopic, Tag, User
from models.activity import Activity, create_status
from models.consts import K_POST
from models.signals import post_created
from models.user import generate_password
from models.utils import generate_id
from views.request import Request
from views.utils import json, abort

FORM_REGEX = re.compile(r'posts\[(?P<index>\d+)\]\[(?P<key>\w+)\]')  # noqa

bp = Blueprint('admin', url_prefix='/')
bp.static('img', './static/img')
bp.static('fonts', './static/fonts')


@bp.middleware('request')
async def inject_user(request: Request) -> None:
    with instant_config(bp, request=request):
        payload = await bp.ctx.auth.extract_payload(request, verify=False)
        user = await jwt_call(
            bp.ctx.auth.retrieve_user, request, payload
        )
        if user:
            request.user = user


@bp.route('/admin')
@mako.template('admin.html')
async def admin(request: Request) -> Dict:
    return {}


@bp.route('/api/posts')
@protected(bp)
async def list_posts(request: Request):
    user = request.user
    if not user:
        return json({'ok': False, 'msg': 'Need Login'}, status=401)
    limit = int(request.args.get('limit')) or PER_PAGE
    page = int(request.args.get('page')) or 1
    with_tag = int(request.args.get('with_tag') or 0)
    offset = (page - 1) * limit
    _posts = await Post.filter(author_id=user.id).order_by('-id').offset(
        offset).limit(limit)
    total = await Post.filter(author_id=user.id).count()
    posts = []
    exclude_ids: List[int] = []
    if (special_id := int(request.args.get('special_id') or 0)):
        if (topic := await SpecialTopic.cache(special_id)):
            items = await topic.get_items()
            exclude_ids = [s.post_id for s in items]
        total -= len(exclude_ids)
    for post in _posts:
        dct = post.to_dict()
        if post.id in exclude_ids:
            continue
        if with_tag:
            author = await post.author
            dct['author_name'] = author.name
            tags = await post.tags
            dct['tags'] = [t.name for t in tags]  # type: ignore
        posts.append(dct)
    return json({'items': posts, 'total': total})


@bp.route('/api/post/new', methods=['POST'])
@protected(bp)
async def new_post(request: Request):
    return await _post(request)


async def _post(request: Request, post_id: Optional[Any] = None):
    user = request.user
    if not user:
        return json({'ok': False, 'msg': 'Need Login'}, status=401)
    form = PostForm(request)
    form.status.data = int(form.status.data)

    post = None
    if post_id is not None:
        post = await Post.get_or_404(post_id)

    if request.method in ('POST', 'PUT') and form.validate():
        title = form.title.data
        if post_id is None:
            post = await Post.filter(title=title).first()
        if not post:
            is_new = True
            post = Post()
        else:
            is_new = False
        tags = form.tags.data
        content = form.content.data
        is_page = form.is_page.data
        del form.tags
        del form.content
        del form.is_page
        form.populate_obj(post)
        post.type = Post.TYPE_PAGE if is_page else Post.TYPE_ARTICLE
        post.author_id = user.id
        await post.save()
        await post.update_tags(tags)
        await post.set_content(content)
        if is_new:
            post_created.send(post_id=post.id, user_id=post.author_id)
        ok = True
    else:
        ok = False
        if (err := raise_error(form.errors)):
            return json({'ok': ok, 'msg': err}, status=400)
    post = await post.to_sync_dict()  # type: ignore
    post['tags'] = [t.name for t in post['tags']]
    return json({'post': post if post else None, 'ok': ok})


def raise_error(errors):
    if errors:
        for k, items in errors.items():
            for i in items:
                return f'{k}: {i}'


@bp.route('/api/post/<post_id>', methods=['GET', 'PUT', 'DELETE'])
@protected(bp)
async def post(request, post_id):
    if request.method == 'PUT':
        return await _post(request, post_id=post_id)

    post = await Post.get_or_404(id=post_id)
    if not (post := await Post.get_or_404(id=post_id)):
        return response.json({'r': 0, 'msg': 'Post not exist'})

    if request.method == 'DELETE':
        await post.delete()
        await PostTag.filter(Q(post_id=post_id)).delete()
        activity = await Activity.filter(target_id=post_id, target_kind=K_POST).first()
        if activity:
            await activity.delete()
        return response.json({'r': 1})

    rv = await post.to_sync_dict()
    rv['tags'] = [t.name for t in rv['tags']]
    author = rv['author']
    rv['status'] = str(rv['status'])
    rv['author'] = {'id': author.id, 'name': author.name}
    return json(rv)


@bp.route('/api/users')
@protected(bp)
async def list_users(request: Request) -> HTTPResponse:
    users = await User.sync_all()
    total = await User.filter().count()
    return json({'items': users, 'total': total})


@bp.route('/api/user/new', methods=['POST'])
@protected(bp)
async def new_user(request: Request):
    return await _user(request)


@bp.route('/api/user/<user_id>', methods=['GET', 'PUT'])
@protected(bp)
async def user(request, user_id):
    if request.method == 'PUT':
        return await _user(request, user_id=user_id)
    user = await User.get_or_404(user_id)
    user = await user.to_sync_dict()
    avatar = user.avatar
    user['avatar_url'] = (request.app.url_for('static', filename=f'upload/{avatar}')  # noqa
                          if avatar else '')
    return json(user)


async def _user(request: Request, user_id: Optional[Any] = None):
    user = None
    form = UserForm(request)

    if user_id is not None:
        user = await User.get_or_404(user_id)

    if request.method in ('POST', 'PUT') and form.validate():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        active = form.active.data
        avatar = form.avatar.data
        if (user := await User.filter(name=name).first()):
            user.email = email
            if password:
                user.password = generate_password(password)  # type: ignore
            user.avatar = avatar
            user.active = active
            await user.save()
        else:
            password = generate_password(password)
            user = await User.create(name=name, email=email, avatar=avatar,
                                     password=password, active=active)
        ok = True
    else:
        ok = False

    return json({'user': await user.to_sync_dict(), 'ok': ok})  # type: ignore


@bp.route('/api/upload', methods=['POST', 'OPTIONS'])
async def upload(request):
    try:
        file = request.files['avatar'][0]
        is_avatar = True
    except KeyError:
        file = request.files['file'][0]
        is_avatar = False
    suffix = file.name.split(".")[-1]
    fid = generate_id()
    filename = f'{fid}.{suffix}'
    uploaded_file = Path(UPLOAD_FOLDER) / filename
    with open(uploaded_file, 'wb') as f:
        f.write(file.body)

    mime, _ = mimetypes.guess_type(str(uploaded_file))
    encoded = b''.join(base64.encodebytes(file.body).splitlines()).decode()

    dct: Dict[str, Union[Dict, int, str]]

    if is_avatar:
        dct = {
            'files': {
                'avatar': f'data:{mime};base64,{encoded}', 'avatar_path': filename
            }
        }
    else:
        if USE_FFMPEG and suffix == 'mp4':
            subprocess.call(
                f'ffmpeg -loglevel error -y -i {uploaded_file} -qscale:v 1 -qmin 1 -qmax 1 -frames:v 1 {Path(UPLOAD_FOLDER) / fid}.png', shell=True)  # noqa

        dct = {'r': 0, 'filename': filename}

    return json(dct)


@bp.route('/api/<target_kind>/<target_id>/status', methods=['POST', 'DELETE'])
@protected(bp)
async def status(request, target_kind, target_id):
    if not target_id:
        abort(404)
    kls = Post if target_kind == 'post' else SpecialTopic
    if not (obj := await kls.get(id=target_id)):
        return response.json({'r': 0, 'msg': 'item not exist'})
    if request.method == 'POST':
        obj.status = kls.STATUS_ONLINE  # type: ignore
    elif request.method == 'DELETE':
        obj.status = kls.STATUS_UNPUBLISHED  # type: ignore
    await obj.save()
    return response.json({'r': 1})


@bp.route('/api/user/search')
@protected(bp)
async def user_search(request: Request) -> HTTPResponse:
    name = request.args.get('name')

    users = await User.sync_all()
    return response.json({
        'items': [{'id': u.id, 'name': u.name}
                  for u in users if name is None or name in u.name]
    })


@bp.route('/api/tags')
@protected(bp)
async def list_tags(request: Request) -> HTTPResponse:
    tags = await Tag.sync_all()
    return response.json({
        'items': [t.name for t in tags]
    })


@bp.route('/api/topics')
@protected(bp)
async def list_topics(request: Request) -> HTTPResponse:
    topics = await SpecialTopic.sync_all()
    total = len(topics)
    return json({'items': topics, 'total': total})


@bp.route('/api/topic/new', methods=['POST'])
@protected(bp)
async def new_topic(request: Request):
    return await _topic(request)


@bp.route('/api/topic/<topic_id>', methods=['GET', 'PUT'])
@protected(bp)
async def topic(request, topic_id):
    if request.method == 'PUT':
        return await _topic(request, topic_id=topic_id)
    topic = await SpecialTopic.get_or_404(topic_id)
    topic = await topic.to_sync_dict()
    topic['status'] = str(topic['status'])
    return json(topic)


async def _topic(request: Request, topic_id: Optional[Any] = None):
    form = TopicForm(request)
    form.status.data = int(form.status.data)

    topic = None
    if topic_id is not None:
        topic = await SpecialTopic.get_or_404(topic_id)

    if request.method in ('POST', 'PUT') and form.validate():
        dct: DefaultDict[str, Dict[str, int]] = defaultdict(dict)
        for k in copy.copy(request.form):
            if k.startswith('posts'):
                match = FORM_REGEX.search(k)
                if (match := FORM_REGEX.search(k)):
                    key = match['key']
                    val = request.form[k][0]
                    dct[match['index']][key] = (
                        int(val) if key == 'id' else val)
                    del request.form[k]

        title = form.title.data
        if topic_id is None:
            topic = await SpecialTopic.filter(title=title).first()
        if not topic:
            topic = SpecialTopic()

        form.populate_obj(topic)
        if dct:
            indexes = [
                (i['id'], int(index))
                for index, i in sorted(dct.items(), key=lambda i: i[0])
            ]
        else:
            indexes = []
        if topic_id is not None:
            await topic.set_indexes(indexes)
        await topic.save()
        if topic_id is None:
            await topic.set_indexes(indexes)
        ok = True
    else:
        ok = False
    topic = await topic.to_sync_dict()  # type: ignore
    return json({'topic': topic if topic else None, 'ok': ok})


@bp.route('/api/user/info')
@protected(bp)
async def user_info(request: Request) -> HTTPResponse:
    user = request.user
    avatar = user.avatar
    data = {
        'name': user.name,
        'avatar': (
            request.app.url_for('static', filename=f'upload/{avatar}')
            if avatar else '')
    }
    return response.json(data)


@bp.route('/api/get_url_info', methods=['POST'])
@protected(bp)
async def get_url_info(request):
    if not (url := request.json.get('url')):
        return json({'r': 403, 'msg': 'URL required'})

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                try:
                    html = await resp.text()
                except Exception:
                    html = resp._body.decode('utf-8')
        except Exception:
            html = ''
    if not html:
        return json({'r': 1, 'msg': '这个网址无法识别'})
    extracted = extraction.Extractor().extract(html, source_url=url)
    return json({
        'ok': 0,
        'info': {
            'title': extracted.title,
            'url': extracted.url or url,
            'abstract': extracted.description
        }
    })


@bp.route('/api/status', methods=['POST'])
@protected(bp)
async def api_status(request):
    user_id = request.user.id
    obj, msg = await create_status(user_id, request.json)
    activity = None if not obj else await obj.to_full_dict()  # type: ignore
    return json({'r': not bool(obj), 'msg': msg, 'activity': activity})
