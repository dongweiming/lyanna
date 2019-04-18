import inspect
import asyncio
import aioredis
from sanic.exceptions import abort
from asyncio.coroutines import CoroWrapper

from tortoise import fields
from tortoise.models import Model, ModelMeta as _ModelMeta

import config
from .mc import cache, clear_mc
from .utils import AttrDict
from ._compat import PY36
from .var import redis_var

MC_KEY_ITEM_BY_ID = '%s:%s'
IGNORE_ATTRS = ['redis', 'stats']
_redis = None


class PropertyHolder(type):

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        new_cls.property_fields = []

        for attr in list(attrs) + sum([list(vars(base))
                                       for base in bases], []):
            if attr.startswith('_') or attr in IGNORE_ATTRS:
                continue
            if isinstance(getattr(new_cls, attr), property):
                new_cls.property_fields.append(attr)
        return new_cls


class ModelMeta(_ModelMeta, PropertyHolder):
    ...


class BaseModel(Model, metaclass=ModelMeta):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    _redis = None

    class Meta:
        abstract = True

    @property
    def url(self):
        return f'/{self.__class__.__name__.lower()}/{self.id}/'

    def canonical_url(self):
        return f'{config.BLOG_URL}{self.url}'

    def to_dict(self):
        return {f: getattr(self, f) for f in self._meta.fields}

    async def to_sync_dict(self):
        rv = self.to_dict()
        for field in self.property_fields:
            coro = getattr(self, field)
            if inspect.iscoroutine(coro) or (
                    PY36 and isinstance(coro, CoroWrapper)):
                rv[field] = await coro
            else:
                rv[field] = coro
        rv['url'] = self.url
        return AttrDict(rv)

    @classmethod
    async def sync_get(cls, *args, **kwargs):
        rv = await super().get(*args, **kwargs)
        return await rv.to_sync_dict()

    @classmethod
    async def sync_first(cls, *args, **kwargs):
        rv = await super().filter(*args, **kwargs).first()
        return await rv.to_sync_dict() if rv else None

    @classmethod
    async def sync_filter(cls, orderings=None, offset=0, limit=20,
                          *args, **kwargs):
        items = []
        queryset = super().filter(*args, **kwargs)
        if orderings is not None:
            if not isinstance(orderings, list):
                orderings = [orderings]
            queryset = queryset.order_by(*orderings)
        if limit is not None:
            queryset = queryset.offset(offset).limit(limit)
        for item in await queryset:
            items.append(await item.to_sync_dict())
        return items

    @classmethod
    async def sync_all(cls):
        items = []
        for item in await super().all():
            items.append(await item.to_sync_dict())
        return items

    @property
    async def redis(self):
        global _redis
        if _redis is None:
            try:
                redis = redis_var.get()
            except LookupError:
                # Hack for debug mode
                loop = asyncio.get_event_loop()
                redis = await aioredis.create_redis_pool(
                    config.REDIS_URL, minsize=5, maxsize=20, loop=loop)
            _redis = redis
        return _redis

    def get_db_key(self, key):
        return f'{self.__class__.__name__}/{self.id}/props/{key}'

    async def set_props_by_key(self, key, value):
        key = self.get_db_key(key)
        return await (await self.redis).set(key, value)  # noqa: W606

    async def get_props_by_key(self, key):
        key = self.get_db_key(key)
        return await (await self.redis).get(key) or b''  # noqa: W606

    @classmethod
    async def get_or_404(cls, id, sync=False):
        obj = await cls.cache(id)
        if not obj:
            abort(404)
        if sync:
            return await obj.to_sync_dict()
        return obj

    @classmethod
    @cache(MC_KEY_ITEM_BY_ID % ('{cls.__name__}', '{id}'))
    async def cache(cls, id):
        return await cls.filter(id=id).first()

    @classmethod
    async def get_multi(cls, ids):
        return [await cls.cache(id) for id in ids]

    @classmethod
    async def create(cls, **kwargs):
        rv = await super().create(**kwargs)
        await cls.__flush__(rv)
        return rv

    async def delete(self, using_db=None):
        rv = await super().delete(using_db=using_db)
        await self.__flush__(self)
        return rv

    async def save(self, *args, **kwargs):
        rv = await super().save(*args, **kwargs)
        await self.__flush__(self)
        return rv

    @classmethod
    async def __flush__(cls, target):
        await clear_mc(MC_KEY_ITEM_BY_ID % (target.__class__.__name__, target.id))  # noqa
        await target.clear_mc()

    async def clear_mc(self):
        ...
