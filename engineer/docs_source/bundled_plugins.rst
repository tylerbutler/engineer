
================
Included Plugins
================

Engineer includes a few optional plugins you can use to further customize its behavior. If you have an idea for your
own plugin, you might consider :ref:`creating it yourself<plugins>`.


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
