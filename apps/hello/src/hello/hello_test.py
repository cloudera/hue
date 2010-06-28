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
# Functional test for hello app.
#
# This test uses "nose"-style testing (no need for a TestCase),
# and nose-style assertions.  It uses the Django client to
# go through most of the stack.
#
# You can use nose.tools.set_trace() to set a breakpoint while
# developing the test.

import simplejson
from nose.tools import *

from desktop.lib.django_test_util import make_logged_in_client

def test_require_login():
  c = make_logged_in_client()
  # All apps require login.
  c.login(username="test", password="test")

  # Test basic output.
  response = c.get('/hello/')
  assert_true("Bonjour" in response.content)

  # Or like so.
  assert_equal("Bonjour", c.get('/hello/').context["greeting"])

  # Test JSON too
  response = c.get('/hello/', dict(format="json"))
  assert_equal(dict(greeting="Bonjour"), simplejson.JSONDecoder().decode(response.content))

  # Can also do this:
  assert_equal(dict(greeting="Bonjour"), c.get_json('/hello/', dict(format="json")))

