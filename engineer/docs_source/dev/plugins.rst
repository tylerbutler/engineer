
.. _plugins:

=======
Plugins
=======

Engineer provides a plugin model that allows further customization of Engineer behavior. While Engineer contained a
rudimentary plugin system for themes in version 0.2.3, version 0.3.0 introduced a much richer system and exposed ways
to modify the post rendering pipeline somewhat in addition to Theme plugins.

Engineer's plugin model is based on Marty Allchin's
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

Alternatively, you can deliver your plugin as an installable Python package. This allows users to download and install
your theme via ``pip`` or any other tool. You can do this by adding an ``engineer.plugins`` setuptools `entry point`_
to your :file:`setup.py` file.

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


Post Processor Plugins
======================

.. autoclass:: engineer.plugins.PostProcessor
   :members: preprocess, postprocess


.. _theme plugins:

Theme Plugins
=============

.. autoclass:: engineer.plugins.ThemeProvider
   :members:

The actual Python code needed to register your theme as a plugin is very minimal, but it is overhead compared
to simply downloading a theme directly. The benefit, of course, is that users can manage the installation of the
theme alongside Engineer itself, and since the theme is globally available, users don't need to copy the theme to
each site they want to use it in.


.. _command plugins:

Command Plugins
===============

.. autoclass:: engineer.plugins.CommandPlugin
   :members:


.. _command plugin examples:

Examples
--------


.. _entry point: http://peak.telecommunity.com/DevCenter/setuptools#extensible-applications-and-frameworks
