# coding=utf-8
import argparse
import gzip
import logging
import sys
import time
import times
from codecs import open
from path import path
from engineer.exceptions import ThemeNotFoundException
from engineer.filters import naturaltime
from engineer.log import get_console_handler, bootstrap
from engineer.plugins import CommandPlugin, load_plugins
from engineer.util import relpath, compress
from engineer import version

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

def clean(args=None):
    from engineer.conf import settings

    logger = logging.getLogger('engineer.engine.clean')
    try:
        settings.OUTPUT_DIR.rmtree()
        settings.OUTPUT_CACHE_DIR.rmtree()
        settings.CACHE_DIR.rmtree()
    except OSError as we:
        if hasattr(we, 'winerror') and we.winerror not in (2, 3):
            logger.exception(we.message)
        else:
            logger.warning("Couldn't find output directory: %s" % settings.OUTPUT_DIR)

    logger.console('Cleaned output directory: %s' % settings.OUTPUT_DIR)


def build(args=None):
    """Builds an Engineer site using the settings specified in *args*."""
    from engineer.conf import settings
    from engineer.loaders import LocalLoader
    from engineer.log import get_file_handler
    from engineer.models import PostCollection, TemplatePage
    from engineer.themes import ThemeManager
    from engineer.util import mirror_folder, ensure_exists, slugify

    if args and args.clean:
        clean()

    settings.create_required_directories()

    logger = logging.getLogger('engineer.engine.build')
    logger.parent.addHandler(get_file_handler(settings.LOG_FILE))

    logger.debug("Starting build using configuration file %s." % settings.SETTINGS_FILE)

    build_stats = {
        'time_run': times.now(),
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

    # Copy static content to output dir
    logger.debug("Copying static files to output cache.")
    s = (settings.ENGINEER.STATIC_DIR / 'engineer').abspath()
    t = settings.OUTPUT_STATIC_DIR / 'engineer'
    mirror_folder(s, t, recurse=False) # Copy only the files in this folder - don't recurse

    theme = ThemeManager.current_theme()
    # Copy Foundation files if used
    if theme.use_foundation:
        s = settings.ENGINEER.LIB_DIR / 'foundation'
        t = ensure_exists(settings.OUTPUT_STATIC_DIR / 'engineer/lib/foundation')
        mirror_folder(s, t)
        logger.debug("Copied Foundation library files.")

    # Copy LESS js file if needed
    if theme.use_lesscss and not settings.PREPROCESS_LESS:
        s = settings.ENGINEER.LIB_DIR / 'less-1.3.1.min.js'
        t = ensure_exists(settings.OUTPUT_STATIC_DIR / 'engineer/lib/')
        s.copy(t)
        logger.debug("Copied LESS CSS files.")

    # Copy jQuery files if needed
    if theme.use_jquery or theme.use_tweet:
        s = settings.ENGINEER.LIB_DIR / 'jquery-1.7.1.min.js'
        t = ensure_exists(settings.OUTPUT_STATIC_DIR / 'engineer/lib/')
        s.copy(t)
        logger.debug("Copied jQuery files.")

    # Copy Tweet files if needed
    if theme.use_tweet:
        s = settings.ENGINEER.LIB_DIR / 'tweet'
        t = ensure_exists(settings.OUTPUT_STATIC_DIR / 'engineer/lib/tweet')
        mirror_folder(s, t)
        logger.debug("Copied Tweet files.")

    # Copy modernizr files if needed
    if theme.use_modernizr:
        s = settings.ENGINEER.LIB_DIR / 'modernizr-2.5.3.min.js'
        t = ensure_exists(settings.OUTPUT_STATIC_DIR / 'engineer/lib/')
        s.copy(t)
        logger.debug("Copied Modernizr files.")

    logger.debug("Copied static files to %s." % relpath(t))

    # Copy 'raw' content to output cache - first pass
    # This first pass ensures that any static content - JS/LESS/CSS - that
    # is needed by site-specific pages (like template pages) is available
    # during the build
    if settings.CONTENT_DIR.exists():
        mirror_folder(settings.CONTENT_DIR,
                      settings.OUTPUT_CACHE_DIR,
                      delete_orphans=False)

    # Copy theme static content to output dir
    logger.debug("Copying theme static files to output cache.")
    try:
        s = theme.static_root.abspath()
    except ThemeNotFoundException as e:
        logger.critical(e.message)
        exit()
    t = (settings.OUTPUT_STATIC_DIR / 'theme').abspath()
    mirror_folder(s, t)
    logger.debug("Copied static files for theme to %s." % relpath(t))

    # Copy any theme additional content to output dir if needed
    if theme.content_mappings:
        logger.debug("Copying additional theme content to output cache.")
        for s, t in theme.content_mappings.iteritems():
            t = settings.OUTPUT_STATIC_DIR / 'theme' / t
            if s.isdir():
                mirror_folder(s, t)
            else:
                s.copy(ensure_exists(t))
            logger.debug("Copied additional files for theme to %s." % relpath(t))

    # Load markdown input posts
    logger.info("Loading posts...")
    new_posts, cached_posts = LocalLoader.load_all(input=settings.POST_DIR)
    all_posts = PostCollection(new_posts + cached_posts)

    to_publish = PostCollection(all_posts.published)
    if settings.PUBLISH_DRAFTS:
        to_publish.extend(all_posts.drafts)
    if settings.PUBLISH_PENDING:
        to_publish.extend(all_posts.pending)
    if settings.PUBLISH_REVIEW:
        to_publish.extend(all_posts.review)

    if not settings.PUBLISH_PENDING and len(all_posts.pending) > 0:
        logger.warning("This site contains the following pending posts:")
        for post in all_posts.pending:
            logger.warning("\t'%s' - publish time: %s, %s." % (post.title,
                                                               naturaltime(post.timestamp),
                                                               post.timestamp_local))
        logger.warning("These posts won't be published until you build the site again after their publish time.")

    all_posts = PostCollection(
        sorted(to_publish, reverse=True, key=lambda post: post.timestamp))

    # Generate template pages
    if settings.TEMPLATE_PAGE_DIR.exists():
        logger.info("Generating template pages from %s." % settings.TEMPLATE_PAGE_DIR)
        template_pages = []
        for template in settings.TEMPLATE_PAGE_DIR.walkfiles('*.html'):
            # We create all the TemplatePage objects first so we have all of the URLs to them in the template
            # environment. Without this step, template pages might have broken links if they link to a page that is
            # loaded after them, since the URL to the not-yet-loaded page will be missing.
            template_pages.append(TemplatePage(template))
        for page in template_pages:
            rendered_page = page.render_html(all_posts)
            ensure_exists(page.output_path)
            with open(page.output_path / page.output_file_name, mode='wb',
                      encoding='UTF-8') as file:
                file.write(rendered_page)
                logger.debug("Output template page %s." % relpath(file.name))
                build_stats['counts']['template_pages'] += 1
        logger.info("Generated %s template pages." % build_stats['counts']['template_pages'])

    # Generate individual post pages
    for post in all_posts:
        rendered_post = post.render_html(all_posts)
        ensure_exists(post.output_path)
        with open(post.output_path, mode='wb',
                  encoding='UTF-8') as file:
            file.write(rendered_post)
            if post in new_posts:
                logger.console("Output new or modified post '%s'." % post.title)
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
            logger.debug("Output rollup page %s." % relpath(file.name))
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

        rendered_archive = all_posts.render_archive_html(all_posts)

        with open(archive_output_path, mode='wb', encoding='UTF-8') as file:
            file.write(rendered_archive)
            logger.debug("Output %s." % relpath(file.name))

    # Generate tag pages
    if num_posts > 0:
        tags_output_path = settings.OUTPUT_CACHE_DIR / 'tag'
        for tag in all_posts.all_tags:
            rendered_tag_page = all_posts.render_tag_html(tag, all_posts)
            tag_path = ensure_exists(
                tags_output_path / slugify(tag) / 'index.html')
            with open(tag_path, mode='wb', encoding='UTF-8') as file:
                file.write(rendered_tag_page)
                build_stats['counts']['tag_pages'] += 1
                logger.debug("Output %s." % relpath(file.name))

    # Generate feeds
    feed_output_path = ensure_exists(settings.OUTPUT_CACHE_DIR / 'feeds/rss.xml')
    feed_content = settings.JINJA_ENV.get_or_select_template(['rss.xml',
                                                              'theme/rss.xml',
                                                              'core/rss.xml']).render(
        post_list=all_posts[:settings.FEED_ITEM_LIMIT],
        build_date=all_posts[0].timestamp)
    with open(feed_output_path, mode='wb', encoding='UTF-8') as file:
        file.write(feed_content)
        logger.debug("Output %s." % relpath(file.name))

    # Generate sitemap
    sitemap_output_path = ensure_exists(settings.OUTPUT_CACHE_DIR / 'sitemap.xml.gz')
    sitemap_content = settings.JINJA_ENV.get_or_select_template(['sitemap.xml',
                                                                 'theme/sitemap.xml',
                                                                 'core/sitemap.xml']).render(post_list=all_posts)
    with gzip.open(sitemap_output_path, mode='wb') as file:
        file.write(sitemap_content)
        logger.debug("Output %s." % relpath(file.name))

    # Copy 'raw' content to output cache - second/final pass
    if settings.CONTENT_DIR.exists():
        mirror_folder(settings.CONTENT_DIR,
                      settings.OUTPUT_CACHE_DIR,
                      delete_orphans=False)

    # Compress all files marked for compression
    for file, compression_type in settings.COMPRESS_FILE_LIST:
        if file not in settings.COMPRESSION_CACHE:
            with open(file, mode='rb') as input:
                output = compress(input.read(), compression_type)
                logger.debug("Compressed %s." % relpath(file))
            settings.COMPRESSION_CACHE[file] = output
        else:
            logger.debug("Found pre-compressed file in cache: %s." % relpath(file))
            output = settings.COMPRESSION_CACHE[file]
        with open(file, mode='wb') as f:
            f.write(output)

    # Remove LESS files if LESS preprocessing is being done
    if settings.PREPROCESS_LESS:
        logger.debug("Deleting LESS files since PREPROCESS_LESS is True.")
        for f in settings.OUTPUT_STATIC_DIR.walkfiles(pattern="*.less"):
            logger.debug("Deleting file: %s." % relpath(f))
            f.remove_p()

    logger.debug("Synchronizing output directory with output cache.")
    build_stats['files'] = mirror_folder(settings.OUTPUT_CACHE_DIR,
                                         settings.OUTPUT_DIR)
    from pprint import pformat

    logger.debug("Folder mirroring report: %s" % pformat(build_stats['files']))
    logger.console('')
    logger.console("Site: '%s' output to %s." % (settings.SITE_TITLE, settings.OUTPUT_DIR))
    logger.console("Posts: %s (%s new or updated)" % (
        (build_stats['counts']['new_posts'] + build_stats['counts'][
                                              'cached_posts']),
        build_stats['counts']['new_posts']))
    logger.console("Post rollup pages: %s (%s posts per page)" % (
        build_stats['counts']['rollups'], settings.ROLLUP_PAGE_SIZE))
    logger.console("Template pages: %s" % build_stats['counts']['template_pages'])
    logger.console("Tag pages: %s" % build_stats['counts']['tag_pages'])
    logger.console("%s new items, %s modified items, and %s deleted items." % (
        len(build_stats['files']['new']),
        len(build_stats['files']['overwritten']),
        len(build_stats['files']['deleted'])))
    logger.console('')
    logger.console("Full build log at %s." % settings.LOG_FILE)

    with open(settings.BUILD_STATS_FILE, mode='wb') as file:
        pickle.dump(build_stats, file)
    settings.CACHE.close()
    return build_stats


def serve(args):
    import bottle
    from engineer.conf import settings
    from engineer import emma

    logger = logging.getLogger(__name__)

    if not settings.OUTPUT_DIR.exists():
        logger.warning(
            "Output directory doesn't exist - did you forget to run 'engineer build'?")
        exit()

    debug_server = bottle.Bottle()
    debug_server.mount('/_emma', emma.Emma().app)

    @debug_server.route('/')
    @debug_server.route('/<filepath:path>')
    def serve_static(filepath='index.html'):
        if settings.HOME_URL != '/':
            # if HOME_URL is not root, we need to adjust the paths
            if filepath.startswith(settings.HOME_URL[1:]):
                filepath = filepath[len(settings.HOME_URL) - 1:]
            else:
                return bottle.HTTPResponse(status=404)
        response = bottle.static_file(filepath, root=settings.OUTPUT_DIR)
        if type(response) is bottle.HTTPError:
            return bottle.static_file(path(filepath) / 'index.html',
                                      root=settings.OUTPUT_DIR)
        else:
            return response

    bottle.debug(True)
    bottle.run(app=debug_server, host='0.0.0.0', port=args.port, reloader=True)


def start_emma(args):
    from engineer import emma

    logger = logging.getLogger('engineer.engine.start_emma')

    em = emma.EmmaStandalone()
    try:
        if args.prefix:
            em.emma_instance.prefix = args.prefix
        if args.generate:
            em.emma_instance.generate_secret()
            logger.console(
                "New Emma URL: %s" % em.emma_instance.get_secret_path(True))
        elif args.url:
            logger.console(
                "Current Emma URL: %s" % em.emma_instance.get_secret_path(True))
        elif args.run:
            em.run(port=args.port)
    except emma.NoSecretException:
        logger.warning(
            "You haven't created a secret for Emma yet. Try 'engineer emma --generate' first.")
    exit()


def init(args):
    from engineer import __file__ as package_file, version

    logger = logging.getLogger('engineer.engine.init')

    sample_site_path = path(package_file).dirname() / 'sample_site'
    target = path.getcwd()
    if target.listdir() and not args.force:
        logger.warning("Target folder %s is not empty." % target)
        exit()
    elif args.force:
        logger.info("Deleting folder contents.")
        try:
            for item in target.dirs():
                item.rmtree()
            for item in target.files():
                item.remove()
        except Exception as e:
            logger.error("Couldn't delete folder contents - aborting.")
            logger.exception(e)
            exit()

    from engineer.util import mirror_folder, ensure_exists

    if args.no_sample:
        ensure_exists(target / 'posts')
        (sample_site_path / 'config.yaml').copyfile(target / 'config.yaml')
    else:
        mirror_folder(sample_site_path, target)
    logger.console("Initialization complete.")
    exit()


def get_argparser():
    # Common parameters
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('-v', '--verbose',
                               dest='verbose',
                               action='count',
                               help="Display verbose output.")
    common_parser.add_argument('-s', '--config', '--settings',
                               dest='config_file',
                               help="Specify a configuration file to use.")

    desc = "Engineer static site builder. [v%s, %s %s]" % (version, version.date, time.strftime('%X', version.time))
    main_parser = argparse.ArgumentParser(description=desc)
    subparsers = main_parser.add_subparsers(title="subcommands",
                                            dest='parser_name')

    parser_build = subparsers.add_parser('build',
                                         help="Build the site.",
                                         parents=[common_parser])
    parser_build.add_argument('-c', '--clean',
                              dest='clean',
                              action='store_true',
                              help="Clean the output directory and clear all the caches before building.")
    parser_build.set_defaults(func=build)

    parser_clean = subparsers.add_parser('clean',
                                         help="Clean the output directory and clear all caches.",
                                         parents=[common_parser])
    parser_clean.set_defaults(func=clean)

    parser_serve = subparsers.add_parser('serve',
                                         help="Start the development server.",
                                         parents=[common_parser])
    parser_serve.add_argument('-p', '--port',
                              type=int,
                              default=8000,
                              dest='port',
                              help="The port the development server should listen on.")
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
    parser_init = subparsers.add_parser('init',
                                        help="Initialize the current directory as an engineer site.",
                                        parents=[common_parser])
    parser_init.add_argument('--no-sample',
                             dest='no_sample',
                             action='store_true',
                             help="Do not include sample content.")
    parser_init.add_argument('--force', '-f',
                             dest='force',
                             action='store_true',
                             help="Delete target folder contents. Use with caution!")
    parser_init.set_defaults(func=init)

    for cmd_plugin in CommandPlugin.plugins:
        if cmd_plugin.active():
            cmd_plugin.add_command(subparsers, main_parser, common_parser)

    return main_parser


def cmdline(args=sys.argv):
    # bootstrap logging
    bootstrap()

    # Load all plugins
    load_plugins()

    args = get_argparser().parse_args(args[1:])
    skip_settings = ('init',)

    logger = logging.getLogger('engineer')
    if args.verbose >= 2:
        logger.removeHandler(get_console_handler(logging.WARNING))
        logger.addHandler(get_console_handler(logging.DEBUG))
    elif args.verbose == 1:
        logger.removeHandler(get_console_handler(logging.WARNING))
        logger.addHandler(get_console_handler(logging.INFO))
    else:
        pass # WARNING level is added by default in bootstrap method

    if args.parser_name in skip_settings:
        pass
    else: # try loading settings
        try:
            from engineer.conf import settings

            if args.config_file is None:
                default_settings_file = path.getcwd() / 'config.yaml'
                logger.info("No '--settings' parameter specified, defaulting to %s." % default_settings_file)
                settings.reload(default_settings_file)
            else:
                settings.reload(settings_file=args.config_file)
        except Exception as e:
            logger.error(e.message)
            exit()

    args.func(args)
    exit()
