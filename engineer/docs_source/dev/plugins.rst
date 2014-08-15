
.. _plugins:

=======
Plugins
=======

Engineer provides a plugin model that allows further customization of Engineer behavior. While Engineer contained a
rudimentary plugin system for themes in version 0.2.3, version 0.3.0 introduced a much richer system and exposed ways
to modify the post rendering pipeline somewhat in addition to Theme plugins.

Engineer's plugin model is based on Marty Alchin's
`simple plugin framework <http://martyalchin.com/2008/jan/10/simple-plugin-framework/>`_. As such,
creating your own plugin is relatively straightforward:

1. Subclass one of the available plugin base classes (e.g. :class:`~engineer.plugins.PostProcessor`)
2. Load the module containing your plugin during an Engineer operation

Step 1 is quite simple. Step 2 is slightly more involved, but you have a couple of options for your plugin.


Loading Plugins
===============

In order for plugins to be found, the module containing them must be imported by Engineer. Engineer provides two ways
to achieve this. First, you can use the :attr:`~engineer.conf.EngineerConfiguration.PLUGINS` setting. Each module
passed in via that setting will be imported, and the plugins they contain will be available to Engineer.

.. tip::

   Command plugins are the exception; they cannot be loaded using the
   :attr:`~engineer.conf.EngineerConfiguration.PLUGINS` setting. They must be installed as a Python package using the
   method below.

Alternatively, you can deliver your plugin as an installable Python package. This allows users to download and install
your theme via ``pip`` or any other tool. You can do this by adding an ``engineer.plugins`` setuptools `entry point`_
to your :file:`setup.py` file.

.. _entry point: http://peak.telecommunity.com/DevCenter/setuptools#extensible-applications-and-frameworks

In particular, within the `setup` function call in your :file:`setup.py` file, add something like the following:

.. code-block:: python

    entry_points={
        'engineer.plugins': ['post_processors=dotted.path.to.module',
                             'themes=another.module.path'],
        }

The above code registers two plugin modules with Engineer. Engineer will import these modules,
and any subclasses of the plugin base classes will be automatically discovered and run with Engineer.

The identifiers to the left of the equals sign (i.e. ``post_processors`` and ``themes``) can be anything at all.
Engineer doesn't look at them or use them. For clarity, in the above example the plugins have been broken into
different modules by type, and each module has an identifier based on the type of plugin that module contains. But
again, this is not required. It could just as easily read:

.. code-block:: python

    ['foo=dotted.path.to.module',
     'bar=another.module.path']

The type of the plugin is determined by its parent class, not by its module or a specific identifier in the setup
function.

.. tip::

   The *only* requirement to get your plugin loaded is for the module containing it to be imported. Thus,
   if you have a number of plugins in different modules, you could create a wrapper module that simply imported the
   others, then sent your entry point to point to the wrapper module. When the wrapper module is imported,
   the other modules will also be imported, and then your plugins will be magically loaded.


.. _plugin permissions:

Plugin Permissions
==================

Some plugin capabilities are restricted and require explicit permission from the Engineer user via the
:attr:`~engineer.conf.EngineerConfiguration.PLUGIN_PERMISSIONS` setting. As of Engineer 0.5.0 there is only one
permission available, ``MODIFY_RAW_POST``.

Prior to Engineer 0.5.0, it was not possible for plugins to modify actual post content. The
:ref:`metadata finalization` plugin modified post metadata, but post content itself was never changed. This was a
deliberate design decision to try and prevent data loss from runaway plugins. It was especially helpful during plugin
testing when bugs weren't yet found and fixed.

In Engineer 0.5.0, plugins can now modify post content using the :meth:`~engineer.models.Post.set_finalized_content`
method on the Post class. However, this is protected by the ``MODIFY_RAW_POST`` permission. If the plugin is not
explicitly listed as having that permission in the user's config, then calls to ``set_finalized_content`` will do
nothing.

.. note::
   The plugin permissions system is a little clunky and overly protective. The intent of the system is to help
   prevent plugins from doing potentially damaging things (like editing post source content) without explicit
   permission from the user. However, it's possible that I'm being paranoid and that this is overkill. Thus,
   consider this 'experimental' in Engineer 0.5.0. It may go away in the future; I welcome feedback on this.

.. versionadded:: 0.5.0


Common Plugin Methods
=====================

All plugins inherit the some methods from :class:`~engineer.plugins.core.PluginMixin`. Note that you should not
subclass the mixin yourself; rather, you should subclass one of the relevant plugin base classes below. The
PluginMixin class is documented only for completeness.

.. autoclass:: engineer.plugins.core.PluginMixin
   :members:


Jinja Environment Plugins
=========================

.. autoclass:: engineer.plugins.JinjaEnvironmentPlugin
   :members:
   :show-inheritance:


Post Processor Plugins
======================

.. autoclass:: engineer.plugins.PostProcessor
   :members:
   :show-inheritance:


.. _theme plugins:

Theme Plugins
=============

.. autoclass:: engineer.plugins.ThemeProvider
   :members:
   :show-inheritance:

The actual Python code needed to register your theme as a plugin is very minimal, but it is overhead compared
to simply downloading a theme directly. The benefit, of course, is that users can manage the installation of the
theme alongside Engineer itself, and since the theme is globally available, users don't need to copy the theme to
each site they want to use it in.


Command Plugins
===============

The Engineer command line can be customized to include your own commands. See :ref:`command plugins` for more
information.

.. versionchanged:: 0.6.0
   Command plugins changed dramatically in version 0.6.0 and are now :ref:`documented separately<command plugins>`.
