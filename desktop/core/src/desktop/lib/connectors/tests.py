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

from nose.tools import assert_equal, assert_true, assert_false

from desktop.lib.connectors.api import _get_installed_connectors
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access

from useradmin.models import User

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


class TestConnectors(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test_connector", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test_connector")
    grant_access(self.user.username, self.user.username, "desktop")


  def test_page(self):
    response = self.client.get("/desktop/connectors/")

    assert_equal(200, response.status_code)


  def test_get_connector_types(self):
    response = self.client.post("/desktop/connectors/api/types/")

    assert_equal(200, response.status_code)


def test_get_installed_editor_connectors():

  with patch('desktop.lib.connectors.api.CONNECTORS.get') as CONNECTORS:
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
    assert_true(len(editor_category), connectors)
    assert_equal(1, len(editor_category), editor_category)
