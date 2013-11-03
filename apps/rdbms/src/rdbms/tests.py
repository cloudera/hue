#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import re

from nose.tools import assert_true

from desktop.lib.django_test_util import make_logged_in_client
from beeswax.server import dbms


class MockRdbms:
  def get_databases(self):
    return ['db1', 'db2']

  def get_tables(self, database):
    return ['table1', 'table2']


class TestMockedRdbms:
  def setUp(self):
    self.client = make_logged_in_client()

    # Mock DB calls as we don't need the real ones
    self.prev_dbms = dbms.get
    dbms.get = lambda a, b: MockRdbms()

  def tearDown(self):
    # Remove monkey patching
    dbms.get = self.prev_dbms

  def test_basic_flow(self):
    response = self.client.get("/rdbms/")
    assert_true('DB Query' in response.content, response.content)
