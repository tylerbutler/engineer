
.. _bundled plugins:

================
Included Plugins
================

Engineer includes a few optional plugins you can use to further customize its behavior. If you have an idea for your
own plugin, you might consider :ref:`creating it yourself<plugins>`.


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

This metadata map tells Engineer to finalize timestamps *only* for published posts and normalizes titles
and slugs for all posts. You can override this default map by providing your own map in your own
:ref:`settings file<settings>`. In addition, you can turn metadata normalization on and off
completely using the :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA`
setting.

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

      A mapping of post metadata values to the post statuses in which they'll be finalized. By default,
      Engineer will finalize timestamps *only* for published posts and normalizes titles and slugs for all posts.

      .. seealso::
         :ref:`metadata finalization`, :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA`


.. versionadded:: 0.4.0
   In version 0.4.0, the old post normalization process has been superceded by the
   :ref:`metadata finalization` and :ref:`post renamer plugin` plugins.


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

The Post Renamer plugin is enabled by default, and can be disabled by setting the ``POST_RENAME_ENABLED`` setting to
false. When enabled, the plugin uses the ``POST_RENAME_CONFIG`` setting to determine how to rename files. This
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
