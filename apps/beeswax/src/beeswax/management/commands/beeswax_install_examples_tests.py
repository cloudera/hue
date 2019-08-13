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

        SampleTable(table_data, 'beeswax', 'default').load(self.user)

        get.assert_called()


  def test_load_tables_concurrency_support(self):
    with patch('beeswax.server.dbms.get') as get:
      with patch('beeswax.management.commands.beeswax_install_examples.has_concurrency_support') as has_concurrency_support:
        get.return_value = Mock(
          get_table=Exception('Table could not be found')
        )
        has_concurrency_support.return_value = True

        cmd = Command()
        cmd._install_tables(self.user, 'beeswax', 'default', 'tables_transactional.json')

        get.assert_called()
