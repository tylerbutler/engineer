# coding=utf-8
from tempfile import mkdtemp

from argh import arg, named
from path import path

from engineer.processors import convert_less
from engineer.themes import ThemeManager

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


# noinspection PyShadowingBuiltins
@named('compile')
def compile_theme(theme_id=None, output_dir=None):
    """Compiles a theme."""
    if output_dir is None:
        output_dir = mkdtemp()
    output_dir = path(output_dir)

    if theme_id is not None:
        themes = [ThemeManager.theme(theme_id)]
    else:
        themes = ThemeManager.themes().values()

    for theme in themes:
        print "Compiling theme: %s" % theme.id
        temp_theme_output_path = path(output_dir / theme.id)
        theme_output_path = theme.static_root / 'stylesheets/%s_precompiled.css' % theme.id
        theme.copy_all_content(temp_theme_output_path)

        convert_less(temp_theme_output_path / 'stylesheets/%s.less' % theme.id,
                     theme_output_path,
                     minify=True)
        print "Done!"


# noinspection PyShadowingBuiltins
@named('list')
def list_theme():
    """List all available Engineer themes."""
    for theme in ThemeManager.themes().itervalues():
        print "%s: %s" % (theme.id, theme.root_path)
