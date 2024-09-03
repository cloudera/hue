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
import unittest
from unittest.mock import Mock, patch

import pytest
from django.test import TestCase

from desktop.auth.backend import rewrite_user
from desktop.conf import ENABLE_CONNECTORS
from desktop.lib.connectors.api import _get_installed_connectors
from desktop.lib.django_test_util import make_logged_in_client
from notebook.conf import _excute_test_query, config_validator, get_ordered_interpreters
from useradmin.models import User, get_default_user_group, update_app_permissions


class TestInterpreterConfig(TestCase):

  def setup_method(self, method):
    self.client = make_logged_in_client(
        username='test_check_config',
        groupname=get_default_user_group(),
        recreate=True,
        is_superuser=False
    )
    self.user = User.objects.get(username='test_check_config')
    self.user = rewrite_user(self.user)

  @classmethod
  def setup_class(cls):
    cls._class_resets = [
      ENABLE_CONNECTORS.set_for_testing(True),
    ]

  @classmethod
  def teardown_class(cls):
    for reset in cls._class_resets:
      reset()

  def test_get_ordered_interpreters(self):
    with patch('desktop.lib.connectors.api._get_installed_connectors') as _get_installed_connectors:
      _get_installed_connectors.return_value = [{
          'nice_name': 'Hive',
          'name': 'hive-1',
          'dialect': 'hive',
          'category': 'editor',
          'interface': 'hiveserver2',
          'settings': {},
          'dialect_properties': {'sql_identifier_quote': '`', 'is_sql': True},
        }
      ]

      interpreters = get_ordered_interpreters(user=self.user)

      assert interpreters, interpreters
      assert all(['dialect_properties' in interpreter for interpreter in interpreters]), interpreters
      assert any([interpreter.get('dialect_properties').get('sql_identifier_quote') for interpreter in interpreters]), interpreters


@pytest.mark.django_db
class TestCheckConfig():

  def setup_method(self):
    self.client = make_logged_in_client(
        username='test_check_config',
        groupname=get_default_user_group(),
        recreate=True,
        is_superuser=False
    )
    self.user = User.objects.get(username='test_check_config')
    self.user = rewrite_user(self.user)

  @classmethod
  def setup_class(cls):
    cls._class_resets = [
      ENABLE_CONNECTORS.set_for_testing(True),
    ]

  @classmethod
  def teardown_class(cls):
    for reset in cls._class_resets:
      reset()

  @patch('notebook.conf.has_connectors', return_value=True)
  def test_config_validator(self, has_connectors):

    with patch('desktop.lib.connectors.api._get_installed_connectors') as _get_installed_connectors:
      with patch('notebook.conf._excute_test_query') as _excute_test_query:
        _get_installed_connectors.return_value = [{
            'nice_name': 'Hive',
            'name': 'hive-1',
            'dialect': 'hive',
            'category': 'editor',
            'interface': 'hiveserver2',
            'settings': {},
            'dialect_properties': {'sql_identifier_quote': '`', 'is_sql': True},
          }
        ]
        _excute_test_query.return_value = Mock(content=json.dumps({'status': 0}))

        connectors = _get_installed_connectors(user=self.user)
        assert connectors, connectors

        warnings = config_validator(user=self.user)

        assert not warnings, warnings

        _excute_test_query.side_effect = Exception('')

        connectors = _get_installed_connectors(user=self.user)
        assert connectors, connectors

        warnings = config_validator(user=self.user)

        assert warnings, warnings
        assert 'Hive - hive (hive-1)' == warnings[0][0]
        assert 'Testing the connector connection failed' in warnings[0][1], warnings

  def test_excute_test_query(self):
    client = Mock()
    connector_id = 'hive'

    _excute_test_query(client=client, connector_id=connector_id)
