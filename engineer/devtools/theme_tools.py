# coding=utf-8
from tempfile import mkdtemp

# noinspection PyPackageRequirements
from argh import named
# noinspection PyPackageRequirements
from clint.textui import colored, indent, puts
# noinspection PyPackageRequirements
from clint.textui import columns
from path import path
from engineer.log import bootstrap


__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


bootstrap()


# noinspection PyShadowingBuiltins
@named('compile')
def compile_theme(theme_id=None):
    """Compiles a theme."""
    from engineer.processors import convert_less
    from engineer.themes import ThemeManager

    if theme_id is None:
        themes = ThemeManager.themes().values()
    else:
        themes = [ThemeManager.theme(theme_id)]

    with(indent(2)):
        puts(colored.yellow("Compiling %s themes." % len(themes)))

        for theme in themes:
            theme_output_path = (theme.static_root / ('stylesheets/%s_precompiled.css' % theme.id)).normpath()

            puts(colored.cyan("Compiling theme %s to %s" % (theme.id, theme_output_path)))
            with indent(4):
                puts("Compiling...")
                convert_less(theme.static_root / ('stylesheets/%s.less' % theme.id),
                             theme_output_path,
                             minify=True)
                puts(colored.green("Done.", bold=True))


# noinspection PyShadowingBuiltins
@named('list')
def list_theme():
    """List all available Engineer themes."""
    from engineer.themes import ThemeManager

    themes = ThemeManager.themes()
    col1, col2 = map(max, zip(*[(len(t.id) + 2, len(t.root_path) + 2) for t in themes.itervalues()]))

    themes = ThemeManager.themes_by_finder()
    for finder in sorted(themes.iterkeys()):
        if len(themes[finder]) > 0:
            puts("%s: " % finder)
            for theme in sorted(themes[finder], key=lambda _: _.id):
                with indent(4):
                    puts(
                        columns(
                            [colored.cyan("%s:" % theme.id), col1],
                            [colored.white(theme.root_path, bold=True), col2]
                        )
                    )


if __name__ == '__main__':
    compile_theme()
