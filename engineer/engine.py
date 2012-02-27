# coding=utf-8
import argparse
from datetime import datetime
import sys
from codecs import open
from path import path
from engineer.conf import settings
from engineer.loaders import LocalLoader
from engineer.models import PostCollection, TemplatePage
from engineer.themes import ThemeManager
from engineer.util import mirror_folder, ensure_exists
from engineer.log import logger

__author__ = 'tyler@tylerbutler.com'

def clean():
    try:
        settings.OUTPUT_DIR.rmtree()
        settings.OUTPUT_CACHE_DIR.rmtree()
    except WindowsError as we:
        if we.winerror not in (2, 3):
            logger.exception(we.message)
        else:
            logger.info("Couldn't find output directory: %s" % settings.OUTPUT_DIR)
    from engineer.post_cache import POST_CACHE

    POST_CACHE.delete()
    logger.info('Cleaned output directory: %s' % settings.OUTPUT_DIR)


def build():
    build_stats = {
        'template_pages': 0,
        'new_posts': 0,
        'cached_posts': 0,
        'rollups': 0,
        'tag_pages': 0,
        }

    settings.OUTPUT_CACHE_DIR.rmtree(ignore_errors=True)

    # Generate template pages
    template_page_source = (settings.TEMPLATE_DIR / 'pages').abspath()
    logger.info("Generating template pages from %s." % template_page_source)
    for template in template_page_source.walkfiles('*.html'):
        page = TemplatePage(template)
        rendered_page = page.render_html()
        ensure_exists(page.output_path)
        with open(page.output_path / page.output_file_name, mode='wb', encoding='UTF-8') as file:
            file.write(rendered_page)
            logger.debug("Output '%s'." % file.name)
            build_stats['template_pages'] += 1

    # Load markdown input posts
    logger.info("Loading posts from %s." % settings.POST_DIR)
    new_posts, cached_posts = LocalLoader.load_all(input=settings.POST_DIR)
    all_posts = PostCollection(new_posts + cached_posts)

    all_posts = PostCollection(sorted(all_posts.published, reverse=True, key=lambda post: post.timestamp))

    # Generate individual post pages
    for post in all_posts:
        rendered_post = post.render_html()
        ensure_exists(post.output_path)
        with open(post.output_path / post.output_file_name, mode='wb', encoding='UTF-8') as file:
            file.write(rendered_post)
            if post in new_posts:
                logger.info("Output new or modified post '%s'." % post.title)
                build_stats['new_posts'] += 1
            elif post in cached_posts:
                build_stats['cached_posts'] += 1

    # Generate rollup pages
    num_posts = len(all_posts)
    num_slices = (num_posts / settings.ROLLUP_PAGE_SIZE) if num_posts % settings.ROLLUP_PAGE_SIZE == 0\
    else (num_posts / settings.ROLLUP_PAGE_SIZE) + 1

    slice_num = 0
    for posts in all_posts.paginate():
        slice_num += 1
        has_next = slice_num < num_slices
        has_previous = 1 < slice_num <= num_slices
        rendered_page = posts.render_listpage_html(slice_num, has_next, has_previous)
        ensure_exists(posts.output_path(slice_num))
        with open(posts.output_path(slice_num), mode='wb', encoding='UTF-8') as file:
            file.write(rendered_page)
            logger.debug("Output '%s'." % file.name)
            build_stats['rollups'] += 1

        # Copy first rollup page to root of site - it's the homepage.
        if slice_num == 1:
            path.copyfile(posts.output_path(slice_num), settings.OUTPUT_CACHE_DIR / 'index.html')
            logger.debug("Output '%s'." % (settings.OUTPUT_CACHE_DIR / 'index.html'))

    # Generate archive page
    if num_posts > 0:
        archive_output_path = settings.OUTPUT_CACHE_DIR / 'archives/index.html'
        ensure_exists(archive_output_path)

        rendered_archive = all_posts.render_archive_html()

        with open(archive_output_path, mode='wb', encoding='UTF-8') as file:
            file.write(rendered_archive)
            logger.debug("Output '%s'." % file.name)

    # Generate tag pages
    if num_posts > 0:
        tags_output_path = settings.OUTPUT_CACHE_DIR / 'tag'
        for tag in all_posts.all_tags:
            rendered_tag_page = all_posts.render_tag_html(tag)
            tag_path = ensure_exists(tags_output_path / tag / 'index.html')
            with open(tag_path, mode='wb', encoding='UTF-8') as file:
                file.write(rendered_tag_page)
                build_stats['tag_pages'] += 1
                logger.debug("Output '%s'." % file.name)

    # Generate feeds
    feed_output_path = ensure_exists(settings.OUTPUT_CACHE_DIR / 'feeds/rss.xml')
    feed_content = settings.JINJA_ENV.get_template('core/rss.xml').render(
        post_list=all_posts[:settings.FEED_ITEM_LIMIT],
        build_date=datetime.now())
    with open(feed_output_path, mode='wb', encoding='UTF-8') as file:
        file.write(feed_content)
        logger.debug("Output '%s'." % file.name)

    # Copy static content to output dir
    s = settings.ENGINEER_STATIC_DIR.abspath()
    t = (settings.OUTPUT_CACHE_DIR / settings.ENGINEER_STATIC_DIR.basename()).abspath()
    mirror_folder(s, t)
    logger.debug("Copied static files to '%s'." % t)

    # Copy theme static content to output dir
    s = ThemeManager.current_theme().static_root.abspath()
    t = (settings.OUTPUT_CACHE_DIR / settings.ENGINEER_STATIC_DIR.basename() / 'theme').abspath()
    mirror_folder(s, t)
    logger.debug("Copied static files for theme to '%s'." % t)

    logger.info("Synchronizing output directory with output cache.")
    report = mirror_folder(settings.OUTPUT_CACHE_DIR, settings.OUTPUT_DIR)
    from pprint import pformat

    logger.debug(pformat(report))
    logger.info('')
    logger.info("Site: '%s' output to %s." % (settings.SITE_TITLE, settings.OUTPUT_DIR))
    logger.info("Posts: %s (%s new or updated)" % (
        (build_stats['new_posts'] + build_stats['cached_posts']), build_stats['new_posts']))
    logger.info("Post rollup pages: %s (%s posts per page)" % (build_stats['rollups'], settings.ROLLUP_PAGE_SIZE))
    logger.info("Template pages: %s" % build_stats['template_pages'])
    logger.info("Tag pages: %s" % build_stats['tag_pages'])
    logger.info("%s new items, %s modified items, and %s deleted items." % (len(report['new']),
                                                                            len(report['overwritten']),
                                                                            len(report['deleted'])))


def cmdline(args=sys.argv):
    # Common parameters
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('--no-cache', '-n', dest='disable_cache', action='store_true',
                               help="Disable the post cache.")
    common_parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help="Display verbose output.")
    common_parser.add_argument('--config', dest='config_file', default='config.yaml',
                               help="Specify a configuration file to use.")

    main_parser = argparse.ArgumentParser(
        description="Engineer site builder.",
        parents=[common_parser])

    top_group = main_parser.add_mutually_exclusive_group(required=True)
    top_group.add_argument('--build', '-b', dest='build',
                           action='store_true', help="Build the site.")
    top_group.add_argument('--serve', '-s', dest='serve',
                           action='store_true', help="Start the development server.")
    top_group.add_argument('--clean', '-c', dest='clean',
                           action='store_true', help="Clean the output directory.")

    args = main_parser.parse_args()

    settings.initialize_from_yaml(args.config_file)
    settings.DISABLE_CACHE = args.disable_cache

    if args.verbose:
        import logging

        logger.setLevel(logging.DEBUG)

    if args.serve:
        from engineer.server import serve

        serve()
    elif args.build:
        build()
        exit()
    elif args.clean:
        clean()
        exit()
    else:
        main_parser.print_help()
        exit()
