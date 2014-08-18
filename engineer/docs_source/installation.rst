
============
Installation
============

Installing Using Pip
====================

Installing Engineer is easy using pip. Simply run the following command::

    pip install engineer

This will install the most recent released version of Engineer, which is version |version|.


Installing from Source
======================


Installing the Release Version from Source
------------------------------------------

If you'd prefer to install the current release version of Engineer (v |version|) directly from the source,
you have a couple of options. First, you can install directly from the GitHub repository using the following command::

    pip install -e git+https://github.com/tylerbutler/engineer.git#egg=engineer

This will check out the latest files from the *master* (release) branch GitHub directly and install the package and
all dependencies. Of course, you can also fork the repository and check out your own copy using the same approach.

Alternatively, you can download the source, unzip/untar it somewhere on your local hard drive, then run ``setup.py``::

    python setup.py install


Installing the In-Development Version from Source
-------------------------------------------------

If you're looking to install the in-development version of Engineer, then you can use the same methods covered above.
Using pip, the command must be changed slightly::

    pip install -e git+https://github.com/tylerbutler/engineer.git@dev#egg=engineer

If you download the Engineer source or clone the repository yourself, make sure you get the *dev* branch contents.

.. note::
   If you install Engineer from source using either of these methods, you should ensure you're looking at the most
   recent version of this documentation that corresponds to the in-development version of Engineer. You can find that
   version of the documentation at `<https://engineer.readthedocs.org/en/latest/>`_.


Creating a New Site
===================

After installation, you can use the :ref:`engineer init` command to initialize a new site with some sample content
and config files. Check the :doc:`cmdline` reference for more details about all the commands available,
or read :doc:`tutorial` if you're new to Engineer.
