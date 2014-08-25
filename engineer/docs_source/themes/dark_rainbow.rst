
.. _dark rainbow:

============
Dark Rainbow
============

The default Engineer theme, **Dark Rainbow** has also been called 'Voldemort's Skittles,' 'Unicorn Vomit,' and
other names not fit to repeat here. Needless to say, the parade of colors isn't for everyone. That said,
Dark Rainbow showcases several of the key features Engineer provides, including customizable navigation with
contextual highlighting, LESS support, TypeKit and JQuery integration, and Foundation CSS-based layouts.

Dark Rainbow was created by `Tyler Butler <http://tylerbutler.com>`_ and is available under a `Creative Commons
Attribution-ShareAlike 3.0 Unported License <http://creativecommons.org/licenses/by-sa/3.0/>`_.

.. note::
   By default :ref:`dark rainbow` uses several fonts available at TypeKit. These fonts are available as part of
   TypeKit's trial plan.

Settings
========

Dark Rainbow supports the following settings which can be configured using the
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
    or the search box will not be visible. See :ref:`dark rainbow snippets` for more information.

    .. versionadded:: 0.4.0

``typekit_id``
    The ID of the TypeKit kit that should be used. Dark Rainbow uses specific fonts that should be included in the kit.

``twitter_id``
    The username of the Twitter user whose feed should be shown in the sidebar. *Defaults to tylerbutler if not
    provided.*

    .. deprecated:: 0.5.0
       This setting is obsolete and ignored. The Tweet library has been removed from Engineer. See the
       :ref:`changelog` for more information.

``tweet_count``
    The number of tweets to include in the Twitter sidebar. *Defaults to 4 if not provided.*

    .. deprecated:: 0.5.0
       This setting is obsolete and ignored. The Tweet library has been removed from Engineer. See the
       :ref:`changelog` for more information.

Fonts
=====

Dark Rainbow requires the following fonts:

- `Museo Slab <https://typekit.com/fonts/museo-slab>`_
- `Myriad Pro <https://typekit.com/fonts/myriad-pro>`_
- `Kulturista Web <https://typekit.com/fonts/kulturista-web>`_
- `Ubuntu Mono <https://typekit.com/fonts/ubuntu-mono>`_ *(optional)*

.. versionchanged:: 0.4.0
   The Anonymous monospace font has been replaced by Ubuntu Mono by default. If you are using TypeKit you'll need to
   update your kit to include the Ubuntu Mono font. If you wish to continue using Anonymous you'll need to add your
   own CSS stylesheet.


Templates
=========

Required Templates and Fragments
--------------------------------

No templates are strictly required for this theme beyond the base :ref:`template fragments` that all Engineer sites
will likely want to provide. In particular, users of the Dark Rainbow theme will probably want to create
:file:`_sidebar.html` and :file:`_primary_nav.html` templates.

.. seealso::
   :ref:`template fragments`, :ref:`navigation`, :ref:`sidebar`


.. _dark rainbow inheritable templates:

Inheritable Templates
---------------------

Dark Rainbow includes several base templates that sites can inherit from to create :ref:`template pages`.

:file:`template_page_simple.html`
    A simple template page layout that includes the default site sidebar.

:file:`template_page_no_sidebar.html`
    A simple template page layout that removes the default site sidebar, devoting the entire page to the template page
    content.


Template Fragments
------------------

Dark Rainbow does not support any additional :ref:`template fragments` beyond those available for all Engineer sites.


.. _dark rainbow snippets:

Snippets
--------

Dark Rainbow provides some small snippets that can be included in the sidebar of your site. These snippets are designed
to be used in the sidebar, so using them is as simple as including them in your site's :ref:`_sidebar.html<sidebar>`
template fragment. In order to maintain maximum compatibility with themes that might not provide these same widgets,
you should specify ``ignore missing`` on the ``include`` directive.

For example, the Engineer sample site includes these widgets like so:

.. literalinclude:: ../../sample_site/default/templates/_sidebar.html
   :language: html+jinja

The following snippets are available:

:file:`snippets/_feed_links.html`
    Adds a link to your RSS feed.

:file:`snippets/_search.html`
    Adds a search box to your site sidebar.


Manifest
========

.. literalinclude:: ../../_themes/dark_rainbow/metadata.yaml
   :language: yaml
