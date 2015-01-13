# coding=utf-8
from engineer.plugins import PostRenderer

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


class PythonMarkdownRenderer(PostRenderer):
    supported_input_formats = ('.markdown', '.md', '.mdown')
    supported_output_formats = ('.html',)

    def render(self, content, input_format, output_format='.html'):
        import markdown

        self.validate(input_format, output_format)

        return markdown.markdown(content, extensions=['extra', 'codehilite'])


class PandocRenderer(PostRenderer):
    supported_input_formats = ('.markdown', '.md', '.mdown')
    supported_output_formats = ('.html',)

    format_map = {
        '.markdown': 'markdown',
        '.md': 'markdown',
        '.mdown': 'markdown',
    }

    def render(self, content, input_format, output_format='.html'):
        # noinspection PyPackageRequirements
        import pypandoc

        logger = self.get_logger()
        self.validate(input_format, output_format)

        try:
            f = self.format_map[input_format] + '-footnotes-pipe_tables'
            logger.error(f)
            return pypandoc.convert(content, 'html5',
                                    format='markdown_mmd',
                                    extra_args=('--highlight-style=tango',))
        except OSError:
            logger.error("Can't find Pandoc...")
            raise


class CommonMarkRenderer(PostRenderer):
    # noinspection PyPackageRequirements
    import CommonMark

    supported_input_formats = ('.markdown', '.md', '.mdown')
    supported_output_formats = ('.html',)

    parser = CommonMark.DocParser()
    renderer = CommonMark.HTMLRenderer()

    def render(self, content, input_format, output_format='.html'):
        logger = self.get_logger()
        self.validate(input_format, output_format)

        ast = self.parser.parse(content)

        return self.renderer.render(ast)

try:
    # noinspection PyPackageRequirements
    import mistune
except ImportError:
    mistune = None

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter


if mistune:
    class MistuneSyntaxHighlightRenderer(mistune.Renderer):
        def block_code(self, code, lang=None):
            if not lang:
                return '\n<pre><code>%s</code></pre>\n' % mistune.escape(code)
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = HtmlFormatter(linenos='table')
            highlighted = highlight(code, lexer, formatter)

            return '<div class="codehilite">%s</div>' % highlighted

    class MistuneRenderer(PostRenderer):
        supported_input_formats = ('.markdown', '.md', '.mdown')
        supported_output_formats = ('.html',)

        def render(self, content, input_format, output_format='.html'):
            logger = self.get_logger()
            logger.warning("using mistune")

            self.validate(input_format, output_format)
            renderer = MistuneSyntaxHighlightRenderer()
            md = mistune.Markdown(renderer=renderer)
            return md.render(content)
