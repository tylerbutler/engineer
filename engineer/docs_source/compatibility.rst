
.. _compatibility:

===============================================
Compatibility With Other Static Site Generators
===============================================

Engineer contains some compatibility features designed to ease transitions from other static site generators such as
Jekyll/Octopress, as well as support tools designed for those systems.

Jekyll/Octopress
================

.. versionadded:: 0.3.0

.. _fencing:

Post Metadata 'Fencing'
-----------------------

Jekyll requires that post metadata (or YAML front matter, in Jekyll terms) be 'fenced' within a YAML document
separator, like so:

.. code-block:: yaml

   ---
   title: Post Title
   tags:
   - tag 1
   - tag 2
   ---

Engineer, in contrast, does not require the metadata to be preceded by a ``---``. However,
Engineer will handle Jekyll-style metadata with no trouble, and will maintain your post format during
:ref:`metadata finalization`.

If you want Engineer to *always* output your metadata with or without fencing, you can use
the :attr:`~engineer.conf.EngineerConfiguration.METADATA_FORMAT` setting. Simply set it to ``fenced`` or
``unfenced`` and Engineer will always output the format you specify, regardless of the input format.

.. versionadded:: 0.3.0


Post Breaks
-----------

Engineer supports Octopress-style ``<!--more-->`` post breaks in addition to the simpler ``-- more --`` Engineer
style using the bundled :ref:`Post Breaks plugin<post breaks plugin>`.

.. versionadded:: 0.3.0

