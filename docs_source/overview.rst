# coding=utf-8

========
Overview
========

The killer workflow:

- Write a post on your iPad using Elements, PlainText, or some other Dropbox-connected Markdown editor.

- Wait ~30 minutes for the post to go live, or kick it off manually using the mini management site or bookmarklet.

Features:

- Posts can be written/edited in Markdown and stored/synchronized using Dropbox.

- Themes provide flexibility in the site look and feel without starting from scratch or rewriting a bunch of content.

- Built-in mini management site (optional) allows you to manage your site remotely.

- Regenerate your site remotely with just a click of a button using the Bookmarklet of Awesomeness.

- Output content is completely static and thus is blazingly fast to serve, scales up very well, and is completely
  independent of any specific web server or technology. Once generated, you can copy your site *anywhere* and use any
  web server you like.

Things that you might not like:

- Search isn't built in. You can configure Google site search (and the built-in themes do this),
  but it's not baked into Engineer. But... do people really use anything besides Google/Bing to find stuff anyway?

- Static sites can feel limited if you're used to doing something super-dynamic every time a page is loaded. Most of
  these things can be handled using either client-side JavaScript (e.g. `timeago.js`_) or clever uses of the Jinja 2
  template system (see the navigation highlighting functionality in Engineer itself for an example of things that can
  be done).

Major components:

Posts
  Posts are the bread and butter of an Engineer site. Posts are written in Markdown with a little YAML-formatted
  metadata, then are transformed into individual pages in a site, and also rolled up into list pages.
Templates
  Templates are how the content you write (typically as Posts) get transformed into a site. Engineer uses Jinja 2 as
  its templating engine. In general you don't have to mess with custom templates aside from specific templates used
  by a given theme.
Themes
  Themes are collections of templates, CSS (or LESS) styles, JavaScript, etc. that dictate the basic look and feel
  of your site. You can create your own themes or use some of the ones that are provided.
List Pages
  List pages are simply roll-up pages of posts. Think of the front page of a blog

Posts and Pages
===============

In Engineer you can add content to the site using Posts or Template Pages.

.. Links

.. _timeago.js: http://timeago.yarp.com/
