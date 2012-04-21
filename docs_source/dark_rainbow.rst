
============
Dark Rainbow
============

The default Engineer theme, Dark Rainbow has also been called 'Voldemort's Skittles,' 'Unicorn Vomit,' and
other names not fit to repeat here. Needless to say, the parade of colors isn't for everyone. That said,
Dark Rainbow showcases several of the key features Engineer provides, including customizable navigation with
contextual highlighting, LESS support, TypeKit and JQuery integration, and Foundation CSS-based layouts.

.. note::
   Dark Rainbow uses several fonts available at TypeKit. These fonts are available as part of TypeKit's trial plan.

Settings
========

Dark Rainbow supports the following settings which can be configured using the
:attr:`~engineer.conf.EngineerConfiguration.THEME_SETTINGS` setting.

``typekit_id``
    The ID of the TypeKit kit that should be used. Dark Rainbow uses specific fonts that should be included in the kit.

``twitter_id``
    The username of the Twitter user whose feed should be shown in the sidebar. *Defaults to tylerbutler if not
    provided.*

``tweet_count``
    The number of tweets to include in the Twitter sidebar. *Defaults to 4 if not provided.*


Fonts
=====

TODO.


Templates
=========

Required Templates and Fragments
--------------------------------

No templates are strictly required for this theme beyond the base :ref:`template fragments` that all Engineer sites
will likely want to provide. In particular, users of the Dark Rainbow theme will probably want to create
:file:`_sidebar.html` and :file:`_primary_nav.html` templates.

.. seealso::
   :ref:`template fragments`, :ref:`navigation`, :ref:`sidebar`


Inheritable Templates
---------------------

Dark Rainbow includes several base templates that sites can inherit from to create :ref:`template pages`.

:file:`template_page_simple`

A simple template page layout that includes the default site sidebar.

:file:`template_page_no_sidebar`

A simple template page layout that removes the default site sidebar, devoting the entire page to the template page
content.


Template Fragments
------------------

Dark Rainbow does not support any additional :ref:`template fragments` beyond those available for all Engineer sites.


Metadata
========

.. code-block:: yaml

   name: 'Dark Rainbow'
   id: dark_rainbow
   description: A dark theme with just a hint of color.
   author: 'Tyler Butler <tyler@tylerbutler.com>'
   website: 'http://tylerbutler.com'
   license: 'Creative Commons BY-SA 3.0'
   use_foundation: yes
   use_lesscss: yes
   use_modernizr: no
   use_jquery: yes

   self_contained: yes
