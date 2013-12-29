# coding=utf-8

from path import path

from engineer.unittests.config_tests import BaseTestCase

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


class PostRenamerTestCase(BaseTestCase):
    def test_settings(self):
        from engineer.conf import settings

        settings.reload('config.yaml')
        self.assertTrue(hasattr(settings, 'POST_RENAME_ENABLED'))
        self.assertTrue(hasattr(settings, 'POST_RENAME_CONFIG'))
        self.assertTrue(settings.POST_RENAME_ENABLED)

    def test_disabled(self):
        from engineer.conf import settings

        settings.reload('renamer_off.yaml')
        self.assertFalse(settings.POST_RENAME_ENABLED)

    def test_post_renamer_default_config(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('config.yaml')

        post = Post('posts/draft_post.md')
        self.assertEqual(post.source.name, '(draft) a-draft-post.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/draft_post.md').exists())

        post = Post('posts/review_post.md')
        self.assertEqual(post.source.name, '(review) 2012-11-02 a-post-in-review.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/review_post.md').exists())

        post = Post('posts/published_post_with_timestamp.md')
        self.assertEqual(post.source.name, '(p) 2012-11-02 a-published-post.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/published_post_with_timestamp.md').exists())

    def test_post_renamer_custom_config(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('custom_renames.yaml')

        post = Post('posts/draft_post.md')
        self.assertEqual(post.source.name, 'draft_post.md')
        self.assertTrue(post.source.exists())

        post = Post('posts/review_post.md')
        self.assertEqual(post.source.name, '2012-11-02-a-post-in-review.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/review_post.md').exists())

        post = Post('posts/published_post_with_timestamp.md')
        self.assertEqual(post.source.name, '(p) 2012-11-02 a-published-post.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/published_post_with_timestamp.md').exists())


class LazyMarkdownLinksTestCase(BaseTestCase):
    _expected_metadata = """title: Lazy Markdown Links
status: published

---

"""

    _expected_output = """This is my text and [this is my link][1]. I'll define
the url for that link under the paragraph.

[1]: http://brettterpstra.com

I can use [multiple][2] lazy links in [a paragraph][3],
and then just define them in order below it.

[2]: https://gist.github.com/ttscoff/7059952
[3]: http://blog.bignerdranch.com/4044-rock-heads/
"""

    def test_plugin(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('config.yaml')

        post = Post('posts/lazy_markdown_links.md')
        self.assertEqual(post.content_preprocessed, self._expected_output)

        # with open(post.source, mode='rb') as post_file:
        #     content = post_file.read()
        # self.assertEqual(content, self._expected_metadata + self._expected_output)
