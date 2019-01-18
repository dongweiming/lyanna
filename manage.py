from pathlib import Path

import click
import cssmin
from tortoise import Tortoise, run_async
from tortoise.exceptions import IntegrityError

from config import HERE
from ext import init_db
from models import create_user


async def init():
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
        'alter table comments add index `idx_post_id` (`post_id`)')
    await client.execute_script(
        'alter table react_items add index `idx_id_kind_user` (`target_id`, `target_kind`, `user_id`)')  # noqa


@click.group()
def cli():
    ...


@cli.command()
def initdb():
    run_async(init())
    click.echo('Init Finished!')


async def _adduser(**kwargs):
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
        'main.min.css': ['pure-min.css', 'base.css'],
        'index.min.css': ['main.min.css', 'fontawesome.min.css'],
        'post.min.css': ['main.min.css', 'post.css', 'react.css',
                         'gitment.css', 'social-sharer.css']
    }
    css_map = {}
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
