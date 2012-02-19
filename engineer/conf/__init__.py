# coding=utf-8
import os
import sys
from path import path
from engineer.conf._settings import LazySettings
from engineer.log import logger

__author__ = 'tyler@tylerbutler.com'

settings = LazySettings()

def configure_settings(settings_module):
    if path.getcwd() not in sys.path:
        sys.path.append(path.getcwd())
    os.environ['ENGINEER_SETTINGS_MODULE'] = settings_module
    logger.info("Using settings module: '%s'" % os.environ['ENGINEER_SETTINGS_MODULE'])
