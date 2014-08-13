# coding=utf-8
from argh import ArghParser

from engineer.devtools.theme_tools import compile_theme, list_theme
from engineer.log import bootstrap
from engineer.plugins import load_plugins


__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

bootstrap()
load_plugins()
parser = ArghParser()
parser.add_commands([compile_theme, list_theme], namespace='themes', title='Theme commands')


def main():
    parser.dispatch()
