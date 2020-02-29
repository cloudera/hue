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
import json
import sys

from django.urls import reverse
from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.connectors.models import Connector
from useradmin.models import User

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


LOG = logging.getLogger(__name__)


class TestInstallExamples():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=True, is_admin=True)
    self.user = User.objects.get(username="test")


  def test_install_via_insert_mysql(self):
    with patch('notebook.views.Connector.objects') as ConnectorObjects:
      with patch('notebook.views.get_interpreter') as get_interpreter:
        with patch('notebook.connectors.base.get_ordered_interpreters') as get_ordered_interpreters:
          with patch('beeswax.management.commands.beeswax_install_examples.make_notebook') as make_notebook:

            ConnectorObjects.get = Mock(
              return_value=Connector(
                id=10,
                name='MySql',
                dialect='mysql',
              ),
            )

            get_interpreter.return_value = {'type': 10, 'dialect': 'mysql'}
            get_ordered_interpreters.return_value = [
              {
                'name': 'MySql',
                'type': 10,
                'dialect': 'mysql',
                'interface': 'sqlalchemy',
                'options': {'url': 'mysql://hue:pwd@hue:3306/hue'},
              }
            ]

            resp = self.client.post(reverse('notebook:install_examples'), {'db_name': 'default'})
            data = json.loads(resp.content)

            assert_equal(0, data['status'], data)
            assert_equal(
                'Query Sample: Salary Analysis mysql installed. Table default.employe_sample installed.',
                data['message'],
                data
            )
            assert_equal('', data['errorMessage'], data)

            make_notebook.assert_called()


  def test_install_via_load_hive(self):
    pass

  def test_install_via_insert_hive(self):
    pass
