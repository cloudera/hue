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

from nose.tools import assert_equal, assert_false, assert_not_equal, assert_true

import json

import logging

from django.core.urlresolvers import reverse
from desktop.lib.django_test_util import make_logged_in_client


LOG = logging.getLogger(__name__)


class RdbmsIndexerTests():

  def test_get_sample_data(self, connect_credentials, db_name):
    db_name = 'test'
    connect_credentials = {}
    connect_credentials['input_format'] = 'db'
    connect_credentials['host_name'] = 'localhost'
    connect_credentials['user_name'] = 'root'
    connect_credentials['password'] = 'root'
    connect_credentials['port'] = '3306'
    connect_credentials['column_name'] = 'empid'
    connect_credentials['table_name'] = 'employee'

    client = make_logged_in_client()
    resp = client.get(reverse('rdbms_indexer:get_sample_data', kwargs={'database': db_name, 'table': connect_credentials['table_name']})) # not sure how to instantiate RdbmsIndexer class and pas the dictionary.
    data = json.loads(resp.content)

    assert_equal(0, data['status'], data)
    assert_true(data['rows'], data)