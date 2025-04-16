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

import sys
import json
import logging
from unittest.mock import Mock, patch

import pytest
from django.urls import reverse

import desktop.conf as desktop_conf
from desktop.lib.django_test_util import make_logged_in_client
from impala.dbms import get_query_server_config
from useradmin.models import User

LOG = logging.getLogger()


@pytest.mark.django_db
class TestDbms():

  def setup_method(self):
    self.client = make_logged_in_client()

  def test_get_connector_config(self):
    connector = {
      'type': 'impala-compute',
      'name': 'impala-1',
      'dialect': 'impala',
      'interface': 'hiveserver2',
      'options': {'server_host': 'gethue.com', 'server_port': 10000}
    }

    with patch('impala.dbms.has_connectors') as has_connectors:
      has_connectors.return_value = True

      config = get_query_server_config(connector)
      assert 'impersonation_enabled' in config, config
