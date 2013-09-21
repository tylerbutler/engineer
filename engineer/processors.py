# coding=utf-8
import logging
import platform
import subprocess

from path import path

from engineer.conf import settings


__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

logger = logging.getLogger(__name__)


# noinspection PyShadowingBuiltins
# Helper function to preprocess LESS files on demand
def preprocess_less(file):
    input_file = path(settings.OUTPUT_CACHE_DIR / settings.ENGINEER.STATIC_DIR.basename() / file)
    css_file = path("%s.css" % str(input_file)[:-5])
    is_cached = input_file in settings.LESS_CACHE
    exists = css_file.exists()
    if is_cached and not exists:
        with open(css_file, mode='wb') as the_file:
            the_file.write(settings.LESS_CACHE[input_file])
        logger.info('Found cached output for LESS file %s. Skipping recompilation.' % file)
    elif not is_cached or not css_file.exists():
        cmd = str.format(str(settings.LESS_PREPROCESSOR), infile=input_file, outfile=css_file).split()
        try:
            subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            logger.critical("Error pre-processing LESS file %s." % file)
            logger.critical(e.output)
            exit(1355)
        except WindowsError as e:
            logger.critical("Unexpected error pre-processing LESS file %s." % file)
            logger.critical(e.strerror)
            exit(1355)
        except Exception as e:
            logger.critical("Unexpected error pre-processing LESS file %s." % file)
            logger.critical(e.message)
            if platform.system() != 'Windows':
                logger.critical("Are you sure lessc is on your path?")
            exit(1355)
        with open(css_file, mode='rb') as the_file:
            contents = the_file.read()
        settings.LESS_CACHE[input_file] = contents
        logger.info("Preprocessed LESS file %s ==> %s." % (file, css_file.name))
    return ""
