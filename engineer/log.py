# coding=utf-8
import logging
import pprint
import sys

from brownie.caching import memoize
from crayola import initialize, ColorStreamHandler


__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

CONSOLE = 1000


class CustomLogger(logging.getLoggerClass()):
    def console(self, msg, *args, **kwargs):
        self.log(CONSOLE, msg, *args, **kwargs)


def bootstrap():
    initialize()
    logging.setLoggerClass(CustomLogger)
    logging.addLevelName(CONSOLE, 'CONSOLE')

    root_logger = logging.getLogger('engineer')
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(get_console_handler(logging.WARNING))


pprinter = pprint.PrettyPrinter()


# noinspection PyBroadException
def log_object(obj):
    try:
        return pprinter.pformat(obj)
    except Exception:
        return str(obj)


@memoize
def get_console_handler(level=CONSOLE):
    console_formatter = logging.Formatter(fmt="%(message)s",
                                          datefmt='%H:%M:%S')
    console_handler = ColorStreamHandler(sys.stdout)
    console_handler.level_map[CONSOLE] = console_handler.default_colors
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    return console_handler


@memoize
def get_file_handler(the_file, mode='w'):
    handler = logging.FileHandler(the_file, mode=mode)
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)8s %(name)30s     %(message)s",
                                           datefmt='%H:%M:%S'))
    handler.setLevel(logging.DEBUG)
    return handler
