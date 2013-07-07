# coding=utf-8

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


class ThemeNotFoundException(Exception):
    pass


class ThemeManifestError(Exception):
    pass


class ThemeDirectoryNotFoundException(Exception):
    def __init__(self, directory, *args, **kwargs):
        super(ThemeDirectoryNotFoundException, self).__init__(*args, **kwargs)
        self.message = "Theme directory cannot be found: %s." % directory


class PostMetadataError(Exception):
    pass
