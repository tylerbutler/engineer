
.. currentmodule:: engineer.conf

======
Themes
======

Engineer currently includes two bundled themes: :ref:`dark rainbow` and :ref:`oleb`. You can also
:doc:`create your own themes <dev/theme_creation>` if you like.

.. seealso:: :doc:`dev/theme_creation`


.. _bundled themes:

Bundled Themes
==============

.. toctree::
   :maxdepth: 2
   :glob:

   themes/*


Using Themes
============

By default Engineer uses the :ref:`dark rainbow` theme. Changing the theme to something else is as simple as
changing the :attr:`~engineer.conf.EngineerConfiguration.THEME` setting in your :doc:`settings file <settings>`.

Most themes do not require any customization, though they might provide :doc:`templates` that you might find useful.
For example, the :ref:`dark rainbow` theme provides a few different layouts for template pages that you can use
as a basis for your template pages.


Installing New Themes
=====================

Engineer themes can be used without installation. Simply download the theme, place it in the :file:`themes` directory
within your site directory, and change your :attr:`~EngineerConfiguration.THEME` setting to use the new theme.

Alternatively, some themes might be available as an installable :ref:`plugin <theme plugins>`. If this is the case
for the theme you want to use, then follow the installation instructions for the theme. Once installed,
it will be available to any Engineer site.
