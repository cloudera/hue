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

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from useradmin.models import User


class TestUsageAnalyticsSettingsAPI(TestCase):
  def setUp(self):
    self.api_client = APIClient()
    self.regular_user = User.objects.create_user(username="testuser", password="")
    self.admin_user = User.objects.create_superuser(username="adminuser", password="")
    self.analytics_settings_url = reverse("api:core_usage_analytics")

  @patch("desktop.auth.api_permissions.is_admin", return_value=True)
  @patch("about.api.Settings.get_settings")
  def test_get_settings_as_admin_success(self, mock_get_settings, mock_is_admin):
    mock_get_settings.return_value = MagicMock(collect_usage=True)
    self.api_client.force_authenticate(user=self.admin_user)

    response = self.api_client.get(self.analytics_settings_url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data, {"collectUsage": True})

  @patch("desktop.auth.api_permissions.is_admin", return_value=False)
  def test_get_settings_as_non_admin_forbidden(self, mock_is_admin):
    self.api_client.force_authenticate(user=self.regular_user)

    response = self.api_client.get(self.analytics_settings_url)

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    self.assertEqual(response.data, {"detail": "You must be a Hue admin to perform this action."})

  @patch("desktop.auth.api_permissions.is_admin", return_value=True)
  @patch("about.api.Settings.get_settings")
  def test_get_settings_as_admin_error(self, mock_get_settings, mock_is_admin):
    mock_get_settings.side_effect = ObjectDoesNotExist("Settings not found")
    self.api_client.force_authenticate(user=self.admin_user)

    response = self.api_client.get(self.analytics_settings_url)

    self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    self.assertEqual(response.data, {"error": "A server error occurred while retrieving usage analytics settings."})

  @patch("desktop.auth.api_permissions.is_admin", return_value=True)
  @patch("about.api.Settings.get_settings")
  def test_post_settings_as_admin_success(self, mock_get_settings, mock_is_admin):
    mock_settings = MagicMock()
    mock_get_settings.return_value = mock_settings
    self.api_client.force_authenticate(user=self.admin_user)
    payload = {"collect_usage": False}

    response = self.api_client.post(self.analytics_settings_url, data=payload, format="json")

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertEqual(response.data, payload)
    self.assertEqual(mock_settings.collect_usage, False)
    mock_settings.save.assert_called_once()

  @patch("desktop.auth.api_permissions.is_admin", return_value=False)
  def test_post_settings_as_non_admin_forbidden(self, mock_is_admin):
    self.api_client.force_authenticate(user=self.regular_user)

    response = self.api_client.post(self.analytics_settings_url)

    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    self.assertEqual(response.data, {"detail": "You must be a Hue admin to perform this action."})

  @patch("desktop.auth.api_permissions.is_admin", return_value=True)
  @patch("about.api.Settings.get_settings")
  def test_post_settings_as_admin_error(self, mock_get_settings, mock_is_admin):
    mock_get_settings.side_effect = ObjectDoesNotExist("Settings not found")
    self.api_client.force_authenticate(user=self.admin_user)
    payload = {"collect_usage": False}

    response = self.api_client.post(self.analytics_settings_url, data=payload, format="json")

    self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    self.assertEqual(response.data, {"error": "A server error occurred while saving the usage analytics settings."})

  @patch("desktop.auth.api_permissions.is_admin", return_value=True)
  @patch("about.api.Settings.get_settings")
  def test_post_settings_as_admin_missing_field(self, mock_get_settings, mock_is_admin):
    mock_get_settings.return_value = MagicMock(collect_usage=True)
    self.api_client.force_authenticate(user=self.admin_user)
    payload = {}

    response = self.api_client.post(self.analytics_settings_url, data=payload, format="json")

    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response.data, {"collect_usage": ["This field is required."]})
