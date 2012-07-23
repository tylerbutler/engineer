# coding=utf-8
import logging
import markdown
import re
import times
import yaml
from codecs import open
from datetime import datetime
from dateutil import parser
from flufl.enum._enum import Enum
from path import path
from typogrify.templatetags.jinja2_filters import typogrify
from yaml.scanner import ScannerError
from zope.cachedescriptors.property import CachedProperty
from engineer.conf import settings
from engineer.exceptions import PostMetadataError
from engineer.filters import localtime
from engineer.plugins import PostProcessor
from engineer.util import setonce, slugify, chunk, urljoin, wrap_list

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

logger = logging.getLogger(__name__)

class Status(Enum):
    """Enum representing the status of a :class:`~Post`."""
    draft = 0 #: Post is a draft.
    published = 1 #: Post is published.
    review = 2 #: Post is in review.

    def __reduce__(self):
        return 'Status'


class Post(object):
    """
    Represents a post written in Markdown and stored in a file.

    :param source: path to the source file for the post.
    """
    _regex = re.compile(r'^[\n|\r\n]*(?P<fence>---)?[\n|\r\n]*(?P<metadata>.+?)[\n|\r\n]*---[\n|\r\n]*(?P<content>.*)[\n|\r\n]*', re.DOTALL)

    # Make _content_raw only settable once. This is just to help prevent data loss that might be caused by
    # inadvertantly messing with this property.
    _content_raw = setonce()

    @staticmethod
    def convert_to_html(content):
        return typogrify(markdown.markdown(content, extensions=['extra', 'codehilite']))

    def __init__(self, source):
        self.source = path(source).abspath()
        """The absolute path to the source file for the post."""

        self.html_template_path = 'theme/post_detail.html'
        """The path to the template to use to transform the post into HTML."""

        self.markdown_template_path = 'core/post.md'
        """The path to the template to use to transform the post back into a :ref:`post source file <posts>`."""

        # This will get set to `True in _parse_source if the source file has 'fenced metadata' (like Jekyll)
        self._fence = False

        metadata, self._content_raw = self._parse_source()

        if not hasattr(self, 'content_preprocessed'):
            self.content_preprocessed = self.content_raw

        # Handle any preprocessor plugins
        for plugin in PostProcessor.plugins:
            plugin.preprocess(self, metadata)

        self.title = metadata.pop('title', self.source.namebase.replace('-', ' ').replace('_', ' '))
        """The title of the post."""

        self.slug = metadata.pop('slug', slugify(self.title))
        """The slug for the post."""

        self.tags = wrap_list(metadata.pop('tags', []))
        """A list of strings representing the tags applied to the post."""

        self.link = metadata.pop('link', None)
        """The post's :ref:`external link <post link>`."""

        self.via = metadata.pop('via', None)
        """The post's attribution name."""

        self.via_link = metadata.pop('via-link', metadata.pop('via_link', None))
        """The post's attribution link."""

        try:
            self.status = Status(metadata.pop('status', Status.draft.name))
            """The status of the post (published or draft)."""

        except ValueError:
            logger.warning("'%s': Invalid status value in metadata. Defaulting to 'draft'." % self.title)
            self.status = Status.draft

        self.timestamp = metadata.pop('timestamp', None)
        """The date/time the post was published or written."""

        if self.timestamp is None:
            self.timestamp = times.now()
            utctime = True
        else:
            utctime = False

        if not isinstance(self.timestamp, datetime):
            # looks like the timestamp from YAML wasn't directly convertible to a datetime, so we need to parse it
            self.timestamp = parser.parse(str(self.timestamp))

        if self.timestamp.tzinfo is not None:
            # parsed timestamp has an associated timezone, so convert it to UTC
            self.timestamp = times.to_universal(self.timestamp)
        elif not utctime:
            # convert to UTC assuming input time is in the DEFAULT_TIMEZONE
            self.timestamp = times.to_universal(self.timestamp, settings.POST_TIMEZONE)

        self.content = Post.convert_to_html(self.content_preprocessed)
        """The post's content in HTML format."""

        self.markdown_file_name = unicode.format(settings.NORMALIZE_INPUT_FILE_MASK,
                                                 self.status.name[:1],
                                                 self.timestamp_local.strftime('%Y-%m-%d'),
                                                 #times.format(self.timestamp, settings.DEFAULT_TIMEZONE, '%Y-%m-%d'),
                                                 self.slug)
        self.url = unicode.format(u'{0}{1}/{2}/',
                                  settings.HOME_URL,
                                  self.timestamp_local.strftime('%Y/%m/%d'),
                                  self.slug)
        """The site-relative URL to the post."""

        self.absolute_url = unicode.format(u'{0}{1}', settings.SITE_URL, self.url)
        """The absolute URL to the post."""

        self.output_path = path(settings.OUTPUT_CACHE_DIR / self.timestamp_local.strftime('%Y/%m/%d') / self.slug)
        self.output_file_name = 'index.html'#'%s.html' % self.slug

        # keep track of any remaining properties in the post metadata
        metadata.pop('url', None) # remove the url property from the metadata dict before copy
        self.custom_properties = metadata.copy()
        """A dict of any custom metadata properties specified in the post."""

        # handle any postprocessor plugins
        for plugin in PostProcessor.plugins:
            plugin.postprocess(self)

        self._normalize_source()

        # update cache
        settings.POST_CACHE[self.source] = self

    @property
    def content_raw(self):
        return self._content_raw

    @property
    def is_draft(self):
        """``True`` if the post is a draft, ``False`` otherwise."""
        return self.status == Status.draft

    @property
    def is_published(self):
        """``True`` if the post is published, ``False`` otherwise."""
        return self.status == Status.published and self.timestamp <= times.now()

    @property
    def is_pending(self):
        """``True`` if the post is marked as published but has a timestamp set in the future."""
        return self.status == Status.published and self.timestamp >= times.now()

    @property
    def is_external_link(self):
        """``True`` if the post has an associated external link. ``False`` otherwise."""
        return self.link is not None and self.link != ''

    @property
    def timestamp_local(self):
        """
        The post's :attr:`timestamp` in 'local' time.

        Local time is determined by the :attr:`~engineer.conf.EngineerConfiguration.POST_TIMEZONE` setting.
        """
        return localtime(self.timestamp)

    def _parse_source(self):
        try:
            with open(self.source, mode='r') as file:
                item = unicode(file.read())
        except UnicodeDecodeError:
            with open(self.source, mode='r', encoding='UTF-8') as file:
                item = file.read()

        parsed_content = re.match(self._regex, item)

        if parsed_content is None or parsed_content.group('metadata') is None:
            # Parsing failed, maybe there's no metadata
            raise PostMetadataError()

        if parsed_content.group('fence') is not None:
            self._fence = True

        # 'Clean' the YAML section since there might be tab characters
        metadata = parsed_content.group('metadata').replace('\t', '    ')
        try:
            metadata = yaml.load(metadata)
        except ScannerError:
            raise PostMetadataError("YAML error parsing metadata.")

        if not isinstance(metadata, dict):
            raise PostMetadataError("Metadata isn't a dict. Instead, it's a %s." % type(metadata))
        content = parsed_content.group('content')

        return metadata, content

    def _normalize_source(self):
        if settings.NORMALIZE_INPUT_FILES:
            output = self.render_markdown()
            output_filename = (self.source.dirname() / self.markdown_file_name).abspath()
            with open(output_filename, mode='wb', encoding='UTF-8') as file:
                file.write(output)

            if self.source.abspath() != output_filename:
                # remove the original source file unless it has
                # the same name as the new target file
                self.source.remove_p()

            self.source = output_filename
        return

    def render_html(self, all_posts=None):
        """
        Renders the Post as HTML using the template specified in :attr:`html_template_path`.

        :param all_posts: An optional :class:`PostCollection` containing all of the posts in the site.
        :return: The rendered HTML as a string.
        """
        index = all_posts.index(self)
        if index > 0: # has newer posts
            newer_post = all_posts[index - 1]
        else:
            newer_post = None

        if index < len(all_posts) - 1: # has older posts
            older_post = all_posts[index + 1]
        else:
            older_post = None
        return settings.JINJA_ENV.get_template(self.html_template_path).render(post=self,
                                                                               newer_post=newer_post,
                                                                               older_post=older_post,
                                                                               all_posts=all_posts,
                                                                               nav_context='post')

    def render_markdown(self):
        """
        Renders the post as Markdown using the template specified in :attr:`markdown_template_path`.

        This method is used to output a post during the :ref:`post normalization` process.
        """

        # A hack to guarantee the YAML output is in a sensible order.
        d = (
            ('title', self.title),
            ('status', self.status.name),
            ('timestamp', self.timestamp_local.strftime(settings.TIME_FORMAT)),
            ('url', self.url),
            ('link', self.link),
            ('via', self.via),
            ('via-link', self.via_link),
            ('slug', self.slug),
            ('tags', self.tags),
            )

        metadata = ''
        for k, v in d:
            if v is not None and len(v) > 0:
                metadata += yaml.safe_dump(dict([(k, v)]), default_flow_style=False)

        # handle custom metadata
        if len(self.custom_properties):
            metadata += '\n'
            metadata += yaml.safe_dump(self.custom_properties, default_flow_style=False)
        return settings.JINJA_ENV.get_template(self.markdown_template_path).render(metadata=metadata,
                                                                                   content=self.content_raw)

    def __unicode__(self):
        return self.markdown_file_name

    __repr__ = __unicode__


class PostCollection(list):
    """A collection of :class:`Posts <engineer.models.Post>`."""

    def __init__(self, seq=()):
        list.__init__(self, seq)
        self.listpage_template = settings.JINJA_ENV.get_template('theme/post_list.html')
        self.archive_template = settings.JINJA_ENV.get_template('theme/post_archives.html')

    def paginate(self, paginate_by=None):
        if paginate_by is None:
            paginate_by = settings.ROLLUP_PAGE_SIZE
        return chunk(self, paginate_by, PostCollection)

    @CachedProperty
    def published(self):
        """Returns a new PostCollection containing the subset of posts that are published."""
        return PostCollection([p for p in self if p.is_published == True])

    @CachedProperty
    def drafts(self):
        """Returns a new PostCollection containing the subset of posts that are drafts."""
        return PostCollection([p for p in self if p.is_draft == True])

    @property
    def pending(self):
        """Returns a new PostCollection containing the subset of posts that are pending."""
        return PostCollection([p for p in self if p.is_pending == True])

    @CachedProperty
    def review(self):
        """Returns a new PostCollection containing the subset of posts whose status is :attr:`~Status.review`."""
        return PostCollection([p for p in self if p.status == Status.review])

    @CachedProperty
    def all_tags(self):
        """Returns a list of all the unique tags, as strings, that posts in the collection have."""
        tags = set()
        for post in self:
            tags.update(post.tags)
        return list(tags)

    def tagged(self, tag):
        """Returns a new PostCollection containing the subset of posts that are tagged with *tag*."""
        return PostCollection([p for p in self if tag in p.tags])

    def output_path(self, slice_num):
        return path(settings.OUTPUT_CACHE_DIR / ("page/%s/index.html" % slice_num))

    def render_listpage_html(self, slice_num, has_next, has_previous, all_posts=None):
        return self.listpage_template.render(
            post_list=self,
            slice_num=slice_num,
            has_next=has_next,
            has_previous=has_previous,
            all_posts=all_posts,
            nav_context='listpage')

    def render_archive_html(self, all_posts=None):
        return self.archive_template.render(post_list=self,
                                            all_posts=all_posts,
                                            nav_context='archive')

    def render_tag_html(self, tag, all_posts=None):
        return settings.JINJA_ENV.get_template('theme/tags_list.html').render(tag=tag,
                                                                              post_list=self.tagged(tag),
                                                                              all_posts=all_posts,
                                                                              nav_context='tag')


class TemplatePage(object):
    def __init__(self, template_path):
        self.html_template = settings.JINJA_ENV.get_template(
            str(settings.TEMPLATE_DIR.relpathto(template_path)).replace('\\', '/'))
        namebase = template_path.namebase
        name_components = settings.TEMPLATE_PAGE_DIR.relpathto(template_path).splitall()[1:]
        name_components[-1] = namebase
        self.name = '/'.join(name_components)
        self.absolute_url = urljoin(settings.HOME_URL, self.name)
        self.output_path = path(settings.OUTPUT_CACHE_DIR / self.name)
        self.output_file_name = 'index.html'

        settings.URLS[self.name] = self.absolute_url

    def render_html(self, all_posts=None):
        rendered = self.html_template.render(nav_context=self.name,
                                             all_posts=all_posts)
        return rendered
