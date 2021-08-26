from pathlib import Path
from typing import Dict

import click
import cssmin
from tortoise import Tortoise, run_async
from tortoise.exceptions import IntegrityError, OperationalError

from config import HERE
from ext import init_db
from models import create_user
from models.blog import PAGEVIEW_FIELD, RK_ALL_POST_IDS, RK_PAGEVIEW
from models.utils import get_redis


async def init() -> None:
    await init_db(create_db=False)
    await Tortoise._drop_databases()
    await init_db(create_db=True)
    await Tortoise.generate_schemas()

    # Add Indexes
    client = Tortoise.get_connection('default')
    await client.execute_script(
        'alter table posts add index `idx_slug` (`slug`)')
    await client.execute_script(
        'alter table post_tags add index `idx_post_tag` (`post_id`, `tag_id`)')
    await client.execute_script(
        'alter table comments add index `idx_target_kind` (`target_id`, `target_kind`)')
    await client.execute_script(
        'alter table react_items add index `idx_id_kind_user` (`target_id`, `target_kind`, `user_id`)')  # noqa

    if not await client.execute_query(
            'show columns from `posts` like "pageview"'):
        await migrate_for_v25()

    try:
        await migrate_for_v35()
    except OperationalError:
        ...


async def _migrate_for_v25() -> None:
    await init_db(create_db=False)
    client = Tortoise.get_connection('default')
    await client.execute_script(
        'alter table posts add column `pageview` int(11) DEFAULT "0"')


async def _migrate_for_v27() -> None:
    redis = await get_redis()
    keys = await redis.keys('lyanna:pageview:*')
    ids = []
    for k in keys:
        id = k.split(b':')[-1]
        if id.isdigit():
            await redis.hset(RK_PAGEVIEW.format(id.decode()), PAGEVIEW_FIELD,
                             int(await redis.get(k)))
            ids.append(id)
    await redis.sadd(RK_ALL_POST_IDS, *ids)
    await init_db(create_db=False)
    client = Tortoise.get_connection('default')
    await client.execute_script(
        '''CREATE TABLE `special_item` (
        `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
        `post_id` int(11) NOT NULL,
        `index` smallint(6) NOT NULL,
        `special_id` smallint(6) NOT NULL,
        `created_at` datetime(6) NOT NULL,
        PRIMARY KEY (`id`),
        KEY `idx_special_post` (`special_id`,`post_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8''')
    await client.execute_script(
        '''CREATE TABLE `special_topic` (
        `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
        `intro` varchar(2000) NOT NULL,
        `title` varchar(100) NOT NULL,
        `created_at` datetime(6) NOT NULL,
        `status` smallint(6) NOT NULL DEFAULT '0',
        `slug` varchar(100) NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE KEY `title` (`title`),
        KEY `idx_slug` (`slug`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8''')

    await client.execute_script(
        ('alter table post_tags add column `updated_at` datetime(6) '
         'DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)'))
    await client.execute_script('alter table users add column `avatar` varchar(100) DEFAULT ""')  # noqa


async def _migrate_for_v30() -> None:
    await init_db(create_db=False)
    client = Tortoise.get_connection('default')
    await client.execute_script(
        '''CREATE TABLE `activity` (
        `can_comment` tinyint(1) NOT NULL,
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `created_at` datetime(6) NOT NULL,
        `user_id` int(11) NOT NULL,
        `target_id` int(11) NOT NULL,
        `target_kind` int(11) NOT NULL,
        PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    await client.execute_script(
        '''CREATE TABLE `statuses` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `created_at` datetime(6) NOT NULL,
        `user_id` int(11) NOT NULL,
        PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    await client.execute_script(
        'ALTER TABLE comments CHANGE `post_id` `target_id` int(11) NOT NULL')
    await client.execute_script(
        'alter table comments add column `target_kind` smallint(6) DEFAULT 1001')


async def _migrate_for_v35() -> None:
    await init_db(create_db=False)
    client = Tortoise.get_connection('default')
    await client.execute_script(
        'alter table activity add index `idx_target_kind` (`target_id`, `target_kind`)')  # noqa


@click.group()
def cli():
    ...


@cli.command()
def initdb():
    run_async(init())
    click.echo('Init Finished!')


@cli.command()
def migrate_for_v25():
    run_async(_migrate_for_v25())
    click.echo('Migrate Finished!')


@cli.command()
def migrate_for_v27():
    run_async(_migrate_for_v27())
    click.echo('Migrate Finished!')


@cli.command()
def migrate_for_v30():
    run_async(_migrate_for_v30())
    click.echo('Migrate Finished!')


@cli.command()
def migrate_for_v35():
    run_async(_migrate_for_v35())
    click.echo('Migrate Finished!')


async def _adduser(**kwargs) -> None:
    await init_db()
    try:
        user = await create_user(**kwargs)
    except IntegrityError as e:
        click.echo(str(e))
    else:
        click.echo(f'User {user.name} created!!! ID: {user.id}')


@cli.command()
@click.option('--name', required=True, prompt=True)
@click.option('--email', required=False, default=None, prompt=True)
@click.option('--password', required=True, prompt=True, hide_input=True,
              confirmation_prompt=True)
def adduser(name, email, password):
    run_async(_adduser(name=name, password=password, email=email))


@cli.command()
def build_css():
    build_map = {
        'main.min.css': ['pure-min.css', 'base.css', 'iconfont.css'],
        'index.min.css': ['main.min.css', 'balloon.min.css', 'index.css',
                          'widget.css'],
        'topic.min.css': ['main.min.css', 'topic.css'],
        'post.min.css': ['main.min.css', 'post.css', 'react.css',
                         'gitment.css', 'dracula.css', 'social-sharer.css']
    }
    css_map: Dict[str, str] = {}
    css_dir = Path(HERE) / 'static/css/'
    for css, files in build_map.items():
        data = ''
        for file in files:
            if file in css_map:
                data += css_map[file]
            else:
                with open(css_dir / file) as f:
                    data_ = f.read()
                    css_map[file] = data_
                data += data_
        with open(css_dir / css, 'w') as f:
            f.write(cssmin.cssmin(data))
            css_map[css] = data


if __name__ == '__main__':
    cli()
