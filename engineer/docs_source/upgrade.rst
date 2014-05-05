
===========================
Upgrading to Engineer 0.5.0
===========================

Engineer 0.5.0 is released with a new version of *setuptools*. Due to some pretty big changes there,
including the recombining of the *distribute* forked project with the main *setuptools* project,
you may get an error when you try to upgrade Engineer in the standard way with ``pip install -U engineer``. It may
look something like this::

    pip install -U engineer

    Downloading/unpacking engineer from https://pypi.python.org/packages/source/e/engineer/engineer-0.5.0.zip#md5=a1bb4061419a5430b91ae597032c801f
    Downloading engineer-0.5.0.zip (3.5MB): 3.5MB downloaded
    Running setup.py egg_info for package engineer

    The required version of setuptools (>=2.1) is not available,
    and can't be installed while this script is running. Please
    install a more recent version first, using
    'easy_install -U setuptools'.

    (Currently using setuptools 0.6c11 (c:\users\tyler\.virtualenvs\engineer\lib\site-packages\setuptools-0.6c11-py2.7.egg))

Fortunately, there are a few ways around this. First, you should upgrade *pip* and *setuptools*. There are details on
how to do this on the `pip website <http://www.pip-installer.org/en/latest/installing.html#upgrade-pip>`_,
but basically it boils down to running this command::

    python -m pip install -U pip

Once pip is upgraded, then you can use it to upgrade setuptools itself::

    pip install -U setuptools

Once *that's* done, you should be able to upgrade Engineer itself like so::

    pip install -U engineer

Note that if you're using virtualenv, you may need to upgrade pip and setuptools in your virtualenv *as well as* the
'global' (outside the virtualenv) versions.

If for some reason these steps don't work, I suggest downloading
`get-pip.py <https://raw.github.com/pypa/pip/master/contrib/get-pip.py>`_, running it using ``python get-pip.py``,
then deleting and recreating any virtualenvs you're using for Engineer. Hopefully it won't come to this,
though. The steps above should be all that's needed.
