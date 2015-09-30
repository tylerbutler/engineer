# coding=utf-8
import logging
import os

from path import path
from testfixtures import LogCapture

from engineer.log import bootstrap
from engineer.plugins import load_plugins
from engineer.unittests import CopyDataTestCase

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

test_data_root = path(__file__).dirname() / 'test_data'
simple_site = test_data_root / 'simple_site'


class BaseTestCase(CopyDataTestCase):
    def setUp(self):
        bootstrap()  # bootstrap logging infrastructure
        load_plugins()  # load plugins
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

    def test_config_inheritance(self):
        from engineer.conf import settings

        settings.reload('inheritance.yaml')
        self.assertEqual(settings.SITE_TITLE, 'Inheritance Test')
        self.assertEqual(settings.HOME_URL, '/')

    def test_config_inheritance_dicts(self):
        from engineer.conf import settings

        settings.reload('inheritance_dicts.yaml')

        expected = {
            'key1': 'value1new',
            'key2': 'value2',
            'key3': 'value3'
        }
        self.assertEqual(settings.test_dict, expected)

    def test_deprecated_settings(self):
        from engineer.conf import settings

        with LogCapture('engineer.conf', level=logging.WARNING) as log_output:
            settings.reload('deprecated_settings.yaml')
            log_output.check(
                ('engineer.conf',
                 'CONSOLE',
                 "Loading configuration from %s." % (self.copied_data_path / 'deprecated_settings.yaml').normpath()),
                ('engineer.conf', 'WARNING', "The 'NORMALIZE_INPUT_FILES' setting was deprecated in version 0.4: This "
                                             "setting is now ignored."),
                ('engineer.conf', 'WARNING', "The 'NORMALIZE_INPUT_FILE_MASK' setting was deprecated in version 0.4: "
                                             "This setting is now ignored.")
            )

    def test_cmdline_override(self):
        from engineer.engine import parse_override_args
        from engineer.conf import settings

        self.assertFalse(settings.PUBLISH_DRAFTS)
        override = parse_override_args("--PUBLISH_DRAFTS true --theme_dirs foo bar".split())
        settings.reload('inheritance.yaml', override)
        self.assertTrue(settings.PUBLISH_DRAFTS)
        self.assertEqual(settings.THEME_DIRS,
                         [self.copied_data_path / 'foo', self.copied_data_path / 'bar'])


class TestVariableExpansion(BaseTestCase):
    def setUp(self):
        from engineer.conf import settings

        BaseTestCase.setUp(self)
        settings.reload('path_variable_expansion.yaml')

    def test_all(self):
        dirs = [
            'CONTENT_DIR',
            'OUTPUT_DIR',
            'TEMPLATE_DIR',
            'TEMPLATE_PAGE_DIR',
            'CACHE_DIR',
            'CACHE_FILE',
            'OUTPUT_CACHE_DIR',
            'BUILD_STATS_FILE',
            'LOG_DIR',
            'LOG_FILE',
        ]

        for k in dirs:
            self._validate(k)

    def test_all_list(self):
        dirs = [
            'POST_DIR',
            'THEME_DIRS'
        ]

        for k in dirs:
            self._validate_list(k)

    def _validate(self, settings_attr):
        from engineer.conf import settings

        logger = logging.getLogger()
        if settings_attr.endswith('_FILE'):
            template_string = '~/%s.file'
        else:
            template_string = '~/%s'
        value = template_string % settings_attr.lower()

        # Skip test if user's path is not defined
        if unicode(path('~').expand()) == u'~':
            logger.warning("Skipping variable expansion since '~' does not resolve to anything.")
            return

        expected = path(value).expand()
        self.assertEqual(getattr(settings, settings_attr), expected)

    def _validate_list(self, settings_attr):
        from engineer.conf import settings

        logger = logging.getLogger()
        values = ['~/foo/', '~/bar', '~/baz/']

        # Skip test if user's path is not defined
        if unicode(path('~').expand()) == u'~':
            logger.warning("Skipping variable expansion since '~' does not resolve to anything.")
            return

        expected = [path(p).expand() for p in values]

        self.assertEqual(getattr(settings, settings_attr), expected)
