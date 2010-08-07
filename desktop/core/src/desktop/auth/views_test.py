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

from nose.tools import assert_true, assert_false, assert_equal

from django.contrib.auth.models import User
from django.test.client import Client
from desktop.lib.django_test_util import make_logged_in_client

def test_jframe_login():
  # Simulate first login ever
  for user in User.objects.all():
    user.delete()

  c = Client()

  response = c.get('/accounts/login_form')
  assert_equal(200, response.status_code, "Expected ok status.")
  assert_true(response.context['first_login_ever'])

  response = c.post('/accounts/login_ajax',
                    dict(username="foo",
                         password="foo"))
  assert_equal(200, response.status_code, "Expected ok status.")

  response = c.get('/accounts/login_form')
  assert_equal(200, response.status_code, "Expected ok status.")
  assert_false(response.context['first_login_ever'])


def test_non_jframe_login():
  client = make_logged_in_client(username="test", password="test")
  # Logout first
  client.get('/accounts/logout')
  # Login
  response = client.post('/accounts/login/', dict(username="test", password="test"), follow=True)
  assert_equal(response.template, 'index.mako')
