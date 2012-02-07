# coding=utf-8
#import logging
#import platform
#from path import path
import logging
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
from zope.cachedescriptors import property as zproperty
from engineer.filters import format_datetime
import platform
import os
from path import path
from engineer.util import get_class, urljoin, LazyObject, ensure_exists

__author__ = 'tyler@tylerbutler.com'

#class Settings2(object):
#    def __init__(self, config_module='engineer.conf.globals'):
#        try:
#            self.USER_SETTINGS_MODULE = get_class(config_module)
#        except ImportError, e:
#            raise ImportError("Could not import settings from '%s'. %s", (config_module, e))
#
#        for setting in dir(globals):
#            if setting == setting.upper():
#                setattr(self, setting, getattr(globals, setting))
#
#        if self.USER_SETTINGS_MODULE != globals:
#            for setting in dir(self.USER_SETTINGS_MODULE):
#                if setting == setting.upper():
#                    setattr(self, setting, getattr(self.USER_SETTINGS_MODULE, setting))
#
#    def normalize(self, p):
#        if path.isabs(path(p)):
#            return path(p)
#        else:
#            return path((self.CONTENT_ROOT_DIR / p).abspath())

class LazySettings(LazyObject):
    def _setup(self):
        settings_module = os.environ['ENGINEER_SETTINGS_MODULE']
        self._wrapped = SettingsOverride(settings_module)


class SettingsBase(object):
    # ENGINEER 'CONSTANT' PATHS
    ENGINEER_ROOT_DIR = path(__file__).dirname().dirname().abspath()
    ENGINEER_TEMPLATE_DIR = (ENGINEER_ROOT_DIR / 'templates').abspath()
    ENGINEER_STATIC_DIR = (ENGINEER_ROOT_DIR / 'static').abspath()
    ENGINEER_THEMES_DIR = (ENGINEER_ROOT_DIR / 'themes').abspath()

    # CONTENT DIRECTORIES
    CONTENT_ROOT_DIR = ENGINEER_ROOT_DIR.dirname()

    #    _DRAFT_DIR = 'drafts'
    #
    @zproperty.Lazy
    def DRAFT_DIR(self):
        return self.normalize('drafts')

    #    _PUBLISHED_DIR = 'published'
    #
    @zproperty.Lazy
    def PUBLISHED_DIR(self):
        return self.normalize('published')

    #    _OUTPUT_DIR = 'output'
    #
    @zproperty.Lazy
    def OUTPUT_DIR(self):
        return self.normalize('output')

        # LOG DIRECTORIES

    #    _LOG_DIR = 'logs'
    #
    @zproperty.Lazy
    def LOG_DIR(self):
        return self.normalize('logs')

    #    @LOG_DIR.setter
    #    def LOG_DIR(self, value):
    #        self._LOG_DIR = value

#    _LOG_FILE = 'build.log'
#
    @zproperty.Lazy
    def LOG_FILE(self):
        return ensure_exists((self.LOG_DIR / 'build.log').abspath())

        #    @LOG_FILE.setter
        #    def LOG_FILE(self, value):
        #        self._LOG_FILE =

        # CACHE DIRECTORIES

    #    _CACHE_DIR = 'cache'

    @zproperty.Lazy
    def CACHE_DIR(self):
        return self.normalize('_cache')

    @zproperty.Lazy
    def JINJA_CACHE_DIR(self):
        return ensure_exists((self.CACHE_DIR / 'jinja_cache').abspath())

    @zproperty.Lazy
    def POST_CACHE_FILE(self):
        return ensure_exists((self.CACHE_DIR / 'post_cache.cache').abspath())

    # URLS
    HOME_URL = '/'

    @zproperty.Lazy
    def STATIC_URL(self):
        return urljoin(self.HOME_URL, 'static')

    URLS = {}

    # THEMES
    THEME_FINDERS = ['engineer.finders.DefaultFinder']
    THEME = 'dark_rainbow'

    # Miscellaneous
    DISABLE_CACHE = False
    USE_CLIENT_SIDE_LESS = (platform.system() == 'Windows')

    @zproperty.CachedProperty
    def JINJA_ENV(self):
        from engineer.urls import url, urlname
        from engineer.themes import ThemeManager
        # Configure Jinja2 environment
        logging.debug("Configuring the Jinja environment.")
        engineer = {
            'foundation_url': urljoin(self.STATIC_URL, 'engineer/lib/foundation/'),
            'jquery_url': urljoin(self.STATIC_URL, 'engineer/lib/jquery-1.6.2.min.js'),
            'modernizr_url': urljoin(self.STATIC_URL, 'engineer/lib/modernizr-2.0.6.min.js'),
            'lesscss_url': urljoin(self.STATIC_URL, 'engineer/lib/less-1.1.5.min.js'),
            }

        env = Environment(
            loader=FileSystemLoader([self.ENGINEER_TEMPLATE_DIR,
                                     #ThemeManager.current_theme().TEMPLATE_DIR,
                                     self.ENGINEER_THEMES_DIR]),
            extensions=['jinja2.ext.with_',
                        'compressinja.html.HtmlCompressor'],
            bytecode_cache=FileSystemBytecodeCache(directory=self.JINJA_CACHE_DIR),
            trim_blocks=True)

        env.filters['date'] = format_datetime
        env.globals['engineer'] = engineer
        env.globals['theme'] = ThemeManager.current_theme()#get_class('engineer.themes.ThemeManager').current_theme()
        env.globals['urlname'] = urlname
        env.globals['url'] = url
        env.globals['STATIC_URL'] = self.STATIC_URL
        env.globals['config'] = self#get_class('engineer.conf.settings')
        return env

    #@zproperty.CachedProperty
#    _post_cache = None
#    @property
#    def POST_CACHE(self):
#        if self._post_cache is None:
#            from engineer.post_cache import POST_CACHE
#            self._post_cache = POST_CACHE
#        return self._post_cache
#        from engineer.post_cache import _PostCache
#        return _PostCache()
    #@zproperty.Lazy


    #@property
#    @zproperty.Lazy
#    def POST_CACHE(self):
#        from engineer.post_cache import _PostCache
#        return _PostCache()

#    @POST_CACHE.setter
#    def POST_CACHE(self, value):


    def normalize(self, p):
        if path.isabs(path(p)):
            return ensure_exists(path(p))
        else:
            return ensure_exists((self.CONTENT_ROOT_DIR / p).abspath())

    def __setattr__(self, key, value):
        if key.endswith('_DIR') and isinstance(value, str):
            value = path(value)
        super(SettingsBase, self).__setattr__(key, value)


class SettingsOverride(SettingsBase):
    def __init__(self, settings_module):
#        if settings_module is None:
#            settings_module = os.environ['ENGINEER_SETTINGS_MODULE']
        try:
            self.SETTINGS_MODULE = __import__(settings_module)
        except ImportError, e:
            raise ImportError("Could not import settings from '%s'. %s", (settings_module, e))

        for setting in dir(self.SETTINGS_MODULE):
            if setting == setting.upper():
#                private_setting = '_%s' % setting
#                if hasattr(self, private_setting):
#                    setattr(self, private_setting, getattr(self.SETTINGS_MODULE, setting))
#                else:
                setattr(self, setting, getattr(self.SETTINGS_MODULE, setting))
