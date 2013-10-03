
.. _changelog:

=========
Changelog
=========

version 0.4.5 - October 2, 2013
===============================

- Update to a new version of typogrify-engineer. Due to changes in the original typogrify package as well as in pip
  installer behavior, Engineer was failing to install properly from PyPI for new users.


version 0.4.4 - June 23, 2013
=================================

- Addresses compatibility issue with more recent versions of html5lib
  (`issue 63 <https://github.com/tylerbutler/engineer/issues/63>`_). A more comprehensive fix will come in a
  future version.


version 0.4.3 - December 10, 2012
=================================

- Fixes `issue 42 <https://github.com/tylerbutler/engineer/issues/42>`_ which managed to sneak into 0.4.2,
  causing an exception to be thrown for some configurations.


version 0.4.2 - December 10, 2012
=================================

.. note:: Engineer no longer requires the ``zope.cachedescriptors`` and ``compressinja`` packages. You can uninstall
   these packages if you wish. If you're using pip, simply type::

       pip uninstall zope.cachedescriptors compressinja

- The :ref:`post renamer plugin` plugin is no longer on by default.

  .. important:: If you wish Engineer to behave the way it did previously, simply set the ``POST_RENAME_ENABLED``
     setting to true in you Engineer settings file.

- Fixes `issue #36 <https://github.com/tylerbutler/engineer/issues/36>`_ which caused cache corruption on Mac OS X
  Lion.
- Fixes `issue #39 <https://github.com/tylerbutler/engineer/pull/39>`_ which prevented the debug server from working
  properly on non-Windows operating systems.


version 0.4.1 - December 4, 2012
================================

- :ref:`Finalization plugin<metadata finalization>`: No longer writes files if their metadata has not changed. This
  should prevent a rather annoying behavior where post files would always be modified during a build regardless if
  they had changed or not. This broke sorting the post files by 'last modified time', among other things.
- Fixes issues with automatic version handling.


version 0.4.0 - November 28, 2012
=================================

- Added support for custom URL/permalink schemes with the :attr:`~engineer.conf.EngineerConfiguration.PERMALINK_STYLE`
  setting.

  .. important:: Note that while the default has not changed in this release, it will in 0.5.0,
     so if you wish to continue to use the current Engineer URL scheme, you should update your settings
     files now.

- Broad changes to post and metadata normalization. These features have been broken out into two separate plugins,
  the :ref:`metadata finalization` plugin and the :ref:`post renamer plugin`. Accordingly, the
  settings :attr:`~engineer.conf.EngineerConfiguration.NORMALIZE_INPUT_FILES`
  and :attr:`~engineer.conf.EngineerConfiguration.NORMALIZE_INPUT_FILE_MASK` have been deprecated. See the
  documentation for the two new plugins for more details.
- The :ref:`dark rainbow` and :ref:`oleb` themes can now support comments using either
  `Disqus <http://www.disqus.com/>`_ or `Intense Debate <https//intensedebate.com/>`_.
- The :ref:`dark rainbow` and :ref:`oleb` themes now support simple site search using Google.
- Added the :attr:`~engineer.conf.EngineerConfiguration.ACTIVE_NAV_CLASS` setting to enable users to change the class
  that is applied to active navigation nodes. This should make it easier to integrate with CSS frameworks that use a
  different class name.
- Theme creators can now more easily share content between several themes using the
  :ref:`copy_content<theme copy_content>` and :ref:`template dirs<theme template_dirs>` theme manifest settings.
- The :ref:`post breaks plugin<post breaks plugin>` now outputs only the teaser content into the site RSS feed by
  default. This behavior can be changed using the ``FEED_FULL_CONTENT`` setting.
- Added a new :class:`~engineer.plugins.CommandPlugin` class. This enables other developers to write plugins that add
  new command line commands to Engineer.
- Standardized a set of common classmethods that are available to all plugins - ``handle_settings`` and
  ``get_logger``.
- Updated bundled less.js to version 1.3.1.
- Lots of bug fixes.


version 0.3.2 - August 18, 2012
===============================

- Fixes a bug in the Markdown filter (used in :ref:`template pages`) that caused incorrect Markdown processing if
  there is leading white space in the Markdown content.
- Add table styles to included themes.


version 0.3.1 - August 5, 2012
==============================

- Fixes a rather nasty bug that would cause a fatal exception if there were non-ASCII characters in a post using
  the :ref:`teaser content` (post breaks) support that was added in version 0.3.0.
- Minor style fixes to Dark Rainbow theme.


version 0.3.0 - July 22, 2012
=============================

.. important::
   The :ref:`theme plugin model <theme plugins>` has changed with version 0.3.0. Installable themes will need to be
   changed to be compatible with the new model.

- A new :ref:`plugin model <plugins>` provides a more flexible way to integrate with Engineer.
- Posts can now have :ref:`custom metadata <post custom properties>`.
- New :ref:`teaser content` (post breaks) support.
- A sitemap is now generated automatically.
- A custom RSS feed url can be specified using the :attr:`~engineer.conf.EngineerConfiguration.FEED_URL` setting.
- Both :ref:`dark rainbow` and :ref:`oleb` now include next/previous post links.
- Site-relative URLs for posts are now included in the post metadata during post normalization. This is useful
  in some cases where you need to know the URL of a post (for example, to link to it in another post) but are offline
  or otherwise unable to get the URL. If you put a manual URL in the post metadata,
  it will be overwritten - it's not used to actually allocate a URL for the post.
- Post metadata now accepts either ``via-link`` or ``via_link``. Normalized metadata will now use ``via-link`` instead
  of ``via_link`` since the former feels more natural in YAML.
- The build process will now output a warning if there are pending posts in the site and
  :attr:`~engineer.conf.EngineerConfiguration.PUBLISH_PENDING` is ``False``. This should help remind users that
  don't run a build automatically that they will need to run another build at a later date/time if they want the
  pending post to actually become visible.
- Bundled libraries updated:

  - LESS: version 1.3.0
  - jQuery: version 1.7.1
  - modernizr: version 2.5.3

- Themes can now indicate whether they use the bundled Tweet library by setting the :ref:`use_tweet <theme use_tweet>`
  property.
- Fixed bug preventing some :ref:`template fragments` from being included properly in some themes.
- The included :ref:`Development server <engineer serve>` no longer restricts requests to those coming from the same
  machine.
- Various build performance enhancements.
- Several fixes to bundled theme styles, including better mobile styles in Dark Rainbow.


version 0.2.4 - May 27, 2012
============================

- A new theme, :ref:`oleb`, has been added. This theme is based on Ole Begemann's oleb.net design and was created with
  his permission.
- During rendering, a new variable called ``all_posts`` is passed. It is a :class:`~engineer.models.PostCollection`
  containing all the posts on the site and can be used to display links to related posts, similarly tagged posts, etc.
- Themes can now be wrapped in a Python package, installed, and register themselves as a
  :ref:`theme plugin <theme plugins>`.
- Bug fixes related to sites hosted at non-root paths.


version 0.2.3 - May 6, 2012
===========================

- External themes are now supported. You can place your custom theme either inside a :file:`themes` directory in your
  site's root directory or in any directory you'd like using the
  :attr:`~engineer.conf.EngineerConfiguration.THEME_DIRS` setting.
- Themes can now specify :ref:`settings defaults <theme settings>` in their manifest.
- :ref:`Zipped themes <zipping themes>` are now supported.
- Multiple :option:`verbosity levels <engineer -v>` are supported by the command line script now.
- :ref:`engineer serve` now supports a :option:`--port <serve -p>` option.
- Build logs are now always written to a ``build.log`` file in the ``logs`` directory.
- CSS/JS compression process is now more efficient.
- Miscellaneous logging and cache fixes.


version 0.2.2 - April 30, 2012
==============================

- Updated sample site to disable :attr:`~engineer.conf.EngineerConfiguration.PREPROCESS_LESS` by default. This way
  the site will still build even if you don't have lessc installed or aren't on Windows.


version 0.2.1 - April 28, 2012
==============================

- Fixed corrupted LESS files that made it into v0.2.0.
- Fixed bug that prevented attribution text and links from showing up in Dark Rainbow theme.


version 0.2.0 - April 22, 2012
==============================

- Better post timezone handling.
- Various fixes to Dark Rainbow theme.
- Various fixes to the post cache mechanisms.
- Preprocessing support for LESS.
- Minification support for JS and CSS static files.
- New commands - 'clean' and 'init'.
- Major documentation improvements. (In other words, there is now documentation.)


version 0.1.0 - March 13, 2012
==============================

- Initial release.
