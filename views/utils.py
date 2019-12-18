from datetime import datetime, timezone
from json import JSONEncoder, dumps
from typing import Any, Dict, Optional

from sanic.response import HTTPResponse


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
