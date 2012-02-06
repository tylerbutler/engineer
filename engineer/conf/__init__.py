# coding=utf-8
#import logging
#import platform
#from path import path
#from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
#from engineer.filters import format_datetime
#from engineer.util import urljoin, get_class
import os
from engineer.conf import defaults
from engineer.util import LazyObject

__author__ = 'tyler@tylerbutler.com'

class LazySettings(LazyObject):
    def _setup(self):
        settings_module = os.environ['ENGINEER_SETTINGS_MODULE']
        self._wrapped = Settings(user_module=settings_module)

class Settings(object):
    configured = False
    defaults_module = __import__('engineer.conf.defaults')

    def __init__(self, user_module=None):
        for setting in dir(self.defaults_module):
            if setting == setting.upper():
                setattr(self, setting, getattr(self.defaults_module, setting))

        if user_module is not None:
            self.user_module = __import__(user_module)
        else:
            self.user_module = __import__('user_settings')

        for setting in dir(self.user_module):
            if setting == setting.upper():
                setattr(self, setting, getattr(self.user_module, setting))

    def __getattr__(self, item):
        attr = getattr(self.user_module, item, getattr(self.defaults_module, item))
        return attr

settings = defaults

#def configure(user_settings_module='config'):
#    global USER_SETTINGS_MODULE
#    USER_SETTINGS_MODULE = __import__(user_settings_module)
#
#
#class Settings(object):
#    def __init__(self):
#        self._configured = False
#
#    def configure(self, user_config_module='settings'):
#        assert not self.configured, "Settings have already been configured."
#        try:
#            self.USER_SETTINGS_MODULE = __import__(user_config_module)
#        except ImportError, e:
#            raise ImportError("Could not import settings from '%s'. %s", (user_config_module, e))
#
#        # Directories
#        self.ENGINE_DIR = path(__file__).dirname().abspath()
#
#        self.USER_ROOT_DIR = self.check('USER_ROOT_DIR', path(self.USER_SETTINGS_MODULE.__file__).abspath())
#        self.DRAFT_DIR = self.normalize(self.check('DRAFT_DIR', 'drafts'))
#        self.PUBLISHED_DIR = self.normalize(self.check('PUBLISHED_DIR', 'published'))
#        self.TEMPLATE_DIR = self.normalize(self.check('TEMPLATE_DIR', 'templates'))
#        self.STATIC_DIR = self.normalize(self.check('STATIC_DIR', 'static'))
#        self.OUTPUT_DIR = self.normalize(self.check('OUTPUT_DIR', 'output'))
#        self.LOG_DIR = self.normalize(self.check('LOG_DIR', 'logs'))
#        self.LOG_FILE = self.normalize(self.check('LOG_FILE', 'build.log'))
#        self.CACHE_DIR = self.normalize(self.check('CACHE_DIR', 'cache'))
#        self.JINJA_CACHE_DIR = self.CACHE_DIR / 'jinja_cache'
#        self.POST_CACHE_FILE = self.CACHE_DIR / 'post_cache.cache'
#
#        # URLs
#        self.HOME_URL = self.check('HOME_URL', '/')
#        self.STATIC_URL = self.check('STATIC_URL', urljoin(self.HOME_URL, 'static'))
#        self.URLS = self.check('URLS', defaults.URLS)
#
#        # Themes
#        self.THEME = self.check('THEME', 'dark_rainbow')
#        self.THEMES_DIR = self.normalize(self.check('THEMES_DIR', path(self.ENGINE_DIR / 'themes').abspath()))
#        self.THEME_FINDERS = ['engineer.finders.DefaultFinder']
#
#        # Miscellaneous
#        self.DISABLE_CACHE = self.check('DISABLE_CACHE', False)
#        self.USE_CLIENT_SIDE_LESS = self.check('USE_CLIENT_SIDE_LESS', (platform.system() == 'Windows'))
#
#        # Ensure directories exist and create them if not
#        if not self.LOG_DIR.exists():
#            logging.info("The log directory '%s' does not exist; creating." % self.LOG_DIR)
#            self.LOG_DIR.makedirs()
#
#        if not self.CACHE_DIR.exists():
#            logging.info("The cache directory '%s' does not exist; creating." % self.CACHE_DIR)
#            self.CACHE_DIR.makedirs()
#
#        if not self.JINJA_CACHE_DIR.exists():
#            logging.info("The jinja cache directory '%s' does not exist; creating." % self.JINJA_CACHE_DIR)
#            self.JINJA_CACHE_DIR.makedirs()
#
#        # Configure Jinja2 environment
#        engineer = {
#            'foundation_url': urljoin(self.STATIC_URL, 'engineer/lib/foundation/'),
#            'jquery_url': urljoin(self.STATIC_URL, 'engineer/lib/jquery-1.6.2.min.js'),
#            'modernizr_url': urljoin(self.STATIC_URL, 'engineer/lib/modernizr-2.0.6.min.js'),
#            'lesscss_url': urljoin(self.STATIC_URL, 'engineer/lib/less-1.1.5.min.js'),
#            }
#
#        self.JINJA_ENV = Environment(
#            loader=FileSystemLoader([settings.TEMPLATE_DIR, settings.ENGINE_DIR / 'themes']),
#            extensions=['jinja2.ext.with_',
#                        'compressinja.html.HtmlCompressor'],
#            bytecode_cache=FileSystemBytecodeCache(directory=settings.JINJA_CACHE_DIR),
#            trim_blocks=True)
#        self.JINJA_ENV.filters['date'] = format_datetime
#        self.JINJA_ENV.globals['engineer'] = engineer
#        self.JINJA_ENV.globals['theme'] = get_class('engineer.themes.ThemeManager').current_theme()
#        self.JINJA_ENV.globals['urlname'] = get_class('engineer.urls').urlname
#        self.JINJA_ENV.globals['url'] = get_class('engineer.urls').url
#        self.JINJA_ENV.globals['STATIC_URL'] = self.STATIC_URL
#        self.JINJA_ENV.globals['config'] = self
#
#        self._configured = True
#
#    @property
#    def configured(self):
#        return self._configured
#
#    def check(self, setting, default):
#        to_return = getattr(self.USER_SETTINGS_MODULE, setting, default)
#        if to_return == default and isinstance(default, (dict, list)):
#            add = getattr(self.USER_SETTINGS_MODULE, '%s_ADD' % setting, None)
#            if add is not None:
#                if isinstance(add, dict):
#                    to_return.update(add)
#                elif isinstance(add, list):
#                    to_return.extend(add)
#        return to_return
#
#    def normalize(self, p):
#        if path.isabs(path(p)):
#            return path(p)
#        else:
#            return path((self.USER_ROOT_DIR / p).abspath())
