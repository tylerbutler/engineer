
============
Introduction
============

Overview
========

At its core, Engineer is a static website generator. In other words, Engineer let's you build a website from a bunch
of files - articles written in Markdown, templates, and other stuff - and outputs *another* bunch of files - HTML,
mostly - that you can then copy wherever you want.

Engineer was inspired by `Brent Simmons`_, Marco Arment's `Second Crack`_, `Jekyll`_, `Octopress`_, and `Hyde`_.

.. Links
.. _timeago.js: http://timeago.yarp.com/
.. _Jinja 2: http://jinja.pocoo.org
.. _Brent Simmons: http://inessential.com/2011/03/16/a_plea_for_baked_weblogs
.. _Second Crack: https://github.com/marcoarment/secondcrack
.. _Jekyll: http://jekyllrb.com/
.. _Octopress: http://octopress.org/
.. _Hyde: http://hyde.github.com/


.. _features:

Features
========

**Write posts from anywhere**

    Posts can be written/edited in Markdown and stored/synchronized using Dropbox or another file synchronization
    solution.

**Preview your site locally**

    Engineer includes a small :ref:`development web server <engineer serve>` that you can use to preview your site
    locally without deploying anywhere.

**Manage your site remotely**

    Even baked sites need a little management, and many existing static generators require you to load up the
    terminal and execute a command to rebuild your site. Engineer lets you :doc:`do that<cmdline>` of course,
    but also provides :doc:`Emma <emma>`, a built-in mini management site (optional) that lets you
    do most of the common management tasks remotely.

**Themes make it easy to change your site's appearance**

    Themes provide flexibility in the site look and feel without starting from scratch or rewriting a bunch of
    content. You can write your own :doc:`themes` as well.

**Use LESS instead of CSS**

    Engineer lets you use LESS instead of CSS if you'd like. LESS can either be preprocessed on the server (requires
    that lessc be installed on non-Windows systems) or processed client-side using less.js.

**It's fast**

    Engineer outputs content quickly (and I'm working to make it *even faster*), and because the output content is
    completely static, it is blazingly fast to serve, scales up very well, and is completely independent of any
    specific web server or technology. Once generated, you can copy your site *anywhere* and use any web server you
    like. In addition, Engineer can optimize your JavaScript and CSS/LESS to minimize their size. Engineer is all
    about speed.


.. _caveats:

Caveats
=======

Despite all of these great features, there are some things that you might *not* like:

**No built-in search**

    Search isn't built in. You can configure Google site search or something, but it's not baked into Engineer. But...
    do people really use anything besides Google/Bing to find stuff anyway?

**Dynamic things require a bit more work**

    Static sites can feel limited if you're accustomed to doing something super-dynamic every time a page is loaded.
    Most of these things can be handled using either client-side JavaScript (e.g. `timeago.js`_) or clever uses of
    the Jinja 2 template system (see the navigation highlighting functionality in Engineer itself for an example of
    things that can be done).

**Might not fit your site's needs**

    If you have a lot of one-off pages (:ref:`template pages` or other such things) then managing them can get a bit
    cumbersome. Engineer really excels when a majority of your site's content has a similar look and feel and you can
    leverage the :ref:`post metadata` for a majority of your content. Engineer isn't limited to blogs, per se,
    but it does make some assumptions that most of your content comes in the form of articles.

**Only supports Markdown and Jinja 2**

    While ideally this will not always be true, currently Engineer requires your posts be written in Markdown and any
    templates you create be written in `Jinja 2`_. This may change in the future, but for now you have to use those
    two languages.

**Engineer is not a CMS**

    If you're looking for a full-blown content management system, then... keep looking. Engineer is decidedly not what
    you want. Engineer operates on the basic principle that your content is stored in text files with minimal
    metadata in the files themselves, so if you're looking for rich URL management, image/file manipulation
    capabilities, etc., Engineer will make you very sad. It's not designed to do that stuff.


Components
==========

:program:`engineer`

    Engineer is primarily controlled by a command-line program aptly called :ref:`engineer <engineer>`. It's used to
    build sites, configure :doc:`Emma <emma>`, start the :ref:`development server <engineer serve>`, etc.

**Theme Infrastructure**

    Engineer exposes a basic infrastructure and API that lets you create your own themes or use themes that others
    have created.

**Plugin Architecture**

    Engineer provides a set of :ref:`bundled plugins` plus a way to :ref:`create your own<plugins>`.

Requirements and Dependencies
=============================

Engineer requires Python 2.7+ and runs on Linux (Ubuntu and CentOS have been tested) and Windows. Chances are it will
run on most platforms that Python and the Python packages Engineer depend on support,
though exhaustive tests have not been run.

Engineer *has not* been tested on Python 3, and almost certainly will not work as-is since I have been a bit sloppy in
my use of Python constructs that are deprecated in Python 3.

All relevant dependencies except Python itself will be installed when you :doc:`install Engineer <installation>`. The
complete set of packages Engineer depends on is as follows:

* path.py
* markdown
* pyYAML
* flufl.enum
* translitcodec
* jinja2
* compressinja
* pygments
* html5lib
* python-dateutil
* zope.cachedescriptors
* humanize
* bottle
* pytz
* times
* cssmin
* lpjsmin
* typogrify-engineer
