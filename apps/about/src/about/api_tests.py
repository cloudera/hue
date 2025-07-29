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
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from useradmin.models import User


@pytest.mark.django_db
class TestUsageAnalyticsSettingsAPI:
  @pytest.fixture
  def api_client(self) -> APIClient:
    return APIClient()

  @pytest.fixture
  def regular_user(self, db) -> User:
    return User.objects.create_user(username="testuser", password="")

  @pytest.fixture
  def admin_user(self, db) -> User:
    return User.objects.create_superuser(username="adminuser", password="")

  @pytest.fixture
  def analytics_settings_url(self) -> str:
    return reverse("api:core_usage_analytics")

  @patch("desktop.auth.api_permissions.is_admin", return_value=True)
  @patch("about.api.Settings.get_settings")
  def test_get_settings_as_admin_success(self, mock_get_settings, mock_is_admin, api_client, admin_user, analytics_settings_url):
    mock_get_settings.return_value = MagicMock(collect_usage=True)
    api_client.force_authenticate(user=admin_user)

    response = api_client.get(analytics_settings_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"collect_usage": True}

  @patch("desktop.auth.api_permissions.is_admin", return_value=False)
  def test_get_settings_as_non_admin_forbidden(self, mock_is_admin, api_client, regular_user, analytics_settings_url):
    api_client.force_authenticate(user=regular_user)

    response = api_client.get(analytics_settings_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data == {"detail": "You must be a Hue admin to perform this action."}

  @patch("desktop.auth.api_permissions.is_admin", return_value=True)
  @patch("about.api.Settings.get_settings")
  def test_get_settings_as_admin_error(self, mock_get_settings, mock_is_admin, api_client, admin_user, analytics_settings_url):
    mock_get_settings.side_effect = ObjectDoesNotExist("Settings not found")
    api_client.force_authenticate(user=admin_user)

    response = api_client.get(analytics_settings_url)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "A server error occurred while retrieving usage analytics settings."}

  @patch("desktop.auth.api_permissions.is_admin", return_value=True)
  @patch("about.api.Settings.get_settings")
  def test_put_settings_as_admin_success(self, mock_get_settings, mock_is_admin, api_client, admin_user, analytics_settings_url):
    mock_settings = MagicMock()
    mock_get_settings.return_value = mock_settings
    api_client.force_authenticate(user=admin_user)
    payload = {"collect_usage": False}

    response = api_client.put(analytics_settings_url, data=payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == payload
    assert mock_settings.collect_usage is False
    mock_settings.save.assert_called_once()

  @patch("desktop.auth.api_permissions.is_admin", return_value=False)
  def test_put_settings_as_non_admin_forbidden(self, mock_is_admin, api_client, regular_user, analytics_settings_url):
    api_client.force_authenticate(user=regular_user)

    response = api_client.put(analytics_settings_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data == {"detail": "You must be a Hue admin to perform this action."}

  @patch("desktop.auth.api_permissions.is_admin", return_value=True)
  @patch("about.api.Settings.get_settings")
  def test_put_settings_as_admin_error(self, mock_get_settings, mock_is_admin, api_client, admin_user, analytics_settings_url):
    mock_get_settings.side_effect = ObjectDoesNotExist("Settings not found")
    api_client.force_authenticate(user=admin_user)
    payload = {"collect_usage": False}

    response = api_client.put(analytics_settings_url, data=payload, format="json")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data == {"error": "A server error occurred while saving the usage analytics settings."}

  @patch("desktop.auth.api_permissions.is_admin", return_value=True)
  @patch("about.api.Settings.get_settings")
  def test_put_settings_as_admin_missing_field(self, mock_get_settings, mock_is_admin, api_client, admin_user, analytics_settings_url):
    mock_get_settings.return_value = MagicMock(collect_usage=True)
    api_client.force_authenticate(user=admin_user)
    payload = {}

    response = api_client.put(analytics_settings_url, data=payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"collect_usage": ["This field is required."]}
