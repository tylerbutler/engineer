# coding=utf-8
import platform
import os
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
from zope.cachedescriptors import property as zproperty
from path import path
from engineer.filters import format_datetime
from engineer.util import urljoin, LazyObject, ensure_exists
from engineer.log import logger

__author__ = 'tyler@tylerbutler.com'

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

    @zproperty.Lazy
    def CONTENT_ROOT_DIR(self):
        return self.normalize(self.ENGINEER_ROOT_DIR.dirname())

    @zproperty.Lazy
    def DRAFT_DIR(self):
        return self.normalize('drafts')

    @zproperty.Lazy
    def PUBLISHED_DIR(self):
        return self.normalize('published')

    @zproperty.Lazy
    def OUTPUT_DIR(self):
        return self.normalize('output')

    @zproperty.Lazy
    def LOG_DIR(self):
        return self.normalize('logs')

    @zproperty.Lazy
    def LOG_FILE(self):
        return ensure_exists((self.LOG_DIR / 'build.log').abspath())

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

    @zproperty.Lazy
    def URLS(self):
        def page(num):
            page_path = urljoin('page', str(num))
            return urljoin(self.HOME_URL, page_path)

        DEFAULT_URLS = {
            'home': '/',
            'atom_feed': 'feeds/atom.xml',
            'rss_feed': 'feeds/rss.xml',
            'page': page,
            }
        return DEFAULT_URLS

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
        logger.debug("Configuring the Jinja environment.")
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
        try:
            self.SETTINGS_MODULE = __import__(settings_module)
        except ImportError, e:
            raise ImportError("Could not import settings from '%s'. %s", (settings_module, e))

        for setting in dir(self.SETTINGS_MODULE):
            if setting == setting.upper():
                setattr(self, setting, getattr(self.SETTINGS_MODULE, setting))
