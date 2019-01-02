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

import logging

from django.contrib.auth.models import User

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_false, assert_not_equal, assert_true

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client

from indexer.conf import ENABLE_SQOOP
from indexer.indexers.rdbms import _get_api
from librdbms.server import dbms as rdbms


LOG = logging.getLogger(__name__)

class TestRdbmsIndexer():

  @classmethod
  def setup_class(cls):
    if not ENABLE_SQOOP.get():
      raise SkipTest
    if not rdbms.get_query_server_config(server='mysql'):
      raise SkipTest
    cls.client = make_logged_in_client()
    cls.user = User.objects.get(username='test')
    cls.user = rewrite_user(cls.user)
    request = Bag()
    request.user = cls.user
    request.POST = {'source': '{"rdbmsMode":"configRdbms", "rdbmsType": "mysql", "inputFormat": "rdbms"}'}
    cls.indexer = _get_api(request)

  @classmethod
  def teardown_class(cls):
    cls.user.is_superuser = False
    cls.user.save()

  def test_get_sample_data(cls):
    data = cls.indexer.get_sample_data({}, database='hue', table='desktop_document2', column='id')

    assert_equal(0, data['status'], data)
    assert_not_equal('', data['rows'], data)

class Bag(dict):
  pass