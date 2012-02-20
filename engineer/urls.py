# coding=utf-8
from inspect import isfunction
from engineer.conf import settings
from engineer.util import urljoin

__author__ = 'tyler@tylerbutler.com'

def urlname(name, *args):
    url = settings.URLS.get(name, settings.HOME_URL)
    if isfunction(url):
        return url(*args)
    else:
        return url


def url(path):
    return urljoin(urlname('home'), path)
