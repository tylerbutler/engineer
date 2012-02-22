# coding=utf-8
from unittest import TestCase
import os
from path import path
from engineer.loaders import LocalLoader

__author__ = 'tyler@tylerbutler.com'

class TestConfig(TestCase):
    def setUp(self):
        pass
        #configure_settings('settings')

    def test_config_yaml(self):
        os.chdir(path(__file__).dirname())
        from engineer.conf import settings
        self.assertEqual(settings.SITE_TITLE, 'Test Config')
        self.assertEqual(settings.HOME_URL, '/test')

    def test_global_settings(self):
        from engineer.conf import settings as s1
        from engineer.conf._settings import EngineerConfiguration
        s2 = EngineerConfiguration(None)
        self.assertEqual(s1.SITE_TITLE, s2.SITE_TITLE)

    def test_manual_config_yaml(self):
        from engineer.conf import settings as s1
        from engineer.conf._settings import EngineerConfiguration
        s2 = EngineerConfiguration('test_data/configs/config2.yaml')
        self.assertEqual(s1.SITE_TITLE, s2.SITE_TITLE)

    def test_load(self):
        posts = LocalLoader.load_all(path(__file__).dirname() / 'test_site/drafts')
        self.assertEqual(len(posts), 20)
