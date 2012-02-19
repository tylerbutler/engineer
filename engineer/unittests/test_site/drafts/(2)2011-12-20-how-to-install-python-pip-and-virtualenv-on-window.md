timestamp: 2011-12-20 22:04:00
lang: markdown
post_id: 2
tags: null
title: How To Install Python, pip, and virtualenv on Windows with PowerShell

---


Get the python 2.7.2 32-bit installer from <python.org>
Get the setuptools exe for python 2.7 and install it

Add the following to your path:

    :::text
    C:\Python27
    C:\Python27\Scripts

Install pip using the `get-pip.py` script ([more details][1] at the pip website). Open up PowerShell, navigate to where you downloaded `pip`, and type

    :::text
    python get-pip.py

`Pip` should now be installed, so type `pip install virtualenv` then `pip install virtualenvwrapper-powershell` to get those installed.

Now you need to import the wrapper module in PowerShell, so type `Import-Module virtualenvwrapper`.
You will probably get an error saying:

    :::text
    Virtualenvwrapper: Virtual environments directory 
    'C:\Users\tylerbu/.virtualenvs' does not exist. Create it or 
    set $env:WORKON_HOME to an existing directory.

Well, at least you know you're on the right track! Do exactly what the message says: create the missing directory.

    mkdir '~\.virtualenvs'

You might also want to change the location to store your virtual environments. To do that, set the `$env:WORKON_HOME` variable to wherever you want to store them.

Now load the module again. Success! Now you have access to a bunch of virtualenv management commands directly in PowerShell. To see all of them, you can type `Get-Command *virtualenv*`.

    :::text
    CommandType     Name                          Definition
    -----------     ----                          ----------
    Function        CDIntoVirtualEnvironment      ...
    Alias           cdvirtualenv                  CDIntoVirtualEnvironment
    Function        Copy-VirtualEnvironment       ...
    Alias           cpvirtualenv                  Copy-VirtualEnvironment
    Function        Get-VirtualEnvironment        ...
    Alias           mkvirtualenv                  New-VirtualEnvironment
    Function        New-VirtualEnvironment        ...
    Function        New-VirtualEnvProject         ...
    Function        Remove-VirtualEnvironment     ...
    Alias           rmvirtualenv                  Remove-VirtualEnvironment
    Function        Set-VirtualEnvironment        ...
    Function        Set-VirtualEnvProject         ...
    Function        VerifyVirtualEnv              ...
    Application     virtualenv.exe                C:\Python27\Scripts\virtualenv.exe
    Application     virtualenv.exe.manifest       C:\Python27\Scripts\virtualenv.exe.manifest
    Application     virtualenv-script.py          C:\Python27\Scripts\virtualenv-script.py

You'll see that there are a bunch of nice PowerShell style cmdlets, like `New-VirtualEnvironment`, but there are also aliases set up mapping those cmdlets to commands you might be more familiar with, like `mkvirtualenv`. Of course you also get regular PowerShell tab completion for these cmdlets and aliases.

Anyway, let's make a new virtualenv:

    :::text
    New-VirtualEnvironment raidmanager --no-site-packages

Replace `raidmanager` with whatever you want to call your virtualenv. I usually name it after the project I plan to use that virtualenv for, but whatever you want works. The `--no-site-packages` argument is also optional. By default, virtualenv copies whatever python packages you have installed in your system python environment to a new one. I dislike this behavior since it can unnecesarily pollute a new virtualenv, so I have the habit of disabling it by passing this argument.

After the command completes, you should see a PowerShell prompt that looks like this:

    :::text
    (raidmanager)PS C:\Users\tylerbu>

The `(raidmanager)` prepended to your prompt reminds you that you're currently working within that virtualenv. If you type `workon` now you should see the available virtualenvs, and if you type `workon name_of_another_virtualenv` you'll flip to that environment.

Now that your virtual environments are configured, you can install packages into them using pip. Open a PowerShell prompt, type `workon name_of_virtualenv` and then type `pip install package_name`. There are also a couple of additional pip commands that might be useful to know. If you have a project with lots of package requirements, it might have come with (or you might have written) a [requirements file][3] (often called `requirements.txt`). To have pip load all of the packages in that file, type:

    :::text
    pip install -r path_to_requirements_file
    
Also, you might have downloaded a package's source manually that has a `setup.py` file in it. You can have pip install that for you by typing:
    
    :::text
    pip install -e path_to_source
    
The `-e` option can also check out source directly from a Mercurial, Git, Subversion, or Bazaar repository and install a package from there.

Now, you might notice at some point - probably once you open a new PowerShell prompt - that you can no longer use the `workon` and `New-VirtualEnvironment` commands. Well, silly, you forgot to import the `virtualenvwrapper` module! Now, you could just import it and move on with your life, but that's going to get annoying really quickly, so you can configure your PowerShell profile so that the module is loaded every time you open up a PowerShell window. First, though, you're going to need to find your profile. To make matters a bit more confusing, there are actually several profiles that PowerShell uses. But only one or two of them are really relevant to us. To see all the profiles available to you, type:

    :::text
    $profile | Format-List * -Force

    AllUsersAllHosts       : C:\Windows\System32\WindowsPowerShell\v1.0\profile.ps1
    AllUsersCurrentHost    : C:\Windows\System32\WindowsPowerShell\v1.0\Microsoft.PowerShell_profile.ps1
    CurrentUserAllHosts    : D:\Users\tylerbu\Documents\WindowsPowerShell\profile.ps1
    CurrentUserCurrentHost : D:\Users\tylerbu\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
    Length                 : 77

Looks like there are four available profile scripts, and based on their names, they all have different scopes. In our case, we probably want the `CurrentUserAllHosts` profile, since that will execute for us in every PowerShell instance. If you navigate to the location listed, there might not be a file there to edit. In that case, the following command will create a file there in the right format:

    :::text
    New-Item -Path $Profile.CurrentUserAllHosts -Type file -Force

Or you could just create a file in your favorite text editor and save it in that location (with the correct name, of course).

In that file, put the command you used to import the `virtualenvwrapper` modules earlier

    :::text
    Import-Module virtualenvwrapper
    
It's worth noting that this file is just a regular PowerShell script, so you can put other stuff in it too, such as aliases you like to set up, etc. Anyway, once that's done, save the file and open a new PowerShell window. Now the `workon` command and other virtualenv cmdlets should start functioning.

There is one final step to getting everything really *ready* for developing Python projects - setting up your IDE to use the appropriate `virtualenv` for your project. There are several different IDE's out there, or you could just rock [Notepad++][], but I personally like [PyCharm][].

If you *are* using PyCharm, there's a section in your project settings where you can specify your Python interpreter. Click *Add* to add a new interpreter, then point it to the `python.exe` inside your `virtualenv`'s `Scripts` directory. In my case, the full path is `C:\Users\tylerbu\.virtualenvs\tylerbutlercom\Scripts\python.exe`.

[1]: http://www.pip-installer.org/en/latest/installing.html#using-the-installer
[2]: http://www.blkmtn.org/PowerShell-Example_profile
[3]: http://www.pip-installer.org/en/latest/requirements.html
[PyCharm]: http://www.jetbrains.com/pycharm/
[Notepad++]: http://notepad-plus-plus.org/
