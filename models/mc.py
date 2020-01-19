import asyncio
import inspect
import re
from functools import wraps
from pickle import dumps, loads
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from aioredis.errors import RedisError

from .utils import Empty, get_redis

__formaters: Dict[str, Callable] = {}
percent_pattern = re.compile(r'%\w')
brace_pattern = re.compile(r'\{[\w\d\.\[\]_]+\}')


def formater(text: str) -> Callable:
    """
    >>> format('%s %s', 3, 2, 7, a=7, id=8)
    '3 2'
    >>> format('%(a)d %(id)s', 3, 2, 7, a=7, id=8)
    '7 8'
    >>> format('{1} {id}', 3, 2, a=7, id=8)
    '2 8'
    >>> class Obj: id = 3
    >>> format('{obj.id} {0.id}', Obj(), obj=Obj())
    '3 3'
    >>> class Obj: id = 3
    >>> format('{obj.id.__class__} {obj.id.__class__.__class__} {0.id} {1}', \
    >>> Obj(), 6, obj=Obj())
    "<type 'int'> <type 'type'> 3 6"
    """
    percent = percent_pattern.findall(text)
    brace = brace_pattern.search(text)
    if percent and brace:
        raise Exception('mixed format is not allowed')

    if percent:
        n = len(percent)
        return lambda *a, **kw: text % tuple(a[:n])
    elif '%(' in text:
        return lambda *a, **kw: text % kw
    else:
        return text.format


def format(text: str, *a, **kw) -> str:
    if (f := __formaters.get(text)) is None:
        f = formater(text)
        __formaters[text] = f
    return f(*a, **kw)  # type: ignore


def gen_key(key_pattern, arg_names, defaults, *a, **kw):
    return gen_key_factory(key_pattern, arg_names, defaults)(*a, **kw)


def gen_key_factory(key_pattern: str, arg_names: List[str],
                    defaults: Optional[Tuple[Any, ...]]) -> Callable:
    args = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}
    if callable(key_pattern):
        names = inspect.getargspec(key_pattern)[0]

    def gen_key(*a: Any, **kw: Any) -> Tuple[str, Dict[str, Any]]:
        aa = args.copy()
        aa.update(zip(arg_names, a))
        aa.update(kw)
        if callable(key_pattern):
            key = key_pattern(*[aa[n] for n in names])
        else:
            key = format(key_pattern, *[aa[n] for n in arg_names], **aa)
        return key and key.replace(' ', '_'), aa
    return gen_key


def cache(key_pattern: str, expire: int = 0, serialize: bool = True,
          parser: Union[Any] = None) -> Callable:
    def deco(f: Callable) -> Callable:
        arg_names, varargs, varkw, defaults, _, _, _ = inspect.getfullargspec(f)  # noqa
        if varargs or varkw:
            raise Exception("do not support varargs")
        gen_key = gen_key_factory(key_pattern, arg_names, defaults)

        @wraps(f)
        async def __(*a: Any, **kw: Any) -> Dict[str, List[Tuple]]:
            redis = await get_redis()
            key, args = gen_key(*a, **kw)
            if not key:
                return f(*a, **kw)
            force = kw.pop('force', False)
            try:
                r = await redis.get(key.encode('utf-8')) if not force else None
            except RedisError:
                r = None
            if r is None:
                r = await f(*a, **kw)
                if r is not None and not isinstance(r, Empty):
                    if serialize:
                        r = dumps(r)
                    else:
                        r = str(r).encode('utf-8')
                    await redis.set(key.encode('utf-8'),
                                    r, expire=expire)
            if serialize:
                try:
                    r = loads(r)
                except TypeError:
                    ...
            if parser is not None:
                try:
                    r = parser(r)
                except ValueError:
                    if parser == int:
                        r = 0
            return r
        __.original_function = f  # type: ignore
        return __
    return deco


async def clear_mc(*keys) -> bool:
    redis = await get_redis()
    if redis is None:
        return False
    await asyncio.gather(*[redis.delete(k.encode('utf-8')) for k in keys],
                         return_exceptions=True)
    return True


class mc:
    @staticmethod
    async def get_multi(*keys) -> List[Any]:
        redis = await get_redis()
        if redis is None:
            return []
        values = await redis.mget(*[k.encode('utf-8') for k in keys])

        rs = []
        for value in values:
            try:
                r = loads(value)
            except TypeError:
                r = None
            rs.append(r)
        return rs

    @staticmethod
    async def set_multi(keys, values, expire: int = 0) -> bool:
        redis = await get_redis()
        for k, v in zip(keys, values):
            await redis.set(k.encode('utf-8'),
                            dumps(v), expire=expire)
        return True

    @staticmethod
    async def incr(key: str, increment: int = 1, default: int = 0) -> bytes:
        redis = await get_redis()
        key = key.encode('utf-8')
        try:
            return await redis.incrby(key, increment)
        except RedisError:
            increment_ = str(default).encode('utf-8')
            await redis.set(key, increment_)
            return increment_

    @staticmethod
    async def decr(key: str, increment: int = 1) -> Union[bytes, bool]:
        redis = await get_redis()
        key = key.encode('utf-8')
        try:
            return await redis.decrby(key, increment)
        except RedisError:
            return False

    @staticmethod
    async def get(key: str):
        redis = await get_redis()
        key = key.encode('utf-8')
        return await redis.get(key)

    @staticmethod
    async def set(key: str, value):
        redis = await get_redis()
        key = key.encode('utf-8')
        return await redis.set(key, value)
