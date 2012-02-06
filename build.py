# coding=utf-8
import argparse
import logging
import os
from codecs import open
from engineer.conf import globals, settings
from engineer.loaders import LocalLoader
from engineer.models import PostCollection, PostCache
from engineer.themes import ThemeManager
from engineer.util import sync_folders

__author__ = 'tyler@tylerbutler.com'

def clean():
    try:
        settings.OUTPUT_DIR.rmtree()
        logging.info('Cleaned output directory: %s' % settings.OUTPUT_DIR)
    except WindowsError as we:
        if we.winerror not in (2, 3):
            logging.exception(we.message)


def build():
    logging.debug("Loading drafts.")
    all_posts = LocalLoader.load_all()

    logging.debug("Loading published.")
    all_posts.extend(LocalLoader.load_all(input=settings.PUBLISHED_DIR))

    logging.debug("Drafts: %d, Published: %d" % (len(all_posts.drafts), len(all_posts.published)))
    #
    #all_posts = PostCollection()
    #all_posts.extend(published)
    #all_posts.extend(drafts)
    #all_posts = pynq.From(all_posts).where("item.status == Status.published").select_many()
    #[(post if post.status!=Status.draft else None)for post in all_posts]

    all_posts = PostCollection(sorted(all_posts.drafts, reverse=True, key=lambda post: post.timestamp))

    # Generate individual post pages
    for post in all_posts:
        rendered_post = post.render_html()
        if not post.output_path.exists():
            post.output_path.makedirs()
        with open(post.output_path / post.output_file_name, mode='wb', encoding='UTF-8') as file:
            logging.info("Output '%s'." % file.name)
            file.write(rendered_post)

    # Generate rollup pages
    num_posts = len(all_posts)
    num_slices = (num_posts / 5) if num_posts % 5 == 0 else (num_posts / 5) + 1

    slice_num = 0
    for posts in all_posts.paginate():
        slice_num += 1
        has_next = slice_num < num_slices
        has_previous = 1 < slice_num <= num_slices
        rendered_page = posts.render_html(slice_num, has_next, has_previous)
        if not posts.output_path(slice_num).exists():
            posts.output_path(slice_num).dirname().makedirs()
        with open(posts.output_path(slice_num), mode='wb', encoding='UTF-8') as file:
            logging.info("Output '%s'." % file.name)
            file.write(rendered_page)


    # Copy static content to output dir
    sync_folders(settings.STATIC_DIR.abspath(),
                 (settings.STATIC_DIR.relpathto(settings.OUTPUT_DIR) / settings.STATIC_DIR.basename()).abspath())

    # Copy theme static content to output dir
    s = ThemeManager.current_theme().static_root.abspath()
    t = (settings.STATIC_DIR.relpathto(settings.OUTPUT_DIR) / settings.STATIC_DIR.basename() / 'theme').abspath()
    sync_folders(s, t)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Engineer site builder.")
    parser.add_argument('--settings', dest='settings_module', default='config',
                        help="Specify a configuration file to use.")
    parser.add_argument('-c', '--clean', dest='clean', action='store_true', help="Clean the output directory.")
    parser.add_argument('-n', '--no-cache', dest='disable_cache', action='store_true', help="Disable the post cache.")
    args = parser.parse_args()

    settings.DISABLE_CACHE = args.disable_cache
    if args.clean:
        clean()
        PostCache.delete()
        #config.CACHE_DIR.rmtree()
        exit()

    os.environ['ENGINEER_SETTINGS_MODULE'] = args.settings_module
    build()
    exit()
