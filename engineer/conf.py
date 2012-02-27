# coding=utf-8
import platform
import yaml
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
from path import path
from zope.cachedescriptors import property as zproperty
from engineer.filters import format_datetime
from engineer.util import urljoin, ensure_exists
from engineer.log import logger

__author__ = 'tyler@tylerbutler.com'

class EngineerConfiguration(object):
    """
    Stores all of the configuration settings for a given Engineer site.

    This class uses the Borg design pattern and shares state among all
    instances of the class.

    There seem to be a lot of differing opinions about whether this design
    pattern is A Good Idea (tm) or not. It definitely seems better than
    Singletons since it enforces *behavior*, not *structure*,
    but it's also possible there's a better way to do it in Python with
    judicious use of globals.
    """

    _state = {}

    def __new__(cls, *p, **k):
        self = object.__new__(cls)
        self.__dict__ = cls._state
        return self

    # ENGINEER 'CONSTANT' PATHS
    ENGINEER_ROOT_DIR = path(__file__).dirname().abspath()
    ENGINEER_TEMPLATE_DIR = (ENGINEER_ROOT_DIR / 'templates').abspath()
    ENGINEER_STATIC_DIR = (ENGINEER_ROOT_DIR / 'static').abspath()
    ENGINEER_THEMES_DIR = (ENGINEER_ROOT_DIR / 'themes').abspath()

    def __init__(self, settings_file='config.yaml'):
        self.initialize_from_yaml(settings_file)

    def initialize_from_yaml(self, yaml_file):
        # Load settings from YAML file if found
        if yaml_file and (path.getcwd() / yaml_file).exists():
            with open(path.getcwd() / yaml_file, mode='rb') as file:
                config = yaml.load(file)
                self.initialize(config)
        else:
            self.initialize({})

    def initialize(self, config):
        if getattr(self, '_initialized', False):
            logger.debug("Configuration has already been initialized once.")
        else:
            self._initialized = True

        # CONTENT DIRECTORIES
        self.CONTENT_ROOT_DIR = path(config.pop('CONTENT_ROOT_DIR', path.getcwd().abspath()))
        self.POST_DIR = self.normalize(config.pop('POST_DIR', 'posts'))
        self.OUTPUT_DIR = self.normalize(config.pop('OUTPUT_DIR', 'output'))
        self.TEMPLATE_DIR = self.normalize(config.pop('TEMPLATE_DIR', 'templates'))
        self.LOG_DIR = self.normalize(config.pop('LOG_DIR', 'logs'))
        self.LOG_FILE = ensure_exists(config.pop('LOG_FILE', (self.LOG_DIR / 'build.log').abspath()))
        self.CACHE_DIR = self.normalize(config.pop('CACHE_DIR', '_cache'))
        self.OUTPUT_CACHE_DIR = ensure_exists(
            config.pop('OUTPUT_CACHE_DIR', (self.CACHE_DIR / 'output_cache').abspath()))
        self.JINJA_CACHE_DIR = ensure_exists(config.pop('JINJA_CACHE_DIR', (self.CACHE_DIR / 'jinja_cache').abspath()))
        self.POST_CACHE_FILE = ensure_exists(
            config.pop('POST_CACHE_FILE', (self.CACHE_DIR / 'post_cache.cache').abspath()))

        # SITE SETTINGS
        self.SITE_TITLE = config.pop('SITE_TITLE', '')
        self.SITE_URL = config.pop('SITE_URL') #required
        self.SITE_AUTHOR = config.pop('SITE_AUTHOR', '')
        self.HOME_URL = config.pop('HOME_URL', '/')
        self.STATIC_URL = config.pop('STATIC_URL', urljoin(self.HOME_URL, 'static'))
        self.ROLLUP_PAGE_SIZE = int(config.pop('ROLLUP_PAGE_SIZE', 5))
        self.FEED_TITLE = config.pop('FEED_TITLE_ATOM', self.SITE_TITLE + ' Feed')
        self.FEED_DESCRIPTION = config.pop('FEED_DESCRIPTION',
                                           'The %s most recent posts from %s.' % (self.ROLLUP_PAGE_SIZE, self.SITE_URL))
        self.FEED_ITEM_LIMIT = config.pop('FEED_ITEM_LIMIT', self.ROLLUP_PAGE_SIZE)

        def page(num):
            page_path = urljoin('page', str(num))
            return urljoin(self.HOME_URL, page_path)

        def tag(name):
            page_path = urljoin('tag', name)
            page_path = urljoin(self.HOME_URL, page_path)
            return page_path

        self.URLS = {
            'home': self.HOME_URL,
            'archives': urljoin(self.HOME_URL, 'archives'),
            'feed': urljoin(self.HOME_URL, 'feeds/rss.xml'),
            'listpage': page,
            'tag': tag,
            }

        # THEMES
        self.THEME_FINDERS = ['engineer.finders.DefaultFinder']
        self.THEME_SETTINGS = config.pop('THEME_SETTINGS', {})
        self.THEME = config.pop('THEME', 'dark_rainbow')

        # Miscellaneous
        self.DEBUG = config.pop('DEBUG', False)
        self.DISABLE_CACHE = config.pop('DISABLE_CACHE', False)
        self.NORMALIZE_INPUT_FILES = config.pop('NORMALIZE_INPUT_FILES', True)
        self.NORMALIZE_INPUT_FILE_MASK = config.pop('NORMALIZE_INPUT_FILE_MASK', u'({0}){1}-{2}.md')
        self.USE_CLIENT_SIDE_LESS = config.pop('USE_CLIENT_SIDE_LESS', (platform.system() == 'Windows'))

        for k, v in config.iteritems():
            setattr(self, k, v)

    @zproperty.CachedProperty
    def JINJA_ENV(self):
        from engineer.urls import url, urlname
        from engineer.themes import ThemeManager
        # Configure Jinja2 environment
        logger.debug("Configuring the Jinja environment.")
        engineer = {
            'foundation_url': urljoin(self.STATIC_URL, 'engineer/lib/foundation/'),
            'jquery_url': urljoin(self.STATIC_URL, 'engineer/lib/jquery-1.6.2.min.js'),
            'modernizr_url': urljoin(self.STATIC_URL, 'engineer/lib/modernizr-2.0.6.min.js'),
            'lesscss_url': urljoin(self.STATIC_URL, 'engineer/lib/less-1.1.5.min.js'),
            }

        env = Environment(
            loader=FileSystemLoader([self.TEMPLATE_DIR,
                                     self.ENGINEER_TEMPLATE_DIR,
                                     ThemeManager.current_theme().template_root]),
            extensions=['jinja2.ext.with_', ],
            #'compressinja.html.HtmlCompressor'],
            bytecode_cache=FileSystemBytecodeCache(directory=self.JINJA_CACHE_DIR),
            trim_blocks=False)

        env.filters['date'] = format_datetime
        env.globals['engineer'] = engineer
        env.globals['theme'] = ThemeManager.current_theme()
        env.globals['urlname'] = urlname
        env.globals['url'] = url
        env.globals['STATIC_URL'] = self.STATIC_URL
        env.globals['settings'] = self
        return env

    def normalize(self, p):
        if path.isabs(path(p)):
            return ensure_exists(path(p))
        else:
            return ensure_exists((self.CONTENT_ROOT_DIR / p).abspath())

settings = EngineerConfiguration()
