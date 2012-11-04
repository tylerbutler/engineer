# coding=utf-8
import re
from codecs import open

import yaml
from path import path

from engineer.enums import Status
from engineer.plugins.core import PostProcessor

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
        'slug': [Status.published, Status.review, Status.draft],
        'url': [Status.review, Status.published]
    }
    _fenced_metadata_formats = ('fenced', 'jekyll', 'octopress')
    _unfenced_metadata_formats = ('unfenced', 'engineer',)
    _default_metadata_format = 'input'

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

        settings.METADATA_FORMAT = config_dict.pop('METADATA_FORMAT', 'input')
        if settings.METADATA_FORMAT not in\
           {cls._default_metadata_format}.union(cls._fenced_metadata_formats).union(cls._unfenced_metadata_formats):
            logger.warning("'%s' is not a valid METADATA_FORMAT setting. Defaulting to '%s'.",
                           settings.METADATA_FORMAT, cls._default_metadata_format)
            settings.METADATA_FORMAT = cls._default_metadata_format
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

        logger = cls.get_logger()
        if settings.FINALIZE_METADATA:
            if settings.METADATA_FORMAT in cls._fenced_metadata_formats:
                logger.debug("METADATA_FORMAT is '%s', metadata will always be fenced during normalization.",
                             settings.METADATA_FORMAT)
                post._fence = True
            elif settings.METADATA_FORMAT in cls._unfenced_metadata_formats:
                logger.debug("METADATA_FORMAT is '%s', metadata will always be unfenced during normalization.",
                             settings.METADATA_FORMAT)
                post._fence = False
            output = cls.render_markdown(post)
            if cls.need_update(post, output):
                logger.debug("Finalizing metadata for post '%s'" % post)
                with open(post.source, mode='wb', encoding='UTF-8') as the_file:
                    the_file.write(output)
            else:
                logger.debug("No metadata finalization needed for post '%s'" % post)
        return post

    @classmethod
    def need_update(cls, post, new_post_content):
        from engineer.models import Post

        old = Post._regex.match(post._file_contents_raw)
        new = Post._regex.match(new_post_content)

        old_fenced = (old.group('fence') is not None)
        if old_fenced != post._fence:
            return True

        old_content = old.group('metadata').strip()
        new_content = new.group('metadata').strip()

        if new_content == old_content:
            return False
        else:
            return True

    @staticmethod
    def render_markdown(post):
        """
        Renders the post as Markdown using the template specified in :attr:`markdown_template_path`.
        """
        from engineer.conf import settings

        # A hack to guarantee the YAML output is in a sensible order.
        # The order, assuming all metadata should be writter, should be:
        #        title
        #        status
        #        timestamp
        #        link
        #        via
        #        via-link
        #        slug
        #        tags
        #        url
        d = [
            ('status', post.status.name),
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
        if 'url' in metadata_to_finalize:
            # insert at end of list
            d.append(('url', post.url))

        metadata = ''
        for k, v in d:
            if v is not None and len(v) > 0:
                metadata += yaml.safe_dump(dict([(k, v)]), default_flow_style=False)

        # handle custom metadata
        if len(post.custom_properties):
            metadata += '\n'
            metadata += yaml.safe_dump(dict(post.custom_properties), default_flow_style=False)
        return settings.JINJA_ENV.get_template(post.markdown_template_path).render(metadata=metadata,
                                                                                   content=post.content_raw,
                                                                                   post=post)


class PostRenamerPlugin(PostProcessor):
    enabled_setting_name = 'POST_RENAME_ENABLED'
    config_setting_name = 'POST_RENAME_CONFIG'
    default_config = {
        Status.published: u'({status_short}) {year}-{month}-{day} {slug}.md',
        Status.draft: u'({status}) {slug}.md',
        Status.review: u'({status}) {year}-{month}-{day} {slug}.md'
    }

    @classmethod
    def handle_settings(cls, config_dict, settings):
        logger = cls.get_logger()
        if not config_dict.pop(cls.enabled_setting_name, False):
            setattr(settings, cls.enabled_setting_name, False)
            return config_dict
        else:
            setattr(settings, cls.enabled_setting_name, True)

        plugin_config = config_dict.pop(cls.config_setting_name, None)
        if plugin_config is None:
            plugin_config = cls.default_config
        else:
            custom_config = dict([(Status(k), v) for k, v in plugin_config.iteritems()])
            plugin_config = cls.default_config.copy()
            plugin_config.update(custom_config)

        logger.debug("Setting the %s setting to %s." % (cls.config_setting_name, plugin_config))
        setattr(settings, cls.config_setting_name, plugin_config)
        return config_dict

    @classmethod
    def postprocess(cls, post):
        from engineer.conf import settings

        logger = cls.get_logger()

        if not getattr(settings, cls.enabled_setting_name, False) or not hasattr(settings, cls.config_setting_name):
            logger.debug("Post Renamer plugin disabled.")
            return post  # early return - plugin is disabled

        config = getattr(settings, cls.config_setting_name)
        mask = config[post.status]
        if mask is None:
            logger.debug("Not renaming post '%s' since its status is configured to be ignored." % post)
            return post

        new_file_name = mask.format(year=unicode(post.timestamp_local.year),
                                    month=u'{0:02d}'.format(post.timestamp_local.month),
                                    day=u'{0:02d}'.format(post.timestamp_local.day),
                                    i_month=post.timestamp_local.month,
                                    i_day=post.timestamp_local.day,
                                    timestamp=post.timestamp_local,
                                    status=post.status.name,
                                    status_short=post.status.name[:1],
                                    slug=post.slug,
                                    post=post)
        new_file = post.source.parent / new_file_name

        if new_file == post.source:
            logger.debug("No need to rename post '%s'; it already has the correct name." % post)
            return post

        if new_file.exists():
            logger.warning("Couldn't rename post '%s' to %s. A file with that name already exists. Skipping it." %
                           (post.title, new_file.abspath()))
            return post

        post.source.rename(new_file)
        post.source = new_file
        logger.info("Renamed post '%s' to %s." % (post.title, new_file.abspath()))
        return post


class GlobalLinksPlugin(PostProcessor):
    setting_name = 'GLOBAL_LINKS_FILE'
    not_enabled_log_message = "Settings don't include a %s setting, " \
                              "so Global Links plugin will not run." % setting_name
    file_not_found_message = "%s %s not found. Global Links plugin will not run."
    error_displayed = False  # flag so 'file not found' error is only displayed once per build

    @classmethod
    def preprocess(cls, post, metadata):
        from engineer.conf import settings

        logger = cls.get_logger()
        if not hasattr(settings, cls.setting_name):
            logger.info(cls.not_enabled_log_message)
            return post, metadata  # early return

        file_path = path(getattr(settings, cls.setting_name)).expand()
        if not file_path.isabs():
            file_path = (settings.SETTINGS_DIR / file_path).abspath()
        try:
            with open(file_path, 'rb') as f:
                abbreviations = f.read()
        except IOError:
            if not cls.error_displayed:
                logger.error(cls.file_not_found_message % (cls.setting_name, file_path))
                cls.error_displayed = True
            return

        post.content_preprocessed += abbreviations
        return post, metadata
