---
title: "WebFaction, bash, Python, and Keeping Your Sanity"
timestamp: 2011-12-28
tags:
	- guides
	- webfaction
	- python
draft: true

---

WebFaction has a lot of different versions of Python available, which makes sense since it's a shared
hosting environment. However, you're probably going to want a specific version for your applications
(2.7 in my case). Luckily, that's pretty easy to do.

The [WebFaction Python docs][1] do actually cover these steps, but if you don't know what you're looking for
they can be hard to find. Basically, you need to specify what version of python you want to use. You could just type
`python2-7` instead of `python` all the time, but that gets old really quickly. It's easier to [create an alias][2]
for the `python` command that points to the version you want to use.

I won't go into the details of doing that since the WebFaction docs actually do a good job, but it's worth calling
out the note in the webfaction docs:

> *Note:*
> The python alias will not be available in shell scripts or other situations where the alias is not defined.
> In such cases, the explicit Python version should be called instead (for example, python2.6).

Keep this in mind. And while you're creating an alias for `python`, you might consider making an alias for
`easy_install`.

Once you've got your aliases set up, it's time to install [virtualenv][] and [virtualenvwrapper][]. That's easy
enough; just type:

    :::bash
    easy_install pip # install pip first...
    pip install virtualenv virtualenvwrapper # then install the rest...

OK, everything is installed, but we need to configure a couple of things for [virtualenvwrapper][] to be useful. You
need to set the `WORKON_HOME` environment variable and load `virtualenvwrapper.sh` into your shell. While you can do
that directly from the prompt, let's put it in our bash profile so it will get loaded automatically whenever we log in.

From the prompt, make sure you're in your home directory, then edit the `.bashrc` file there[^1]:

    :::bash
    cd ~ # make sure we're in the home directory
    nano .bashrc # use nano to edit the file

You'll want to add the following lines to your `.bashrc` file (at the bottom, most likely):

    :::bash
    export WORKON_HOME=$HOME/.virtualenvs # Store all the virtualenvs in ~/.virtualenvs
    export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python2.7 # Tell virtualenvwrapper to use python 2.7
    export VIRTUALENVWRAPPER_VIRTUALENV=~/bin/virtualenv # Tell virtualenvwrapper where virtualenv is
    source ~/bin/virtualenvwrapper.sh # Load virtualenvwrapper into the shell

    export PIP_VIRTUALENV_BASE=$WORKON_HOME # Tell pip to create its virtualenvs in $WORKON_HOME
    export PIP_RESPECT_VIRTUALENV=true # Tell pip to automatically use the currently active virtualenv

Some of these might be optional (in particular, lines 3, 6 and 7) but after a number of iterations this is what mine
ended up looking like.

After saving the file and exiting nano[^2], you'll need to reload the shell. Again, that's easy:

    :::bash
    source .bashrc

At this point you should be able to type `workon` to list any available virtualenvs, and use `mkvirtualenv` to create
them. There's more information in the `virtualenvwrapper command reference`.

Now that you are ready to deploy virtual environments, you might be interested in my guide on [deploying and
managing Django sites with mod_wsgi][4].

[^1]:
    You could also use `.bash_profile` rather than `.bashrc`, though I'm not sure it really matters in this case. Josh
    Staiger has [a good explanation of the difference between the two][3] that's worth reading if you're interested.

[^2]:
    Why nano instead of vim? Hey, if you're knowledgeable enough to know how to use vim, then this article is too
    remedial for you anyway. Go ahead and use vim, emacs, or whatever else if you'd like.

[1]: http://docs.webfaction.com/software/python.html
[2]: http://docs.webfaction.com/software/python.html#creating-a-python-alias
[3]: http://www.joshstaiger.org/archives/2005/07/bash_profile_vs.html
[4]: http://tylerbutler.com
[virtualenv]: http://www.virtualenv.org/
[virtualenvwrapper]: http://www.doughellmann.com/docs/virtualenvwrapper/
[virtualenvwrapper command reference]: http://www.doughellmann.com/docs/virtualenvwrapper/command_ref.html
