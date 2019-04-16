from tortoise import fields
from werkzeug.security import check_password_hash, generate_password_hash

from .base import BaseModel


class User(BaseModel):
    email = fields.CharField(max_length=100)
    name = fields.CharField(max_length=100, unique=True)
    password = fields.TextField()
    active = fields.BooleanField(default=True)

    class Meta:
        table = 'users'

    def to_dict(self):
        rv = super().to_dict()
        rv.pop('password')
        return rv


class GithubUser(BaseModel):
    gid = fields.IntField(unique=True)
    email = fields.CharField(max_length=100, default='', unique=True)
    username = fields.CharField(max_length=100, unique=True)
    picture = fields.CharField(max_length=100, default='')
    link = fields.CharField(max_length=100, default='')

    class Meta:
        table = 'github_users'


def generate_password(password):
    return generate_password_hash(
        password, method='pbkdf2:sha256')


async def create_user(**data):
    if 'name' not in data or 'password' not in data:
        raise ValueError('username and password are required.')

    data['password'] = generate_password(data.pop('password'))

    user = await User.create(**data)
    return user


async def validate_login(name, password):
    user = await User.filter(name=name).first()
    if not user:
        return False, None
    if check_password_hash(user.password, password):
        return True, user
    return False, None


async def create_github_user(user_info):
    user, _ = await GithubUser.get_or_create(
        gid=user_info.id, email=user_info.email or user_info.username,
        username=user_info.username, picture=user_info.picture)
    return user
