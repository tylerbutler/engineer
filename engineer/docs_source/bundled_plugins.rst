
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


.. versionchanged:: 0.4.0
   Prior to version 0.4.0, this process also renamed files and was far less customizable. In versions
   0.4.0+, post files will no longer be renamed by this plugin and it can be easily disabled with the
   :attr:`~engineer.conf.EngineerConfiguration.FINALIZE_METADATA`setting.


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

.. seealso:: :ref:`compatibility`
