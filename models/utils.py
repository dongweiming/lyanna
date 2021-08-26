from __future__ import annotations

import asyncio
import binascii
import math
import os
import random
import re
import struct
import threading
import time
from dataclasses import dataclass
from functools import wraps
from typing import Dict, Iterator, List, Union
from urllib.parse import unquote

import aioredis
from aioredis.commands import Redis
from arq.connections import RedisSettings as _RedisSettings

from config import REDIS_URL, AttrDict

from .var import redis_var

_redis = None


def trunc_utf8(string: str, num: int, etc: str = '...') -> str:
    if num >= len(string):
        return string

    if etc:
        trunc_idx = num - len(etc)
    else:
        trunc_idx = num
    ret = string[:trunc_idx]
    if etc:
        ret += etc
    return ret


class Empty:

    def __call__(self, *a, **kw):
        return empty

    def __nonzero__(self):
        return False

    def __contains__(self, item):
        return False

    def __repr__(self):
        return '<Empty Object>'

    def __str__(self):
        return ''

    def __eq__(self, v):
        return isinstance(v, Empty)

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return empty

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def next(self):
        raise StopIteration

    def __getattr__(self, mname):
        return ''

    def __setattr__(self, name, value):
        return self

    def __delattr__(self, name):
        return self

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__ = d


empty = Empty()


class Pagination:

    def __init__(self, page: int, per_page: int, total: int,
                 items: List[AttrDict]) -> None:
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items

    @property
    def pages(self) -> int:
        if self.per_page == 0 or self.total is None:
            pages = 0
        else:
            pages = int(math.ceil(self.total / float(self.per_page)))
        return pages

    @property
    def prev_num(self):
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def next_num(self):
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge: int = 2, left_current: int = 2,
                   right_current: int = 2,
                   right_edge: int = 2) -> Iterator[Union[Iterator, Iterator[int],
                                                          None, int]]:
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or self.page - left_current - 1 < num < self.page + right_current  # noqa
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


def _parse_rfc1738_args(name: str) -> Dict[str, str]:
    pattern = re.compile(
        r"""
            (?P<name>[\w\+]+)://
            (?:
                (?P<username>[^:/]*)
                (?::(?P<password>.*))?
            @)?
            (?:
                (?:
                    \[(?P<ipv6host>[^/]+)\] |
                    (?P<ipv4host>[^/:]+)
                )?
                (?::(?P<port>[^/]*))?
            )?
            (?:/(?P<database>.*))?
            """,
        re.X,
    )

    if (m := pattern.match(name)) is not None:
        components = m.groupdict()  # type: ignore
        if components['database'] is not None:
            tokens = components['database'].split('?', 2)
            components['database'] = tokens[0]

        if components['password'] is not None:
            components['password'] = unquote(components['password'])

        ipv4host = components.pop('ipv4host')
        ipv6host = components.pop('ipv6host')
        components['host'] = ipv4host or ipv6host
        return components
    else:
        raise ValueError(
            f"Could not parse rfc1738 URL from string '{name}'"
        )


@dataclass
class RedisSettings(_RedisSettings):
    @classmethod
    def from_url(cls, db_url: str) -> RedisSettings:
        url = _parse_rfc1738_args(db_url)
        return cls(url['host'], url['port'],
                   url['database'] and int(url['database']) or 0,
                   url['password'], None, 5, 1)


async def get_redis(loop=None) -> Redis:
    global _redis
    if _redis is None:
        try:
            redis = redis_var.get()
        except LookupError:
            # Hack for debug mode
            if loop is None:
                loop = asyncio.get_event_loop()
            redis = await aioredis.create_redis_pool(
                REDIS_URL, minsize=5, maxsize=20, loop=loop)
        _redis = redis
        redis_var.set(redis)
    return _redis


class ObjectId:
    _inc = random.randint(0, 0xFFFFFF)
    _inc_lock = threading.Lock()


def generate_id() -> str:
    oid = struct.pack(">i", int(time.time()))
    oid += struct.pack(">H", os.getpid() % 0xFFFF)
    with ObjectId._inc_lock:
        oid += struct.pack(">i", ObjectId._inc)[2:4]
        ObjectId._inc = (ObjectId._inc + 1) % 0xFFFFFF
    return binascii.hexlify(oid).decode('utf-8')


# Modify from https://github.com/pydanny/cached-property/blob/master/cached_property.py
class cached_property:
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self

        if asyncio and asyncio.iscoroutinefunction(self.func):
            return self._wrap_in_coroutine(obj)  # type: ignore

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    def _wrap_in_coroutine(self, obj):
        @wraps(obj)
        async def wrapper():
            future = asyncio.ensure_future(self.func(obj))
            obj.__dict__[self.func.__name__] = future
            return await future

        return wrapper()
