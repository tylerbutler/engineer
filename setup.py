# coding=utf-8
from distutils.core import setup
from setuptools import find_packages

def get_install_requirements():
    requirements = []
    with open('requirements.txt') as file:
        temp = file.readlines()
        temp = [i[:-1] for i in temp]

        for line in temp:
            if line is None or line == '' or line.startswith('#'):
                continue
            else:
                requirements.append(line)
        return requirements


def get_readme():
    with open('README.txt') as file:
        return file.read()

setup(
    name='engineer',
    version='0.1.0',
    author='Tyler Butler',
    author_email='tyler@tylerbutler.com',
    packages=find_packages(),
    scripts=['build.py'],
    #url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='A static blog engine.',
    long_description=get_readme(),
    install_requires=get_install_requirements(),
    zip_safe=True, # Setting to False doesn't create an egg - easier to debug and hack on
    include_package_data=True,
    )
