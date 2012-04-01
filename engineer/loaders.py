# coding=utf-8
from path import path
from engineer.conf import settings
from engineer.log import logger
from engineer.models import Post, MetadataError, PostCollection

__author__ = 'tyler@tylerbutler.com'

class LocalLoader(object):
    @staticmethod
    def load_all(input):
        new_posts = PostCollection()
        cached_posts = PostCollection()

        file_list = []
        for directory in input:
            logger.debug("Getting posts from %s." % directory)
            file_list.extend(path(directory).listdir('*.md') + path(directory).listdir('*.markdown'))

        for f in file_list:
            try:
                if f not in settings.POST_CACHE:
                    logger.debug("'%s': Beginning to parse." % f.basename())
                    post = Post(f)
                    logger.debug("'%s': Parsed successfully." % f.basename())
                    new_posts.append(post)
                    logger.info("'%s': LOADED successfully." % f.basename())
                else:
                    logger.debug("'%s': FROM CACHE" % f.basename())
                    cached_posts.append(settings.POST_CACHE[f])
            except MetadataError as e:
                logger.warning("SKIPPING '%s': metadata is invalid. %s" % (f.basename(), e.message))
                continue
        logger.info(
            "Successfully parsed %d new items and loaded %s from the cache." % (len(new_posts), len(cached_posts)))

        settings.CACHE.sync()
        return new_posts, cached_posts
