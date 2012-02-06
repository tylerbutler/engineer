# coding=utf-8
import logging
from path import path
from engineer.conf import settings
from engineer.models import Post, MetadataError, PostCollection, PostCache

__author__ = 'tyler@tylerbutler.com'

class LocalLoader(object):
    @staticmethod
    def load_all(input=settings.DRAFT_DIR):
        posts = PostCollection()
        file_list = path(input).listdir('*.md') + path(input).listdir('*.markdown')
        print file_list
        for f in file_list:#path(input).walkfiles(pattern='*.{md,*.markdown}'):
            try:
                if not PostCache.is_cached(f):
                    logging.debug("'%s': Beginning to parse." % f.basename())
                    post = Post(f)
                    logging.debug("'%s': Parsed successfully." % f.basename())
                    posts.append(post)
                else:
                    logging.debug("'%s': SKIPPING - file is cached and does not need to be generated again." % f.basename())
            except MetadataError as e:
                logging.warning("'%s': SKIPPING - metadata is invalid. %s" % (f.basename(), e.message))
                continue
        logging.debug("Successfully parsed %d items." % len(posts))
        PostCache._save_cache()
        return posts
