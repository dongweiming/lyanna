import base64
import mimetypes
from pathlib import Path

from sanic import Blueprint, response
from sanic.exceptions import abort
from sanic_jwt import protected
from sanic_jwt.decorators import instant_config
from sanic_jwt.utils import call as jwt_call

from ext import mako
from tortoise.query_utils import Q
from config import PER_PAGE, SHOW_PROFILE
from models import Post, User, Tag, PostTag
from models.user import generate_password
from models.profile import Profile
from forms import UserForm, PostForm, ProfileForm
from views.utils import json

bp = Blueprint('admin', url_prefix='/')
bp.static('img', './static/img')
bp.static('fonts', './static/fonts')


@bp.middleware('request')
async def inject_user(request):
    with instant_config(bp, request=request):
        payload = bp.auth.extract_payload(request, verify=False)
        user = await jwt_call(
            bp.auth.retrieve_user, request, payload
        )
        if user:
            request.user = user


@bp.route('/api/user/info')
@protected(bp)
async def user_info(request):
    profile = await Profile.get()
    avatar = profile.get('avatar')
    data = {
        'name': request.user.name,
        'avatar': (
            request.app.url_for('static', filename=f'upload/{avatar}')
            if avatar else '')
    }
    return response.json(data)


@bp.route('/admin')
@mako.template('admin.html')
async def admin(request):
    return {}


@bp.route('/api/posts')
@protected(bp)
async def list_posts(request):
    limit = int(request.args.get('limit')) or PER_PAGE
    page = int(request.args.get('page')) or 1
    offset = (page - 1) * limit
    _posts = await Post.sync_filter(limit=limit, offset=offset,
                                    orderings='-id')
    total = await Post.filter().count()
    posts = []
    for post in _posts:
        post['author_name'] = post['author'].name
        post['tags'] = [t.name for t in post['tags']]
        posts.append(post)
    return json({'items': posts, 'total': total})


@bp.route('/api/post/new', methods=['POST'])
@protected(bp)
async def new_post(request):
    return await _post(request)


async def _post(request, post_id=None):
    form = PostForm(request)
    form.status.data = int(form.status.data)

    post = None
    if post_id is not None:
        post = await Post.get_or_404(post_id)

    if request.method in ('POST', 'PUT') and form.validate():
        title = form.title.data
        assert str(form.author_id.data).isdigit()
        if post_id is None:
            post = await Post.filter(title=title).first()
        if not post:
            post = Post()
        tags = form.tags.data
        content = form.content.data
        is_page = form.is_page.data
        del form.tags
        del form.content
        del form.is_page
        form.populate_obj(post)
        post.type = Post.TYPE_PAGE if is_page else Post.TYPE_ARTICLE
        await post.save()
        await post.update_tags(tags)
        await post.set_content(content)
        ok = True
    else:
        ok = False
    post = await post.to_sync_dict()
    post['tags'] = [t.name for t in post['tags']]
    return json({'post': post if post else None, 'ok': ok})


@bp.route('/api/post/<post_id>', methods=['GET', 'PUT'])
@protected(bp)
async def post(request, post_id):
    if request.method == 'PUT':
        return await _post(request, post_id=post_id)
    post = await Post.get_or_404(post_id)
    rv = await post.to_sync_dict()
    rv['tags'] = [t.name for t in rv['tags']]
    author = rv['author']
    rv['status'] = str(rv['status'])
    rv['author'] = {'id': author.id, 'name': author.name}
    return json(rv)


@bp.route('/api/users')
@protected(bp)
async def list_users(request):
    users = await User.sync_all()
    total = await User.filter().count()
    return response.json({'items': users, 'total': total})


@bp.route('/api/user/new', methods=['POST'])
@protected(bp)
async def new_user(request):
    return await _user(request)


@bp.route('/api/user/<user_id>', methods=['GET', 'PUT'])
@protected(bp)
async def user(request, user_id):
    if request.method == 'PUT':
        return await _user(request, user_id=user_id)
    user = await User.get_or_404(user_id)
    return response.json(await user.to_sync_dict())


async def _user(request, user_id=None):
    user = None
    form = UserForm(request)

    if user_id is not None:
        user = await User.get_or_404(user_id)

    if request.method in ('POST', 'PUT') and form.validate():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        active = form.active.data
        user = await User.filter(name=name).first()
        if user:
            user.email = email
            if password:
                user.password = generate_password(password)
            user.active = active
            await user.save()
        else:
            user = await User.create(name=name, email=email,
                                     password=password, active=active)
        ok = True
    else:
        ok = False
    return response.json({'user': await user.to_sync_dict()
                          if user else None, 'ok': ok})


@bp.route('/api/upload', methods=['POST', 'OPTIONS'])
async def upload(request):
    file = request.files['avatar'][0]
    avatar_path = file.name
    uploaded_file = Path(request.app.config.UPLOAD_FOLDER) / avatar_path
    with open(uploaded_file, 'wb') as f:
        f.write(file.body)

    mime, _ = mimetypes.guess_type(str(uploaded_file))
    encoded = b''.join(base64.encodestring(file.body).splitlines()).decode()

    return response.json({'files': {'avatar': f'data:{mime};base64,{encoded}'},
                          'avatar_path': avatar_path})


@bp.route('/api/profile', methods=['GET', 'PUT'])
async def profile(request):
    if not SHOW_PROFILE:
        return response.json({'on': False})
    if request.method == 'PUT':
        profile = {'avatar': ''}
        form = ProfileForm(request)
        if form.validate():
            intro = form.intro.data
            avatar = form.avatar.data
            github_url = form.github_url.data
            linkedin_url = form.linkedin_url.data
            profile = {'intro': intro, 'github_url': github_url,
                       'linkedin_url': linkedin_url}
            if avatar:
                profile.update(avatar=avatar)
            await Profile.set(**profile)
        if not profile.get('avatar'):
            try:
                profile['avatar'] = (await Profile.get()).avatar
            except AttributeError:
                ...
    elif request.method == 'GET':
        profile = await Profile.get()

    avatar = profile.get('avatar')
    if avatar:
        profile['avatar_url'] = request.app.url_for(
            'static', filename=f'upload/{avatar}')
    else:
        profile['avatar_url'] = ''
    return response.json({'on': True, 'profile': profile})


@bp.route('/api/post/<post_id>/status', methods=['POST', 'DELETE'])
@protected(bp)
async def status(request, post_id):
    if not post_id:
        abort(404)
    post = await Post.get(id=post_id)
    if not post:
        return response.json({'r': 0, 'msg': 'Post not exist'})
    if request.method == 'POST':
        post.status = Post.STATUS_ONLINE
    elif request.method == 'DELETE':
        post.status = Post.STATUS_UNPUBLISHED
    await post.save()
    return response.json({'r': 1})


@bp.route('/api/post/<post_id>', methods=['DELETE'])
@protected(bp)
async def delete(request, post_id):
    if not post_id:
        abort(404)
    post = await Post.get(id=post_id)
    if not post:
        return response.json({'r': 0, 'msg': 'Post not exist'})
    await post.delete()
    await PostTag.filter(Q(post_id=post_id)).delete()
    return response.json({'r': 1})


@bp.route('/api/user/search')
@protected(bp)
async def user_search(request):
    name = request.args.get('name')

    users = await User.sync_all()
    return response.json({
        'items': [{'id': u.id, 'name': u.name}
                  for u in users if name is None or name in u.name]
    })


@bp.route('/api/tags')
@protected(bp)
async def list_tags(request):
    tags = await Tag.sync_all()
    return response.json({
        'items': [t.name for t in tags]
    })
