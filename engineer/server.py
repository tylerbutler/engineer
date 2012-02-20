# coding=utf-8
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer
from os import getcwd, chdir
from engineer.conf import settings

__author__ = 'tyler@tylerbutler.com'

#class EngineerHTTPRequestHandler(SimpleHTTPRequestHandler):
#    def do_GET(self):
#        #logger.debug('got a GET request')
#        SimpleHTTPRequestHandler.do_GET(self)

def serve(path=settings.OUTPUT_DIR, port=8000):
    old_working_dir = getcwd()
    chdir(path)
    new_working_dir = getcwd()
    httpd = TCPServer(("", port), SimpleHTTPRequestHandler)
    print 'Starting development server rooted at %s' % new_working_dir
    httpd.serve_forever()
