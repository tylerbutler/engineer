# coding=utf-8
import logging

from brownie.caching import memoize, cached_property
from engineer.exceptions import UnsupportedPostFormat
from engineer.log import log_object
from engineer.util import get_class_string, update_additive

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
    return ThemeProvider, PostProcessor, JinjaEnvironmentPlugin, PostRenderer


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
    _logs = '_logs'
    _enabled = 'enabled'

    _required_settings = {
        _enabled: False,
        _logs: dict()
    }

    _settings = _required_settings

    setting_name = None
    default_settings = {}

    @classmethod
    def get_name(cls):
        return get_class_string(cls)

    @classmethod
    def get_logger(cls, custom_name=None):
        """Returns a logger for the plugin."""
        name = custom_name or cls.get_name()
        return logging.getLogger(name)

    @classmethod
    def get_setting_name(cls):
        if cls.setting_name is None:
            # raise NotImplementedError("A setting_name property must be set on the class.")
            return cls.__name__ + '_SETTINGS'
        else:
            return cls.setting_name

    @classmethod
    def get_default_settings(cls):
        return cls.default_settings

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
        :param settings: The global :class:`~engineer.conf.EngineerConfiguration` object that contains all the
            settings for the current Engineer process. Any custom settings should be added to this object.

        :returns: The modified ``config_dict`` object.
        """
        cls.initialize_settings(config_dict)
        return config_dict

    @classmethod
    def initialize_settings(cls, config_dict):
        # Combine the required, default, and user-supplied settings
        plugin_settings = cls._required_settings.copy()
        user_supplied_settings = config_dict.pop(cls.get_setting_name(), {})
        update_additive(plugin_settings, cls.get_default_settings())
        update_additive(plugin_settings, user_supplied_settings)

        cls.store_settings(plugin_settings)

        return plugin_settings, user_supplied_settings

    @classmethod
    def store_settings(cls, plugin_settings):
        cls._settings = plugin_settings

    @classmethod
    def get_settings(cls):
        return cls._settings

    @classmethod
    def is_enabled(cls):
        return cls.get_settings()[cls._enabled]

    @classmethod
    def log_once(cls, msg, key, level=logging.DEBUG):
        if cls.get_settings()[cls._logs].get(key, False):
            return
        else:
            cls.get_logger().log(level, msg)
            cls.get_settings()[cls._logs][key] = True


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

        The preprocess method should use the ``content_preprocessed`` attribute to get/modify the content of *post*.
        This ensures that preprocessors from other plugins can be chained together.

        By default, the ``content_preprocessed`` value is used only
        for generating post HTML. It is not written back to the source post file. However, sometimes you may want
        to make a permanent change to the post content that is written out. In this case, you should call the
        :meth:`~engineer.models.Post.set_finalized_content` method, passing it the modified content. This
        method will ensure the data is written back to the source file by the :ref:`metadata finalization` plugin.
        This means that in order for a plugin to write preprocessed data back to the post file,
        the :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA` setting must be
        enabled.

        Your plugin will also need to be explicitly granted the ``MODIFY_RAW_POST`` permission. See more
        detail in :ref:`plugin permissions`.

        In addition, the preprocess method can add/remove/update properties on the *post* object itself as needed.

        .. tip::
           Since the :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA` setting must be enabled for
           plugins to write back to source post files, you should check this setting in addition to any other
           settings you may be using.

        :param post: The post being currently processed by Engineer.
        :param metadata: A dict of the post metadata contained in the post source file. It contains no
            default values - only the values contained within the post source file itself. The preprocess method can
            add, update, or otherwise manipulate metadata prior to it being processed by Engineer manipulating this
            parameter.

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


class JinjaEnvironmentPlugin(PluginMixin):
    """
    Base class for JinjaEnvironment :ref:`plugins`.

    JinjaEnvironment plugins can supplement the Jinja 2 environment with things like filters and global
    functions. These additions can then be used in your Jinja templates.

    .. versionadded:: 0.5.0
    """
    __metaclass__ = PluginMount

    filters = {}
    """
    A dict of filters to add to the Jinja environment. The key of each entry should be the name of the filter (as it
    will be used inside templates), while the value should be the filter function. If you require more custom logic
    to build the dict of filters, override the :meth:`~engineer.plugins.JinjaEnvironmentPlugin.get_filters` method.
    """

    globals = {}
    """
    A dict of functions to add to the Jinja environment globally. The key of each entry should be the name of the
    function (as it will be used inside templates), while the value should be the function itself. If you require more
    custom logic to build this dict, override the :meth:`~engineer.plugins.JinjaEnvironmentPlugin.get_globals` method.
    """

    @classmethod
    def _add_filters(cls, jinja_env):
        logger = cls.get_logger()
        filters = cls.get_filters()
        for filter_name, filter_function in filters.iteritems():
            if filter_name in jinja_env.filters:
                logger.warning("Jinja filter name conflict. "
                               "A plugin is trying to add a filter with a name that conflicts with an existing filter. "
                               "Filter name: %s" % filter_name)
            else:
                jinja_env.filters[filter_name] = filter_function
                logger.debug("Registered Jinja filter: %s" % filter_name)

    @classmethod
    def _add_globals(cls, jinja_env):
        logger = cls.get_logger()
        global_list = cls.get_globals()
        for global_name, the_global in global_list.iteritems():
            if global_name in jinja_env.globals:
                logger.warning("Jinja global name conflict. "
                               "A plugin is trying to add a global with a name that conflicts with an existing global. "
                               "Global name: %s" % global_name)
            else:
                jinja_env.globals[global_name] = the_global
                logger.debug("Registered Jinja global: %s" % global_name)

    @classmethod
    def update_environment(cls, jinja_env):
        """
        For complete customization of the Jinja environment, subclasses can override this method.

        Subclasses should ensure that the base implementation is called first in their overridden implementation. For
        example:

        .. code-block:: python

            @classmethod
            def update_environment(cls, jinja_env):
                super(BundledFilters, cls).update_environment(jinja_env)
                # some other code here...

        :param jinja_env: The Jinja environment.
        """
        cls._add_filters(jinja_env)
        cls._add_globals(jinja_env)

    @classmethod
    def get_filters(cls):
        """
        If required, subclasses can override this method to return a dict of filters to add to the Jinja environment.
        The default implementation simply returns :attr:`~engineer.plugins.JinjaEnvironmentPlugin.filters`.
        """
        return cls.filters

    @classmethod
    def get_globals(cls):
        """
        If required, subclasses can override this method to return a dict of functions to add to the Jinja
        environment globally. The default implementation simply
        returns :attr:`~engineer.plugins.JinjaEnvironmentPlugin.globals`.
        """
        return cls.globals


class PostRenderer(PluginMixin):
    """
    Base class for PostRenderer :ref:`plugins`.

    .. versionadded:: 0.6.0
    """
    __metaclass__ = PluginMount

    supported_input_formats = ()
    supported_output_formats = ()

    @cached_property
    def supported_extensions_dict(self):
        return dict([(ext, self.__class__) for ext in self.supported_input_formats])

    def render(self, content, input_format, output_format):
        raise NotImplementedError

    # def render_post(self, post):
    #     return self.render(post.content_preprocessed, input_format=post.format, output_format='.html')

    def validate(self, input_format, output_format):
        if input_format not in self.supported_input_formats:
            raise UnsupportedPostFormat(input_format, self.supported_input_formats, self.__class__)

        if output_format not in self.supported_output_formats:
            raise UnsupportedPostFormat(output_format, self.supported_output_formats, self.__class__)

    # noinspection PyUnresolvedReferences
    @staticmethod
    @memoize
    def get_all_supported_post_formats():
        from engineer.conf import settings

        logger = PostRenderer.get_logger()
        extensions = []
        for plugin in PostRenderer.plugins:
            for ext in plugin.supported_input_formats:
                extensions.append((ext, get_class_string(plugin)))

        d = dict()
        for ext, cls in extensions:
            if ext not in d:
                d[ext] = [cls]
            else:
                d[ext].append(cls)

        for ext in d:
            logger.warn("Multiple PostRenderers available for '%s': %s"
                        "\n(Configured to use %s)" % (ext,
                                                      log_object(d[ext]),
                                                      get_class_string(settings.POST_RENDERER_CONFIG[ext])))

        return d.keys()
