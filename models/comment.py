from __future__ import annotations

import asyncio
from typing import Dict, List

from arq import create_pool
from tortoise import fields
from tortoise.query_utils import Q

from config import REDIS_URL, partials

from .base import BaseModel
from .consts import K_COMMENT, K_POST, ONE_DAY, ONE_HOUR
from .mc import cache, clear_mc, mc
from .mixin import ContentMixin
from .react import ReactItem, ReactMixin
from .signals import comment_reacted
from .user import GithubUser
from .utils import RedisSettings

MC_KEY_COMMENT_LIST = 'comment:comment_list:%s:%s'
MC_KEY_N_COMMENTS = 'comment:n_comments:%s:%s'
MC_KEY_COMMNET_IDS_REACTED_BY_USER = 'react:comment_ids_reacted_by:%s:%s'
MC_KEY_LATEST_COMMENTS = 'comment:latest_comments:%s'


class Comment(ReactMixin, ContentMixin, BaseModel):
    github_id = fields.IntField()
    target_kind = fields.IntField()
    target_id = fields.IntField()
    ref_id = fields.IntField(default=0)
    kind = K_COMMENT

    class Meta:
        table = 'comments'

    async def clear_mc(self):
        keys = [MC_KEY_COMMENT_LIST % (self.target_id, self.target_kind)]
        partial_config = next((p for p in partials
                               if p['name'] == 'latest_comments'), None)
        if partial_config:
            count = partial_config.get('count')
            if count:
                keys.append(MC_KEY_LATEST_COMMENTS % count)
        await clear_mc(*keys)

    @property
    async def user(self) -> GithubUser:
        return await GithubUser.filter(gid=self.github_id).first()

    async def incr(self):
        default = await self.filter(target_id=self.target_id,
                                    target_kind=self.target_kind).count()
        return await mc.incr(MC_KEY_N_COMMENTS % (self.target_id, self.target_kind),
                             default=default)

    async def decr(self):
        return await mc.decr(MC_KEY_N_COMMENTS % (self.target_id, self.target_kind))


class CommentMixin:
    id: int
    kind: int
    can_comment = fields.BooleanField(default=True)

    async def add_comment(self, user_id, content, ref_id=0, kind=K_POST):
        obj = await Comment.create(
            github_id=user_id, target_id=self.id, target_kind=kind,
            ref_id=ref_id)
        redis = await create_pool(RedisSettings.from_url(REDIS_URL))
        await asyncio.gather(
            obj.set_content(content),
            redis.enqueue_job('mention_users', self.id, content, user_id),
            return_exceptions=True
        )
        return obj

    async def del_comment(self, user_id, comment_id):
        c = await Comment.get(id=comment_id)
        if c and c.github_id == user_id and c.target_id == self.id:
            await c.delete()
            return True
        return False

    @property  # type: ignore
    @cache(MC_KEY_COMMENT_LIST % ('{self.id}', '{self.kind}'))
    async def comments(self) -> List[Dict]:
        return await Comment.sync_filter(
            target_id=self.id, target_kind=self.kind, orderings=['-id'])

    @property  # type: ignore
    @cache(MC_KEY_N_COMMENTS % ('{self.id}', '{self.kind}'), ONE_DAY, serialize=False,
           parser=int)
    async def n_comments(self) -> int:
        return await Comment.filter(target_id=self.id, target_kind=self.kind).count()

    @cache(MC_KEY_COMMNET_IDS_REACTED_BY_USER % (
        '{user_id}', '{self.id}'), ONE_HOUR)
    async def comments_reacted_by(self, user_id):
        if not (cids := [c.id for c in await self.comments]):
            return []
        queryset = await ReactItem.filter(
            Q(user_id=user_id), Q(target_id__in=cids),
            Q(target_kind=K_COMMENT))
        return [[item.target_id, item.reaction_type] for item in queryset]


@comment_reacted.connect
async def update_comment_list_cache(_, user_id, comment_id):
    if (comment := await Comment.cache(comment_id)):
        asyncio.gather(
            clear_mc(MC_KEY_COMMENT_LIST % (comment.target_id, comment.target_kind)),
            clear_mc(MC_KEY_COMMNET_IDS_REACTED_BY_USER % (
                user_id, comment.target_id)),
            return_exceptions=True
        )


@cache(MC_KEY_LATEST_COMMENTS % '{count}', ONE_HOUR)
async def get_latest_comments(count=5):
    return await Comment.filter().order_by('-id').limit(count)
