---
title: "Managing Django Sites on WebFaction"
timestamp: 2011-12-28
tags:
status: published
---

Handy tools
- PuTTY
- WinSCP

## Create Apps and Sites Using the WebFaction Control Panel

Log in to the webfaction control panel.
Under domains/websites select applications.
Click the *New* icon in the lower right-hand corner.
Under app category select mod_wsgi
App type select the appropriate type - mod_wsgi 3.3/Python 2.7 for me

After it's created make a note of the port number for the app [11050]

Go to the domains section and add a domain and subdomains if you haven't already.

- tylerbutler.com
- staging.tylerbutler.com
- sandbox.tylerbutler.com

Go to the sites section and add a new site.
Select the appropriate subdomain(s) from the list - you can map multiple subdomains to the same site.
Finally, you need to map the application you created earlier to a site URL.

Click the *New* button in the lower right-hand corner, select the application from the dropdown, and type the path you
want to use to access that site. For example, `/` will mean you'll hit that application by visiting
http://sub.domain.tld/ where sub.domain.tld is obviously replaced by your own domain.

This mapping is nice because it lets you map individual applications to different paths within your URL,
so if you add a new Django application later you can simply add a new entry here to make it accessible at
the `/new_project` URL if you want.

Now, after a few minutes, you should be able to visit your site in a browser. You'll see something like this:

	Welcome to your mod_wsgi website! It uses:

	Python 3.1.3 (r313:86834, Dec  1 2010, 06:15:12) 
	[GCC 4.1.2 20080704 (Red Hat 4.1.2-48)]

All of your web applications are stored in `~/webapps/app_name`. Since we're using mod_wsgi there's not a lot in
there except the Apache config, but you'll want to remember that for later.

## Getting the files to the server

Now that we've got our apps created and wired up, it's time to be a command-line commando. [Log into your
webfaction account via SSH][1]. Now would also be a good time to set up your WebFaction bash profile and get
virtualenv and virtualenvwrapper installed if you haven't already. I put together [a guide][2] for that as well.
Check it out and come back - I'll wait.

We'll use virtualenv to consolidate all the packages needed by each Django site, so create a virtualenv for that
purpose:

    $ mkvirtualenv staging.tylerbutler.com

    New python executable in staging.tylerbutler.com/bin/python2.7
    Also creating executable in staging.tylerbutler.com/bin/python
    Installing setuptools............done.
    Installing pip...............done.
    virtualenvwrapper.user_scripts creating /home/username/.virtualenvs/staging.tylerbutler.com/bin/predeactivate
    virtualenvwrapper.user_scripts creating /home/username/.virtualenvs/staging.tylerbutler.com/bin/postdeactivate
    virtualenvwrapper.user_scripts creating /home/username/.virtualenvs/staging.tylerbutler.com/bin/preactivate
    virtualenvwrapper.user_scripts creating /home/username/.virtualenvs/staging.tylerbutler.com/bin/postactivate
    virtualenvwrapper.user_scripts creating /home/username/.virtualenvs/staging.tylerbutler.com/bin/get_env_details

Now you need to decide where you're going to store your actual Django site files. I put all of mine in
`~/sites`, with a folder structure based on domain name and subdomain. For example, the http://staging.tylerbutler.com
site goes in `~/sites/tylerbutlercom/staging`, while the http://www.tylerbutler.com site goes in
`~/sites/tylerbutlercom/www`.

However you choose to do it, move your files to the server and put them in that folder[^1]. Now you need to configure
the mod_wsgi application you created earlier to point to your Django site. To do this, you'll need to edit the
`~/webapps/app_name/apache2/conf/httpd.conf` file. It should look very similar to this *before* you start editing it:

    ServerRoot "/home/username/webapps/staging_tylerbutler_com/apache2"

    LoadModule dir_module        modules/mod_dir.so
    LoadModule env_module        modules/mod_env.so
    LoadModule log_config_module modules/mod_log_config.so
    LoadModule mime_module       modules/mod_mime.so
    LoadModule rewrite_module    modules/mod_rewrite.so
    LoadModule setenvif_module   modules/mod_setenvif.so
    LoadModule wsgi_module       modules/mod_wsgi.so

    LogFormat "%{X-Forwarded-For}i %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
    CustomLog /home/username/logs/user/access_staging_tylerbutler_com.log combined
    DirectoryIndex index.py
    DocumentRoot /home/tylerbutler/webapps/staging_tylerbutler_com/htdocs
    ErrorLog /home/tylerbutler/logs/user/error_staging_tylerbutler_com.log
    KeepAlive Off
    Listen 11050
    MaxSpareThreads 3
    MinSpareThreads 1
    ServerLimit 1
    SetEnvIf X-Forwarded-SSL on HTTPS=1
    ThreadsPerChild 5
    WSGIDaemonProcess staging_tylerbutler_com processes=5 python-path=/home/tylerbutler/webapps/staging_tylerbutler_com/lib/python2.7 threads=1
    WSGIProcessGroup staging_tylerbutler_com
    WSGIRestrictEmbedded On
    WSGILazyInitialization On

    <Directory /home/tylerbutler/webapps/staging_tylerbutler_com/htdocs>
        AddHandler wsgi-script .py
    </Directory>

Some things to note here:

- The `CustomLog` (line 12) and `ErrorLog` (line 14) entries tell you where the logs will be kept. There isn't a reason
to change the defaults, but if you're ever wondering, that's where the logs for this particular application will be.
- The `Listen` entry defines what port the application is running on. This should match the port associated with the
application in the control panel that you noted earlier. Don't change this.

1. Comment out the `DirectoryIndex` and `DocumentRoot` entries (lines 13 and 14).
2.


[^1]:
You might also choose to use Mercurial or Git as a way to deploy your files. I am considering doing that myself,
but haven't started yet.


other good reference: http://insatsu.us/blogs/thomas-schreiber/2009/04/09/deploying-djangos-sites-framework-webfaction-virtu/

[1]: http://docs.webfaction.com/user-guide/access.html#connecting-with-ssh
[2]: http://tylerbutler.com/
