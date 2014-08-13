# coding=utf-8
import logging

from brownie.caching import memoize, cached_property
from jinja2.loaders import FileSystemLoader
from path import path
from webassets import Bundle, Environment as AssetsEnvironment
from webassets.loaders import YAMLLoader
import yaml

from engineer.conf import settings
from engineer.exceptions import ThemeNotFoundException
from engineer.util import get_class, mirror_folder, ensure_exists, urljoin, wrap_list


__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


# noinspection PyNoneFunctionAssignment
# noinspection PyPep8Naming
class Theme(object):
    """
    Creates a new theme object based on the contents of *theme_root_path*.
    """

    def __init__(self, theme_root_path, **kwargs):
        self.logger = logging.getLogger('engineer.themes.Theme')

        self.root_path = path(theme_root_path)
        self.name = kwargs.get('name')
        self.id = kwargs.get('id', self.name.lower().replace(' ', '_'))
        self.description = kwargs.get('description', None)
        self.author = kwargs.get('author', None)
        self.website = kwargs.get('website', None)
        self.license = kwargs.get('license', None)

        self.self_contained = kwargs.get('self_contained', True)
        self.static_root = path(kwargs.get('static_root', self.root_path / 'static/')).abspath()
        self.template_root = path(kwargs.get('template_root', self.root_path / 'templates')).abspath()
        self.template_dirs = [self.template_root]
        self.use_precompiled_styles = kwargs.get('use_precompiled_styles', True)

        self.bundle_files = {'bundles.yaml'}
        self.bundle_files.update(wrap_list(kwargs.get('bundles', [])))

        # set up mappings for any additional content
        self.content_mappings = {}
        if 'copy_content' in kwargs:
            for item, target in iter(kwargs['copy_content']):
                item_path = path(item)
                source = path(self.root_path / item_path).abspath()
                if target is None:
                    target = item_path
                self.content_mappings[source] = target

        if 'template_dirs' in kwargs:
            self.template_dirs.extend([path(self.root_path / t).abspath() for t in kwargs['template_dirs']])

        # set the default theme settings values
        default_settings = kwargs.get('settings', None)
        if default_settings:
            for k, v in default_settings.iteritems():
                setattr(self, k, v)

        # update the theme settings based on anything passed in via the site settings
        for k, v in settings.THEME_SETTINGS.iteritems():
            setattr(self, k, v)

    @property
    def STATICFILE_DIR(self):
        return self.static_root

    @property
    def TEMPLATE_DIR(self):
        return self.template_root

    @property
    def template_loader(self):
        return FileSystemLoader(self.template_dirs)

    @cached_property
    def assets_environment(self):
        # because we're using the append_path function to add paths for the source files, the
        # directory argument will be used as the output path
        assets_env = AssetsEnvironment(directory=(settings.OUTPUT_STATIC_DIR / 'bundled'),
                                       url=urljoin(settings.STATIC_URL, 'bundled'),
                                       # cache=self.ENGINEER.WEBASSETS_CACHE_DIR,  # this seems broken in webassets
                                       debug='merge' if settings.DEBUG else False)
        assets_env.config['less_bin'] = settings.LESS_PREPROCESSOR

        # register the global bundles
        assets_env.append_path(settings.ENGINEER.LIB_DIR, url=urljoin(settings.STATIC_URL, 'lib'))

        for name, bundle in ThemeManager.global_bundles.iteritems():
            assets_env.register(name, bundle)

        # register code style bundles
        assets_env.append_path(settings.ENGINEER.THEMES_DIR / '_shared/code_styles',
                               url=urljoin(settings.STATIC_URL, 'code'))
        for name, bundle in ThemeManager.code_style_bundles.iteritems():
            assets_env.register(name, bundle)

        # register the local bundles
        for bundle_file in self.bundle_files:
            bundle_yaml = self.root_path / bundle_file
            if bundle_yaml.exists():
                assets_env.append_path(self.root_path, url=urljoin(settings.STATIC_URL, 'theme_bundled'))
                loader = YAMLLoader(bundle_yaml.abspath())
                local_bundles = loader.load_bundles(assets_env)
                for name, bundle in local_bundles.iteritems():
                    assets_env.register(name, bundle)
            else:
                self.logger.warning("Cannot find bundle file %s for theme %s." % (bundle_file, self.id))

        return assets_env

    def theme_path(self, template):
        if (self.template_root / template).abspath().exists():
            return str(self.template_root / template)
        else:
            return template

    def copy_content(self, output_path):
        # Copy theme static content to output dir
        try:
            s = self.static_root.abspath()
        except ThemeNotFoundException as e:
            self.logger.critical(e.message)
            exit()
        t = path(output_path).abspath()
        # noinspection PyUnboundLocalVariable
        mirror_folder(s, t)

    def copy_related_content(self, output_path):
        if self.content_mappings:
            for s, t in self.content_mappings.iteritems():
                t = path(output_path / t).abspath()
                if s.isdir():
                    mirror_folder(s, t)
                else:
                    s.copy(ensure_exists(t))

    def copy_all_content(self, output_dir):
        self.copy_content(output_dir)
        self.copy_related_content(output_dir)

    @staticmethod
    def from_yaml(yaml_file):
        with open(yaml_file, mode='rb') as the_file:
            yaml_doc = yaml.load(the_file.read())
        theme = Theme(path(yaml_file).dirname(), **yaml_doc)
        return theme

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.name


class ThemeManager(object):
    @classmethod
    @memoize
    def themes(cls):
        themes = []
        for f in settings.THEME_FINDERS:
            finder = get_class(f)
            themes.extend(finder.get_themes())
        # noinspection PyTypeChecker
        return dict([t.id, t] for t in themes)

    @classmethod
    @memoize
    def themes_by_finder(cls):
        themes = {}
        for f in settings.THEME_FINDERS:
            finder = get_class(f)
            themes[f] = finder.get_themes()
        return themes

    @classmethod
    @memoize
    def current_theme(cls):
        theme = ThemeManager.themes().get(settings.THEME)
        if theme is not None:
            return theme
        else:
            raise ThemeNotFoundException("Theme with id '%s' cannot be found." % settings.THEME)

    @staticmethod
    @memoize
    def theme_path(template):
        return path(ThemeManager.current_theme().template_root) / template

    # noinspection PyShadowingBuiltins
    @staticmethod
    @memoize
    def theme(id):
        if id not in ThemeManager.themes():
            raise ThemeNotFoundException("Theme with id '%s' cannot be found." % id)
        else:
            return ThemeManager.themes()[id]

    global_bundles = {
        'jquery': Bundle('jquery-1.11.0.min.js',
                         output='jquery.%(version)s.js'),
        'less': Bundle('less-1.7.0.min.js',
                       output='less.%(version)s.js'),
        'modernizr': Bundle('modernizr-2.7.1.min.js',
                            output='modernizr.%(version)s.js'),
        'foundation_js': Bundle('foundation/javascripts/foundation.js',
                                filters='jsmin',
                                output='foundation.%(version)s.js'),
        'foundation_css': Bundle('foundation/stylesheets/grid.css',
                                 'foundation/stylesheets/mobile.css',
                                 filters='cssmin',
                                 output='foundation.%(version)s.css'),
        'foundation_css_ie': Bundle('foundation/stylesheets/ie.css',
                                    filters='cssmin',
                                    output='foundation_ie.%(version)s.css'),
        'normalize': Bundle('normalize/normalize.css',
                            filters='cssmin',
                            output='normalize.%(version)s.css')
    }

    _codestyle_list = (settings.ENGINEER.THEMES_DIR / '_shared/code_styles/').files('*.css')
    code_style_bundles = dict([('codestyle_%s' % name.namebase,
                                Bundle(name, output=('codestyle_%s' % name.namebase) + '.%(version)s.css'))
                               for name in _codestyle_list])
