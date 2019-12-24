from typing import Any, Callable, Dict, List

import mistune
from sanic import Blueprint
from sanic.response import json
from sanic_mako import render_template_def

from config import DEBUG
from models import Activity, Comment, Post, ReactItem
from models.consts import K_POST

bp = Blueprint('j', url_prefix='/j')


def login_required(f: Callable) -> Callable:
    async def wrapped(request, **kwargs):
        if not (user := request['session'].get('user')):
            return json({'r': 403, 'msg': 'Login required.'})
            user = {'gid': 841395}  # My Github id
        if (target_id := kwargs.pop('target_id', None)) is not None:
            target_kind = kwargs.pop('target_kind', 'post')
            if target_kind == 'post':
                kls = Post
            elif target_kind == 'activity':
                kls = Activity
            elif target_kind == 'comment':
                kls = Comment
            else:
                return json({'r': 403, 'msg': 'Not support'})
            if not (target := await kls.cache(target_id)):
                return json({'r': 1, 'msg': f'{kls.__class__.__name__} not exist'})
            args = (user, target)
        else:
            args = (user,)  # type: ignore
        return await f(request, *args, **kwargs)
    return wrapped


@bp.route('/<target_kind>/<target_id>/comment', methods=['POST'])
@login_required
async def create_comment(request, user, target):
    if not (content := request.form.get('content')):
        return json({'r': 1, 'msg': 'Content required.'})
    ref_id = int(request.form.get('ref_id', 0))
    comment = await target.add_comment(user['gid'], content, ref_id, target.kind)
    comment = await comment.to_sync_dict()

    rv = {'r': 0 if comment else 1}
    if target.kind == K_POST:
        reacted_comments = await target.comments_reacted_by(user['gid'])
        rv.update({
            'html': await render_template_def(
                'utils.html', 'render_single_comment', request,
                {'comment': comment, 'github_user': user,
                 'reacted_comments': reacted_comments})
        })
    else:
        rv.update({'comment': comment})
    return json(rv)


@bp.route('/post/<post_id>/comments')
async def comments(request, post_id):
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


@bp.route('/post/<target_id>/react', methods=['POST', 'DELETE'])
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


@bp.route('/<target_kind>/<target_id>/react', methods=['POST', 'DELETE'])
@login_required
async def target_react(request, user, target):
    reaction_type = int(request.form.get('reaction_type', ReactItem.K_LOVE))
    if reaction_type not in (ReactItem.K_LOVE, ReactItem.K_UPVOTE):
        return json({'r': 1, 'msg': 'Not supported reaction_type'})

    if request.method == 'POST':
        rv = await target.add_reaction(user['gid'], reaction_type)
    elif request.method == 'DELETE':
        rv = await target.cancel_reaction(user['gid'], reaction_type)

    n_reacted = 0
    if reaction_type == ReactItem.K_LOVE:
        n_reacted = await target.n_likes
    elif reaction_type == ReactItem.K_UPVOTE:
        n_reacted = await target.n_upvotes

    return json({'r': int(not rv), 'n_reacted': n_reacted})


@bp.route('/activities', methods=['GET'])
async def activities(request):
    page = int(request.args.get('page', 1))
    total = await Activity.count()
    items = await Activity.get_multi_by(page)
    if not (user := request['session'].get('user')):
        user_id = 841395 if DEBUG else None
    else:
        user_id = user['gid']
    reactions: Dict[int, Any] = {}
    if user_id is not None:
        reactions = await Activity.get_reactions_by_targets(
            [item['id'] for item in items], user_id)
    activities = []
    for item in items:
        id = item['id']
        item['liked'] = id in reactions and ReactItem.K_LOVE in [
            r.reaction_type for r in reactions[id]]
        activities.append(item)
    return json({'items': activities, 'total': total})


@bp.route('/activity/<activity_id>/comments')
async def activity_comments(request, activity_id):
    if not (activity := await Activity.cache(activity_id)):
        return json({'r': 1, 'msg': 'Activity not exist'})

    return json({'r': 0, 'items': await activity.comments})
