# coding=utf-8
from __future__ import absolute_import
import argparse

from brownie.caching import cached_property

from engineer.commands.argh_helpers import argh_installed
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
    commands.sort(key=lambda cmd: cmd._name_checked())
    return commands


class _CommandMixin(PluginMixin):
    """
    Engineer's command processing is built using argparse. One of Argparse's 'quirks,' or design
    decisions/constraints, is that it is not easy to access subparsers arbitrarily. Essentially, you can only
    parsers very early on in the process of building the argparse objects. Thus, all command plugins are passed
    a ``main_parser``, which is the main ArgumentParser object, when they are instantiated. In addition,
    they are passed the top-most ``subparser`` object, created by initially calling ``add_subparsers`` on the main
    ArgumentParser object. With these two components, it is possible to manipulate the commands in diverse ways.

    Fortunately, for the most part, plugin implementers needn't be concerned with this detail, since it is abstracted
    away by the :class:`~engineer.commands.core._CommandMixin` class and other subclasses.
    """
    def __init__(self, main_parser, top_level_parser=None):
        self._main_parser = main_parser
        self._top_level_parser = top_level_parser
        self._command_parser = None

    def setup_command(self):
        """
        Called by Engineer immediately after instantiating the command class.

        Override this method to run any unique logic that needs to be run prior to using the command. You should do
        this instead of overriding the constructor.

        Note that this method is overridden already in
        """
        raise NotImplementedError()

    def handler_function(self, args=None):
        """
        This function contains your actual command logic. Note that if you prefer, you can implement your command
        function with a different name and simply set ``handler_function`` to be the function you defined. In other
        words:

        .. code-block:: python

            def my_function(*args, **kwargs):
                # my implementation
                pass

            handler_function = my_function

        """
        raise NotImplementedError()

    @classmethod
    def _name_checked(cls):
        if hasattr(cls, 'argh_name'):
            return cls.argh_name

        if hasattr(cls, 'name'):
            return cls.name

        if hasattr(cls, 'namespace'):
            return cls.namespace

        return 'NO_COMMAND_NAME'


# noinspection PyShadowingBuiltins
class _ArgParseMixin(_CommandMixin):
    name = None
    """The name of the command."""

    help = None
    """The help string for the command."""

    need_settings = True
    """Set to True if the command requires an Engineer config file."""

    need_verbose = True
    """Set to True if the command supports the standard Engineer ``verbose`` option."""

    @cached_property
    def parser(self):
        """Returns the appropriate parser to use for adding arguments to your command."""
        if self._command_parser is None:
            parents = []
            if self.need_verbose:
                parents.append(verbose_parser)
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
        """Override this method in subclasses to add arguments to parsers as needed."""
        raise NotImplementedError()

    def _finalize(self):
        if not self.parser.get_default('handle'):
            self.parser.set_defaults(handler_function=self.handler_function)
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


if argh_installed:
    class SimpleArghCommand(_ArgParseMixin):
        """
        The ``@verbose`` and ``@settings`` decorators should not be used in subclasses. Use the
        :attr:`~engineer.commands.core._ArgParseMixin.need_verbose` and
        :attr:`~engineer.commands.core._ArgParseMixin.need_settings` attributes in subclasses instead.
        """
        __metaclass__ = CommandMount

        handler_function = None

        def add_arguments(self):
            from argh.helpers import set_default_command

            if self.handler_function is not None:
                set_default_command(self.parser, self.handler_function)


class Command(_CommandMixin):
    """
    The most barebones command plugin base class. You should use :class:`~engineer.commands.core.ArgParseCommand`
    or :class:`~engineer.commands.core.SimpleArghCommand` wherever possible.
    """
    __metaclass__ = CommandMount
