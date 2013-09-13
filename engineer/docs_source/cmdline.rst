
.. _cmdline:

====================
Engineer Commandline
====================

Engineer is primarily invoked at the command line. The command is aptly called ``engineer``,
or ``engineer.exe`` on Windows. It accepts five basic top-level commands: ``build``, ``clean``, ``serve``,
``emma`` and ``init``, which each accept additional parameters.

Common Arguments
================

.. _engineer:

.. program:: engineer

All of the Engineer commands accept the following arguments:

.. option:: -h, --help

   Display help for the command.


.. option:: -v, --verbose

   Display verbose command line output. You can see *extremely* verbose output by specifying the option twice. For
   example::

       engineer build -vv

   .. versionchanged:: 0.2.3

.. option:: -s, --settings, --config

   Specify the  to use. Defaults to ``config.yaml`` if not provided.

   .. note:: While the  :ref:`engineer init` command does accept this argument, it does not use it in any way.


Sub-commands
============

.. _engineer init:

``engineer init``
-----------------

.. program:: init

Initialize a directory with a basic structure for an Engineer site, optionally including sample content. Note that
using the ``init`` command is *not* required to create an Engineer site; all it does is a create a general purpose
folder structure, a :doc:`settings file <settings>`, and optionally some sample content.

**Usage**::

    engineer init [-h] [-v] [-s CONFIG_FILE] [--no-sample] [-f]

.. option:: --no-sample

   By default, the ``init`` command includes some sample content to provide a starting point for a new site. By
   passing this option, however, no sample content will be created.


.. option:: -f, --force

   Forcefully initialize a folder as an engineer site even if the target folder is not empty. **Use with caution!**


.. _engineer build:

``engineer build``
------------------

.. program:: build

Build an Engineer site from an input settings file and other source files.

**Usage**::

    engineer build [-h] [-v] [-s CONFIG_FILE] [-c]

.. option:: -c, --clean

   Clear all caches and the output directory prior to building. This parameter is equivalent
   to :ref:`engineer clean` but immediately runs a ``build`` after.


.. _engineer clean:

``engineer clean``
------------------

.. program:: clean

Clears all caches and the output directory. This can be useful if you're seeing strange errors such as changes not
being picked up properly or you simply want to 'start fresh.'

**Usage**::

    engineer clean [-h] [-v] [-s CONFIG_FILE] [-p PORT]


.. _engineer serve:

``engineer serve``
------------------

.. program:: serve

Starts the built-in Engineer development server. The dev server will serve up a site's output directory contents at
http://localhost:8000. You can press :kbd:`Ctrl-C` to stop the dev server when you're done with it. Note that
``serve`` does not build a site, so you should run :ref:`engineer build` before you run :ref:`engineer serve`. Also
keep in mind that if you make changes to the site source, such as posts or whatnot,
you'll need to manually rebuild the site in order for those changes to be reflected. Adding the capability to
autodetect changes and rebuild the site as needed `are planned <https://trello.com/c/l5daPclc>`_ but not yet
implemented.

.. note::
   It's not a good idea to use the dev server to serve your site in production. While it's probably capable of this
   since it uses bottle.py under the covers, it hasn't been tested or designed for that purpose. Besides,
   part of the benefit in using Engineer in the first place is that you can just copy the output to an existing
   production web server and go. Why take on additional overhead of running your own server if you don't need to?

**Usage**::

    engineer serve [-h] [-v] [-s CONFIG_FILE] [-p PORT]

.. option:: -p, --port

   Specify the port the development server should run on. If not specified, the default is 8000.

   .. versionadded:: 0.2.3


.. _engineer emma:

``engineer emma``
------------------

.. program:: emma

Documentation TBD.

**Usage**::

    engineer emma [-h] [-v] [-s CONFIG_FILE] [-p PORT] [--prefix PREFIX] (-r | -g | -u)

