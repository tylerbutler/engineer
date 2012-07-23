# coding=utf-8
from tempfile import mkdtemp
from unittest.case import TestCase
from path import path
from engineer.log import bootstrap

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

class SettingsTestCase(TestCase):
    settings_file = None

    def __init__(self, *args, **kwargs):
        from engineer.conf import EngineerConfiguration

        super(SettingsTestCase, self).__init__(*args, **kwargs)
        self._source_settings_file = self.settings_file
        EngineerConfiguration(self._source_settings_file)

    def tearDown(self):
        from engineer.conf import EngineerConfiguration

        EngineerConfiguration(self._source_settings_file)


class CopyDataTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp_dirs = []

    def __init__(self, *args, **kwargs):
        bootstrap()
        super(CopyDataTestCase, self).__init__(*args, **kwargs)
        self.copied_data_path = None

    @property
    def source_path(self):
        return self._source_path

    @source_path.setter
    def source_path(self, value):
        if self.copied_data_path is not None:
            self.copied_data_path.rmtree()
        temp = mkdtemp()
        self.copied_data_path = (path(temp) / '__in_progress_test_data').abspath()
        self._source_path = value
        self.source_path.copytree(self.copied_data_path)
        print "Copied temp test data to: %s" % self.copied_data_path

    def tearDown(self):
        print "Marking temp folder for deletion: %s" % self.copied_data_path.dirname()
        self.tmp_dirs.append(self.copied_data_path.dirname())

    @classmethod
    def tearDownClass(cls):
        print "Teardownclass running... %s" % cls.tmp_dirs
        for dir in cls.tmp_dirs:
            print "Deleting temp folder: %s" % dir
            dir.rmtree(ignore_errors=True)
        del cls.tmp_dirs

    @staticmethod
    def removal_error(func, path, exc_info):
        pass
