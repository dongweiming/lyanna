from json import dumps, JSONEncoder
from datetime import datetime, date, timezone

from sanic.response import HTTPResponse


class APIJSONEncoder(JSONEncoder):
    def default(self, val):
        if isinstance(val, (datetime, date)):
            return int(val.replace(tzinfo=timezone.utc).timestamp())
        try:
            return JSONEncoder.default(self, val)
        except TypeError as e:
            if hasattr(val, 'to_dict'):
                return val.to_dict()
            raise e


def json(body, status=200, headers=None, content_type="application/json",
         **kwargs):
    return HTTPResponse(
        dumps(body, separators=(",", ":"), cls=APIJSONEncoder, **kwargs),
        headers=headers,
        status=status,
        content_type=content_type,
    )
