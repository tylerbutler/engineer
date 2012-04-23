
=====
Posts
=====

.. currentmodule:: engineer.conf

Posts are the bread and butter of an Engineer site. Posts are Markdown files with either a ``.md`` or ``.markdown``
file extension and are structured like this:

.. code-block:: yaml

    title: Why Do We Have to Reboot So Much?
    timestamp: 2012-02-03 13:36:00
    status: published
    tags:
    - software design
    - grandma
    slug: why-do-we-have-to-reboot-so-much

    ---

    Because it's the easiest way to kill/restart processes.

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
       value, the time will be assumed to be


.. _post status:

``status``
    The status of the post - ``published`` or ``draft``. This always defaults
    to ``draft`` if it's missing or set to an unknown value to avoid
    accidentally publishing something that wasn't meant to be published.


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
    a specific tag listed.


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


.. _post via_link:

``via_link``
    If you want to link to a different URL as part of your attribution, you
    can provide an optional link to the blog or individual's personal site
    (or perhaps the article that linked you to the external link originally).
    Exactly how this attribution metadata is used in the site depends on the
    theme.


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


.. _timezones:

A Note About Timezones
~~~~~~~~~~~~~~~~~~~~~~

TODO
