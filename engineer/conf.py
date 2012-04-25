# coding=utf-8
from inspect import isfunction
import logging
import platform
import pytz
import shelve
import times
import yaml
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
from typogrify.templatetags.jinja2_filters import typogrify
from path import path
from zope.cachedescriptors import property as zproperty
from engineer.cache import SimpleFileCache
from engineer.util import urljoin, slugify, ensure_exists, wrap_list
from engineer.version import __version__ as version

__author__ = 'tyler@tylerbutler.com'

logger = logging.getLogger(__name__)

class SettingsFileNotFoundException(Exception):
    pass


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

    _required_params = ('SITE_URL',)

    class _EngineerConstants(object):
        # ENGINEER 'CONSTANTS'
        ROOT_DIR = path(__file__).dirname().abspath()
        TEMPLATE_DIR = (ROOT_DIR / 'templates').abspath()
        STATIC_DIR = (ROOT_DIR / 'static').abspath()
        THEMES_DIR = (ROOT_DIR / 'themes').abspath()

        # URLs to included libraries - will be updated in the EngineerConfiguration.initialize() method.
        FOUNDATION_CSS_URL = None
        JQUERY_URL = None
        MODERNIZR_URL = None
        LESS_JS_URL = None
        TWEET_URL = None

    def __init__(self, settings_file=None):
        self.reload(settings_file)

    def reload(self, settings_file=None):
        if settings_file is None:
            if hasattr(self,
                       'SETTINGS_FILE') and self.SETTINGS_FILE is not None:
                # First check if SETTINGS_FILE has been defined. If so, we'll reload from that file.
                settings_file = self.SETTINGS_FILE
            else:
                # Looks like we're just loading the 'empty' config.
                logger.info("Initializing empty configuration.")
                self.SETTINGS_FILE = None
                self._initialize({})
                return

        if path(settings_file).exists() and path(settings_file).isfile():
            self.SETTINGS_FILE = settings_file = path(settings_file).abspath()
            logger.console("Loading configuration from %s." % path(settings_file).abspath())
            # Find the complete set of settings files based on inheritance
            all_configs = []
            config = {}
            try:
                while True:
                    with open(settings_file, mode='rb') as file:
                        temp_config = yaml.load(file)
                        logger.debug("Loaded %s file." % settings_file)
                    all_configs.append((temp_config, settings_file))
                    if 'SUPER' not in temp_config:
                        break
                    else:
                        new_settings = path(temp_config['SUPER'])
                        if not new_settings.isabs():
                            settings_file = (
                                settings_file.dirname() / new_settings).abspath()
                        logger.debug("Going to next settings file... %s" %
                                     path(temp_config['SUPER']).abspath())
            except Exception as e:
                logger.exception(e.message)

            # load parent configs
            all_configs.reverse()
            for c in all_configs[:-1]:
                logger.debug("Loading parent configuration from %s." % path(
                    c[1]).abspath())
                config.update(c[0])

            # load main config
            logger.debug("Finalizing configuration from %s." % path(
                all_configs[-1][1]).abspath())
            config.update(all_configs[-1][0])

            for param in self._required_params:
                if param not in config:
                    raise Exception(
                        "Required setting '%s' is missing from config file %s." %
                        (param, self.SETTINGS_FILE))
            self._initialize(config)
            self.SETTINGS_FILE_LOAD_TIME = times.now()
        else:
            raise SettingsFileNotFoundException(
                "Settings file %s not found!" % settings_file)

    def _initialize(self, config):
        self.ENGINEER = EngineerConfiguration._EngineerConstants()

        # CONTENT DIRECTORIES
        self.SETTINGS_DIR = path(config.pop('SETTINGS_DIR',
                                            self.SETTINGS_FILE.dirname().abspath() if self.SETTINGS_FILE is not
                                                                                      None else path.getcwd()))
        self.CONTENT_DIR = self.normalize(config.pop('CONTENT_DIR', 'content'))
        self.POST_DIR = self.normalize_list(config.pop('POST_DIR', 'posts'))
        self.OUTPUT_DIR = self.normalize(config.pop('OUTPUT_DIR', 'output'))
        self.TEMPLATE_DIR = self.normalize(
            config.pop('TEMPLATE_DIR', 'templates'))
        self.TEMPLATE_PAGE_DIR = config.pop('TEMPLATE_PAGE_DIR', (
            self.TEMPLATE_DIR / 'pages').abspath())
        self.LOG_DIR = self.normalize(config.pop('LOG_DIR', 'logs'))
        self.LOG_FILE = config.pop('LOG_FILE',
                                   (self.LOG_DIR / 'build.log').abspath())

        self.CACHE_DIR = config.pop('CACHE_DIR', None)
        if self.CACHE_DIR is None:
            if self.SETTINGS_FILE is not None:
                self.CACHE_DIR = self.normalize(
                    '_cache/%s' % self.SETTINGS_FILE.name)
            else:
                self.CACHE_DIR = self.normalize('_cache/None')
        else:
            self.CACHE_DIR = self.normalize(self.CACHE_DIR)

        self.CACHE_FILE = config.pop('CACHE_FILE', (self.CACHE_DIR / 'engineer.cache').abspath())
        self.OUTPUT_CACHE_DIR = config.pop('OUTPUT_CACHE_DIR', (self.CACHE_DIR / 'output_cache').abspath())
        self.JINJA_CACHE_DIR = config.pop('JINJA_CACHE_DIR', (self.CACHE_DIR / 'jinja_cache').abspath())
        self.BUILD_STATS_FILE = config.pop('BUILD_STATS_FILE', (self.CACHE_DIR / 'build_stats.cache').abspath())

        # THEMES
        self.THEME_FINDERS = ['engineer.finders.DefaultFinder']
        self.THEME_SETTINGS = config.pop('THEME_SETTINGS', {})
        self.THEME = config.pop('THEME', 'dark_rainbow')

        # PREPROCESSOR / COMPRESSOR SETTINGS
        self.COMPRESSOR_ENABLED = config.pop('COMPRESSOR_ENABLED', True)
        self.COMPRESSOR_FILE_EXTENSIONS = config.pop(
            'COMPRESSOR_FILE_EXTENSIONS', ['js', 'css'])
        self.PREPROCESS_LESS = config.pop('PREPROCESS_LESS', True)
        if not 'LESS_PREPROCESSOR' in config:
            if platform.system() == 'Windows':
                self.LESS_PREPROCESSOR = str(self.ENGINEER.ROOT_DIR /
                                             'lib/dotless/dotless.Compiler.exe') + ' {infile} {outfile}'
            else:
                self.LESS_PREPROCESSOR = 'lessc {infile} {outfile}'
        else:
            self.LESS_PREPROCESSOR = path(config.pop('LESS_PREPROCESSOR'))


        # SITE SETTINGS
        self.SITE_TITLE = config.pop('SITE_TITLE', 'SITE_TITLE')
        self.SITE_URL = config.pop('SITE_URL', 'SITE_URL')
        self.SITE_AUTHOR = config.pop('SITE_AUTHOR', None)
        self.HOME_URL = config.pop('HOME_URL', '/')
        self.STATIC_URL = config.pop('STATIC_URL',
                                     urljoin(self.HOME_URL, 'static'))
        self.ROLLUP_PAGE_SIZE = int(config.pop('ROLLUP_PAGE_SIZE', 5))

        # RSS FEED SETTINGS
        self.FEED_TITLE = config.pop('FEED_TITLE',
                                     self.SITE_TITLE + ' Feed')
        self.FEED_ITEM_LIMIT = config.pop('FEED_ITEM_LIMIT',
                                          self.ROLLUP_PAGE_SIZE)
        self.FEED_DESCRIPTION = config.pop('FEED_DESCRIPTION',
                                           'The %s most recent posts from %s.' % (self.FEED_ITEM_LIMIT, self.SITE_URL))

        # These 'constants' are updated here so they're relative to the STATIC_URL value
        self.ENGINEER.FOUNDATION_CSS_URL = urljoin(self.STATIC_URL,
                                                   'engineer/lib/foundation/')
        self.ENGINEER.JQUERY_URL = urljoin(self.STATIC_URL,
                                           'engineer/lib/jquery-1.6.2.min.js')
        self.ENGINEER.MODERNIZR_URL = urljoin(self.STATIC_URL,
                                              'engineer/lib/modernizr-2.0.6.min.js')
        self.ENGINEER.LESS_JS_URL = urljoin(self.STATIC_URL,
                                            'engineer/lib/less-1.1.5.min.js')
        self.ENGINEER.TWEET_URL = urljoin(self.STATIC_URL,
                                          'engineer/lib/tweet/tweet/jquery.tweet.js')

        # URL helper functions
        def page(num):
            page_path = urljoin('page', str(num))
            return urljoin(self.HOME_URL, page_path)

        def tag(name):
            page_path = urljoin('tag', slugify(name))
            page_path = urljoin(self.HOME_URL, page_path)
            return page_path

        self.URLS = {
            'home': self.HOME_URL,
            'archives': urljoin(self.HOME_URL, 'archives'),
            'feed': urljoin(self.HOME_URL, 'feeds/rss.xml'),
            'listpage': page,
            'tag': tag,
            }
        # Update URLs from the config setting if they're present
        self.URLS.update(config.pop('URLS', {}))

        # MISCELLANEOUS SETTINGS
        self.DEBUG = config.pop('DEBUG', False)
        #self.DISABLE_CACHE = config.pop('DISABLE_CACHE', False)
        self.NORMALIZE_INPUT_FILES = config.pop('NORMALIZE_INPUT_FILES', True)
        self.NORMALIZE_INPUT_FILE_MASK = config.pop('NORMALIZE_INPUT_FILE_MASK',
                                                    u'({0}){1}-{2}.md')
        self.PUBLISH_DRAFTS = config.pop('PUBLISH_DRAFTS', False)
        self.PUBLISH_PENDING = config.pop('PUBLISH_PENDING', False)
        self.POST_TIMEZONE = pytz.timezone(config.pop('POST_TIMEZONE', 'UTC'))
        self.SERVER_TIMEZONE = self.POST_TIMEZONE if config.get(
            'SERVER_TIMEZONE',
            None) is None else config.pop('SERVER_TIMEZONE')
        self.TIME_FORMAT = config.pop('TIME_FORMAT',
                                      '%I:%M %p %A, %B %d, %Y %Z') # '%Y-%m-%d %H:%M:%S %Z%z'

        # Pull any remaining settings in the config and set them as attributes on the settings object
        for k, v in config.iteritems():
            setattr(self, k, v)

    @zproperty.CachedProperty
    def OUTPUT_STATIC_DIR(self):
        return path(
            self.OUTPUT_CACHE_DIR / self.ENGINEER.STATIC_DIR.basename()).abspath()

    @zproperty.CachedProperty
    def JINJA_ENV(self):
        from engineer.filters import format_datetime, markdown_filter, localtime, naturaltime, compress
        from engineer.processors import preprocess_less
        from engineer.themes import ThemeManager

        # Configure Jinja2 environment
        logger.debug("Configuring the Jinja environment.")

        # Helper function to look up a URL by name
        def urlname(name, *args):
            url = settings.URLS.get(name, settings.HOME_URL)
            if isfunction(url):
                return url(*args)
            else:
                return url

        env = Environment(
            loader=FileSystemLoader([self.TEMPLATE_DIR,
                                     ThemeManager.current_theme().template_root,
                                     #self.ENGINEER.THEMES_DIR / 'base_templates',
                                     self.ENGINEER.TEMPLATE_DIR])
            ,
            extensions=['jinja2.ext.with_', ],
            #'compressinja.html.HtmlCompressor'],
            bytecode_cache=FileSystemBytecodeCache(
                directory=self.JINJA_CACHE_DIR),
            trim_blocks=False)

        # Filters
        env.filters['compress'] = compress
        env.filters['date'] = format_datetime
        env.filters['localtime'] = localtime
        env.filters['naturaltime'] = naturaltime
        env.filters['typogrify'] = typogrify
        env.filters['markdown'] = markdown_filter

        # Globals
        env.globals['theme'] = ThemeManager.current_theme()
        env.globals['urlname'] = urlname
        env.globals['preprocess_less'] = preprocess_less
        #        env.globals['url'] = url
        env.globals['STATIC_URL'] = self.STATIC_URL
        env.globals['DEBUG'] = self.DEBUG
        env.globals['settings'] = self
        return env

    @zproperty.CachedProperty
    def CACHE(self):
        # Use a shelf as the main cache
        try:
            CACHE = shelve.open(self.CACHE_FILE, writeback=True)
        except Exception as e:
            logger.exception(e)
            CACHE = None
            exit()
        if CACHE is None or not CACHE.has_key('version') or CACHE[
                                                            'version'] != version:
            # all new caches
            logger.debug(
                "Caches either don't exist or are old, so creating new ones...")
            CACHE['version'] = version
            CACHE['POST_CACHE'] = self.POST_CACHE = SimpleFileCache(
                version=version)
            CACHE[
            'COMPRESSION_CACHE'] = self.COMPRESSION_CACHE = SimpleFileCache(
                version=version)
            CACHE['LESS_CACHE'] = self.LESS_CACHE = SimpleFileCache(
                version=version)
        return CACHE

    @zproperty.CachedProperty
    def COMPRESSION_CACHE(self):
        if not self.CACHE.has_key('COMPRESSION_CACHE'):
            self.CACHE['COMPRESSION_CACHE'] = SimpleFileCache()
        return self.CACHE['COMPRESSION_CACHE']

    @zproperty.CachedProperty
    def POST_CACHE(self):
        if not self.CACHE.has_key('POST_CACHE'):
            self.CACHE['POST_CACHE'] = SimpleFileCache()
        return self.CACHE['POST_CACHE']

    def normalize(self, p):
        if path(p).isabs():
            return path(p)
        else:
            return (self.SETTINGS_DIR / p).abspath()

    def normalize_list(self, p):
        l = wrap_list(p)
        return_list = []
        for p in l:
            return_list.append(self.normalize(p))
        return return_list

    def create_required_directories(self):
        """Creates any directories required for Engineer to function if they don't already exist."""
        required = (self.CACHE_DIR,
                    self.JINJA_CACHE_DIR,
                    self.LOG_DIR,
                    self.OUTPUT_DIR,)

        for folder in required:
            ensure_exists(folder)

settings = EngineerConfiguration()
