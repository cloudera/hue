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
from desktop.lib import django_mako

from nose.tools import assert_true, assert_equal
from desktop.lib.django_test_util import make_logged_in_client
from django.conf.urls.defaults import patterns, url
from django.http import HttpResponse
from django.db.models import query, CharField, SmallIntegerField
from desktop.lib.paginator import Paginator
import desktop
import desktop.urls
import desktop.conf
import logging
import time
from desktop.lib.django_util import TruncatingModel
import desktop.views as views

def setup_test_environment():
  """
  Sets up mako to signal template rendering.
  """
  django_mako.render_to_string = django_mako.render_to_string_test
setup_test_environment.__test__ = False

def teardown_test_environment():
  """
  This method is called by nose_runner when
  the tests all finish.  This helps track
  down when tests aren't cleaning up after
  themselves and leaving threads hanging around.
  """
  import threading
  # We should shut down all relevant threads by test completion.
  threads = list(threading.enumerate())

  try:
    import threadframe
    import traceback
    if len(threads) > 1:
      for v in threadframe.dict().values():
        traceback.print_stack(v)
  finally:
    # threadframe is only available in the dev build.
    pass

  assert 1 == len(threads), threads

  django_mako.render_to_string = django_mako.render_to_string_normal
teardown_test_environment.__test__ = False

def test_dump_config():
  c = make_logged_in_client()

  CANARY = "abracadabra"
  clear = desktop.conf.HTTP_HOST.set_for_testing(CANARY)

  response1 = c.get('/dump_config')
  assert_true(CANARY in response1.content)

  response2 = c.get('/dump_config', dict(private="true"))
  assert_true(CANARY in response2.content)

  # There are more private variables...
  assert_true(len(response1.content) < len(response2.content))

  clear()

def test_prefs():
  c = make_logged_in_client()

  # Get everything
  response = c.get('/prefs/')
  assert_equal('{}', response.content)

  # Set and get
  response = c.get('/prefs/foo', dict(set="bar"))
  assert_equal('true', response.content)
  response = c.get('/prefs/foo')
  assert_equal('"bar"', response.content)

  # Reset (use post this time)
  c.post('/prefs/foo', dict(set="baz"))
  response = c.get('/prefs/foo')
  assert_equal('"baz"', response.content)

  # Check multiple values
  c.post('/prefs/elephant', dict(set="room"))
  response = c.get('/prefs/')
  assert_true("baz" in response.content)
  assert_true("room" in response.content)

  # Delete everything
  c.get('/prefs/elephant', dict(delete=""))
  c.get('/prefs/foo', dict(delete=""))
  response = c.get('/prefs/')
  assert_equal('{}', response.content)

  # Check non-existent value
  response = c.get('/prefs/doesNotExist')
  assert_equal('null', response.content)

def test_status_bar():
  """
  Subs out the status_bar_views registry with temporary examples.
  Tests handling of errors on view functions.
  """
  backup = views._status_bar_views
  views._status_bar_views = []

  c = make_logged_in_client()
  views.register_status_bar_view(lambda _: HttpResponse("foo", status=200))
  views.register_status_bar_view(lambda _: HttpResponse("bar"))
  views.register_status_bar_view(lambda _: None)
  def f(r):
    raise Exception()
  views.register_status_bar_view(f)

  response = c.get("/status_bar")
  assert_equal("foobar", response.content)

  views._status_bar_views = backup


def test_paginator():
  """
  Test that the paginator works with partial list.
  """
  def assert_page(page, data, start, end):
    assert_equal(page.object_list, data)
    assert_equal(page.start_index(), start)
    assert_equal(page.end_index(), end)

  # First page 1-20
  obj = range(20)
  pgn = Paginator(obj, per_page=20, total=25)
  assert_page(pgn.page(1), obj, 1, 20)

  # Second page 21-25
  obj = range(5)
  pgn = Paginator(obj, per_page=20, total=25)
  assert_page(pgn.page(2), obj, 21, 25)

  # Handle extra data on first page (22 items on a 20-page)
  obj = range(22)
  pgn = Paginator(obj, per_page=20, total=25)
  assert_page(pgn.page(1), range(20), 1, 20)

  # Handle extra data on second page (22 items on a 20-page)
  obj = range(22)
  pgn = Paginator(obj, per_page=20, total=25)
  assert_page(pgn.page(2), range(5), 21, 25)

  # Handle total < len(obj). Only works for QuerySet.
  obj = query.QuerySet()
  obj._result_cache = range(10)
  pgn = Paginator(obj, per_page=10, total=9)
  assert_page(pgn.page(1), range(10), 1, 10)

  # Still works with a normal complete list
  obj = range(25)
  pgn = Paginator(obj, per_page=20)
  assert_page(pgn.page(1), range(20), 1, 20)
  assert_page(pgn.page(2), range(20, 25), 21, 25)

def test_thread_dump():
  c = make_logged_in_client()
  response = c.get("/debug/threads")
  assert_true("test_thread_dump" in response.content)

def test_truncating_model():
  class TinyModel(TruncatingModel):
    short_field = CharField(max_length=10)
    non_string_field = SmallIntegerField()

  a = TinyModel()

  a.short_field = 'a' * 9 # One less than it's max length
  assert_true(a.short_field == 'a' * 9, 'Short-enough field does not get truncated')

  a.short_field = 'a' * 11 # One more than it's max_length
  assert_true(a.short_field == 'a' * 10, 'Too-long field gets truncated')

  a.non_string_field = 10**10
  assert_true(a.non_string_field == 10**10, 'non-string fields are not truncated')


def test_500_handling():
  restore_django_debug = desktop.conf.DJANGO_DEBUG_MODE.set_for_testing(False)
  restore_500_debug = desktop.conf.HTTP_500_DEBUG_MODE.set_for_testing(False)

  exc_msg = "error_raising_view: Test 500 handling"
  def error_raising_view(request, *args, **kwargs):
    raise Exception(exc_msg)

  # Add an error view
  error_url_pat = patterns('', url('^500_internal_error$', error_raising_view))[0]
  desktop.urls.urlpatterns.append(error_url_pat)
  try:
    def store_exc_info(*args, **kwargs):
      pass
    # Disable the test client's exception forwarding
    c = make_logged_in_client()
    c.store_exc_info = store_exc_info

    response = c.get('/500_internal_error')
    assert_equal(response.template.name, '500.html')
    assert_true('should be fixed shortly. Thanks for your patience' in response.content)
    assert_true(exc_msg not in response.content)

    # Now test the 500 handler with backtrace
    desktop.conf.HTTP_500_DEBUG_MODE.set_for_testing(True)
    response = c.get('/500_internal_error')
    assert_equal(response.template.name, 'Technical 500 template')
    assert_true(exc_msg in response.content)
  finally:
    # Restore the world
    desktop.urls.urlpatterns.remove(error_url_pat)
    restore_django_debug()
    restore_500_debug()


def test_404_handling():
  view_name = '/the-view-that-is-not-there'
  c = make_logged_in_client()
  response = c.get(view_name)
  assert_equal(response.template.name, '404.html')
  assert_true('Page Not Found' in response.content)
  assert_true(view_name in response.content)

class RecordingHandler(logging.Handler):
  def __init__(self, *args, **kwargs):
    logging.Handler.__init__(self, *args, **kwargs)
    self.records = []

  def emit(self, r):
    self.records.append(r)

def test_log_event():
  c = make_logged_in_client()
  root = logging.getLogger("desktop.views.log_frontend_event")
  handler = RecordingHandler()
  root.addHandler(handler)

  c.get("/log_frontend_event?level=info&message=foo")
  assert_equal("INFO", handler.records[-1].levelname)
  assert_equal("Untrusted log event from user test: foo", handler.records[-1].message)
  assert_equal("desktop.views.log_frontend_event", handler.records[-1].name)

  c.get("/log_frontend_event?level=error&message=foo2")
  assert_equal("ERROR", handler.records[-1].levelname)
  assert_equal("Untrusted log event from user test: foo2", handler.records[-1].message)

  c.get("/log_frontend_event?message=foo3")
  assert_equal("INFO", handler.records[-1].levelname)
  assert_equal("Untrusted log event from user test: foo3", handler.records[-1].message)

  c.post("/log_frontend_event", {
    "message": "01234567" * 1024})
  assert_equal("INFO", handler.records[-1].levelname)
  assert_equal("Untrusted log event from user test: " + "01234567"*(1024/8), 
    handler.records[-1].message)

  root.removeHandler(handler)


def test_config_check():
  reset = (
    desktop.conf.SECRET_KEY.set_for_testing(''),
    desktop.conf.SSL_CERTIFICATE.set_for_testing('foobar'),
    desktop.conf.SSL_PRIVATE_KEY.set_for_testing(''),
    desktop.conf.DEFAULT_SITE_ENCODING.set_for_testing('klingon')
  )

  try:
    cli = make_logged_in_client()
    resp = cli.get('/debug/check_config')
    assert_true('Secret key should be configured' in resp.content)
    assert_true('desktop.ssl_certificate' in resp.content)
    assert_true('Path does not exist' in resp.content)
    assert_true('SSL private key file should be set' in resp.content)
    assert_true('klingon' in resp.content)
    assert_true('Encoding not supported' in resp.content)

    # Alert present in the status bar
    resp = cli.get('/status_bar/')
    assert_true('Misconfiguration' in resp.content)
  finally:
    for old_conf in reset:
      old_conf()


def test_last_access_time():
  c = make_logged_in_client(username="access_test")
  c.post('/accounts/login_ajax')
  login = desktop.auth.views.get_current_users()
  before_access_time = time.time()
  response = c.post('/status_bar')
  after_access_time = time.time()
  access = desktop.auth.views.get_current_users()

  user = response.context['user']
  login_time = login[user]['time']
  access_time = access[user]['time']

  # Check that 'last_access_time' is later than login time
  assert_true(login_time < access_time)
  # Check that 'last_access_time' is in between the timestamps before and after the last access path
  assert_true(before_access_time < access_time)
  assert_true(access_time < after_access_time)
