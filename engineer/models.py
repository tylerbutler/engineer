# coding=utf-8
import markdown
import pynq
import re
import yaml
from codecs import open
from datetime import datetime
from dateutil import parser
from flufl.enum._enum import Enum
from path import path
from typogrify.templatetags.jinja2_filters import typogrify
from engineer.conf import settings
from engineer.post_cache import POST_CACHE
from engineer.util import slugify, chunk, urljoin
from engineer.log import logger

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'tyler@tylerbutler.com'

class Status(Enum):
    draft = 0
    published = 1

    def __reduce__(self):
        return 'Status'


class MetadataError(Exception):
    pass


class Post(object):
    _regex = re.compile(r'^[\n|\r\n]*(?P<metadata>.+?)[\n|\r\n]*---[\n|\r\n]*(?P<content>.*)[\n|\r\n]*', re.DOTALL)

    def __init__(self, source):
        self.source = path(source).abspath()
        self.html_template = settings.JINJA_ENV.get_template('theme/post_detail.html')
        self.markdown_template = settings.JINJA_ENV.get_template('core/post.md')

        metadata, self.content_raw = self._parse_source()

        self.title = metadata.get('title', self.source.namebase.replace('-', ' ').replace('_', ' '))
        self.slug = metadata.get('slug', slugify(self.title))
        self.external_link = metadata.get('external_link', None)
        try:
            self.status = Status(metadata.get('status', Status.draft.name))
        except ValueError:
            logger.warning("'%s': Invalid status value in metadata. Defaulting to 'draft'." % self.title)
            self.status = Status.draft

        self.timestamp = metadata.get('timestamp', datetime.now())
        if not isinstance(self.timestamp, datetime):
            self.timestamp = parser.parse(str(self.timestamp))

        self.content = typogrify(markdown.markdown(self.content_raw))

        self.markdown_file_name = unicode.format(u'({0}){1}-{2}.md',
                                                 self.status.name[:1],
                                                 self.timestamp.strftime('%Y-%m-%d'),
                                                 self.slug)
        self.absolute_url = unicode.format(u'{0}{1}/{2}/',
                                           settings.HOME_URL,
                                           self.timestamp.strftime('%Y/%m/%d'),
                                           self.slug)
        self.output_path = path(settings.OUTPUT_DIR / self.timestamp.strftime('%Y/%m/%d') / self.slug)
        self.output_file_name = 'index.html'#'%s.html' % self.slug

        # update cache
        POST_CACHE[self.source] = {
            'mtime': self.source.mtime,
            'size': self.source.size,
            'checksum': self.source.read_hexhash('sha256'),
            #'post': self
        }

    @property
    def is_draft(self):
        return self.status == Status.draft

    @property
    def is_published(self):
        return self.status == Status.published

    @property
    def is_external_link(self):
        return self.external_link is not None

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
        if metadata is None:
            raise MetadataError()
        content = parsed_content.group('content')

        return metadata, content

    def render_html(self):
        return self.html_template.render(post=self, nav_context='post')

    def render_markdown(self):
        metadata = yaml.dump({
            'title': self.title,
            'timestamp': self.timestamp,
            'status': self.status.name,
            'slug': self.slug
        }, default_flow_style=False)
        return self.markdown_template.render(metadata=metadata, content=self.content_raw)

    def __unicode__(self):
        return self.markdown_file_name

    __repr__ = __unicode__


class TemplatePage(object):
    def __init__(self, template_path):
        self.html_template = settings.JINJA_ENV.get_template('pages/%s' % template_path.name)
        self.name = template_path.namebase
        self.absolute_url = urljoin(settings.HOME_URL, self.name)
        self.output_path = path(settings.OUTPUT_DIR / self.name)
        self.output_file_name = 'index.html'

        settings.URLS[self.name] = self.absolute_url

    def render_html(self):
    #        settings.JINJA_ENV.globals['engineer']['navigation']['section'] = self.name
        rendered = self.html_template.render(nav_context=self.name)
        #        settings.JINJA_ENV.globals['engineer']['navigation']['section'] = 'default'
        return rendered


class PostCollection(list):
    def __init__(self, seq=()):
        list.__init__(self, seq)
        self.listpage_template = settings.JINJA_ENV.get_template('theme/post_list.html')
        self.archive_template = settings.JINJA_ENV.get_template('theme/post_archives.html')

    def paginate(self, paginate_by=5):
        return chunk(self, paginate_by, PostCollection)

    @property
    def published(self):
        return pynq.From(self).where("item.is_published == True").select_many()

    @property
    def drafts(self):
        return pynq.From(self).where("item.is_draft == True").select_many()

    @property
    def grouped_by_year(self):
        years = map(lambda x: x.timestamp.year, self)
        years = set(years)

        to_return = [(year, filter(lambda p: p.timestamp.year == year, self)) for year in years]
        to_return = sorted(to_return, reverse=True)

        return to_return

    def output_path(self, slice_num):
        return path(settings.OUTPUT_DIR / ("page/%s/index.html" % slice_num))

    def render_listpage_html(self, slice_num, has_next, has_previous):
        return self.listpage_template.render(
            post_list=self,
            slice_num=slice_num,
            has_next=has_next,
            has_previous=has_previous,
            nav_context='listpage')

    def render_archive_html(self):
        return self.archive_template.render(post_list=self.grouped_by_year, nav_context='archive')
