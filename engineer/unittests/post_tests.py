# coding=utf-8
import times
from datetime import timedelta
from unittest.case import TestCase
from path import path
from engineer.exceptions import PostMetadataError
from engineer.log import bootstrap
from engineer.models import Post
from engineer.plugins import load_plugins

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

test_data_root = path(__file__).dirname() / 'test_data'
post_tests_dir = test_data_root / 'post_tests'
simple_site = test_data_root / 'simple_site'

class PostTestCase(TestCase):
    def setUp(self):
        bootstrap() #bootstrap logging infrastructure
        load_plugins() #load plugins
        from engineer.conf import settings

        settings.reload(settings_file=post_tests_dir / 'settings.yaml')
        settings.create_required_directories()


class MetadataTests(PostTestCase):
    def default_metadata_test(self):
        """Metadata defaults"""
        file = post_tests_dir / 'fenced_metadata.md'
        post = Post(file)

        self.assertNotEqual(post.slug, None)
        self.assertNotEqual(post.timestamp, None)
        self.assertNotEqual(post.status, None)

    def missing_metadata_test(self):
        """Missing metadata"""
        file = post_tests_dir / 'missing_metadata.md'
        with self.assertRaises(PostMetadataError):
            Post(file)

    def fenced_metadata_test(self):
        """Fenced metadata"""
        file = post_tests_dir / 'fenced_metadata.md'
        post = Post(file)

        self.assertEqual(post._fence, True)

    def single_tag_test(self):
        """Single tag"""
        file = post_tests_dir / 'tag_single.md'
        post = Post(file)

        self.assertEqual(post.tags, ['single'])
        self.assertEqual(len(post.tags), 1)

    def multiple_tag_test(self):
        """Multiple tags"""
        file = post_tests_dir / 'tag_multiple.md'
        post = Post(file)

        self.assertEqual(len(post.tags), 3)
        self.assertIsInstance(post.tags, list)

    def no_custom_properties_test(self):
        """No custom properties"""
        file = post_tests_dir / 'fenced_metadata.md'
        post = Post(file)

        self.assertEqual(post.custom_properties, {})

    def custom_properties_test(self):
        """Custom properties"""
        file = post_tests_dir / 'custom_properties.md'
        post = Post(file)

        self.assertEqual(len(post.custom_properties), 2)
        self.assertIsInstance(post.custom_properties['custom_list'], list)
        self.assertIsInstance(post.custom_properties['custom_dict'], dict)

    def cased_metadata_test(self):
        """Cased metadata"""
        file = post_tests_dir / 'cased_metadata.md'
        post = Post(file)

        self.assertEqual(post.title, 'Cased Metadata')
        self.assertEqual(post.custom_properties['customproperty'], 'custom')
        self.assertEqual(len(post.tags), 2)


class StatusTests(PostTestCase):
    def draft_default_test(self):
        """Draft default status"""
        file = post_tests_dir / 'fenced_metadata.md'
        post = Post(file)

        self.assertTrue(post.is_draft)
        self.assertFalse(post.is_published)

    def published_test(self):
        """Published status"""
        file = post_tests_dir / 'published.md'
        post = Post(file)

        self.assertTrue(post.is_published)
        self.assertFalse(post.is_draft)

    def pending_test(self):
        """Pending status"""
        file = post_tests_dir / 'published.md'
        post = Post(file)
        post.timestamp = times.now() + timedelta(days=1)

        self.assertTrue(post.is_pending)
        self.assertFalse(post.is_published)
        self.assertFalse(post.is_draft)


class ContentTests(PostTestCase):
    def post_breaks_simple_test(self):
        """Post breaks of the form: -- more --"""
        file = post_tests_dir / 'post_breaks_simple.md'
        post = Post(file)

        self.assertNotEqual(getattr(post, 'content_teaser', None), None)

    def post_breaks_octopress_test(self):
        """Post breaks of the form: <!-- more -->"""
        file = post_tests_dir / 'post_breaks_octopress.md'
        post = Post(file)

        self.assertNotEqual(getattr(post, 'content_teaser', None), None)

    def unicode_content_test(self):
        """Unicode post content."""
        file = post_tests_dir / 'unicode_content.md'

        # Just loading the post will throw an exception if the unicode handling is broken - no need to specifically
        # assert anything for that case.
        post = Post(file)

        self.assertIn(u"also a “unicode character” in the metadata!", post.tags)
