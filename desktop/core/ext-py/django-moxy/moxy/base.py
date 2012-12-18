#!/usr/bin/env python
'''
    MySQL database backend for Django using MySQLdb and Eventlet
'''

import eventlet.db_pool

from django.db.backends import BaseDatabaseWrapper, BaseDatabaseFeatures, BaseDatabaseOperations, util
try:
    import MySQLdb
except ImportError, e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("Error loading MySQLdb module: %s" % e)

import re

from MySQLdb.converters import conversions
from MySQLdb.constants import FIELD_TYPE, FLAG, CLIENT

from django.db.backends import *
from django.db.backends.mysql import base as mysqldb_base
from django.db.backends.mysql.client import DatabaseClient
from django.db.backends.mysql.creation import DatabaseCreation
from django.db.backends.mysql.introspection import DatabaseIntrospection
from django.db.backends.mysql.validation import DatabaseValidation
from django.db.backends.signals import connection_created
from django.utils.safestring import SafeString, SafeUnicode

# Raise exceptions for database warnings if DEBUG is on
from django.conf import settings

DatabaseError = MySQLdb.DatabaseError
IntegrityError = MySQLdb.IntegrityError

# MySQLdb-1.2.1 returns TIME columns as timedelta -- they are more like
# timedelta in terms of actual behavior as they are signed and include days --
# and Django expects time, so we still need to override that. We also need to
# add special handling for SafeUnicode and SafeString as MySQLdb's type
# checking is too tight to catch those (see Django ticket #6052).
django_conversions = conversions.copy()
django_conversions.update({
    FIELD_TYPE.TIME: util.typecast_time,
    FIELD_TYPE.DECIMAL: util.typecast_decimal,
    FIELD_TYPE.NEWDECIMAL: util.typecast_decimal,
})

# This should match the numerical portion of the version numbers (we can treat
# versions like 5.0.24 and 5.0.24a as the same). Based on the list of version
# at http://dev.mysql.com/doc/refman/4.1/en/news.html and
# http://dev.mysql.com/doc/refman/5.0/en/news.html .
server_version_re = re.compile(r'(\d{1,2})\.(\d{1,2})\.(\d{1,2})')

# MySQLdb-1.2.1 and newer automatically makes use of SHOW WARNINGS on
# MySQL-4.1 and newer, so the MysqlDebugWrapper is unnecessary. Since the
# point is to raise Warnings as exceptions, this can be done with the Python
# warning module, and this is setup when the connection is created, and the
# standard util.CursorDebugWrapper can be used. Also, using sql_mode
# TRADITIONAL will automatically cause most warnings to be treated as errors.

class DatabaseFeatures(mysqldb_base.DatabaseFeatures):
    pass


class DatabaseWrapper(BaseDatabaseWrapper):

    operators = {
        'exact': '= %s',
        'iexact': 'LIKE %s',
        'contains': 'LIKE BINARY %s',
        'icontains': 'LIKE %s',
        'regex': 'REGEXP BINARY %s',
        'iregex': 'REGEXP %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE BINARY %s',
        'endswith': 'LIKE BINARY %s',
        'istartswith': 'LIKE %s',
        'iendswith': 'LIKE %s',
    }

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.server_version = None

        self.features = DatabaseFeatures()
        self.ops = mysqldb_base.DatabaseOperations()
        self.client = DatabaseClient(self)
        self.creation = DatabaseCreation(self)
        self.introspection = DatabaseIntrospection(self)
        self.validation = DatabaseValidation(self)

        self.pool = None

    def _valid_connection(self):
        if self.connection is not None:
            try:
                self.connection.ping()
                return True
            except DatabaseError:
                self.put(self.connection)
                self.connection = None
        return False

    def _cursor(self):
        if not self.pool:
            kwargs = {
                'conv': django_conversions,
                'charset': 'utf8',
                'use_unicode': True,
            }
            settings_dict = self.settings_dict
            if settings_dict['USER']:
                kwargs['user'] = settings_dict['USER']
            if settings_dict['NAME']:
                kwargs['db'] = settings_dict['NAME']
            if settings_dict['PASSWORD']:
                kwargs['passwd'] = settings_dict['PASSWORD']
            if settings_dict['HOST'].startswith('/'):
                kwargs['unix_socket'] = settings_dict['HOST']
            elif settings_dict['HOST']:
                kwargs['host'] = settings_dict['HOST']
            if settings_dict['PORT']:
                kwargs['port'] = int(settings_dict['PORT'])
            kwargs['client_flag'] = CLIENT.FOUND_ROWS
            kwargs.update(settings_dict['OPTIONS'])
            self.pool = eventlet.db_pool.TpooledConnectionPool(MySQLdb, min_size=1, max_size=16, **kwargs)

        if not self._valid_connection():
            self.connection = self.pool.get()
            connection_created.send(sender=self.__class__)
        cursor = mysqldb_base.CursorWrapper(self.connection.cursor())
        return cursor

    def _rollback(self):
        try:
            BaseDatabaseWrapper._rollback(self)
        except Database.NotSupportedError:
            pass

    def get_server_version(self):
        if not self.server_version:
            if not self._valid_connection():
                self.cursor()
            m = server_version_re.match(self.connection._base.get_server_info())
            if not m:
                raise Exception('Unable to determine MySQL version from version string %r' % self.connection.get_server_info())
            self.server_version = tuple([int(x) for x in m.groups()])
        return self.server_version
