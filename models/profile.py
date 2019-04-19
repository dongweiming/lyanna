import os
import json
from pathlib import Path

import attr

from config import HERE
from .mc import cache, clear_mc

MC_KEY_PROFILE = 'profile'
PROFILE_FILE = 'profile.json'


@attr.s
class Profile:
    intro = attr.ib(default='', validator=attr.validators.instance_of(str))
    github_url = attr.ib(default='',
                         validator=attr.validators.instance_of(str))
    avatar = attr.ib(default='', repr=False,
                     validator=attr.validators.instance_of(str))
    linkedin_url = attr.ib(default='', repr=False,
                           validator=attr.validators.instance_of(str))

    @classmethod
    @cache(MC_KEY_PROFILE)
    async def get(cls):
        file = Path(HERE) / PROFILE_FILE
        if not os.path.exists(file):
            return {}

        with open(file) as f:
            return attr.asdict(cls(**json.load(f)))

    @classmethod
    async def set(cls, **kw):
        profile = cls(**kw)
        with open(Path(HERE) / PROFILE_FILE, 'w') as f:
            json.dump(attr.asdict(profile), f)
            await clear_mc(MC_KEY_PROFILE)
