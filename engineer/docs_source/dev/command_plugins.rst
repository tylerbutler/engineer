
.. _command plugins:

Command Plugins
===============

There are many cases where it may be useful to enhance Engineer by adding new commands to its
:ref:`command line interface<cmdline>`. Engineer provides a way for you to do this fairly easily using the same model
as :ref:`other plugins<plugins>`. In fact, the core Engineer commands are implemented as plugins that come bundled
with Engineer.

.. tip::

   Unlike other plugin types, Command plugins cannot be loaded using
   the :attr:`~engineer.conf.EngineerConfiguration.PLUGINS` setting.  They must be installed as a Python package and
   are therefore available to all sites using a given Engineer installation.


Command Plugin Forms
--------------------

Engineer provides two forms of command extensibility: argparse and ``argh``. The argparse style will be
familiar to anyone who has used argparse, the
`command-line processing module <https://docs.python.org/2.7/howto/argparse.html#id1>`_ in the Python standard library.

The alternative is to use `argh <http://argh.readthedocs.org/en/latest/>`_, which is a wrapper around argparse
that provides a great deal of simplifying functionality while retaining the power inherent in argparse.

So, what style should you use? In general, I recommend using argh if you're new to Python or command-line
handling in general. I think it's much simpler to use, and it requires a lot less boilerplate code. While none of the
core Engineer commands use argh, there are examples below that will guide you through the process.

One very minor drawback to argh is that as of Engineer version 0.6.0, it is not included as a dependency and thus is
not installed by default. This means that you'll need to include it as a dependency in your own plugin's package. An
upcoming version of Engineer may include it so this would no longer be necessary.

The core Engineer commands were originally written before the command plugin model existed,
and were written to use argparse directly. Depending on what you're doing you might find it more powerful.
Certainly if you already have experience with argparse, there's no reason to go out and learn how to use argh.
unless you want to.


Basic Plugin Model
------------------

As with :ref:`other plugins<plugins>`, command plugins are implemented by subclassing a plugin base class. Unlike
other plugins, however, there are multiple base classes to use. In addition,
there is a more complex class hierarchy including some private mixin classes that are documented here for
completeness, but that you shouldn't need to subclass directly in your plugins.

The mixins and base classes abstract away most of the complexity of dealing with the guts of the parsers,
and provide simple ways to plug in your own functions. In addition, you can also add the ``verbose`` and ``settings``
options that are available in most Engineer commands easily without implementing them yourself.

.. autoclass:: engineer.commands.core._CommandMixin
   :members:
   :show-inheritance:


Argparse-based Plugins
----------------------

.. autoclass:: engineer.commands.core._ArgParseMixin
   :members:
   :show-inheritance:

.. autoclass:: engineer.commands.core.ArgParseCommand
   :members:
   :show-inheritance:


Argh-based Plugins
------------------

.. autoclass:: engineer.commands.core.SimpleArghCommand
   :members:
   :show-inheritance:


More Advanced Plugin Styles
---------------------------

.. autoclass:: engineer.commands.core.Command
   :members:
   :show-inheritance:
