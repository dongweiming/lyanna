from sanic.request import Request as _Request

import config
from models import User


class Request(_Request):  # type: ignore
    user: User
    partials = config.partials
