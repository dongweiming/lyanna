from sanic_jwt import exceptions  # noqa

from .blog import Post, Tag, PostTag  # noqa
from .comment import Comment  # noqa
from .react import ReactItem  # noqa
from .user import User, create_user, GithubUser, validate_login  # noqa
from .react import ReactItem, ReactStats  # noqa


async def jwt_authenticate(request, *args, **kwargs):
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        raise exceptions.AuthenticationFailed('Missing username or password.')

    ok, user = await validate_login(username, password)
    if not ok:
        raise exceptions.AuthenticationFailed('User or Password is incorrect.')

    if not user.active:
        raise exceptions.AuthenticationFailed(
            'The account has been deactivated!')
    return {'user_id': user.id}
