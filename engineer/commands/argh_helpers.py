# coding=utf-8
from __future__ import absolute_import

try:
    from argh.decorators import arg

    argh_installed = True
except ImportError:
    argh_installed = False

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


if argh_installed:
    from argh.helpers import set_default_command
