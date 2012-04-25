# coding=utf-8
import sys
import logging

__author__ = 'tyler@tylerbutler.com'

CONSOLE = 1000

class CustomLogger(logging.getLoggerClass()):
    def console(self, msg, *args, **kwargs):
        self.log(CONSOLE, msg, *args, **kwargs)


def bootstrap():
    logging.setLoggerClass(CustomLogger)
    logging.addLevelName(CONSOLE, 'CONSOLE')

    root_logger = logging.getLogger('engineer')
    root_logger.setLevel(logging.DEBUG)


def get_console_handler(level=CONSOLE):
    console_formatter = logging.Formatter(fmt="%(message)s",
                                          datefmt='%H:%M:%S')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    return console_handler


def get_file_handler(file, mode='w'):
    handler = logging.FileHandler(file, mode=mode)
    handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)8s %(name)30s     %(message)s",
                                           datefmt='%H:%M:%S'))
    handler.setLevel(logging.DEBUG)
    return handler
