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

import json
import logging
import sys

from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_equal, assert_false, assert_raises

from django.urls import reverse

import desktop.conf as desktop_conf
from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import User


from impala.dbms import get_query_server_config

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


LOG = logging.getLogger()


class TestDbms():

  def setUp(self):
    self.client = make_logged_in_client()


  def test_get_connector_config(self):
    connector = {
      'type': 'impala-1',
      'dialect': 'impala',
      'options': {'server_host': 'gethue.com', 'server_port': 10000}
    }

    with patch('impala.dbms.has_connectors') as has_connectors:
      has_connectors.return_value = True

      config = get_query_server_config(connector)
      assert_true('impersonation_enabled' in config, config)
