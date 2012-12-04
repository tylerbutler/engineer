# coding=utf-8
from jinja2.loaders import FileSystemLoader
import yaml
from brownie.caching import memoize
from path import path
from engineer.conf import settings
from engineer.exceptions import ThemeNotFoundException
from engineer.util import get_class

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

class Theme(object):
    """
    Creates a new theme object based on the contents of *theme_root_path*.
    """

    def __init__(self, theme_root_path, **kwargs):
        self.root_path = path(theme_root_path)
        self.name = kwargs.get('name')
        self.id = kwargs.get('id', self.name.lower().replace(' ', '_'))
        self.description = kwargs.get('description', None)
        self.author = kwargs.get('author', None)
        self.website = kwargs.get('website', None)
        self.license = kwargs.get('license', None)
        self.use_foundation = kwargs.get('use_foundation', False)
        self.use_lesscss = kwargs.get('use_lesscss', False)
        self.use_modernizr = kwargs.get('use_moderinzr', False)
        self.use_jquery = kwargs.get('use_jquery', False)
        self.use_tweet = kwargs.get('use_tweet', False)

        self.self_contained = kwargs.get('self_contained', True)
        self.static_root = path(kwargs.get('static_root', self.root_path / 'static/')).abspath()
        self.template_root = path(kwargs.get('template_root', self.root_path / 'templates')).abspath()
        self.template_dirs = [self.template_root]

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

    def theme_path(self, template):
        if (self.template_root / template).abspath().exists():
            return str(self.template_root / template)
        else:
            return template

    @staticmethod
    def from_yaml(yaml_file):
        with open(yaml_file, mode='rb') as file:
            yaml_doc = yaml.load(file.read())
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
        return dict([t.id, t] for t in themes)

    @classmethod
    @memoize
    def current_theme(cls):
        theme = ThemeManager.themes().get(settings.THEME, None)
        if theme is not None:
            return theme
        else:
            raise ThemeNotFoundException("Theme with id '%s' cannot be found." % settings.THEME)

    @staticmethod
    @memoize
    def theme_path(template):
        return path(ThemeManager.current_theme().template_root) / template

    @staticmethod
    @memoize
    def theme(id):
        if id not in ThemeManager.themes():
            raise ThemeNotFoundException("Theme with id '%s' cannot be found." % settings.THEME)
        else:
            return ThemeManager.themes[id]
