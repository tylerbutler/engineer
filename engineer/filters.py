# coding=utf-8
import humanize
import logging
import re
import times
from markdown import markdown
from path import path
from typogrify import filters as Typogrify
from typogrify.templatetags import jinja_filters

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

logger = logging.getLogger(__name__)

def format_datetime(value, format_string='%Y-%m-%d'):
    return value.strftime(format_string)


def markdown_filter(value, typogrify=True, extensions=('extra', 'codehilite')):
    """
    A smart wrapper around the ``markdown`` and ``typogrify`` functions that automatically removes leading
    whitespace before every line. This is necessary because Markdown is whitespace-sensitive. Consider some Markdown
    content in a template that looks like this:

    ..  codeblock:: html+jinja
        <article>
            {% filter markdown %}
                ## A Heading

                Some content here.

                    Code goes here.
                    More lines of code
                    And more.

                Closing thoughts
            {% endfilter %}
        </article>

    In this example, a typical Markdown filter would see the leading whitespace before the first heading and assume
    it was a code block, which would then cause the entire Markdown document to be rendered incorrectly. You may have
    a document with spacing like this because your text editor automatically 'pretty-prints' the markup,
    including the content within the filter tag.

    This filter automatically removes the leading whitespace - leaving code block and other expected offsets in place
    of course - so that rendering occurs correctly regardless of the nested spacing of the source document.
    """

    # Determine how many leading spaces there are, then remove that number from the beginning of each line.
    match = re.match(r'(\n*)(\s*)', value)
    s, e = match.span(2)
    pattern = re.compile(r'^ {%s}' % (e - s), # use ^ in the pattern so mid-string matches won't be removed
                         flags=re.MULTILINE) # use multi-line mode so ^ will match the start of each line
    output = pattern.sub(u'', value)
    if typogrify:
        return jinja_filters.typogrify(markdown(output, extensions=extensions))
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


def compress(value):
    from engineer.conf import settings

    if not settings.COMPRESSOR_ENABLED:
        return value
    else: # COMPRESSOR_ENABLED == True
        import html5lib

        def _min_js_slim(js_string):
            # NOTE: The slimit filter seems to break some scripts. I'm not sure why. I'm leaving this code in for
            # posterity, but it's not functional right now and shouldn't be used.
            from slimit import minify

            return minify(js_string)

        doc = html5lib.parseFragment(value.strip())
        to_compress = [l for l in doc.childNodes if
                       l.name in ('link', 'script')]

        for item in to_compress:
            if item.name == 'link':
                src = item.attributes['href']
                compression_type = 'css'
            elif item.name == 'script':
                if 'src' in item.attributes:
                    src = item.attributes['src']
                    compression_type = 'js'
                else: # inline script
                    continue
                    # TODO: Inline script minification.
                    #has_inline = True
                    #if len(item.childNodes) > 1:
                    #    raise Exception("For some reason the inline script node has more than one child node.")
                    #else:
                    #    item.childNodes[0].value = _min_js(item.childNodes[0].value)
            else:
                raise Exception("Hmmm, wasn't expecting a '%s' here." % item.name)

            if src.startswith(settings.HOME_URL):
                # trim the HOME_URL since it won't be part of the local path to the file
                src = src[len(settings.HOME_URL):]
            elif src.startswith('/'):
                # trim the leading '/' from the src so we can combine it with the OUTPUT_CACHE_DIR to get a path
                src = src[1:]

            file = path(settings.OUTPUT_CACHE_DIR / src).abspath()

            if file.ext[1:] in settings.COMPRESSOR_FILE_EXTENSIONS:
                settings.COMPRESS_FILE_LIST.add((file, compression_type))

                # TODO: Inline script minification.
                #    if has_inline: # Handle inline script
                #        # Since we have inline script, we need to serialize the minified content into a string and return it
                #        walker = treewalkers.getTreeWalker('simpletree')
                #        stream = walker(doc)
                #        s = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False,
                #                                                     #strip_whitespace=True,
                #                                                     quote_attr_values=True)
                #        generator = s.serialize(stream)
                #        output = ''
                #        for tag in generator:
                #            output += tag

        return value


def typogrify_no_widont(value):
    value = Typogrify.amp(value)
    value = Typogrify.smartypants(value)
    value = Typogrify.caps(value)
    value = Typogrify.initial_quotes(value)
    return value
