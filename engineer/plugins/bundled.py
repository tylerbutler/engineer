# coding=utf-8
import logging
import re

from codecs import open
from path import path
import yaml

# noinspection PyPackageRequirements
from typogrify.templatetags.jinja_filters import register

from engineer.enums import Status
from engineer.filters import compress, format_datetime, img, localtime, markdown_filter, \
    naturaltime, typogrify_no_widont
from engineer.log import log_object
from engineer.plugins.core import PostProcessor, JinjaEnvironmentPlugin
from engineer.util import flatten_list

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


class PostBreaksProcessor(PostProcessor):
    _regex = re.compile(r'^(?P<teaser_content>.*?)(?P<break>\s*<?!?-{2,}\s*more\s*-{2,}>?)\s*(?P<rest_of_content>.*)',
                        re.DOTALL)

    default_settings = {
        'enabled': True
    }

    @classmethod
    def preprocess(cls, post, metadata):
        from engineer.models import Post

        if not cls.is_enabled():
            return post

        # First check if either form of the break marker is present using the regex
        parsed_content = re.match(cls._regex, post.content_preprocessed)
        if parsed_content is None or parsed_content.group('teaser_content') is None:
            post.content_teaser = None
            return post

        # Post is meant to be broken apart, so normalize the break marker to the HTML comment form.
        post.content_preprocessed = unicode(parsed_content.group('teaser_content') +
                                            '\n\n<!-- more -->\n\n' +
                                            parsed_content.group('rest_of_content'))

        # Convert the full post to HTML, then use the regex again to split the resulting HTML post. This is needed
        # since Markdown might have links in the first half of the post that are listed at the bottom. By converting
        # the whole post to HTML first then splitting we get a correctly processed HTML teaser.
        parsed_content = re.match(cls._regex, post.content)
        post.content_teaser = parsed_content.group('teaser_content')
        return post


class FinalizationPlugin(PostProcessor):
    _finalize_map_defaults = {
        'timestamp': [Status.published],
        'title': [Status.published, Status.review, Status.draft],
        'slug': [Status.published, Status.review, Status.draft],
        'url': [Status.review, Status.published]
    }
    _fenced_metadata_formats = ('fenced', 'jekyll', 'octopress')
    _unfenced_metadata_formats = ('unfenced', 'engineer',)
    _default_metadata_format = 'input'

    setting_name = 'FINALIZE_METADATA'
    default_settings = {
        'config': _finalize_map_defaults,
        'format': _default_metadata_format
    }

    disabled_msg = "A metadata finalization config is specified but the plugin is disabled."

    @classmethod
    def handle_settings(cls, config_dict, settings):
        logger = cls.get_logger()
        plugin_settings, user_supplied_settings = cls.initialize_settings(config_dict)

        # POST METADATA FINALIZATION SETTINGS
        if not cls.is_enabled and 'config' in user_supplied_settings:
            cls.log_once(cls.disabled_msg, 'disabled_msg', logging.WARNING)
        elif 'config' in user_supplied_settings:
            for metadata_attribute, statuses in user_supplied_settings['config'].iteritems():
                plugin_settings['config'][metadata_attribute] = [Status(s) for s in statuses]

        valid_metadata_formats = set(flatten_list((
            cls._default_metadata_format,
            cls._fenced_metadata_formats,
            cls._unfenced_metadata_formats,
        )))

        if plugin_settings['format'] not in valid_metadata_formats:
            logger.warning("'%s' is not a valid METADATA_FORMAT setting. Defaulting to '%s'.",
                           plugin_settings.format, cls._default_metadata_format)
            plugin_settings.format = cls._default_metadata_format

        cls.store_settings(plugin_settings)
        return config_dict

    @classmethod
    def preprocess(cls, post, metadata):
        if cls.is_enabled():
            # Get the list of metadata that's specified directly in the source file -- this metadata we *always* want
            # to ensure gets output during finalization. Store it on the post object,
            # then we'll use it later in the postprocess method.
            post.metadata_original = set(metadata.keys())
        return post, metadata

    @classmethod
    def postprocess(cls, post):
        logger = cls.get_logger()
        if cls.is_enabled():
            metadata_format = cls.get_settings()['format']
            if metadata_format in cls._fenced_metadata_formats:
                logger.debug("METADATA_FORMAT is '%s', metadata will always be fenced during normalization.",
                             metadata_format)
                post._fence = True
            elif metadata_format in cls._unfenced_metadata_formats:
                logger.debug("METADATA_FORMAT is '%s', metadata will always be unfenced during normalization.",
                             metadata_format)
                post._fence = False
            output = cls.render_markdown(post)
            if cls.need_update(post, output):
                logger.debug("Finalizing metadata for post '%s'" % post)
                with open(post.source, mode='wb', encoding='UTF-8') as the_file:
                    the_file.write(output)
            else:
                logger.debug("No metadata finalization needed for post '%s'" % post)
        return post

    # noinspection PyProtectedMember
    @classmethod
    def need_update(cls, post, new_post_content):
        from engineer.models import Post

        old = Post._regex.match(post._file_contents_raw)
        new = Post._regex.match(new_post_content)

        old_fenced = (old.group('fence') is not None)
        if old_fenced != post._fence:
            return True

        old_metadata = old.group('metadata').strip()
        new_metadata = new.group('metadata').strip()

        if new_metadata != old_metadata:
            return True

        old_content = old.group('content').strip()
        new_content = new.group('content').strip()

        if new_content != old_content:
            return True
        else:
            return False

    @staticmethod
    def render_markdown(post):
        """
        Renders the post as Markdown using the template specified in :attr:`markdown_template_path`.
        """
        from engineer.conf import settings

        # A hack to guarantee the YAML output is in a sensible order.
        # The order, assuming all metadata should be written, should be:
        # title
        # status
        # timestamp
        # link
        # via
        # via-link
        # slug
        # tags
        # updated
        # template
        # content-template
        # url
        d = [
            ('status', post.status.name),
            ('link', post.link),
            ('via', post.via),
            ('via-link', post.via_link),
            ('tags', post.tags),
            ('updated', post.updated_local.strftime(settings.TIME_FORMAT) if post.updated is not None else None),
            ('template', post.template if post.template != 'theme/post_detail.html' else None),
            ('content-template',
             post.content_template if post.content_template != 'theme/_content_default.html' else None),
        ]

        # The complete set of metadata that should be written is the union of the FINALIZE_METADATA.config setting and
        # the set of metadata that was in the file originally.
        finalization_config = FinalizationPlugin.get_settings()['config']
        metadata_to_finalize = set([m for m, s in finalization_config.iteritems() if post.status in s])
        metadata_to_finalize.update(post.metadata_original)

        if 'title' in metadata_to_finalize:
            # insert at the top of the list
            d.insert(0, ('title', post.title))
        if 'slug' in metadata_to_finalize:
            # insert right before tags
            d.insert(d.index(('tags', post.tags)), ('slug', post.slug))
        if 'timestamp' in metadata_to_finalize:
            # insert right after status
            d.insert(d.index(('status', post.status.name)), ('timestamp',
                                                             post.timestamp_local.strftime(settings.TIME_FORMAT)))
        if 'url' in metadata_to_finalize:
            # insert at end of list
            d.append(('url', post.url))

        metadata = ''
        for k, v in d:
            if v is not None and len(v) > 0:
                metadata += yaml.safe_dump(dict([(k, v)]), default_flow_style=False)

        # handle custom metadata
        if len(post.custom_properties):
            metadata += '\n'
            metadata += yaml.safe_dump(dict(post.custom_properties), default_flow_style=False)
        return settings.JINJA_ENV.get_template(post.markdown_template_path).render(metadata=metadata,
                                                                                   content=post.content_finalized,
                                                                                   post=post)


class PostRenamerPlugin(PostProcessor):
    _default_config = {
        Status.published: u'({status_short}) {year}-{month}-{day} {slug}.md',
        Status.draft: u'({status}) {slug}.md',
        Status.review: u'({status}) {year}-{month}-{day} {slug}.md'
    }

    setting_name = 'POST_RENAME'
    default_settings = {
        'config': _default_config
    }

    @classmethod
    def handle_settings(cls, config_dict, settings):
        logger = cls.get_logger()
        plugin_settings, user_supplied_settings = cls.initialize_settings(config_dict)

        if 'config' in user_supplied_settings:
            config = cls.default_settings['config'].copy()
            custom_config = dict([(Status(k), v) for k, v in user_supplied_settings['config'].iteritems()])
            config.update(custom_config)
            plugin_settings['config'] = config

        logger.debug("Setting the %s setting to %s." % (cls.get_setting_name(), log_object(plugin_settings)))
        cls.store_settings(plugin_settings)
        return config_dict

    @classmethod
    def postprocess(cls, post):
        logger = cls.get_logger()

        if not cls.is_enabled():
            logger.debug("Post Renamer plugin disabled.")
            return post  # early return - plugin is disabled

        config = cls.get_settings()['config']
        mask = config[post.status]
        logger.debug("In postprocess, config is: %s" % log_object(config))
        if mask is None:
            logger.debug("Not renaming post '%s' since its status is configured to be ignored." % post)
            return post

        new_file_name = mask.format(year=unicode(post.timestamp_local.year),
                                    month=u'{0:02d}'.format(post.timestamp_local.month),
                                    day=u'{0:02d}'.format(post.timestamp_local.day),
                                    i_month=post.timestamp_local.month,
                                    i_day=post.timestamp_local.day,
                                    timestamp=post.timestamp_local,
                                    status=post.status.name,
                                    status_short=post.status.name[:1],
                                    slug=post.slug,
                                    post=post)
        new_file = post.source.parent / new_file_name

        if new_file == post.source:
            logger.debug("No need to rename post '%s'; it already has the correct name." % post)
            return post

        if new_file.exists():
            logger.warning("Couldn't rename post %s to %s." %
                           (post.source.abspath(), new_file.abspath()))
            logger.warning("   A file with that name already exists. Skipping it.")
            return post

        post.source.rename(new_file)
        post.source = new_file
        logger.info("Renamed post '%s' to %s." % (post.title, new_file.abspath()))
        return post


class GlobalLinksPlugin(PostProcessor):
    setting_name = 'GLOBAL_LINKS'
    default_settings = {
        'file': 'global_links.md',
        'post_link_enabled': True
    }
    not_enabled_log_message = "Settings don't include a %s setting, " \
                              "so Global Links plugin will not run." % setting_name
    file_not_found_message = "Global Links file %s not found. Global Links plugin will not run."
    error_displayed = False  # flag so 'file not found' error is only displayed once per build

    @classmethod
    def preprocess(cls, post, metadata):
        from engineer.conf import settings

        if not cls.is_enabled():
            cls.log_once(cls.not_enabled_log_message, 'disabled', logging.INFO)
            return post, metadata  # early return

        file_path = path(cls.get_settings()['file']).expand()
        if not file_path.isabs():
            file_path = (settings.SETTINGS_DIR / file_path).abspath()
        try:
            with open(file_path, 'rb') as f:
                global_links = f.read()
        except IOError:
            cls.log_once(cls.file_not_found_message % file_path, 'fnf', logging.ERROR)
            return

        post.stash_content(global_links)
        return post, metadata


class PostLinkPlugin(PostProcessor):
    setting_name = 'POST_LINK'
    default_settings = {
        'enabled': True
    }

    @classmethod
    def preprocess(cls, post, metadata):
        if post.is_external_link:
            if cls.is_enabled():
                post.stash_content('\n[post-link]: %s' % post.link)
            else:
                cls.log_once("PostLink plugin is disabled and will not run.", 'disabled')


class LazyMarkdownLinksPlugin(PostProcessor):
    # Inspired by Brett Terpstra: http://brettterpstra.com/2013/10/19/lazy-markdown-reference-links/
    setting_name = 'LAZY_LINKS'
    default_settings = {
        'enabled': True,
        'persist': False
    }

    _link_regex = re.compile(r'''
        (           # Start group 1, which is the actual link text
            \[          # Match a literal [
            [^\]]+      # Match anything except a literal ] - this will be the link text itself
            \]          # Match a literal ]
            \s*         # Any whitespace (including newlines)
            \[          # Match the opening bracket of the lazy link marker
        )           # End group 1
        \*          # Literal * - this is the lazy link marker
        (           # Start group 2, which is everything after the lazy link marker
            \]          # Literal ]
            .*?^        # Non-greedy match of anything up to a new line
            \[          # Literal [
        )           # End Group 2
        \*\]:       # Match a literal *]: - the lazy link URL definition follows this
        ''', re.MULTILINE | re.DOTALL | re.UNICODE | re.VERBOSE)

    _counter_regex = re.compile(r'\[(\d+)\]:', re.UNICODE)
    _counter = 0

    @classmethod
    def _replace(cls, match):
        cls._counter += 1
        sub_str = '%s%s%s%s]:' % (match.group(1), cls._counter, match.group(2), cls._counter)
        return sub_str

    @staticmethod
    def get_max_link_number(post):
        all_values = set([int(i) for i in LazyMarkdownLinksPlugin._counter_regex.findall(post)])
        return max(all_values) if all_values else 0

    @classmethod
    def preprocess(cls, post, metadata):
        logger = cls.get_logger()
        content = post.content_preprocessed
        cls._counter = cls.get_max_link_number(content)

        # This while loop ensures we handle overlapping matches
        while cls._link_regex.search(content):
            content = cls._link_regex.sub(cls._replace, content)
        post.content_preprocessed = content
        if cls.get_settings()['persist']:
            if not post.set_finalized_content(content, cls):
                logger.warning("Failed to persist lazy links.")
        return post, metadata


class JinjaPostProcessor(PostProcessor):
    setting_name = 'JINJA_POSTPROCESSOR'
    default_settings = {
        'enabled': True,
    }
    not_enabled_log_message = "JinjaPostProcessor plugin is disabled."

    @classmethod
    def preprocess(cls, post, metadata):
        from engineer.conf import settings

        if not cls.is_enabled():
            cls.log_once(cls.not_enabled_log_message, 'disabled', logging.INFO)
            return post, metadata  # early return

        template = settings.JINJA_ENV.from_string(post.content_preprocessed)
        post.content_preprocessed = template.render()
        return post, metadata


class ContentTemplateProcessor(PostProcessor):
    default_settings = {
        'enabled': True,
    }

    @classmethod
    def preprocess(cls, post, metadata):
        from engineer.conf import settings
        from engineer.models import Post

        logger = cls.get_logger()

        if post.content_template != Post.DEFAULT_CONTENT_TEMPLATE:
            logger.debug("Using non-default content template '%s' for post '%s'." % (post.content_template, post))

        template = settings.JINJA_ENV.get_template(post.content_template)
        post.content_preprocessed = template.render(post=post, content=post.content_preprocessed)
        return post, metadata


class BundledFilters(JinjaEnvironmentPlugin):
    filters = {
        'date': format_datetime,
        'markdown': markdown_filter
    }
    filters.update(dict([(f.__name__, f) for f in [localtime, naturaltime, compress, typogrify_no_widont, img]]))

    globals = {
        'img': img
    }

    @classmethod
    def update_environment(cls, jinja_env):
        super(BundledFilters, cls).update_environment(jinja_env)

        logger = cls.get_logger()
        register(jinja_env)  # register typogrify filters
        logger.debug("Registered typogrify filters.")


class PythonMarkdownRenderer(PostRenderer):
    supported_input_formats = ('.markdown', '.md', '.mdown')
    supported_output_formats = ('.html',)

    def render(self, content, input_format, output_format='.html'):
        import markdown

        self.validate(input_format, output_format)

        return markdown.markdown(content, extensions=['extra', 'codehilite'])


# class PandocRenderer(PostRenderer):
# supported_input_formats = ('.markdown', '.md', '.mdown')
# supported_output_formats = ('.html',)
#
# format_map = {
# '.markdown': 'markdown',
# '.md': 'markdown',
# '.mdown': 'markdown',
# }
#
# def render(self, content, input_format, output_format='.html'):
# import pypandoc
#
# logger = self.get_logger()
#         self.validate(input_format, output_format)
#
#         try:
#             f = self.format_map[input_format] + '-footnotes-pipe_tables'
#             logger.error(f)
#             return pypandoc.convert(content, 'html5',
#                                     format='markdown_mmd',
#                                     extra_args=('--highlight-style=tango',))
#         except OSError:
#             logger.error("Can't find Pandoc...")
#             raise


# class CommonMarkRenderer(PostRenderer):
#     import CommonMark
#
#     supported_input_formats = ('.markdown', '.md', '.mdown')
#     supported_output_formats = ('.html',)
#
#     parser = CommonMark.DocParser()
#     renderer = CommonMark.HTMLRenderer()
#
#     def render(self, content, input_format, output_format='.html'):
#
#         logger = self.get_logger()
#         self.validate(input_format, output_format)
#
#         ast = self.parser.parse(content)
#
#         return self.renderer.render(ast)

import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter


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
