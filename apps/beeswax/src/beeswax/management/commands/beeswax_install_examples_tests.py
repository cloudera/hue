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

from mock import patch, Mock, MagicMock
from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access

from beeswax.management.commands.beeswax_install_examples import SampleTable, Command

from django.contrib.auth.models import User


LOG = logging.getLogger(__name__)


class TestTransactionalTables():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)

    self.user = rewrite_user(User.objects.get(username="test"))
    grant_access("test", "default", "notebook")


  def test_load_sample_07_with_concurrency_support(self):
    table_data =   {
      "data_file": "sample_07.csv",
      "create_hql": "CREATE TABLE `sample_07` (\n  `code` string ,\n  `description` string ,\n  `total_emp` int ,\n  `salary` int )\nSTORED AS parquet\nTBLPROPERTIES ('transactional'='true', 'transactional_properties'='insert_only')\n",
      "table_name": "sample_07"
    }

    with patch('beeswax.server.dbms.get') as get:
      with patch('beeswax.management.commands.beeswax_install_examples.has_concurrency_support') as has_concurrency_support:
        has_concurrency_support.return_value = True

        SampleTable(table_data, 'beeswax', 'default').install(self.user)

        get.assert_called()


  def test_load_web_logs_with_concurrency_support(self):
    table_data = {
      "partition_files": {
        "`date`='2015-11-18'": "web_logs_1.csv",
        "`date`='2015-11-19'": "web_logs_2.csv",
        "`date`='2015-11-20'": "web_logs_3.csv",
        "`date`='2015-11-21'": "web_logs_4.csv"
      },
      "create_hql": "CREATE TABLE `web_logs`  (  `_version_` bigint,   `app` string,   `bytes` int,   `city` string,   `client_ip` string,   `code` smallint,   `country_code` string,   `country_code3` string,   `country_name` string,   `device_family` string,   `extension` string,   `latitude` float,   `longitude` float,   `method` string,   `os_family` string,   `os_major` string,   `protocol` string,   `record` string,   `referer` string,   `region_code` string,   `request` string,   `subapp` string,   `time` string,   `url` string,   `user_agent` string,   `user_agent_family` string,   `user_agent_major` string,   `id` string)\nPARTITIONED BY (  `date` string  )\nSTORED AS parquet\nTBLPROPERTIES ('transactional'='true', 'transactional_properties'='insert_only')",
      "table_name": "web_logs",
      "columns": [{"name": "_version_", "type": "bigint"}, {"name": "app", "type": "string"}, {"name": "bytes", "type": "int"}, {"name": "city", "type": "string"}, {"name": "client_ip", "type": "string"}, {"name": "code", "type": "smallint"}, {"name": "country_code", "type": "string"}, {"name": "country_code3", "type": "string"}, {"name": "country_name", "type": "string"}, {"name": "device_family", "type": "string"}, {"name": "extension", "type": "string"}, {"name": "latitude", "type": "float"}, {"name": "longitude", "type": "float"}, {"name": "method", "type": "string"}, {"name": "os_family", "type": "string"}, {"name": "os_major", "type": "string"}, {"name": "protocol", "type": "string"}, {"name": "record", "type": "string"}, {"name": "referer", "type": "string"}, {"name": "region_code", "type": "string"}, {"name": "request", "type": "string"}, {"name": "subapp", "type": "string"}, {"name": "time", "type": "string"}, {"name": "url", "type": "string"}, {"name": "user_agent", "type": "string"}, {"name": "user_agent_family", "type": "string"}, {"name": "user_agent_major", "type": "string"}, {"name": "id", "type": "string"}, {"name": "date", "type": "string"}]
    }

    with patch('beeswax.server.dbms.get') as get:
      with patch('beeswax.management.commands.beeswax_install_examples.has_concurrency_support') as has_concurrency_support:
        has_concurrency_support.return_value = True

        SampleTable(table_data, 'beeswax', 'default').install(self.user)

        get.assert_called()
