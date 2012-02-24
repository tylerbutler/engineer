# coding=utf-8
import yaml
from path import path
from engineer.conf import settings
from engineer.util import get_class

__author__ = 'tyler@tylerbutler.com'

class Theme(object):
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

        self.self_contained = kwargs.get('self_contained', True)
        self.static_root = path(kwargs.get('static_root', self.root_path / 'static/')).abspath()
        self.template_root = path(kwargs.get('template_root', self.root_path / 'templates')).abspath()

        if 'templates' in kwargs:
            self.templates = dict((k, self.theme_path(v)) for (k, v) in kwargs['templates'].iteritems())
        else:
            self.templates = dict((p.namebase, 'theme/%s' % p.name) for p in
            self.template_root.walkfiles(pattern='*.html'))

        for k, v in settings.THEME_SETTINGS.iteritems():
            setattr(self, k, v)

    @property
    def STATICFILE_DIR(self):
        return self.static_root

    @property
    def TEMPLATE_DIR(self):
        return self.template_root

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


class ThemeManager(object):
    @classmethod
    def themes(cls):
        themes = []
        for f in settings.THEME_FINDERS:
            finder = get_class(f)
            themes.extend(finder.get_themes())

        return dict([t.id, t] for t in themes)

    @classmethod
    def current_theme(cls):
        return ThemeManager.themes().get(settings.THEME, None)

    @staticmethod
    def theme_path(template):
        return path(ThemeManager.current_theme().template_root) / template

    @staticmethod
    def theme(id):
        return ThemeManager.themes[id]
