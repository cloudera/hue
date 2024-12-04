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

import json
import socket
from unittest.mock import Mock, patch

import pytest

from desktop.lib.django_test_util import make_logged_in_client
from desktop.log.api import get_hue_logs
from useradmin.models import User


@pytest.mark.django_db
class TestHueLogs:
  def setup_method(self):
    self.client_admin = make_logged_in_client(username="test_admin", groupname="default", recreate=True, is_superuser=True)
    self.user_admin = User.objects.get(username="test_admin")

    self.client_not_admin = make_logged_in_client(username="test_not_admin", groupname="default", recreate=True, is_superuser=False)
    self.user_not_admin = User.objects.get(username="test_not_admin")

  def test_get_hue_logs_unauthorized(self):
    request = Mock(method='GET', user=self.user_not_admin)

    response = get_hue_logs(request)
    res_content = response.content.decode('utf-8')

    assert response.status_code == 403
    assert res_content == 'You must be a Hue admin to access this endpoint.'

  def test_log_directory_not_set(self):
    with patch('desktop.log.api.os.getenv') as os_getenv:
      request = Mock(method='GET', user=self.user_admin)
      os_getenv.return_value = None

      response = get_hue_logs(request)
      res_content = response.content.decode('utf-8')

      assert response.status_code == 404
      assert res_content == 'The log directory is not set or does not exist.'

  def test_log_file_not_found(self):
    with patch('desktop.log.api.os.getenv') as os_getenv:
      with patch('desktop.log.api.os.path.exists') as os_path_exist:
        request = Mock(method='GET', user=self.user_admin)
        os_getenv.return_value = '/var/log/hue/'
        os_path_exist.return_value = False

        response = get_hue_logs(request)
        res_content = response.content.decode('utf-8')

        assert response.status_code == 404
        assert res_content == 'The log file does not exist.'

  def test_get_hue_logs_success(self):
    with patch('desktop.log.api.os') as mock_os:
      with patch('desktop.log.api._read_log_file') as _read_log_file:
        request = Mock(method='GET', user=self.user_admin)
        _read_log_file.return_value = 'test log content'

        mock_os.os_getenv.return_value = '/var/log/hue/'
        mock_os.path.exists.return_value = True
        mock_os.path.getsize.return_value = 32 * 1024 * 2  # Greater than log buffer size

        response = get_hue_logs(request)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data == {'hue_hostname': socket.gethostname(), 'logs': 'test log content'}
