
.. _bundled plugins:

================
Included Plugins
================

Engineer includes a few optional plugins you can use to further customize its behavior. If you have an idea for your
own plugin, you might consider :ref:`creating it yourself<plugins>`.

.. note::
   Some plugin capabilities require you to explicitly give the plugin :ref:`special permissions<plugin permissions>`.
   Check the plugin's documentation to see if this is the case. The plugin permissions system is new to
   Engineer 0.5.0.


.. _metadata finalization:

Metadata Finalization
=====================

Engineer will automatically fill in pieces of metadata about your posts
during the build process, and this plugin can also 'finalize' some of that
metadata and write it back to your post file.

For example, if you have a post that you just wrote and are
ready to publish, you likely want Engineer to use the current date/time as the
timestamp for the post. However, in order to ensure future build processes know the right
publish time for that post, the metadata needs to be in the file itself, so Engineer
will automatically add ``timestamp: <current date/time>`` to your post file when
it builds the site.

On the other hand, you might have a post that is in review or draft form, and you're
building the site to preview it. In that case, you *don't* want the timestamp to be added to
the file.

Settings
--------

The finalization process is customizable. The :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA_CONFIG`
setting defines which metadata settings are finalized and what posts (based on their status)
the finalization process applies to. For example, the default ``FINALIZE_METADATA_CONFIG``
looks like this:

.. code-block:: yaml

    FINALIZE_METADATA_CONFIG:
      timestamp:
        - published
      title:
        - published
        - review
        - draft
      slug:
        - published
        - review
        - draft
      url:
        - published
        - review

This metadata map tells Engineer to finalize timestamps *only* for published posts and normalizes titles
and slugs for all posts. You can override this default map by providing your own map in your own
:ref:`settings file<settings>`. In addition, you can turn metadata normalization on and off
completely using the :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA`
setting.

.. note::
   Metadata that already exists in post files will always be maintained regardless of this setting. For example,
   if you are using the default settings but have a draft post that already has a ``url`` value,
   that metadata will be maintained in the output file, even though URLs will not be set for drafts in general.

.. currentmodule:: engineer.conf

.. class:: EngineerConfiguration

   .. attribute:: FINALIZE_METADATA

      **Default:** ``True``

      Turns :ref:`metadata finalization` on and off.

      .. seealso::
         :ref:`metadata finalization`, :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA_CONFIG`


   .. attribute:: FINALIZE_METADATA_CONFIG

      **Default:**

      .. code-block:: yaml

          FINALIZE_METADATA_CONFIG:
            timestamp:
              - published
            title:
              - published
              - review
              - draft
            slug:
              - published
              - review
              - draft
            url:
              - published
              - review

      A mapping of post metadata values to the post statuses in which they'll be finalized. By default,
      Engineer will finalize timestamps *only* for published posts and normalizes titles and slugs for all posts.

      .. seealso::
         :ref:`metadata finalization`, :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA`


   .. attribute:: METADATA_FORMAT

      **Default:** ``'input'``

      Specifies which metadata format to output. As of version 0.5.0, this only controls whether or not to force
      :ref:`fencing`. When set to the default, ``'input'``, the finalized metadata format will match that of the
      input.

      Other valid values for this setting are:

      ``'fenced'``
          Always output the metadata as fenced.

      ``'unfenced'``
          Always output the metadata as unfenced.

.. versionadded:: 0.4.0
   In version 0.4.0, the old post normalization process has been superceded by the
   :ref:`metadata finalization` and :ref:`post renamer plugin` plugins.

.. versionchanged:: 0.5.0
   Added the :attr:`~engineer.conf.EngineerConfiguration.METADATA_FORMAT` setting.


.. _post breaks plugin:

Post Breaks/Excerpts/Teasers
============================

If you wish to show only an excerpt of a post on a rollup page, you can insert a break marker into your post content
and Engineer will break it up for you.

Engineer supports Octopress-style ``<!--more-->`` post breaks in addition to the simpler ``-- more --``. Use
whichever one you wish. Only the first section of the post, before the 'more' break marker,
will be displayed on a rollup page.

By default the RSS feed that Engineer generates will only include teaser content. However,
you can override this and make your feed full content by setting the ``FEED_FULL_CONTENT`` setting to true in your
Engineer settings file.

The Post Breaks plugin does not need to be activated in any way; it always runs but has no effect on posts that don't
include a break marker.

.. versionadded:: 0.3.0

.. versionchanged:: 0.4.0
   Added the ``FEED_FULL_CONTENT`` setting.

.. seealso:: :ref:`compatibility`


.. _post renamer plugin:

Post Renamer
============

It can be handy when your post source files have names that tell you a little about the post itself. While you can
obviously name post files whatever you like, Engineer can automatically rename your files during the build process to
help keep things organized. When combined with :ref:`metadata finalization`, Engineer can do a lot of heavy lifting
to keep your posts organized and easy to manage.

The Post Renamer plugin is disabled by default, and can be enabled by setting the ``POST_RENAME_ENABLED`` setting to
true. When enabled, the plugin uses the ``POST_RENAME_CONFIG`` setting to determine how to rename files. This
configuration setting is similar in form to the :attr:`~engineer.conf.EngineerConfiguration.PERMALINK_STYLE`
setting, and specifies a mapping of :ref:`post status<post status>` to a rename format string.

For example, the default ``POST_RENAME_CONFIG`` setting is:

.. code-block:: yaml

    POST_RENAME_CONFIG:
      draft: '({status}) {slug}.md'
      review: '({status}) {year}-{month}-{day} {slug}.md'
      published: '({status_short}) {year}-{month}-{day} {slug}.md'

With this configuration, a draft post with the title "Welcome to Engineer" would be renamed to
``(draft) welcome-to-engineer.md``. The format strings should follow standard
`Python string formatting <http://docs.python.org/library/string.html#format-specification-mini-language>`_ rules.
The following named parameters are available for you to use in your format string:

``year``
    The year portion of the post's timestamp as an integer.

``month``
    The month portion of the post's timestamp as string - includes a leading zero if needed.

``day``
    The day portion of the post's timestamp as a string - includes a leading zero if needed.

``i_month``
    The month portion of the post's timestamp as an integer.

``i_day``
    The day portion of the post's timestamp as an integer.

``slug``
    The post's slug.

``status``
    The post's status as a string (e.g. ``draft``).

``status_short``
    The post's status in a short form (e.g. ``d`` for ``draft``, ``p`` for ``published``, etc.).

``timestamp``
    The post's timestamp as a datetime.

``post``
    The post object itself.

If you wish for posts of a certain status to not be renamed at all, simply use a ``~`` ( tilde - YAML's equivalent to
``None`` or null) in your ``POST_RENAME_CONFIG`` setting. For example, the following setting will not rename draft
and review posts, but will rename published posts according to the default configuration:

.. code-block:: yaml

    POST_RENAME_CONFIG:
      draft: ~
      review: ~

.. versionadded:: 0.4.0
   In version 0.4.0, the old post normalization process has been superceded by the
   :ref:`metadata finalization` and :ref:`post renamer plugin` plugins.

.. versionchanged:: 0.4.2
   The plugin is now disabled by default. Renaming post files caused confusion and headaches for new Engineer users.


.. _global links plugin:

Global/Shared Links
===================

If you find yourself often inserting the same links in your posts, you might benefit from using the Global Links
plugin. Using this plugin, you can create a list of common links and store them in a file along with your site
settings. You can reference these links in any post; they are always available to all posts.

.. versionadded:: 0.5.0

Usage
-----

Activating the Plugin
~~~~~~~~~~~~~~~~~~~~~

In order to use global links, you first need to do two things:

1. Create a file to store the links. This file can be anywhere, but it is generally easiest to put it alongside your
   site's :ref:`settings file(s)<settings>`. The convention is to call the file ``global_links.md`` but this is by no
   means required.
2. Set the ``GLOBAL_LINKS_FILE`` setting in your settings file. It should be set to the path of your global
   links file. It can either be an absolute path, or a path *relative to the location of the settings file.*

Once you have done this, the links in the file you created in step 1 will be available to all posts.


Adding Links
~~~~~~~~~~~~

The Global Links plugin utilizes a feature in Markdown called '`reference-style links`_'. Reference-style links look
like this:

.. code-block:: text

   This is an example of a [reference-style link][rsl]. You can also use implicit link names like [Google][] if you
   prefer.

   [rsl]: http://daringfireball.net/projects/markdown/syntax#link
   [Google]: http://www.google.com

As you can see, reference-style links allow you to link to things using definitions defined later in the Markdown
document. The Global Links plugin simply takes advantage of this. If you put the following in your
``GLOBAL_LINKS_FILE``, it will be available to all posts:

.. code-block:: text

   [rsl]: http://daringfireball.net/projects/markdown/syntax#link
   [Google]: http://www.google.com

Then you can write your posts and reference the links defined in your ``GLOBAL_LINKS_FILE``.

.. tip::
   The Global Links plugin isn't limited to just links. You can also put `abbreviations`_ or even `footnotes`_
   (though I can't think of any reason why you'd want to use 'global footnotes'), in your ``GLOBAL_LINKS_FILE``,
   and it will be available to your posts.

.. _`reference-style links`: http://daringfireball.net/projects/markdown/syntax#link
.. _`abbreviations`: http://packages.python.org/Markdown/extensions/abbreviations.html
.. _`footnotes`: http://packages.python.org/Markdown/extensions/footnotes.html


.. _lazy links plugin:

Markdown Lazy Links
===================

This plugin allows you to use 'lazy links' in your posts. The idea comes from Brett Terpstra,
and more detail is available at `<http://brettterpstra.com/2013/10/19/lazy-markdown-reference-links/>`_. Unlike
Brett's sample implementation, the Engineer plugin supports adding lazy links to posts that already have numeric
reference links.

.. versionadded:: 0.5.0

Usage
-----

The lazy links plugin is enabled by default, so you can start using them without any configuration changes.

By default, the lazy links are handled each time a build is run. In other words, the lazy links are transformed into
numeric reference-style links each time; the links stay lazy in the original source post. If you wish to transform
the lazy links into real numeric reference-style links in the source post files as part of a build,
you'll need to tweak a few settings:

1. Ensure the :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA` setting is enabled.
2. Set the ``LAZY_LINKS_PERSIST`` setting to ``True`` in your configuration file.
3. Give ``engineer.plugins.bundled.LazyMarkdownLinksPlugin`` the ``MODIFY_RAW_POST`` permission.

   .. seealso:: :ref:`plugin permissions`

A sample Engineer configuration file might look like this:

.. code-block:: yaml

   FINALIZE_METADATA: yes
   LAZY_LINKS_PERSIST: yes

   PLUGIN_PERMISSIONS:
     MODIFY_RAW_POST:
     - engineer.plugins.bundled.LazyMarkdownLinksPlugin


.. _jinja post processor plugin:

Jinja Post Processor Plugin
===========================

This plugin runs your post content through the Jinja template engine prior to tranforming it into HTML. This allows
you to use Jinja filters, variables, and other content in your posts. For example, this plugin lets you use the
handy :ref:`img<post images>` Jinja filter to insert images into your posts consistently.

.. versionadded:: 0.5.0

Usage
-----

The Jinja Post Processor plugin is enabled by default. If you wish to disable it,
you can set the ``JINJA_POSTPROCESSOR_ENABLED`` setting to ``False`` in your configuration file. Keep in mind that
disabling the plugin will cause some built-in Engineer features such as the :ref:`img filter<post images>` to not work.
