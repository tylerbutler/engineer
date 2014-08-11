# coding=utf-8
from __future__ import absolute_import

from path import path

from engineer.commands.argh_helpers import argh_installed

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

_no_need_settings_registry = []

if argh_installed:
    from argh.decorators import arg, named
    from engineer.commands.core import Command, SimpleArghCommand

    def need_settings(needed=True):
        def wrapper(func):
            if not needed:
                _no_need_settings_registry.append(func)
            return func
        return wrapper

    class PrintArghCommand(SimpleArghCommand):
        """
        A simple example command using Argh.

        This example inherits from :class:`~engineer.commands.SimpleArghCommand` and exposes a single function
        as an Engineer command.
        """

        name = 'echo'
        help = "Echo a command line argument if argh is installed."
        need_settings = False

        @arg('name')
        @arg('-t', '--test', default=False)
        def print_argh(self, args):
            print "Argh is installed! %s! %s" % (args.name, '(test)' if args.test else '')

        handler_function = print_argh

    class SimplePrintSettings(SimpleArghCommand):
        @named('sps')
        @arg('-t', '--test', default=False)
        def print_settings(self, args):
            """[SIMPLE] Prints the currently loaded Engineer settings."""
            from engineer.conf import settings
            print "test: %s" % args.test
            print "verbose: %s" % args.verbose

            print settings

        name = print_settings.argh_name if hasattr(print_settings, 'argh_name') else 'print_settings'
        help = print_settings.__doc__
        handler_function = print_settings

    # class ArghSamplePlugin2(Command):
    #     """
    #     A more complex example command plugin using Argh.
    #
    #     This example inherits from :class:`~engineer.commands.Command` and exposes two separate functions
    #     as Engineer commands. Both commands are top-level commands.
    #
    #     This example shows a number of things:
    #
    #     1. How to use the ``@named`` decorator from argh to rename the function. Note that in order to use this
    #        properly, you need to pass the ``argh_name`` property to the ``main_parser`` as the function name.
    #     2. How to use the ``@verbose`` and ``@settings`` decorators to automatically add those
    #        parameters to a custom command.
    #     3. How to pass the ``__name__`` and ``__doc__`` properties to the ``main_parser``.
    #     4. How to pass the ``need_settings`` property to subparsers so that Engineer does not try to load settings
    #        files when executing a command.
    #     """
    #
    #     from argh.decorators import arg, named
    #
    #     @staticmethod
    #     @named('argh_function')
    #     @arg('-t', '--test', default=False)
    #     @arg('--format', choices=['json', 'yaml'], default='json', help='The format to use.')
    #     @verbose
    #     def function1(args):
    #         """A sample command."""
    #         print "function1 called."
    #         print "test: %s" % args.test
    #         print "verbose: %s" % args.verbose
    #
    #     @staticmethod
    #     @arg('-t', '--test', default=False)
    #     @verbose
    #     @settings
    #     def print_settings(args):
    #         """Prints the currently loaded Engineer settings."""
    #         from engineer.conf import settings
    #         if args.test:
    #             print "test: true"
    #         else:
    #             print "test: false"
    #         print "verbose: %s" % args.verbose
    #
    #         print settings
    #
    #     def setup_command(self):
    #         from argh.helpers import set_default_command
    #
    #         parser = self._main_parser.add_parser(self.function1.argh_name, help=self.function1.__doc__)
    #         parser.set_defaults(need_settings=False)  # needed to tell engineer not to try loading settings
    #         set_default_command(parser, self.function1)
    #
    #         second_parser = self._main_parser.add_parser(self.print_settings.__name__,
    # help=self.print_settings.__doc__)
    #         second_parser.set_defaults(need_settings=True)
    #         set_default_command(second_parser, self.print_settings)

    settings = arg('-s', '--config', '--settings',
                   dest='config_file',
                   default=None,
                   help="Specify a configuration file to use.")
    verbose = arg('-v', '--verbose',
                  dest='verbose',
                  action='count',
                  default=0,
                  help="Display verbose output.")

    class PrintSettingsArghCommand(Command):
        @named('ps')
        @arg('-t', '--test', default=False)
        @settings
        @verbose
        def print_settings(self, args):
            """Prints the currently loaded Engineer settings."""
            from engineer.conf import settings
            print "test: %s" % args.test
            print "verbose: %s" % args.verbose

            print settings

        def setup_command(self):
            from argh.helpers import set_default_command

            parser = self._main_parser.add_parser(self.print_settings.argh_name, help=self.print_settings.__doc__)
            parser.set_defaults(need_settings=True)
            set_default_command(parser, self.print_settings)

    # noinspection PyShadowingBuiltins,PyUnusedLocal
    class ArghSamplePlugin3(Command):
        from argh.decorators import arg, expects_obj, named

        namespace = 'argh3'

        @staticmethod
        @named('f1')
        @verbose
        @settings
        def requires_settings(format='json', input_path=path.getcwd(),
                              output_path=path.getcwd() / 'imported_posts', **kwargs):
            args = format
            print 'format: %s' % args.format
            print 'input_path: %s' % args.input_path
            print 'output_path: %s' % args.output_path
            print 'verbose: %s' % args.verbose

        @staticmethod
        @named('ns')
        @expects_obj
        #@verbose
        @need_settings(False)
        @arg('--format', choices=['json'], default='json', help='The format of the posts to import.')
        def no_settings_required(args):
            print 'format: %s' % args.format
            print 'verbose: %s' % args.verbose

        def setup_command(self):
            from argh.assembling import add_commands, get_subparsers

            add_commands(self._top_level_parser, [self.requires_settings, self.no_settings_required],
                         namespace=self.namespace,
                         description='argh sample 3',
                         title='argh sample 3',
                         help='argh sample command group')
            r = get_subparsers(self._top_level_parser).choices[self.namespace]
            r = get_subparsers(r)
            for k, parser in r.choices.iteritems():
                if parser._defaults['function'] in _no_need_settings_registry:
                    parser.set_defaults(need_settings=False)
