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

from builtins import object
import json
import pytest

from django.urls import reverse
from django.test import TestCase

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import Settings
from oozie.tests import OozieBase
from useradmin.models import User


@pytest.mark.django_db
class TestAboutBase(object):
  def setup_method(self):
    self.client = make_logged_in_client(username="about", is_superuser=False)
    grant_access("about", "about", "about")

    self.client_admin = make_logged_in_client(username="about_admin", is_superuser=True)
    grant_access("about_admin", "about_admin", "about")


@pytest.mark.integration
class TestAbout(TestAboutBase, OozieBase):

  def test_admin_wizard_permissions(self):
    response = self.client_admin.get(reverse('about:index'))
    assert 'Step 1: <i class="fa fa-check"></i> Checks' in response.content, response.content

    response = self.client.get(reverse('about:index'))
    assert not 'Step 1: <i class="fa fa-check"></i> Checks' in response.content, response.content


class TestAboutWithNoCluster(TestAboutBase):

  def test_dump_config(self):
    # Exception raised if bad unicode
    self.client_admin.get(reverse('about:index'), HTTP_ACCEPT_LANGUAGE='fr-fr')

  def test_collect_usage(self):
    collect_usage = Settings.get_settings().collect_usage

    try:
      response = self.client_admin.post(reverse('about:update_preferences'), {'collect_usage': False})
      data = json.loads(response.content)
      assert data['status'] == 0
      assert not data['collect_usage']

      response = self.client_admin.post(reverse('about:update_preferences'), {'collect_usage': True})
      data = json.loads(response.content)
      assert data['status'] == 0
      assert data['collect_usage']
    finally:
      settings = Settings.get_settings()
      settings.collect_usage = collect_usage
      settings.save()
