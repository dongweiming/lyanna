from tortoise import Tortoise
from sanic_mako import SanicMako

from config import DB_URL, SENTRY_DSN

mako = SanicMako()


async def init_db(create_db=False):
    await Tortoise.init(
        db_url=DB_URL,
        modules={'models': ['models']},
        _create_db=create_db
    )

if SENTRY_DSN:
    from sanic_sentry import SanicSentry
    sentry = SanicSentry()
else:
    sentry = None
