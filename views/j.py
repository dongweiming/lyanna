import mistune

from sanic import Blueprint
from sanic.response import json
from sanic_mako import render_template_def

from models import Post, ReactItem, Comment

bp = Blueprint('j', url_prefix='/j')


def login_required(f):
    async def wrapped(request, **kwargs):
        user = request['session'].get('user')
        if not user:
            return json({'r': 403, 'msg': 'Login required.'})
        post_id = kwargs.pop('post_id', None)
        if post_id is not None:
            post = await Post.cache(post_id)
            if not post:
                return json({'r': 1, 'msg': 'Post not exist'})
            args = (user, post)
        else:
            args = (user,)
        return await f(request, *args, **kwargs)
    return wrapped


@bp.route('/post/<post_id>/comment', methods=['POST'])
@login_required
async def create_comment(request, user, post):
    content = request.form.get('content')
    if not content:
        return json({'r': 1, 'msg': 'Comment content required.'})
    comment = await post.add_comment(user['gid'], content)
    liked_comment_ids = await post.comment_ids_liked_by(user['gid'])
    comment = await comment.to_sync_dict()

    return json({
        'r': 0 if comment else 1,
        'html': await render_template_def(
            'utils.html', 'render_single_comment', request,
            {'comment': comment, 'github_user': user,
             'liked_comment_ids': liked_comment_ids})
    })


@bp.route('/post/<post_id>/comments')
async def comments(request, post_id):
    post = await Post.cache(id=post_id)
    if not post:
        return json({'r': 1, 'msg': 'Post not exist'})

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    start = (page - 1) * per_page
    comments = (await post.comments)[start: start + per_page]
    user = request['session'].get('user')

    liked_comment_ids = []
    if user:
        liked_comment_ids = await post.comment_ids_liked_by(user['gid'])

    return json({
        'r': 0,
        'html': await render_template_def(
            'utils.html', 'render_comments', request,
            {'comments': comments, 'github_user': user,
             'liked_comment_ids': liked_comment_ids})
    })


@bp.route('/markdown', methods=['POST'])
@login_required
async def render_markdown(request, user):
    text = request.form.get('text')
    if not text:
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


@bp.route('/comment/<comment_id>/like', methods=['POST', 'DELETE'])
async def comment_like(request, comment_id):
    user = request['session'].get('user')
    if not user:
        return json({'r': 403, 'msg': 'Login required.'})
    comment = await Comment.cache(comment_id)
    if not comment:
        return json({'r': 1, 'msg': 'Comment not exist'})

    if request.method == 'POST':
        rv = await comment.add_reaction(user['gid'], ReactItem.K_LOVE)
    elif request.method == 'DELETE':
        rv = await comment.cancel_reaction(user['gid'])

    return json({'r': int(not rv), 'n_likes': await comment.n_likes})
