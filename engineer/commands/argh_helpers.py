# coding=utf-8
from __future__ import absolute_import

try:
    # noinspection PyUnresolvedReferences
    from argh.decorators import arg

    argh_installed = True
except ImportError:
    argh_installed = False

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

if argh_installed:
    # noinspection PyUnresolvedReferences
    from argh.helpers import set_default_command

    _no_config_file_registry = []

    config_file = arg('-s', '--config', '--settings',
                      dest='config_file',
                      default='config.yaml',
                      help="Specify a configuration file to use.")

    verbose = arg('-v', '--verbose',
                  dest='verbose',
                  action='count',
                  default=0,
                  help="Display verbose output.")

    def no_config_file(*args):
        def wrapper(func):
            _no_config_file_registry.append(func)
            return func
        return wrapper

    def does_not_require_config_file(func):
        return func in _no_config_file_registry

