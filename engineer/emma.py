# coding=utf-8
import bottle
from path import path
from uuid import uuid4

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'tyler@tylerbutler.com'

secret_file = path(__file__).dirname() / '_emma_secret.pvt'
_secret = None

def get_secret():
    global _secret
    if secret_file.exists():
        with open(secret_file, mode='rb') as file:
            _secret = pickle.load(file)
    return _secret


def generate_secret():
    global _secret
    new_secret = uuid4()
    with open(secret_file, mode='wb') as file:
        pickle.dump(new_secret, file)
    _secret = new_secret


def get_secret_path():
    if get_secret() is None:
        raise Exception("No secret!")
    return '/_emma/%s' % get_secret()


def url(path_to_append):
    if path_to_append is None or path_to_append == '':
        return [get_secret_path(), get_secret_path() + '/']
    else:
        path = '%s/%s' % (get_secret_path(), path_to_append)
        return [path, path + '/']


class Emma(object):
    emma = bottle.Bottle()
    mgmt = bottle.Bottle()

    def __init__(self):
        # Not using the decorator syntax since that causes the functions to
        # get called on module import, which will throw an exception if
        # generate_secret hasn't been called yet.
        self.emma.route(url(None), callback=self._home)
        self.emma.route(url('publish'), callback=self._publish)

    def _home(self):
        return 'manage_home'

    def _publish(self):
        return 'publish'

    def run(self):
        bottle.run(app=self.emma, reloader=True)


if __name__ == "__main__":
    emma = Emma()
    emma.run()
