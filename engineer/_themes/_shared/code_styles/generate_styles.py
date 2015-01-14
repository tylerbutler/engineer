# coding=utf-8
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.styles import get_all_styles

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

'''
Run this script to output all registered Pygments styles as flat CSS files in the current directory.

Other styles that can be installed using pip:

pygments-style-github
pygments-style-railscasts

And some can be installed/downloaded manually...

https://github.com/john2x/solarized-pygment
https://github.com/brolewis/pygments_zenburn
https://github.com/oblique/pygments-style-behelit
https://github.com/idleberg/base16-pygments

'''


def main():
    for style in get_all_styles():
        formatter = HtmlFormatter(style=style)
        css = formatter.get_style_defs()
        filename = '%s.css' % style
        with open(filename, mode='wb') as the_file:
            the_file.writelines(css)
        print "Output %s" % filename

if __name__ == '__main__':
    main()
