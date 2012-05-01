===============
Getting Started
===============

Engineer's :ref:`init <engineer init>` command can be used to create a sample Engineer site in a matter of seconds.
The steps below will walk through that process. You can also look at the source for
`tylerbutler.com <https://github.com/tylerbutler/tylerbutler.com>`_ to get more ideas of what's possible with Engineer.


Your First Engineer Site
========================

After you've installed Engineer, you can use the :program:`engineer` command at the command line to interact with it.
The :ref:`engineer init` command will create a basic folder structure for you in a directory of your choosing,
and using that command is a good place to start if you're new to Engineer. Open up a terminal and type::

    PS C:\> mkdir my-engineer-site
    PS C:\> cd my-engineer-site
    PS C:\my-engineer-site> engineer init
    21:39:46 engineer Initialization complete.
    PS C:\my-engineer-site> ls

        Directory: C:\my-engineer-site

    Mode                LastWriteTime     Length Name
    ----                -------------     ------ ----
    d----          4/7/2012   9:29 PM            archives
    d----          4/7/2012   9:29 PM            posts
    d----          4/7/2012   9:29 PM            templates
    -a---          4/7/2012   9:29 PM        260 base.yaml
    -a---          4/7/2012   9:29 PM        153 config.yaml
    -a---          4/7/2012   9:29 PM         30 debug.yaml

    PS C:\my-engineer-site>


Building the Site
-----------------

Now you have a basic Engineer site, along with some sample content. We'll go over the details of what the files and
folders in the site folder are used for, but for now, let's build the sample site::

    PS C:\my-engineer-site> engineer build

    21:48:00 engineer Initializing empty configuration.
    21:48:00 engineer No '--settings' parameter specified, defaulting to C:\my-engineer-site\config.yaml.
    21:48:00 engineer Loading configuration from C:\my-engineer-site\config.yaml.
    21:48:00 engineer Generating template pages from C:\my-engineer-site\templates\pages.
    21:48:00 engineer Caches either don't exist or are old, so creating new ones...
    21:48:00 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\engineer\lib\foundation\stylesheets\grid.css.
    21:48:00 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\engineer\lib\foundation\stylesheets\mobile.css.
    21:48:01 engineer Preprocessed LESS file theme/stylesheets/dark_rainbow.less.
    21:48:01 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\theme\stylesheets\dark_rainbow.css.
    21:48:01 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\engineer\lib\foundation\javascripts\foundation.js.
    21:48:01 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\theme\scripts\highlight.js.
    21:48:01 engineer Loading posts...
    21:48:01 engineer '(d)2012-03-09-a-draft-post.md': LOADED successfully.
    21:48:01 engineer '(d)2012-03-18-test-post.md': LOADED successfully.
    21:48:01 engineer '(p)2012-03-07-markdown-tutorial.md': LOADED successfully.
    21:48:01 engineer '(p)2012-03-08-theme-style-preview.md': LOADED successfully.
    21:48:01 engineer '(p)2012-03-09-what-s-next.md': LOADED successfully.
    21:48:01 engineer '(p)2012-03-10-welcome.md': LOADED successfully.
    21:48:01 engineer Successfully parsed 6 new items and loaded 0 from the cache.
    21:48:01 engineer Output new or modified post 'Welcome'.
    21:48:01 engineer Output new or modified post 'What's Next?'.
    21:48:01 engineer Output new or modified post 'Theme Style Preview'.
    21:48:01 engineer Output new or modified post 'Markdown Tutorial'.
    21:48:01 engineer Synchronizing output directory with output cache.
    21:48:02 engineer
    21:48:02 engineer Site: 'Engineer Site' output to C:\my-engineer-site\output.
    21:48:02 engineer Posts: 4 (4 new or updated)
    21:48:02 engineer Post rollup pages: 1 (5 posts per page)
    21:48:02 engineer Template pages: 2
    21:48:02 engineer Tag pages: 7
    21:48:02 engineer 96 new items, 0 modified items, and 0 deleted items.

A few seconds after typing :program:`engineer build` you should see some output similar to the above. The last few
lines provide a summary of the overall build. In this case, there were four new posts, a rollup page,
two template pages, and seven tag pages output. A total of 96 new files were output - that count includes static
files such as JavaScript and CSS. For fun, let's see what happens if we run the build command again immediately::

    PS C:\my-engineer-site> engineer build

    22:02:49 engineer Initializing empty configuration.
    22:02:49 engineer No '--settings' parameter specified, defaulting to C:\my-engineer-site\config.yaml.
    22:02:49 engineer Loading configuration from C:\my-engineer-site\config.yaml.
    22:02:49 engineer Generating template pages from C:\my-engineer-site\templates\pages.
    22:02:49 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\engineer\lib\foundation\stylesheets\grid.css.
    22:02:49 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\engineer\lib\foundation\stylesheets\mobile.css.
    22:02:50 engineer Preprocessed LESS file theme/stylesheets/dark_rainbow.less.
    22:02:50 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\theme\stylesheets\dark_rainbow.css.
    22:02:50 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\engineer\lib\foundation\javascripts\foundation.js.
    22:02:50 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\theme\scripts\highlight.js.
    22:02:50 engineer Loading posts...
    22:02:50 engineer Successfully parsed 0 new items and loaded 6 from the cache.
    22:02:50 engineer Synchronizing output directory with output cache.
    22:02:50 engineer
    22:02:50 engineer Site: 'Engineer Site' output to C:\my-engineer-site\output.
    22:02:50 engineer Posts: 4 (0 new or updated)
    22:02:50 engineer Post rollup pages: 1 (5 posts per page)
    22:02:50 engineer Template pages: 2
    22:02:50 engineer Tag pages: 7
    22:02:50 engineer 0 new items, 0 modified items, and 0 deleted items.

You'll notice that the output is slightly different. In this case, the same number of posts, template pages,
tag pages, etc. were output, but Engineer didn't end up changing any output files. This is because Engineer recognized
that there weren't any changes to the source files that required outputting content.

Seeing What Your Site Looks Like
--------------------------------

Now let's see what that site we just built actually looks like! We can use the built-in development server to do that::

    PS C:\my-engineer-site> engineer serve

    22:07:50 engineer Initializing empty configuration.
    22:07:50 engineer No '--settings' parameter specified, defaulting to C:\my-engineer-site\config.yaml.
    22:07:50 engineer Loading configuration from C:\my-engineer-site\config.yaml.
    22:07:50 engineer Initializing empty configuration.
    22:07:50 engineer No '--settings' parameter specified, defaulting to C:\my-engineer-site\config.yaml.
    22:07:50 engineer Loading configuration from C:\my-engineer-site\config.yaml.
    Bottle server starting up (using WSGIRefServer())...
    Listening on http://localhost:8000/
    Hit Ctrl-C to quit.

If you visit http://localhost:8000/ you'll see the output of the build process just as it would look if you copied
the output folder to another web server. You can click around the site as much as you'd like. When you're done,
you can shut down the development server by pressing :kbd:`Ctrl-C`.

Now let's see what happens if we make a change to the site. Let's publish one of the draft posts in the :file:`posts`
folder. Open :file:`(d)2012-03-18-test-post.md` in a text editor (any one will do) and you should see something like
this:

.. code-block:: yaml

    title: Test Post
    timestamp: 05:51 PM Sunday, March 18, 2012 UTC
    status: draft
    slug: test-post

    ---

    This is a test post.

Change the line that says ``status: draft`` to read ``status: published`` instead and save the file. Then do another
build::

    PS C:\my-engineer-site> engineer build

    22:22:51 engineer Initializing empty configuration.
    22:22:51 engineer No '--settings' parameter specified, defaulting to C:\my-engineer-site\config.yaml.
    22:22:51 engineer Loading configuration from C:\my-engineer-site\config.yaml.
    22:22:51 engineer Generating template pages from C:\my-engineer-site\templates\pages.
    22:22:51 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\engineer\lib\foundation\stylesheets\grid.css.
    22:22:51 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\engineer\lib\foundation\stylesheets\mobile.css.
    22:22:52 engineer Preprocessed LESS file theme/stylesheets/dark_rainbow.less.
    22:22:52 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\theme\stylesheets\dark_rainbow.css.
    22:22:52 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\engineer\lib\foundation\javascripts\foundation.js.
    22:22:52 engineer Compressed file C:\my-engineer-site\_cache\config.yaml\output_cache\static\theme\scripts\highlight.js.
    22:22:52 engineer Loading posts...
    22:22:52 engineer '(d)2012-03-18-test-post.md': LOADED successfully.
    22:22:52 engineer Successfully parsed 1 new items and loaded 5 from the cache.
    22:22:52 engineer Output new or modified post 'Test Post'.
    22:22:52 engineer Synchronizing output directory with output cache.
    22:22:52 engineer
    22:22:52 engineer Site: 'Engineer Site' output to C:\my-engineer-site\output.
    22:22:52 engineer Posts: 5 (1 new or updated)
    22:22:52 engineer Post rollup pages: 1 (5 posts per page)
    22:22:52 engineer Template pages: 2
    22:22:52 engineer Tag pages: 7
    22:22:52 engineer 3 new items, 4 modified items, and 0 deleted items.

In this case, we see that there were several new files and folders created as well as some updates ones. Now use
:program:`engineer serve` to see what the site looks like. You should see the new post that we just published.
Finally, try deleting a file in the :file:`posts` folder, rebuilding, and see what happens...

While the sample site serves as a good starting point and a great way to familiarize yourself with the Engineer
command line interface, it's probably not what you want your site to look like. Let's look at the files and
folders in the site directory to see what we might want to change.

.. seealso::
   :doc:`Engineer command reference <cmdline>`

File System Structure
---------------------

The file system in :file:`C:\\my-engineer-site\\` should look something like this::

   /my-engineer-site
      - base.yaml
      - config.yaml
      - debug.yaml
      /_cache
      /archives
      /output
      /posts
      /templates

You can ignore the :file:`_cache` folder. It's just used by Engineer to improve performance. You could even delete it
if you wanted; Engineer would simply recreate if needed. The ``.yaml`` files are used for configuration - there are a
couple of different ones available so the same site can be generated in different ways out output to different
locations.

The :file:`archives` and :file:`posts` folders contain :doc:`posts` for the site. The :file:`templates` folder contains
:doc:`templates`, including :ref:`template pages`,  and the :file:`output` folder contains - you guessed it! - the
output content of your site after it's built by Engineer.

As you can see, each of these folders contains content used to build out the site. For more information about each of
these things, see the relevant topic guides.

.. seealso::
   The following topic guides have specific information about the major components used in Engineer:

   - :doc:`settings`
   - :doc:`Post <posts>`
   - :doc:`templates`
   - :ref:`template pages`
   - :doc:`themes`
