
:orphan:

=================
Template Contexts
=================

TODO


Global Context
==============

TODO


Post Pages
==========

TODO

``post``
    The post itself

``newer_post``
    The next post, sorted by date. If such a post doesn't exist, this is ``None``.

``older_post``
    The previous post, sorted by date. If such a post doesn't exist, this is ``None``.

``all_posts``
    A :class:`~engineer.models.PostCollection` of all the posts that are being rendered.

``nav_context``
    Always set to ``'post'``.

    .. seealso:: :ref:`navigation contexts`


List Pages
==========

TODO

.. code-block:: python

   self.listpage_template.render(
                post_list=self,
                slice_num=slice_num,
                has_next=has_next,
                has_previous=has_previous,
                all_posts=all_posts,
                nav_context='listpage')


Archive Pages
=============

TODO

.. code-block:: python

   self.archive_template.render(post_list=self,
                                all_posts=all_posts,
                                nav_context='archive')


Tag Pages
=========

TODO

.. code-block:: python

   render(tag=tag,
         post_list=self.tagged(tag),
         all_posts=all_posts,
         nav_context='tag')
