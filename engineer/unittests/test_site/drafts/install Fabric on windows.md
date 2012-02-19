---
---

Before we get started, if you *haven't* already installed Python, you might be able to save yourself some trouble... The [Python for Windows download page][2] on <python.org> has this statement:

> You may also wish to download Win32all, Mark Hammond's add-on that includes the Win32 API, COM support, and Pythonwin extensions. It's available from the pywin32 project on SourceForge.

It's entirely possible that just using that installer rather than the one from <python.org> will make the steps below unnecessary. Unfortunately I have not had the time to validate whather that's true or not. Anyway, you probably already have Python installed anyway, so read on.

First make sure you can compile C extensions on your box. You'll need that for pycrypto, which Fabric depends on.

install fabric using pip:

	pip install Fabric
	
Check if things are working:

	(tylerbutler.com)PS C:\Users\Tyler\Code\tylerbutlercom\PROJECT_ROOT> fab
	
	...
	
	File "C:\Users\Tyler\.virtualenvs\tylerbutler.com\lib\site-packages\fabric\state.py", line 85, in _get_system_username

			import win32api
		ImportError: No module named win32api
		
Hmm, it appears not... You need to get PyWin32 installed. As far as I can tell, the only way to do that is with the .exe installer you download at <http://sourceforge.net/projects/pywin32/>. If you're using virtualenv, you may need to activate your virtualenv before kicking off the installer, so it shows up in the list of available python installations to install to. If you want to use it in multiple virtualenvs, the only way I know to do it is to install it multiple times, selecting a different virtualenv each time until it's installed in all of them. If you know of a better way let me know.[^1]

Now that you have 

	Fatal error: Couldn't find any fabfiles!

	Remember that -f can be used to specify fabfile path, and use -h for help.

	Aborting.

Great, things should be working. Now back to the [Fabric tutorial][1].


[^1]:
While pywin32 is listed on PyPI and a `pip search pywin32` does indicate you could install it, when I tried, I got this:

	Downloading/unpacking pywin32
	  Could not find any downloads that satisfy the requirement pywin32
	No distributions at all found for pywin32

[1]: http://docs.fabfile.org/en/1.3.3/tutorial.html
[2]: http://python.org/download/windows/
