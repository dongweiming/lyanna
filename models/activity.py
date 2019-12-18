from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from pickle import dumps, loads
from typing import Any, Dict, List, Optional, Tuple, Union

from tortoise import fields

from config import USE_FFMPEG

from .base import BaseModel
from .blog import Post
from .comment import CommentMixin
from .consts import K_ACTIVITY, K_POST, K_STATUS
from .mc import cache, clear_mc
from .mixin import ContentMixin
from .react import ReactMixin
from .user import User

PER_PAGE = 10
MC_KEY_GET_BY = 'core:activities:%s'
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
    images: List[str] = field(default_factory=list)
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
    title: Optional[str] = ''
    cover_url: str = ''
    layout: int = Attachment.LAYOUT_VIDEO


class Status(ContentMixin, BaseModel):
    kind = K_STATUS
    user_id = fields.IntField()

    class Meta:
        table = 'statuses'

    @classmethod
    async def create(cls, **kwargs) -> Status:
        content = kwargs.pop('content')
        obj = await super().create(**kwargs)
        await obj.set_content(content)
        return obj

    async def set_attachments(
            self, attachments: List[Union[Link, Photo, Video]]) -> bool:
        if not attachments:
            return False
        lst = []
        for attach in attachments:
            lst.append(asdict(attach))
        await self.set_props_by_key('attachments', dumps(lst))
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


class Activity(CommentMixin, ReactMixin, BaseModel):
    kind = K_ACTIVITY
    user_id = fields.IntField()
    target_id = fields.IntField()
    target_kind = fields.IntField()

    @classmethod
    # @cache(MC_KEY_GET_BY % '{page}')
    async def get_multi_by(cls, page: int = 1) -> List[Dict]:
        items = []
        queryset = cls.offset((page - 1) * PER_PAGE).limit(PER_PAGE).order_by('-id')
        for item in await queryset:
            items.append(await item.to_full_dict())
        return items

    @property
    async def target(self):
        kls = None
        if self.target_kind == K_POST:
            kls = Post
        elif self.target_kind == K_STATUS:
            kls = Status
        if kls is None:
            return
        return await kls.cache(self.target_id)

    @property
    async def user(self) -> User:
        return await User.cache(self.user_id)

    async def to_full_dict(self) -> Dict[str, Any]:
        target = await self.target
        if not target:
            return {}
        return {
            'user': (await self.user).to_dict(),
            'target': await target.to_sync_dict()
        }

    async def clear_mc(self):
        total = await self.filter().count()
        page_count = math.ceil(total / PER_PAGE)
        keys = [MC_KEY_GET_BY % p for p in range(1, page_count + 1)]
        await clear_mc(*keys)


async def create_status(user_id: int, data: Dict):
    if not (text := data.get('text')):
        return False, 'Text required.'
    fids = data.get('fids', [])
    attachments: List[Union[Link, Photo, Video]] = []
    if fids:
        layout = Video if (is_video := fids[0].endswith('mp4')) else Photo
        for fid in fids:
            attach = layout(url=f'/static/upload/{fid}')
            if USE_FFMPEG and is_video:
                attach.cover_url = f'/static/upload/{fid.replace(".mp4", ".gif")}'
            attachments.append(attach)
    elif (url := data.get('url')):
        url_info = data.get('url_info', {})
        attachments = [Link(url=url, title=url_info.get('title', url),
                            abstract=url_info.get('abstract', ''))]
    status = await Status.create(user_id=user_id, content=text)
    if not status:
        return False, 'Create status fail.'
    await status.set_attachments(attachments)
    act = await Activity.create(target_id=status.id, target_kind=K_STATUS,
                                user_id=user_id)
    dct = await act.to_full_dict()
    return bool(dct), act
