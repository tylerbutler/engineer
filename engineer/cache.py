# coding=utf-8
from path import path

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


class SimpleFileCache(object):
    # noinspection PyUnusedLocal
    def __init__(self, version=None, *args):
        self._cache = {}
        self._meta = {}
        self._version = version

        self.clear()

        if version is not None:
            self._version = version

    def __getitem__(self, item):
        return self._cache[item]

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

        self._cache[key] = value

    def __delitem__(self, key):
        del self._meta[key]
        del self._cache[key]

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
            return item in self._cache

    def __repr__(self):
        from pprint import pprint

        return pprint((self._meta, self._cache))

    def clear(self):
        self._cache.clear()
        self._meta.clear()
