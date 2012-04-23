
==========================
Frequently Asked Questions
==========================


How Do I...
===========

.. _change theme:

...change my site theme?
------------------------

You can change the theme for a site using the :attr:`~engineer.conf.EngineerConfiguration.THEME` setting in your
:doc:`settings file <settings>`. You'll need to specify the :ref:`ID <theme id>` for the theme.

.. seealso::
   :doc:`settings`, :ref:`bundled themes`


...customize my site's navigation links?
----------------------------------------

See :ref:`navigation` and templates.


...add a flat page, like an 'about' or 'contact' page?
------------------------------------------------------

If you have an already-generated HTML page that you just want to put in your site,
the :ref:`raw content` feature might be what you're looking for. More likely, though, you'll want to take advantage of
:ref:`template pages`, which provide a simple way to create flat pages while inheriting the look and feel of your
site theme.

.. seealso::
   :ref:`template pages`, :ref:`raw content`


.. _add script:

...add custom JavaScript or CSS?
--------------------------------

If you need to load additional JavaScript or CSS in your site, you can use the :file:`_scripts_top.html`,
:file:`_scripts_bottom.html`, and :file:`_stylesheets.html` :ref:`template fragments`.

For example, to load the Google Analytics JavaScript on your pages, you might add a :file:`_scripts_top.html` template
fragment to your site's :file:`templates` folder, then paste the Google Analytics ``<script>`` tag into that file.
All pages in your site will then include the Google Analytics JavaScript. Similarly, you can use the
:file:`_stylesheets.html` template fragment to include additional CSS or LESS stylesheets.

.. seealso::
   :ref:`template fragments`


.. _google analytics:

...hook up Google Analytics (or another analytics system)?
----------------------------------------------------------

See :ref:`How do I add custom JavaScript or CSS? <add script>` which explains how to add custom JavaScript,
including the Google Analytics JavaScript, to your site pages.


...add a favicon or robots.txt file?
------------------------------------

The :ref:`raw content` feature of Engineer can handle this. For example, to add a :file:`robots.txt` file to the root
of your site, put the file in the :attr:`~engineer.conf.EngineerConfiguration.CONTENT_DIR` of your site (defaults to
:file:`content`).

.. seealso::
   :ref:`raw content`
