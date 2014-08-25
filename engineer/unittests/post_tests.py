# coding=utf-8
import os
from datetime import timedelta

import arrow
from path import path

from engineer.exceptions import PostMetadataError
from engineer.log import bootstrap
bootstrap()
from engineer.models import Post
from engineer.plugins import load_plugins
from engineer.unittests import CopyDataTestCase

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

test_data_root = path(__file__).dirname() / 'test_data'


class PostTestCase(CopyDataTestCase):
    def setUp(self):
        from engineer.conf import settings

        bootstrap()  # bootstrap logging infrastructure
        load_plugins()  # load plugins
        self.source_path = test_data_root
        os.chdir(self.copied_data_path)
        post_tests_dir = self.copied_data_path / 'post_tests'
        self.config_dir = post_tests_dir / 'configs'
        self.post_dir = post_tests_dir / 'posts'

        settings.reload(self.config_dir / 'settings.yaml')
        settings.create_required_directories()


#noinspection PyShadowingBuiltins
class MetadataTests(PostTestCase):
    def default_metadata_test(self):
        """Metadata defaults"""
        file = self.post_dir / 'fenced_metadata.md'
        post = Post(file)

        self.assertNotEqual(post.slug, None)
        self.assertNotEqual(post.timestamp, None)
        self.assertNotEqual(post.status, None)

    def missing_metadata_test(self):
        """Missing metadata"""
        file = self.post_dir / 'missing_metadata.md'
        with self.assertRaises(PostMetadataError):
            Post(file)

    #noinspection PyProtectedMember
    def fenced_metadata_test(self):
        """Fenced metadata"""
        file = self.post_dir / 'fenced_metadata.md'
        post = Post(file)

        self.assertEqual(post._fence, True)

    def single_tag_test(self):
        """Single tag"""
        file = self.post_dir / 'tag_single.md'
        post = Post(file)

        self.assertEqual(post.tags, ['single'])
        self.assertEqual(len(post.tags), 1)

    def multiple_tag_test(self):
        """Multiple tags"""
        file = self.post_dir / 'tag_multiple.md'
        post = Post(file)

        self.assertEqual(len(post.tags), 3)
        self.assertIsInstance(post.tags, list)

    def no_custom_properties_test(self):
        """No custom properties"""
        file = self.post_dir / 'fenced_metadata.md'
        post = Post(file)

        self.assertEqual(post.custom_properties, {})

    def custom_properties_test(self):
        """Custom properties"""
        file = self.post_dir / 'custom_properties.md'
        post = Post(file)

        self.assertEqual(len(post.custom_properties), 2)
        self.assertIsInstance(post.custom_properties['custom_list'], list)
        self.assertIsInstance(post.custom_properties['custom_dict'], dict)

    def cased_metadata_test(self):
        """Cased metadata"""
        file = self.post_dir / 'cased_metadata.md'
        post = Post(file)

        self.assertEqual(post.title, 'Cased Metadata')
        self.assertEqual(post.custom_properties['customproperty'], 'custom')
        self.assertEqual(len(post.tags), 2)

    def numeric_tags_test(self):
        """Numeric tags"""
        file = self.post_dir / 'numeric_tags.md'
        post = Post(file)

        self.assertSequenceEqual(post.tags, ['2013', '2014'])


#noinspection PyShadowingBuiltins
class StatusTests(PostTestCase):
    def draft_default_test(self):
        """Draft default status"""
        file = self.post_dir / 'fenced_metadata.md'
        post = Post(file)

        self.assertTrue(post.is_draft)
        self.assertFalse(post.is_published)

    def published_test(self):
        """Published status"""
        file = self.post_dir / 'published.md'
        post = Post(file)

        self.assertTrue(post.is_published)
        self.assertFalse(post.is_draft)

    def pending_test(self):
        """Pending status"""
        file = self.post_dir / 'published.md'
        post = Post(file)
        post.timestamp = arrow.now().replace(days=+1)

        self.assertTrue(post.is_pending)
        self.assertFalse(post.is_published)
        self.assertFalse(post.is_draft)


#noinspection PyShadowingBuiltins
class ContentTests(PostTestCase):
    def post_breaks_simple_test(self):
        """Post breaks of the form: -- more --"""
        file = self.post_dir / 'post_breaks_simple.md'
        post = Post(file)

        self.assertNotEqual(getattr(post, 'content_teaser', None), None)

    def post_breaks_octopress_test(self):
        """Post breaks of the form: <!-- more -->"""
        file = self.post_dir / 'post_breaks_octopress.md'
        post = Post(file)

        self.assertNotEqual(getattr(post, 'content_teaser', None), None)

    def unicode_content_test(self):
        """Unicode post content."""
        file = self.post_dir / 'unicode_content.md'

        # Just loading the post will throw an exception if the unicode handling is broken - no need to specifically
        # assert anything for that case.
        post = Post(file)

        self.assertIn(u"also a “unicode character” in the metadata!", post.tags)


#noinspection PyShadowingBuiltins
class PermalinkTests(PostTestCase):
    def test_fulldate(self):
        from engineer.conf import settings

        settings.reload(self.config_dir / 'permalinks_fulldate.yaml')
        file = self.post_dir / 'tag_multiple.md'
        post = Post(file)

        self.assertEqual(post.url, '/test/2012/09/04/tag-multiple/')
        self.assertEqual(post.output_file_name, 'index.html')

    def test_slug(self):
        from engineer.conf import settings

        settings.reload(self.config_dir / 'permalinks_slug.yaml')
        file = self.post_dir / 'tag_multiple.md'
        post = Post(file)

        self.assertEqual(post.url, '/test/2012/09/04/tag-multiple.html')
        self.assertEqual(post.output_file_name, 'tag-multiple.html')

    def test_pretty(self):
        from engineer.conf import settings

        settings.reload(self.config_dir / 'permalinks_pretty.yaml')
        file = self.post_dir / 'tag_multiple.md'
        post = Post(file)

        self.assertEqual(post.url, '/test/2012/09/tag-multiple/')
        self.assertEqual(post.output_file_name, 'index.html')

    def test_timestamp_custom(self):
        from engineer.conf import settings

        settings.reload(self.config_dir / 'permalinks_timestamp_custom.yaml')
        file = self.post_dir / 'tag_multiple.md'
        post = Post(file)

        self.assertEqual(post.url, '/test/2012-09-04/tag-multiple.html')
        self.assertEqual(post.output_file_name, 'tag-multiple.html')

    def test_leading_slash(self):
        from engineer.conf import settings

        settings.reload(self.config_dir / 'permalinks_leading_slash.yaml')
        file = self.post_dir / 'tag_multiple.md'
        post = Post(file)

        self.assertEqual(post.url, '/test/2012-09-04/tag-multiple.html')
        self.assertEqual(post.output_file_name, 'tag-multiple.html')

    def test_no_end_slash(self):
        from engineer.conf import settings

        settings.reload(self.config_dir / 'permalinks_no_end_slash.yaml')
        file = self.post_dir / 'tag_multiple.md'
        post = Post(file)

        self.assertEqual(post.url, '/test/test/tag-multiple.html')
        self.assertEqual(post.output_file_name, 'tag-multiple.html')

    def test_end_slash(self):
        from engineer.conf import settings

        settings.reload(self.config_dir / 'permalinks_end_slash.yaml')
        file = self.post_dir / 'tag_multiple.md'
        post = Post(file)

        self.assertEqual(post.url, '/test/test/tag-multiple/')
        self.assertEqual(post.output_file_name, 'index.html')

    def test_no_leading_zeroes(self):
        from engineer.conf import settings

        settings.reload(self.config_dir / 'permalinks_no_leading_zeroes.yaml')
        file = self.post_dir / 'tag_multiple.md'
        post = Post(file)

        self.assertEqual(post.url, '/test/2012/9/4/tag-multiple.html')
        self.assertEqual(post.output_file_name, 'tag-multiple.html')


class GlobalLinksTests(PostTestCase):
    def global_links_test(self):
        """Global links test."""
        from engineer.conf import settings

        settings.reload(self.config_dir / 'global_links_settings.yaml')
        post = Post(self.post_dir / 'global_links_post.md')

        expected_content = """
<p><a href="http://tylerbutler.com">Tyler Butler</a> is the author of&nbsp;Engineer.</p>
<p>He does not like to be called <a href="http://tylerbutler.com">Ty</a>.</p>
        """

        actual_content = unicode(post.convert_to_html(post.content_preprocessed))
        self.assertEqual(actual_content.strip(), expected_content.strip())
