# coding=utf-8

__author__ = 'tyler@tylerbutler.com'

# Adapted from Marty Alchin: http://martyalchin.com/2008/jan/10/simple-plugin-framework/

def find_plugins(entrypoint):
    try:
        import pkg_resources
    except ImportError:
        pkg_resources = None

    if pkg_resources is None:
        return
    for entrypoint in pkg_resources.iter_entry_points(entrypoint):
        yield entrypoint.name, entrypoint.load()


def load_plugins():
    """Load all plugins."""

    # Themes
    for theme, theme_path in find_plugins('engineer.themes'):
        ThemeProvider.themes.append(theme_path)

    # Post Preprocessors
    for plugin in find_plugins('engineer/post_preprocessors'):
        pass

    # Post Postprocessors
    for plugin in find_plugins('engineer.post_postprocessors'):
        pass


class ThemeProvider(object):
    themes = []


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)


class PostPreprocessorProvider(object):
    __metaclass__ = PluginMount

    @staticmethod
    def process(post):
        raise NotImplementedError


class PostPostprocessorProvider(object):
    __metaclass__ = PluginMount

    @staticmethod
    def process(post):
        raise NotImplementedError
