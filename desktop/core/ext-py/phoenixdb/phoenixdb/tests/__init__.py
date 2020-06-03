# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import unittest

import phoenixdb

TEST_DB_URL = os.environ.get('PHOENIXDB_TEST_DB_URL', "http://localhost:8765")
TEST_DB_TRUSTSTORE = os.environ.get('PHOENIXDB_TEST_DB_TRUSTSTORE')
TEST_DB_AUTHENTICATION = os.environ.get('PHOENIXDB_TEST_DB_AUTHENTICATION')
TEST_DB_AVATICA_USER = os.environ.get('PHOENIXDB_TEST_DB_AVATICA_USER')
TEST_DB_AVATICA_PASSWORD = os.environ.get('PHOENIXDB_TEST_DB_AVATICA_PASSWORD')

httpArgs = {}
if TEST_DB_TRUSTSTORE is not None:
    httpArgs.update(verify=TEST_DB_TRUSTSTORE)
if TEST_DB_AUTHENTICATION is not None:
    httpArgs.update(authentication=TEST_DB_AUTHENTICATION)
if TEST_DB_AVATICA_USER is not None:
    httpArgs.update(avatica_user=TEST_DB_AVATICA_USER)
if TEST_DB_AVATICA_PASSWORD is not None:
    httpArgs.update(avatica_password=TEST_DB_AVATICA_PASSWORD)


@unittest.skipIf(TEST_DB_URL is None, "these tests require the PHOENIXDB_TEST_DB_URL environment variable set to a clean database")
class DatabaseTestCase(unittest.TestCase):

    def setUp(self):
        self.conn = phoenixdb.connect(TEST_DB_URL, autocommit=True, **httpArgs)

        def closeDb():
            self.conn.close()
        self.addCleanup(closeDb)

    def reopen(self, **avaticaArgs):
        self.conn.close()
        kwargs = avaticaArgs.copy()
        kwargs.update(httpArgs)
        self.conn = phoenixdb.connect(TEST_DB_URL, **kwargs)

    def addTableCleanup(self, name):
        def dropTable():
            with self.conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS {table}".format(table=name))
        self.addCleanup(dropTable)

    def createTable(self, name, statement):
        with self.conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS {table}".format(table=name))
            cursor.execute(statement.format(table=name))
            self.addTableCleanup(name)
