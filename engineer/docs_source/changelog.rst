
=========
Changelog
=========

version 0.2.3 - May 6, 2012
===========================

- External themes are now supported. You can place your custom theme either inside a :file:`themes` directory in your
  site's root directory or in any directory you'd like using the
  :attr:`~engineer.conf.EngineerConfiguration.THEME_DIRS` setting.
- Themes can now specify :ref:`settings defaults <theme default>` in their manifest.
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
