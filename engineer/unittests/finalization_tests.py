# coding=utf-8

from engineer.unittests.config_tests import BaseTestCase

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

class MetadataFinalizationTestCase(BaseTestCase):
    def test_finalization_settings(self):
        from engineer.conf import settings

        self.assertTrue(hasattr(settings, 'FINALIZE_METADATA'))

    def test_finalization_draft(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('finalization.yaml')
        settings.create_required_directories()
        post = Post('posts/finalization_draft.md')
        self.assertEqual(post.title, "Finalization Draft")

        expected_output = """title: Finalization Draft
status: draft
slug: finalization-draft
tags:
- tag

---

This is a finalization test post.
""".format(year=post.timestamp_local.year, month=post.timestamp_local.month, day=post.timestamp_local.day)

        with open(post.source, mode='rb') as post_file:
            content = post_file.read()
        self.assertEqual(content, expected_output)
