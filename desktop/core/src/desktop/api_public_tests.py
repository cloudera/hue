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

import json
import pytest
import sys

from django.http import HttpResponse
from django.urls import reverse



from useradmin.models import User
from desktop.conf import CUSTOM
from desktop.api_public import get_django_request
from desktop.lib.django_test_util import Client, make_logged_in_client

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


@pytest.mark.django_db
class TestCoreApi():
  def setup_method(self):
    self.unauthorized_client = Client()

  def test_banners(self):
    with patch('desktop.api2.get_banner_message') as get_banner_message:
      try:
        configured_banner = '<div>Some config banner</div>'
        system_banner = '<div>Some system banner</div>'
        done = CUSTOM.BANNER_TOP_HTML.set_for_testing(configured_banner)
        get_banner_message.return_value = system_banner

        response = self.unauthorized_client.get(reverse('api:core_banners'))

        get_banner_message.assert_called()
        json_resp = json.loads(response.content)
        assert json_resp['configured'] == configured_banner
        assert json_resp['system'] == system_banner
      finally:
        done()


@pytest.mark.django_db
class TestEditorApi():
  TEST_INTERPRETER = {
    'name': 'MySql', 'displayName': 'MySql', 'type': '1', 'interface': 'sqlalchemy',
    'options': {'url': 'mysql://hue:hue@localhost:3306/hue', 'has_ssh': False, 'ssh_server_host': '127.0.0.1'},
    'dialect': 'mysql',
    'dialect_properties': {'is_sql': True, 'sql_identifier_quote': '`', 'sql_identifier_comment_single': '--',
                           'has_catalog': True, 'has_database': True, 'has_table': True, 'has_live_queries': False,
                           'has_optimizer_risks': True, 'has_optimizer_values': True, 'has_auto_limit': False,
                           'has_reference_language': False, 'has_reference_functions': False,
                           'has_use_statement': False}, 'category': 'editor', 'is_sql': True, 'is_catalog': False
  }

  def setup_method(self):
    self.client = make_logged_in_client(username="api_user", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_api_user", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="api_user")
    self.user_not_me = User.objects.get(username="not_api_user")

  def test_urls_exist(self):
    assert reverse('api:editor_execute', args=['hive']) == '/api/v1/editor/execute/hive'

  def test_editor_execute(self):
    with patch('desktop.api_public.notebook_api.execute') as execute:
      with patch('desktop.api_public._get_interpreter_from_dialect') as _get_interpreter_from_dialect:
        execute.return_value = HttpResponse()
        _get_interpreter_from_dialect.return_value = TestEditorApi.TEST_INTERPRETER

        self.client.post(reverse('api:editor_execute', args=['hive']), {'statement': 'SHOW TABLES'})

      execute.assert_called()
      if not execute.call_args.args[1]:
        raise SkipTest()  # Incorrect in Py3 CircleCi
      assert execute.call_args.args[1] == 'hive'
      json.loads(execute.call_args.args[0].POST['notebook'])
      json.loads(execute.call_args.args[0].POST['snippet'])

  def test_get_django_request(self):
    request = Mock()

    django_request = get_django_request(request)

    assert hasattr(django_request.user, 'has_hue_permission')
