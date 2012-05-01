# coding=utf-8
import logging
import posixpath
import re
import filecmp
import hashlib
import translitcodec
from itertools import chain, islice
from path import path
from urlparse import urljoin, urlparse, urlunparse

__author__ = 'tyler@tylerbutler.com'

_punctuation_regex = re.compile(r'[\t :!"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

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


def mirror_folder(source, target, delete_orphans=True, _level=0):
    """Mirrors a folder *source* into a target folder *target*."""

    logger = logging.getLogger('engineer.util.mirror_folder')

    def expand_tree(p):
        tree = []
        for item in path(p).walk():
            tree.append(item)
        return tree

    report = {
        'deleted': set([]),
        'overwritten': set([]),
        'new': set([])
    }
    d1 = source
    d2 = target
    logger.debug("Mirroring %s ==> %s" % (d1, d2))
    if not d2.exists():
        d2.makedirs()
    compare = filecmp.dircmp(d1, d2)

    # Delete orphan files/folders in the target folder
    if delete_orphans:
        for item in compare.right_only:
            fullpath = path(d2 / item)
            if fullpath.isdir():
                logger.debug(
                    "%s ==> Deleted - doesn't exist in source" % fullpath)
                report['deleted'].add(fullpath)
                if len(fullpath.listdir()) > 0:
                    report['deleted'].update(expand_tree(fullpath))
                fullpath.rmtree()
            elif fullpath.isfile():
                logger.debug(
                    "%s ==> Deleted - doesn't exist in source" % fullpath)
                report['deleted'].add(fullpath)
                fullpath.remove()

    # Copy new files and folders from the source to the target
    for item in compare.left_only:
        fullpath = d1 / item
        if fullpath.isdir():
            logger.debug(
                "Copying new directory %s ==> %s" % (fullpath, (d2 / item)))
            fullpath.copytree(d2 / item)
            report['new'].add(d2 / item)
            report['new'].update(expand_tree(d2 / item))
        elif fullpath.isfile():
            logger.debug("Copying new file %s ==> %s" % (fullpath, (d2 / item)))
            fullpath.copy2(d2)
            report['new'].add(d2 / item)

    # Copy modified files in the source to the target, overwriting the target file
    for item in compare.diff_files:
        logger.debug(
            "Overwriting existing file %s ==> %s" % ((d1 / item), (d2 / item)))
        (d1 / item).copy2(d2)
        report['overwritten'].add(d2 / item)

    # Recurse into subfolders that exist in both the source and target
    for item in compare.common_dirs:
        rpt = mirror_folder(d1 / item, d2 / item, delete_orphans, _level + 1)
        report['new'].update(rpt['new'])
        report['overwritten'].update(rpt['overwritten'])
        report['deleted'].update(rpt['deleted'])
    return report


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


def wrap_list(item):
    if item is None:
        return []
    elif isinstance(item, list):
        return item
    elif isinstance(item, (tuple, set)):
        return list(item)
    else:
        return [item]


class Borg(object):
    """
    A class that shares state among all instances of the class.

    There seem to be a lot of differing opinions about whether this design
    pattern is A Good Idea (tm) or not. It definitely seems better than
    Singletons since it enforces *behavior*, not *structure*,
    but it's also possible there's a better way to do it in Python with
    judicious use of globals.
    """
    _state = {}

    def __new__(cls, *p, **k):
        self = object.__new__(cls)
        self.__dict__ = cls._state
        return self


def relpath(path):
    from engineer.conf import settings

    return '/' + settings.OUTPUT_CACHE_DIR.relpathto(path)


def _min_css(css_string):
    from cssmin import cssmin

    return cssmin(css_string)


def _min_js(js_string):
    import lpjsmin

    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    input = StringIO(js_string)
    output = StringIO()
    lpjsmin.minify_stream(input, output)
    to_return = output.getvalue()
    output.close()
    input.close()
    return to_return


def compress(item, compression_type):
    if compression_type == 'css':
        return _min_css(item)
    elif compression_type == 'js':
        return _min_js(item)
    else:
        raise ValueError("Unexpected compression_type: %s" % compression_type)
