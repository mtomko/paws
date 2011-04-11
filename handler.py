'''
File: handler.py
Author: Mark Tomko
Date: 2010-12-29

Contains the handler classes
'''
import uuid

import tornado.web

from model import Alias
from paws import PAWSError

class PAWSHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('user')

class RedirectToConsoleHandler(PAWSHandler):
    def get(self):
	self.redirect('/admin')

class LoginHandler(PAWSHandler):
    def initialize(self, auth):
        self.__auth = auth

    def get(self):
        self.render('login.html', page='login')

    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        if self.__auth.authenticates(username, password):    
            self.set_secure_cookie('user', self.get_argument('username'))
            self.set_secure_cookie('session_id', str(uuid.uuid4()))
            self.redirect('/admin')
        else:
            self.redirect(self.login_url)

class LogoutHandler(PAWSHandler):
    def get(self):
        self.clear_cookie('user')
        self.clear_cookie('sesion_id')
        self.redirect('/login')        

class AliasHandler(PAWSHandler):
    def initialize(self, dbm):
        self.__dbm = dbm

    def get(self, alias):
        with self.__dbm.db() as db:
            desc = Alias.from_json(db.load(alias))
            self.redirect(desc.get_url())

class AdminHandler(PAWSHandler):
    def initialize(self, dbm):
        self.__dbm = dbm

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()

        # get data from the database
        records = {}
        with self.__dbm.db() as db:
            record_count = db.count()
            # transform db records from string to Alias
            for k, v in db.records().items():
                records[k] = Alias.from_json(v)

        self.render('admin.html', user=user, page='admin', \
                    records=records, record_count=record_count)

class AddAliasHandler(PAWSHandler):
    def initialize(self, dbm):
        self.__dbm = dbm

    @tornado.web.authenticated
    def get(self):
        user = self.get_current_user()
        self.render('add.html', user=user, page='add')

    @tornado.web.authenticated
    def post(self):
        alias = self.get_argument('alias')
        url = self.get_argument('url')
        user = self.get_current_user()
        with self.__dbm.db() as db:
            db.store(alias, Alias.to_json(Alias(url, user)))
        self.redirect('/admin')

class DeleteAliasHandler(PAWSHandler):
    def initialize(self, dbm):
        self.__dbm = dbm

    @tornado.web.authenticated
    def post(self, alias):
        with self.__dbm.db() as db:
            db.delete(alias)
        self.redirect('/admin')

