
:orphan:

**List Pages**
  List pages are simply roll-up pages of posts. Think of the front page of a
  blog, or a tag page listing all the posts tagged with a certain tag. You generally won't need to create these
  yourself - themes will create the ones that make sense automatically - but you can generate them yourself if you
  like.


**Templates**
  Templates are how the content you write (typically as Posts) get
  transformed into a site. Engineer uses `Jinja 2 <http://jinja.pocoo.org>`_ as its templating
  engine. In general you don't have to mess with custom templates aside from specific
  templates used by a given theme - unless you want to.

  .. seealso::
     :doc:`Template reference <templates>`

**Template pages**
  Template pages are a variation of templates. They're used for 'special' pages in a site that need to behave or look
  a little different than a standard post. For example, in the sample site, both the *about* and *themes* pages are
  template pages.

  .. seealso::
     :ref:`Template pages reference <template pages>`

**Themes**
  Themes are collections of templates, CSS (or LESS) styles, JavaScript,
  etc. that dictate the basic look and feel of your site. You can create your
  own themes or use some of the ones that are provided.

  .. seealso::
     :doc:`Theme reference <themes>`


Posts and Pages
---------------

In Engineer you can add content to the site using :doc:`posts` or :ref:`template pages`.


.. note::

   For all settings that specify a file system path, relative paths are assumed to be relative to
   :attr:`~engineer.conf.EngineerConfiguration.SETTINGS_DIR`, the directory that contains the settings file being
   used. Absolute paths are accepted and won't be modified, but relative paths are always relative to the settings
   file unless otherwise stated.

A website isn't much use without some sort of navigation, and Engineer-based sites are no exception. While at its
core, navigation constructs are nothing more than links to pages in the site, Engineer provides a few features that
makes using and managing the navigation for your site

Every type of item is rendered in Engineer using a 'navigation context'. This context

