# coding=utf-8
import logging
from uuid import uuid4

import bottle
from path import path

from engineer.conf import settings


try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

logger = logging.getLogger(__name__)


class NoSecretException(Exception):
    pass


#def url(path_to_append, absolute=False):
#    if path_to_append is None or path_to_append == '':
#        return [get_secret_path(absolute), get_secret_path(absolute) + '/']
#    else:
#        path = '%s/%s' % (get_secret_path(absolute), path_to_append)
#        return [path, path + '/']


# noinspection PyUnresolvedReferences
class EmmaStandalone(object):
    app = bottle.Bottle()

    def __init__(self):
        self.emma_instance = Emma()

    @staticmethod
    @app.route('/static/<filepath:path>')
    def _serve_static(filepath):
        response = bottle.static_file(filepath,
                                      root=settings.ENGINEER.STATIC_DIR)
        if type(response) is bottle.HTTPError:
            return bottle.static_file(path(filepath) / 'index.html',
                                      root=settings.OUTPUT_DIR)
        else:
            return response

    def run(self, port=8080, **kwargs):
        self.app.mount(self.emma_instance.get_secret_path(),
                       self.emma_instance.app)

        use_cherrypy = False
        if 'server' not in kwargs:
            try:
                import cherrypy

                use_cherrypy = True
            except ImportError:
                pass
        if use_cherrypy:
            bottle.run(app=self.app, port=port, server='cherrypy')
        else:
            bottle.run(app=self.app, port=port, **kwargs)


class Emma(object):
    app = bottle.Bottle()

    def __init__(self, prefix=None):
        self.prefix = prefix

        if self.prefix is None and hasattr(settings, 'EMMA_PREFIX'):
            self.prefix = settings.EMMA_PREFIX

        self.stats = None
        self.messages = []

        self.app.route('/', callback=self._home, name='home')
        self.app.route('/', method='POST', callback=self._home, name='home')
        self.app.route('/build', callback=self._build, name='build')
        self.app.route('/clean', callback=self._clean, name='clean')
        self.app.route('/reload_settings', callback=self._reload_settings,
                       name='reload_settings')
        self.app.route('/disable', callback=self._disable, name='disable')
        self.app.route('/disable/confirm', callback=self._confirm_disable,
                       name='confirm_disable')

        self.app.route('/static/<filepath:path>', callback=self._serve_static,
                       name='static')

    #        try:
    #            logger.debug("Absolute URL prefix: %s" % url(None, True))
    #            logger.debug("Relative URL prefix: %s" % url(None))
    #        except NoSecretException:
    #            pass

    def _home(self):
        template = settings.JINJA_ENV.get_template('emma/home.html')
        if settings.BUILD_STATS_FILE.exists():
            with open(settings.BUILD_STATS_FILE, mode='rb') as the_file:
                stats = pickle.load(the_file)
        else:
            stats = None
        current_messages = self.messages
        self.messages = []
        return template.render(get_url=self.get_url, len=len, stats=stats,
                               messages=current_messages)

    def _build(self):
        from engineer.engine import build

        self.stats = build()
        self.messages.append("Build successful.")
        return bottle.redirect(self.get_url('home'))

    def _clean(self):
        from engineer.engine import build, get_argparser

        self.stats = build(get_argparser().parse_args(['build', '-c']))
        self.messages.append("Clean build successful.")
        return bottle.redirect(self.get_url('home'))

    def _reload_settings(self):
        settings.reload()
        self.messages.append(
            "Settings reloaded from %s." % settings.SETTINGS_FILE)
        return bottle.redirect(self.get_url('home'))

    def _disable(self):
        template = settings.JINJA_ENV.get_template('emma/disable.html')
        return template.render(get_url=self.get_url)

    def _confirm_disable(self):
        self.secret_file.remove_p()
        exit()

    def _serve_static(self, filepath):
        response = bottle.static_file(filepath,
                                      root=settings.ENGINEER.STATIC_DIR)
        if type(response) is bottle.HTTPError:
            return bottle.static_file(path(filepath) / 'index.html',
                                      root=settings.OUTPUT_DIR)
        else:
            return response

    def get_url(self, routename, **kwargs):
        # Wrapper method around bottle's get_url method to handle the case
        # where a prefix is set
        if self.prefix is not None:
            url = "%s/%s" % (
                '/'.join(self.get_secret_path(True).split('/')[:-1]),
                self.app.get_url(routename, **kwargs))
            return url
        else:
            return self.app.get_url(routename, **kwargs)

    @property
    def secret_file(self):
        return settings.SETTINGS_DIR / ('_%s_emma_secret.pvt' % settings.SETTINGS_FILE.name)

    @property
    def secret(self):
        if self.secret_file.exists():
            with open(self.secret_file, mode='rb') as the_file:
                self._secret = pickle.load(the_file)
            return self._secret
        else:
            return None

    def get_secret_path(self, absolute=False):
        if self.secret is None:
            raise NoSecretException("No secret!")
        if not absolute:
            return '/%s' % self.secret
        else:
            if self.prefix is not None:
                return '%s/%s/%s' % (
                    settings.SITE_URL, self.prefix, self.secret)
            else:
                return '%s/%s' % (settings.SITE_URL, self.secret)

    def generate_secret(self):
        new_secret = uuid4()
        if self.secret is not None:
            logger.warning("A secret already existed but was overwritten.")
        with open(self.secret_file, mode='wb') as the_file:
            pickle.dump(new_secret, the_file)
        self._secret = new_secret
        logger.console("Wrote secret file: %s" % self.secret_file)
