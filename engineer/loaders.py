# coding=utf-8
import logging

from path import path

from engineer.conf import settings
from engineer.exceptions import PostMetadataError
from engineer.models import Post, PostCollection


__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

logger = logging.getLogger(__name__)


#noinspection PyShadowingBuiltins
class LocalLoader(object):
    @staticmethod
    def load_all(input):
        new_posts = PostCollection()
        cached_posts = PostCollection()

        # parse input directories into a dict. The key is the path, the value is a bool indicating
        # whether the path should be walked when looking for posts or not
        directories = {}
        for dir in input:
            if unicode(dir).endswith('*'):
                directories[path(dir[:-1]).expand().abspath().normpath()] = True
            else:
                directories[path(dir).expand().abspath().normpath()] = False

        file_list = []
        for directory, should_walk in directories.iteritems():
            if directory.exists():
                logger.info("Getting posts from %s." % directory)
                if should_walk:
                    file_list.extend([f for f in directory.walkfiles('*.md')] +
                                     [f for f in directory.files('*.markdown')])
                else:
                    file_list.extend(directory.files('*.md') + directory.files('*.markdown'))
            else:
                logger.warning("Can't find source post directory %s." % directory)

        for f in file_list:
            try:
                if f not in settings.POST_CACHE:
                    logger.debug("'%s': Beginning to parse." % f.basename())
                    post = Post(f)
                    logger.debug("'%s': Parsed successfully." % f.basename())
                    new_posts.append(post)
                    logger.info("'%s': LOADED" % f.basename())
                else:
                    logger.info("'%s': FROM CACHE" % f.basename())
                    cached_posts.append(settings.POST_CACHE[f])
            except PostMetadataError as e:
                logger.warning("SKIPPING '%s': metadata is invalid. %s" % (f.basename(), e.message))
                continue
        logger.console("Found %d new posts and loaded %s from the cache." % (len(new_posts), len(cached_posts)))

        settings.CACHE.sync()
        return new_posts, cached_posts
