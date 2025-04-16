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

import sys
import json
import unittest
from unittest.mock import Mock, patch

import pytest
from django.test import TestCase

from desktop.auth.backend import is_admin, rewrite_user
from desktop.conf import ENABLE_CONNECTORS, ENABLE_ORGANIZATIONS
from desktop.lib.connectors.api import _get_installed_connectors
from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import Connector, User, get_default_user_group, update_app_permissions
from useradmin.permissions import GroupPermission, HuePermission


@pytest.mark.django_db
class TestConnectors(object):

  def setup_method(self):
    self.client = make_logged_in_client(username="test_connector", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test_connector")

    self.admin_client = make_logged_in_client(username="admin_test_connector", recreate=True, is_superuser=True)
    self.admin_user = User.objects.get(username="admin_test_connector")

  @classmethod
  def setup_class(cls):
    cls._class_resets = [
      ENABLE_CONNECTORS.set_for_testing(True),
      ENABLE_ORGANIZATIONS.set_for_testing(False),
    ]

  @classmethod
  def teardown_class(cls):
    for reset in cls._class_resets:
      reset()

  def test_page(self):
    response = self.client.get("/desktop/connectors/")

    assert 200 == response.status_code

  def test_get_connector_types(self):
    response = self.client.post("/desktop/connectors/api/types/")

    assert 200 == response.status_code

  def test_create_connector_perm(self):
    response = self.client.post("/desktop/connectors/api/instance/update/")
    assert 401 == response.status_code

    response = self.client.post("/desktop/connectors/api/instance/delete/")
    assert 401 == response.status_code

  def test_test_connector(self):
    connector = {
      'connector': json.dumps({
        'name': 'hive', 'dialect': 'hive', 'id': 'id-1', 'nice_name': 'Sales DB', 'settings': {}, 'interface': 'hiveserver2'
      })
    }

    response = self.client.post("/desktop/connectors/api/instance/test/", connector)
    assert 401 == response.status_code

    with patch('desktop.lib.connectors.api.config_validator') as config_validator:
      config_validator.return_value = []

      response = self.admin_client.post("/desktop/connectors/api/instance/test/", connector)
      assert 200 == response.status_code
      assert not json.loads(response.content)['warnings']

    with patch('notebook.conf._excute_test_query') as _excute_test_query:
      _excute_test_query.side_effect = Exception('')  # Just in case as relying on connector id not existing

      response = self.admin_client.post("/desktop/connectors/api/instance/test/", connector)
      assert 200 == response.status_code
      assert json.loads(response.content)['warnings']


class TestConnectorListing(TestCase):

  def setup_method(self):
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
  def setup_class(cls):
    if not ENABLE_CONNECTORS.get():  # Skip for now
      pytest.skip("Skipping Test")

    cls._class_resets = [
      ENABLE_CONNECTORS.set_for_testing(True),
    ]

  @classmethod
  def teardown_class(cls):
    HuePermission.objects.all().delete()

    for reset in cls._class_resets:
      reset()

    update_app_permissions()

  def test_get_installed_editor_connectors(self):

    with patch('desktop.lib.connectors.models.Connector.objects.all') as ConnectorObjectsAll:
      ConnectorObjectsAll.return_value = [
        Connector(name='MySql', dialect='mysql', settings=json.dumps([{"name": "url", "value": "mysql://hue:pwd@hue:3306/hue"}]))
      ]

      connectors = _get_installed_connectors()

      editor_category = [category for category in connectors if category['category'] == 'editor']
      assert editor_category, connectors
      assert 1 == len(editor_category), editor_category

  def test_get_connectors_for_user(self):
    connector = Connector.objects.create(
        name='MySql', dialect='mysql', settings=json.dumps([{"name": "url", "value": "mysql://hue:pwd@hue:3306/hue"}])
    )

    # Could leverate update_app_permissions() instead of adding manually the permission but this is more lightweight for now
    conn_perm = HuePermission.objects.create(app=connector.name, action='access', description='', connector=connector)
    GroupPermission.objects.create(group=self.user.groups.first(), hue_permission=conn_perm)

    try:
      assert self.user.get_permissions()
      connectors = _get_installed_connectors(user=self.user)
      assert connectors, connectors

      connectors = _get_installed_connectors(user=self.alone_user)
      assert not connectors, connectors
    finally:
      connector.delete()
