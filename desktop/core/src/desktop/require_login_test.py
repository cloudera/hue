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
#
# Test for RequireLoginEverywhereMiddleware in middleware.py
# 
# This test uses "nose"-style testing (no need for a TestCase),
# and nose-style assertions.

from nose.tools import *

from django.test.client import Client
import django


def test_require_login():
  c = Client()
  # We're not logged in, so expect a redirection.

  response = c.get('/profile')
  assert_true(isinstance(response, django.http.HttpResponseRedirect), "Expected redirect")
  assert_equal("/hue/accounts/login?next=/profile", response["Location"])

  # AllowAllBackend should let us in.
  c.login(username="test", password="test")
  # And now we shouldn't need to be redirected.
  response = c.get('/', follow=True)
  assert_equal(200, response.status_code)


def test_ajax_require_login():
  c = Client()
  response = c.get('/profile',
                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
  assert_equal("LOGIN_REQUIRED", response["X-Hue-Middleware-Response"],
               "Expected magic header from middleware")
