# coding=utf-8
from collections import namedtuple
from datetime import datetime, date as sysdate
import os
import re
from subprocess import Popen, PIPE
import time
from distutils.command.sdist import sdist as _sdist
from distutils.core import Command

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

# Inspired by https://github.com/warner/python-ecdsa/blob/0ed702a9d4057ecf33eea969b8cf280eaccd89a1/setup.py#L34
# and https://gist.github.com/dcreager/300803

VersionTuple = namedtuple('VersionTuple', ['major', 'minor', 'patch', 'dev', 'local'])
git_describe_regex = re.compile(
    r'''
^
v?
(?:(?P<major>\d+)\.?)
(?:(?P<minor>\d+)?\.?)
(?:(?P<patch>\d+)?)
(?P<prerelease>-(?P<commit_count>\d+)-(?P<commit>[a-z0-9]*)(-(?P<dirty>\w*))?)?
(\+(?P<build>[\.0-9A-Za-z-]*))?
$
''', re.VERBOSE)

pep440_regex = re.compile(r'''
^
v?
(?:(?P<epoch>\d+)!)?
(?P<major>\d+)
(?:\.(?P<minor>\d+))?
(?:\.(?P<patch>\d+))?
(?P<prereleasetype>a|b|rc)?
(?P<prereleaseversion>\d+)?
(?:\.post(?P<post>\d+))?
(?:\.dev(?P<dev>\d+))?
(\+(?P<local>[\.0-9A-Za-z-]*))?
$
''', re.VERBOSE)


class VersionClass(object):
    def __init__(self, version_string='0.0.1', the_date=None, the_time=None):
        self._original_version_string = version_string
        self._version_tuple = self._parse_tuple(version_string)
        if the_time is None:
            the_time = datetime.utcnow()
        if the_date is None:
            the_date = the_time.date
        self.time = the_time
        self.date = the_date

        self.datetime = the_time

    @property
    def string(self):
        return self.public_version_string

    @property
    def public_version_string(self):
        if self.dev_string:
            return '.'.join((self.patch_string, self.dev_string))
        else:
            return self.patch_string

    @property
    def local_version_string(self):
        if self.tuple.local:
            return self.public_version_string + '+' + self.tuple.local
        else:
            return self.public_version_string

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
        return '.'.join(self.tuple[0:3])

    @property
    def dev_string(self):
        dev_str = 'dev'
        if self.tuple.dev:
            return dev_str + self.tuple.dev
        else:
            return ''

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
        # try to parse using git describe
        if git_describe_regex.match(ver_string):
            ver = git_describe_regex.search(ver_string).groupdict()
            dev = ver['commit_count'] or ''
            local = ver['commit'] or ''
        # fall back to pep440 parsing
        elif pep440_regex.match(ver_string):
            ver = pep440_regex.search(ver_string).groupdict()
            dev = ver['dev'] or ''
            local = ver['local'] or ''
        else:
            raise ValueError("Couldn't parse version string: %s" % ver_string)

        major = ver['major'] or '0'
        minor = ver['minor'] or '0'
        patch = ver['patch'] or '0'
        return VersionTuple(major, minor, patch, dev, local)

    def __unicode__(self):
        return self.string

    __str__ = __unicode__
    __repr__ = __unicode__

VERSION_FILENAME = '_version.py'
VERSION_PY_TEMPLATE = VERSION_FILENAME + '.template'
VERSION_PY_DEFAULT = """# coding=utf-8
from datetime import date, datetime
from propane_distribution import VersionClass

# This file is originally generated from Git information by running 'setup.py
# version'. Distributions contain a pre-generated copy of this file.

__version__ = '{version}'
__date__ = date({year}, {month}, {day})
__time__ = datetime.utcfromtimestamp({time})

version = VersionClass(__version__, __date__, __time__)
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
    template_path = os.path.join(os.path.dirname(version_path), VERSION_PY_TEMPLATE)
    if os.path.exists(template_path):
        with open(template_path, mode='rb') as template_file:
            version_py_template = template_file.read()
    else:
        version_py_template = VERSION_PY_DEFAULT

    try:
        p = Popen(["git", "describe", "--tags", "--always", "--dirty"],
                  stdout=PIPE)
    except EnvironmentError:
        print GIT_RUN_FAIL_MSG % version_path
        return
    stdout = p.communicate()[0]
    if p.returncode != 0:
        print GIT_RUN_FAIL_MSG % version_path
        return
    if stdout.startswith(git_tag_prefix):
        ver_raw = stdout[len(git_tag_prefix):].strip()
    else:
        ver_raw = stdout.strip()
    ver = VersionClass(ver_raw).local_version_string
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


# noinspection PyUnboundLocalVariable
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
        packages = [pkg for pkg in distcmd.distribution.packages if '.' not in pkg]
        if len(packages) == 1:
            version_path = os.path.join(os.getcwd(), packages[0], VERSION_FILENAME)
        else:
            raise Exception("Couldn't find appropriate version_path.")

    return version_path


# noinspection PyAttributeOutsideInit
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


# noinspection PyPep8Naming
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


def main():
    v = VersionClass('v0.5.1.dev87')
    pass


if __name__ == '__main__':
    main()
