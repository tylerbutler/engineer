# coding=utf-8
from path import path
from engineer.models import Post, MetadataError, PostCollection
from engineer.log import logger

__author__ = 'tyler@tylerbutler.com'

class LocalLoader(object):
    @staticmethod
    def load_all(input):
        from engineer.post_cache import POST_CACHE
        posts = PostCollection()
        file_list = path(input).listdir('*.md') + path(input).listdir('*.markdown')
        for f in file_list:#path(input).walkfiles(pattern='*.{md,*.markdown}'):
            try:
                if not POST_CACHE.is_cached(f):
                    logger.debug("'%s': Beginning to parse." % f.basename())
                    post = Post(f)
                    logger.debug("'%s': Parsed successfully." % f.basename())
                    posts.append(post)
                    logger.info("'%s': LOADED successfully." % f.basename())
                else:
                    logger.info("'%s': SKIPPING - file is cached and does not need to be generated again." %
                                f.basename())
            except MetadataError as e:
                logger.warning("'%s': SKIPPING - metadata is invalid. %s" % (f.basename(), e.message))
                continue
        logger.debug("Successfully parsed %d items." % len(posts))
        POST_CACHE.save()
        return posts
