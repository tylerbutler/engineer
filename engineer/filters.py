# coding=utf-8
import re
from markdown import markdown
from typogrify.templatetags import jinja2_filters

__author__ = 'tyler@tylerbutler.com'

def format_datetime(value, format_string='%Y-%m-%d'):
    return value.strftime(format_string)


def markdown_filter(value, typogrify=True, extensions=('extra', 'codehilite')):
    match = re.match(r'\s*', value)
    s, e = match.span()
    pattern = r'\n {%s}' % (e - s - 1)
    output = re.sub(pattern, r'\n', value)
    if typogrify:
        return jinja2_filters.typogrify(markdown(output, extensions=extensions))
    else:
        return markdown(output, extensions=extensions)
