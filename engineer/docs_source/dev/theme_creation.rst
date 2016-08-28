
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

    .
    ├── theme_id
    |   ├── static
    |   |   ├── scripts
    |   |   |   ├── script.js
    |   |   |   └── ...
    |   |   ├── stylesheets
    |   |   |   ├── theme.less
    |   |   |   ├── reset.css
    |   |   |   └── ...
    |   |   ├── templates
    |   |   |   ├── theme
    |   |   |   |   ├── layouts
    |   |   |   |   |   └── ...
    |   |   |   |   ├── _footer.html
    |   |   |   |   ├── base.html
    |   |   |   |   ├── post_list.html
    |   |   |   |   └── ...
    |   ├── bundles.yaml
    |   └── metadata.yaml


.. _theme manifest:

Theme Manifest
==============

Each theme must contain a file called ``metadata.yaml`` that contains metadata about the theme. The theme manifest
is a simple text file in YAML format. The Dark Rainbow theme manifest looks like this, for example:

.. literalinclude:: ../../_themes/dark_rainbow/metadata.yaml
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

    .. note:: This parameter is not currently used and may be deprecated in the future.


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


.. _theme use_precompiled_styles:

``use_precompiled_styles`` *(optional)*
    Indicates whether to use precompiled stylesheets. Defaults to ``True``.

    .. seealso:: :ref:`theme styles`

    .. versionadded:: 0.5.0


.. _theme use_foundation:

``use_foundation`` *(optional)*
    Indicates whether the theme makes use of the Foundation CSS library included in Engineer. Defaults to ``False``.

    .. deprecated:: 0.6.0
       This setting is obsolete and ignored. Themes should now use


.. _theme use_jquery:

``use_jquery`` *(optional)*
    Indicates whether the theme makes use of the jQuery library included in Engineer. Defaults to ``False``.


.. _theme use_lesscss:

``use_lesscss`` *(optional)*
    Indicates whether the theme makes use of the LESS CSS library included in Engineer. Defaults to ``False``.


.. _theme use_modernizr:

``use_modernizr`` *(optional)*
    Indicates whether the theme makes use of the Modernizr library included in Engineer. Defaults to ``True``.

    .. versionchanged:: 0.5.0
       This setting now defaults to ``True`` instead of ``False``.


.. _theme use_normalize_css:

``use_normalize_css`` *(optional)*
    Indicates whether the theme makes use of the `normalize.css <http://necolas.github.io/normalize.css/>`_ file
    included in Engineer. Defaults to ``True``.

    .. versionadded:: 0.5.0


.. _theme use_tweet:

``use_tweet`` *(optional)*
    Indicates whether the theme makes use of the Tweet library included in Engineer. Defaults to ``False``.

    .. deprecated:: 0.5.0
       This setting is obsolete and ignored. The Tweet library has been removed from Engineer. See the
       :ref:`changelog` for more information.


.. _theme settings:

``settings`` *(optional)*
    A dictionary of all the themes-specific settings that users of your theme can provide via
    :attr:`~engineer.conf.EngineerConfiguration.THEME_SETTINGS` and their default values. If your theme supports
    custom settings, you **must** specify defaults. Due to the way Engineer loads your theme settings and a user's
    site settings, your settings may not be created at all unless you specify them here.

    .. versionadded:: 0.2.3

    .. seealso:: :ref:`use theme settings`


.. _theme template_dirs:

``template_dirs`` *(optional)*
    A list of paths, each relative to the path to the theme manifest file itself,
    that should be included when searching for theme templates. These paths are in addition to the ``templates``
    folder within the theme's folder itself, and will be searched in the order specified *after* the theme's
    ``templates`` folder.

    Like :ref:`copy_content<theme copy_content>`, this parameter is useful if you are creating multiple themes that
    share common templates. You can specify the paths to the common templates and they will be available during the
    build process.

    .. code-block:: yaml

        template_dirs:
          - '../_shared/templates/'

    .. versionadded:: 0.4.0


.. _theme copy_content:

``copy_content`` *(optional)*
    A list of paths to files or directories that should be copied to the theme's output location during a build. This
    is useful if you are creating multiple themes that all share some common static content (JavaScript files, images,
    etc.). By specifying this parameter, content will be copied to a central location for you during the build
    process so you can include it in your theme templates, LESS files, etc.

    .. tip::
        Since Engineer uses webassets to manage static content in version 0.6.0+, the ``copy_content`` setting should
        be used for content other than CSS and JavaScript files, such as images or web fonts. Style and script files
        should be managed using :ref:`webassets bundles <theme bundles>`.

    This parameter should be a 'list of lists.' Each entry in the list is a list itself containing two items. The
    first item is the path to the file or folder that should be copied. *This path should be relative to the location
    of the theme manifest.*

    The second parameter should be the target location for the file or folder. *The target path should be relative to
    the static/theme folder in the output folder.*

    For example, consider the following ``copy_content`` parameter in a theme manifest:

    .. code-block:: yaml

        copy_content:
          - ['../Font-Awesome-More/font', 'font']
          - ['../bootswatch/img/', 'img']
          - ['../bootstrap/js/', 'js']

    In this example, the ``../Font-Awesome-More/font`` (a path relative to the location of the theme manifest file
    itself) will be copied to ``static/theme/font``.

    .. versionadded:: 0.4.0


.. _theme styles:

Static Content
==============

Starting with Engineer version 0.6.0, theme static content is managed using
`webassets <http://webassets.readthedocs.org/>`_. While themes can link directly to static content in their
templates, using webassets is preferred. Webassets handles combining and minifying static content automatically.

.. versionadded:: 0.6.0


.. _theme bundles:

Bundles
-------

Webassets uses 'bundles' to combine and minify static files. Bundles are essentially a collection of static files, as
well as a set of filters that define what happens to the files (compiled to CSS/JS, minified, etc.), and an output
file location.

Engineer :ref:`includes some pre-defined bundles <theme included bundles>`, which you can use in addition to defining
your own. Bundles can include other bundles, so it's easy to include the pre-defined bundles into your own if you
wish. This also makes it easy to share common static content across multiple themes.

In order to define your own bundles for your theme, create a YAML file called ``bundles.yaml`` alongside your
:ref:`theme manifest`. This file should contain all the bundles used in your theme. Note that while webassets itself
supports defining bundles directly in Python code, Engineer currently only uses YAML input for custom theme bundles.

The bundle format itself is straightforward. As an example, this is the ``bundles.yaml`` file for the
:ref:`dark rainbow` theme:

.. literalinclude:: ../../_themes/dark_rainbow/bundles.yaml
   :language: yaml

Note that all the paths to files, both input and output, should be relative to the ``bundles.yaml`` file itself. Make
sure that your output file name includes the version placeholder (``%(version)s``) for cache-busting purposes. See
:ref:`webassets:expiry` for more details.

Also, keep in mind that while all of the filters supported by webassets are available for you to use in your bundles,
many of them require external dependencies that are not included in Engineer by default. If you don't wish to require
additional dependencies beyond what is included in Engineer, you should use only the ``cssmin``, ``jsmin``, and
``less`` filters. You can read more about all the webassets filters
:ref:`in the webassets documentation <webassets:builtin-filters>`.


.. _theme included bundles:

Included Bundles
~~~~~~~~~~~~~~~~

Engineer includes several CSS/JavaScript libraries that you can use in your themes. These libraries are exposed as
bundles. Simply add the appropriate bundle's name to the ``contents`` of your own bundle.

.. literalinclude:: ../../static/engineer/lib/global_bundles.yaml
   :language: yaml


Stylesheets
-----------

In addition to CSS, Engineer can automatically compile LESS stylesheets during a site build,
so you are free to use LESS rather than CSS for your styles. When linking to your LESS stylesheet in your templates,
you should use the ``render_less_link`` :ref:`macro <macros>`. This will ensure that the stylesheet is compiled as
part of the site build process if needed.

Starting with Engineer 0.5.0, themes can include a 'precompiled' version of the LESS stylesheets they need. This is
useful since in most cases users of your theme will not be making modifications to your LESS files. Thus,
referencing a pre-built version of the stylesheet makes for faster builds.

In order to include a precompiled version of your stylesheets, simply add it alongside your regular stylesheet and
append ``_precompiled`` to the name. For example, if your stylesheet is called ``dark_rainbow.less``,
then your precompiled version should be called ``dark_rainbow_precompiled.css``. As long as you are referencing your
stylesheet from your templates using the ``render_less_link`` :ref:`macro <macros>`,
the precompiled version will automatically be picked up during a site build. No other changes are needed.


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


.. _image template:

Images
------

The built-in ``img`` function will output content using a template fragment at :file:`templates/theme/_img.html`.
Individual themes can override this output by providing their own custom template.

The template is always passed the following keyword variables:

- source
- classes
- width
- height
- title
- alt
- link

All except the ``source`` parameter are optional so the template should handle these cases appropriately. The default
template looks like this:

.. literalinclude:: ../../_templates/theme/_img.html
   :language: html+jinja

.. seealso::
   :ref:`post images`

.. versionadded:: 0.5.0


Sitemap Templates
-----------------

Themes can provide custom templates for sitemap, just as :ref:`individual sites can <sitemap template>`.
These templates should be in the theme's :file:`templates/theme` folder.

.. versionadded:: 0.3.0


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

You may wish instead to deliver your theme as an installable Python package. This allows users to download and install
your theme via ``pip`` or any other tool. See :ref:`theme plugins` for more details.


Add Your Theme to Engineer
--------------------------

If you'd like to make your theme available with the main Engineer application, send a pull request on github.
