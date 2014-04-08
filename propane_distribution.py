# coding=utf-8
from collections import namedtuple
import os
import re
import subprocess
import time
from datetime import datetime, date as sysdate
from distutils.command.sdist import sdist as _sdist
from distutils.core import Command


__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

# Inspired by https://github.com/warner/python-ecdsa/blob/0ed702a9d4057ecf33eea969b8cf280eaccd89a1/setup.py#L34

VersionTuple = namedtuple('VersionTuple', ['major', 'minor', 'patch'])


class version_class(object):
    def __init__(self, version_string='0.0.1', the_date=None, the_time=None):
        self.version = version_string
        self._version_tuple = self._parse_tuple(self.version)
        if the_time is None:
            the_time = datetime.utcnow()
        if the_date is None:
            the_date = the_time.date
        self.time = the_time
        self.date = the_date

    @property
    def string(self):
        return self.version

    @property
    def tuple(self):
        return self._version_tuple

    @property
    def major_string(self):
        return self.tuple.major

    @property
    def minor_string(self):
        return '.'.join(self.tuple[0:2])

    @property
    def patch_string(self):
        return self.string

    def __lt__(self, other):
        return self.string.__lt__(other.string)

    def __le__(self, other):
        return self.string.__le__(other.string)

    def __eq__(self, other):
        return self.string.__eq__(other.string)

    def __ne__(self, other):
        return self.string.__ne__(other.string)

    def __gt__(self, other):
        return self.string.__gt__(other.string)

    def __ge__(self, other):
        return self.string.__ge__(other.string)

    @staticmethod
    def _parse_tuple(ver_string):
        split_string = ver_string.split('.')
        return VersionTuple(split_string[0], split_string[1], '.'.join(split_string[2:]))

    def __unicode__(self):
        return self.string

    __str__ = __unicode__
    __repr__ = __unicode__


VERSION_FILENAME = '_version.py'
VERSION_PY = """# coding=utf-8
import time
from datetime import date
from propane_distribution import version_class

# This file is originally generated from Git information by running 'setup.py
# version'. Distributions contain a pre-generated copy of this file.

__version__ = '{version}'
__date__ = date({year}, {month}, {day})
__time__ = time.gmtime({time})

version = version_class(__version__, __date__, __time__)
"""

GIT_RUN_FAIL_MSG = "unable to run git, leaving %s alone"


def update_version_py(git_tag_prefix='v', version_path=None):
    if version_path is None:
        version_path = os.path.join(os.getcwd(), VERSION_FILENAME)
    else:
        if os.path.isdir(version_path):
            version_path = os.path.join(version_path, VERSION_FILENAME)
        else:
            version_path = os.path.join(version_path)

    # Check if the project has a version template
    template_path = os.path.join(os.path.dirname(version_path), '_version.py.template')
    if os.path.exists(template_path):
        with open(template_path, mode='rb') as template_file:
            version_py_template = template_file.read()
    else:
        version_py_template = VERSION_PY

    try:
        p = subprocess.Popen(["git", "describe", "--tags", "--dirty", "--always"],
                             stdout=subprocess.PIPE)
    except EnvironmentError:
        print GIT_RUN_FAIL_MSG % version_path
        return
    stdout = p.communicate()[0]
    if p.returncode != 0:
        print GIT_RUN_FAIL_MSG % version_path
        return
    if stdout.startswith(git_tag_prefix):
        ver = stdout[len(git_tag_prefix):].strip()
    else:
        ver = stdout.strip()
    with open(version_path, 'wb') as f:
        today = sysdate.today()
        f.write(version_py_template.format(version=ver,
                                           year=today.year,
                                           month=today.month,
                                           day=today.day,
                                           time=time.time()))
    print "set %s to '%s'" % (version_path, ver)


def get_version(version_path=None):
    if version_path is None:
        version_path = os.path.join(os.getcwd(), VERSION_FILENAME)
    else:
        version_path = os.path.join(version_path)

    try:
        f = open(version_path)
    except EnvironmentError:
        return None
    for line in f.readlines():
        mo = re.match("__version__ = '([^']+)'", line)
        if mo:
            ver = mo.group(1)
            return ver
    return None


#noinspection PyUnboundLocalVariable
def get_version_path(distcmd):
    if len(distcmd.distribution.package_data) == 1:
        version_path = os.path.join(os.getcwd(), distcmd.distribution.package_data.keys()[0], VERSION_FILENAME)
    elif len(distcmd.distribution.package_data) > 1:
        for tmp_path in distcmd.distribution.package_data.keys():
            test_path = os.path.join(os.getcwd(), tmp_path, VERSION_FILENAME)
            if os.path.exists(test_path):
                version_path = test_path
                break
            elif os.path.exists(os.path.dirname(test_path)):
                version_path = os.path.join(os.path.dirname(test_path), VERSION_FILENAME)
            else:
                version_path = os.path.join(os.getcwd(), distcmd.distribution.package_data.keys()[0], VERSION_FILENAME)
    else:
        packages = [pkg for pkg in distcmd.distribution.packages if not '.' in pkg]
        if len(packages) == 1:
            version_path = os.path.join(os.getcwd(), packages[0], VERSION_FILENAME)
        else:
            raise Exception("Couldn't find appropriate version_path.")

    return version_path


class Version(Command):
    description = "update %s from Git repo" % VERSION_FILENAME
    user_options = [('version-path=', 'f',
                     "path to version file to update [default: %s]" % VERSION_FILENAME),
                    ('tag-prefix', 't',
                     "git tag prefix to use [default: 'v']")]
    boolean_options = []

    def initialize_options(self):
        self.version_path = None
        self.tag_prefix = 'v'

    def finalize_options(self):
        if self.version_path is None:
            self.version_path = get_version_path(self)
        print self.version_path

    def run(self):
        update_version_py(git_tag_prefix=self.tag_prefix, version_path=self.version_path)
        print "Version is now", get_version(version_path=self.version_path)


class sdist(_sdist):
    def run(self):
        update_version_py(version_path=get_version_path(self))
        # unless we update this, the sdist command will keep
        # using the old version
        self.distribution.metadata.version = get_version(get_version_path(self))
        return _sdist.run(self)


cmdclassdict = {
    'version': Version,
    'sdist': sdist
}


def get_install_requirements():
    requirements = []
    with open('requirements.txt') as file_:
        temp = file_.readlines()
        temp = [i[:-1] for i in temp]

        for line in temp:
            if line is None or line == '' or line.startswith(('#', '-e', 'git+', 'hg+')):
                continue
            else:
                requirements.append(line)
        return requirements


def get_readme():
    with open('README.md') as file_:
        return file_.read()
