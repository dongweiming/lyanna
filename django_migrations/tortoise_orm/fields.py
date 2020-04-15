from typing import Optional

from django.db import models


class CharField(models.CharField):
    def __init__(
        self, max_length: int, description: Optional[str] = None, **kwargs
    ):
        kwargs.pop("verbose_name", None)
        super().__init__(description, max_length=max_length, **kwargs)


class IntField(models.IntegerField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs.pop("verbose_name", None)
        super().__init__(description, **kwargs)


class JSONField(models.TextField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs.pop("verbose_name", None)
        super().__init__(description, **kwargs)


class TextField(models.TextField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs.pop("verbose_name", None)
        super().__init__(description, **kwargs)


class BooleanField(models.BooleanField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs.pop("verbose_name", None)
        super().__init__(description, **kwargs)


class DatetimeField(models.DateTimeField):
    def __init__(self, description: Optional[str] = None, **kwargs):
        kwargs.pop("verbose_name", None)
        super().__init__(description, **kwargs)


class DecimalField(models.DecimalField):
    def __init__(
        self,
        max_digits: int,
        decimal_places: int,
        description: Optional[str] = None,
        **kwargs
    ):
        kwargs.pop("verbose_name", None)
        super().__init__(
            description,
            max_digits=max_digits,
            decimal_places=decimal_places,
            **kwargs
        )
