# coding=utf-8
from path import path
from engineer.models import Post, MetadataError, PostCollection
from engineer.post_cache import POST_CACHE
from engineer.log import logger

__author__ = 'tyler@tylerbutler.com'

class LocalLoader(object):
    @staticmethod
    def load_all(input):
        new_posts = PostCollection()
        cached_posts = PostCollection()
        file_list = path(input).listdir('*.md') + path(input).listdir('*.markdown')
        for f in file_list:
            try:
                if not POST_CACHE.is_cached(f):
                    logger.debug("'%s': Beginning to parse." % f.basename())
                    post = Post(f)
                    logger.debug("'%s': Parsed successfully." % f.basename())
                    new_posts.append(post)
                    logger.info("'%s': LOADED successfully." % f.basename())
                else:
                    logger.debug("'%s': FROM CACHE" % f.basename())
                    cached_posts.append(POST_CACHE[f]['post'])
            except MetadataError as e:
                logger.warning("SKIPPING '%s': metadata is invalid. %s" % (f.basename(), e.message))
                continue
        logger.info(
            "Successfully parsed %d new items and loaded %s from the cache." % (len(new_posts), len(cached_posts)))
        POST_CACHE.save()
        return new_posts, cached_posts
