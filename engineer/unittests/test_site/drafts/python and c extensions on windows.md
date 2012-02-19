install vc++ 2008 express, seems like the simplest option. Reboot after you install it.

that might be all you need, but if you had another VS product installed - say, Visual Studio 2010 - then you might see an error like this when trying to install:

	...
	
	query_vcvarsall
		raise ValueError(str(list(result.keys())))
	ValueError: [u'path']
	An error occured when trying to install pycrypto 2.0.1.

I have no idea exactly what is going on here.ou need to 'configure' your compiler using vcvarsall.bat. That file should be in `C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC`. Run it and you should see something like this:

	PS C:\Users\Tyler> & "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\vcvarsall.bat"
	Setting environment for using Microsoft Visual Studio 2008 x86 tools.
	
Now when you try to install your python package that required compilation, things should work.

If you're using 64-bit Python, unfortunately I can't help you. I had so many problems with 64-bit that I just uninstalled it and went back to 32-bit. I'm sure all the problems I had are solveable - I just didn't have the patience. Just getting *this* up and running was enough to make me hulk-rage.
