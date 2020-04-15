from sanic_jwt import exceptions  # noqa

from .activity import Activity, Status  # noqa
from .blog import Post, PostTag, SpecialItem, SpecialTopic, Tag  # noqa
from .comment import Comment  # noqa
from .react import ReactItem, ReactStats  # noqa
from .user import GithubUser, User, create_user, validate_login  # noqa


async def jwt_authenticate(request, *args, **kwargs):
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        raise exceptions.AuthenticationFailed('Missing username or password.')

    ok, user = await validate_login(username, password)
    if not ok:
        raise exceptions.AuthenticationFailed('User or Password is incorrect.')

    if not user.active:  # type: ignore
        raise exceptions.AuthenticationFailed(
            'The account has been deactivated!')
    return {'user_id': user.id}  # type: ignore
