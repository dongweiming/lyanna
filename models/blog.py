import re
import random
from datetime import datetime, timedelta
from html.parser import HTMLParser

import mistune
from tortoise import fields
from tortoise.query_utils import Q

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from .mc import cache, clear_mc
from .base import BaseModel
from .user import User
from .consts import K_POST, ONE_HOUR
from .utils import trunc_utf8
from .comment import CommentMixin
from .react import ReactMixin
from .toc import TocMixin

MC_KEY_TAGS_BY_POST_ID = 'post:%s:tags'
MC_KEY_RELATED = 'post:related_posts:%s'
MC_KEY_POST_BY_SLUG = 'post:%s:slug'
MC_KEY_ALL_POSTS = 'core:posts:%s'
MC_KEY_FEED = 'core:feed'
MC_KEY_SITEMAP = 'core:sitemap'
MC_KEY_SEARCH = 'core:search.json'
MC_KEY_ARCHIVES = 'core:archives'
MC_KEY_ARCHIVE = 'core:archive:%s'
MC_KEY_TAGS = 'core:tags:%s'
MC_KEY_TAG = 'core:tag:%s'
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
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = BlogHtmlFormatter(
            noclasses=inlinestyles, linenos=linenos,
            cssclass='highlight %s' % lang, lang=lang
        )
        code = highlight(text, lexer, formatter)
        return code
    except Exception:
        return '<pre class="%s"><code>%s</code></pre>\n' % (
            lang, mistune.escape(text)
        )


class BlogRenderer(mistune.Renderer):

    def header(self, text, level, raw=None):
        text = text.replace(' ', '')
        return f'<h{level} id="{text}">{text}</h{level}>\n'

    def block_code(self, text, lang):
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(text, lang, inlinestyles, linenos)


class TocRenderer(TocMixin, mistune.Renderer):
    ...


renderer = BlogRenderer(linenos=False, inlinestyles=False)
toc = TocRenderer()
markdown = mistune.Markdown(escape=True, renderer=renderer)
toc_md = mistune.Markdown(renderer=toc)


class Post(CommentMixin, ReactMixin, BaseModel):
    STATUSES = (
        STATUS_UNPUBLISHED,
        STATUS_ONLINE
    ) = range(2)

    TYPES = (TYPE_ARTICLE, TYPE_PAGE) = range(2)

    title = fields.CharField(max_length=100, unique=True)
    author_id = fields.IntField()
    slug = fields.CharField(max_length=100)
    summary = fields.CharField(max_length=255)
    can_comment = fields.BooleanField(default=True)
    status = fields.IntField(default=STATUS_UNPUBLISHED)
    type = fields.IntField(default=TYPE_ARTICLE)
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
        pts = await PostTag.filter(post_id=self.id)
        if not pts:
            return []
        ids = [pt.tag_id for pt in pts]
        return await Tag.filter(id__in=ids).all()

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
            Q(post_id__not=self.id), Q(tag_id__in=tag_ids),
            Q(created_at__gte=(datetime.now() - timedelta(days=180)))).values_list(  # noqa
                'post_id', flat=True))

        excluded_ids = await self.filter(
            Q(status__not=self.STATUS_ONLINE)).values_list('id', flat=True)

        post_ids -= set(excluded_ids)
        try:
            post_ids = random.sample(post_ids, limit)
        except ValueError:
            ...
        return await self.get_multi(post_ids)

    async def clear_mc(self):
        await clear_mc(MC_KEY_RELATED % self.id)
        await clear_mc(MC_KEY_POST_BY_SLUG % self.slug)
        for key in [MC_KEY_FEED, MC_KEY_SITEMAP, MC_KEY_SEARCH,
                    MC_KEY_ARCHIVES, MC_KEY_TAGS]:
            await clear_mc(key)
        for i in [True, False]:
            await clear_mc(MC_KEY_ALL_POSTS % i)
        await clear_mc(MC_KEY_ARCHIVE % self.created_at.year)

        for tag in await self.tags:
            await clear_mc(MC_KEY_TAG % tag.id)

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
        return f'/page/{self.slug}' if self.is_page else super().url


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

    class Meta:
        table = 'post_tags'

    @classmethod
    async def update_multi(cls, post_id, tags):
        tags = set(tags)
        origin_tags = set([t.name for t in (
            await Post.sync_get(id=post_id)).tags])
        need_add = tags - origin_tags
        need_del = origin_tags - tags
        need_add_tag_ids = set()
        need_del_tag_ids = set()
        for tag_name in need_add:
            tag, _ = await Tag.get_or_create(name=tag_name)
            need_add_tag_ids.add(tag.id)
        for tag_name in need_del:
            tag, _ = await Tag.get_or_create(name=tag_name)
            need_del_tag_ids.add(tag.id)

        if need_del_tag_ids:
            await cls.filter(Q(post_id=post_id),
                             Q(tag_id__in=need_del_tag_ids)).delete()
        for tag_id in need_add_tag_ids:
            await cls.get_or_create(post_id=post_id, tag_id=tag_id)

        await clear_mc(MC_KEY_TAGS_BY_POST_ID % post_id)
