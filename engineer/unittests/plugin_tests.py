# coding=utf-8
from engineer.log import bootstrap

bootstrap()

from path import path
from engineer.enums import Status
from engineer.models import Post
from engineer.plugins import PostRenamerPlugin

from engineer.unittests.config_tests import BaseTestCase
from engineer.unittests.post_tests import PostTestCase

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


class PostRenamerTestCase(BaseTestCase):
    def test_settings(self):
        from engineer.conf import settings

        settings.reload('config.yaml')
        self.assertTrue('config' in PostRenamerPlugin.get_settings())
        self.assertTrue(PostRenamerPlugin.is_enabled())

    def test_disabled(self):
        from engineer.conf import settings

        settings.reload('renamer_off.yaml')
        plugin_enabled = PostRenamerPlugin.is_enabled()
        self.assertFalse(plugin_enabled)

    def test_post_renamer_default_config(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('config.yaml')
        settings.create_required_directories()
        self.assertEqual(PostRenamerPlugin.get_settings()['config'][Status.draft], '({status}) {slug}.md')

        post = Post('posts/draft_post.md')
        self.assertTrue(post.source.exists())
        self.assertEqual(post.source.name, '(draft) a-draft-post.md')
        self.assertFalse(path('posts/draft_post.md').exists())

        post = Post('posts/review_post.md')
        self.assertTrue(post.source.exists())
        self.assertEqual(post.source.name, '(review) 2012-11-02 a-post-in-review.md')
        self.assertFalse(path('posts/review_post.md').exists())

        post = Post('posts/published_post_with_timestamp.md')
        self.assertEqual(post.source.name, '(p) 2012-11-02 a-published-post.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/published_post_with_timestamp.md').exists())

    def test_post_renamer_custom_config(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('custom_renames.yaml')
        settings.create_required_directories()

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
status: draft
slug: lazy-markdown-links

---

"""

    _expected_output = """This is my text and [this is my link][4]. I'll define
the url for that link under the paragraph.

[4]: http://brettterpstra.com

I can use [multiple][5] lazy links in [a paragraph][6],
and then just define them in order below it.

[5]: https://gist.github.com/ttscoff/7059952
[6]: http://blog.bignerdranch.com/4044-rock-heads/

I can also use lazy links when there are already [existing
numbered links][1] in [the text][3].

[1]: http://www.tylerbutler.com
[3]: http://www.xkcd2.com
"""

    _expected_output2 = """[Lazy links][1] can come in handy. But sometimes you have links
already defined and you also want to add [some lazy ones][3].

[1]: http://www.tylerbutler.com/
[3]: http://www.xkcd2.com/

Luckily the [Engineer][2] Lazy Markdown Link plugin [handles this
case][4] automatically.

[4]: http://www.tylerbutler.com/
[2]: https://github.com/tylerbutler/engineer/
"""

    def test_lazy_links(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('config.yaml')
        settings.create_required_directories()

        post = Post('posts/lazy_markdown_links.md')
        self.assertEqual(post.content_preprocessed.strip(), self._expected_output.strip())

        post = Post('posts/lazy_markdown_links2.md')
        self.assertEqual(post.content_preprocessed.strip(), self._expected_output2.strip())

    def test_lazy_links_persist(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('lazy_links_persist.yaml')
        settings.create_required_directories()

        post = Post('posts/lazy_markdown_links.md')
        self.assertEqual(post.content_preprocessed.strip(), self._expected_output.strip())

        with open(post.source, mode='rb') as post_file:
            content = post_file.read()
        self.assertEqual(content.strip(), self._expected_metadata + self._expected_output.strip())


class PostLinkHelperTestCase(PostTestCase):
    def post_link_settings_test(self):
        """Post link settings test."""
        from engineer.conf import settings
        from engineer.plugins.bundled import PostLinkPlugin

        settings.reload(self.config_dir / 'post_link_default.yaml')
        self.assertTrue(PostLinkPlugin.is_enabled())

        settings.reload(self.config_dir / 'post_link_disabled_settings.yaml')
        self.assertFalse(PostLinkPlugin.is_enabled())

    def post_link_test(self):
        """Post link test."""
        from engineer.conf import settings

        settings.reload(self.config_dir / 'post_link_settings.yaml')
        post = Post(self.post_dir / 'post_link_post.md')

        expected_content = """
<p>Tyler Butler has a home on the web at <a href="http://tylerbutler.com">tylerbutler.com</a>.</p>
        """.replace('\r\n', '\n')

        actual_content = unicode(post.content).replace('\r\n', '\n')
        self.assertEqual(actual_content.strip(), expected_content.strip())

    def post_link_disabled_test(self):
        """Post link disabled test."""
        from engineer.conf import settings

        settings.reload(self.config_dir / 'post_link_disabled_settings.yaml')
        post = Post(self.post_dir / 'post_link_post.md')

        expected_content = "<p>Tyler Butler has a home on the web at&nbsp;[tylerbutler.com][post-link].</p>"

        actual_content = unicode(post.content).replace('\r\n', '\n')
        self.assertEqual(actual_content.strip(), expected_content.strip())
