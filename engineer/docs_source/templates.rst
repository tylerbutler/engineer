
=========
Templates
=========

Engineer makes heavy use of `Jinja2`_ templates to render a site. Most templates come as part of :doc:`themes`,
and you might not even need to worry about them. In fact, Engineer makes it easy to customize your site without
creating full-blown Jinja templates.

.. note::
   Doing anything somewhat advanced with templates will require some knowledge of the Jinja2 template syntax and
   features. The `Jinja2 Documentation`_ is an excellent place to learn more about the language. The
   `Template Designer Documentation`_ in particular is a useful starting point if you're ready to jump right in. As
   usual, you can look at the :doc:`sample site <tutorial>` as a reference point to see how things fit together.

.. _Jinja2: http://jinja.pocoo.org/
.. _Jinja2 Documentation: http://jinja.pocoo.org/docs/
.. _Template Designer Documentation: http://jinja.pocoo.org/docs/templates/


.. _template fragments:

Template Fragments
==================

Template fragments are blocks of HTML that you want to put into pages on your site. For example,
the :file:`_footer.html` fragment contains markup you want to appear in the footer of your site. While template
fragments are complete Jinja2 templates, and thus can contain any Jinja2 syntax, you don't have to. In fact,
with the exception of :ref:`navigation`, you can simply put raw HTML into your template fragments - Engineer will
pull the content of those fragments into your site.


.. _built-in fragments:

Built-in Template Fragments
---------------------------

Engineer makes several template fragments available to all sites. While individual themes might also expose their
own, the following are available regardless of the theme you're using. In order to 'use' a fragment,
all you need to do is create a file with the same name as the fragment you're using in your
:attr:`~engineer.conf.EngineerConfiguration.TEMPLATE_DIR`. For example, creating a :file:`_footer.html` file in your
template directory will make Engineer put the contents of that file in the footer of your site.

.. tip::

   Template fragments should always be put in your site's
   :attr:`~engineer.conf.EngineerConfiguration.TEMPLATE_DIR`. The built-in fragments should all be in the root of the
   template dir, but themes might also support other fragments that should be located in slightly different places.
   Check your theme's documentation for details.

By convention all template fragments' names start with an underscore (``_``) and are optional. That said, the
:file:`_sidebar.html` and :file:`_nav_primary.html` fragments should be created. Otherwise you'll most likely see
sample content for your site's sidebar and navigation.

.. admonition:: Theme Designer Note

   Template fragments are meant to contain only HTML (with the notable exception of :ref:`navigation`). If you're
   including your own fragments, you should ensure users don't need to use special Jinja syntax or unique macros in
   their fragments if at all possible. If you do require such advanced syntax, be sure it's clearly documented.

:file:`_scripts_top.html`
    Use this fragment to put additional scripts at the top of your pages. This can be useful for getting
    :ref:`web analytics <google analytics>` scripts into your site, for example.

:file:`_scripts_bottom.html`
    This fragment is similar to :file:`_scripts_top.html` except the scripts are included at the bottom of your pages
    rather than at the top.

:file:`_stylesheets.html`
    Use this fragment to put additional CSS or LESS stylesheets at the top of your pages.

:file:`_nav_primary.html`

:file:`_nav_primary_links.html`
    These two fragments together contain the outer navigation links for your site. See the documentation on
    :ref:`navigation` for more details on fragment and what they should contain.

:file:`_sidebar.html`
    This fragment contains a sidebar for your site. See the documentation on :ref:`sidebar` for more details on this
    fragment and what it should contain.

:file:`_footer.html`
    This fragment contains the footer content for your site.

    .. note:: The Engineer developers (just me, really) would really appreciate it if you linked to the Engineer
       project in your footer. If you're finding Engineer useful, then linking back to the project is a great way to
       spread the word. You can put a link in manually if you'd like, or you can simply paste the following snippet
       into your :file:`_footer.html` fragment:

       .. code-block:: jinja

          {% include 'snippets/_powered_by.html' %}

       That will insert a little 'Powered by Engineer' link into your footer. Don't feel obligated to do this,
       of course, but if you do I really do appreciate it!


.. _navigation:

Navigation
----------

.. warning:: Navigation is an area of active development in Engineer. The current system is kludgy at best and I plan
   to give it a proper overhaul in an upcoming Engineer release.

Navigation links are critical to any website. In Engineer, the primary navigation links for your site should be put
in the :file:`_nav_primary_links.html` template fragment. This file should contain a set of ``<li>`` elements,
each of which is a navigation link. You can hard-code these links if you'd like, but Engineer includes
some Jinja macros that make generating more dynamic navigation links possible.

If you need more control over your navigation, you can also override the contents of :file:`_nav_primary.html` by
providing your own. By default, :file:`_nav_primary.html` merely contains some outer scaffolding for navigation links
(i.e. a ``<ul>`` tag):

.. literalinclude:: ../templates/_nav_primary.html
   :language: html+jinja

You can of course replace this with whatever you wish, but keep in mind that some themes may expect certain CSS
classes to be applied to the navigation.


Using ``navigation_link``
~~~~~~~~~~~~~~~~~~~~~~~~~

Since Engineer sites are statically generated, creating dynamic navigation links with highlighting for current nodes
is a bit challenging. The ``navigation_link`` macro makes this easier. A
`macro <http://jinja.pocoo.org/docs/templates/#macros>`_ is a Jinja2 construct that is similar to a function in a
programming language. The ``navigation_link`` macro, when called, outputs a list item (``<li>`` element) with a link.

It's a bit easier to see it in action. Here's what the sample site :file:`_nav_primary_links.html` template fragment
looks like:

.. literalinclude:: ../templates/_nav_primary_links.html
   :language: html+jinja

We first import the ``navigation_link`` macro from :file:`core/_macros.html`, then subsequently call the macro to
create the individual list items in the navigation list. When this fragment is rendered on the homepage of the site,
the HTML looks like this:

.. code-block:: html

   <li class="current"><a href="/">articles</a></li>
   <li><a href="/about">about</a></li>
   <li><a href="/themes">themes</a></li>

The ``navigation_link`` macro takes four arguments: the text to display for the link,
the actual URL of the link, a list of contexts in which the link should be highlighted,
and an optional CSS class name that should be applied to the active navigation nodes. By default, a highlighted link
simply has the CSS class specified in the :attr:`~engineer.conf.EngineerConfiguration.ACTIVE_NAV_CLASS` setting
applied to it; this can be overridden with each call to ``navigation_link``.


.. _navigation contexts:

Navigation Contexts
*******************

The way that Engineer determines whether a link should be highlighted or not is based on the current navigation
context. Whenever Engineer is rendering a page it has a context. If that context is in the list of contexts passed to
``navigation_link``, then Engineer highlights that link. Thus, in the example above,
the *articles* link should be highlighted whenever the current navigation context is ``post`` or ``listpage``.

Available navigation contexts:

``post``
    This context is active whenever Engineer is rendering a post.

``listpage``
    This context is active whenever Engineer is rendering a list of posts. For example,
    the home page of the Engineer site will have this navigation context.

``archive``
    This context is active whenever Engineer is rendering the archives page.

``tag``
    This context is active whenever Engineer is rendering a tag page.

template page name
    In addition, all template pages are rendered with a navigation context matching their name. In the sample site,
    this is used to highlight the *about* and *themes* navigation links when you're visiting those template pages in
    the site.


.. _urlname:

The ``urlname`` Function
************************

The ``urlname`` function provides a quick way to get a URL for a given page in your site. It is especially handy for
navigation. The acceptable arguments are:

``'home'``
    URL to the home page of the site.

``'archives'``
    URL to the archives page.

``'feed'``
    URL to the site RSS feed.

``'listpage'``
    URL to a specific slice of the home page. Since Engineer paginates the home page,
    this argument allows one to create a link directly to a specific page in the pagination. The slice number is
    provided as a second argument. For example:

    .. code-block:: python

       urlname('listpage', 2)

``'tag'``
    URL to the tag page for the given tag. The tag name is provided as a second argument. For example:

    .. code-block:: python

       urlname('tag', 'engineer')


.. _sidebar:

Sidebar
-------

The :file:`_sidebar.html` should contain HTML markup you wish to display in a sidebar on your site. This content
should be wrapped in a ``<section>`` container as appropriate. For example, the sample site :file:`_sidebar.html`
looks like this:

.. literalinclude:: ../sample_site/default/templates/_sidebar.html
   :language: html+jinja


.. _rss template:

Sitemap Templates
-----------------

If you need to customize the sitemap that Engineer generates for you, you can provide your own templates that
Engineer will use to generate it. This template should be named :file:`sitemap.xml` and should be in the root of your
site's :attr:`~engineer.conf.EngineerConfiguration.TEMPLATE_DIR`.

.. versionadded:: 0.3.0


Snippets
========

In addition to :ref:`template fragments`, some themes might provide 'snippets': small pieces of content or layout
that you might want to include in your sidebar, footer, etc. For example, the :ref:`dark rainbow` theme provides
snippets for a search bar and RSS feed links to include in your sidebar. Also, the 'Powered by Engineer' footer is a
snippet. By convention, snippets are placed in the 'snippets' folder. Because some themes might not provide snippets,
you should use the ``ignore missing`` command when including them in your site. For example:

.. literalinclude:: ../sample_site/default/templates/_sidebar.html
   :language: html+jinja

.. versionadded:: 0.4.0


.. _template pages:

Template Pages
==============

Many sites have a need for 'flat' pages like an 'about' or 'contact us' page. The 'flat' terminology isn't quite
right in Engineer's case, since all pages in Engineer are flat, but the need is real. Engineer provides this
capability via template pages.

A template page is basically just a simple HTML page in your site, but unlike a standard HTML page,
you can use Jinja2 templates to inherit the look and feel of your site but add content specific to your page. As
usual, it's easier to look at an example. Here's the :file:`themes.html` template page from the Engineer sample site:

.. code-block:: html+jinja

   {% extends 'theme/template_page_simple.html' %}

   {% block page_title %}Themes{% endblock %}

   {% block header_secondary_title %}Themes{% endblock %}

   {% block content %}
       <article>
           <p>Engineer comes with two themes, and provides a basic framework for creating
           additional ones if you're so inclined.</p>

           <h2>Dark Rainbow</h2>

           <p>The default Engineer theme, Dark Rainbow has also been called 'Voldemort's Skittles,'
               'Unicorn Vomit,' and other names not fit to repeat here. Needless to say, the parade of
               colors isn't for everyone.</p>
       </article>
   {% endblock %}

As you can see, this page extends :file:`theme/template_page_simple.html`, which is one of the inheritable templates
included with the :ref:`Dark Rainbow <dark rainbow inheritable templates>` theme. It sets the page title to 'Themes'
and adds some basic content for the page in the ``content`` block.

All themes include a basic template page base called :file:`template_page_base.html` that exposes the following blocks:

``page_title``
    The title of the page.

``content``
    The content of the page.

Themes may expose their own additional template page bases, like
:ref:`Dark Rainbow <dark rainbow inheritable templates>` does, but at the very least :file:`template_page_base.html`
will always be available.

Template pages should be placed in your :attr:`~engineer.conf.EngineerConfiguration.TEMPLATE_PAGE_DIR`. Folders are
permitted, so you can organize your template pages and that structure will be reflected in the URL paths to your pages.

.. tip::
   If you'd like to write content for template pages in Markdown, you can. Simply wrap your Markdown content with the
   ``markdown`` filter. For example::

       {% filter markdown %}
           This site is built using [Engineer](/projects/engineer), a static site generator I wrote myself after
           being inspired by [Brent Simmons][], Marco Arment's Second Crack, Jekyll, Octopress,
           and Hyde. It's written in [Python][] and uses [Jinja2][] for templating. I use the management site
           available with Engineer (aka Emma) to manage my posts, which in turn runs on [Bottle][].
       {%endfilter %}

