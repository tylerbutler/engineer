# coding=utf-8
from codecs import open
import re

import yaml
from path import path

from engineer.plugins import PostProcessor
from engineer.enums import Status

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


class FinalizationPlugin(PostProcessor):
    _finalize_map_defaults = {
        'timestamp': [Status.published],
        'title': [Status.published, Status.review, Status.draft],
        'slug': [Status.published, Status.review, Status.draft]
    }

    @classmethod
    def handle_settings(cls, config_dict, settings):
        logger = cls.get_logger()

        # POST METADATA FINALIZATION SETTINGS
        settings.FINALIZE_METADATA = config_dict.pop('FINALIZE_METADATA', True)

        if 'FINALIZE_METADATA_CONFIG' in config_dict.keys():
            if not settings.FINALIZE_METADATA:
                logger.warning('FINALIZE_METADATA_CONFIG is defined but FINALIZE_METADATA is set to False.')
            else:
                for metadata_attribute, statuses in config_dict['FINALIZE_METADATA_CONFIG'].iteritems():
                    cls._finalize_map_defaults[metadata_attribute] = [Status(s) for s in statuses]
            del config_dict['FINALIZE_METADATA_CONFIG']
        settings.FINALIZE_METADATA = cls._finalize_map_defaults

        return config_dict

    @classmethod
    def preprocess(cls, post, metadata):
        from engineer.conf import settings

        if settings.FINALIZE_METADATA:
            # Get the list of metadata that's specified directly in the source file -- this metadata we *always* want
            # to ensure gets output during finalization. Store it on the post object,
            # then we'll use it later in the postprocess method.
            post.metadata_original = set(metadata.keys())
        return post, metadata

    @classmethod
    def postprocess(cls, post):
        from engineer.conf import settings

        if settings.FINALIZE_METADATA:
            output = cls.render_markdown(post)
            with open(post.source, mode='wb', encoding='UTF-8') as file:
                file.write(output)
        return post

    @staticmethod
    def render_markdown(post):
        """
        Renders the post as Markdown using the template specified in :attr:`markdown_template_path`.
        """
        from engineer.conf import settings

        # A hack to guarantee the YAML output is in a sensible order.
        d = [
            ('status', post.status.name),
            ('url', post.url),
            ('link', post.link),
            ('via', post.via),
            ('via-link', post.via_link),
            ('tags', post.tags),
        ]

        # The complete set of metadata that should be written is the union of the FINALIZE_METADATA setting and the
        # set of metadata that was in the file originally.
        metadata_to_finalize = set([m for m, s in settings.FINALIZE_METADATA.iteritems() if post.status in s])
        metadata_to_finalize.update(post.metadata_original)
        
        if 'title' in metadata_to_finalize:
            # insert at the top of the list
            d.insert(0, ('title', post.title))
        if 'slug' in metadata_to_finalize:
            # insert right before tags
            d.insert(-1, ('slug', post.slug))
        if 'timestamp' in metadata_to_finalize:
            # insert right after status
            d.insert(d.index(('status', post.status.name)), ('timestamp',
                                                             post.timestamp_local.strftime(settings.TIME_FORMAT)))

        metadata = ''
        for k, v in d:
            if v is not None and len(v) > 0:
                metadata += yaml.safe_dump(dict([(k, v)]), default_flow_style=False)

        # handle custom metadata
        if len(post.custom_properties):
            metadata += '\n'
            metadata += yaml.safe_dump(dict(post.custom_properties), default_flow_style=False)
        return settings.JINJA_ENV.get_template(post.markdown_template_path).render(metadata=metadata,
                                                                                   content=post.content_raw)
