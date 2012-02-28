.. documentation master file, created by
.. sphinx-quickstart on Mon Oct 24 17:35:56 2011.
.. You can adapt this file completely to your liking, but it should at least
.. contain the root `toctree` directive.

======================
Engineer Documentation
======================

.. toctree::
   :maxdepth: 3

   quickstart
   usage

What is Engineer?
=================

At its core, engineer is a static website generator. In other words,
engineer let's you build a website from a bunch of files - articles written
in Markdown, templates, and other stuff - and outputs *another* bunch
of files - HTML, mostly - that you can then copy wherever you want.

Features
--------

- Posts can be written/edited in Markdown and stored/synchronized using Dropbox.
- Themes provide flexibility in the site look and feel without starting from
  scratch or rewriting a bunch of content.
- Built-in mini management site (optional) allows you to manage your site
  remotely.
- Regenerate your site remotely with just a click of a button using the
  Bookmarklet of Awesomeness.
- Output content is completely static and thus is blazingly fast to serve,
  scales up very well, and is completely independent of any specific web
  server or technology. Once generated, you can copy your site
  *anywhere* and use any web server you like.

Despite all of these great features, there are some things that you might not
like:

- Search isn't built in. You can configure Google site search (and the
  built-in themes do this), but it's not baked into Engineer. But... do
  people really use anything besides Google/Bing to find stuff anyway?
- Static sites can feel limited if you're used to doing something
  super-dynamic every time a page is loaded. Most of these things can be
  handled using either client-side JavaScript (e.g. `timeago.js`_)
  or clever uses of the Jinja 2 template system (see the navigation
  highlighting functionality in Engineer itself for an example of things
  that can be done).

.. Links

.. _timeago.js: http://timeago.yarp.com/
.. _A Plea for Baked Weblogs: http://inessential.com/2011/03/16/a_plea_for_baked_weblogs


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

