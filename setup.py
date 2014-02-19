# coding=utf-8
# Bootstrap installation of setuptools
from ez_setup import use_setuptools
use_setuptools()

import os
import sys
from fnmatch import fnmatchcase
from distutils.util import convert_path
from propane_distribution import cmdclassdict
from setuptools import setup, find_packages
from engineer import version

PROJECT = 'engineer'

################################################################################
# find_package_data written by Ian Bicking.

# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ('*.py', '*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
                                './dist', 'EGG-INFO', '*.egg-info')

def find_package_data(
        where='.', package='',
        exclude=standard_exclude,
        exclude_directories=standard_exclude_directories,
        only_in_packages=True,
        show_ignored=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.

    The dictionary looks like::

        {'package': [files]}

    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.

    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).

    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.

    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).

    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.

    This function is by Ian Bicking.
    """

    out = {}
    stack = [(convert_path(where), '', package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                    stack.append((fn, '', new_package, False))
                else:
                    stack.append((fn, prefix + name + '/', package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "File %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    return out

################################################################################

def get_install_requirements():
    requirements = []
    with open('requirements.txt') as file:
        temp = file.readlines()
        temp = [i[:-1] for i in temp]

        for line in temp:
            if line is None or line == '' or line.startswith(('#', '-e')):
                continue
            else:
                requirements.append(line)
        return requirements


def get_readme():
    with open('README.md') as file:
        return file.read()

setup(
    name=PROJECT,
    version=version.string,
    author='Tyler Butler',
    author_email='tyler@tylerbutler.com',
    platforms='any',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['engineer=engineer.engine:cmdline'],
    },
    url='http://github.com/tylerbutler/engineer',
    license='MIT',
    description='A static website generator.',
    long_description=get_readme(),
    install_requires=get_install_requirements(),
    tests_require=('nose'),
    cmdclass=cmdclassdict,
    include_package_data=True,
    package_data=find_package_data(PROJECT,
                                   package=PROJECT,
                                   only_in_packages=False),
    zip_safe=True, # Setting to False doesn't create an egg - easier to debug and hack on
)
