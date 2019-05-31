import glob
import argparse

from tortoise import run_async
from tortoise.exceptions import IntegrityError
import yaml

from ext import init_db
from models import Post

parser = argparse.ArgumentParser(description='Hexo Exporter')
parser.add_argument('source_dirs', metavar='DIR', type=str, nargs='+',
                    help='Markdown file directories')
parser.add_argument('--uid', type=int, help='Author ID')
args = parser.parse_args()
source_dirs = args.source_dirs

if not args.uid:
    print('the `uid` argument are required!')
    exit(1)

files = []

for dir in source_dirs:
    files.extend(sum([glob.glob(f'{dir}/*.{pattern}')
                      for pattern in ('md', 'markdown')], []))

files = sorted(files, reverse=False)


async def write_post(file):
    flag = False
    meta_info = ''

    with open(file) as f:
        for i in f:
            i = i.strip()
            if i == '---' and flag:
                break
            if i == '---':
                flag = True
                continue
            meta_info += i + '\n'

        meta_dict = yaml.load(meta_info, yaml.SafeLoader)
        title = meta_dict['title']
        date = meta_dict.get('date') or meta_dict.get('created')
        tags = meta_dict.get('tags', [])
        if not (title and date):
            print(f"[Fail] Parse meta failed in {file.name}")
            return
        content = ''.join(f.readlines())

        try:
            await Post.create(title=title, content=content, tags=tags,
                              author_id=args.uid, slug='', summary='',
                              status=Post.STATUS_ONLINE, created_at=date)
            print(f"[Success] Load post: {file.name}")
        except IntegrityError:
            ...


async def main():
    await init_db()
    for f in files:
        await write_post(f)


if __name__ == '__main__':
    run_async(main())
