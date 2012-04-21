
.. _build pipeline:

==================
The Build Pipeline
==================

TODO

Basic Flow
==========

All content first gets put into the output cache.

#. Copy base Engineer static content
#. Copy theme static content
#. Generate template pages
#. Load posts from cache and :attr:`~engineer.conf.EngineerConfiguration.POST_DIR`
#. Generate posts
#. Generate rollup pages
#. Generate archive pages
#. Generate tag pages
#. Generate feeds
#. Process/minify CSS/LESS/JS during post generation
#. Copy 'raw content' to output cache
#. Remove source LESS files from output cache is LESS preprocessing is turned on
#. Synchronize output directory with output cache

.. _raw content:

Raw Content
-----------

TODO
