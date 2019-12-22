from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, Iterator, List, Union
from urllib.parse import unquote

from arq.connections import RedisSettings as _RedisSettings

from config import AttrDict


def trunc_utf8(string: str, num: int, etc: str = '...') -> str:
    if num >= len(string):
        return string

    if etc:
        trunc_idx = num - len(etc)
    else:
        trunc_idx = num
    ret = string[:trunc_idx]
    if etc:
        ret += etc
    return ret


class Empty:

    def __call__(self, *a, **kw):
        return empty

    def __nonzero__(self):
        return False

    def __contains__(self, item):
        return False

    def __repr__(self):
        return '<Empty Object>'

    def __str__(self):
        return ''

    def __eq__(self, v):
        return isinstance(v, Empty)

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return empty

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def next(self):
        raise StopIteration

    def __getattr__(self, mname):
        return ''

    def __setattr__(self, name, value):
        return self

    def __delattr__(self, name):
        return self


empty = Empty()


class Pagination:

    def __init__(self, page: int, per_page: int, total: int,
                 items: List[AttrDict]) -> None:
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items

    @property
    def pages(self) -> int:
        if self.per_page == 0 or self.total is None:
            pages = 0
        else:
            pages = int(math.ceil(self.total / float(self.per_page)))
        return pages

    @property
    def prev_num(self):
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def next_num(self):
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge: int = 2, left_current: int = 2,
                   right_current: int = 2,
                   right_edge: int = 2) -> Iterator[Union[Iterator, Iterator[int],
                                                          None, int]]:
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or self.page - left_current - 1 < num < self.page + right_current  # noqa
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


def _parse_rfc1738_args(name: str) -> Dict[str, str]:
    pattern = re.compile(
        r"""
            (?P<name>[\w\+]+)://
            (?:
                (?P<username>[^:/]*)
                (?::(?P<password>.*))?
            @)?
            (?:
                (?:
                    \[(?P<ipv6host>[^/]+)\] |
                    (?P<ipv4host>[^/:]+)
                )?
                (?::(?P<port>[^/]*))?
            )?
            (?:/(?P<database>.*))?
            """,
        re.X,
    )

    if (m := pattern.match(name)) is not None:
        components = m.groupdict()  # type: ignore
        if components['database'] is not None:
            tokens = components['database'].split('?', 2)
            components['database'] = tokens[0]

        if components['password'] is not None:
            components['password'] = unquote(components['password'])

        ipv4host = components.pop('ipv4host')
        ipv6host = components.pop('ipv6host')
        components['host'] = ipv4host or ipv6host
        return components
    else:
        raise ValueError(
            f"Could not parse rfc1738 URL from string '{name}'"
        )


@dataclass
class RedisSettings(_RedisSettings):  # type: ignore
    @classmethod
    def from_url(cls, db_url: str) -> RedisSettings:
        url = _parse_rfc1738_args(db_url)
        return cls(url['host'], url['port'],
                   url['database'] and int(url['database']) or 0,
                   url['password'], 1, 5, 1)
