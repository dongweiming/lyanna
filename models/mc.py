import re
import asyncio
import inspect
from functools import wraps
from pickle import loads, dumps

import aiomcache

import config
from .var import memcache_var
from .utils import Empty

_memcache = None
__formaters = {}
percent_pattern = re.compile(r'%\w')
brace_pattern = re.compile(r'\{[\w\d\.\[\]_]+\}')


async def get_memcache():
    global _memcache
    if _memcache is not None:
        return _memcache
    try:
        memcache = memcache_var.get()
    except LookupError:
        # Hack for debug mode
        memcache = None
    if memcache is None:
        loop = asyncio.get_event_loop()
        memcache = aiomcache.Client(config.MEMCACHED_HOST,
                                    config.MEMCACHED_PORT,
                                    loop=loop)
    _memcache = memcache
    return memcache


def formater(text):
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


def format(text, *a, **kw):
    f = __formaters.get(text)
    if f is None:
        f = formater(text)
        __formaters[text] = f
    return f(*a, **kw)


def gen_key(key_pattern, arg_names, defaults, *a, **kw):
    return gen_key_factory(key_pattern, arg_names, defaults)(*a, **kw)


def gen_key_factory(key_pattern, arg_names, defaults):
    args = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}
    if callable(key_pattern):
        names = inspect.getargspec(key_pattern)[0]

    def gen_key(*a, **kw):
        aa = args.copy()
        aa.update(zip(arg_names, a))
        aa.update(kw)
        if callable(key_pattern):
            key = key_pattern(*[aa[n] for n in names])
        else:
            key = format(key_pattern, *[aa[n] for n in arg_names], **aa)
        return key and key.replace(' ', '_'), aa
    return gen_key


def cache(key_pattern, expire=0):
    def deco(f):
        arg_names, varargs, varkw, defaults = inspect.getargspec(f)
        if varargs or varkw:
            raise Exception("do not support varargs")
        gen_key = gen_key_factory(key_pattern, arg_names, defaults)

        @wraps(f)
        async def _(*a, **kw):
            memcache = await get_memcache()
            key, args = gen_key(*a, **kw)
            if not key:
                return f(*a, **kw)
            force = kw.pop('force', False)
            r = await memcache.get(key.encode('utf-8')) if not force else None

            if r is None:
                r = await f(*a, **kw)
                if r is not None and not isinstance(r, Empty):
                    r = dumps(r)
                    await memcache.set(key.encode('utf-8'),
                                       r, expire)
            try:
                r = loads(r)
            except TypeError:
                ...
            return r
        _.original_function = f
        return _
    return deco


async def clear_mc(*keys):
    memcache = await get_memcache()
    assert memcache is not None
    for k in keys:
        await memcache.delete(k.encode('utf-8'))
