# coding=utf-8
import logging
from path import path
from engineer.conf import settings
from engineer.exceptions import PostMetadataError
from engineer.models import Post, PostCollection

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

logger = logging.getLogger(__name__)


# noinspection PyShadowingBuiltins
class LocalLoader(object):
    @staticmethod
    def load_all(input):
        new_posts = PostCollection()
        cached_posts = PostCollection()

        # expand user paths in all post paths
        directories = [path(p).expand().abspath() for p in input]

        file_list = []
        for directory in directories:
            if directory.exists():
                logger.info("Getting posts from %s." % directory)
                file_list.extend(directory.listdir('*.md') + directory.listdir('*.markdown'))
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
