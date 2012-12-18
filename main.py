import os.path
import os
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
import requests
from pyquery import PyQuery as pq
import urllib
import urlparse
import json
import re

# helper functions
def url_fix(s, charset='utf-8'):
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

# import and define tornado-y things
from tornado.options import define, options
define("port", default=5000, help="run on the given port", type=int)

# application settings and handle mapping info
class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        handlers = [
            (r"/([^/]+)?", MainHandler),
            (r"/post_form/", FormHandler),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


# the main page
class MainHandler(tornado.web.RequestHandler):
    def get(self, q):
        if os.environ.has_key('GOOGLEANALYTICSID'):
            google_analytics_id = os.environ['GOOGLEANALYTICSID']
        else:
            google_analytics_id = False

        self.render(
            "main.html",
            page_title='HypeM Favorites Downloader',
            page_heading='Hi!',
            google_analytics_id=google_analytics_id,
        )

class FormHandler(tornado.web.RequestHandler):
    def get(self    ):
        username = self.get_argument('username')
        if username == '':
            form_response = {'error': True, 'msg': 'Please enter your username.'}
        else:
            msg = url_fix(username)
            form_response = {'error': True, 'msg': msg }
        self.write(form_response)


# RAMMING SPEEEEEEED!
def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(os.environ.get("PORT", 5000))

    # start it up
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()