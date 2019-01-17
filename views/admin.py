from pathlib import Path

from sanic import Blueprint
from sanic_mako import render_template

from ext import mako, auth
from config import UPLOAD_FOLDER, PER_PAGE
from models import Post, User, create_user, Tag
from models.utils import Pagination
from models.user import generate_password
from models.profile import get_profile, set_profile
from forms import UserForm, PostForm, ProfileForm

bp = Blueprint('admin', url_prefix='/admin')


@bp.route('/')
@auth.login_required
@mako.template('admin/index.html')
async def index(request):
    return {}


@bp.route('/posts/<page>')
@bp.route('/posts')
@auth.login_required
@mako.template('admin/list_posts.html')
async def list_posts(request, page=1):
    return await _get_post_context(page)


async def _get_post_context(page=1):
    page = int(page)
    start = (page - 1) * PER_PAGE
    posts = await Post.get_all()
    total = len(posts)
    posts = posts[start: start + PER_PAGE]
    paginatior = Pagination(page, PER_PAGE, total, posts)
    return {'paginatior': paginatior, 'total': total, 'msg': '', 'page': page}


@bp.route('/posts/new', methods=['GET', 'POST'])
@auth.login_required
async def new_post(request):
    return await _post(request)


async def _post(request, post_id=None):
    form = PostForm(request)
    msg = ''

    if post_id is not None:
        post = await Post.get_or_404(post_id, sync=True)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        assert str(form.author_id.data).isdigit()
        post = await Post.filter(title=title).first()
        if post:
            await post.save()
            msg = 'Post was successfully updated.'
        else:
            post = Post()
            msg = 'Post was successfully created.'
        form.status.data = form.status.data == 'on'
        tags = form.tags.data
        content = form.content.data
        is_page = form.is_page.data
        del form.tags
        del form.content
        del form.is_page
        form.populate_obj(post)
        if is_page:
            post.type = Post.TYPE_PAGE
        await post.save()
        await post.update_tags(tags)
        await post.set_content(content)
        context = await _get_post_context()
        return await render_template('admin/list_posts.html', request, context)
    elif post_id is not None:
        form = PostForm(request, obj=post)
        form.tags.data = [tag.name for tag in post.tags]
        form.can_comment.data = post.can_comment
        form.is_page.data = post.is_page
        form.status.data = 'on' if post.status else 'off'
        form.submit.label.text = 'Update'

    tags = await Tag.all()
    authors = await User.all()
    return await render_template('admin/post.html', request,
                                 {'form': form, 'msg': msg, 'post_id': post_id,
                                  'tags': tags, 'authors': authors})


@bp.route('/post/<post_id>/edit', methods=['GET', 'POST'])
@auth.login_required
async def edit_post(request, post_id=None):
    return await _post(request, post_id=post_id)


@bp.route('/users')
@auth.login_required
@mako.template('admin/list_users.html')
async def list_users(request):
    users = await User.all()
    total = await User.filter().count()
    return {'users': users, 'total': total, 'msg': ''}


@bp.route('/users/new', methods=['GET', 'POST'])
@auth.login_required
async def new_user(request):
    return await _user(request)


async def _user(request, user_id=None):
    form = UserForm(request)
    msg = ''

    if user_id is not None:
        user = await User.get_or_404(user_id)

    if request.method == 'POST' and form.validate():
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
            msg = 'User was successfully updated.'
        else:
            user = await User.create(name=name, email=email,
                                     password=password, active=active)
            msg = 'User was successfully created.'
        users = await User.all()
        total = await User.filter().count()
        context = {'users': users, 'total': total, 'msg': msg}
        return await render_template('admin/list_users.html', request, context)
    elif user_id is not None:
        form = UserForm(request, obj=user)
        form.password.data = ''
        form.active.data = user.active
        form.submit.label.text = 'Update'
    return await render_template('admin/user.html', request,
                                 {'form': form, 'msg': msg,
                                  'user_id': user_id})


@bp.route('/user/<user_id>/edit', methods=['GET', 'POST'])
@auth.login_required
async def edit_user(request, user_id=None):
    return await _user(request, user_id=user_id)


@bp.route('/profile', methods=['GET', 'POST'])
@auth.login_required
@mako.template('admin/profile.html')
async def profile(request):
    form = ProfileForm(request)
    if request.method == 'POST':
        avatar_path = ''
        if form.validate():
            image = form.avatar.data
            intro = form.intro.data
            github_url = form.github_url.data
            linkedin_url = form.linkedin_url.data
            avatar_path = image.name
            uploaded_file = Path(
                request.app.config.UPLOAD_FOLDER) / avatar_path
            uploaded_file.write_bytes(image.body)
            form.avatar_path.data = avatar_path
            kw = {'intro': intro, 'github_url': github_url,
                  'linkedin_url': linkedin_url}
            if avatar_path:
                kw.update(avatar=avatar_path)
            await set_profile(**kw)
        if not avatar_path:
            form.avatar_path.data = (await get_profile()).avatar
    elif request.method == 'GET':
        profile = await get_profile()
        form.intro.data = profile.intro
        form.github_url.data = profile.github_url
        form.linkedin_url.data = profile.linkedin_url
        form.avatar_path.data = profile.avatar

    return {'form': form}
