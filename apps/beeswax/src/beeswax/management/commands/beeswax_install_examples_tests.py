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

from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false

from desktop.auth.backend import rewrite_user
from desktop.lib.django_test_util import make_logged_in_client
from desktop.models import Document2
from useradmin.models import User, install_sample_user

from beeswax.management.commands.beeswax_install_examples import SampleTable, Command, SampleQuery

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


LOG = logging.getLogger()


class TestStandardTables():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")


  def test_install_queries_mysql(self):
    design_dict = {
      "name": "TestStandardTables Query",
      "desc": "Small query",
      "type": "2",
      "dialects": ["postgresql", "mysql", "presto"],
      "data": {
        "query": {
          "query": "SELECT 1",
          "type": 0,
          "email_notify": False,
          "is_parameterized": False,
          "database": "default"
        },
        "functions": [],
        "VERSION": "0.4.1",
        "file_resources": [],
        "settings": []
      }
    }
    interpreter = {'type': 'mysql', 'dialect': 'mysql'}

    design = SampleQuery(design_dict)
    assert_false(Document2.objects.filter(name='TestStandardTables Query').exists())

    with patch('notebook.models.get_interpreter') as get_interpreter:
      design.install(django_user=self.user, interpreter=interpreter)

      assert_true(Document2.objects.filter(name='TestStandardTables Query').exists())
      query = Document2.objects.filter(name='TestStandardTables Query').get()
      assert_equal('query-mysql', query.type)


class TestHiveServer2():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")

  def test_install_queries(self):
    design_dict = {
      "name": "TestBeswaxHiveTables Query",
      "desc": "Small query",
      "type": "0",
      "data": {
        "query": {
          "query": "SELECT 1",
          "type": 0,
          "email_notify": False,
          "is_parameterized": False,
          "database": "default"
        },
        "functions": [],
        "VERSION": "0.4.1",
        "file_resources": [],
        "settings": []
      }
    }
    interpreter = {'type': 'hive', 'dialect': 'hive'}

    design = SampleQuery(design_dict)
    assert_false(Document2.objects.filter(name='TestBeswaxHiveTables Query').exists())

    with patch('notebook.models.get_interpreter') as get_interpreter:
      design.install(django_user=self.user, interpreter=interpreter)

      assert_true(Document2.objects.filter(name='TestBeswaxHiveTables Query').exists())
      query = Document2.objects.filter(name='TestBeswaxHiveTables Query').get()
      assert_equal('query-hive', query.type)


  def test_create_table_load_data_but_no_fs(self):
    table_data = {
      "data_file": "sample_07.csv",
      "create_sql":
        """CREATE TABLE `sample_07` (\n  `code` string ,\n  `description` string ,\n  `total_emp` int ,\n  `salary` int )"""
        """\nSTORED AS parquet\nTBLPROPERTIES ('transactional'='true', 'transactional_properties'='insert_only')\n""",
      "table_name": "sample_07",
    }

    with patch('beeswax.management.commands.beeswax_install_examples.make_notebook') as make_notebook:
      with patch('beeswax.management.commands.beeswax_install_examples.has_concurrency_support') as has_concurrency_support:
        has_concurrency_support.return_value = True

        SampleTable(table_data, 'hive', 'default').install(self.user)

        make_notebook.assert_not_called()



class TestTransactionalTables():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = rewrite_user(User.objects.get(username="test"))


  def test_load_sample_07_with_concurrency_support(self):
    table_data = {
      "data_file": "sample_07.csv",
      "create_sql":
        """CREATE TABLE `sample_07` (\n  `code` string ,\n  `description` string ,\n  `total_emp` int ,\n  `salary` int )\n"""
        """STORED AS parquet\nTBLPROPERTIES ('transactional'='true', 'transactional_properties'='insert_only')\n""",
      "table_name": "sample_07",
      "transactional": True
    }

    with patch('beeswax.management.commands.beeswax_install_examples.make_notebook') as make_notebook:
      with patch('beeswax.management.commands.beeswax_install_examples.has_concurrency_support') as has_concurrency_support:
        has_concurrency_support.return_value = True

        SampleTable(table_data, 'hive', 'default').install(self.user)

        make_notebook.assert_called()


  def test_load_web_logs_with_concurrency_support(self):
    table_data = {
      "partition_files": {
        "`date`='2015-11-18'": "web_logs_1.csv",
        "`date`='2015-11-19'": "web_logs_2.csv",
        "`date`='2015-11-20'": "web_logs_3.csv",
        "`date`='2015-11-21'": "web_logs_4.csv"
      },
      "create_sql":
          """CREATE TABLE `web_logs`  (  `_version_` bigint,   `app` string,   `bytes` int,   `city` string,   `client_ip` string,   """
          """`code` smallint,   `country_code` string,   `country_code3` string,   `country_name` string,   `device_family` string,  """
          """ `extension` string,   `latitude` float,   `longitude` float,   `method` string,   `os_family` string,   `os_major` string,"""
          """   `protocol` string,   `record` string,   `referer` string,   `region_code` string,   `request` string,   `subapp` string,"""
          """   `time` string,   `url` string,   `user_agent` string,   `user_agent_family` string,   `user_agent_major` string,"""
          """   `id` string)\nPARTITIONED BY (  `date` string  )\nSTORED AS parquet\nTBLPROPERTIES ('transactional'='true',"""
          """ 'transactional_properties'='insert_only')""",
      "table_name": "web_logs",
      "columns": [
          {"name": "_version_", "type": "bigint"}, {"name": "app", "type": "string"}, {"name": "bytes", "type": "int"},
          {"name": "city", "type": "string"}, {"name": "client_ip", "type": "string"}, {"name": "code", "type": "smallint"},
          {"name": "country_code", "type": "string"}, {"name": "country_code3", "type": "string"},
          {"name": "country_name", "type": "string"}, {"name": "device_family", "type": "string"},
          {"name": "extension", "type": "string"}, {"name": "latitude", "type": "float"},
          {"name": "longitude", "type": "float"}, {"name": "method", "type": "string"},
          {"name": "os_family", "type": "string"}, {"name": "os_major", "type": "string"},
          {"name": "protocol", "type": "string"}, {"name": "record", "type": "string"},
          {"name": "referer", "type": "string"}, {"name": "region_code", "type": "string"},
          {"name": "request", "type": "string"}, {"name": "subapp", "type": "string"},
          {"name": "time", "type": "string"}, {"name": "url", "type": "string"},
          {"name": "user_agent", "type": "string"}, {"name": "user_agent_family", "type": "string"},
          {"name": "user_agent_major", "type": "string"}, {"name": "id", "type": "string"}, {"name": "date", "type": "string"}],
      "transactional": True
    }

    with patch('beeswax.management.commands.beeswax_install_examples.make_notebook') as make_notebook:
      with patch('beeswax.management.commands.beeswax_install_examples.has_concurrency_support') as has_concurrency_support:
        has_concurrency_support.return_value = True

        SampleTable(table_data, 'hive', 'default').install(self.user)

        make_notebook.assert_called()


  def test_create_phoenix_table(self):
    table_data = {
      "data_file": "./tables/us_population.csv",
      "create_sql":
        """CREATE TABLE IF NOT EXISTS us_population (\n  state CHAR(2) NOT NULL,\n  city VARCHAR NOT NULL,\n  """
        """population BIGINT\n  CONSTRAINT my_pk PRIMARY KEY (state, city)\n)\n""",
      "insert_sql": "UPSERT INTO us_population VALUES %(values)s",
      "table_name": "us_population",
      "dialects": ["phoenix"],
      "transactional": True,
      "is_multi_inserts": True
    }

    with patch('beeswax.management.commands.beeswax_install_examples.make_notebook') as make_notebook:
      SampleTable(table_data, 'phoenix', 'default').install(self.user)

      make_notebook.assert_called_with(
        name='Insert data in sample table us_population',
        editor_type='phoenix',
        statement="UPSERT INTO us_population VALUES ('CA', 'San Jose', 912332)",
        status='ready',
        database='default',
        last_executed=-1,
        on_success_url='assist.db.refresh', is_task=False
      )
