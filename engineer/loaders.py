# coding=utf-8
import logging
from path import path
from engineer.conf import settings
from engineer.exceptions import PostMetadataError
from engineer.models import Post, PostCollection

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

logger = logging.getLogger(__name__)

class LocalLoader(object):
    @staticmethod
    def load_all(input):
        new_posts = PostCollection()
        cached_posts = PostCollection()

        file_list = []
        for directory in input:
            logger.info("Getting posts from %s." % directory)
            file_list.extend(path(directory).listdir('*.md') + path(directory).listdir('*.markdown'))

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
