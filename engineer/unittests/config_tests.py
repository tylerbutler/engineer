# coding=utf-8
import os
from path import path
from engineer.log import bootstrap
from engineer.unittests import CopyDataTestCase, SettingsTestCase

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

test_data_root = path(__file__).dirname() / 'test_data'
simple_site = test_data_root / 'simple_site'

class BaseTestCase(CopyDataTestCase):
    def setUp(self):
        bootstrap() #bootstrap logging infrastructure
        self.source_path = simple_site
        os.chdir(self.copied_data_path)


class TestConfig(BaseTestCase):
    def test_config_yaml(self):
        from engineer.conf import settings

        settings.reload('config.yaml')
        self.assertEqual(settings.SITE_TITLE, 'Test Config')
        self.assertEqual(settings.HOME_URL, '/')

    def test_global_settings(self):
        """All EngineerConfiguration instances share state"""
        from engineer.conf import settings as s1
        from engineer.conf import EngineerConfiguration

        s2 = EngineerConfiguration()
        self.assertEqual(s1.SITE_TITLE, s2.SITE_TITLE)

    def test_manual_config_yaml(self):
        """Creating an EngineerConfiguration manually also shares state with configs created other ways"""
        from engineer.conf import settings as s1
        from engineer.conf import EngineerConfiguration

        os.chdir(test_data_root)
        s2 = EngineerConfiguration('configs/config2.yaml')
        self.assertEqual(s1.SITE_TITLE, s2.SITE_TITLE)

