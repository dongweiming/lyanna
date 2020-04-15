from __future__ import annotations

from collections import defaultdict
from typing import Any, DefaultDict, Dict, List

from tortoise import fields

from .base import BaseModel
from .consts import K_COMMENT
from .mc import cache, clear_mc, mc
from .signals import comment_reacted
from .utils import cached_property, empty

MC_KEY_USER_REACT_STAT = 'react:stats:%s:%s'
MC_KEY_REACTION_ITEM_BY_USER_TARGET = 'react:reaction_item:%s:%s:%s'
MC_KEY_TARGET_N_LIKES = 'react:stats:n_likes:%s:%s'
MC_KEY_TARGET_N_UPVOTES = 'react:stats:n_upvotes:%s:%s'


class ReactItem(BaseModel):
    target_id = fields.IntField()
    target_kind = fields.IntField()
    user_id = fields.IntField()
    reaction_type = fields.IntField()

    REACTION_KINDS = (
        K_UPVOTE,
        K_FUNNY,
        K_LOVE,
        K_SURPRISED,
        K_SAD
    ) = range(5)
    REACTION_MAP = {
        'upvote': K_UPVOTE,
        'funny': K_FUNNY,
        'love': K_LOVE,
        'surprised': K_SURPRISED,
        'sad': K_SAD
    }

    class Meta:
        table = 'react_items'

    @classmethod
    async def create(cls, **kwargs) -> ReactItem:
        obj = await super().create(**kwargs)
        react_name = next((name for name, type in cls.REACTION_MAP.items()
                           if type == obj.reaction_type), None)
        stat = await ReactStats.get_by_target(obj.target_id, obj.target_kind)
        field = f'{react_name}_count'
        setattr(stat, field, getattr(stat, field) + 1)
        await stat.save()
        return obj

    @classmethod
    @cache(MC_KEY_REACTION_ITEM_BY_USER_TARGET % (
        '{user_id}', '{target_id}', '{target_kind}'))
    async def get_reaction_items(cls, user_id, target_id, target_kind):
        return await cls.filter(user_id=user_id, target_id=target_id,
                                target_kind=target_kind).all()

    async def delete(self, using_db=None) -> ReactItem:
        rv = await super().delete(using_db=using_db)  # type: ignore
        stat = await ReactStats.get_by_target(self.target_id, self.target_kind)
        react_name = next((name for name, type in self.REACTION_MAP.items()
                           if type == self.reaction_type), None)
        field = f'{react_name}_count'

        setattr(stat, field, max(getattr(stat, field) - 1, 0))
        await stat.save()
        return rv

    async def clear_mc(self):
        await clear_mc(MC_KEY_REACTION_ITEM_BY_USER_TARGET % (
            self.user_id, self.target_id, self.target_kind))

        if self.target_kind == K_COMMENT:
            comment_reacted.send(user_id=self.user_id,
                                 comment_id=self.target_id)

    async def incr(self):
        default = 0
        if self.reaction_type in (self.K_UPVOTE, self.K_LOVE):
            default = await self.filter(target_id=self.target_id,
                                        target_kind=self.target_kind,
                                        reaction_type=self.reaction_type).count()
        if self.reaction_type == self.K_UPVOTE:
            return await mc.incr(MC_KEY_TARGET_N_UPVOTES % (
                self.target_id, self.target_kind), default=default)
        elif self.reaction_type == self.K_LOVE:
            return await mc.incr(MC_KEY_TARGET_N_LIKES % (
                self.target_id, self.target_kind), default=default)

    async def decr(self):
        if self.reaction_type == self.K_UPVOTE:
            return await mc.decr(MC_KEY_TARGET_N_UPVOTES % (
                self.target_id, self.target_kind))
        elif self.reaction_type == self.K_LOVE:
            return await mc.decr(MC_KEY_TARGET_N_LIKES % (
                self.target_id, self.target_kind))


class ReactStats(BaseModel):
    target_id = fields.IntField()
    target_kind = fields.IntField()
    upvote_count = fields.IntField(default=0)
    funny_count = fields.IntField(default=0)
    love_count = fields.IntField(default=0)
    surprised_count = fields.IntField(default=0)
    sad_count = fields.IntField(default=0)

    @classmethod
    @cache(MC_KEY_USER_REACT_STAT % ('{target_id}', '{target_kind}'))
    async def get_by_target(cls, target_id: int, target_kind: int) -> ReactStats:
        rv = await cls.filter(target_id=target_id,
                              target_kind=target_kind).first()
        if not rv:
            rv = await cls.create(target_id=target_id, target_kind=target_kind)
        return rv

    async def clear_mc(self):
        await clear_mc(MC_KEY_USER_REACT_STAT % (
            self.target_id, self.target_kind))


class ReactMixin:
    id: int
    kind: int

    async def add_reaction(self, user_id, reaction_type):
        items = await ReactItem.get_reaction_items(user_id, self.id, self.kind)
        if not items or not any(i for i in items if reaction_type == i.reaction_type):
            item = await ReactItem.create(
                target_id=self.id, target_kind=self.kind,
                user_id=user_id, reaction_type=reaction_type)
            return bool(item)
        return True

    async def cancel_reaction(self, user_id, reaction_type=None):
        items = await ReactItem.get_reaction_items(user_id, self.id, self.kind)
        if items:
            if reaction_type is not None:
                for item in items:
                    await item.delete()
            else:
                if (item := next((
                        i for i in items if reaction_type == i.reaction_type),
                                 None)) is not None:
                    await item.delete()
        return True

    @cached_property
    async def stats(self) -> ReactStats:
        return await ReactStats.get_by_target(self.id, self.kind)

    async def get_reaction_type(self, user_id):
        items = await ReactItem.get_reaction_items(user_id, self.id, self.kind)
        return items[0].reaction_type if items else None

    @property  # type: ignore
    @cache(MC_KEY_TARGET_N_LIKES % ('{self.id}', '{self.kind}'), serialize=False,
           parser=int)
    async def n_likes(self):
        return (await self.stats).love_count

    @property  # type: ignore
    @cache(MC_KEY_TARGET_N_UPVOTES % ('{self.id}', '{self.kind}'), serialize=False,
           parser=int)
    async def n_upvotes(self):
        return (await self.stats).upvote_count

    @classmethod
    async def get_reactions_by_targets(
            cls, target_ids: List[int], user_id: int) -> Dict:
        target_kind = cls.kind
        keys = [MC_KEY_REACTION_ITEM_BY_USER_TARGET % (
            user_id, target_id, target_kind) for target_id in target_ids]
        values = await mc.get_multi(*keys)
        cached = {id: v for id, v in zip(target_ids, values) if v is not None}
        missed_ids = [id for id in target_ids if id not in cached]
        if not missed_ids:
            return {k: v for k, v in cached.items() if v}
        reactions = await ReactItem.filter(user_id=user_id, target_id__in=missed_ids,
                                           target_kind=target_kind).all()
        missed_cached: DefaultDict[int, Any] = defaultdict(list)
        for r in reactions:
            missed_cached[r.target_id].append(r)
        cached.update(missed_cached)
        for id in missed_ids:
            if id not in missed_cached:
                missed_cached[id] = empty
        missed_keys = [MC_KEY_REACTION_ITEM_BY_USER_TARGET % (
            user_id, target_id, target_kind) for target_id in missed_cached]
        if missed_keys:
            await mc.set_multi(missed_keys, missed_cached.values())
        return cached
