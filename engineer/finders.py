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
        themes_path = settings.ENGINEER.THEMES_DIR
        return cls.get_from_directory(themes_path)
