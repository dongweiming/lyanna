import os
import json
from pathlib import Path

from jsonschema import validate

from config import HERE
from .mc import cache, clear_mc
from .utils import AttrDict

schema = {
    "type": "object",
    "properties": {
        "intro": {"type": "string"},
        "github_url": {"type": "string"},
        "avatar": {"type": "string"},
        "linkedin_url": {"type": "string"}
    },
}
MC_KEY_PROFILE = 'profile'
PROFILE_FILE = 'profile.json'


@cache(MC_KEY_PROFILE)
async def get_profile():
    file = Path(HERE) / PROFILE_FILE
    if not os.path.exists(file):
        return {}

    with open(file) as f:
        return AttrDict(json.load(f))


async def set_profile(**kw):
    validate(kw, schema)
    with open(Path(HERE) / PROFILE_FILE, 'w') as f:
        json.dump(kw, f)
        await clear_mc(MC_KEY_PROFILE)
