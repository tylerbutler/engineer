# coding=utf-8
from unittest import TestCase
from path import path
from engineer.conf import configure_settings
from engineer.loaders import LocalLoader

__author__ = 'tyler@tylerbutler.com'

class TestConfig(TestCase):
    def setUp(self):
        configure_settings('settings')

    def test_init(self):
        from engineer.conf import settings

    def test_load(self):
        posts = LocalLoader.load_all(path(__file__).dirname() / 'test_site/drafts')
        self.assertEqual(len(posts), 20)
