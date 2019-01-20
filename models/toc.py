# coding: utf-8
# Modified from https://github.com/lepture/mistune-contrib


class TocMixin:

    """TOC mixin for Renderer, mix this with Renderer::

        class TocRenderer(TocMixin, Renderer):
            pass

        toc = TocRenderer()
        md = mistune.Markdown(renderer=toc)

        # required in this order
        toc.reset_toc()          # initial the status
        md.parse(text)           # parse for headers
        toc.render_toc(level=3)  # render TOC HTML
    """

    def reset_toc(self):
        self.toc_tree = []
        self.toc_count = 0

    def header(self, text, level, raw=None):
        rv = '<h%d id="toc-%d">%s</h%d>\n' % (
            level, self.toc_count, text, level
        )
        self.toc_tree.append((self.toc_count, text, level, raw))
        self.toc_count += 1
        return rv

    def render_toc(self, level=3):
        """Render TOC to HTML.

        :param level: render toc to the given level
        """
        return ''.join(self._iter_toc(level))

    def _iter_toc(self, level):
        first_level = 0
        last_level = 0

        yield '<div id="toc" class="toc-article"><strong class="toc-title">目录</strong><ol class="toc">\n'  # noqa

        for toc in self.toc_tree:
            index, text, l, raw = toc
            title = text.replace(' ', '')

            if l > level:
                # ignore this level
                continue

            if first_level == 0:
                # based on first level
                first_level = l
                last_level = l
                yield f'<li class="toc-item toc-level-{l - 1}"><a class="toc-link" href="#{title}"><span class="toc-text">{text}</span></a>'  # noqa
            elif last_level == l:
                yield f'</li>\n<li class="toc-item toc-level-{l - 1}"><a class="toc-link" href="#{title}"><span class="toc-text">{text}</span></a>'  # noqa
            elif last_level == l - 1:
                last_level = l
                yield f'<ol class="toc-child">\n<li class="toc-item toc-level-{l - 1}"><a class="toc-link" href="#{title}"><span class="toc-text">{text}</span></a>'  # noqa
            elif last_level > l:
                yield '</li>'
                while last_level > l:
                    yield '</ol>\n</li>\n'
                    last_level -= 1
                yield '<li><a href="#toc-%d">%s</a>' % (index, text)

        # close tags
        yield '</li>\n'
        while last_level > first_level:
            yield '</ul>\n</li>\n'
            last_level -= 1

        yield '</ul></div>\n'
