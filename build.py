# coding=utf-8
import argparse
import logging
import os
from engineer.engine import build, clean

__author__ = 'tyler@tylerbutler.com'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description="Engineer site builder.")
    parser.add_argument('--settings', dest='settings_module', default='settings',
                        help="Specify a configuration file to use.")
    parser.add_argument('-c', '--clean', dest='clean', action='store_true', help="Clean the output directory.")
    parser.add_argument('-n', '--no-cache', dest='disable_cache', action='store_true', help="Disable the post cache.")
    args = parser.parse_args()

    os.environ['ENGINEER_SETTINGS_MODULE'] = args.settings_module
    from engineer.conf import settings

    settings.DISABLE_CACHE = args.disable_cache
    if args.clean:
        clean()
        exit()

    build()
    exit()
