
======
Themes
======

Engineer includes a bundled default theme called :doc:`dark_rainbow` and will include other themes soon. You can also
create your own themes if you like.


.. _bundled themes:

Bundled Themes
==============

.. toctree::
   :maxdepth: 1

   dark_rainbow


Using Themes
============

By default Engineer uses the :doc:`dark_rainbow` theme. Changing the theme to something else is as simple as changing
the :attr:`~engineer.conf.EngineerConfiguration.THEME` setting in your :doc:`settings file <settings>`.

Most themes do not require any customization, though they might provide :doc:`templates` that you might find useful.
For example, the :doc:`dark_rainbow` theme provides a few different layouts for template pages that you can use as a
basis for your template pages.


Creating Your Own Themes
========================

Theme Package Structure
-----------------------

Themes are essentially a folder with a manifest and a collection of templates and supporting static files (images,
CSS, Javascript, etc.).

A sample theme folder might look like this::

    /theme_id
        - metadata.yaml
        /static
            /scripts
                - script.js
                - ...
            /stylesheets
                - theme.less
                - reset.css
                - ...
        /templates
            /theme
               /layouts
                    - ...
                - _footer.html
                - base.html
                - post_list.html
                - ...

Theme Manifest
--------------

Each theme must contain a file called ``metadata.yaml`` that contains metadata about the theme. The theme manifest
is a simple text file in YAML format. The Dark Rainbow theme manifest looks like this, for example:

.. code-block:: yaml

   name: 'Dark Rainbow'
   id: dark_rainbow
   description: A dark theme with just a hint of color.
   author: 'Tyler Butler <tyler@tylerbutler.com>'
   website: 'http://tylerbutler.com'
   license: 'Creative Commons BY-SA 3.0'
   use_foundation: yes
   use_lesscss: yes
   use_modernizr: no
   use_jquery: yes

   self_contained: yes


Theme Manifest Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~

.. _theme name:

``name``
    The verbose human-readable name of the theme.


.. _theme id:

``id``
    The ID of the theme. This must match the folder name of the theme and should not contain spaces. This is used
    internally by Engineer to identify the theme.


.. _theme self_contained:

``self_contained`` *(optional)*
    Indicates whether the theme is self-contained or not. Defaults to ``True`` if not specified.


.. _theme description:

``description`` *(optional)*
    A more verbose description of the theme.


.. _theme author:

``author`` *(optional)*
    The name and/or email address of the theme's author.


.. _theme website:

``website`` *(optional)*
    The website where the theme or information about it can be found.


.. _theme license:

``license`` *(optional)*
    The license under which the theme is made available.


.. _theme use_foundation:

``use_foundation`` *(optional)*
    Indicates whether the theme makes use of the Foundation CSS library included in Engineer. Defaults to ``False``.


.. _theme use_lesscss:

``use_lesscss`` *(optional)*
    Indicates whether the theme makes use of the LESS CSS library included in Engineer. Defaults to ``False``.


.. _theme use_modernizr:

``use_modernizr`` *(optional)*
    Indicates whether the theme makes use of the Modernizr library included in Engineer. Defaults to ``False``.


.. _theme use_jquery:

``use_jquery`` *(optional)*
    Indicates whether the theme makes use of the jQuery library included in Engineer. Defaults to ``False``.


Required Templates
------------------

The following templates must be present in a theme's :file:`templates/theme` folder:

* _single_post.html
* base.html
* post_archives.html
* post_detail.html
* post_list.html
* template_page_base.html

You can of course include additional templates or template fragments, for use either internally in your theme, or that
users of your theme can take advantage of to further customize their site.


API Reference
=============

.. currentmodule:: engineer.themes

.. autoclass:: Theme
   :members:
