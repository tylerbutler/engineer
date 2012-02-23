# coding=utf-8
import cPickle as pickle
from path import path
from engineer.conf import settings
from engineer.log import logger
from engineer.util import Borg

__author__ = 'tyler@tylerbutler.com'

class CacheBorg(object):
    _state = {}

    def __new__(cls, *p, **k):
        self = object.__new__(cls)
        self.__dict__ = cls._state
        return self


class _CacheDict(dict):
    def __init__(self, cache_version):
        dict.__init__(self)
        self.cache_version = cache_version


class _PostCache(CacheBorg):
    CACHE_VERSION = 1.1
    _dict = _CacheDict(CACHE_VERSION)

    def __getitem__(self, item):
        return self._dict.__getitem__(item)

    def __setitem__(self, key, value):
        return self._dict.__setitem__(key, value)

    def __delitem__(self, key):
        return self._dict.__delitem__(key)

    def __contains__(self, item):
        return self._dict.__contains__(item)

    def __iter__(self):
        return self._dict.__iter__()

    def clear(self):
        self._dict.clear()

    def __init__(self, *args):
        self.enabled = not settings.DISABLE_CACHE
        self._cache_file = settings.POST_CACHE_FILE

        try:
            with open(self._cache_file) as f:
                temp_cache = pickle.load(f)
                if temp_cache.cache_version != self.CACHE_VERSION:
                    logger.debug("The current post cache is version %s; current version is %s. Rebuilding cache." %
                                 (temp_cache.cache_version, self.CACHE_VERSION))
                    self._dict.clear()
                else:
                    self._dict = temp_cache
        except (IOError, AttributeError, EOFError, TypeError):
            self._dict.clear()

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

        self._dict.cache_version = self.CACHE_VERSION
        cache_file = path(self._cache_file).abspath()
        with open(cache_file, mode='wb') as f:
            pickle.dump(self._dict, f)

    def delete(self):
        try:
            path(self._cache_file).abspath().remove()
        except WindowsError as we:
            if we.winerror not in (2, 3):
                logger.exception(we.message)
        self.clear()


class _PostCacheWrapper(Borg):
    _cache = _PostCache()

    def delete(self):
        self._cache.delete()

    def is_cached(self, file):
        return self._cache.is_cached(file)

POST_CACHE = _PostCache()
