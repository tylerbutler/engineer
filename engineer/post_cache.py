# coding=utf-8
import cPickle as pickle
import logging
from path import path
from engineer.conf import settings
from engineer.conf._globals import POST_CACHE as GLOBAL_CACHE

__author__ = 'tyler@tylerbutler.com'

#class _PostCacheNew(dict):
#    CACHE_VERSION = 0
#
#    def __init__(self, empty=False):
#        if not empty:
#            _PostCache.load()
#            #dict.__init__(tmp)
#        else:
#            dict.__init__(self)
#
#    @staticmethod
#    def is_cached(file):
#        if settings.DISABLE_CACHE:
#            return False
#
#        file = path(file).abspath()
#        if file not in POST_CACHE:
#            return False
#        cache_entry = POST_CACHE[file]
#        if cache_entry['mtime'] != file.mtime:
#            return False
#        if cache_entry['size'] != file.size:
#            return False
#        if cache_entry['checksum'] != file.read_hexhash():
#            return False
#        return True
#
#    @staticmethod
#    def load():
#        try:
#            if settings.DISABLE_CACHE or hasattr(settings, 'POST_CACHE'):
#                return None
#        except:
#            return None
#
#        cache_file = settings.POST_CACHE_FILE
#        try:
#            with open(cache_file) as f:
#                pickled_cache = pickle.load(f)
#                if pickled_cache.pickled_version != _PostCache.CACHE_VERSION:
#                    return _PostCache(empty=True)
#            return pickled_cache
#        except:# (IOError, AttributeError, EOFError):
#            return _PostCache(empty=True)
#
#    @staticmethod
#    def save():
#        if settings.DISABLE_CACHE:
#            return
#
#        POST_CACHE.pickled_version = _PostCache.CACHE_VERSION
#        cache_file = path(settings.POST_CACHE_FILE).abspath()
#        with open(cache_file, mode='wb') as f:
#            try:
#                logging.error('saving cache!')
#                #d = dict(settings.POST_CACHE)
#                pickle.dump(POST_CACHE, f)
#            except Exception as ex:
#                logging.exception(ex)
#
#    @staticmethod
#    def delete():
#        try:
#            path(settings.POST_CACHE_FILE).abspath().remove()
#        except WindowsError as we:
#            if we.winerror not in (2, 3):
#                logging.exception(we.message)
#        POST_CACHE = _PostCache(empty=True)

TEMP_CACHE = None

class _PostCache(dict):
    CACHE_VERSION = 1

    def __init__(self, empty=False):
        dict.__init__(self)
        if not empty:
            _PostCache._load_cache()
            global POST_CACHE, TEMP_CACHE
            POST_CACHE = TEMP_CACHE

    @staticmethod
    def is_cached(file):
        if settings.DISABLE_CACHE:
            return False

        file = path(file).abspath()
        if file not in POST_CACHE:
            return False
        cache_entry = POST_CACHE[file]
        if cache_entry['mtime'] != file.mtime:
            return False
        if cache_entry['size'] != file.size:
            return False
        if cache_entry['checksum'] != file.read_hexhash('sha256'):
            return False
        return True

    @staticmethod
    def _load_cache():
        global TEMP_CACHE
        try:
            if settings.DISABLE_CACHE:# or hasattr(settings, 'POST_CACHE'):
                return
        except Exception, e:
            TEMP_CACHE = _PostCache(empty=True)

        cache_file = settings.POST_CACHE_FILE
        try:
            with open(cache_file) as f:
                TEMP_CACHE = pickle.load(f)
                if TEMP_CACHE.pickled_version != _PostCache.CACHE_VERSION:
                    logging.debug("The current post cache is version %s; current version is %s. Rebuilding cache." %
                        (TEMP_CACHE.pickled_version, _PostCache.CACHE_VERSION))
                    TEMP_CACHE = _PostCache(empty=True)
        except (IOError, AttributeError, EOFError):
            TEMP_CACHE = _PostCache(empty=True)

    @staticmethod
    def save():
        if settings.DISABLE_CACHE:
            return

        POST_CACHE.pickled_version = _PostCache.CACHE_VERSION
        cache_file = path(settings.POST_CACHE_FILE).abspath()
        with open(cache_file, mode='wb') as f:
            d = dict(POST_CACHE)
            pickle.dump(POST_CACHE, f)

    @staticmethod
    def delete():
        try:
            path(settings.POST_CACHE_FILE).abspath().remove()
        except WindowsError as we:
            if we.winerror not in (2, 3):
                logging.exception(we.message)
        POST_CACHE = _PostCache(empty=True)

_PostCache()

POST_CACHE = TEMP_CACHE
