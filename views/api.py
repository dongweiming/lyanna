from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import abort

from ext import auth
from models import Post

bp = Blueprint('api', url_prefix='/api')


@bp.route('/publish/<post_id>', methods=['POST', 'DELETE'])
@auth.login_required
async def publish(request, post_id):
    if not post_id:
        abort(404)
    post = await Post.get(id=post_id)
    if not post:
        return json({'r': 1, 'msg': 'Post not exist'})
    if request.method == 'POST':
        post.status = Post.STATUS_ONLINE
    elif request.method == 'DELETE':
        post.status = Post.STATUS_UNPUBLISHED
    await post.save()
    return json({'r': 0})


@bp.route('/delete/<post_id>', methods=['DELETE'])
@auth.login_required
async def delete(request, post_id):
    if not post_id:
        abort(404)
    post = await Post.get(id=post_id)
    if not post:
        return json({'r': 1, 'msg': 'Post not exist'})
    await post.delete()
    return json({'r': 0})
