
.. _posts:

=====
Posts
=====

.. currentmodule:: engineer.conf

Posts are the bread and butter of an Engineer site. Posts are Markdown files with either a ``.md`` or ``.markdown``
file extension and are structured like this:

.. literalinclude:: ../sample_site/posts/(p)2012-03-09-what-s-next.md
   :language: yaml

Posts are typically stored in a folder called :file:`posts` within your site's source directory,
but you can put them anywhere - even in multiple folders - by changing the :attr:`~EngineerConfiguration.POST_DIR`
setting.

Everything above the ``---`` is :ref:`post metadata`, and everything below it
is the post itself (in Markdown, of course).

.. _post metadata:

Metadata
========

Posts should contain some metadata that tells Engineer about the post. This
metadata must be in `YAML format <http://pyyaml.org/wiki/PyYAMLDocumentation#YAMLsyntax>`_,
and must be the first thing in your post file. The YAML document separator
(``---``) separates the post content and metadata.

None of the metadata is strictly *required* since there are defaults for everything but you must have at least one
piece of metadata in your post file.

.. versionchanged:: 0.3.0
   The metadata can now have a YAML document separator (``---``) above it as well as below it. This format is used by
   Jekyll, and by extension, Octopress, so posts written for those systems will migrate to Engineer without problems.

   .. seealso:: :ref:`compatibility`

Metadata Parameters
-------------------

.. _post title:

``title``
    The title of the post. If you don't provide this, engineer will try to
    generate one based on the name of your post file,
    replacing any dashes or underscores in the file name with spaces. For
    example, if your post file is named ``A-Day-In-the-Life.md``,
    Engineer will set the post title to 'A Day In the Life' unless you
    explicitly define a ``title`` in the post metadata.


.. _post timestamp:

``timestamp``
    The date and time that the post is/was published. The format of the date
    and time has pretty loose requirements, but in general it's best to follow
    this basic format: ``2012-03-21 13:43:04``. The timestamp can be a future
    time, in which case the post will not become published until that time. If
    you don't provide an explicit timestamp, Engineer will set it to the date
    and time that the site is next built.

    .. note::

       Unless you specifically provide a timezone offset in your ``timestamp``
       value, the time will be assumed to be in the same time zone as your
       :attr:`~engineer.conf.EngineerConfiguration.POST_TIMEZONE` setting.

    .. seealso:: :ref:`timezones`


.. _post status:

``status``
    The status of the post. Valid values are:

    :attr:`~engineer.models.Status.draft`
        Draft posts are never output when a site is built. Status always defaults to
        :attr:`~engineer.models.Status.draft` if it's missing or set to an unknown
        value to avoid accidentally publishing something that wasn't meant to be published.

    :attr:`~engineer.models.Status.published`
        Published posts are always output when a site is built *unless* they have a
        :ref:`timestamp <post timestamp>` in the future, in which case they are not output.
        This behavior can be customized using the
        :attr:`~engineer.conf.EngineerConfiguration.PUBLISH_PENDING` setting.

    :attr:`~engineer.models.Status.review`
        Posts marked ``review`` are only output if the setting
        :attr:`~engineer.conf.EngineerConfiguration.PUBLISH_REVIEW` is set to true.

        .. versionadded:: 0.3.0

    .. seealso:: :attr:`~engineer.conf.EngineerConfiguration.PUBLISH_DRAFTS`,
       :attr:`~engineer.conf.EngineerConfiguration.PUBLISH_PENDING`,
       :attr:`~engineer.conf.EngineerConfiguration.PUBLISH_REVIEW`


.. _post slug:

``slug``
    You can set an explicit slug for the post. The slug represents the URL for
    your post and thus should only contain URL-safe characters. If not set,
    Engineer will generate a slug for you based on the name of your page.
    In general the only time you'll need or want to consider
    manually setting this is if you have multiple posts with the same name
    (and published on the same day), which Engineer cannot currently handle on
    its own.


.. _post tags:

``tags``
    A list of tags to be applied to the post. Completely optional. Tags will
    be used to generate tag pages - pages with all of the posts tagged with
    a specific tag listed. You can specify a single tag or multiple tags.
    If you specify multiple tags, they must be YAML list format.


.. _post link:

``link``
    If the post has an associated external link, the main post title on the
    site and in the RSS feed will link to the external link instead of the
    permalink to the post on your site. This method of linking was
    popularized by John Gruber on http://daringfireball.net.


.. _post via:

``via``
    If you're including an external link, you might also want to provide some
    attribution to the person or site that helped you find the link. In this
    case, you can provide the ``via`` metadata property. It should be a
    string - the name of the person or site that you want to credit.


.. _post via-link:

``via-link``
    If you want to link to a different URL as part of your attribution, you
    can provide an optional link to the blog or individual's personal site
    (or perhaps the article that linked you to the external link originally).
    Exactly how this attribution metadata is used in the site depends on the
    theme.

    .. versionchanged:: 0.3.0
       Prior to version 0.3.0, this property was ``via_link``. Both forms of
       the property are supported in version 0.3.0+.


.. _post normalization:

Metadata Normalization
----------------------

By default, Engineer normalizes your post metadata when it builds your site.
This process rewrites the metadata, filling in any of the 'canonical'
properties with default values if they're missing. For example,
if you didn't provide a timestamp, then Engineer would add one and rewrite
your post metadata section to include the timestamp it set for you.

The normalization process also renames your post files to follow a standard
format. You can disable normalization for your site using the
:attr:`~EngineerConfiguration.NORMALIZE_INPUT_FILES` setting.

.. _post custom properties:

Custom Metadata
---------------

In addition to the metadata properties listed above, each post can include other
custom metadata, specified in YAML just like regular metadata. Engineer will add
these custom properties to the Post's :attr:`~engineer.models.Post.custom_properties`
property, where they can be used by themes or plugins.

Custom properties are not manipulated in any way by Engineer itself (though plugins
may change/update them) and they are maintained during :ref:`post normalization`.

.. _timezones:

A Note About Timezones
~~~~~~~~~~~~~~~~~~~~~~

Time zones are a tricky thing in the best of circumstances, and unfortunately
one of Python's few weaknesses is how it deals with them. It's particularly
difficult to get the current system time zone, especially on Windows,
so Engineer forces you to set a time zone explicitly. If you don't, Engineer
assumes that times are in UTC. You can use the
:attr:`~EngineerConfiguration.POST_TIMEZONE` setting to set which timezone
Engineer should assume your post timestamps are in.

You can see a complete list of the valid timezone settings
`at the PostgreSQL site`__. Yes, it's a bit weird, but the list
there is the most comprehensive one I've seen that doesn't threaten to utterly
confuse and overwhelm mere mortals when they see it. Keep in mind that some
rows in the table list multiple valid strings that happen to correspond to the
same time zone. For example, ``Asia/Jerusalem``, ``Asia/Tel_Aviv``, and
``Israel`` all correspond to the same timezone, and all are valid strings. (Why
they could not simply put a delimiter *other than a space* between the strings
in a single row I'll never understand.)

You can also choose to put a date/time string *with a UTC offset* in relevant
places, in which case Engineer will understand that the time is in a specific
zone. For example, if you specify your post's :ref:`timestamp <post timestamp>`
as something like ``2012-04-17 08:47:00-08:00``, Engineer will understand that
the time specified is 8 hours behind UTC. Generally I have found this to be
a hassle, since forgetting the offset can cause incorrect post timestamps,
and setting the :attr:`~EngineerConfiguration.POST_TIMEZONE` is much more
straightforward.

You might also find yourself in a situation where you write your posts in one
timezone, but your server is in another. This generally isn't a problem *unless*
you're using :doc:`Emma <emma>`. In that case you should be sure to set your
:attr:`~EngineerConfiguration.SERVER_TIMEZONE` as well.

.. __: http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE


Post Content
============

Your post content should be written in Markdown, and all the usual Markdown syntax rules apply. Engineer does provide
some helpful CSS styles that might be useful when writing your posts. In addition to these,
individual themes might provide their own.


Images
------

If you have images in your posts, you should wrap them in an outer ``div`` with the class ``image``. If the image has
a caption, you can also apply the ``caption`` class to the outer ``div`` and include the caption in a ``p`` tag just
below the image. Finally, you can apply the ``left``, ``right``, and ``center`` classes to the outer ``div`` to
align the image. For example:

.. code-block:: html

    <div class="image caption center">
        <a href="http://www.flickr.com/photos/76037594@N06/7206331966/">
            <img src="http://farm8.staticflickr.com/7241/7206331966_66d2e5e577.jpg"
                 width="500"
                 height="375"
                 alt="An xkcd.com comic in Reeder">
        </a>
        <p>An xkcd.com comic in Reeder</p>
    </div>


.. _teaser content:

Teaser Content
--------------

Some themes support 'teaser content.' As part of a post, you can specify a break in the content. Only content before
the break will be displayed on list pages, such as the homepage, but individual post pages will contain the full
post.

You can specify the break in your post with either ``-- more --`` or the Octopress-style ``<!-- more -->``.

.. versionadded:: 0.3.0
