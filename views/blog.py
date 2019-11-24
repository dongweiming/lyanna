import random
from itertools import groupby
from collections import Counter

from sanic import Blueprint
from sanic.exceptions import abort
from tortoise.query_utils import Q

from ext import mako
from config import PER_PAGE, AttrDict, partials
from models.mc import cache
from models.utils import Pagination
from models.blog import (
    MC_KEY_ARCHIVES, MC_KEY_ARCHIVE, MC_KEY_TAGS, MC_KEY_TAG,
    get_most_viewed_posts)
from models.comment import get_latest_comments
from models import Post, Tag, PostTag, SpecialTopic

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
    json = {'paginatior': paginatior}

    for partial in partials:
        partial = AttrDict(partial)
        if partial.name == 'most_viewed':
            json.update({
                'most_viewed_posts': await get_most_viewed_posts(
                    partial.count)
            })
        elif partial.name == 'latest_comments':
            comments = await get_latest_comments(partial.count)
            latest_comments = []
            for c in comments:
                user = await c.user
                post = await Post.cache(c.post_id)
                user = AttrDict({
                    'name': user.username,
                    'link': user.link,
                    'avatar': user.picture,
                })
                post = AttrDict({
                    'title': post.title if post else '[已删除]',
                })
                dct = {
                    'user': user,
                    'post': post,
                    'content': await c.content,
                    'date': c.created_at.strftime('%Y-%m-%d')
                }
                latest_comments.append(AttrDict(dct))
            json.update({'latest_comments': latest_comments})
        elif partial.name == 'tagcloud':
            tags = await _tags()
            random.shuffle(tags)
            json.update({'tags': tags})
    return json


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

    pageview = await post.incr_pageview()
    related_posts = await post.get_related()
    post = await post.to_sync_dict()
    return {'post': post, 'github_user': github_user, 'stats': stats,
            'reaction_type': reaction_type, 'related_posts': related_posts,
            'liked_comment_ids': liked_comment_ids, 'pageview': pageview}


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
    tags = await _tags()
    return {'tags': sorted(tags, key=lambda x: x[1], reverse=True)}


async def _tags():
    tag_ids = await PostTag.filter().values_list('tag_id', flat=True)
    counter = Counter(tag_ids)
    tags_ = await Tag.get_multi(counter.keys())
    return [(tags_[index], count)
            for index, count in enumerate(counter.values())]


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


@bp.route('/topics')
@bp.route('/topics/<ident>')
@mako.template('topics.html')
async def topics(request, ident=1):
    start = (ident - 1) * PER_PAGE
    topics = await SpecialTopic.get_all()
    total = len(topics)
    topics = topics[start: start + PER_PAGE]
    paginatior = Pagination(ident, PER_PAGE, total, topics)
    return {'paginatior': paginatior}


@bp.route('/special/<ident>')
@mako.template('topic.html')
async def topic(request, ident):
    topic = await SpecialTopic.cache(ident)
    posts = await topic.get_post_items()
    return {'topic': topic, 'posts': [await p.to_sync_dict() for p in posts]}
