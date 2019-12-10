from sanic.request import Request as _Request
from models import User

import config


class Request(_Request):  # type: ignore
    user: User
    partials = config.partials
