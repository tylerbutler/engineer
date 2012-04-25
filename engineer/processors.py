# coding=utf-8
import logging
import subprocess
from path import path
from engineer.conf import settings

__author__ = 'tyler@tylerbutler.com'

logger = logging.getLogger(__name__)

# Helper function to preprocess LESS files on demand
def preprocess_less(file):
    input_file = path(settings.OUTPUT_CACHE_DIR / settings.ENGINEER.STATIC_DIR.basename() / file)
    css_file = path("%s.css" % str(input_file)[:-5])
    if not css_file.exists():
        cmd = str.format(str(settings.LESS_PREPROCESSOR), infile=input_file, outfile=css_file).split()
        try:
            result = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            logger.critical(e.cmd)
            logger.critical(e.output)
            raise
        logger.info("Preprocessed LESS file %s." % file)
    return ""
