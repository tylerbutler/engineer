# coding=utf-8
import bottle
from path import path
from uuid import uuid4
from engineer.conf import settings
from engineer.log import logger

try:
    import cPickle as pickle
except ImportError:
    import pickle

__author__ = 'tyler@tylerbutler.com'

secret_file = settings.CONTENT_ROOT_DIR / '_emma_secret.pvt'
_secret = None
_prefix = None

def get_secret():
    global _secret
    if secret_file.exists():
        with open(secret_file, mode='rb') as file:
            _secret = pickle.load(file)
    return _secret


def generate_secret():
    global _secret
    new_secret = uuid4()
    if get_secret() is not None:
        logger.warning("A secret already existed but was overwritten.")
    with open(secret_file, mode='wb') as file:
        pickle.dump(new_secret, file)
    _secret = new_secret


def get_secret_path(absolute=False):
    global _prefix
    if get_secret() is None:
        raise NoSecretException("No secret!")
    if not absolute:
        return '/%s' % get_secret()
    else:
        if _prefix is not None:
            return '%s/%s/%s' % (settings.SITE_URL, _prefix, get_secret())
        else:
            return '%s/%s' % (settings.SITE_URL, get_secret())


class NoSecretException(Exception):
    pass


def url(path_to_append, absolute=False):
    if path_to_append is None or path_to_append == '':
        return [get_secret_path(absolute), get_secret_path(absolute) + '/']
    else:
        path = '%s/%s' % (get_secret_path(absolute), path_to_append)
        return [path, path + '/']


class EmmaStandalone(object):
    app = bottle.Bottle()

    def __init__(self):
        em = Emma()
        self.app.mount(get_secret_path(), em.app)

    @staticmethod
    @app.route('/static/<filepath:path>')
    def _serve_static(filepath):
        response = bottle.static_file(filepath, root=settings.ENGINEER_STATIC_DIR)
        if type(response) is bottle.HTTPError:
            return bottle.static_file(path(filepath) / 'index.html',
                                      root=settings.OUTPUT_DIR)
        else:
            return response

    def run(self, port=8080, **kwargs):
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

    def __init__(self):
        self.stats = None
        self.messages = []

        self.app.route('/', callback=self._home, name='home')
        self.app.route('/', method='POST', callback=self._home, name='home')
        self.app.route('/build', callback=self._build, name='build')
        self.app.route('/clean', callback=self._clean, name='clean')
        self.app.route('/disable', callback=self._disable, name='disable')
        self.app.route('/disable/confirm', callback=self._confirm_disable, name='confirm_disable')

        self.app.route('/static/<filepath:path>', callback=self._serve_static, name='static')

        try:
            logger.debug("Absolute URL prefix: %s" % url(None, True))
            logger.debug("Relative URL prefix: %s" % url(None))
        except NoSecretException:
            pass

    def _home(self):
        template = settings.JINJA_ENV.get_template('emma/home.html')
        if settings.BUILD_STATS_FILE.exists():
            with open(settings.BUILD_STATS_FILE, mode='rb') as file:
                stats = pickle.load(file)
        else:
            stats = None
        current_messages = self.messages
        self.messages = []
        return template.render(get_url=self.get_url, len=len, stats=stats, messages=current_messages)

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

    def _disable(self):
        template = settings.JINJA_ENV.get_template('emma/disable.html')
        return template.render(get_url=self.get_url)

    def _confirm_disable(self):
        global _secret
        _secret = None
        global secret_file
        secret_file.remove()
        exit()

    def _serve_static(self, filepath):
        response = bottle.static_file(filepath, root=settings.ENGINEER_STATIC_DIR)
        if type(response) is bottle.HTTPError:
            return bottle.static_file(path(filepath) / 'index.html',
                                      root=settings.OUTPUT_DIR)
        else:
            return response

    def get_url(self, routename, **kwargs):
        # Wrapper method around bottle's get_url method to handle the case
        # where a prefix is set
        global _prefix
        if _prefix is not None:
            url = "%s/%s" % ('/'.join(get_secret_path(True).split('/')[:-1]),
                             self.app.get_url(routename, **kwargs))
            return url
        else:
            return self.app.get_url(routename, **kwargs)
