# coding=utf-8
from logging import getLogger
from path import path
from tempfile import mkdtemp
from zipfile import ZipFile
from engineer.conf import settings
from engineer.exceptions import ThemeDirectoryNotFoundException
from engineer.themes import Theme

__author__ = 'tyler@tylerbutler.com'

logger = getLogger('engineer.finders')

class BaseFinder(object):
    @classmethod
    def get_from_directory(cls, directory):
        if not path(directory).exists():
            raise ThemeDirectoryNotFoundException(directory)
        themes = []
        for file in directory.walkfiles('metadata.yaml'):
            themes.append(Theme.from_yaml(file))

        for zipped_file in directory.walkfiles('*.zip'):
            temp = path(mkdtemp())
            with ZipFile(zipped_file, 'r') as theme:
                theme.extractall(path=temp)
            logger.debug("Zipped theme %s unzipped to %s." % (zipped_file, temp))
            themes.extend(cls.get_from_directory(temp))
        return themes

    @classmethod
    def get_themes(cls):
        return NotImplementedError()


class DefaultFinder(BaseFinder):
    """Locates and loads built-in Engineer themes."""

    @classmethod
    def get_themes(cls):
        themes_path = settings.ENGINEER.THEMES_DIR
        return cls.get_from_directory(themes_path)


class SiteFinder(BaseFinder):
    """
    Loads themes from the ``/themes`` directory inside a site folder.

    .. versionadded:: 0.2.3
    """

    @classmethod
    def get_themes(cls):
        themes_path = settings.SETTINGS_DIR / 'themes'
        if themes_path.exists():
            return cls.get_from_directory(themes_path)
        else:
            return []


class ThemeDirsFinder(BaseFinder):
    """
    Loads themes from the directories specified in :attr:`~engineer.conf.EngineerConfiguration.THEME_DIRS`.

    .. versionadded:: 0.2.3
    """

    @classmethod
    def get_themes(cls):
        themes = []
        for dir in settings.THEME_DIRS:
            try:
                themes.extend(cls.get_from_directory(dir))
            except ThemeDirectoryNotFoundException as e:
                logger.warning(e.message)
                continue
        return themes


class PluginFinder(BaseFinder):
    """
    Loads themes from any installed :ref:`theme plugins`.

    .. versionadded:: 0.2.4
    """

    @staticmethod
    def find_theme_plugins():
        try:
            import pkg_resources
        except ImportError:
            pkg_resources = None

        if pkg_resources is None:
            return
        for entrypoint in pkg_resources.iter_entry_points('engineer.themes'):
            yield entrypoint.name, entrypoint.load()

    @classmethod
    def get_themes(cls):
        themes = []
        try:
            for name, theme_path in PluginFinder.find_theme_plugins():
                themes.extend(cls.get_from_directory(theme_path))
        except ImportError as e:
            logger.warning(e.message)
            return []

        return themes
