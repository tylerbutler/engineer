
============
Installation
============

Installing Using Pip
====================

Installing Engineer is easy using pip. Simply run the following command::

    pip install engineer


Installing from Source
======================

If you'd prefer to install Engineer directly from the source, you have a couple of options. First,
you can install directly from the github repository using the following command::

    pip install -e git://github.com/tylerbutler/engineer.git#egg=engineer

This will check out the latest files from github directly and install the package and all dependencies. Of course,
you can also fork the repository and check out your own copy using the same approach.

Alternatively, you can download the source, unzip/untar it somewhere on your local hard drive, then run ``setup.py``::

    python setup.py install


Creating a New Site
===================

After installation, you can use the :ref:`engineer init` command to initialize a new site with some sample content
and config files. Check the :doc:`cmdline` reference for more details about all the commands available,
or read :doc:`tutorial` if you're new to Engineer.
