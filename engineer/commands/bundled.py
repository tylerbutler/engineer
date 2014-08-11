# coding=utf-8
from __future__ import absolute_import

from path import path

from engineer.commands.core import ArgParseCommand


__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


# noinspection PyShadowingBuiltins
class BuildCommand(ArgParseCommand):
    name = 'build'
    help = 'Build the site.'

    def add_arguments(self):
        self.parser.add_argument('-c', '--clean',
                                 dest='clean',
                                 action='store_true',
                                 help="Clean the output directory and clear all the caches before building.")
        self.parser.set_defaults(handle=self.build)

    def build(self, args=None):
        # Build command implementation goes here.
        pass


# noinspection PyShadowingBuiltins
class CleanCommand(ArgParseCommand):
    name = 'clean'
    help = "Clean the output directory and clear all caches."

    def clean(self, args=None):
        # Clean command implementation goes here.
        pass

    handle = clean


# noinspection PyShadowingBuiltins
class ServeCommand(ArgParseCommand):
    name = 'serve'
    help = "Start the development server."

    def add_arguments(self):
        self.parser.add_argument('-p', '--port',
                                 type=int,
                                 default=8000,
                                 dest='port',
                                 help="The port the development server should listen on.")

    def handle(self, args=None):
        # Serve command implementation goes here.
        pass


# noinspection PyShadowingBuiltins
class InitCommand(ArgParseCommand):
    name = 'init'
    help = "Initialize the current directory as an engineer site."
    need_settings = False

    def add_arguments(self):
        self.parser.add_argument('--no-sample',
                                 dest='no_sample',
                                 action='store_true',
                                 help="Do not include sample content.")
        self.parser.add_argument('--force', '-f',
                                 dest='force',
                                 action='store_true',
                                 help="Delete target folder contents. Use with caution!")

    def handle(self, args=None):
        # Init command implementation goes here.
        pass


# noinspection PyShadowingBuiltins
class EmmaCommand(ArgParseCommand):
    name = 'emma'
    help = "Start Emma, the built-in management server."

    def add_arguments(self):
        self.parser.add_argument('-p', '--port',
                                 type=int,
                                 default=8080,
                                 dest='port',
                                 help="The port Emma should listen on.")
        self.parser.add_argument('--prefix',
                                 type=str,
                                 dest='prefix',
                                 help="The prefix path the Emma site will be rooted at.")
        emma_options = self.parser.add_mutually_exclusive_group(required=True)
        emma_options.add_argument('-r', '--run',
                                  dest='run',
                                  action='store_true',
                                  help="Run Emma.")
        emma_options.add_argument('-g', '--generate',
                                  dest='generate',
                                  action='store_true',
                                  help="Generate a new secret location for Emma.")
        emma_options.add_argument('-u', '--url',
                                  dest='url',
                                  action='store_true',
                                  help="Get Emma's current URL.")

    def handle(self, args=None):
        # Emma command implementation goes here.
        pass
