# coding=utf-8
import argparse
from datetime import datetime
import sys
import bottle
from codecs import open
from path import path
from engineer.conf import settings
from engineer import emma
from engineer.loaders import LocalLoader
from engineer.models import PostCollection, TemplatePage
from engineer.themes import ThemeManager
from engineer.util import mirror_folder, ensure_exists, slugify
from engineer.log import logger

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'tyler@tylerbutler.com'

def clean():
    try:
        settings.OUTPUT_DIR.rmtree()
        settings.OUTPUT_CACHE_DIR.rmtree()
    except OSError as we:
        if hasattr(we, 'winerror') and we.winerror not in (2, 3):
            logger.exception(we.message)
        else:
            logger.info(
                "Couldn't find output directory: %s" % settings.OUTPUT_DIR)
    from engineer.post_cache import POST_CACHE

    POST_CACHE.delete()
    logger.info('Cleaned output directory: %s' % settings.OUTPUT_DIR)


def build(args=None):
    if args and args.clean:
        clean()

    build_stats = {
        'time_run': datetime.now(),
        'counts': {
            'template_pages': 0,
            'new_posts': 0,
            'cached_posts': 0,
            'rollups': 0,
            'tag_pages': 0,
            },
        'files': {},
        }

    # Remove the output cache (not the post cache or the Jinja cache)
    # since we're rebuilding the site
    settings.OUTPUT_CACHE_DIR.rmtree(ignore_errors=True)

    # Generate template pages
    template_page_source = (settings.TEMPLATE_DIR / 'pages').abspath()
    if template_page_source.exists():
        logger.info("Generating template pages from %s." % template_page_source)
        for template in template_page_source.walkfiles('*.html'):
            page = TemplatePage(template)
            rendered_page = page.render_html()
            ensure_exists(page.output_path)
            with open(page.output_path / page.output_file_name, mode='wb',
                      encoding='UTF-8') as file:
                file.write(rendered_page)
                logger.debug("Output '%s'." % file.name)
                build_stats['counts']['template_pages'] += 1

    # Load markdown input posts
    logger.info("Loading posts from %s." % settings.POST_DIR)
    new_posts, cached_posts = LocalLoader.load_all(input=settings.POST_DIR)
    all_posts = PostCollection(new_posts + cached_posts)

    if settings.PUBLISH_DRAFTS:
        to_publish = all_posts
    else:
        to_publish = PostCollection(all_posts.published)

    all_posts = PostCollection(
        sorted(to_publish, reverse=True, key=lambda post: post.timestamp))

    # Generate individual post pages
    for post in all_posts:
        rendered_post = post.render_html()
        ensure_exists(post.output_path)
        with open(post.output_path / post.output_file_name, mode='wb',
                  encoding='UTF-8') as file:
            file.write(rendered_post)
            if post in new_posts:
                logger.info("Output new or modified post '%s'." % post.title)
                build_stats['counts']['new_posts'] += 1
            elif post in cached_posts:
                build_stats['counts']['cached_posts'] += 1

    # Generate rollup pages
    num_posts = len(all_posts)
    num_slices = (
        num_posts / settings.ROLLUP_PAGE_SIZE) if num_posts % settings.ROLLUP_PAGE_SIZE == 0\
    else (num_posts / settings.ROLLUP_PAGE_SIZE) + 1

    slice_num = 0
    for posts in all_posts.paginate():
        slice_num += 1
        has_next = slice_num < num_slices
        has_previous = 1 < slice_num <= num_slices
        rendered_page = posts.render_listpage_html(slice_num, has_next,
                                                   has_previous)
        ensure_exists(posts.output_path(slice_num))
        with open(posts.output_path(slice_num), mode='wb',
                  encoding='UTF-8') as file:
            file.write(rendered_page)
            logger.debug("Output '%s'." % file.name)
            build_stats['counts']['rollups'] += 1

        # Copy first rollup page to root of site - it's the homepage.
        if slice_num == 1:
            path.copyfile(posts.output_path(slice_num),
                          settings.OUTPUT_CACHE_DIR / 'index.html')
            logger.debug(
                "Output '%s'." % (settings.OUTPUT_CACHE_DIR / 'index.html'))

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
            tag_path = ensure_exists(tags_output_path / slugify(tag) / 'index.html')
            with open(tag_path, mode='wb', encoding='UTF-8') as file:
                file.write(rendered_tag_page)
                build_stats['counts']['tag_pages'] += 1
                logger.debug("Output '%s'." % file.name)

    # Generate feeds
    feed_output_path = ensure_exists(
        settings.OUTPUT_CACHE_DIR / 'feeds/rss.xml')
    feed_content = settings.JINJA_ENV.get_template('core/rss.xml').render(
        post_list=all_posts[:settings.FEED_ITEM_LIMIT],
        build_date=datetime.now())
    with open(feed_output_path, mode='wb', encoding='UTF-8') as file:
        file.write(feed_content)
        logger.debug("Output '%s'." % file.name)

    # Copy static content to output dir
    s = settings.ENGINEER_STATIC_DIR.abspath()
    t = ( settings.OUTPUT_CACHE_DIR /
          settings.ENGINEER_STATIC_DIR.basename()).abspath()
    mirror_folder(s, t)
    logger.debug("Copied static files to '%s'." % t)

    # Copy theme static content to output dir
    s = ThemeManager.current_theme().static_root.abspath()
    t = (
        settings.OUTPUT_CACHE_DIR / settings.ENGINEER_STATIC_DIR.basename() / 'theme').abspath()
    mirror_folder(s, t)
    logger.debug("Copied static files for theme to '%s'." % t)

    logger.info("Synchronizing output directory with output cache.")
    build_stats['files'] = mirror_folder(settings.OUTPUT_CACHE_DIR, settings.OUTPUT_DIR)
    from pprint import pformat

    logger.debug("Folder mirroring report: %s" % pformat(build_stats['files']))
    logger.info('')
    logger.info(
        "Site: '%s' output to %s." % (settings.SITE_TITLE, settings.OUTPUT_DIR))
    logger.info("Posts: %s (%s new or updated)" % (
        (build_stats['counts']['new_posts'] + build_stats['counts']['cached_posts']),
        build_stats['counts']['new_posts']))
    logger.info("Post rollup pages: %s (%s posts per page)" % (
        build_stats['counts']['rollups'], settings.ROLLUP_PAGE_SIZE))
    logger.info("Template pages: %s" % build_stats['counts']['template_pages'])
    logger.info("Tag pages: %s" % build_stats['counts']['tag_pages'])
    logger.info("%s new items, %s modified items, and %s deleted items." % (
        len(build_stats['files']['new']),
        len(build_stats['files']['overwritten']),
        len(build_stats['files']['deleted'])))
    with open(settings.BUILD_STATS_FILE, mode='wb') as file:
        pickle.dump(build_stats, file)
    return build_stats


def serve(args):
    @bottle.route('/<filepath:path>')
    def serve_static(filepath):
        response = bottle.static_file(filepath, root=settings.OUTPUT_DIR)
        if type(response) is bottle.HTTPError:
            return bottle.static_file(path(filepath) / 'index.html',
                                      root=settings.OUTPUT_DIR)
        else:
            return response

    @bottle.route('/manage')
    def manage():
        return 'Management Page'

    bottle.debug(True)
    bottle.run(host='localhost', port=8000, reloader=True)


def start_emma(args):
    try:
        if args.prefix:
            emma._prefix = args.prefix
        if args.generate:
            emma.generate_secret()
            logger.info("New Emma URL: %s" % emma.get_secret_path(True))
        elif args.url:
            logger.info("Current Emma URL: %s" % emma.get_secret_path(True))
        elif args.run:
            emma.Emma().run(port=args.port)
    except emma.NoSecretException:
        logger.warning("You haven't created a secret for Emma yet. Try 'engineer emma --generate' first.")
    exit()


def get_argparser():
    # Common parameters
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('-v', '--verbose',
                               dest='verbose',
                               action='store_true',
                               help="Display verbose output.")
    common_parser.add_argument('--config', '--settings',
                               dest='config_file',
                               default='config.yaml',
                               help="Specify a configuration file to use.")

    main_parser = argparse.ArgumentParser(
        description="Engineer static site builder.")
    subparsers = main_parser.add_subparsers(title="subcommands")

    parser_build = subparsers.add_parser('build',
                                         help="Build the site.",
                                         parents=[common_parser])
    parser_build.add_argument('-c', '--clean',
                              dest='clean',
                              action='store_true',
                              help="Clean the output directory and clear all the caches before building.")
    parser_build.set_defaults(func=build)

    parser_serve = subparsers.add_parser('serve',
                                         help="Start the development server.",
                                         parents=[common_parser])
    parser_serve.set_defaults(func=serve)

    parser_emma = subparsers.add_parser('emma',
                                        help="Start Emma, the built-in management server.",
                                        parents=[common_parser])
    parser_emma.add_argument('-p', '--port',
                             type=int,
                             default=8080,
                             dest='port',
                             help="The port Emma should listen on.")
    parser_emma.add_argument('--prefix',
                             type=str,
                             dest='prefix',
                             help="The prefix path the Emma site will be rooted at.")
    emma_options = parser_emma.add_mutually_exclusive_group(required=True)
    emma_options.add_argument('-r', '--run',
                              dest='run',
                              action='store_true',
                              help="Run Emma.")
    emma_options.add_argument('-g', '--generate',
                              dest='generate',
                              action='store_true',
                              help="Generate a new secret location for Emma.")
    emma_options.add_argument('-u', '--url',
                              dest='url',
                              action='store_true',
                              help="Get Emma's current URL.")
    parser_emma.set_defaults(func=start_emma)
    return main_parser


def cmdline(args=sys.argv):
    args = get_argparser().parse_args(args[1:])
    settings.initialize_from_yaml(args.config_file)

    if args.verbose:
        import logging

        logger.setLevel(logging.DEBUG)

    args.func(args)
    exit()
