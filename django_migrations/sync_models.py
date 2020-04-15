#!/usr/bin/env python3
"""
该脚本用于同步models/文件夹里与django_migrations里的*.py内容，
主要是讲Meta里的table替换成db_table
"""
import re
from pathlib import Path

RE_TABLE = re.compile(r'^(\s+)(table = "\w+")$', flags=re.M)


def main() -> None:
    # 注意：models/里不能有二级目录
    skip = "base.py"
    a, b = "models", "django_migrations/tortoise_orm/models"
    a_pys = Path(a).rglob("*.py")
    b_path = Path(b)
    b_files = set(i.name for i in b_path.rglob("*.py"))
    for i in a_pys:
        if i.name == skip or ".bak" in str(i):
            continue
        if i.name not in b_files:
            cmd = f"cp {i} {b_path}"
            print('-->', cmd)
            b_path.joinpath(i.name).write_text(i.read_text())
        else:
            b_py = b_path / i.name
            sa, sb = i.read_text(), b_py.read_text()
            expected = RE_TABLE.sub(r"\1db_\2", sa)
            if sb != expected:
                b_py.write_text(expected)
                print(f"{b_py} refreshed!")
    text = Path('config.py').read_text()
    if not (config := Path('django_migrations/config.py')).exists() or text != config.read_text():
        config.write_text(text)
        print(f'{config} created or updated.')


if __name__ == "__main__":
    main()
