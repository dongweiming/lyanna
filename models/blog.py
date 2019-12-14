from __future__ import annotations

import random
import re
from datetime import datetime, timedelta
from html.parser import HTMLParser
from typing import Any, Callable, Dict, List, Tuple, Union  # noqa

from aioredis.errors import RedisError
from tortoise import fields
from tortoise.models import ModelMeta
from tortoise.query_utils import Q
from tortoise.queryset import QuerySet

from config import PERMALINK_TYPE, AttrDict

from .base import BaseModel
from .mixin import get_redis
from .comment import CommentMixin
from .consts import K_POST, ONE_HOUR, PERMALINK_TYPES
from .markdown import markdown, toc, toc_md
from .mc import cache, clear_mc
from .react import ReactMixin
from .user import User
from .utils import trunc_utf8
from .mixin import ContentMixin

MC_KEY_TAGS_BY_POST_ID = 'post:%s:tags'
MC_KEY_RELATED = 'post:related_posts:%s'
MC_KEY_POST_BY_SLUG = 'post:%s:slug'
MC_KEY_ALL_POSTS = 'core:posts:%s:v2'
MC_KEY_FEED = 'core:feed'
MC_KEY_SITEMAP = 'core:sitemap'
MC_KEY_SEARCH = 'core:search.json'
MC_KEY_ARCHIVES = 'core:archives'
MC_KEY_ARCHIVE = 'core:archive:%s'
MC_KEY_TAGS = 'core:tags'
MC_KEY_TAG = 'core:tag:%s'
MC_KEY_SPECIAL_ITEMS = 'special:%s:items'
MC_KEY_SPECIAL_POST_ITEMS = 'special:%s:post_items'
MC_KEY_SPECIAL_BY_PID = 'special:by_pid:%s'
MC_KEY_SPECIAL_BY_SLUG = 'special:%s:slug'
MC_KEY_ALL_SPECIAL_TOPICS = 'special:topics'
RK_PAGEVIEW = 'lyanna:pageview:{}:v2'
RK_ALL_POST_IDS = 'lyanna:all_post_ids'
RK_VISITED_POST_IDS = 'lyanna:visited_post_ids'
BQ_REGEX = re.compile(r'<blockquote>.*?</blockquote>')
PAGEVIEW_FIELD = 'pv'


class MLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class StatusMixin(metaclass=ModelMeta):
    STATUSES = (
        STATUS_UNPUBLISHED,
        STATUS_ONLINE
    ) = range(2)
    status = fields.SmallIntField(default=STATUS_UNPUBLISHED)


class Post(CommentMixin, ReactMixin, StatusMixin, ContentMixin, BaseModel):

    TYPES = (TYPE_ARTICLE, TYPE_PAGE) = range(2)

    title = fields.CharField(max_length=100, unique=True)
    author_id = fields.IntField()
    slug = fields.CharField(max_length=100)
    summary = fields.CharField(max_length=255)
    type = fields.IntField(default=TYPE_ARTICLE)
    _pageview = fields.IntField(source_field='pageview', default=0)
    kind = K_POST

    class Meta:
        table = 'posts'

    @classmethod
    async def create(cls, **kwargs):
        tags = kwargs.pop('tags', [])
        content = kwargs.pop('content')
        obj = await super().create(**kwargs)
        if (tags := kwargs.pop('tags', [])):
            await PostTag.update_multi(obj.id, tags)
        await obj.set_content(content)
        return obj

    async def update_tags(self, tagnames):
        if tagnames:
            await PostTag.update_multi(self.id, tagnames)
        return True

    @property  # type: ignore
    @cache(MC_KEY_TAGS_BY_POST_ID % ('{self.id}'))
    async def tags(self) -> List:
        pts = await PostTag.filter(post_id=self.id).order_by(
            'updated_at').all()
        if not pts:
            return []
        ids = [pt.tag_id for pt in pts]
        tags = await Tag.filter(id__in=ids).all()
        return sorted(tags, key=lambda t: ids.index(t.id))

    @property
    async def author(self) -> User:
        rv = await User.cache(self.author_id)
        return rv

    @property
    def preview_url(self) -> str:
        return f'/{self.__class__.__name__.lower()}/{self.id}/preview'

    @property
    async def html_content(self) -> str:
        content = await self.content
        if not (content := await self.content):
            return ''
        return markdown(content)

    @property
    async def excerpt(self) -> str:
        if self.summary:
            return self.summary
        s = MLStripper()  # type: ignore
        s.feed(await self.html_content)
        return trunc_utf8(BQ_REGEX.sub('', s.get_data()).replace('\n', ''), 100)  # noqa

    @cache(MC_KEY_RELATED % ('{self.id}'), ONE_HOUR)
    async def get_related(self, limit: int = 4):
        tag_ids = [tag.id for tag in await self.tags]
        if not (tag_ids := [tag.id for tag in await self.tags]):
            return []
        post_ids = set(await PostTag.filter(
            Q(post_id__not=self.id), Q(tag_id__in=tag_ids)).values_list(
                'post_id', flat=True))

        excluded_ids = await self.filter(
            Q(created_at__lt=(datetime.now() - timedelta(days=180))) |
            Q(status__not=self.STATUS_ONLINE)).values_list('id', flat=True)

        post_ids -= set(excluded_ids)
        try:
            _post_ids = random.sample(post_ids, limit)
        except ValueError:
            _post_ids = []
        return await self.get_multi(_post_ids)

    async def clear_mc(self):
        keys = [
            MC_KEY_FEED, MC_KEY_SITEMAP, MC_KEY_SEARCH, MC_KEY_ARCHIVES,
            MC_KEY_TAGS, MC_KEY_RELATED % self.id,
            MC_KEY_POST_BY_SLUG % self.slug,
            MC_KEY_ARCHIVE % self.created_at.year]
        for i in [True, False]:
            keys.append(MC_KEY_ALL_POSTS % i)

        for tag in await self.tags:
            keys.append(MC_KEY_TAG % tag.id)
        await clear_mc(*keys)
        await SpecialTopic.flush_by_pid(self.id)

    @classmethod
    @cache(MC_KEY_POST_BY_SLUG % '{slug}')
    async def get_by_slug(cls, slug: str) -> None:
        return await cls.filter(slug=slug).first()

    @classmethod
    @cache(MC_KEY_ALL_POSTS % '{with_page}')
    async def get_all(cls, with_page: bool = True) -> List[Post]:
        if with_page:
            return await Post.sync_filter(
                status=Post.STATUS_ONLINE,
                orderings=['-id'], limit=None)
        return await Post.sync_filter(
            status=Post.STATUS_ONLINE, type__not=cls.TYPE_PAGE,
            orderings=['-id'], limit=None)

    @classmethod
    async def cache(cls, ident: Union[str, int]) -> Post:
        if str(ident).isdigit():
            return await super().cache(ident)
        return await cls.get_by_slug(ident)

    @property
    async def toc(self) -> str:
        if not (content := await self.content):
            return ''
        toc.reset_toc()
        toc_md.parse(content)
        return toc.render_toc(level=4)

    @property
    def is_page(self) -> bool:
        return self.type == self.TYPE_PAGE

    @property
    def url(self) -> str:
        if self.is_page:
            return f'/page/{self.slug}'
        if PERMALINK_TYPE not in PERMALINK_TYPES:
            raise TypeError('Wrong url type!')
        return f'/post/{getattr(self, PERMALINK_TYPE) or self.id}/'

    async def incr_pageview(self, increment: int = 1) -> int:
        redis = await self.redis
        try:
            await redis.sadd(RK_ALL_POST_IDS, self.id)
            await redis.sadd(RK_VISITED_POST_IDS, self.id)
            return await redis.hincrby(RK_PAGEVIEW.format(self.id),
                                       PAGEVIEW_FIELD, increment)
        except RedisError:
            return self._pageview

    @property
    async def pageview(self) -> int:
        try:
            return int(await (await self.redis).hget(
                RK_PAGEVIEW.format(self.id), PAGEVIEW_FIELD) or 0)
        except RedisError:
            return self._pageview


class Tag(BaseModel):
    name = fields.CharField(max_length=100, unique=True)

    class Meta:
        table = 'tags'

    @classmethod
    def get_by_name(cls, name: str) -> QuerySet:
        return cls.filter(name=name).first()

    @classmethod
    def create(cls, **kwargs) -> Tag:
        name = kwargs.pop('name')
        kwargs['name'] = name.lower()
        return super().create(**kwargs)  # type: ignore


class PostTag(BaseModel):
    post_id = fields.IntField()
    tag_id = fields.IntField()
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'post_tags'

    @classmethod
    async def update_multi(cls, post_id: int, tags: List[str]) -> None:
        origin_tags = set([t.name for t in (
            await Post.sync_get(id=post_id)).tags])
        need_add = set(tags) - origin_tags
        need_del = origin_tags - set(tags)
        need_add_tag_ids = []
        need_del_tag_ids = set()
        for tag_name in need_add:
            tag, _ = await Tag.get_or_create(name=tag_name)
            need_add_tag_ids.append([tag.id, tag_name])
        for tag_name in need_del:
            tag, _ = await Tag.get_or_create(name=tag_name)
            need_del_tag_ids.add(tag.id)

        if need_del_tag_ids:
            await cls.filter(Q(post_id=post_id),
                             Q(tag_id__in=need_del_tag_ids)).delete()
        for tag_id, _ in sorted(need_add_tag_ids,
                                key=lambda x: tags.index(x[1])):
            await cls.get_or_create(post_id=post_id, tag_id=tag_id)

        await clear_mc(MC_KEY_TAGS_BY_POST_ID % post_id)


class SpecialItem(BaseModel):
    post_id = fields.IntField()
    index = fields.SmallIntField()
    special_id = fields.SmallIntField()

    class Meta:
        table = 'special_item'

    @classmethod
    @cache(MC_KEY_SPECIAL_BY_PID % ('{post_id}'))
    async def get_special_id_by_pid(cls, post_id: int) -> List[Any]:
        return await SpecialItem.filter(post_id=post_id).values_list(
            'special_id', flat=True)


class SpecialTopic(StatusMixin, BaseModel):
    id = fields.SmallIntField(pk=True)
    intro = fields.CharField(max_length=2000)
    slug = fields.CharField(max_length=100)
    title = fields.CharField(max_length=100, unique=True)

    class Meta:
        table = 'special_topic'

    @cache(MC_KEY_SPECIAL_POST_ITEMS % ('{self.id}'))
    async def get_post_items(self):
        items = await self.get_items()
        if not (post_ids := [s.post_id for s in items]):
            return []
        posts = await Post.filter(id__in=post_ids).all()
        return sorted(posts, key=lambda p: post_ids.index(p.id))

    @cache(MC_KEY_SPECIAL_ITEMS % ('{self.id}'))
    async def get_items(self) -> List[SpecialItem]:
        return await SpecialItem.filter(special_id=self.id).order_by(
            'index').all()

    async def set_indexes(self, indexes):
        origin_map = {i.post_id: i for i in await self.get_items()}
        pids = [pid for pid, index in indexes]
        need_del_pids = set(origin_map) - set(pids)

        if need_del_pids:
            await SpecialItem.filter(Q(special_id=self.id),
                                     Q(post_id__in=need_del_pids)).delete()
        for pid, index in indexes:
            if pid in origin_map:
                special = origin_map[pid]
                if index != special.index:
                    special.index = index
                    await special.save()
            else:
                await SpecialItem.get_or_create(
                    post_id=pid, special_id=self.id, index=index)

        await clear_mc(MC_KEY_SPECIAL_ITEMS % self.id,
                       MC_KEY_SPECIAL_POST_ITEMS % self.id)

    @classmethod
    async def flush_by_pid(cls, post_id: int) -> None:
        special_ids = await SpecialItem.get_special_id_by_pid(post_id)
        keys = [MC_KEY_SPECIAL_ITEMS % i for i in special_ids]
        keys.extend([MC_KEY_SPECIAL_POST_ITEMS % i for i in special_ids])
        keys.append(MC_KEY_SPECIAL_BY_PID % post_id)
        await clear_mc(*keys)

    @property
    async def n_posts(self) -> int:
        return len(await self.get_post_items())

    @property
    async def posts(self) -> List[Dict[str, Any]]:
        return [{'id': p.id, 'title': p.title}
                for p in await self.get_post_items()]

    @property
    def url(self) -> str:
        return f'/special/{self.slug or self.id}'

    @classmethod
    @cache(MC_KEY_SPECIAL_BY_SLUG % '{slug}')
    async def get_by_slug(cls, slug: str) -> SpecialTopic:
        return await cls.filter(slug=slug).first()

    @classmethod
    @cache(MC_KEY_ALL_SPECIAL_TOPICS)
    async def get_all(cls) -> List[AttrDict]:
        return await cls.sync_filter(status=cls.STATUS_ONLINE,
                                     orderings=['-id'], limit=None)

    @classmethod
    async def cache(cls, ident: Union[str, int]) -> None:
        if str(ident).isdigit():
            return await super().cache(ident)
        return await cls.get_by_slug(ident)

    async def clear_mc(self):
        keys = [
            MC_KEY_SPECIAL_BY_SLUG % self.slug,
            MC_KEY_SPECIAL_POST_ITEMS % self.id,
            MC_KEY_SPECIAL_ITEMS % self.id,
            MC_KEY_ALL_SPECIAL_TOPICS
        ]
        await clear_mc(*keys)


async def get_most_viewed_posts(
        count: int, offset: int = 0) -> List[Tuple[int, Post]]:
    redis = await get_redis()
    key_pattern = RK_PAGEVIEW.replace('{}', '*')
    keys = (await redis.sort(RK_ALL_POST_IDS, by=f'{key_pattern}->pv',
                             asc=False))[offset:count]
    p = redis.pipeline()
    for k in keys:
        p.hgetall(RK_PAGEVIEW.format(k.decode()))
    counts = [int(d.get(PAGEVIEW_FIELD.encode(), 0))
              for d in await p.execute()]
    posts = await Post.get_multi([k.decode() for k in keys])
    items = []
    for index, p in enumerate(posts):
        items.append((counts[index], p))
    return items
