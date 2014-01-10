# coding=utf-8
from engineer.unittests.post_tests import PostTestCase

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


class LoaderTest(PostTestCase):
    def subdir_loading_test(self):
        from engineer.conf import settings
        from engineer.loaders import LocalLoader
        from engineer.models import Post, PostCollection

        settings.reload(self.config_dir / 'load_from_subdir.yaml')
        post_file = self.post_dir / 'subdir/post_in_subdir.md'
        expected_post = Post(post_file)
        new_posts, cached_posts = LocalLoader.load_all(settings.POST_DIR)
        all_posts = PostCollection(new_posts + cached_posts)

        self.assertIn(expected_post, all_posts)

    def regular_loading_test(self):
        from engineer.conf import settings
        from engineer.loaders import LocalLoader
        from engineer.models import Post, PostCollection

        post_file = self.post_dir / 'subdir/post_in_subdir.md'
        expected_post = Post(post_file)
        new_posts, cached_posts = LocalLoader.load_all(settings.POST_DIR)
        all_posts = PostCollection(new_posts + cached_posts)

        self.assertNotIn(expected_post, all_posts)
