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
from zope.cachedescriptors.property import CachedProperty
from engineer.conf import settings
from engineer.filters import localtime
from engineer.util import slugify, chunk, urljoin

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'tyler@tylerbutler.com'

logger = logging.getLogger(__name__)

class Status(Enum):
    """Enum representing the status of a :class:`~Post`."""
    draft = 0 #: Post is a draft.
    published = 1 #: Post is published.

    def __reduce__(self):
        return 'Status'


class MetadataError(Exception):
    pass


class Post(object):
    """
    Represents a post written in Markdown and stored in a file.

    :param source: path to the source file for the post.
    """
    _regex = re.compile(r'^[\n|\r\n]*(?P<metadata>.+?)[\n|\r\n]*---[\n|\r\n]*(?P<content>.*)[\n|\r\n]*', re.DOTALL)

    def __init__(self, source):
        self.source = path(source).abspath()
        """The absolute path to the source file for the post."""

        self.html_template_path = 'theme/post_detail.html'
        """The path to the template to use to transform the post into HTML."""

        self.markdown_template_path = 'core/post.md'
        """The path to the template to use to transform the post into HTML."""

        metadata, self._content_raw = self._parse_source()

        self.title = metadata.get('title', self.source.namebase.replace('-', ' ').replace('_', ' '))
        """The title of the post."""

        self.slug = metadata.get('slug', slugify(self.title))
        """The slug for the post."""

        self.tags = metadata.get('tags', [])
        """A list of strings representing the tags applied to the post."""

        self.link = metadata.get('link', None)
        """The post's external link."""

        self.via = metadata.get('via', None)
        """The post's attribution name."""

        self.via_link = metadata.get('via_link', None)
        """The post's attribution link."""

        try:
            self.status = Status(metadata.get('status', Status.draft.name))
        except ValueError:
            root_logger.warning("'%s': Invalid status value in metadata. Defaulting to 'draft'." % self.title)
            self.status = Status.draft

        self.timestamp = metadata.get('timestamp', None)
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

        self.content = typogrify(markdown.markdown(self._content_raw, extensions=['extra', 'codehilite']))

        self.markdown_file_name = unicode.format(settings.NORMALIZE_INPUT_FILE_MASK,
                                                 self.status.name[:1],
                                                 self.timestamp_local.strftime('%Y-%m-%d'),
                                                 #times.format(self.timestamp, settings.DEFAULT_TIMEZONE, '%Y-%m-%d'),
                                                 self.slug)
        self.url = unicode.format(u'{0}{1}/{2}/',
                                  settings.HOME_URL,
                                  self.timestamp_local.strftime('%Y/%m/%d'),
                                  self.slug)
        self.absolute_url = unicode.format(u'{0}{1}', settings.SITE_URL, self.url)
        self.output_path = path(settings.OUTPUT_CACHE_DIR / self.timestamp_local.strftime('%Y/%m/%d') / self.slug)
        self.output_file_name = 'index.html'#'%s.html' % self.slug

        self._normalize_source()

        # update cache
        settings.POST_CACHE[self.source] = self

    @property
    def is_draft(self):
        return self.status == Status.draft

    @property
    def is_published(self):
        """
        ``True`` if the post is published, ``False`` otherwise.
        """
        return self.status == Status.published and self.timestamp <= times.now()

    @property
    def is_pending(self):
        return self.status == Status.published and self.timestamp >= times.now()

    @property
    def is_external_link(self):
        return self.link is not None and self.link != ''

    @property
    def timestamp_local(self):
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
            raise MetadataError()

        # 'Clean' the YAML section since there might be tab characters
        metadata = parsed_content.group('metadata').replace('\t', '    ')
        metadata = yaml.load(metadata)
        if not isinstance(metadata, dict):
            raise MetadataError()
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

    def render_html(self):
        return settings.JINJA_ENV.get_template(self.html_template_path).render(post=self, nav_context='post')

    def render_markdown(self):
        # A hack to guarantee the YAML output is in a sensible order.
        d = {
            'title': self.title,
            'timestamp': self.timestamp_local.strftime(settings.TIME_FORMAT),
            'status': self.status.name,
            'slug': self.slug,
            'link': self.link,
            'via': self.via,
            'via_link': self.via_link,
            'tags': self.tags,
            }
        order = ['title', 'timestamp', 'status', 'tags', 'link', 'via', 'via_link', 'slug', ]
        metadata = ''
        for k in order:
            if k in d and d[k] is not None and len(d[k]) > 0:
                metadata += yaml.safe_dump(dict([[k, d[k]]]), default_flow_style=False)
        return settings.JINJA_ENV.get_template(self.markdown_template_path).render(metadata=metadata,
                                                                                   content=self._content_raw)

    def __unicode__(self):
        return self.markdown_file_name

    __repr__ = __unicode__


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

    def render_html(self):
        rendered = self.html_template.render(nav_context=self.name)
        return rendered


class PostCollection(list):
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
        return PostCollection([p for p in self if p.is_published == True])

    @CachedProperty
    def drafts(self):
        return PostCollection([p for p in self if p.is_draft == True])

    @property
    def pending(self):
        return PostCollection([p for p in self if p.is_pending == True])

    @CachedProperty
    def all_tags(self):
        tags = set()
        for post in self:
            tags.update(post.tags)
        return list(tags)

    @CachedProperty
    def grouped_by_year(self):
        years = map(lambda x: x.timestamp.year, self)
        years = set(years)

        to_return = [(year, filter(lambda p: p.timestamp.year == year, self)) for year in years]
        to_return = sorted(to_return, reverse=True)

        return to_return

    def tagged(self, tag):
        return PostCollection([p for p in self if tag in p.tags])

    def output_path(self, slice_num):
        return path(settings.OUTPUT_CACHE_DIR / ("page/%s/index.html" % slice_num))

    def render_listpage_html(self, slice_num, has_next, has_previous):
        return self.listpage_template.render(
            post_list=self,
            slice_num=slice_num,
            has_next=has_next,
            has_previous=has_previous,
            nav_context='listpage')

    def render_archive_html(self):
        return self.archive_template.render(post_list=self.grouped_by_year, nav_context='archive')

    def render_tag_html(self, tag):
        return settings.JINJA_ENV.get_template('theme/tags_list.html').render(tag=tag,
                                                                              post_list=self.tagged(
                                                                                  tag).grouped_by_year,
                                                                              nav_context='tag')
