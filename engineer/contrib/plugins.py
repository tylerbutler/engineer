# coding=utf-8
import re
from path import path
from engineer.plugins import CommandPlugin, PostProcessor

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

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
        post.content_preprocessed = unicode(parsed_content.group('teaser_content') +
                                            '\n\n<!-- more -->\n\n' +
                                            parsed_content.group('rest_of_content'))

        # Convert the full post to HTML, then use the regex again to split the resulting HTML post. This is needed
        # since Markdown might have links in the first half of the post that are listed at the bottom. By converting
        # the whole post to HTML first then splitting we get a correctly processed HTML teaser.
        parsed_content = re.match(cls._regex, Post.convert_to_html(post.content_preprocessed))
        post.content_teaser = parsed_content.group('teaser_content')
        return post

