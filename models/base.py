import asyncio
import inspect
from datetime import datetime
from typing import Any, Dict, KeysView, List, Optional, Set, Union

from sanic.exceptions import abort
from tortoise import fields

import config
from config import AttrDict

from .mc import cache, clear_mc

from tortoise.models import Model, ModelMeta as _ModelMeta  # isort:skip


MC_KEY_ITEM_BY_ID = '%s:%s:v2'
IGNORE_ATTRS = ['redis', 'stats']


class PropertyHolder(type):

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        new_cls.property_fields = []  # type: ignore

        for attr in list(attrs) + sum([list(vars(base))
                                       for base in bases], []):
            if attr.startswith('_') or attr in IGNORE_ATTRS:
                continue
            if isinstance(getattr(new_cls, attr), property):
                new_cls.property_fields.append(attr)  # type: ignore
        return new_cls


class ModelMeta(_ModelMeta, PropertyHolder):  # type: ignore
    ...


class BaseModel(Model, metaclass=ModelMeta):  # type: ignore
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    _redis = None

    class Meta:
        abstract = True

    @property
    def url(self) -> str:
        return f'/{self.__class__.__name__.lower()}/{self.id}/'

    def canonical_url(self):
        return f'{config.BLOG_URL}{self.url}'

    def to_dict(self) -> Dict[str, Union[datetime, int, str]]:
        return {f: getattr(self, f) for f in self._meta.fields}

    async def to_sync_dict(self):
        rv = self.to_dict()
        for field in self.property_fields:
            coro = getattr(self, field)
            if inspect.iscoroutine(coro):
                rv[field] = await coro
            else:
                rv[field] = coro
        rv['url'] = self.url
        return AttrDict(rv)

    @classmethod
    async def sync_get(cls, *args: Any, **kwargs: Any):
        rv = await super().get(*args, **kwargs)
        return await rv.to_sync_dict()

    @classmethod
    async def sync_first(cls, *args, **kwargs):
        rv = await super().filter(*args, **kwargs).first()
        return await rv.to_sync_dict() if rv else None

    @classmethod
    async def sync_filter(cls, orderings: Union[List[str], str, None] = None,
                          offset: int = 0, limit: Optional[Any] = 20,
                          *args: Any, **kwargs: Any):
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
    async def sync_all(cls, ordering: str = '-id'):
        items = []
        for item in await cls.filter().order_by(ordering).all():
            items.append(await item.to_sync_dict())
        return items

    @classmethod
    async def get_or_404(cls, id: Union[str, int], sync: bool = False):
        if not (obj := await cls.cache(id)):
            abort(404)
        if sync:
            return await obj.to_sync_dict()
        return obj

    @classmethod
    @cache(MC_KEY_ITEM_BY_ID % ('{cls.__name__}', '{id}'))
    async def cache(cls, id: Union[str, int]) -> Any:
        return await cls.filter(id=id).first()

    @classmethod
    async def get_multi(cls, ids: Union[List[int], Set[int], KeysView[Any]]):
        return [await cls.cache(id) for id in ids]

    @classmethod
    async def create(cls, **kwargs: Any):
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
    async def __flush__(cls, target) -> None:
        await asyncio.gather(
            clear_mc(MC_KEY_ITEM_BY_ID % (target.__class__.__name__, target.id)),  # noqa
            target.clear_mc(), return_exceptions=True
        )

    async def clear_mc(self):
        ...

    async def update(self, **kwargs):
        fields = self._meta.fields
        for k, v in kwargs.items():
            if k not in fields:
                print(f'WARN: Field `{k}` may not be saved!')
            setattr(self, k, v)
        await self.save()  # type: ignore
        return self
