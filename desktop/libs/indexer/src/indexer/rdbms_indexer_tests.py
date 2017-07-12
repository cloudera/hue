#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import json
import logging

from django.contrib.auth.models import User

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_false, assert_not_equal, assert_true
from desktop.lib.django_test_util import make_logged_in_client
from indexer.conf import ENABLE_SQOOP

from indexer.rdbms_indexer import RdbmsIndexer


LOG = logging.getLogger(__name__)


class TestRdbmsIndexer():
  if not ENABLE_SQOOP.get():
    raise SkipTest
  '''
  def test_get_databases(self):
    self.client = make_logged_in_client()
    self.user = User.objects.get(username='test')

    indexer = RdbmsIndexer(self.user, db_conf_name='mysql')

    data = indexer.get_databases()
    assert_equal(1, data['status'], data)

  '''
  def test_get_sample_data(self):
    self.client = make_logged_in_client()
    self.user = User.objects.get(username='test')

    indexer = RdbmsIndexer(self.user, db_conf_name='mysql')
    data = indexer.get_sample_data(database='hue', table='employee', column='empname')

    assert_equal(0, data['status'], data)
    assert_equal('',data['rows'], data)
  '''
  def test_columns(self):
    self.client = make_logged_in_client()
    self.user = User.objects.get(username='test')

    indexer = RdbmsIndexer(self.user, db_conf_name='mysql')
    data = indexer.get_columns(database='hue', table='employee')

    assert_not_equal([], data, data)
    assert_true(data, data)

  def test_get_tables(self):
    self.client = make_logged_in_client()
    self.user = User.objects.get(username='test')

    indexer = RdbmsIndexer(self.user, db_conf_name='mysql')

    data = indexer.get_tables('hue')
    assert_equal(0, data['status'], data)
  '''