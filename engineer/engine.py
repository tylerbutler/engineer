# coding=utf-8
import argparse
import logging
import os
import sys
import time

from path import path

from engineer.commands import all_commands, common_parser
from engineer.log import get_console_handler, bootstrap
from engineer.plugins import load_plugins
from engineer.util import relpath, compress, has_files, diff_dir
from engineer import version


try:
    # noinspection PyPep8Naming
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


def get_argparser():
    # from engineer.commands.argh import PrintArghCommand
    desc = "Engineer static site builder. [v%s, %s %s]" % (version, version.date, time.strftime('%X', version.time))
    top_level_parser = argparse.ArgumentParser(prog='engineer',
                                               description=desc,
                                               formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = top_level_parser.add_subparsers(title="subcommands",
                                                 dest='parser_name')

    for command_class in all_commands():
        instance = command_class(subparsers, top_level_parser)
        instance.setup_command()

    return top_level_parser


def parse_override_args(extra_args):
    override = {}
    override_settings_indexes = [i for i, j in enumerate(extra_args) if j.startswith('--')]
    for index, item in enumerate(override_settings_indexes):
        v2 = override_settings_indexes[index + 1] if (index + 1) < len(override_settings_indexes) else len(extra_args)
        r = range(item + 1, v2)
        for _ in r:
            values = [extra_args[v] for v in r]
            if len(values) == 1:
                values = values[0]
            override[extra_args[item][2:].upper()] = values
    return override


def cmdline(args=sys.argv):
    # bootstrap logging
    bootstrap()

    # Load all plugins
    load_plugins()

    skip_settings = []
    args, extra_args = get_argparser().parse_known_args(args[1:])

    # Handle common parameters if they're present
    common_args, extra_args = common_parser.parse_known_args(extra_args)

    override = parse_override_args(extra_args)

    verbose = getattr(args, 'verbose', common_args.verbose)
    config_file = getattr(args, 'config_file', common_args.config_file)

    logger = logging.getLogger('engineer')
    if verbose >= 2:
        logger.removeHandler(get_console_handler(logging.WARNING))
        logger.addHandler(get_console_handler(logging.DEBUG))
    elif verbose == 1:
        logger.removeHandler(get_console_handler(logging.WARNING))
        logger.addHandler(get_console_handler(logging.INFO))
    else:
        pass  # WARNING level is added by default in bootstrap method

    if args.parser_name in skip_settings or (hasattr(args, 'need_settings') and not args.need_settings):
        pass
    else:  # try loading settings
        try:
            from engineer.conf import settings

            if config_file is None:
                default_settings_file = path.getcwd() / 'config.yaml'
                logger.info("No '--settings' parameter specified, defaulting to %s." % default_settings_file)
                settings.reload(default_settings_file, override)
            else:
                settings.reload(config_file, override)
        except Exception as e:
            logger.error(e.message)
            exit()

    # noinspection PyBroadException
    try:
        if hasattr(args, 'function'):
            args.function(args)
        elif hasattr(args, 'func'):
            args.func(args)
        elif hasattr(args, 'handler_function'):
            args.handler_function(args)
        else:
            args.handle(args)
    except Exception as e:
        logger.exception("Unexpected error: %s" % e.message)

    exit()
