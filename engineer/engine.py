# coding=utf-8
import argparse
import sys
from codecs import open
from path import path
from engineer.conf import settings, configure_settings
from engineer.loaders import LocalLoader
from engineer.models import PostCollection, TemplatePage
from engineer.themes import ThemeManager
from engineer.util import sync_folders
from engineer.log import logger, get_logger

__author__ = 'tyler@tylerbutler.com'

def clean():
    try:
        settings.OUTPUT_DIR.rmtree()
    except WindowsError as we:
        if we.winerror not in (2, 3):
            logger.exception(we.message)
        else:
            logger.info("Couldn't find output directory: %s" % settings.OUTPUT_DIR)
    from engineer.post_cache import POST_CACHE

    POST_CACHE.delete()
    logger.info('Cleaned output directory: %s' % settings.OUTPUT_DIR)


def build():
    # Generate template pages
    for template in (settings.TEMPLATE_DIR / 'pages').walkfiles('*.html'):
        page = TemplatePage(template)
        rendered_page = page.render_html()
        if not page.output_path.exists():
            page.output_path.makedirs()
        with open(page.output_path/page.output_file_name, mode='wb', encoding='UTF-8') as file:
            file.write(rendered_page)
            logger.info("Output '%s'." % file.name)

    # Load markdown input posts
    logger.debug("Loading drafts.")
    all_posts = LocalLoader.load_all(input=settings.DRAFT_DIR)

    logger.debug("Loading published.")
    all_posts.extend(LocalLoader.load_all(input=settings.PUBLISHED_DIR))

    logger.debug("Drafts: %d, Published: %d" % (len(all_posts.drafts), len(all_posts.published)))

    all_posts = PostCollection(sorted(all_posts.published, reverse=True, key=lambda post: post.timestamp))

    # Generate individual post pages
    for post in all_posts:
        rendered_post = post.render_html()
        if not post.output_path.exists():
            post.output_path.makedirs()
        with open(post.output_path / post.output_file_name, mode='wb', encoding='UTF-8') as file:
            logger.info("Output '%s'." % file.name)
            file.write(rendered_post)

    # Generate rollup pages
    num_posts = len(all_posts)
    num_slices = (num_posts / 5) if num_posts % 5 == 0 else (num_posts / 5) + 1

    slice_num = 0
    for posts in all_posts.paginate():
        slice_num += 1
        has_next = slice_num < num_slices
        has_previous = 1 < slice_num <= num_slices
        rendered_page = posts.render_listpage_html(slice_num, has_next, has_previous)
        if not posts.output_path(slice_num).exists():
            posts.output_path(slice_num).dirname().makedirs()
        with open(posts.output_path(slice_num), mode='wb', encoding='UTF-8') as file:
            file.write(rendered_page)
            logger.info("Output '%s'." % file.name)

        # Copy first rollup page to root of site - it's the homepage.
        if slice_num == 1:
            path.copyfile(posts.output_path(slice_num), settings.OUTPUT_DIR / 'index.html')
            logger.info("Output '%s'." % (settings.OUTPUT_DIR / 'index.html'))

    # Generate archive page
    archive_output_path = settings.OUTPUT_DIR / 'archives/index.html'
    if not archive_output_path.exists():
        archive_output_path.dirname().makedirs()

    rendered_archive = all_posts.render_archive_html()

    with open(settings.OUTPUT_DIR / 'archives/index.html', mode='wb', encoding='UTF-8') as file:
        file.write(rendered_archive)
        logger.info("Output '%s'." % file.name)

    # Copy static content to output dir
    s = settings.ENGINEER_STATIC_DIR.abspath()
    t = (settings.OUTPUT_DIR / settings.ENGINEER_STATIC_DIR.basename()).abspath()
    sync_folders(s, t)
    logger.info("Copied static files to '%s'." % t)

    # Copy theme static content to output dir
    s = ThemeManager.current_theme().static_root.abspath()
    t = (settings.OUTPUT_DIR / settings.ENGINEER_STATIC_DIR.basename() / 'theme').abspath()
    sync_folders(s, t)
    logger.info("Copied static files for theme to '%s'." % t)


def cmdline(args=sys.argv):
    parser = argparse.ArgumentParser(description="Engineer site builder.")

    top_group = parser.add_mutually_exclusive_group()
    top_group.add_argument('--build', '-b', dest='build', action='store_true', help="Build the site.")
    top_group.add_argument('--clean', '-c', dest='clean', action='store_true', help="Clean the output directory.")
    top_group.add_argument('--serve', '-s', dest='serve', action='store_true', help="Start the development server.")

    parser.add_argument('--no-cache', '-n', dest='disable_cache', action='store_true', help="Disable the post cache.")
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help="Display verbose output.")
    parser.add_argument('--settings', dest='settings_module', default='settings',
                        help="Specify a configuration file to use.")
    args = parser.parse_args()

    configure_settings(args.settings_module)
    settings.DISABLE_CACHE = args.disable_cache

    if args.verbose:
        import logging
        logger.setLevel(logging.DEBUG)

    if args.serve:
        from engineer.server import serve

        serve()
    elif args.clean:
        clean()
        exit()
    elif args.build:
        build()
        exit()
    else:
        parser.print_help()
        exit()
