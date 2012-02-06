# coding=utf-8
from inspect import isfunction
from engineer.conf import settings
from engineer.util import urljoin

__author__ = 'tyler@tylerbutler.com'

def urlname(name, *args):
    url = settings.URLS.get(name, None)
    if isfunction(url):
        return url(*args)
    else:
        return url


def url(path):
    return urljoin(urlname('home'), path)


def page(num):
    page_path = urljoin('page', str(num))
    return url(page_path)


DEFAULT_URLS = {
    'home': '/',
    'atom_feed': 'feeds/atom.xml',
    'rss_feed': 'feeds/rss.xml',
    'page': page,
    }
