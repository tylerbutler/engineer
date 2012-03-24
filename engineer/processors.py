# coding=utf-8
import subprocess
from path import path
from engineer.conf import settings
from engineer.log import logger

__author__ = 'tyler@tylerbutler.com'

# Helper function to preprocess LESS files on demand
def preprocess_less(file):
    file = path(settings.OUTPUT_CACHE_DIR / settings.ENGINEER.STATIC_DIR.basename() / file)
    css_file = path("%s.css" % str(file)[:-5])
    if not css_file.exists():
        result = subprocess.check_output("\"%s\" %s" % (settings.LESS_PREPROCESSOR, file))
        logger.info("Preprocessed LESS file %s." % file)
        file.remove_p()
    return ""
