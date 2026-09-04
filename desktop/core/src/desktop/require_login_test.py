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

# Test for RequireLoginEverywhereMiddleware in middleware.py


import sys
from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

import django
import pytest
from django.test.client import Client


@pytest.mark.django_db
def test_require_login():
  c = Client()
  # We're not logged in, so expect a redirection.

  response = c.get('/profile')
  assert isinstance(response, django.http.HttpResponseRedirect), "Expected redirect"
  assert "/hue/accounts/login?next=/profile" == response["Location"]

  # AllowAllBackend should let us in.
  c.login(request=Mock(), username="test", password="test")
  # And now we shouldn't need to be redirected.
  response = c.get('/', follow=True)
  assert 200 == response.status_code


def test_require_login_preserves_ofs_route_delimiter():
  c = Client()
  response = c.get('/hue/filebrowser/view=ofs%3A%2F%2Fom%2Fhuevol%2Fhuebucket%2Fhue-demo.txt')

  assert 302 == response.status_code
  next_url = parse_qs(urlparse(response['Location']).query)['next'][0]
  assert '/hue/filebrowser/view=ofs://om/huevol/huebucket/hue-demo.txt' == next_url


def test_require_login_does_not_duplicate_hue_prefix_for_embeddable_route():
  c = Client()
  response = c.get('/hue/filebrowser/view=ofs%3A%2F%2Fom%2Fhuevol%2Fhuebucket%2Fhue-demo.txt?is_embeddable=true')

  assert 200 == response.status_code
  next_url = parse_qs(urlparse(response.json()['url']).query)['next'][0]
  assert '/hue/filebrowser/view=ofs://om/huevol/huebucket/hue-demo.txt?' == next_url


def test_require_login_preserves_encoded_query_string():
  c = Client()
  response = c.get('/profile?search=a%26b')

  assert 302 == response.status_code
  next_url = parse_qs(urlparse(response['Location']).query)['next'][0]
  assert '/profile?search=a%26b' == next_url


def test_ajax_require_login():
  c = Client()
  response = c.get('/profile',
                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
  assert "LOGIN_REQUIRED" == response["X-Hue-Middleware-Response"], "Expected magic header from middleware"
