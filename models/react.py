from tortoise import fields

from .base import BaseModel
from .mc import cache, clear_mc
from .consts import K_COMMENT
from .signals import comment_reacted

MC_KEY_USER_REACT_STAT = 'react:stats:%s:%s'
MC_KEY_REACTION_ITEM_BY_USER_TARGET = 'react:reaction_item:%s:%s:%s'


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
    async def create(cls, **kwargs):
        obj = await super().create(**kwargs)
        react_name = next((name for name, type in cls.REACTION_MAP.items()
                           if type == obj.reaction_type), None)
        stat = await ReactStats.get_by_target(obj.target_id, obj.target_kind)
        field = f'{react_name}_count'
        setattr(stat, field, getattr(stat, field) + 1)
        await stat.save()
        return obj

    @classmethod
    @cache(MC_KEY_REACTION_ITEM_BY_USER_TARGET % ('{user_id}', '{target_id}',
                                                  '{target_kind}'))
    async def get_reaction_item(cls, user_id, target_id, target_kind):
        rv = await cls.filter(user_id=user_id, target_id=target_id,
                              target_kind=target_kind).first()
        return rv

    async def delete(self, using_db=None):
        rv = await super().delete(using_db=using_db)
        stat = await ReactStats.get_by_target(self.target_id, self.target_kind)
        react_name = next((name for name, type in self.REACTION_MAP.items()
                           if type == self.reaction_type), None)
        field = f'{react_name}_count'
        setattr(stat, field, getattr(stat, field) - 1)
        await stat.save()
        return rv

    async def clear_mc(self):
        await clear_mc(MC_KEY_REACTION_ITEM_BY_USER_TARGET % (
            self.user_id, self.target_id, self.target_kind))

        if self.target_kind == K_COMMENT:
            comment_reacted.send(user_id=self.user_id,
                                 comment_id=self.target_id)


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
    async def get_by_target(cls, target_id, target_kind):
        rv = await cls.filter(target_id=target_id,
                              target_kind=target_kind).first()
        if not rv:
            rv = await cls.create(target_id=target_id,
                                  target_kind=target_kind)
        return rv

    async def clear_mc(self):
        await clear_mc(MC_KEY_USER_REACT_STAT % (
            self.target_id, self.target_kind))


class ReactMixin:
    async def add_reaction(self, user_id, reaction_type):
        item = await ReactItem.get_reaction_item(user_id, self.id, self.kind)
        if item and reaction_type == item.reaction_type:
            await item.save()
            return True
        if not item:
            item = await ReactItem.create(
                target_id=self.id, target_kind=self.kind,
                user_id=user_id, reaction_type=reaction_type)
        else:
            item.reaction_type = reaction_type
            await item.save()

        return bool(item)

    async def cancel_reaction(self, user_id):
        item = await ReactItem.get_reaction_item(user_id, self.id, self.kind)
        if item:
            await item.delete()
        return True

    @property
    async def stats(self):
        return await ReactStats.get_by_target(self.id, self.kind)

    async def get_reaction_type(self, user_id):
        item = await ReactItem.get_reaction_item(user_id, self.id, self.kind)
        return item.reaction_type if item else None
