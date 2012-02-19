# coding=utf-8
import os
import platform
from path import path
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
from engineer.util import urljoin
from engineer.log import logger

__author__ = 'tyler@tylerbutler.com'

try:
    USER_SETTINGS_MODULE = __import__(os.environ['ENGINEER_SETTINGS_MODULE'])
except KeyError, ImportError:
    logger.exception("The ENGINEER_SETTINGS_MODULE variable doesn't seem to be set...")

def check(setting, default):
    to_return = getattr(USER_SETTINGS_MODULE, setting, default)
    if to_return == default and isinstance(default, (dict, list)):
        add = getattr(USER_SETTINGS_MODULE, '%s_ADD' % setting, None)
        if add is not None:
            if isinstance(add, dict):
                to_return.update(add)
            elif isinstance(add, list):
                to_return.extend(add)
    return to_return


def normalize(p):
    if path.isabs(path(p)):
        return path(p)
    else:
        return path((USER_ROOT_DIR / p).abspath())

# Directories
ENGINE_DIR = path(__file__).dirname().dirname().abspath()

USER_ROOT_DIR = check('USER_ROOT_DIR', path(USER_SETTINGS_MODULE.__file__).dirname().abspath())
DRAFT_DIR = normalize(check('DRAFT_DIR', 'drafts'))
PUBLISHED_DIR = normalize(check('PUBLISHED_DIR', 'published'))
TEMPLATE_DIR = normalize(check('TEMPLATE_DIR', ENGINE_DIR / 'templates'))
STATIC_DIR = normalize(check('STATIC_DIR', ENGINE_DIR / 'static'))
OUTPUT_DIR = normalize(check('OUTPUT_DIR', 'output'))
LOG_DIR = normalize(check('LOG_DIR', 'logs'))
LOG_FILE = normalize(check('LOG_FILE', 'build.log'))
CACHE_DIR = normalize(check('CACHE_DIR', 'cache'))
JINJA_CACHE_DIR = CACHE_DIR / 'jinja_cache'
POST_CACHE_FILE = CACHE_DIR / 'post_cache.cache'

# URLs
HOME_URL = check('HOME_URL', '/')
STATIC_URL = check('STATIC_URL', urljoin(HOME_URL, 'static'))
URLS = check('URLS', None)

# Themes
THEME = check('THEME', 'dark_rainbow')
THEMES_DIR = normalize(check('THEMES_DIR', path(ENGINE_DIR / 'themes').abspath()))
THEME_FINDERS = ['engineer.finders.DefaultFinder']

# Miscellaneous
DISABLE_CACHE = check('DISABLE_CACHE', False)
USE_CLIENT_SIDE_LESS = check('USE_CLIENT_SIDE_LESS', (platform.system() == 'Windows'))

# Ensure directories exist and create them if not
if not LOG_DIR.exists():
    logger.info("The log directory '%s' does not exist; creating." % LOG_DIR)
    LOG_DIR.makedirs()

if not CACHE_DIR.exists():
    logger.info("The cache directory '%s' does not exist; creating." % CACHE_DIR)
    CACHE_DIR.makedirs()

if not JINJA_CACHE_DIR.exists():
    logger.info("The jinja cache directory '%s' does not exist; creating." % JINJA_CACHE_DIR)
    JINJA_CACHE_DIR.makedirs()

# Configure Jinja2 environment
engineer = {
    'foundation_url': urljoin(STATIC_URL, 'engineer/lib/foundation/'),
    'jquery_url': urljoin(STATIC_URL, 'engineer/lib/jquery-1.6.2.min.js'),
    'modernizr_url': urljoin(STATIC_URL, 'engineer/lib/modernizr-2.0.6.min.js'),
    'lesscss_url': urljoin(STATIC_URL, 'engineer/lib/less-1.1.5.min.js'),
    }

JINJA_ENV = Environment(
    loader=FileSystemLoader([TEMPLATE_DIR, ENGINE_DIR / 'themes/templates']),
    extensions=['jinja2.ext.with_',
                'compressinja.html.HtmlCompressor'],
    bytecode_cache=FileSystemBytecodeCache(directory=JINJA_CACHE_DIR),
    trim_blocks=True)
#JINJA_ENV.filters['date'] = format_datetime
#JINJA_ENV.globals['engineer'] = engineer
#JINJA_ENV.globals['theme'] = get_class('engineer.themes.ThemeManager').current_theme()
#JINJA_ENV.globals['urlname'] = get_class('engineer.urls').urlname
#JINJA_ENV.globals['url'] = get_class('engineer.urls').url
#JINJA_ENV.globals['STATIC_URL'] = STATIC_URL
#JINJA_ENV.globals['config'] = get_class('engineer.conf.settings')
