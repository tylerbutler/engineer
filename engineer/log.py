# coding=utf-8
import sys, platform
import logging
from brownie.caching import memoize
from engineer.lib.ansistrm import ColorizingStreamHandler

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

CONSOLE = 1000

class Colors(object):
    BLACK = 'black'
    RED = 'red'
    GREEN = 'green'
    YELLOW = 'yellow'
    BLUE = 'blue'
    MAGENTA = 'magenta'
    CYAN = 'cyan'
    WHITE = 'white'


class CustomLogger(logging.getLoggerClass()):
    def console(self, msg, *args, **kwargs):
        self.log(CONSOLE, msg, *args, **kwargs)


class ColorStreamHandler(ColorizingStreamHandler):
    def __init__(self, stream=None):
        super(ColorizingStreamHandler, self).__init__(stream)

        #levels to (background, foreground, bold/intense)
        self.level_map.update({
            CONSOLE: (None, Colors.WHITE, False),
            logging.DEBUG: (None, Colors.BLUE, True),
            logging.INFO: (None, Colors.GREEN, True),
            logging.WARNING: (None, Colors.YELLOW, True),
            })


def bootstrap():
    logging.setLoggerClass(CustomLogger)
    logging.addLevelName(CONSOLE, 'CONSOLE')

    root_logger = logging.getLogger('engineer')
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(get_console_handler(logging.WARNING))


@memoize
def get_console_handler(level=CONSOLE):
    console_formatter = logging.Formatter(fmt="%(message)s",
                                          datefmt='%H:%M:%S')
    console_handler = ColorStreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    return console_handler


@memoize
def get_file_handler(file, mode='w'):
    handler = logging.FileHandler(file, mode=mode)
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)8s %(name)30s     %(message)s",
                                           datefmt='%H:%M:%S'))
    handler.setLevel(logging.DEBUG)
    return handler
