# coding=utf-8
from path import path
import posixpath
import re
import filecmp
import hashlib
import logging
import translitcodec
from itertools import chain, islice
from urlparse import urljoin, urlparse, urlunparse

__author__ = 'tyler@tylerbutler.com'

_punctuation_regex = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, length_limit=0, delimiter=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punctuation_regex.split(text.lower()):
        word = word.encode('translit/long')
        if word:
            result.append(word)
    slug = unicode(delimiter.join(result))
    if length_limit > 0:
        return slug[0:length_limit]
    return slug


def get_class( class_string ):
    """Given a string representing a path to a class, instantiates that class."""
    parts = class_string.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def count_iterable(i):
    return sum(1 for e in i)


def expand_url(home, url):
    join = urljoin(home, url)
    url2 = urlparse(join)
    path = posixpath.normpath(url2[2])

    return urlunparse(
        (url2.scheme, url2.netloc, path, url2.params, url2.query, url2.fragment)
    )


def urljoin(url1, url2):
    return posixpath.join(url1, url2)


def checksum(file):
    with open(file) as f:
        checksum = hashlib.sha256(f.read()).hexdigest()
    return checksum


def chunk(seq, chunksize, process=iter):
    it = iter(seq)
    while True:
        yield process(chain([it.next()], islice(it, chunksize - 1)))

# class comes from Django
class LazyObject(object):
    """
    A wrapper for another class that can be used to delay instantiation of the
    wrapped class.

    By subclassing, you have the opportunity to intercept and alter the
    instantiation. If you don't need to do that, use SimpleLazyObject.
    """
    def __init__(self):
        self._wrapped = None

    def __getattr__(self, name):
        if self._wrapped is None:
            self._setup()
        return getattr(self._wrapped, name)

    def __setattr__(self, name, value):
        if name == "_wrapped":
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__["_wrapped"] = value
        else:
            if self._wrapped is None:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        if name == "_wrapped":
            raise TypeError("can't delete _wrapped.")
        if self._wrapped is None:
            self._setup()
        delattr(self._wrapped, name)

    def _setup(self):
        """
        Must be implemented by subclasses to initialise the wrapped object.
        """
        raise NotImplementedError

    # introspection support:
    __members__ = property(lambda self: self.__dir__())

    def __dir__(self):
        if self._wrapped is None:
            self._setup()
        return  dir(self._wrapped)

def sync_folders(d1, d2):
    logging.debug("Synchronizing %s ==> %s" % (d1, d2))
    if not d2.exists():
        d2.makedirs()
    compare = filecmp.dircmp(d1, d2)
    for item in compare.left_only:
        fullpath = d1 / item
        if fullpath.isdir():
            logging.debug("Copying new directory %s ==> %s" % (fullpath, (d2 / item)))
            fullpath.copytree(d2 / item)
        elif fullpath.isfile():
            logging.debug("Copying new file %s ==> %s" % (fullpath, d2))
            fullpath.copy2(d2)
    for item in compare.diff_files:
        logging.debug("Overwriting existing file %s ==> %s" % ((d1 / item), d2))
        (d1 / item).copy2(d2)
    for item in compare.common_dirs:
        sync_folders(d1 / item, d2 / item)

def ensure_exists(p):
    """
    Ensures a given path *p* exists.

    If a path to a file is passed in, then the path to the file will be checked.
    """
    if path(p).ext:
        path(p).dirname().makedirs_p()
    else:
        path(p).makedirs_p()
    return p
