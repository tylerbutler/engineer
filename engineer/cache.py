# coding=utf-8
from path import path

try:
    import cPickle as pickle
except ImportError:
    import pickle

from engineer.conf import settings
from engineer.log import logger

__author__ = 'tyler@tylerbutler.com'

class SimpleFileCache(object):
    _cache = {}
    _meta = {}
    _version = 1

    def __getitem__(self, item):
        return self._cache.__getitem__(item)

    def __setitem__(self, key, value):
        k = path(key)
        if k.exists():
            self._meta[key] = {
                #                'mtime': key.mtime,
                #                'size': key.size,
                'checksum': key.read_hexhash('sha256')
            }
        else:
            raise ValueError("File to be cached does not exist.")

        return self._cache.__setitem__(key, value)

    def __delitem__(self, key):
        self._meta.__delitem__(key)
        return self._cache.__delitem__(key)

    def __contains__(self, item):
        if item not in self._meta:
            return False
        else:
            cache_entry = self._meta[item]
            #            if cache_entry['mtime'] != item.mtime:
            #                return False
            #            if cache_entry['size'] != item.size:
            #                return False
            if cache_entry['checksum'] != item.read_hexhash('sha256'):
                return False
            return self._cache.__contains__(item)

    def __iter__(self):
        return self._cache.__iter__()

    def clear(self):
        self._cache.clear()
        self._meta.clear()

    def __init__(self, cache_file, version=None, *args):
        self.clear()
        self._cache_file = path(cache_file).abspath()

        if version is not None:
            self._version = version

        self.load_cache_from_file()

    def load_cache_from_file(self, file=None):
        if file is None:
            file = self._cache_file

        if file.exists():
            try:
                with open(file, mode='rb') as f:
                    temp_cache = pickle.load(f)
                if not hasattr(temp_cache, '_version') or temp_cache._version != self._version:
                    logger.debug("Loaded cache version %s; current version is %s. Rebuilding cache." %
                                 (temp_cache._version, self._version))
                    self.clear()
                else:
                    self._cache = temp_cache._cache
            except (KeyError, IOError, AttributeError, EOFError, TypeError) as e:
                logger.exception("Error loading cache from file: %s" % e.message)
                self.clear()

    def save(self):
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


COMPRESSION_CACHE = SimpleFileCache(settings.CACHE_DIR / 'compression_cache.cache', version=1)
LESS_CACHE = SimpleFileCache(settings.CACHE_DIR / 'less.cache', version=1)
