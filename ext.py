from tortoise import Tortoise
from sanic_mako import SanicMako
from sanic_auth import Auth
import aiotask_context as context  # noqa

from config import DB_URL, SENTRY_DSN

mako = SanicMako()
auth = Auth()


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
