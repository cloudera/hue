#!/usr/bin/env python
## -*- coding: utf-8 -*-
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
import unittest

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false

from desktop.auth.backend import rewrite_user
from desktop.conf import ENABLE_CONNECTORS
from desktop.lib.connectors.api import _get_installed_connectors
from desktop.lib.django_test_util import make_logged_in_client

from useradmin.models import User, update_app_permissions, get_default_user_group


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


class TestConnectors(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test_connector", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test_connector")

  def test_page(self):
    response = self.client.get("/desktop/connectors/")

    assert_equal(200, response.status_code)

  def test_get_connector_types(self):
    response = self.client.post("/desktop/connectors/api/types/")

    assert_equal(200, response.status_code)

  def test_create_connector_perm(self):
    response = self.client.post("/desktop/connectors/api/instance/update/")
    assert_equal(401, response.status_code)

    response = self.client.post("/desktop/connectors/api/instance/delete/")
    assert_equal(401, response.status_code)


class TestConnectorListing(unittest.TestCase):

  def setUp(self):
    self.client = make_logged_in_client(
        username='test_connector',
        groupname=get_default_user_group(),
        recreate=True,
        is_superuser=False
    )
    self.user = User.objects.get(username='test_connector')
    self.user = rewrite_user(self.user)

    self.alone_client = make_logged_in_client(
        username='test_alone',
        groupname='alone',  # Not in default group
        recreate=True,
        is_superuser=False
    )
    self.alone_user = User.objects.get(username='test_alone')
    self.alone_user = rewrite_user(self.alone_user)

  @classmethod
  def setUpClass(cls):
    if not ENABLE_CONNECTORS.get():  # Skip for now
      raise SkipTest

    cls._class_resets = [
      ENABLE_CONNECTORS.set_for_testing(True),
    ]

  @classmethod
  def tearDownClass(cls):
    for reset in cls._class_resets:
      reset()

    update_app_permissions()


  def test_get_installed_editor_connectors(self):

    with patch('desktop.lib.connectors.models.CONNECTORS.get') as CONNECTORS:
      CONNECTORS.return_value = {
        'mysql-1': Mock(
          NICE_NAME=Mock(get=Mock(return_value='MySql')),
          DIALECT=Mock(get=Mock(return_value='mysql')),
          INTERFACE=Mock(get=Mock(return_value='sqlalchemy')),
          SETTINGS=Mock(get=Mock(return_value=[{"name": "url", "value": "mysql://hue:pwd@hue:3306/hue"}])),
        )
      }

      connectors = _get_installed_connectors()

      editor_category = [category for category in connectors if category['category'] == 'editor']
      assert_true(editor_category, connectors)
      assert_equal(1, len(editor_category), editor_category)


  def test_get_connectors_for_user(self):

    with patch('desktop.lib.connectors.models.CONNECTORS.get') as CONNECTORS:
      CONNECTORS.return_value = {
        'mysql-1': Mock(
          NICE_NAME=Mock(get=Mock(return_value='MySql')),
          DIALECT=Mock(get=Mock(return_value='mysql')),
          INTERFACE=Mock(get=Mock(return_value='sqlalchemy')),
          SETTINGS=Mock(get=Mock(return_value=[{"name": "url", "value": "mysql://hue:pwd@hue:3306/hue"}])),
        )
      }

      update_app_permissions()

      connectors = _get_installed_connectors(user=self.user)
      assert_true(connectors, connectors)

      connectors = _get_installed_connectors(user=self.alone_user)
      assert_false(connectors, connectors)
