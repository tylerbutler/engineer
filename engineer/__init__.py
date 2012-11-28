# coding=utf-8
import os

try:
    from _version import version
except ImportError:

    print "Got an import error"
    from propane_distribution import update_version_py

    update_version_py(version_path=os.path.dirname(__file__))
    from _version import version

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'
