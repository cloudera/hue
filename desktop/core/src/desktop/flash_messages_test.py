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
# Tests for the flash messaging support

from desktop.middleware import FlashMessenger
from desktop.lib.django_test_util import make_logged_in_client

from nose.tools import assert_true, assert_equal
import simplejson
import UserDict

class MockRequest(object):
  def __init__(self):
    self.session = UserDict.UserDict()

def minimal_flow_test():
  r = MockRequest()
  m = FlashMessenger(r)
  output = m.get()
  assert_true(len(output) == 0)

def message_test():
  r = MockRequest()
  m = FlashMessenger(r)
  m.put("Hi")
  m.put("Bye")
  assert_equal(2, len(r.session["flashMessages"]))
  assert_equal(True, r.session.modified)
  output = m.get()
  assert_equal(None, r.session.get("flashMessages"))
  assert_equal(["Hi", "Bye"], output)
  
def cross_request_flash_messages_test():
  c = make_logged_in_client()
  assert_equal(None, c.session.get('flashMessages'))
  c.get('/jframegallery/gallery/flash.html')
  assert_equal(3, len(c.session['flashMessages']))
  response = c.get('/jframegallery/', dict(format="embed"))
  assert_equal(3, len(simplejson.loads(response["X-Hue-Flash-Messages"])))
  assert_equal(None, c.session.get('flashMessages'))
  response = c.get('/jframegallery/', dict(format="embed"))
  assert_equal(None, response.get("X-Hue-Flash-Messages", None))
  
def missing_slash_test():
  c = make_logged_in_client()
  response = c.get('/accounts/logout')
  assert_equal(301, response.status_code) # redirect
