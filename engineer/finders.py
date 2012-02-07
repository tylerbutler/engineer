from engineer.conf import settings
from engineer.themes import Theme

__author__ = 'tyler@tylerbutler.com'

class BaseFinder(object):
    @classmethod
    def get_from_directory(cls, directory):
        themes = []
        for file in directory.walkfiles('metadata.yaml'):
            themes.append(Theme.from_yaml(file))
        return themes


class DefaultFinder(BaseFinder):
    @classmethod
    def get_themes(cls):
        themes_path = settings.ENGINEER_THEMES_DIR
        return cls.get_from_directory(themes_path)


#class AppDirectoriesFinder(BaseFinder):
#    @classmethod
#    def get_themes(cls):
#        themes = []
#        for app in settings.INSTALLED_APPS:
#            # ignore built-in Django apps - none of them will have themes
#            if not app.startswith('django.'):
#                mod = __import__(app)
#                theme_path = path(mod.__file__).dirname() / 'themes'
#                if theme_path.exists():
#                    themes.extend(cls.get_from_directory(theme_path))
#        return themes
