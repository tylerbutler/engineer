# coding=utf-8
import argparse

from brownie.caching import cached_property

from engineer.plugins import PluginMixin

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


# noinspection PyMissingConstructor
class CommandMount(type):
    """A metaclass used to identify :ref:`commands`."""

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'commands'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new command type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.commands = []
        else:
            # This must be a command implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.commands.append(cls)


def all_commands():
    import sys
    import inspect

    classes = [c[1] for c in inspect.getmembers(sys.modules[__name__], inspect.isclass)
               if c[1].__class__ == CommandMount]
    commands = []
    for klass in classes:
        commands.extend(klass.commands)
    return sorted(commands)


class _CommandMixin(PluginMixin):
    def __init__(self, main_parser, top_level_parser=None):
        self._main_parser = main_parser
        self._top_level_parser = top_level_parser
        self._command_parser = None

    def setup_command(self):
        raise NotImplementedError()

    def handle(self, args=None):
        raise NotImplementedError()


# noinspection PyShadowingBuiltins
class _ArgParseMixin(_CommandMixin):
    name = None
    help = None
    need_settings = False
    need_settings = True

    @cached_property
    def parser(self):
        if self._command_parser is None:
            parents = [verbose_parser]
            if self.need_settings:
                parents.append(settings_parser)

            self._command_parser = self._main_parser.add_parser(self.name,
                                                                help=self.help,
                                                                parents=parents,
                                                                formatter_class=argparse.RawDescriptionHelpFormatter)
        return self._command_parser

    def setup_command(self):
        self.add_arguments()
        self._finalize()

    def add_arguments(self):
        return False

    def _finalize(self):
        if not self.parser.get_default('handle'):
            self.parser.set_defaults(handle=self.handle)
        self.parser.set_defaults(need_settings=self.need_settings)


settings_parser = argparse.ArgumentParser(add_help=False,
                                          description=argparse.SUPPRESS,
                                          usage=argparse.SUPPRESS)
settings_parser.add_argument('-s', '--config', '--settings',
                             dest='config_file',
                             default=None,
                             help="Specify a configuration file to use.")

verbose_parser = argparse.ArgumentParser(add_help=False,
                                         description=argparse.SUPPRESS,
                                         usage=argparse.SUPPRESS)
verbose_parser.add_argument('-v', '--verbose',
                            dest='verbose',
                            action='count',
                            default=0,
                            help="Display verbose output.")

common_parser = argparse.ArgumentParser(add_help=False,
                                        description=argparse.SUPPRESS,
                                        usage=argparse.SUPPRESS,
                                        parents=[verbose_parser, settings_parser])


class ArgParseCommand(_ArgParseMixin):
    __metaclass__ = CommandMount


class Command(_CommandMixin):
    __metaclass__ = CommandMount
