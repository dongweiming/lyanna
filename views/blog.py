import random
from collections import Counter
from itertools import groupby
from typing import Dict, List, Tuple, Union

from sanic import Blueprint
from sanic.exceptions import abort
from tortoise.query_utils import Q

from config import PER_PAGE, AttrDict, partials
from ext import mako
from models import Post, PostTag, SpecialTopic, Tag
from models.blog import (MC_KEY_ARCHIVE, MC_KEY_ARCHIVES, MC_KEY_TAG,
                         MC_KEY_TAGS, get_most_viewed_posts)
from models.comment import get_latest_comments
from models.mc import cache
from models.utils import Pagination
from views.request import Request

bp = Blueprint('blog', url_prefix='/')


def grouper(item: Post) -> int:
    return item.created_at.year


@bp.route('/')
async def index(request: Request):
    return await _posts(request)


@bp.route('/page/<ident>')
async def page(request: Request, ident: Union[str, int] = 1):
    if str(ident).isdigit():
        return await _posts(request, page=int(ident))
    return await _post(request, ident=ident)


@mako.template('index.html')
async def _posts(request: Request, page: int = 1):
    paginatior = await Post.paginate(page, PER_PAGE)
    json: Dict[
        str, Union[List[Tuple[int, Post]], List[AttrDict],
                   List[Tuple[Tag, int]], Pagination]] = {'paginatior': paginatior}

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
                post = await Post.cache(c.target_id)
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
async def post(request: Request, ident: str):
    return await _post(request, ident=ident)


@mako.template('post.html')
async def _post(request: Request, ident: str, is_preview: bool = False):
    post = await Post.get_or_404(ident)
    if not is_preview and post.status != Post.STATUS_ONLINE:
        abort(404)

    github_user = request.ctx.session.get('user')
    stats = await post.stats
    reaction_type = None
    reacted_comments: List[List[int]] = []
    if github_user:
        reaction_type = await post.get_reaction_type(github_user['gid'])
        reacted_comments = await post.comments_reacted_by(github_user['gid'])

    pageview = await post.incr_pageview()
    related_posts = await post.get_related()
    post = await post.to_sync_dict()
    return {'post': post, 'github_user': github_user, 'stats': stats,
            'reaction_type': reaction_type, 'related_posts': related_posts,
            'reacted_comments': reacted_comments, 'pageview': pageview}


@bp.route('/post/<ident>/preview')
async def preview(request, ident):
    return await _post(request, ident=ident, is_preview=True)


@bp.route('/archives')
@mako.template('archives.html')
@cache(MC_KEY_ARCHIVES)
async def archives(request: Request) -> Dict[str, List[Tuple[int, List[Post]]]]:
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
async def tags(request: Request) -> Dict[str, List[Tuple[Tag, int]]]:
    tags = await _tags()
    return {'tags': sorted(tags, key=lambda x: x[1], reverse=True)}


async def _tags() -> List[Tuple[Tag, int]]:
    tag_ids = await PostTag.filter().values_list('tag_id', flat=True)
    counter = Counter(tag_ids)
    tags_ = await Tag.get_multi(counter.keys())
    return [(tags_[index], count)
            for index, count in enumerate(counter.values())]


@bp.route('/tag/<tag_id>')
@mako.template('tag.html')
@cache(MC_KEY_TAG % '{tag_id}')
async def tag(request, tag_id):
    if not (tag := await Tag.cache(tag_id)):
        abort(404)
    post_ids = await PostTag.filter(tag_id=tag_id).values_list(
        'post_id', flat=True)
    posts = await Post.filter(Q(status=Post.STATUS_ONLINE),
                              Q(id__in=post_ids)).order_by('-id').all()
    return {'tag': tag, 'posts': posts}


@bp.route('/topics')
@bp.route('/topics/<ident>')
@mako.template('topics.html')
async def topics(request: Request, ident_: str = "1") -> Dict[str, Pagination]:
    try:
        ident = int(ident_)
    except ValueError:
        abort(404)
    start = (ident - 1) * PER_PAGE
    topics = await SpecialTopic.get_all()
    total = len(topics)
    topics = topics[start: start + PER_PAGE]
    paginatior = Pagination(ident, PER_PAGE, total, topics)
    return {'paginatior': paginatior}


@bp.route('/special/<ident>')
@mako.template('topic.html')
async def topic(request: Request, ident: str):
    topic = await SpecialTopic.cache(ident)
    posts = await topic.get_post_items()  # type: ignore
    return {'topic': topic, 'posts': [await p.to_sync_dict() for p in posts]}


@bp.route('/activities')
@mako.template('activities.html')
async def activities(request: Request):
    return {}
