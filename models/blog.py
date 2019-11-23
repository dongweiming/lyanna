import re
import ast
import types
import random
import inspect
from datetime import datetime, timedelta
from html.parser import HTMLParser

import pangu
import mistune
from tortoise import fields
from aioredis.errors import RedisError
from tortoise.query_utils import Q
from tortoise.models import ModelMeta

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from config import PERMALINK_TYPE
from .mc import cache, clear_mc
from .base import BaseModel
from .user import User
from .consts import K_POST, ONE_HOUR, PERMALINK_TYPES
from .utils import trunc_utf8
from .comment import CommentMixin
from .react import ReactMixin
from .toc import TocMixin

MC_KEY_TAGS_BY_POST_ID = 'post:%s:tags'
MC_KEY_RELATED = 'post:related_posts:%s'
MC_KEY_POST_BY_SLUG = 'post:%s:slug'
MC_KEY_ALL_POSTS = 'core:posts:%s:v2'
MC_KEY_FEED = 'core:feed'
MC_KEY_SITEMAP = 'core:sitemap'
MC_KEY_SEARCH = 'core:search.json'
MC_KEY_ARCHIVES = 'core:archives'
MC_KEY_ARCHIVE = 'core:archive:%s'
MC_KEY_TAGS = 'core:tags'
MC_KEY_TAG = 'core:tag:%s'
MC_KEY_SPECIAL_ITEMS = 'special:%s:items'
MC_KEY_SPECIAL_POST_ITEMS = 'special:%s:post_items'
MC_KEY_SPECIAL_BY_PID = 'special:by_pid:%s'
MC_KEY_SPECIAL_BY_SLUG = 'special:%s:slug'
MC_KEY_ALL_SPECIAL_TOPICS = 'special:topics'
RK_PAGEVIEW = 'lyanna:pageview:{}'
RK_VISITED_POST_IDS = 'lyanna:visited_post_ids'
BQ_REGEX = re.compile(r'<blockquote>.*?</blockquote>')


class MLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class PanguMeta(type):
    def __new__(cls, name, bases, attrs):
        for base in bases:
            for name, fn in inspect.getmembers(base):
                if (isinstance(fn, types.FunctionType) and
                        name not in ('codespan', 'paragraph')):
                    try:
                        idx = inspect.getfullargspec(fn).args.index('text')
                    except ValueError:
                        continue
                    setattr(base, name, cls.deco(fn, idx))

        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def deco(cls, func, index):
        def wrapper(*args, **kwargs):
            _args = list(args)
            _args[index] = pangu.spacing_text(_args[index])
            result = func(*_args, **kwargs)
            return result
        return wrapper


class BlogHtmlFormatter(HtmlFormatter):

    def __init__(self, **options):
        super().__init__(**options)
        self.lang = options.get('lang', '')

    def _wrap_div(self, inner):
        style = []
        if (self.noclasses and not self.nobackground and
                self.style.background_color is not None):
            style.append('background: %s' % (self.style.background_color,))
        if self.cssstyles:
            style.append(self.cssstyles)
        style = '; '.join(style)

        yield 0, ('<figure' + (self.cssclass and ' class="%s"' % self.cssclass) +  # noqa
                  (style and (' style="%s"' % style)) +
                  (self.lang and ' data-lang="%s"' % self.lang) +
                  '><table><tbody><tr><td class="code">')
        for tup in inner:
            yield tup
        yield 0, '</table></figure>\n'

    def _wrap_pre(self, inner):
        style = []
        if self.prestyles:
            style.append(self.prestyles)
        if self.noclasses:
            style.append('line-height: 125%')
        style = '; '.join(style)

        if self.filename:
            yield 0, ('<span class="filename">' + self.filename + '</span>')

        # the empty span here is to keep leading empty lines from being
        # ignored by HTML parsers
        yield 0, ('<pre' + (style and ' style="%s"' % style) + (
            self.lang and f' class="hljs {self.lang}"') + '><span></span>')
        for tup in inner:
            yield tup
        yield 0, '</pre>'


def block_code(text, lang, inlinestyles=False, linenos=False):
    if not lang:
        text = text.strip()
        return '<pre><code>%s</code></pre>\n' % mistune.escape(text)

    try:
        if lang in ('py', 'python'):
            lang = 'python3'
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = BlogHtmlFormatter(
            noclasses=inlinestyles, linenos=linenos,
            cssclass='highlight %s' % lang, lang=lang
        )
        code = highlight(text, lexer, formatter)
        return code
    except Exception:
        # Github Card
        if lang == 'card':
            try:
                dct = ast.literal_eval(text)
                user = dct.get('user')
                if user:
                    repo = dct.get('repo')
                    card_html = f'''<div class="github-card" data-user="{ user }" { f'data-repo="{ repo }"' if repo else "" }></div>'''  # noqa
                    if dct.get('right'):
                        card_html = f'<div class="card-right">{card_html}</div>'  # noqa
                    return card_html
            except (ValueError, SyntaxError):
                ...

        return '<pre class="%s"><code>%s</code></pre>\n' % (
            lang, mistune.escape(text)
        )


class BlogRenderer(mistune.Renderer, metaclass=PanguMeta):
    def header(self, text, level, raw=None):
        hid = text.replace(' ', '')
        return f'<h{level} id="{hid}">{text}</h{level}>\n'

    def block_code(self, code, lang):
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(code, lang, inlinestyles, linenos)

    def link(self, link, title, text):
        return f' {super().link(link, title, text) } '


class TocRenderer(TocMixin, mistune.Renderer):
    ...


renderer = BlogRenderer(linenos=False, inlinestyles=False)
toc = TocRenderer()
markdown = mistune.Markdown(escape=True, renderer=renderer)
toc_md = mistune.Markdown(renderer=toc)


class StatusMixin(metaclass=ModelMeta):
    STATUSES = (
        STATUS_UNPUBLISHED,
        STATUS_ONLINE
    ) = range(2)
    status = fields.SmallIntField(default=STATUS_UNPUBLISHED)


class Post(CommentMixin, ReactMixin, StatusMixin, BaseModel):

    TYPES = (TYPE_ARTICLE, TYPE_PAGE) = range(2)

    title = fields.CharField(max_length=100, unique=True)
    author_id = fields.IntField()
    slug = fields.CharField(max_length=100)
    summary = fields.CharField(max_length=255)
    can_comment = fields.BooleanField(default=True)
    type = fields.IntField(default=TYPE_ARTICLE)
    _pageview = fields.IntField(source_field='pageview', default=0)
    kind = K_POST

    class Meta:
        table = 'posts'

    @classmethod
    async def create(cls, **kwargs):
        tags = kwargs.pop('tags', [])
        content = kwargs.pop('content')
        obj = await super().create(**kwargs)
        if tags:
            await PostTag.update_multi(obj.id, tags)
        await obj.set_content(content)
        return obj

    async def update_tags(self, tagnames):
        if tagnames:
            await PostTag.update_multi(self.id, tagnames)
        return True

    @property
    @cache(MC_KEY_TAGS_BY_POST_ID % ('{self.id}'))
    async def tags(self):
        pts = await PostTag.filter(post_id=self.id).order_by('updated_at').all()
        if not pts:
            return []
        ids = [pt.tag_id for pt in pts]
        tags = await Tag.filter(id__in=ids).all()
        return sorted(tags, key=lambda t: ids.index(t.id))

    @property
    async def author(self):
        rv = await User.cache(self.author_id)
        return rv

    @property
    def preview_url(self):
        return f'/{self.__class__.__name__.lower()}/{self.id}/preview'

    async def set_content(self, content):
        return await self.set_props_by_key('content', content)

    async def save(self, *args, **kwargs):
        content = kwargs.pop('content', None)
        if content is not None:
            await self.set_content(content)
        return await super().save(*args, **kwargs)

    @property
    async def content(self):
        rv = await self.get_props_by_key('content')
        if rv:
            return rv.decode('utf-8')

    @property
    async def html_content(self):
        content = await self.content
        if not content:
            return ''
        return markdown(content)

    @property
    async def excerpt(self):
        if self.summary:
            return self.summary
        s = MLStripper()
        s.feed(await self.html_content)
        return trunc_utf8(BQ_REGEX.sub('', s.get_data()).replace('\n', ''), 100)  # noqa

    @cache(MC_KEY_RELATED % ('{self.id}'), ONE_HOUR)
    async def get_related(self, limit=4):
        tag_ids = [tag.id for tag in await self.tags]
        if not tag_ids:
            return []
        post_ids = set(await PostTag.filter(
            Q(post_id__not=self.id), Q(tag_id__in=tag_ids)).values_list(
                'post_id', flat=True))

        excluded_ids = await self.filter(
            Q(created_at__lt=(datetime.now() - timedelta(days=180))) |
            Q(status__not=self.STATUS_ONLINE)).values_list('id', flat=True)

        post_ids -= set(excluded_ids)
        try:
            post_ids = random.sample(post_ids, limit)
        except ValueError:
            ...
        return await self.get_multi(post_ids)

    async def clear_mc(self):
        keys = [
            MC_KEY_FEED, MC_KEY_SITEMAP, MC_KEY_SEARCH, MC_KEY_ARCHIVES,
            MC_KEY_TAGS, MC_KEY_RELATED % self.id,
            MC_KEY_POST_BY_SLUG % self.slug,
            MC_KEY_ARCHIVE % self.created_at.year]
        for i in [True, False]:
            keys.append(MC_KEY_ALL_POSTS % i)

        for tag in await self.tags:
            keys.append(MC_KEY_TAG % tag.id)
        await clear_mc(*keys)
        await SpecialTopic.flush_by_pid(self.id)

    @classmethod
    @cache(MC_KEY_POST_BY_SLUG % '{slug}')
    async def get_by_slug(cls, slug):
        return await cls.filter(slug=slug).first()

    @classmethod
    @cache(MC_KEY_ALL_POSTS % '{with_page}')
    async def get_all(cls, with_page=True):
        if with_page:
            return await Post.sync_filter(status=Post.STATUS_ONLINE,
                                          orderings=['-id'], limit=None)
        return await Post.sync_filter(status=Post.STATUS_ONLINE,
                                      type__not=cls.TYPE_PAGE,
                                      orderings=['-id'], limit=None)

    @classmethod
    async def cache(cls, ident):
        if str(ident).isdigit():
            return await super().cache(ident)
        return await cls.get_by_slug(ident)

    @property
    async def toc(self):
        content = await self.content
        if not content:
            return ''
        toc.reset_toc()
        toc_md.parse(content)
        return toc.render_toc(level=4)

    @property
    def is_page(self):
        return self.type == self.TYPE_PAGE

    @property
    def url(self):
        if self.is_page:
            return f'/page/{self.slug}'
        assert PERMALINK_TYPE in PERMALINK_TYPES
        return f'/post/{getattr(self, PERMALINK_TYPE) or self.id}/'

    async def incr_pageview(self, increment=1):
        redis = await self.redis
        try:
            await redis.sadd(RK_VISITED_POST_IDS, self.id)
            return await redis.incrby(RK_PAGEVIEW.format(self.id), increment)
        except RedisError:
            return self._pageview

    @property
    async def pageview(self):
        try:
            return int(await (await self.redis).get(
                RK_PAGEVIEW.format(self.id)) or 0)
        except RedisError:
            return self._pageview


class Tag(BaseModel):
    name = fields.CharField(max_length=100, unique=True)

    class Meta:
        table = 'tags'

    @classmethod
    def get_by_name(cls, name):
        return cls.filter(name=name).first()

    @classmethod
    def create(cls, **kwargs):
        name = kwargs.pop('name')
        kwargs['name'] = name.lower()
        return super().create(**kwargs)


class PostTag(BaseModel):
    post_id = fields.IntField()
    tag_id = fields.IntField()
    updated_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'post_tags'

    @classmethod
    async def update_multi(cls, post_id, tags):
        origin_tags = set([t.name for t in (
            await Post.sync_get(id=post_id)).tags])
        need_add = set(tags) - origin_tags
        need_del = origin_tags - set(tags)
        need_add_tag_ids = []
        need_del_tag_ids = set()
        for tag_name in need_add:
            tag, _ = await Tag.get_or_create(name=tag_name)
            need_add_tag_ids.append([tag.id, tag_name])
        for tag_name in need_del:
            tag, _ = await Tag.get_or_create(name=tag_name)
            need_del_tag_ids.add(tag.id)

        if need_del_tag_ids:
            await cls.filter(Q(post_id=post_id),
                             Q(tag_id__in=need_del_tag_ids)).delete()
        for tag_id, _ in sorted(need_add_tag_ids,
                                key=lambda x: tags.index(x[1])):
            print(tag_id, _)
            await cls.get_or_create(post_id=post_id, tag_id=tag_id)

        await clear_mc(MC_KEY_TAGS_BY_POST_ID % post_id)


class SpecialItem(BaseModel):
    post_id = fields.IntField()
    index = fields.SmallIntField()
    special_id = fields.SmallIntField()

    class Meta:
        table = 'special_item'

    @classmethod
    @cache(MC_KEY_SPECIAL_BY_PID % ('{post_id}'))
    async def get_special_id_by_pid(cls, post_id):
        return await SpecialItem.filter(post_id=post_id).values_list(
            'special_id', flat=True)


class SpecialTopic(StatusMixin, BaseModel):
    id = fields.SmallIntField()
    intro = fields.CharField(max_length=2000)
    slug = fields.CharField(max_length=100)
    title = fields.CharField(max_length=100, unique=True)

    class Meta:
        table = 'special_topic'

    @cache(MC_KEY_SPECIAL_POST_ITEMS % ('{self.id}'))
    async def get_post_items(self):
        items = await self.get_items()
        post_ids = [s.post_id for s in items]
        if not post_ids:
            return []
        posts = await Post.filter(id__in=post_ids).all()
        return sorted(posts, key=lambda p: post_ids.index(p.id))

    @cache(MC_KEY_SPECIAL_ITEMS % ('{self.id}'))
    async def get_items(self):
        return await SpecialItem.filter(special_id=self.id).order_by(
            'index').all()

    async def set_indexes(self, indexes):
        origin_map = {i.post_id: i for i in await self.get_items()}
        pids = [pid for pid, index in indexes]
        need_del_pids = set(origin_map) - set(pids)

        if need_del_pids:
            await SpecialItem.filter(Q(special_id=self.id),
                                     Q(post_id__in=need_del_pids)).delete()
        for pid, index in indexes:
            if pid in origin_map:
                special = origin_map[pid]
                if index != special.index:
                    special.index = index
                    await special.save()
            else:
                await SpecialItem.get_or_create(
                    post_id=pid, special_id=self.id, index=index)

        await clear_mc(MC_KEY_SPECIAL_ITEMS % self.id,
                       MC_KEY_SPECIAL_POST_ITEMS % self.id)

    @classmethod
    async def flush_by_pid(cls, post_id):
        special_ids = SpecialItem.get_special_id_by_pid(post_id)
        keys = [MC_KEY_SPECIAL_ITEMS % i for i in special_ids]
        keys.extend([MC_KEY_SPECIAL_POST_ITEMS % i for i in special_ids])
        keys.append(MC_KEY_SPECIAL_BY_PID % post_id)
        await clear_mc(*keys)

    @property
    async def n_posts(self):
        return len(await self.get_post_items())

    @property
    async def posts(self):
        return [{'id': p.id, 'title': p.title}
                for p in await self.get_post_items()]

    @property
    def url(self):
        return f'/special/{self.slug or self.id}'

    @classmethod
    @cache(MC_KEY_SPECIAL_BY_SLUG % '{slug}')
    async def get_by_slug(cls, slug):
        return await cls.filter(slug=slug).first()

    @classmethod
    @cache(MC_KEY_ALL_SPECIAL_TOPICS)
    async def get_all(cls):
        return await cls.sync_filter(status=cls.STATUS_ONLINE,
                                     orderings=['-id'], limit=None)

    @classmethod
    async def cache(cls, ident):
        if str(ident).isdigit():
            return await super().cache(ident)
        return await cls.get_by_slug(ident)

    async def clear_mc(self):
        keys = [
            MC_KEY_SPECIAL_BY_SLUG % self.slug,
            MC_KEY_SPECIAL_POST_ITEMS % self.id,
            MC_KEY_SPECIAL_ITEMS % self.id,
            MC_KEY_ALL_SPECIAL_TOPICS
        ]
        await clear_mc(*keys)
