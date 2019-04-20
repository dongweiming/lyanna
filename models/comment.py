import mistune
from tortoise import fields
from tortoise.query_utils import Q
from arq import create_pool

from config import REDIS_URL
from .base import BaseModel
from .mc import cache, clear_mc
from .user import GithubUser
from .consts import K_COMMENT, ONE_HOUR
from .react import ReactMixin, ReactItem
from .signals import comment_reacted
from .utils import RedisSettings

markdown = mistune.Markdown()
MC_KEY_COMMENT_LIST = 'comment:%s:comment_list'
MC_KEY_N_COMMENTS = 'comment:%s:n_comments'
MC_KEY_COMMNET_IDS_LIKED_BY_USER = 'react:comment_ids_liked_by:%s:%s'


class Comment(ReactMixin, BaseModel):
    github_id = fields.IntField()
    post_id = fields.IntField()
    ref_id = fields.IntField(default=0)
    kind = K_COMMENT

    class Meta:
        table = 'comments'

    async def set_content(self, content):
        return await self.set_props_by_key('content', content)

    async def save(self, *args, **kwargs):
        content = kwargs.pop('content', None)
        if content is not None:
            await self.set_content(content)
        return await super().save(*args, **kwargs)

    @property
    async def content(self):
        rv = await self.get_props_by_key('content')
        if rv:
            return rv.decode('utf-8')

    @property
    async def html_content(self):
        content = await self.content
        if not content:
            return ''
        return markdown(content)

    async def clear_mc(self):
        for key in (MC_KEY_N_COMMENTS, MC_KEY_COMMENT_LIST):
            await clear_mc(key % self.post_id)

    @property
    async def user(self):
        return await GithubUser.get(gid=self.github_id)

    @property
    async def n_likes(self):
        return (await self.stats).love_count


class CommentMixin:
    async def add_comment(self, user_id, content, ref_id=0):
        obj = await Comment.create(github_id=user_id, post_id=self.id,
                                   ref_id=ref_id)
        await obj.set_content(content)
        redis = await create_pool(RedisSettings.from_url(REDIS_URL))
        await redis.enqueue_job('mention_users', self.id, content, user_id)
        return obj

    async def del_comment(self, user_id, comment_id):
        c = await Comment.get(id=comment_id)
        if c and c.github_id == user_id and c.post_id == self.id:
            await c.delete()
            return True
        return False

    @property
    @cache(MC_KEY_COMMENT_LIST % ('{self.id}'))
    async def comments(self):
        return await Comment.sync_filter(post_id=self.id, orderings=['-id'])

    @property
    @cache(MC_KEY_N_COMMENTS % ('{self.id}'))
    async def n_comments(self):
        return await Comment.filter(post_id=self.id).count()

    @cache(MC_KEY_COMMNET_IDS_LIKED_BY_USER % (
        '{user_id}', '{self.id}'), ONE_HOUR)
    async def comment_ids_liked_by(self, user_id):
        cids = [c.id for c in await self.comments]
        if not cids:
            return []
        queryset = await ReactItem.filter(
            Q(user_id=user_id), Q(target_id__in=cids),
            Q(target_kind=K_COMMENT))
        return [item.target_id for item in queryset]


@comment_reacted.connect
async def update_comment_list_cache(_, user_id, comment_id):
    comment = await Comment.cache(comment_id)
    if comment:
        await clear_mc(MC_KEY_COMMENT_LIST % comment.post_id)
        await clear_mc(MC_KEY_COMMNET_IDS_LIKED_BY_USER % (
            user_id, comment.post_id))
