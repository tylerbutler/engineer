# coding=utf-8
import humanize
import re
import times
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


def localtime(value, tz=None):
    from engineer.conf import settings

    if tz is None:
        tz = settings.POST_TIMEZONE

    return times.to_local(value, tz)


def naturaltime(value):
    from engineer.conf import settings

    server_time = localtime(value, settings.SERVER_TIMEZONE).replace(tzinfo=None)
    friendly = humanize.naturaltime(server_time)
    return friendly
