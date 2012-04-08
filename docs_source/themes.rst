
======
Themes
======

Engineer includes a bundled default theme called Dark Rainbow and will include other themes soon. You can also create
your own themes if you like.

.. toctree::
   :maxdepth: 2

   dark_rainbow

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
is a simple text file in YAML format. The Dark Rainbow theme manifest looks like this, for example::

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

The following templates must be present in a theme:

* _single_post.html
* base.html
* post_archives.html
* post_detail.html
* post_list.html
* tags_list.html

API Reference
=============

.. currentmodule:: engineer.themes

.. autoclass:: Theme
   :members:
