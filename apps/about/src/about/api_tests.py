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
from unittest.mock import Mock, patch

from rest_framework import status

from about.api import get_usage_analytics, update_usage_analytics


class TestUsageAnalyticsAPI:
  def test_get_usage_analytics_success(self):
    with patch('about.api.is_admin') as mock_is_admin:
      with patch('about.api.Settings.get_settings') as mock_get_settings:
        mock_is_admin.return_value = True
        mock_get_settings.return_value = Mock(collect_usage=True)

        request = Mock(method='GET', user=Mock())
        response = get_usage_analytics(request)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'analytics_enabled': True}

  def test_get_usage_analytics_unauthorized(self):
    with patch('about.api.is_admin') as mock_is_admin:
      mock_is_admin.return_value = False

      request = Mock(method='GET', user=Mock())
      response = get_usage_analytics(request)

      assert response.status_code == status.HTTP_403_FORBIDDEN
      assert response.data['message'] == "You must be a Hue admin to access this endpoint."

  def test_get_usage_analytics_error(self):
    with patch('about.api.is_admin') as mock_is_admin:
      with patch('about.api.Settings.get_settings') as mock_get_settings:
        mock_is_admin.return_value = True
        mock_get_settings.side_effect = Exception("Test error")

        request = Mock(method='GET', user=Mock())
        response = get_usage_analytics(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error retrieving usage analytics" in response.data['message']

  def test_update_usage_analytics_success(self):
    with patch('about.api.is_admin') as mock_is_admin:
      with patch('about.api.Settings.get_settings') as mock_get_settings:
        mock_is_admin.return_value = True
        mock_get_settings.return_value = Mock(save=Mock())

        request = Mock(method='POST', user=Mock(), POST={'analytics_enabled': 'true'})
        response = update_usage_analytics(request)

        assert response.status_code == status.HTTP_200_OK
        assert mock_get_settings.return_value.save.called
        assert response.data == {'analytics_enabled': True}

  def test_update_usage_analytics_unauthorized(self):
    with patch('about.api.is_admin') as mock_is_admin:
      mock_is_admin.return_value = False

      request = Mock(method='POST', user=Mock(), data={'analytics_enabled': 'true'})
      response = update_usage_analytics(request)

      assert response.status_code == status.HTTP_403_FORBIDDEN
      assert response.data['message'] == "You must be a Hue admin to access this endpoint."

  def test_update_usage_analytics_missing_param(self):
    with patch('about.api.is_admin') as mock_is_admin:
      mock_is_admin.return_value = True

      request = Mock(method='POST', user=Mock(), POST={})
      response = update_usage_analytics(request)

      assert response.status_code == status.HTTP_400_BAD_REQUEST
      assert response.data['message'] == 'Missing parameter: analytics_enabled is required.'

  def test_update_usage_analytics_error(self):
    with patch('about.api.is_admin') as mock_is_admin:
      with patch('about.api.Settings.get_settings') as mock_get_settings:
        mock_is_admin.return_value = True
        mock_get_settings.side_effect = Exception("Test error")

        request = Mock(method='POST', user=Mock(), POST={'analytics_enabled': 'true'})
        response = update_usage_analytics(request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error updating usage analytics" in response.data['message']
