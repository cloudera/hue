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

from mock import patch, Mock
from nose.tools import assert_equal, assert_true

from beeswax.server.dbms import get_query_server_config


LOG = logging.getLogger(__name__)


class TestGetQueryServerConfig():

  def test_get_default(self):

    with patch('beeswax.conf.HIVE_SERVER_HOST.get') as HIVE_SERVER_HOST:
      with patch('beeswax.conf.HIVE_SERVER_PORT.get') as HIVE_SERVER_PORT:
        HIVE_SERVER_HOST.return_value = 'hive.gethue.com'
        HIVE_SERVER_PORT.return_value=10002

        query_server = get_query_server_config()

        assert_equal(query_server['server_name'], 'beeswax')
        assert_equal(query_server['server_host'], 'hive.gethue.com')
        assert_equal(query_server['server_port'], 10002)
