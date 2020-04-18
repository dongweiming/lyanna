#!/usr/bin/env python3
"""
该脚本用于同步models/文件夹里与django_migrations里的*.py内容，
主要是讲Meta里的table替换成db_table
"""
import re
from pathlib import Path

RE_TABLE = re.compile(r'^(\s+)(table = ["\']\w+["\'])$', flags=re.M)
TORTOISE_DJANGO = [
    ('from tortoise import fields', 'from .base import fields'),
    ('from tortoise.query_utils import Q', 'from django.db.models import Q'),
    (
        'from tortoise.query import QuerySet',
        'from django.db.models.query import QuerySet',
    ),
    ('from tortoise.models import ModelMeta', 'from .base import ModelMeta'),
    ('metaclass=ModelMeta', 'object'),
]


def convert_tortoise_orm_to_django_orm(s: str) -> str:
    '''将tortoise-orm转换为django-orm的语法'''
    expected = RE_TABLE.sub(r"\1db_\2", s)
    for i in TORTOISE_DJANGO:
        expected = expected.replace(*i)
    return expected


def main() -> None:
    # 注意：models/里不能有二级目录
    skip = "base.py"
    a, b = "models", "django_migrations/tortoise_orm/models"
    if (
        not (base_path := Path(__file__).parent)
        .joinpath('.gitignore')
        .exists()
    ):
        base_path = base_path.resolve().parent
    a_pys = base_path.joinpath(a).rglob("*.py")
    b_path = base_path / b
    b_files = set(i.name for i in b_path.rglob("*.py"))
    for i in a_pys:
        if i.name == skip:
            continue
        expected = convert_tortoise_orm_to_django_orm(i.read_text())
        if i.name not in b_files:
            cmd = f"cp {i} {b_path}"
            print('-->', cmd)
            b_path.joinpath(i.name).write_text(expected)
        elif (b_py := b_path / i.name).read_text() != expected:
            b_py.write_text(expected)
            print(f"{b_py} refreshed!")
    text = base_path.joinpath('config.py').read_text()
    config = base_path.joinpath('django_migrations/config.py')
    if not config.exists() or text != config.read_text():
        config.write_text(text)
        print(f'{config} created or updated.')


if __name__ == "__main__":
    main()
