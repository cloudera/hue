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

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_permission
from django.conf import settings
import desktop.conf

from nose.tools import assert_equal


def test_jframe_middleware():
  c = make_logged_in_client()
  path = "/about/?foo=bar&baz=3"
  response = c.get(path)
  assert_equal(path, response["X-Hue-JFrame-Path"])

  path_nocache = "/about/?noCache=blabla&foo=bar&baz=3"
  response = c.get(path_nocache)
  assert_equal(path, response["X-Hue-JFrame-Path"])

  path_nocache = "/about/?noCache=blabla&foo=bar&noCache=twiceover&baz=3"
  response = c.get(path_nocache)
  assert_equal(path, response["X-Hue-JFrame-Path"])

  path = "/about/"
  response = c.get(path)
  assert_equal(path, response["X-Hue-JFrame-Path"])

  response = c.get("/about/?")
  assert_equal("/about/", response["X-Hue-JFrame-Path"])


def test_view_perms():
  # Super user
  c = make_logged_in_client()

  response = c.get("/useradmin/")
  assert_equal(200, response.status_code)

  response = c.get("/useradmin/users/edit/test")
  assert_equal(200, response.status_code)

  # Normal user
  c = make_logged_in_client('user', is_superuser=False)
  add_permission('user', 'test-view-group', 'access_view:useradmin:edit_user', 'useradmin')

  response = c.get("/useradmin/")
  assert_equal(401, response.status_code)

  response = c.get("/useradmin/users/edit/test")
  assert_equal(401, response.status_code)

  response = c.get("/useradmin/users/edit/user") # Can access his profile page
  assert_equal(200, response.status_code, response.content)


def test_ensure_safe_method_middleware():
  try:
    # Super user
    c = make_logged_in_client()

    # GET works
    response = c.get("/useradmin/")
    assert_equal(200, response.status_code)

    # Disallow GET
    done = desktop.conf.HTTP_ALLOWED_METHODS.set_for_testing([])

    # GET should not work because allowed methods is empty.
    response = c.get("/useradmin/")
    assert_equal(405, response.status_code)
  finally:
    done()


def test_ensure_safe_redirect_middleware():
  done = []
  settings.MIDDLEWARE_CLASSES.append('desktop.middleware.EnsureSafeRedirectURLMiddleware')
  try:
    # Super user
    c = make_logged_in_client()

    # GET works
    response = c.get("/useradmin/")
    assert_equal(200, response.status_code)

    # Disallow most redirects
    done.append(desktop.conf.REDIRECT_WHITELIST.set_for_testing('^\d+$'))
    response = c.get("")
    assert_equal(403, response.status_code)

    # Allow all redirects
    done.append(desktop.conf.REDIRECT_WHITELIST.set_for_testing('.*'))
    response = c.get("")
    assert_equal(302, response.status_code)

    # Allow all redirects and disallow most at the same time.
    # should have a logic OR functionality.
    done.append(desktop.conf.REDIRECT_WHITELIST.set_for_testing('\d+,.*'))
    response = c.get("")
    assert_equal(302, response.status_code)
  finally:
    settings.MIDDLEWARE_CLASSES.pop()
    for finish in done:
      finish()
