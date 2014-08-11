# coding=utf-8
from __future__ import absolute_import

import filecmp
import gzip
import os
from codecs import open

from path import path
from feedgenerator import Rss201rev2Feed, Atom1Feed
import times

from engineer.commands.core import ArgParseCommand
from engineer.util import mirror_folder, ensure_exists, slugify, relpath, compress, has_files, diff_dir


try:
    # noinspection PyPep8Naming
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


# noinspection PyShadowingBuiltins
class BuildCommand(ArgParseCommand):
    name = 'build'
    help = 'Build the site.'

    def add_arguments(self):
        self.parser.add_argument('-c', '--clean',
                                 dest='clean',
                                 action='store_true',
                                 help="Clean the output directory and clear all the caches before building.")
        self.parser.set_defaults(handle=self.build)

    # noinspection PyShadowingBuiltins
    def build(self, args=None):
        """Builds an Engineer site using the settings specified in *args*."""

        from engineer.conf import settings
        from engineer.filters import naturaltime
        from engineer.loaders import LocalLoader
        from engineer.log import get_file_handler
        from engineer.models import PostCollection, TemplatePage
        from engineer.themes import ThemeManager

        if args and args.clean:
            clean = CleanCommand(None)
            clean.clean()

        settings.create_required_directories()

        logger = self.get_logger()
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

        theme = ThemeManager.current_theme()
        engineer_lib = (settings.OUTPUT_STATIC_DIR / 'engineer/lib/').abspath()
        ensure_exists(engineer_lib)
        # Copy Foundation files if used
        if theme.use_foundation:
            s = settings.ENGINEER.LIB_DIR / settings.ENGINEER.FOUNDATION_CSS
            t = ensure_exists(engineer_lib / settings.ENGINEER.FOUNDATION_CSS)
            mirror_folder(s, t)
            logger.debug("Copied Foundation library files.")

        # Copy LESS js file if needed
        if theme.use_lesscss and not settings.PREPROCESS_LESS:
            s = settings.ENGINEER.LIB_DIR / settings.ENGINEER.LESS_JS
            s.copy(engineer_lib)
            logger.debug("Copied LESS CSS files.")

        # Copy jQuery files if needed
        if theme.use_jquery:
            s = settings.ENGINEER.LIB_DIR / settings.ENGINEER.JQUERY
            s.copy(engineer_lib)
            logger.debug("Copied jQuery files.")

        # Copy modernizr files if needed
        if theme.use_modernizr:
            s = settings.ENGINEER.LIB_DIR / settings.ENGINEER.MODERNIZR
            s.copy(engineer_lib)
            logger.debug("Copied Modernizr files.")

        # Copy normalize.css if needed
        if theme.use_normalize_css:
            s = settings.ENGINEER.LIB_DIR / settings.ENGINEER.NORMALIZE_CSS
            s.copy(engineer_lib)
            logger.debug("Copied normalize.css.")

        # Copy 'raw' content to output cache - first pass
        # This first pass ensures that any static content - JS/LESS/CSS - that
        # is needed by site-specific pages (like template pages) is available
        # during the build
        if settings.CONTENT_DIR.exists():
            mirror_folder(settings.CONTENT_DIR,
                          settings.OUTPUT_CACHE_DIR,
                          delete_orphans=False)

        # Copy theme static content to output dir
        theme_output_dir = settings.OUTPUT_STATIC_DIR / 'theme'
        logger.debug("Copying theme static files to output cache.")
        theme.copy_content(theme_output_dir)
        logger.debug("Copied static files for theme to %s." % relpath(theme_output_dir))

        # Copy any theme additional content to output dir if needed
        if theme.content_mappings:
            logger.debug("Copying additional theme content to output cache.")
            theme.copy_related_content(theme_output_dir)
            logger.debug("Copied additional files for theme to %s." % relpath(theme_output_dir))

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
            sorted(to_publish, reverse=True, key=lambda p: p.timestamp))

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
                          encoding='UTF-8') as the_file:
                    the_file.write(rendered_page)
                    logger.info("Output template page %s." % relpath(the_file.name))
                    build_stats['counts']['template_pages'] += 1
            logger.info("Generated %s template pages." % build_stats['counts']['template_pages'])

        # Generate individual post pages
        for post in all_posts:
            rendered_post = post.render_html(all_posts)
            ensure_exists(post.output_path)
            with open(post.output_path, mode='wb',
                      encoding='UTF-8') as the_file:
                the_file.write(rendered_post)
                if post in new_posts:
                    logger.console("Output new or modified post '%s'." % post.title)
                    build_stats['counts']['new_posts'] += 1
                elif post in cached_posts:
                    build_stats['counts']['cached_posts'] += 1

        # Generate rollup pages
        num_posts = len(all_posts)
        num_slices = (
            num_posts / settings.ROLLUP_PAGE_SIZE) if num_posts % settings.ROLLUP_PAGE_SIZE == 0 \
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
                      encoding='UTF-8') as the_file:
                the_file.write(rendered_page)
                logger.debug("Output rollup page %s." % relpath(the_file.name))
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

            with open(archive_output_path, mode='wb', encoding='UTF-8') as the_file:
                the_file.write(rendered_archive)
                logger.debug("Output %s." % relpath(the_file.name))

        # Generate tag pages
        if num_posts > 0:
            tags_output_path = settings.OUTPUT_CACHE_DIR / 'tag'
            for tag in all_posts.all_tags:
                rendered_tag_page = all_posts.render_tag_html(tag, all_posts)
                tag_path = ensure_exists(
                    tags_output_path / slugify(tag) / 'index.html')
                with open(tag_path, mode='wb', encoding='UTF-8') as the_file:
                    the_file.write(rendered_tag_page)
                    build_stats['counts']['tag_pages'] += 1
                    logger.debug("Output %s." % relpath(the_file.name))

        # Generate feeds
        rss_feed_output_path = ensure_exists(settings.OUTPUT_CACHE_DIR / 'feeds/rss.xml')
        atom_feed_output_path = ensure_exists(settings.OUTPUT_CACHE_DIR / 'feeds/atom.xml')
        rss_feed = Rss201rev2Feed(
            title=settings.FEED_TITLE,
            link=settings.SITE_URL,
            description=settings.FEED_DESCRIPTION,
            feed_url=settings.FEED_URL
        )

        atom_feed = Atom1Feed(
            title=settings.FEED_TITLE,
            link=settings.SITE_URL,
            description=settings.FEED_DESCRIPTION,
            feed_url=settings.FEED_URL
        )

        for feed in (rss_feed, atom_feed):
            for post in all_posts[:settings.FEED_ITEM_LIMIT]:
                title = settings.JINJA_ENV.get_template('core/feeds/title.jinja2').render(post=post)
                link = settings.JINJA_ENV.get_template('core/feeds/link.jinja2').render(post=post)
                content = settings.JINJA_ENV.get_template('core/feeds/content.jinja2').render(post=post)
                feed.add_item(
                    title=title,
                    link=link,
                    description=content,
                    pubdate=post.timestamp,
                    unique_id=post.absolute_url)

        with open(rss_feed_output_path, mode='wb') as the_file:
            rss_feed.write(the_file, 'UTF-8')
            logger.debug("Output %s." % relpath(the_file.name))

        with open(atom_feed_output_path, mode='wb') as the_file:
            atom_feed.write(the_file, 'UTF-8')
            logger.debug("Output %s." % relpath(the_file.name))

        # Generate sitemap
        sitemap_file_name = 'sitemap.xml.gz'
        sitemap_output_path = ensure_exists(settings.OUTPUT_CACHE_DIR / sitemap_file_name)
        sitemap_content = settings.JINJA_ENV.get_or_select_template(['sitemap.xml',
                                                                     'theme/sitemap.xml',
                                                                     'core/sitemap.xml']).render(post_list=all_posts)
        with gzip.open(sitemap_output_path, mode='wb') as the_file:
            the_file.write(sitemap_content)
            logger.debug("Output %s." % relpath(the_file.name))

        # Copy 'raw' content to output cache - second/final pass
        if settings.CONTENT_DIR.exists():
            mirror_folder(settings.CONTENT_DIR,
                          settings.OUTPUT_CACHE_DIR,
                          delete_orphans=False)

        # Compress all files marked for compression
        for the_file, compression_type in settings.COMPRESS_FILE_LIST:
            if the_file not in settings.COMPRESSION_CACHE:
                with open(the_file, mode='rb') as input:
                    output = compress(input.read(), compression_type)
                    logger.debug("Compressed %s." % relpath(the_file))
                settings.COMPRESSION_CACHE[the_file] = output
            else:
                logger.debug("Found pre-compressed file in cache: %s." % relpath(the_file))
                output = settings.COMPRESSION_CACHE[the_file]
            with open(the_file, mode='wb') as f:
                f.write(output)

        # Remove LESS files if LESS preprocessing is being done
        if settings.PREPROCESS_LESS:
            logger.debug("Deleting LESS files since PREPROCESS_LESS is True.")
            for f in settings.OUTPUT_STATIC_DIR.walkfiles(pattern="*.less"):
                logger.debug("Deleting file: %s." % relpath(f))
                f.remove_p()

        # Check if anything has changed other than the sitemap
        have_changes = False
        compare = filecmp.dircmp(settings.OUTPUT_CACHE_DIR,
                                 settings.OUTPUT_DIR,
                                 ignore=settings.OUTPUT_DIR_IGNORE)

        # The algorithm below takes advantage of the fact that once we've determined that there is more than one file
        # that's different, or if the first item returned by the generator is not the sitemap, then we can break out of
        # the generator loop early. This is also advantageous because it doesn't require us to completely exhaust the
        # generator. In the case of a fresh site build, for example, the generator will return a lot more data. So the
        # other approach here of expanding the generator into a list with a list comprehension would be inefficient
        # in many cases. This approach performs equally well in all cases at the cost of some unusual-looking code.
        diff_file_count = 0
        if not has_files(settings.OUTPUT_DIR):
            have_changes = True
        else:
            for file_path in diff_dir(compare):
                diff_file_count += 1
                if file_path != sitemap_output_path:
                    have_changes = True
                    break
                if diff_file_count > 1:
                    have_changes = True
                    break

        if not have_changes:
            logger.console('')
            logger.console("No site changes to publish.")
        else:
            logger.debug("Synchronizing output directory with output cache.")
            build_stats['files'] = mirror_folder(settings.OUTPUT_CACHE_DIR,
                                                 settings.OUTPUT_DIR,
                                                 ignore_list=settings.OUTPUT_DIR_IGNORE)
            from pprint import pformat

            logger.debug("Folder mirroring report: %s" % pformat(build_stats['files']))
            logger.console('')
            logger.console("Site: '%s' output to %s." % (settings.SITE_TITLE, settings.OUTPUT_DIR))
            logger.console("Posts: %s (%s new or updated)" % (
                (build_stats['counts']['new_posts'] + build_stats['counts']['cached_posts']),
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
        logger.console('')

        with open(settings.BUILD_STATS_FILE, mode='wb') as the_file:
            pickle.dump(build_stats, the_file)
        settings.CACHE.close()
        return build_stats


# noinspection PyShadowingBuiltins
class CleanCommand(ArgParseCommand):
    name = 'clean'
    help = "Clean the output directory and clear all caches."

    # noinspection PyUnusedLocal
    def clean(self, args=None):
        from engineer.conf import settings

        logger = self.get_logger()

        # Expand the ignore list to be full paths
        ignore_list = [path(settings.OUTPUT_DIR / i).normpath() for i in settings.OUTPUT_DIR_IGNORE]
        ignore_dirs = [p for p in ignore_list if p.isdir()]
        ignore_files = []
        for the_dir in ignore_dirs:
            ignore_files.extend([f.normpath() for f in the_dir.walkfiles()])
        ignore_files.extend([p.normpath() for p in ignore_list if p.isfile()])

        # Delete all FILES that are not ignored
        if settings.OUTPUT_DIR.exists():
            for p in settings.OUTPUT_DIR.walkfiles():
                if p in ignore_files:
                    continue
                else:
                    p.remove()

        # Delete all directories with no files. All non-ignored files were already deleted so every directory
        # except those that were ignored will be empty.
        for dirpath, dirnames, filenames in os.walk(settings.OUTPUT_DIR.normpath()):
            dirpath = path(dirpath)
            if dirpath != settings.OUTPUT_DIR:
                if not has_files(dirpath):
                    # no files under this entire path, so can call rmtree
                    # noinspection PyArgumentList
                    dirpath.rmtree()
                    del dirnames[:]
                elif dirpath in ignore_list:
                    # we don't need to descend into the subdirs if this dir is in the ignore list
                    del dirnames[:]

        delete_paths = (
            settings.OUTPUT_DIR,
            settings.OUTPUT_CACHE_DIR,
            settings.CACHE_DIR,
        )

        for the_path in delete_paths:
            try:
                the_path.rmtree()
                logger.info("Deleted %s." % the_path)
            except OSError as we:
                if hasattr(we, 'winerror') and we.winerror not in (2, 3):
                    logger.exception(we.message)
                else:
                    logger.warning("Couldn't find output directory to delete: %s" % we.filename)

        logger.console('Cleaned output directory: %s' % settings.OUTPUT_DIR)

    handler_function = clean


# noinspection PyShadowingBuiltins
class ServeCommand(ArgParseCommand):
    name = 'serve'
    help = "Start the development server."

    def add_arguments(self):
        self.parser.add_argument('-p', '--port',
                                 type=int,
                                 default=8000,
                                 dest='port',
                                 help="The port the development server should listen on.")

    def handler_function(self, args=None):
        import bottle
        from engineer.conf import settings
        from engineer import emma

        logger = self.get_logger()

        if not settings.OUTPUT_DIR.exists():
            logger.warning(
                "Output directory doesn't exist - did you forget to run 'engineer build'?")
            exit()

        debug_server = bottle.Bottle()
        debug_server.mount('/_emma', emma.Emma().app)

        #noinspection PyUnresolvedReferences,PyUnusedLocal
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



# noinspection PyShadowingBuiltins
class InitCommand(ArgParseCommand):
    name = 'init'
    help = "Initialize the current directory as an engineer site."
    need_settings = False

    def add_arguments(self):
        self.parser.add_argument('-m', '--mode',
                                 dest='mode',
                                 default='default',
                                 choices=['azure'],
                                 help="Initialize site with folder structures designed for deployment to a service "
                                      "such as Azure.")
        self.parser.add_argument('--sample',
                                 dest='sample',
                                 action='store_true',
                                 help="Include sample content.")
        self.parser.add_argument('--force', '-f',
                                 dest='force',
                                 action='store_true',
                                 help="Delete target folder contents. Use with caution!")

    def handler_function(self, args=None):
        from engineer import __file__ as package_file

        logger = self.get_logger()

        sample_site_path = path(package_file).dirname() / ('sample_site/%s' % args.mode)
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

        if args.sample:
            mirror_folder(sample_site_path, target)
        else:
            ensure_exists(target / 'posts')
            ensure_exists(target / 'content')
            ensure_exists(target / 'templates')
            mirror_folder(sample_site_path, target, recurse=False)
        logger.console("Initialization complete.")
        exit()


# noinspection PyShadowingBuiltins
class EmmaCommand(ArgParseCommand):
    name = 'emma'
    help = "Start Emma, the built-in management server."

    def add_arguments(self):
        self.parser.add_argument('-p', '--port',
                                 type=int,
                                 default=8080,
                                 dest='port',
                                 help="The port Emma should listen on.")
        self.parser.add_argument('--prefix',
                                 type=str,
                                 dest='prefix',
                                 help="The prefix path the Emma site will be rooted at.")
        emma_options = self.parser.add_mutually_exclusive_group(required=True)
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

    def handler_function(self, args=None):
        from engineer import emma

        logger = self.get_logger()

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
