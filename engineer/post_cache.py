# coding=utf-8
import cPickle as pickle
from path import path
from engineer.conf import settings
from engineer.log import logger

__author__ = 'tyler@tylerbutler.com'

class _PostCache(object):
    _cache = {}

    def __getitem__(self, item):
        return self._cache.__getitem__(item)

    def __setitem__(self, key, value):
        return self._cache.__setitem__(key, value)

    def __delitem__(self, key):
        return self._cache.__delitem__(key)

    def __contains__(self, item):
        return self._cache.__contains__(item)

    def __iter__(self):
        return self._cache.__iter__()

    def clear(self):
        self._cache.clear()
        self.CACHE_VERSION = 1.2
        self.enabled = not settings.DISABLE_CACHE
        self._cache_file = settings.POST_CACHE_FILE

    def __init__(self, *args):
        self.clear()
        try:
            with open(self._cache_file, mode='rb') as f:
                temp_cache = pickle.load(f)
                if not hasattr(temp_cache, 'CACHE_VERSION') or temp_cache.CACHE_VERSION != self.CACHE_VERSION:
                    logger.debug("The current post cache is version %s; current version is %s. Rebuilding cache." %
                                 (temp_cache['CACHE_VERSION'], self.CACHE_VERSION))
                    self.clear()
                else:
                    self.CACHE_VERSION = temp_cache.CACHE_VERSION
                    self._cache = temp_cache._cache
        except (KeyError, IOError, AttributeError, EOFError, TypeError), e:
            self.clear()

    def is_cached(self, file):
        if not self.enabled:
            return False

        file = path(file).abspath()
        if file not in self:
            return False
        cache_entry = self[file]
        if cache_entry['mtime'] != file.mtime:
            return False
        if cache_entry['size'] != file.size:
            return False
        if cache_entry['checksum'] != file.read_hexhash('sha256'):
            return False
        return True

    def save(self):
        if not self.enabled:
            return

        cache_file = path(self._cache_file).abspath()
        with open(cache_file, mode='wb') as f:
            pickle.dump(self, f)

    def delete(self):
        try:
            path(self._cache_file).abspath().remove()
        except OSError as we:
            if hasattr(we, 'winerror') and we.winerror not in (2, 3):
                logger.exception(we.message)
        self.clear()

POST_CACHE = _PostCache()
