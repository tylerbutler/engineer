# coding=utf-8
import logging

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

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


# noinspection PyUnresolvedReferences,PyUnusedLocal
def load_plugins():
    """Load all plugins."""

    # Ensure the built-in plugins are loaded by importing the module
    from engineer.plugins import bundled

    # Load registered plugin modules
    for name, module in find_plugins('engineer.plugins'):
        # No need to import the module manually because find_plugins will do that.
        pass


def get_all_plugin_types():
    return ThemeProvider, PostProcessor, CommandPlugin


# noinspection PyMissingConstructor,PyUnusedLocal
class PluginMount(type):
    """A metaclass used to identify :ref:`plugins`."""

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


class PluginMixin(object):
    @classmethod
    def get_logger(cls):
        """Returns a logger for the plugin."""
        return logging.getLogger('.'.join([cls.__module__, cls.__name__]))

    @classmethod
    def handle_settings(cls, config_dict, settings):
        """
        If a plugin defines its own settings, it may also need to handle those settings in some unique way when the
        Engineer configuration files are being read. By overriding this method,
        plugins can ensure such unique handling of their settings is done.

        Note that a plugin does not have to handle its own settings unless there is unique processing that must be
        done. Any settings that are unknown to Engineer will automatically be added as attributes on the
        :class:`~engineer.conf.EngineerConfiguration` object. This method should only be implemented if the settings
        must be processed in some more complicated way prior to being added to the global configuration object.

        Implementations of this method should check for the plugin-specific settings in ``config_dict`` and set
        appropriate attributes/properties on the ``settings`` object. In addition, settings that
        have been handled should be removed from ``config_dict``. This ensures they are not handled by
        other plugins or the default Engineer code.

        :param config_dict: The dict of as-yet unhandled settings in the current settings file.

        :param settings: The global :class:`~engineer.conf.EngineerConfiguration` object that contains all the
            settings for the current Engineer process. Any custom settings should be added to this object.

        :returns: The modified ``config_dict`` object.
        """
        return config_dict


class ThemeProvider(PluginMixin):
    """
    Base class for Theme :ref:`plugins`.

    ThemeProvider subclasses must provide a value for :attr:`~engineer.plugins.ThemeProvider.paths`.

    .. versionchanged:: 0.3.0
    """
    __metaclass__ = PluginMount

    paths = ()  # empty tuple
    """An iterable of absolute paths containing one or more :ref:`theme manifests <theme manifest>`."""


class PostProcessor(PluginMixin):
    """
    Base class for Post Processor :ref:`plugins`.

    PostProcessor subclasses should provide implementations for :meth:`~engineer.plugins.PostProcessor.preprocess` or
    :meth:`~engineer.plugins.PostProcessor.postprocess` (or both) as appropriate.
    """
    __metaclass__ = PluginMount

    @classmethod
    def preprocess(cls, post, metadata):
        """
        The ``preprocess`` method is called during the Post import process, before any post metadata defaults
        have been set.

        :param post: The post being currently processed by Engineer. The preprocess method should use the
            ``content_preprocessed`` attribute to get/modify the content of *post*. This ensures that preprocessors
            from other plugins can be chained together.

        :param metadata: A dict of the post metadata contained in the post source file. It contains no
            default values - only the values contained within the post source file itself. The preprocess method can
            add, update, or otherwise manipulate metadata prior to it being processed by Engineer manipulating this
            parameter.

        In addition, the preprocess method can add/remove/update properties on the *post* object itself as needed.

        :return: The *post* and *metadata* values should be returned (as a 2-tuple) by the method.
        """
        return post, metadata

    @classmethod
    def postprocess(cls, post):
        """
        The ``postprocess`` method is called after the post has been imported and processed as well as converted to
        HTML and output.

        :param post: The post being currently processed by Engineer.
        :return: The *post* parameter should be returned.
        """
        return post


class CommandPlugin(PluginMixin):
    """
    Base class for Command :ref:`plugins`.

    Command plugins add new commands to the :ref:`cmdline`. CommandPlugin subclasses must provide an implementation
    for :meth:`~engineer.plugins.CommandPlugin.add_command`, and can optionally override
    the :meth:`~engineer.plugins.CommandPlugin.active` classmethod to determine whether or not the plugin should
    actually be loaded.

    .. note::
        Because Engineer uses :mod:`argparse` for parsing out its commands, you should be somewhat familiar with
        it in order to implement a Command plugin.

    .. seealso:: :ref:`command plugin examples`
    """
    __metaclass__ = PluginMount

    @classmethod
    def active(cls):
        """
        If this method returns ``False``, the plugin will not run and any commands added by the plugin will not
        be available.

        This method can be overridden to make commands available only if certain criteria are met (for example,
        a custom :ref:`setting<settings>`).

        :return: A boolean value indicating whether or not the plugin is active and should run. Default
            implementation always returns ``True``.
        """
        return True

    @classmethod
    def add_command(cls, subparser, main_parser, common_parser):
        """
        This method is called by Engineer while it is building its :class:`~argparse.ArgumentParser`,
        allowing one to add addition parsers and subparsers to supplement the core :ref:`Engineer commands<cmdline>`.

        :param subparser:
            Since Engineer's built-in commands are subparsers, :meth:`~argparse.ArgumentParser.add_subparsers` is
            called to generate a subparser. :mod:`argparse` only supports
            calling :meth:`~argparse.ArgumentParser.add_subparsers` once, so the subparser object itself (the result
            of the initial :meth:`~argparse.ArgumentParser.add_subparsers` call Engineer made when building its
            parser) is passed in this parameter. This allows you to add either another top-level command by calling
            ``add_parser()`` then adding arguments directly, or to create further nested commands by adding a parser
            with additional subparsers within it.

        :param main_parser:
            The top level :class:`~argparse.ArgumentParser` used by Engineer. This is generally only useful if you're
            using an :mod:`argparse` wrapper library such as `argh <http://packages.python.org/argh/index.html>`_ in
            your plugin. Most wrapper libraries require the root :class:`~argparse.ArgumentParser` object to add their
            subparsers to. If you're using :mod:`argparse` directly, you can ignore this parameter and work with
            the ``subparser`` parameter exclusively.

        :param common_parser:
            Engineer provides several :ref:`common arguments<engineer>` for its commands. If you wish to makes these
            arguments available for your custom commands, you should pass ``common_parser`` in
            to ``add_parser()`` via the ``parents`` parameter.
        """
        raise NotImplementedError()
