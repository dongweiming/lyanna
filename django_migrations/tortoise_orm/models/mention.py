import re
from typing import List

from tortoise.query_utils import Q

from models.user import GithubUser

MENTION_LIMIT = 20
_METION_UID_RE = re.compile(r'@([a-zA-Z0-9][-.\w]*?)(?![-.\w])')
EMAIL_SUBJECT = '有人在 {title} 的评论中提到了你!'


class Mention:
    @staticmethod
    def _parse_mention_names(author: GithubUser, content: str = '') -> List[str]:
        names = set(name for name in _METION_UID_RE.findall(content)
                    if name and name != author.username)
        return list(names)[:MENTION_LIMIT]

    @classmethod
    async def get_mention_users(cls, content: str, author_id: int) -> List[GithubUser]:
        if not (author := await GithubUser.cache(author_id)):
            return []
        mention_names = cls._parse_mention_names(author, content)
        return await GithubUser.filter(Q(username__in=mention_names))
