'''
Created on Dec 27, 2010

@author: mark
'''
import datetime
import json

import kyotocabinet

from paws import PAWSError

class Alias(object):
    '''
    classdocs
    '''

    def __init__(self, url=None, creator=None, created_date=datetime.datetime.utcnow()):
        '''
        Constructor
        '''
        self.__url = url
        self.__creator = creator
        self.__created_date = created_date

    @staticmethod
    def from_json(str):
        obj = json.loads(str)
        return Alias(obj['url'], obj['creator'], datetime.datetime.strptime(obj['created_date'], '%Y-%m-%dT%H:%M:%S'))

    @staticmethod
    def to_json(alias):
        return json.dumps(dict(url=alias.get_url(), creator=alias.get_creator(), created_date=alias.get_created_date().strftime('%Y-%m-%dT%H:%M:%S')))

    def set_creator(self, creator):
        self.__creator = creator

    def set_created_date(self, created_date):
        self.__created_date = created_date

    def set_url(self, url):
        self.__url = url

    def get_creator(self):
        return self.__creator

    def get_created_date(self):
        return self.__created_date

    def get_url(self):
        return self.__url

class DB(object):
    '''
    A DB wrapper object based on the kyotocabinet
    library.
    '''
    class Visitor(kyotocabinet.Visitor):
        def __init__(self):
            self.__records = {}

        def visit_full(self, key, value):
            self.__records[key] = value

        def get_records(self):
            return self.__records

    def __init__(self, db):
        '''
        Constructor
        '''
        self.__db= db

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def store(self, alias, desc):
        if not self.__db.set(alias, desc):
            raise PAWSError('store error: ' + str(self.__db.error()))

    def load(self, alias):
        return self.__db.get(alias)

    def delete(self, alias):
        return self.__db.remove(alias)

    def count(self):
        return self.__db.count()

    def records(self):
        visitor = DB.Visitor()
        if not self.__db.iterate(visitor, False):
            raise PAWSError('iterate error: ' + str(self.__db.error()))
        return visitor.get_records()

    def open(self):
        # the database gets opened by the manager, so this is a no-op
        pass

    def close(self):
        if not self.__db.synchronize():
            raise PAWSError('synchronize error: ' + str(self.__db.error()))

class DBManager(object):
    def __init__(self, dbpath):
        self.__dbpath = dbpath

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def open(self):
        self.__db = kyotocabinet.DB()
        if not self.__db.open(self.__dbpath, kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE):
            raise PAWSError('open error: ' + str(self.__db.error()))

    def close(self):
        if not self.__db.close():
            raise PAWSError('close error: ' + str(self.__db.error()))

    def db(self):
        return DB(self.__db)

class Authenticator(object):
    def __init__(self):
        self.__users = {'admin': 'admin'}

    def authenticates(self, user, password):
        if self.__users[user] == password:
            return True
        return False
