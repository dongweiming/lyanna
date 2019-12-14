import ast
import inspect
import types
from typing import Any, Callable

import mistune
import pangu
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from .toc import TocMixin


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
    def deco(cls, func: Callable, index: int) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> str:
            _args = list(args)
            _args[index] = pangu.spacing_text(_args[index])
            result = func(*_args, **kwargs)
            return result
        return wrapper


class BlogHtmlFormatter(HtmlFormatter):  # type: ignore

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


def block_code(text: str, lang: str, inlinestyles: bool = False,
               linenos: bool = False) -> str:
    if not lang:
        text = text.strip()
        return '<pre><code>%s</code></pre>\n' % mistune.escape(text)

    try:
        if lang in ('py', 'python'):
            lang = 'python3'
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = BlogHtmlFormatter(  # type: ignore
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
                if (user := dct.get('user')):
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


class BlogRenderer(mistune.Renderer, metaclass=PanguMeta):  # type: ignore
    def header(self, text, level, raw=None):
        hid = text.replace(' ', '')
        return f'<h{level} id="{hid}">{text}</h{level}>\n'

    def block_code(self, code, lang):
        inlinestyles = self.options.get('inlinestyles')
        linenos = self.options.get('linenos')
        return block_code(code, lang, inlinestyles, linenos)

    def link(self, link, title, text):
        return f' {super().link(link, title, text) } '


class TocRenderer(TocMixin, mistune.Renderer):  # type:ignore
    ...


renderer = BlogRenderer(linenos=False, inlinestyles=False)
toc = TocRenderer()
markdown = mistune.Markdown(escape=True, renderer=renderer)
toc_md = mistune.Markdown(renderer=toc)
