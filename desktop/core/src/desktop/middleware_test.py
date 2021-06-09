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

import json
import os
import sys
import tempfile

from django.conf import settings
from django.test.client import Client
from nose.tools import assert_equal, assert_false, assert_true
from nose.plugins.skip import SkipTest

import desktop.conf

from desktop.conf import AUDIT_EVENT_LOG_DIR
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_permission

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock

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


def test_audit_logging_middleware_enable():
  c = make_logged_in_client(username='test_audit_logging', is_superuser=False)

  # Make sure we enable it with a file path
  with tempfile.NamedTemporaryFile("w+t") as log_tmp:
    log_path = log_tmp.name
    reset = AUDIT_EVENT_LOG_DIR.set_for_testing(log_path)
    settings.MIDDLEWARE.append('desktop.middleware.AuditLoggingMiddleware') # Re-add middleware

    try:
      # Check if we audit correctly
      response = c.get("/useradmin/permissions/edit/beeswax/access")
      assert_true('audited' in response, response)

      audit = open(log_path).readlines()
      for line in audit:
        audit_json = json.loads(line)
        audit_record = list(audit_json.values())[0]
        assert_equal('test_audit_logging', audit_record['user'], audit_record)
        assert_equal('/useradmin/permissions/edit/beeswax/access', audit_record['url'], audit_record)

    finally:
      settings.MIDDLEWARE.pop()
      reset()

def test_audit_logging_middleware_disable():
  c = make_logged_in_client(username='test_audit_logging', is_superuser=False)

  reset = AUDIT_EVENT_LOG_DIR.set_for_testing('')
  try:
    # No middleware yet
    response = c.get("/oozie/")
    assert_false('audited' in response, response)
  finally:
    reset()


def test_ensure_safe_redirect_middleware():
  raise SkipTest
  done = []
  settings.MIDDLEWARE.append('desktop.middleware.EnsureSafeRedirectURLMiddleware')
  try:
    # Super user
    c = make_logged_in_client()

    # POST works
    response = c.post("/hue/accounts/login/", {
      'username': 'test',
      'password': 'test',
    })
    assert_equal(302, response.status_code)

    # Disallow most redirects
    done.append(desktop.conf.REDIRECT_WHITELIST.set_for_testing('^\d+$'))
    response = c.post("/hue/accounts/login/", {
      'username': 'test',
      'password': 'test',
      'next': 'http://example.com',
    })
    assert_equal(403, response.status_code)

    # Allow all redirects
    done.append(desktop.conf.REDIRECT_WHITELIST.set_for_testing('.*'))
    response = c.post("/hue/accounts/login/", {
      'username': 'test',
      'password': 'test',
      'next': 'http://example.com',
    })
    assert_equal(302, response.status_code)

    # Allow all redirects and disallow most at the same time.
    # should have a logic OR functionality.
    done.append(desktop.conf.REDIRECT_WHITELIST.set_for_testing('\d+,.*'))
    response = c.post("", {
      'username': 'test',
      'password': 'test',
      'next': 'http://example.com',
    })
    assert_equal(302, response.status_code)
  finally:
    settings.MIDDLEWARE.pop()
    for finish in done:
      finish()

def test_spnego_middleware():
  done = []
  orig_backends = settings.AUTHENTICATION_BACKENDS
  try:
    # use SpnegoDjangoBackend to enable 'desktop.middleware.SpnegoMiddleware'
    done.append(desktop.conf.AUTH.BACKEND.set_for_testing(['desktop.auth.backend.SpnegoDjangoBackend']))
    settings.AUTHENTICATION_BACKENDS = (['desktop.auth.backend.SpnegoDjangoBackend'])

    c = Client()
    with patch('kerberos.authGSSServerInit') as authGSSServerInit, \
         patch('kerberos.authGSSServerStep') as authGSSServerStep, \
         patch('kerberos.authGSSServerResponse') as authGSSServerResponse, \
         patch('kerberos.authGSSServerClean') as authGSSServerClean, \
         patch('kerberos.authGSSServerUserName') as authGSSServerUserName:
      authGSSServerInit.return_value = 1, 'context'
      authGSSServerStep.return_value = 1
      authGSSServerResponse.return_value = 'gssstring'
      authGSSServerClean.return_value = None
      authGSSServerUserName.return_value = 'spnego_test'

      header = {'HTTP_AUTHORIZATION': 'Negotiate test'}
      response = c.get("/hue/editor/?type=impala", **header)
      assert_equal(200, response.status_code)
      assert_equal(response['WWW-Authenticate'], 'Negotiate %s' % authGSSServerResponse.return_value)

    c = Client()
    response = c.get("/hue/editor/?type=impala")
    assert_equal(401, response.status_code)

    c = Client()
    response = c.get("/desktop/debug/is_alive")
    assert_equal(200, response.status_code)
  finally:
    settings.MIDDLEWARE.pop()
    for finish in done:
      finish()
    settings.AUTHENTICATION_BACKENDS = orig_backends

