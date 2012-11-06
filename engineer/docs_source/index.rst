
=========================================================
Engineer: A Static Website Generator for Fellow Engineers
=========================================================

.. sidebar:: What's New in Version |release|?

   * Custom URL and permalink schemes
   * Comments integration using Disqus or IntenseDebate
   * Big changes to metadata normalization and automated file renaming

   There's more! See the full :ref:`changelog` for details.


At its core, Engineer is a static website generator. In other words, Engineer let's you build a website from a bunch
of files - articles written in Markdown, templates, and other stuff - and outputs *another* bunch of files - HTML,
mostly - that you can then copy wherever you want. It has some very nice :ref:`features` that will make you happy,
but it's :ref:`not for everybody <caveats>`.

Engineer was inspired by `Brent Simmons`_, Marco Arment's `Second Crack`_, `Jekyll`_, `Octopress`_, and `Hyde`_.

.. note::
   The Engineer documentation is a work in progress. It is by-and-large up-to-date and the most relevant
   sections are complete, but some of the more 'advanced' sections are not yet complete.

.. Links
.. _Brent Simmons: http://inessential.com/2011/03/16/a_plea_for_baked_weblogs
.. _Second Crack: https://github.com/marcoarment/secondcrack
.. _Jekyll: http://jekyllrb.com/
.. _Octopress: http://octopress.org/
.. _Hyde: http://hyde.github.com/


Bugs and Feature Roadmap
========================

If you find any bugs in Engineer please file an issue in the Github
`issue tracker <https://github.com/tylerbutler/engineer/issues>`_ (or fork and fix it yourself
and send me a pull request). Feature ideas and other feedback are welcome as well!


Narrative Documentation
=======================

.. toctree::
   :maxdepth: 3

   intro
   installation
   tutorial
   settings
   posts
   themes
   templates
   bundled_plugins
   cmdline
   emma
   compatibility
   faq
   changelog


Developer Documentation
=======================

.. toctree::
   :maxdepth: 2

   dev/pipeline
   dev/theme_creation
   dev/plugins
   dev/macros


API Documentation
=================

.. toctree::
   :maxdepth: 2
   :glob:

   api/*


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

