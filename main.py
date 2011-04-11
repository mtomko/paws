#!/usr/bin/env python
'''
Created on Dec 27, 2010

@author: Mark Tomko
'''
import os
import sys

import tornado.httpserver
import tornado.ioloop
import tornado.web

from model import Authenticator, DBManager
from handler import AliasHandler
from handler import AddAliasHandler, AdminHandler, DeleteAliasHandler
from handler import RedirectToConsoleHandler, LoginHandler, LogoutHandler

settings = {
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'cookie_secret': 'SVZoZVFzU05QTGh1dFZMYzBMRExUNmRDWDY0emhKTzdaWQ0K',
    'login_url': '/login',
    'xsrf_cookies': True,
}

with DBManager('alias.kch') as dbm:
    application = tornado.web.Application([
        (r"/", RedirectToConsoleHandler),
        (r"/a/([a-zA-Z0-9_]+)", AliasHandler, dict(dbm=dbm)),
        (r"/login", LoginHandler, dict(auth=Authenticator())),
        (r"/logout", LogoutHandler),
        (r"/admin[/]?", AdminHandler, dict(dbm=dbm)),
        (r"/admin/add", AddAliasHandler, dict(dbm=dbm)),
        (r"/admin/delete/([a-zA-Z0-9_]+)", DeleteAliasHandler, dict(dbm=dbm)),
   ], **settings)

    if __name__ == "__main__":
        port = int(sys.argv[1])
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()

