
.. currentmodule:: engineer.conf

========================
Creating Your Own Themes
========================

Theme Package Structure
=======================

Themes are essentially a folder with a manifest and a collection of templates and supporting static files (images,
CSS, Javascript, etc.). Custom themes should be put in a :file:`themes` folder within the site's root. You can put
themes elsewhere by specifying the :attr:`~EngineerConfiguration.THEME_DIRS` setting.

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
==============

Each theme must contain a file called ``metadata.yaml`` that contains metadata about the theme. The theme manifest
is a simple text file in YAML format. The Dark Rainbow theme manifest looks like this, for example:

.. literalinclude:: ../../themes/dark_rainbow/metadata.yaml
   :language: yaml


Theme Manifest Parameters
-------------------------

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


.. _theme default:

``settings`` *(optional)*
    A dictionary of all the themes-specific settings that users of your theme can provide via
    :attr:`~engineer.conf.EngineerConfiguration.THEME_SETTINGS` and their default values. If your theme supports
    custom settings, you must specify defaults. Due to the way Engineer loads your theme settings and a user's
    site settings, your settings may not be created at all unless you specify them here.

    .. versionadded:: 0.2.3

    .. seealso:: :ref:`use theme settings`


Required Templates
==================

The following templates must be present in a theme's :file:`templates/theme` folder:

* _single_post.html
* base.html
* post_archives.html
* post_detail.html
* post_list.html
* template_page_base.html

You can of course include additional templates or template fragments, for use either internally in your theme, or that
users of your theme can take advantage of to further customize their site.

You should also ensure that your theme templates load the :ref:`built-in fragments` that Engineer users will expect.


Required Styles
===============

TODO

.image, .left, .right, .caption


.. _use theme settings:

Referring to Custom Theme Settings in Templates
===============================================

Custom theme settings are available in all Engineer templates. Every template is passed a context variable called
``theme`` that represents the current theme. Any custom settings specified are available as attributes on that
object. For example, if your theme defines a custom setting called ``typekit_id``, then you can refer to that setting
in any Engineer template like so:

.. code-block:: html+jinja

    {# TYPEKIT #}
    <script type="text/javascript"
           src="http://use.typekit.com/{{ theme.typekit_id }}.js"></script>
    <script type="text/javascript">
       try {
           Typekit.load();
       } catch (e) {}
    </script>


Useful Macros
=============

TODO


.. _zipping themes:

Zipping Themes
==============

You can optionally put your theme directory in a zip file. The file should have a ``.zip`` file extension. Engineer
will unzip the folder to a temporary location during a build and load the theme from that temporary location.

.. versionadded:: 0.2.3


Sharing Your Theme
==================

The simplest way to share your theme is to :ref:`zip it up <zipping themes>` and make it available to download. Users
can then download it and use it by placing it in their site's :file:`themes` directory or in another one of their
:attr:`~EngineerConfiguration.THEME_DIRS`.


.. _theme plugins:

Theme Plugins
-------------

You may wish to deliver your theme as an installable Python package. This allows users to download and install your
theme via ``pip`` or any other tool. You can do this by wrapping your theme in a Python package and adding some
specific entry points to your :file:`setup.py` file.

In particular, within the `setup` function call in your :file:`setup.py` file, add something like the following:

.. code-block:: python

    entry_points={
        'engineer.themes': ['jordanm_light=jordanm:light'],
        }

The above code registers the ``jordanm_light`` theme with Engineer. It tells Engineer that within the ``jordanm``
module there is a property/function ``light`` that will return the path to the theme. Engineer will automatically
find all themes registered in this way and make them available to sites.

The actual Python code needed to register your theme in this way is very minimal, but it is overhead compared
to simply downloading a theme directly. The benefit, of course, is that users can manage the installation of the
theme alongside Engineer itself, and since the theme is globally available, users don't need to copy the theme to
each site they want to use it in.

.. versionadded:: 0.2.4

.. seealso:: :ref:`plugins`


Add Your Theme to Engineer
--------------------------

If you'd like to make your theme available with the main Engineer application, send a pull request on github.
