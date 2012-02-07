from unittest import TestCase
from engineer.loaders import LocalLoader

__author__ = 'tyler@tylerbutler.com'

class TestConfig(TestCase):
    def setUp(self):
        pass

    def test_init(self):
        from engineer.conf import settings


    def test_load(self):
        posts = LocalLoader.load_all()
        self.assertEqual(len(posts), 20)
