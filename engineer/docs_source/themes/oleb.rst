
.. _oleb:

=====
Ole B
=====

**Ole B** is a bright, simple theme based on Ole Begemann's design for `<http://oleb.net>`_,
created with his permission. The theme was written from scratch by `Tyler Butler <http://tylerbutler.com>`_ using
Ole's site as a reference.

.. note::
   By default :ref:`oleb` uses several fonts available at TypeKit. These fonts are available as part of TypeKit's
   trial plan.

Settings
========

Ole B supports the following settings which can be configured using the
:attr:`~engineer.conf.EngineerConfiguration.THEME_SETTINGS` setting.

``comments``
    Set this setting to enable comments on your site. Comments are off by default. You can use either
    `Disqus <http://www.disqus.com/>`_ or `Instense Debate <https//intensedebate.com/>`_ as your comment system. To
    use Disqus, set the ``comments`` setting to ``disqus``. To use Intense Debate instead,
    set the ``comments`` setting to ``intensedebate``. Be sure to also set the ``comments_account`` setting properly
    as well.

``comments_account``
    Both Disqus and Intense Debate require an account ID in order to associate comments properly with your site. Set
    this setting to the account ID for your respective comment account.

``simple_search``
    A boolean indicating whether simple search should be enabled for the site. *Defaults to true.*

    Note that if you have customized your sidebar, you must include the ``_search.html`` snippet in your sidebar file
    or the search box will not be visible. See :ref:`oleb snippets` for more information.

    .. versionadded:: 0.4.0

``typekit_id``
    The ID of the TypeKit kit that should be used. Ole B uses specific fonts that should be included in the kit.

``twitter_id``
    The username of the Twitter user whose feed should be shown in the sidebar. *Defaults to tylerbutler if not
    provided.*

``tweet_count``
    The number of tweets to include in the Twitter sidebar. *Defaults to 4 if not provided.*


Fonts
=====

Ole B requires the following fonts:

- `Museo Slab <https://typekit.com/fonts/museo-slab>`_
- `Museo Sans <https://typekit.com/fonts/museo-sans>`_


Templates
=========

Required Templates and Fragments
--------------------------------

No templates are strictly required for this theme beyond the base :ref:`template fragments` that all Engineer sites
will likely want to provide. In particular, users of the Ole B theme will probably want to create
:file:`_sidebar.html` and :file:`_primary_nav.html` templates.

.. seealso::
   :ref:`template fragments`, :ref:`navigation`, :ref:`sidebar`


.. _oleb inheritable templates:

Inheritable Templates
---------------------

Ole B includes several base templates that sites can inherit from to create :ref:`template pages`.

:file:`template_page_simple`
    A simple template page layout that includes the default site sidebar.


Template Fragments
------------------

Ole B does not support any additional :ref:`template fragments` beyond those available for all Engineer sites.


.. _oleb snippets:

Snippets
--------

OleB provides some small snippets that can be included in the sidebar of your site. These snippets are designed
to be used in the sidebar, so using them is as simple as including them in your site's :ref:`_sidebar.html<sidebar>`
template fragment. In order to maintain maximum compatibility with themes that might not provide these same widgets,
you should specify ``ignore missing`` on the ``include`` directive.

For example, the Engineer sample site includes these widgets like so:

.. literalinclude:: ../../sample_site/templates/_sidebar.html
   :language: html+jinja

The following snippets are available:

:file:`snippets/_feed_links.html`
    Adds a link to your RSS feed.

:file:`snippets/_search.html`
    Adds a search box to your site sidebar.


Manifest
========

.. literalinclude:: ../../themes/oleb/metadata.yaml
   :language: yaml
