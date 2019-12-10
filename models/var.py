import contextvars
from typing import Any

redis_var: contextvars.ContextVar[Any] = contextvars.ContextVar('redis')
memcache_var: contextvars.ContextVar[Any] = contextvars.ContextVar('memcache')
