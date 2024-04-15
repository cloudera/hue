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
import pytest
import sys
import tempfile

from django.conf import settings
from django.test.client import Client
from django.test import RequestFactory, TestCase
from django.http import HttpResponse
from django.core import exceptions

import desktop.conf

from desktop.middleware import CacheControlMiddleware, MultipleProxyMiddleware
from desktop.conf import AUDIT_EVENT_LOG_DIR, CUSTOM_CACHE_CONTROL
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_permission

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock

@pytest.mark.django_db
def test_view_perms():
  # Super user
  c = make_logged_in_client()

  response = c.get("/useradmin/")
  assert 200 == response.status_code

  response = c.get("/useradmin/users/edit/test")
  assert 200 == response.status_code

  # Normal user
  c = make_logged_in_client('user', is_superuser=False)
  add_permission('user', 'test-view-group', 'access_view:useradmin:edit_user', 'useradmin')

  response = c.get("/useradmin/")
  assert 401 == response.status_code

  response = c.get("/useradmin/users/edit/test")
  assert 401 == response.status_code

  response = c.get("/useradmin/users/edit/user") # Can access his profile page
  assert 200 == response.status_code, response.content


@pytest.mark.django_db
def test_ensure_safe_method_middleware():
  try:
    # Super user
    c = make_logged_in_client()

    # GET works
    response = c.get("/useradmin/")
    assert 200 == response.status_code

    # Disallow GET
    done = desktop.conf.HTTP_ALLOWED_METHODS.set_for_testing([])

    # GET should not work because allowed methods is empty.
    response = c.get("/useradmin/")
    assert 405 == response.status_code
  finally:
    done()


@pytest.mark.django_db
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
      assert 'audited' in response, response

      audit = open(log_path).readlines()
      for line in audit:
        audit_json = json.loads(line)
        audit_record = list(audit_json.values())[0]
        assert 'test_audit_logging' == audit_record['user'], audit_record
        assert '/useradmin/permissions/edit/beeswax/access' == audit_record['url'], audit_record

    finally:
      settings.MIDDLEWARE.pop()
      reset()

@pytest.mark.django_db
def test_audit_logging_middleware_disable():
  c = make_logged_in_client(username='test_audit_logging', is_superuser=False)

  reset = AUDIT_EVENT_LOG_DIR.set_for_testing('')
  try:
    # No middleware yet
    response = c.get("/oozie/")
    assert not 'audited' in response, response
  finally:
    reset()


def test_ensure_safe_redirect_middleware():
  pytest.skip("Skipping Test")
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
    assert 302 == response.status_code

    # Disallow most redirects
    done.append(desktop.conf.REDIRECT_WHITELIST.set_for_testing('^\d+$'))
    response = c.post("/hue/accounts/login/", {
      'username': 'test',
      'password': 'test',
      'next': 'http://example.com',
    })
    assert 403 == response.status_code

    # Allow all redirects
    done.append(desktop.conf.REDIRECT_WHITELIST.set_for_testing('.*'))
    response = c.post("/hue/accounts/login/", {
      'username': 'test',
      'password': 'test',
      'next': 'http://example.com',
    })
    assert 302 == response.status_code

    # Allow all redirects and disallow most at the same time.
    # should have a logic OR functionality.
    done.append(desktop.conf.REDIRECT_WHITELIST.set_for_testing('\d+,.*'))
    response = c.post("", {
      'username': 'test',
      'password': 'test',
      'next': 'http://example.com',
    })
    assert 302 == response.status_code
  finally:
    settings.MIDDLEWARE.pop()
    for finish in done:
      finish()

@pytest.mark.django_db
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
      assert 200 == response.status_code
      assert response['WWW-Authenticate'] == 'Negotiate %s' % authGSSServerResponse.return_value

    c = Client()
    response = c.get("/hue/editor/?type=impala")
    assert 401 == response.status_code

    c = Client()
    response = c.get("/desktop/debug/is_alive")
    assert 200 == response.status_code
  finally:
    settings.MIDDLEWARE.pop()
    for finish in done:
      finish()
    settings.AUTHENTICATION_BACKENDS = orig_backends

def test_cache_control_middleware():
  c = Client()
  request = c.get("/")

  def dummy_get_response(request):
    return HttpResponse()

  reset = CUSTOM_CACHE_CONTROL.set_for_testing(True)
  try:
    middleware = CacheControlMiddleware(dummy_get_response)
    response = middleware(request)
    assert response['Cache-Control'] == 'no-cache, no-store, must-revalidate'
    assert response['Pragma'] == 'no-cache'
    assert response['Expires'] == '0'
  finally:
    reset()

  reset = CUSTOM_CACHE_CONTROL.set_for_testing(False)
  try:
    middleware = CacheControlMiddleware(dummy_get_response)
    response = middleware(request)
    assert 'Cache-Control' not in response
    assert 'Pragma' not in response
    assert 'Expires' not in response
  except exceptions.MiddlewareNotUsed:
    response = dummy_get_response(request)
  finally:
    reset()

def get_response(request):
  return request

@pytest.mark.django_db
class TestMultipleProxyMiddleware(TestCase):

  def setup_method(self, method):
    self.factory = RequestFactory()
    self.middleware = MultipleProxyMiddleware(get_response)

  def test_multiple_proxy_middleware(self):
    request = self.factory.get('/')
    request.META['HTTP_X_FORWARDED_FOR'] = '192.0.2.0, 192.0.2.1, 192.0.2.2'
    request.META['HTTP_X_REAL_IP'] = '192.0.2.1'
    self.middleware(request)
    assert request.META['HTTP_X_FORWARDED_FOR'] == '192.0.2.1'

  def test_multiple_proxy_middleware_without_x_real_ip(self):
    request = self.factory.get('/')
    request.META['HTTP_X_FORWARDED_FOR'] = '192.0.2.0, 192.0.2.1, 192.0.2.2'
    self.middleware(request)
    assert request.META['HTTP_X_FORWARDED_FOR'] == '192.0.2.2'

  def test_multiple_proxy_middleware_without_x_forwarded_for(self):
    request = self.factory.get('/')
    request.META['REMOTE_ADDR'] = '192.0.2.0'
    self.middleware(request)
    assert request.META['HTTP_X_FORWARDED_FOR'] == '192.0.2.0'

