from itertools import groupby
from collections import Counter

from sanic import Blueprint
from sanic.exceptions import abort
from tortoise.query_utils import Q

from ext import mako
from config import PER_PAGE
from models.mc import cache
from models.profile import Profile
from models.utils import Pagination
from models.blog import (
    MC_KEY_ARCHIVES, MC_KEY_ARCHIVE, MC_KEY_TAGS, MC_KEY_TAG)
from models import Post, Tag, PostTag

bp = Blueprint('blog', url_prefix='/')


def grouper(item):
    return item.created_at.year


@bp.route('/')
async def index(request):
    return await _posts(request)


@bp.route('/page/<ident>')
async def page(request, ident=1):
    if str(ident).isdigit():
        return await _posts(request, page=int(ident))
    return await _post(request, ident=ident)


@mako.template('index.html')
async def _posts(request, page=1):
    start = (page - 1) * PER_PAGE
    posts = await Post.get_all(with_page=False)
    total = len(posts)
    posts = posts[start: start + PER_PAGE]
    paginatior = Pagination(page, PER_PAGE, total, posts)
    profile = await Profile.get()
    return {'paginatior': paginatior, 'profile': profile}


@bp.route('/post/<ident>')
async def post(request, ident):
    return await _post(request, ident=ident)


@mako.template('post.html')
async def _post(request, ident, is_preview=False):
    post = await Post.get_or_404(ident)
    if not is_preview and post.status != Post.STATUS_ONLINE:
        abort(404)

    github_user = request['session'].get('user')
    stats = await post.stats
    reaction_type = None
    liked_comment_ids = []
    if github_user:
        reaction_type = await post.get_reaction_type(github_user['gid'])
        liked_comment_ids = await post.comment_ids_liked_by(
            github_user['gid'])

    related_posts = await post.get_related()
    post = await post.to_sync_dict()
    return {'post': post, 'github_user': github_user, 'stats': stats,
            'reaction_type': reaction_type, 'related_posts': related_posts,
            'liked_comment_ids': liked_comment_ids}


@bp.route('/post/<ident>/preview')
async def preview(request, ident):
    return await _post(request, ident=ident, is_preview=True)


@bp.route('/archives')
@mako.template('archives.html')
@cache(MC_KEY_ARCHIVES)
async def archives(request):
    rv = {
        year: list(items) for year, items in groupby(
            await Post.filter(Q(status=Post.STATUS_ONLINE)).order_by('-id'),
            grouper)
    }
    archives = sorted(rv.items(), key=lambda x: x[0],
                      reverse=True)
    return {'archives': archives}


@bp.route('/archive/<year>')
@mako.template('archives.html')
@cache(MC_KEY_ARCHIVE % '{year}')
async def archive(request, year):
    posts = await Post.filter(
        Q(status=Post.STATUS_ONLINE),
        Q(created_at__gte=f'{ year }-01-01'),
        Q(created_at__lt=f'{ int(year) + 1 }-01-01')).order_by('-id')
    archives = [(year, posts)]
    return {'archives': archives}


@bp.route('/tags')
@mako.template('tags.html')
@cache(MC_KEY_TAGS)
async def tags(request):
    tag_ids = await PostTag.filter().values_list('tag_id', flat=True)
    counter = Counter(tag_ids)
    tags_ = await Tag.get_multi(counter.keys())
    tags = [(tags_[index], count)
            for index, count in enumerate(counter.values())]
    return {'tags': tags}


@bp.route('/tag/<tag_id>')
@mako.template('tag.html')
@cache(MC_KEY_TAG % '{tag_id}')
async def tag(request, tag_id):
    tag = await Tag.cache(tag_id)
    if not tag:
        abort(404)
    post_ids = await PostTag.filter(tag_id=tag_id).values_list(
        'post_id', flat=True)
    posts = await Post.filter(Q(status=Post.STATUS_ONLINE),
                              Q(id__in=post_ids)).order_by('-id').all()
    return {'tag': tag, 'posts': posts}
