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

"""
Checks that the login lockout configured in settings.py works with the installed django-axes.

Hue maps its [[auth]] lockout options to django-axes settings, whose names changed between releases, so a
mismatch would silently turn the lockout off or make it count every user behind a proxy as one client.
"""

import pytest
from django.conf import settings
from django.urls import reverse

from desktop.lib.django_test_util import Client
from useradmin.models import User

FAILURE_LIMIT = 3
FORWARDED_FOR_HEADER = "HTTP_X_FORWARDED_FOR"


@pytest.mark.django_db
class TestLoginLockout:
  @pytest.fixture(autouse=True)
  def lockout_enabled(self, settings):
    settings.AXES_ENABLED = True
    settings.AXES_LOCK_OUT_AT_FAILURE = True
    settings.AXES_FAILURE_LIMIT = FAILURE_LIMIT

  def setup_method(self):
    self.username = "lockout_user"
    self.password = "correct-password"
    User.objects.create_user(username=self.username, password=self.password)
    self.client = Client()

  def _login(self, password, **extra):
    return self.client.post(reverse("desktop_auth_views_dt_login"), {"username": self.username, "password": password}, **extra)

  def _lock_out(self, **extra):
    # A failed login can count as more than one failure, so keep failing until the limit is certainly reached.
    for _ in range(FAILURE_LIMIT):
      self._login("wrong-password", **extra)

  def test_lockout_parameters_are_configured_as_a_list_of_parameters(self):
    assert isinstance(settings.AXES_LOCKOUT_PARAMETERS, list)
    assert all(isinstance(parameters, list) for parameters in settings.AXES_LOCKOUT_PARAMETERS)
    assert "ip_address" in settings.AXES_LOCKOUT_PARAMETERS[0]

  def test_login_works_without_failed_attempts(self):
    response = self._login(self.password)

    assert response.status_code == 302
    assert "_auth_user_id" in self.client.session

  def test_account_is_locked_after_repeated_failed_logins(self):
    self._lock_out()

    response = self._login(self.password)

    assert response.status_code == 429
    assert "_auth_user_id" not in self.client.session

  def test_lockout_is_counted_per_client_ip_when_behind_a_reverse_proxy(self, settings):
    settings.AXES_IPWARE_META_PRECEDENCE_ORDER = (FORWARDED_FOR_HEADER,)
    self._lock_out(**{FORWARDED_FOR_HEADER: "10.0.0.1"})

    locked_out = self._login(self.password, **{FORWARDED_FOR_HEADER: "10.0.0.1"})
    other_client = self._login(self.password, **{FORWARDED_FOR_HEADER: "10.0.0.2"})

    assert locked_out.status_code == 429
    assert other_client.status_code == 302
