import re
from datetime import datetime, timezone
from json import JSONEncoder, dumps
from typing import Any, Dict, Optional

import aiohttp
from sanic.exceptions import SanicException
from sanic.response import HTTPResponse

from config import HERE

DOUBAN_URL_RE = re.compile('https://(\w+)\.douban\.com\/subject\/(\d+)')


class APIJSONEncoder(JSONEncoder):
    def default(self, val):
        if isinstance(val, datetime):
            return int(val.replace(tzinfo=timezone.utc).timestamp())
        try:
            return JSONEncoder.default(self, val)
        except TypeError as e:
            if hasattr(val, 'to_dict'):
                return val.to_dict()
            raise e


def json(body: Dict[str, Any], status: int = 200, headers: Optional[Any] = None,
         content_type: str = "application/json", **kwargs: Any) -> HTTPResponse:
    return HTTPResponse(
        dumps(body, separators=(",", ":"), cls=APIJSONEncoder, **kwargs),
        headers=headers,
        status=status,
        content_type=content_type,
    )


def abort(status_code):
    raise SanicException(None, status_code)


async def save_image(url) -> str:
    basename = url.rpartition('/')[-1]
    dist = HERE / 'static/jpg' / basename
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.read()
            with open(dist, 'wb') as f:
                f.write(data)
            return data, basename


def normalization_url(url):
    if 'douban.com' in url:
        m = DOUBAN_URL_RE.search(url)
        if m:
            url = m.group()
    return url
