from typing import Optional

from django.db import models


def tortoise_to_django(kwargs: dict) -> dict:
    kwargs.pop("verbose_name", None)
    if (db_column := kwargs.pop('source_field', None)) is not None:
        kwargs['db_column'] = db_column
    if (pk := kwargs.pop('pk', None)) is not None:
        kwargs['primary_key'] = pk
    return kwargs


class CharField(models.CharField):
    def __init__(
        self, max_length: int, description: Optional[str] = None, **kwargs
    ):
        kwargs = tortoise_to_django(kwargs)
        super().__init__(description, max_length=max_length, **kwargs)


class IntField(models.IntegerField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs = tortoise_to_django(kwargs)
        super().__init__(description, **kwargs)


class SmallIntField(models.SmallIntegerField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs = tortoise_to_django(kwargs)
        super().__init__(description, **kwargs)


class JSONField(models.TextField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs = tortoise_to_django(kwargs)
        super().__init__(description, **kwargs)


class TextField(models.TextField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs = tortoise_to_django(kwargs)
        super().__init__(description, **kwargs)


class BooleanField(models.BooleanField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs = tortoise_to_django(kwargs)
        super().__init__(description, **kwargs)


class DatetimeField(models.DateTimeField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs = tortoise_to_django(kwargs)
        super().__init__(description, **kwargs)


class DecimalField(models.DecimalField):
    def __init__(
        self,
        max_digits: int,
        decimal_places: int,
        description: Optional[str] = None,
        **kwargs,
    ):
        kwargs = tortoise_to_django(kwargs)
        super().__init__(
            description,
            max_digits=max_digits,
            decimal_places=decimal_places,
            **kwargs,
        )
