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
import sys
from beeswax.server.dbms import get_query_server_config
from desktop.lib.exceptions_renderable import PopupException
from desktop.settings import CACHES_HIVE_DISCOVERY_KEY
from django.core.cache import caches
from nose.tools import assert_equal, assert_raises

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock

LOG = logging.getLogger(__name__)
cache = caches[CACHES_HIVE_DISCOVERY_KEY]


class TestGetQueryServerConfig():
  def setUp(self):
    cache.clear()

  def test_get_default(self):

    with patch('beeswax.conf.HIVE_SERVER_HOST.get') as HIVE_SERVER_HOST:
      with patch('beeswax.conf.HIVE_SERVER_PORT.get') as HIVE_SERVER_PORT:
        HIVE_SERVER_HOST.return_value = 'hive.gethue.com'
        HIVE_SERVER_PORT.return_value = 10002

        query_server = get_query_server_config()

        assert_equal(query_server['server_name'], 'beeswax')
        assert_equal(query_server['server_host'], 'hive.gethue.com')
        assert_equal(query_server['server_port'], 10002)

  def test_get_impala(self):

    with patch('impala.conf.SERVER_HOST.get') as SERVER_HOST:
      with patch('impala.conf.SERVER_PORT.get') as SERVER_PORT:
        SERVER_HOST.return_value = 'impala.gethue.com'
        SERVER_PORT.return_value = 10002

        query_server = get_query_server_config(name='impala')

        assert_equal(query_server['server_name'], 'impala')
        assert_equal(query_server['server_host'], 'impala.gethue.com')
        assert_equal(query_server['server_port'], 10002)

  def test_get_llap(self):

    with patch('beeswax.conf.LLAP_SERVER_HOST.get') as LLAP_SERVER_HOST:
      with patch('beeswax.conf.LLAP_SERVER_PORT.get') as LLAP_SERVER_PORT:
        LLAP_SERVER_HOST.return_value = 'hive-llap.gethue.com'
        LLAP_SERVER_PORT.return_value = 10002

        query_server = get_query_server_config(name='llap')

        assert_equal(query_server['server_name'], 'beeswax')
        assert_equal(query_server['server_host'], 'hive-llap.gethue.com')
        assert_equal(query_server['server_port'], 10002)

  def test_get_llap_discovery(self):

    with patch('beeswax.conf.HIVE_DISCOVERY_LLAP.get') as HIVE_DISCOVERY_LLAP:
      with patch('beeswax.conf.HIVE_DISCOVERY_LLAP_HA.get') as HIVE_DISCOVERY_LLAP_HA:
        with patch('beeswax.server.dbms.KazooClient') as KazooClient:
          with patch(
              'beeswax.conf.LLAP_SERVER_PORT.get') as LLAP_SERVER_PORT:  # Workaround, to remove when assert
            # server_port ok
            HIVE_DISCOVERY_LLAP.return_value = True
            HIVE_DISCOVERY_LLAP_HA.return_value = False
            LLAP_SERVER_PORT.return_value = 25000
            KazooClient.return_value = Mock(
              exists=Mock(return_value=True),
              # Bug "TypeError: expected string or buffer" if False, to add a new test case and fix
              get_children=Mock(return_value=['llap1=hive-llap-1.gethue.com:20000;llap2=hive-llap-2.gethue.com:20000'])
            )
            query_server = get_query_server_config(name='llap')

            assert_equal(query_server['server_name'], 'beeswax')
            assert_equal(query_server['server_host'], 'hive-llap-1.gethue.com')
            # assert_equal(query_server['server_port'], 20000) # Bug Always set to LLAP_SERVER_PORT?
            assert_equal(query_server['server_port'], 25000)  # To remove this line and comment above when fixed.

  def test_get_llap_ha_discovery_all_server_down(self):

    with patch('beeswax.conf.HIVE_DISCOVERY_LLAP.get') as HIVE_DISCOVERY_LLAP:
      with patch('beeswax.conf.HIVE_DISCOVERY_LLAP_HA.get') as HIVE_DISCOVERY_LLAP_HA:
        with patch('beeswax.server.dbms.KazooClient') as KazooClient:
          HIVE_DISCOVERY_LLAP.return_value = True
          HIVE_DISCOVERY_LLAP_HA.return_value = True

          KazooClient.return_value = Mock(
            exists=Mock(return_value=True),
            # Bug "TypeError: expected string or buffer" if False, to add a new test case and fix
            get_children=Mock(return_value=[])
          )

          assert_raises(PopupException, get_query_server_config, name='llap')
          try:
            query_server = get_query_server_config(name='llap')
          except PopupException as e:
            assert_equal(e.message, 'There is no running Hive LLAP server available')

  def test_get_hive_ha_discovery_all_server_down(self):

    with patch('beeswax.conf.HIVE_DISCOVERY_LLAP.get') as HIVE_DISCOVERY_LLAP:
      with patch('beeswax.conf.HIVE_DISCOVERY_LLAP_HA.get') as HIVE_DISCOVERY_LLAP_HA:
        with patch('beeswax.conf.HIVE_DISCOVERY_HS2.get') as HIVE_DISCOVERY_HS2:
          with patch('beeswax.conf.HIVE_DISCOVERY_HIVESERVER2_ZNODE.get') as HIVE_DISCOVERY_HIVESERVER2_ZNODE:
            with patch('beeswax.server.dbms.KazooClient') as KazooClient:
              HIVE_DISCOVERY_LLAP.return_value = False
              HIVE_DISCOVERY_LLAP_HA.return_value = False
              HIVE_DISCOVERY_HS2.return_value = True
              HIVE_DISCOVERY_HIVESERVER2_ZNODE.return_value = True

              KazooClient.return_value = Mock(
                exists=Mock(return_value=True),
                # Bug "TypeError: expected string or buffer" if False, to add a new test case and fix
                get_children=Mock(return_value=[])
              )

              assert_raises(PopupException, get_query_server_config, name='hive')
              try:
                query_server = get_query_server_config(name='hive')
              except PopupException as e:
                assert_equal(e.message, 'There are no running Hive server available')

  def test_get_hs2_discovery(self):

    with patch('beeswax.conf.HIVE_DISCOVERY_HS2.get') as HIVE_DISCOVERY_HS2:
      with patch('beeswax.conf.HIVE_DISCOVERY_HIVESERVER2_ZNODE.get') as HIVE_DISCOVERY_HIVESERVER2_ZNODE:
        with patch('beeswax.server.dbms.KazooClient') as KazooClient:
          HIVE_DISCOVERY_HS2.return_value = True
          HIVE_DISCOVERY_HIVESERVER2_ZNODE.return_value = True
          KazooClient.return_value = Mock(
            exists=Mock(return_value=True),
            # Bug "TypeError: expected string or buffer" if False, to add a new test case and fix
            get_children=Mock(return_value=[
              'serverUri=hive-llap-1.gethue.com:10000;serverUri=hive-llap-2.gethue.com:10000'])
          )

          try:
            query_server = get_query_server_config(name='hive')
          except PopupException as e:
            assert_equal(e.message, 'There are no running Hive server available')

          assert_equal(query_server['server_name'], 'beeswax')
          assert_equal(query_server['server_host'], 'hive-llap-1.gethue.com')
          assert_equal(query_server['server_port'], 10000)


# TODO: all the combinations in new test methods, e.g.:
# HIVE_DISCOVERY_LLAP_HA.get() --> True
# ...
