from __future__ import annotations

from dataclasses import dataclass
from pickle import dumps, loads
from typing import List, Optional, Dict, Tuple, Union

from tortoise import fields

from .base import BaseModel
from .comment import CommentMixin
from .consts import K_STATUS, K_ACTIVITY
from .mc import cache, clear_mc
from .react import ReactMixin
from .user import User
from .mixin import ContentMixin

MC_KEY_ALL_STATUSES = 'core:statuses'
MC_KEY_STATUS_ATTACHMENTS = 'core.status:attachments:%s'


@dataclass
class Attachment:
    LAYOUTS = (LAYOUT_LINK, LAYOUT_PHOTO, LAYOUT_CODE, LAYOUT_VIDEO) = range(4)
    layout: int = LAYOUT_LINK
    url: Union[Optional[str], str] = ''


@dataclass
class Link(Attachment):
    title: str = ''
    abstract: str = ''
    images: List[str] = []
    layout: int = Attachment.LAYOUT_LINK


@dataclass
class Photo(Attachment):
    title: Optional[str] = ''
    size: Tuple[int, int] = (0, 0)
    layout: int = Attachment.LAYOUT_PHOTO


@dataclass
class CodeSnippet(Attachment):
    url: Optional[str] = ''
    content: Optional[str] = ''
    layout: int = Attachment.LAYOUT_CODE


@dataclass
class Video(Attachment):
    runtime: int = 0
    title: Optional[str] = ''
    cover_url: str = ''
    layout: int = Attachment.LAYOUT_VIDEO


class Status(ContentMixin, BaseModel):
    kind = K_STATUS
    user_id = fields.IntField()

    class Meta:
        table = 'statuses'

    @classmethod
    async def create(cls, **kwargs):
        content = kwargs.pop('content')
        obj = await super().create(**kwargs)
        await obj.set_content(content)
        return obj

    async def set_attachments(self, attachments: List[Dict]) -> bool:
        lst = []
        for attach in attachments:
            lst.append(Attachment())
        await self.set_props_by_key('attachments', dumps(lst).decode('utf-8'))
        return True

    @property
    # @cache(MC_KEY_STATUS_ATTACHMENTS % '{self.id}')
    async def attachments(self) -> List[Attachment]:
        if not (rv := await self.get_props_by_key('attachments')):
            return []
        return loads(rv)

    @property
    async def user(self) -> User:
        rv = await User.cache(self.user_id)
        return rv

    async def clear_mc(self):
        keys = [MC_KEY_STATUS_ATTACHMENTS % self.id]
        await clear_mc(*keys)

    @cache(MC_KEY_ALL_STATUSES)
    async def get_all(cls, with_page) -> List[Status]:
        return await cls.sync_filter(orderings=['-id'], limit=None)


class Activity(CommentMixin, ReactMixin, BaseModel):
    kind = K_ACTIVITY
    user_id = fields.IntField()
    target_id = fields.IntField()
    target_kind = fields.IntField()
