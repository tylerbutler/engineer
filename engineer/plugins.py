# coding=utf-8
import re

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

# Adapted from Marty Alchin: http://martyalchin.com/2008/jan/10/simple-plugin-framework/

def find_plugins(entrypoint):
    try:
        import pkg_resources
    except ImportError:
        pkg_resources = None

    if pkg_resources is None:
        return
    for entrypoint in pkg_resources.iter_entry_points(entrypoint):
        yield entrypoint.name, entrypoint.load()


def load_plugins():
    """Load all plugins."""

    # Load registered plugin modules
    for name, module in find_plugins('engineer.plugins'):
        # No need to import the module manually because find_plugins will do that.
        pass

        # Themes

#    for theme, theme_path in find_plugins('engineer.themes'):
#        ThemeProvider.themes.append(theme_path)


class PluginMount(type):
    """A metaclass used to identify :ref:`plugins`."""

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)


class ThemeProvider(object):
    """
    Base class for Theme :ref:`plugins`.

    ThemeProvider subclasses must provide a value for :attr:`~engineer.plugins.ThemeProvider.paths`.

    .. versionchanged:: 0.3.0
    """
    __metaclass__ = PluginMount

    paths = () # empty tuple
    """An iterable of absolute paths containing one or more :ref:`theme manifests <theme manifest>`."""


class PostProcessor(object):
    """
    Base class for Post Processor :ref:`plugins`.

    PostProcessor subclasses should provide implementations for :meth:`~engineer.plugins.PostProcessor.preprocess` or
    :meth:`~engineer.plugins.PostProcessor.postprocess` (or both) as appropriate.
    """
    __metaclass__ = PluginMount

    @classmethod
    def preprocess(cls, post, metadata):
        """
        The ``preprocess`` method is called during the Post import process, before any post metadata defaults have been
        set. It is called before the content is converted to HTML, and prior to any :ref:`post normalization`.

        :param post: The post being currently processed by Engineer. The preprocess method should use the
            ``content_preprocessed`` attribute to get/modify the content of *post*. This ensures that preprocessors
            from other plugins can be chained together.

        :param metadata: A dict of the post metadata contained in the post source file. It contains no
            default values - only the values contained within the post source file itself. The preprocess method can
            add, update, or otherwise manipulate metadata prior to it being processed by Engineer manipulating this
            parameter.

        In addition, the preprocess method can add/remove/update properties on the *post* object itself as needed.

        :return: The *post* and *metadata* values should be returned (as a 2-tuple) by the method.
        """
        return post, metadata

    @classmethod
    def postprocess(cls, post):
        """
        The ``postprocess`` method is called after the post has been imported and processed as well as converted to
        HTML and output, but prior to any :ref:`post normalization`.

        :param post: The post being currently processed by Engineer.
        :return: The *post* parameter should be returned.
        """
        return post


class PostBreaksProcessor(PostProcessor):
    _regex = re.compile(r'^(?P<teaser_content>.*?)(?P<break>\s*<?!?-{2,}\s*more\s*-{2,}>?)(?P<rest_of_content>.*)',
                        re.DOTALL)

    @classmethod
    def preprocess(cls, post, metadata):
        from engineer.models import Post

        # First check if either form of the break marker is present using the regex
        parsed_content = re.match(cls._regex, post.content_preprocessed)
        if parsed_content is None or parsed_content.group('teaser_content') is None:
            post.content_teaser = None
            return post

        # Post is meant to be broken apart, so normalize the break marker to the HTML comment form.
        post.content_preprocessed = str(parsed_content.group('teaser_content') +
                                        '<!-- more -->' +
                                        parsed_content.group('rest_of_content'))

        # Convert the full post to HTML, then use the regex again to split the resulting HTML post. This is needed
        # since Markdown might have links in the first half of the post that are listed at the bottom. By converting
        # the whole post to HTML first then splitting we get a correctly processed HTML teaser.
        parsed_content = re.match(cls._regex, Post.convert_to_html(post.content_preprocessed))
        post.content_teaser = parsed_content.group('teaser_content')
        return post
