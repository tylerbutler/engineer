# coding=utf-8
from __future__ import absolute_import
import argparse

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


# noinspection PyProtectedMember
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
    Mixin class that provides the basic implementation shared by all command plugins.
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

        The built-in Engineer commands all use this approach. You can see the source for those classes in the
        :mod:`engineer.commands.bundled` module.
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


_settings_parser = argparse.ArgumentParser(add_help=False,
                                           description=argparse.SUPPRESS,
                                           usage=argparse.SUPPRESS)
_settings_parser.add_argument('-s', '--config', '--settings',
                              dest='config_file',
                              default=None,
                              help="Specify a configuration file to use.")

_verbose_parser = argparse.ArgumentParser(add_help=False,
                                          description=argparse.SUPPRESS,
                                          usage=argparse.SUPPRESS)
_verbose_parser.add_argument('-v', '--verbose',
                             dest='verbose',
                             action='count',
                             default=0,
                             help="Display verbose output.")

common_parser = argparse.ArgumentParser(add_help=False,
                                        description=argparse.SUPPRESS,
                                        usage=argparse.SUPPRESS,
                                        parents=[_verbose_parser, _settings_parser])


# noinspection PyShadowingBuiltins,PyAbstractClass
class _ArgparseMixin(_CommandMixin):
    _name = None
    _help = None
    _need_settings = True
    _need_verbose = True

    @property
    def name(self):
        """The name of the command."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def help(self):
        """The help string for the command."""
        return self._help

    @help.setter
    def help(self, value):
        self._help = value

    @property
    def need_settings(self):
        """Defaults to True. Set to False if the command does not require an Engineer config file."""
        return self._need_settings

    @need_settings.setter
    def need_settings(self, value):
        self._need_settings = value

    @property
    def need_verbose(self):
        """
        Defaults to True. Set to False if the command does not support the standard Engineer
        :option:`verbose<engineer -v>` option.
        """
        return self._need_verbose

    @need_verbose.setter
    def need_verbose(self, value):
        self._need_verbose = value

    @property
    def parser(self):
        """Returns the appropriate parser to use for adding arguments to your command."""
        if self._command_parser is None:
            parents = []
            if self.need_verbose:
                parents.append(_verbose_parser)
            if self.need_settings:
                parents.append(_settings_parser)

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


# noinspection PyAbstractClass
class ArgparseCommand(_ArgparseMixin):
    """
    Serves as a base class for simple argparse-based commands. All built-in Engineer commands, such as
    :ref:`engineer clean`, are examples of this type of command. See the source for the classes in the
    :mod:`engineer.commands.bundled` module for a specific example.
    """
    __metaclass__ = CommandMount

    def add_arguments(self):
        pass


if argh_installed:
    class ArghCommand(_ArgparseMixin):
        """
        ..  warning::
            The ``@verbose`` and ``@settings`` decorators should not be used in subclasses. Use the
            :attr:`~engineer.commands.core.ArgparseCommand.need_verbose` and
            :attr:`~engineer.commands.core.ArgparseCommand.need_settings` attributes in subclasses instead.
        """
        __metaclass__ = CommandMount

        handler_function = None

        def add_arguments(self):
            from argh.helpers import set_default_command

            if self.handler_function is not None:
                set_default_command(self.parser, self.handler_function)


# noinspection PyAbstractClass
class Command(_CommandMixin):
    """
    The most barebones command plugin base class. You should use :class:`~engineer.commands.core.ArgparseCommand`
    or :class:`~engineer.commands.core.ArghCommand` wherever possible.
    """
    __metaclass__ = CommandMount
