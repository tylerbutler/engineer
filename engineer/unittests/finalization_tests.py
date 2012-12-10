# coding=utf-8

from engineer.unittests.config_tests import BaseTestCase

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

finalization_draft_output = """title: Finalization Draft
status: draft
slug: finalization-draft
tags:
- tag

---

This is a finalization test post.
"""

finalization_fenced_output = """---

title: Finalization Fenced
status: draft
slug: finalization-fenced
tags:
- tag

---

This is a finalization test post.
"""

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

        expected_output = finalization_draft_output
        with open(post.source, mode='rb') as post_file:
            content = post_file.read()
        self.assertEqual(content, expected_output)

    def test_finalization_fenced_post(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('finalization.yaml')
        settings.create_required_directories()
        post = Post('posts/finalization_fenced.md')
        self.assertEqual(post.title, "Finalization Fenced")

        expected_output = finalization_fenced_output
        with open(post.source, mode='rb') as post_file:
            content = post_file.read()
        self.assertEqual(content, expected_output)

    def test_force_fenced_metadata(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('finalization_fenced.yaml')
        settings.create_required_directories()
        post = Post('posts/finalization_draft.md')
        self.assertEqual(post.title, "Finalization Draft")

        expected_output = '---\n\n' + finalization_draft_output
        with open(post.source, mode='rb') as post_file:
            content = post_file.read()
        self.assertEqual(content, expected_output)

    def test_finalization_unfenced_post(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('finalization_unfenced.yaml')
        settings.create_required_directories()
        post = Post('posts/finalization_fenced.md')
        self.assertEqual(post.title, "Finalization Fenced")

        expected_output = ''.join(finalization_fenced_output.splitlines(True)[2:])
        with open(post.source, mode='rb') as post_file:
            content = post_file.read()
        self.assertEqual(content, expected_output)

