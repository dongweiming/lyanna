import contextvars


redis_var = contextvars.ContextVar('redis')
memcache_var = contextvars.ContextVar('memcache')
