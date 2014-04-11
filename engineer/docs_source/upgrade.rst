
===========================
Upgrading to Engineer 0.5.0
===========================

Engineer 0.5.0 is released with a new version of *setuptools*. Due to some pretty big changes there,
including the recombining of the *distribute* forked project with the main *setuptools* project,
you may get an error when you try to upgrade Engineer in the standard way with ``pip install -U engineer``.

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
