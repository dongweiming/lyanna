from typing import Callable, List

import aiohttp
import mistune
import extraction
from sanic import Blueprint
from sanic.response import json
from sanic_mako import render_template_def

from models import Comment, Post, ReactItem

bp = Blueprint('j', url_prefix='/j')


def login_required(f: Callable) -> Callable:
    async def wrapped(request, **kwargs):
        if not (user := request['session'].get('user')):
            return json({'r': 403, 'msg': 'Login required.'})
        if (post_id := kwargs.pop('post_id', None)) is not None:
            if not (post := await Post.cache(post_id)):
                return json({'r': 1, 'msg': 'Post not exist'})
            args = (user, post)
        else:
            args = (user,)  # type: ignore
        return await f(request, *args, **kwargs)
    return wrapped


@bp.route('/post/<post_id>/comment', methods=['POST'])
@login_required
async def create_comment(request, user, post):
    if not (content := request.form.get('content')):
        return json({'r': 1, 'msg': 'Comment content required.'})
    ref_id = int(request.form.get('ref_id', 0))
    comment = await post.add_comment(user['gid'], content, ref_id)
    reacted_comments = await post.comments_reacted_by(user['gid'])
    comment = await comment.to_sync_dict()

    return json({
        'r': 0 if comment else 1,
        'html': await render_template_def(
            'utils.html', 'render_single_comment', request,
            {'comment': comment, 'github_user': user,
             'reacted_comments': reacted_comments})
    })


@bp.route('/post/<post_id>/comments')
async def comments(request, post_id):
    post = await Post.cache(post_id)
    if not (post := await Post.cache(post_id)):
        return json({'r': 1, 'msg': 'Post not exist'})

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    start = (page - 1) * per_page
    comments = (await post.comments)[start: start + per_page]

    reacted_comments: List[List[int]] = []
    if (user := request['session'].get('user')):
        reacted_comments = await post.comments_reacted_by(user['gid'])

    return json({
        'r': 0,
        'html': await render_template_def(
            'utils.html', 'render_comments', request,
            {'comments': comments, 'github_user': user,
             'reacted_comments': reacted_comments})
    })


@bp.route('/markdown', methods=['POST'])
@login_required
async def render_markdown(request, user):
    if not (text := request.form.get('text')):
        return json({'r': 1, 'msg': 'Text required.'})
    return json({'r': 0, 'text':  mistune.markdown(text)})


@bp.route('/post/<post_id>/react', methods=['POST', 'DELETE'])
@login_required
async def react(request, user, post):
    if request.method == 'POST':
        reaction_type = request.form.get('reaction_type', None)
        if reaction_type is None:
            return json({'r': 1, 'msg': 'Reaction type error.'})
        rv = await post.add_reaction(user['gid'], reaction_type)
    elif request.method == 'DELETE':
        rv = await post.cancel_reaction(user['gid'])

    stats = await post.stats
    reaction_type = None

    if user:
        reaction_type = await post.get_reaction_type(user['gid'])
    return json({'r': int(not rv),
                 'html': await render_template_def(
        'utils.html', 'render_react_container', request,
                      {'stats': stats, 'reaction_type': reaction_type})
                 })


@bp.route('/comment/<comment_id>/react', methods=['POST', 'DELETE'])
async def comment_react(request, comment_id):
    user = request['session'].get('user')
    if not user:
        return json({'r': 403, 'msg': 'Login required'})
    if not (comment := await Comment.cache(comment_id)):
        return json({'r': 404, 'msg': 'Comment not exist'})

    reaction_type = int(request.form.get('reaction_type', ReactItem.K_LOVE))
    if reaction_type not in (ReactItem.K_LOVE, ReactItem.K_UPVOTE):
        return json({'r': 1, 'msg': 'Not supported reaction_type'})

    if request.method == 'POST':
        rv = await comment.add_reaction(user['gid'], reaction_type)
    elif request.method == 'DELETE':
        rv = await comment.cancel_reaction(user['gid'], reaction_type)

    n_reacted = 0
    if reaction_type == ReactItem.K_LOVE:
        n_reacted = await comment.n_likes
    elif reaction_type == ReactItem.K_UPVOTE:
        n_reacted = await comment.n_upvotes

    return json({'r': int(not rv), 'n_reacted': n_reacted})


@bp.route('/get_url_info', methods=['POST'])
async def get_url_info(request):
    user = request['session'].get('user')
    if not user:
        return json({'r': 403, 'msg': 'Login required'})
    if not (url := request.form.get('url')):
        return json({'r': 403, 'msg': 'URL required'})

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
    extracted = extraction.Extractor().extract(html, source_url=url)
    return json({
        'title': extracted.title,
        'url': extracted.url or url,
        'abstract': extracted.description
    })


@bp.route('/activity', methods=['POST'])
async def activity(request):
    return json({
        'r': 0
    })
