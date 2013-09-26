# coding=utf-8
import collections
import filecmp
import hashlib
import itertools
import logging
import posixpath
import re
from itertools import chain, islice
import urlparse

#noinspection PyUnresolvedReferences
import translitcodec
#noinspection PyPackageRequirements
from path import path


__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

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


def get_class(class_string):
    """Given a string representing a path to a class, instantiates that class."""
    parts = class_string.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def count_iterable(i):
    #noinspection PyUnusedLocal
    return sum(1 for e in i)


def expand_url(home, url):
    join = urlparse.urljoin(home, url)
    url2 = urlparse.urlparse(join)
    the_path = posixpath.normpath(url2[2])

    return urlparse.urlunparse(
        (url2.scheme, url2.netloc, the_path, url2.params, url2.query, url2.fragment)
    )


def urljoin(url1, url2):
    # This method is necessary because sometimes urlparse.urljoin simply doesn't work correctly
    # when joining URL fragments.
    return posixpath.join(url1, url2)


def checksum(the_file):
    with open(the_file) as f:
        _checksum = hashlib.sha256(f.read()).hexdigest()
    return _checksum


def chunk(seq, chunksize, process=iter):
    it = iter(seq)
    while True:
        yield process(chain([it.next()], islice(it, chunksize - 1)))


def mirror_folder(source, target, delete_orphans=True, recurse=True, ignore_list=None, _level=0):
    """Mirrors a folder *source* into a target folder *target*."""

    logger = logging.getLogger('engineer.util.mirror_folder')

    def expand_tree(p):
        tree = []
        for node in path(p).walk():
            tree.append(node)
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

    # Expand the ignore list to be full paths
    if ignore_list is None:
        ignore_list = []

    ignore_list = [path(d2 / i) for i in ignore_list]

    # Delete orphan files/folders in the target folder
    if delete_orphans:
        for item in compare.right_only:
            fullpath = path(d2 / item)
            if fullpath in ignore_list:
                logger.debug(
                    "%s ==> Ignored - path is in ignore list" % fullpath)
                continue

            if fullpath.isdir() and recurse:
                logger.debug(
                    "%s ==> Deleted - doesn't exist in source" % fullpath)
                report['deleted'].add(fullpath)
                if len(fullpath.listdir()) > 0:
                    report['deleted'].update(expand_tree(fullpath))

                #noinspection PyArgumentList
                fullpath.rmtree()
            elif fullpath.isfile():
                logger.debug(
                    "%s ==> Deleted - doesn't exist in source" % fullpath)
                report['deleted'].add(fullpath)
                fullpath.remove()

    # Copy new files and folders from the source to the target
    for item in compare.left_only:
        fullpath = d1 / item
        if fullpath.isdir() and recurse:
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
    if recurse:
        for item in compare.common_dirs:
            rpt = mirror_folder(d1 / item, d2 / item, delete_orphans, _level=_level + 1)
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
    """
    Returns an object as a list.

    If the object is a list, it is returned directly. If it is a tuple or set, it
    is returned as a list. If it is another object, it is wrapped in a list and
    returned.
    """
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


def relpath(the_path):
    from engineer.conf import settings

    return '/' + settings.OUTPUT_CACHE_DIR.relpathto(the_path)


def _min_css(css_string):
    from cssmin import cssmin

    return cssmin(css_string)


def _min_js(js_string):
    import lpjsmin

    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    the_input = StringIO(js_string)
    output = StringIO()
    lpjsmin.minify_stream(the_input, output)
    to_return = output.getvalue()
    output.close()
    the_input.close()
    return to_return


def compress(item, compression_type):
    if compression_type == 'css':
        return _min_css(item)
    elif compression_type == 'js':
        return _min_js(item)
    else:
        raise ValueError("Unexpected compression_type: %s" % compression_type)


# setonce class from Ian Bicking: http://blog.ianbicking.org/easy-readonly-attributes.html
_setonce_count = itertools.count()


class setonce(object):
    """
    Allows an attribute to be set once (typically in __init__), but
    be read-only afterwards.

    Example::

        >>> class A(object):
        ...     x = setonce()
        >>> a = A()
        >>> a.x
        Traceback (most recent call last):
        ...
        AttributeError: 'A' object has no attribute '_setonce_attr_0'
        >>> a.x = 10
        >>> a.x
        10
        >>> a.x = 20
        Traceback (most recent call last):
        ...
        AttributeError: Attribute already set
        >>> del a.x
        >>> a.x = 20
        >>> a.x
        20

    You can also force a set to occur::

        >>> A.x.set(a, 30)
        >>> a.x
        30
    """

    def __init__(self, doc=None):
        self._count = _setonce_count.next()
        self._name = '_setonce_attr_%s' % self._count
        self.__doc__ = doc

    #noinspection PyUnusedLocal
    def __get__(self, obj, obj_type=None):
        if obj is None:
            return self
        return getattr(obj, self._name)

    def __set__(self, obj, value):
        try:
            getattr(obj, self._name)
        except AttributeError:
            setattr(obj, self._name, value)
        else:
            raise AttributeError("Attribute already set")

    def set(self, obj, value):
        setattr(obj, self._name, value)

    def __delete__(self, obj):
        delattr(obj, self._name)


def update_additive(dict1, dict2):
    """
    A utility method to update a dict or other mapping type with the contents of another dict.

    This method updates the contents of ``dict1``, overwriting any existing key/value pairs in ``dict1`` with the
    corresponding key/value pair in ``dict2``. If the value in ``dict2`` is a mapping type itself, then
    ``update_additive`` is called recursively. This ensures that nested maps are updated rather than simply
    overwritten.

    This method should be functionally equivalent to ``dict.update()`` except in the case of values that are
    themselves nested maps. If you know that ``dict1`` does not have nested maps,
    or you want to overwrite all values with the exact content of then you should simply use ``dict.update()``.
    """
    for key, value in dict2.items():
        if key not in dict1:
            dict1[key] = value
        else:  # key in dict1
            if isinstance(dict1[key], collections.Mapping):
                assert isinstance(value, collections.Mapping)
                update_additive(dict1[key], value)
            else:  # value is not a mapping type
                assert not isinstance(value, collections.Mapping)
                dict1[key] = value
