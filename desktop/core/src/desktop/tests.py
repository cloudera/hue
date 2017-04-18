#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import logging
import os
import StringIO
import subprocess
import sys
import time

import proxy.conf
import tempfile

from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal, assert_raises, nottest
from django.conf.urls import patterns, url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.db.models import query, CharField, SmallIntegerField

from settings import HUE_DESKTOP_VERSION

from beeswax.conf import HIVE_SERVER_HOST
from pig.models import PigScript
from useradmin.models import GroupPermission

import desktop
import desktop.conf
import desktop.urls
import desktop.redaction as redaction
import desktop.views as views

from desktop.appmanager import DESKTOP_APPS
from desktop.lib import django_mako
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.paginator import Paginator
from desktop.lib.conf import validate_path
from desktop.lib.django_util import TruncatingModel
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.test_utils import grant_access
from desktop.models import Directory, Document, Document2, get_data_link, _version_from_properties, HUE_VERSION
from desktop.redaction import logfilter
from desktop.redaction.engine import RedactionPolicy, RedactionRule
from desktop.views import check_config, home


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
  import desktop.lib.thread_util

  # We should shut down all relevant threads by test completion.
  threads = list(threading.enumerate())

  if len(threads) > 1:
    desktop.lib.thread_util.dump_traceback()

  assert 1 == len(threads), threads

  django_mako.render_to_string = django_mako.render_to_string_normal
teardown_test_environment.__test__ = False


def test_home():
  c = make_logged_in_client(username="test_home", groupname="test_home", recreate=True, is_superuser=False)
  user = User.objects.get(username="test_home")

  response = c.get(reverse(home))
  assert_equal(["notmine", "trash", "mine", "history"], json.loads(response.context['json_tags']).keys())
  assert_equal(200, response.status_code)

  script, created = PigScript.objects.get_or_create(owner=user)
  doc = Document.objects.link(script, owner=script.owner, name='test_home')

  response = c.get(reverse(home))
  assert_true(str(doc.id) in json.loads(response.context['json_documents']))

  response = c.get(reverse(home))
  tags = json.loads(response.context['json_tags'])
  assert_equal([doc.id], tags['mine'][0]['docs'], tags)
  assert_equal([], tags['trash']['docs'], tags)
  assert_equal([], tags['history']['docs'], tags)

  doc.send_to_trash()

  response = c.get(reverse(home))
  tags = json.loads(response.context['json_tags'])
  assert_equal([], tags['mine'][0]['docs'], tags)
  assert_equal([doc.id], tags['trash']['docs'], tags)
  assert_equal([], tags['history']['docs'], tags)

  doc.restore_from_trash()

  response = c.get(reverse(home))
  tags = json.loads(response.context['json_tags'])
  assert_equal([doc.id], tags['mine'][0]['docs'], tags)
  assert_equal([], tags['trash']['docs'], tags)
  assert_equal([], tags['history']['docs'], tags)

  doc.add_to_history()

  response = c.get(reverse(home))
  tags = json.loads(response.context['json_tags'])
  assert_equal([], tags['mine'][0]['docs'], tags)
  assert_equal([], tags['trash']['docs'], tags)
  assert_equal([], tags['history']['docs'], tags) # We currently don't fetch [doc.id]

def test_skip_wizard():
  c = make_logged_in_client() # is_superuser

  response = c.get('/', follow=True)
  assert_true(['admin_wizard.mako' in _template.filename for _template in response.templates], [_template.filename for _template in response.templates])

  c.cookies['hueLandingPage'] = 'home'
  response = c.get('/', follow=True)
  assert_true(['home.mako' in _template.filename for _template in response.templates], [_template.filename for _template in response.templates])

  c.cookies['hueLandingPage'] = ''
  response = c.get('/', follow=True)
  assert_true(['admin_wizard.mako' in _template.filename for _template in response.templates], [_template.filename for _template in response.templates])


  c = make_logged_in_client(username="test_skip_wizard", password="test_skip_wizard", is_superuser=False)

  response = c.get('/', follow=True)
  assert_true(['home.mako' in _template.filename for _template in response.templates], [_template.filename for _template in response.templates])

  c.cookies['hueLandingPage'] = 'home'
  response = c.get('/', follow=True)
  assert_true(['home.mako' in _template.filename for _template in response.templates], [_template.filename for _template in response.templates])

  c.cookies['hueLandingPage'] = ''
  response = c.get('/', follow=True)
  assert_true(['home.mako' in _template.filename for _template in response.templates], [_template.filename for _template in response.templates])

def test_log_view():
  c = make_logged_in_client()

  URL = reverse(views.log_view)

  LOG = logging.getLogger(__name__)
  LOG.warn('une voix m’a réveillé')

  # UnicodeDecodeError: 'ascii' codec can't decode byte... should not happen
  response = c.get(URL)
  assert_equal(200, response.status_code)

  c = make_logged_in_client()

  URL = reverse(views.log_view)

  LOG = logging.getLogger(__name__)
  LOG.warn('Got response: PK\x03\x04\n\x00\x00\x08\x00\x00\xad\x0cN?\x00\x00\x00\x00')

  # DjangoUnicodeDecodeError: 'utf8' codec can't decode byte 0xad in position 75: invalid start byte... should not happen
  response = c.get(URL)
  assert_equal(200, response.status_code)

def test_download_log_view():
  c = make_logged_in_client()

  URL = reverse(views.download_log_view)

  LOG = logging.getLogger(__name__)
  LOG.warn(u'une voix m’a réveillé')

  # UnicodeDecodeError: 'ascii' codec can't decode byte... should not happen
  response = c.get(URL)
  assert_equal("application/zip", response.get('Content-Type', ''))

def test_dump_config():
  c = make_logged_in_client()

  CANARY = "abracadabra"

  # Depending on the order of the conf.initialize() in settings, the set_for_testing() are not seen in the global settings variable
  clear = HIVE_SERVER_HOST.set_for_testing(CANARY)

  response1 = c.get(reverse('desktop.views.dump_config'))
  assert_true(CANARY in response1.content, response1.content)

  response2 = c.get(reverse('desktop.views.dump_config'), dict(private="true"))
  assert_true(CANARY in response2.content)

  # There are more private variables...
  assert_true(len(response1.content) < len(response2.content))

  clear()

  CANARY = "(localhost|127\.0\.0\.1):(50030|50070|50060|50075)"
  clear = proxy.conf.WHITELIST.set_for_testing(CANARY)

  response1 = c.get(reverse('desktop.views.dump_config'))
  assert_true(CANARY in response1.content)

  clear()

  # Malformed port per HUE-674
  CANARY = "asdfoijaoidfjaosdjffjfjaoojosjfiojdosjoidjfoa"
  clear = HIVE_SERVER_HOST.set_for_testing(CANARY)

  response1 = c.get(reverse('desktop.views.dump_config'))
  assert_true(CANARY in response1.content, response1.content)

  clear()

  CANARY = '/tmp/spacé.dat'
  finish = proxy.conf.WHITELIST.set_for_testing(CANARY)
  try:
    response = c.get(reverse('desktop.views.dump_config'))
    assert_true(CANARY in response.content, response.content)
  finally:
    finish()

  # Not showing some passwords
  response = c.get(reverse('desktop.views.dump_config'))
  assert_false('bind_password' in response.content)

  # Login as someone else
  client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
  grant_access("not_me", "test", "desktop")

  response = client_not_me.get(reverse('desktop.views.dump_config'))
  assert_true("You must be a superuser" in response.content, response.content)

  os.environ["HUE_CONF_DIR"] = "/tmp/test_hue_conf_dir"
  resp = c.get(reverse('desktop.views.dump_config'))
  del os.environ["HUE_CONF_DIR"]
  assert_true('/tmp/test_hue_conf_dir' in resp.content, resp)


def hue_version():
  global HUE_VERSION
  HUE_VERSION_BAK = HUE_VERSION

  try:
    assert_equal('3.9.0-cdh5.9.0-SNAPSHOT', _version_from_properties(StringIO.StringIO("""# Autogenerated build properties
version=3.9.0-cdh5.9.0-SNAPSHOT
git.hash=f5fbe90b6a1d0c186b0ddc6e65ce5fc8d24725c8
cloudera.hash=f5fbe90b6a1d0c186b0ddc6e65ce5fc8d24725c8aaaaa""")))

    assert_equal(HUE_DESKTOP_VERSION, _version_from_properties(StringIO.StringIO("""# Autogenerated build properties
version=3.9.0-cdh5.9.0-SNAPSHOT git.hash=f5fbe90b6a1d0c186b0ddc6e65ce5fc8d24725c8 cloudera.hash=f5fbe90b6a1d0c186b0ddc6e65ce5fc8d24725c8aaaaa""")))

    assert_equal(HUE_DESKTOP_VERSION, _version_from_properties(StringIO.StringIO('')))
  finally:
    HUE_VERSION = HUE_VERSION_BAK


def test_prefs():
  c = make_logged_in_client()

  # Get everything
  response = c.get('/desktop/api2/user_preferences/')
  assert_equal({}, json.loads(response.content)['data'])

  # Set and get
  response = c.post('/desktop/api2/user_preferences/foo', {'set': 'bar'})
  assert_equal('bar', json.loads(response.content)['data']['foo'])
  response = c.get('/desktop/api2/user_preferences/')
  assert_equal('bar', json.loads(response.content)['data']['foo'])

  # Reset (use post this time)
  c.post('/desktop/api2/user_preferences/foo', {'set': 'baz'})
  response = c.get('/desktop/api2/user_preferences/foo')
  assert_equal('baz', json.loads(response.content)['data']['foo'])

  # Check multiple values
  c.post('/desktop/api2/user_preferences/elephant', {'set': 'room'})
  response = c.get('/desktop/api2/user_preferences/')
  assert_true("baz" in json.loads(response.content)['data'].values(), response.content)
  assert_true("room" in json.loads(response.content)['data'].values(), response.content)

  # Delete everything
  c.post('/desktop/api2/user_preferences/elephant', {'delete': ''})
  c.post('/desktop/api2/user_preferences/foo', {'delete': ''})
  response = c.get('/desktop/api2/user_preferences/')
  assert_equal({}, json.loads(response.content)['data'])

  # Check non-existent value
  response = c.get('/desktop/api2/user_preferences/doesNotExist')
  assert_equal(None, json.loads(response.content)['data'])


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

  response = c.get("/desktop/status_bar")
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
  response = c.get("/desktop/debug/threads")
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


def test_error_handling():
  raise SkipTest

  restore_django_debug = desktop.conf.DJANGO_DEBUG_MODE.set_for_testing(False)
  restore_500_debug = desktop.conf.HTTP_500_DEBUG_MODE.set_for_testing(False)

  exc_msg = "error_raising_view: Test earráid handling"
  def error_raising_view(request, *args, **kwargs):
    raise Exception(exc_msg)

  def popup_exception_view(request, *args, **kwargs):
    raise PopupException(exc_msg, title="earráid", detail=exc_msg)

  # Add an error view
  error_url_pat = patterns('',
                           url('^500_internal_error$', error_raising_view),
                           url('^popup_exception$', popup_exception_view))
  desktop.urls.urlpatterns.extend(error_url_pat)
  try:
    def store_exc_info(*args, **kwargs):
      pass
    # Disable the test client's exception forwarding
    c = make_logged_in_client()
    c.store_exc_info = store_exc_info

    response = c.get('/500_internal_error')
    assert_true(any(["500.mako" in _template.filename for _template in response.templates]))
    assert_true('Thank you for your patience' in response.content)
    assert_true(exc_msg not in response.content)

    # Now test the 500 handler with backtrace
    desktop.conf.HTTP_500_DEBUG_MODE.set_for_testing(True)
    response = c.get('/500_internal_error')
    assert_equal(response.template.name, 'Technical 500 template')
    assert_true(exc_msg in response.content)

    # PopupException
    response = c.get('/popup_exception')
    assert_true(any(["popup_error.mako" in _template.filename for _template in response.templates]))
    assert_true(exc_msg in response.content)
  finally:
    # Restore the world
    for i in error_url_pat:
      desktop.urls.urlpatterns.remove(i)
    restore_django_debug()
    restore_500_debug()


def test_desktop_permissions():
  USERNAME = 'test_core_permissions'
  GROUPNAME = 'default'

  desktop.conf.REDIRECT_WHITELIST.set_for_testing('^\/.*$,^http:\/\/testserver\/.*$')

  c = make_logged_in_client(USERNAME, groupname=GROUPNAME, recreate=True, is_superuser=False)

  # Access to the basic works
  assert_equal(200, c.get('/accounts/login/', follow=True).status_code)
  assert_equal(200, c.get('/accounts/logout', follow=True).status_code)
  assert_equal(200, c.get('/home', follow=True).status_code)


def test_app_permissions():
  USERNAME = 'test_app_permissions'
  GROUPNAME = 'impala_only'
  desktop.conf.REDIRECT_WHITELIST.set_for_testing('^\/.*$,^http:\/\/testserver\/.*$')

  c = make_logged_in_client(USERNAME, groupname=GROUPNAME, recreate=True, is_superuser=False)

  # Reset all perms
  GroupPermission.objects.filter(group__name=GROUPNAME).delete()

  def check_app(status_code, app_name):
    if app_name in DESKTOP_APPS:
      assert_equal(
          status_code,
          c.get('/' + app_name, follow=True).status_code,
          'status_code=%s app_name=%s' % (status_code, app_name))

  # Access to nothing
  check_app(401, 'beeswax')
  check_app(401, 'impala')
  check_app(401, 'hbase')

  # Add access to beeswax
  grant_access(USERNAME, GROUPNAME, "beeswax")
  check_app(200, 'beeswax')
  check_app(401, 'impala')
  check_app(401, 'hbase')

  # Add access to hbase
  grant_access(USERNAME, GROUPNAME, "hbase")
  check_app(200, 'beeswax')
  check_app(401, 'impala')
  check_app(200, 'hbase')

  # Reset all perms
  GroupPermission.objects.filter(group__name=GROUPNAME).delete()
  check_app(401, 'beeswax')
  check_app(401, 'impala')
  check_app(401, 'hbase')

  # Test only impala perm
  grant_access(USERNAME, GROUPNAME, "impala")
  check_app(401, 'beeswax')
  check_app(200, 'impala')
  check_app(401, 'hbase')


def test_error_handling_failure():
  # Change rewrite_user to call has_hue_permission
  # Try to get filebrowser page
  # test for default 500 page
  # Restore rewrite_user
  import desktop.auth.backend

  c = make_logged_in_client()

  restore_django_debug = desktop.conf.DJANGO_DEBUG_MODE.set_for_testing(False)
  restore_500_debug = desktop.conf.HTTP_500_DEBUG_MODE.set_for_testing(False)

  original_rewrite_user = desktop.auth.backend.rewrite_user

  def rewrite_user(user):
    user = original_rewrite_user(user)
    delattr(user, 'has_hue_permission')
    return user

  original_rewrite_user = desktop.auth.backend.rewrite_user
  desktop.auth.backend.rewrite_user = rewrite_user

  try:
    # Make sure we are showing default 500.html page.
    # See django.test.client#L246
    assert_raises(AttributeError, c.get, reverse('desktop.views.dump_config'))
  finally:
    # Restore the world
    restore_django_debug()
    restore_500_debug()
    desktop.auth.backend.rewrite_user = original_rewrite_user


def test_404_handling():
  view_name = '/the-view-that-is-not-there'
  c = make_logged_in_client()
  response = c.get(view_name)
  assert_true(any(['404.mako' in _template.filename for _template in response.templates]), response.templates)
  assert_true('not found' in response.content)
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

  c.get("/desktop/log_frontend_event?level=info&message=foo")
  assert_equal("INFO", handler.records[-1].levelname)
  assert_equal("Untrusted log event from user test: foo", handler.records[-1].message)
  assert_equal("desktop.views.log_frontend_event", handler.records[-1].name)

  c.get("/desktop/log_frontend_event?level=error&message=foo2")
  assert_equal("ERROR", handler.records[-1].levelname)
  assert_equal("Untrusted log event from user test: foo2", handler.records[-1].message)

  c.get("/desktop/log_frontend_event?message=foo3")
  assert_equal("INFO", handler.records[-1].levelname)
  assert_equal("Untrusted log event from user test: foo3", handler.records[-1].message)

  c.post("/desktop/log_frontend_event", {
    "message": "01234567" * 1024})
  assert_equal("INFO", handler.records[-1].levelname)
  assert_equal("Untrusted log event from user test: " + "01234567"*(1024/8),
    handler.records[-1].message)

  root.removeHandler(handler)

def test_validate_path():
  with tempfile.NamedTemporaryFile() as local_file:
    reset = desktop.conf.SSL_PRIVATE_KEY.set_for_testing(local_file.name)
    assert_equal([], validate_path(desktop.conf.SSL_PRIVATE_KEY, is_dir=False))
    reset()

  try:
    reset = desktop.conf.SSL_PRIVATE_KEY.set_for_testing('/tmm/does_not_exist')
    assert_not_equal([], validate_path(desktop.conf.SSL_PRIVATE_KEY, is_dir=True))
    assert_true(False)
  except Exception, ex:
    assert_true('does not exist' in str(ex), ex)
  finally:
    reset()

@attr('requires_hadoop')
def test_config_check():
  with tempfile.NamedTemporaryFile() as cert_file:
    with tempfile.NamedTemporaryFile() as key_file:
      reset = (
        desktop.conf.SECRET_KEY.set_for_testing(''),
        desktop.conf.SECRET_KEY_SCRIPT.set_for_testing(present=False),
        desktop.conf.SSL_CERTIFICATE.set_for_testing(cert_file.name),
        desktop.conf.SSL_PRIVATE_KEY.set_for_testing(key_file.name),
        desktop.conf.DEFAULT_SITE_ENCODING.set_for_testing('klingon')
      )

      try:
        cli = make_logged_in_client()
        resp = cli.get('/desktop/debug/check_config')
        assert_true('Secret key should be configured' in resp.content, resp)
        assert_true('klingon' in resp.content, resp)
        assert_true('Encoding not supported' in resp.content, resp)

        # Set HUE_CONF_DIR and make sure check_config returns appropriate conf
        os.environ["HUE_CONF_DIR"] = "/tmp/test_hue_conf_dir"
        resp = cli.get('/desktop/debug/check_config')
        del os.environ["HUE_CONF_DIR"]
        assert_true('/tmp/test_hue_conf_dir' in resp.content, resp)
      finally:
        for old_conf in reset:
          old_conf()


def test_last_access_time():
  c = make_logged_in_client(username="access_test")
  c.post('/accounts/login/')
  login = desktop.auth.views.get_current_users()
  before_access_time = time.time()
  response = c.get('/home')
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


def test_ui_customizations():
  custom_message = 'test ui customization'
  reset = (
    desktop.conf.CUSTOM.BANNER_TOP_HTML.set_for_testing(custom_message),
    desktop.conf.CUSTOM.LOGIN_SPLASH_HTML.set_for_testing(custom_message),
  )

  try:
    c = make_logged_in_client()
    resp = c.get('/accounts/login/', follow=False)
    assert_true(custom_message in resp.content, resp)
    resp = c.get('/about', follow=True)
    assert_true(custom_message in resp.content, resp)
  finally:
    for old_conf in reset:
      old_conf()


@attr('requires_hadoop')
def test_check_config_ajax():
  c = make_logged_in_client()
  response = c.get(reverse(check_config))
  assert_true("misconfiguration" in response.content, response.content)


def test_cx_Oracle():
  """
  Tests that cx_Oracle (external dependency) is built correctly.
  """
  if 'ORACLE_HOME' not in os.environ and 'ORACLE_INSTANTCLIENT_HOME' not in os.environ:
    raise SkipTest

  try:
    import cx_Oracle
    return
  except ImportError, ex:
    if "No module named" in ex.message:
      assert_true(False, "cx_Oracle skipped its build. This happens if "
          "env var ORACLE_HOME or ORACLE_INSTANTCLIENT_HOME is not defined. "
          "So ignore this test failure if your build does not need to work "
          "with an oracle backend.")

class TestStrictRedirection():

  def setUp(self):
    self.client = make_logged_in_client()
    self.user = dict(username="test", password="test")
    desktop.conf.REDIRECT_WHITELIST.set_for_testing('^\/.*$,^http:\/\/example.com\/.*$')

  def test_redirection_blocked(self):
    # Redirection with code 301 should be handled properly
    # Redirection with Status code 301 example reference: http://www.somacon.com/p145.php
    self._test_redirection(redirection_url='http://www.somacon.com/color/html_css_table_border_styles.php',
                           expected_status_code=403)
    # Redirection with code 302 should be handled properly
    self._test_redirection(redirection_url='http://www.google.com',
                           expected_status_code=403)

  def test_redirection_allowed(self):
    # Redirection to the host where Hue is running should be OK.
    self._test_redirection(redirection_url='/', expected_status_code=302)
    self._test_redirection(redirection_url='/pig', expected_status_code=302)
    self._test_redirection(redirection_url='http://testserver/', expected_status_code=302)
    self._test_redirection(redirection_url='https://testserver/', expected_status_code=302, **{
      'SERVER_PORT': '443',
      'wsgi.url_scheme': 'https',
    })
    self._test_redirection(redirection_url='http://example.com/', expected_status_code=302)

  def _test_redirection(self, redirection_url, expected_status_code, **kwargs):
    self.client.get('/accounts/logout', **kwargs)
    response = self.client.post('/accounts/login/?next=' + redirection_url, self.user, **kwargs)
    assert_equal(expected_status_code, response.status_code)
    if expected_status_code == 403:
        error_msg = 'Redirect to ' + redirection_url + ' is not allowed.'
        assert_true(error_msg in response.content, response.content)


class BaseTestPasswordConfig(object):

  SCRIPT = '%s -c "print \'\\n password from script \\n\'"' % sys.executable

  def get_config_password(self):
    raise NotImplementedError

  def get_config_password_script(self):
    raise NotImplementedError

  def get_password(self):
    raise NotImplementedError

  def test_read_password_from_script(self):
    self._run_test_read_password_from_script_with(present=False)
    self._run_test_read_password_from_script_with(data=None)
    self._run_test_read_password_from_script_with(data='')

  def _run_test_read_password_from_script_with(self, **kwargs):
    resets = [
      self.get_config_password().set_for_testing(**kwargs),
      self.get_config_password_script().set_for_testing(self.SCRIPT),
    ]

    try:
      assert_equal(self.get_password(), ' password from script ', 'pwd: %s, kwargs: %s' % (self.get_password(), kwargs))
    finally:
      for reset in resets:
        reset()

  def test_config_password_overrides_script_password(self):
    resets = [
      self.get_config_password().set_for_testing(' password from config '),
      self.get_config_password_script().set_for_testing(self.SCRIPT),
    ]

    try:
      assert_equal(self.get_password(), ' password from config ')
    finally:
      for reset in resets:
        reset()

  def test_password_script_raises_exception(self):
    resets = [
      self.get_config_password().set_for_testing(present=False),
      self.get_config_password_script().set_for_testing(
          '%s -c "import sys; sys.exit(1)"' % sys.executable
      ),
    ]

    try:
      assert_raises(subprocess.CalledProcessError, self.get_password)
    finally:
      for reset in resets:
        reset()

    resets = [
      self.get_config_password().set_for_testing(present=False),
      self.get_config_password_script().set_for_testing('/does-not-exist'),
    ]

    try:
      assert_raises(subprocess.CalledProcessError, self.get_password)
    finally:
      for reset in resets:
        reset()


class TestSecretKeyConfig(BaseTestPasswordConfig):

  def get_config_password(self):
    return desktop.conf.SECRET_KEY

  def get_config_password_script(self):
    return desktop.conf.SECRET_KEY_SCRIPT

  def get_password(self):
    return desktop.conf.get_secret_key()


class TestDatabasePasswordConfig(BaseTestPasswordConfig):

  def get_config_password(self):
    return desktop.conf.DATABASE.PASSWORD

  def get_config_password_script(self):
    return desktop.conf.DATABASE.PASSWORD_SCRIPT

  def get_password(self):
    return desktop.conf.get_database_password()


class TestLDAPPasswordConfig(BaseTestPasswordConfig):

  def get_config_password(self):
    return desktop.conf.AUTH_PASSWORD

  def get_config_password_script(self):
    return desktop.conf.AUTH_PASSWORD_SCRIPT

  def get_password(self):
    # We are using dynamic_default now, so we need to cheat for the tests as only using set_for_testing(present=False) will trigger it.
    if desktop.conf.AUTH_PASSWORD.get():
      return desktop.conf.AUTH_PASSWORD.get()
    else:
      return self.get_config_password_script().get()


class TestLDAPBindPasswordConfig(BaseTestPasswordConfig):

  def setup(self):
    self.finish = desktop.conf.LDAP.LDAP_SERVERS.set_for_testing({'test': {}})

  def teardown(self):
    self.finish()

  def get_config_password(self):
    return desktop.conf.LDAP.LDAP_SERVERS['test'].BIND_PASSWORD

  def get_config_password_script(self):
    return desktop.conf.LDAP.LDAP_SERVERS['test'].BIND_PASSWORD_SCRIPT

  def get_password(self):
    return desktop.conf.get_ldap_bind_password(desktop.conf.LDAP.LDAP_SERVERS['test'])


class TestSMTPPasswordConfig(BaseTestPasswordConfig):

  def get_config_password(self):
    return desktop.conf.SMTP.PASSWORD

  def get_config_password_script(self):
    return desktop.conf.SMTP.PASSWORD_SCRIPT

  def get_password(self):
    return desktop.conf.get_smtp_password()


class TestDocument(object):

  def setUp(self):
    make_logged_in_client(username="original_owner", groupname="test_doc", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="original_owner")

    make_logged_in_client(username="copy_owner", groupname="test_doc", recreate=True, is_superuser=False)
    self.copy_user = User.objects.get(username="copy_owner")

    self.document2 = Document2.objects.create(name='Test Document2',
                                              type='search-dashboard',
                                              owner=self.user,
                                              description='Test Document2')

    self.document = Document.objects.link(content_object=self.document2,
                                          owner=self.user,
                                          name='Test Document',
                                          description='Test Document',
                                          extra='test')

    self.document.save()
    self.document2.doc.add(self.document)

  def tearDown(self):
    # Get any Doc2 objects that were created and delete them, Doc1 child objects will be deleted in turn
    test_docs = Document2.objects.filter(name__contains='Test Document2')
    test_docs.delete()

  def test_document_create(self):
    assert_true(Document2.objects.filter(name='Test Document2').exists())
    assert_true(Document.objects.filter(name='Test Document').exists())
    assert_equal(Document2.objects.get(name='Test Document2').id, self.document2.id)
    assert_equal(Document.objects.get(name='Test Document').id, self.document.id)

  def test_document_trashed_and_restore(self):
    home_dir = Directory.objects.get_home_directory(self.user)
    test_dir, created = Directory.objects.get_or_create(
        parent_directory=home_dir,
        owner=self.user,
        name='test_dir'
    )
    test_doc = Document2.objects.create(
        name='Test Document2',
        type='search-dashboard',
        owner=self.user,
        description='Test Document2',
        parent_directory=test_dir
    )

    child_dir, created = Directory.objects.get_or_create(
        parent_directory=test_dir,
        owner=self.user,
        name='child_dir'
    )
    test_doc1 = Document2.objects.create(
        name='Test Document2',
        type='search-dashboard',
        owner=self.user,
        description='Test Document2',
        parent_directory=child_dir
    )

    assert_false(test_dir.is_trashed)
    assert_false(test_doc.is_trashed)
    assert_false(child_dir.is_trashed)
    assert_false(test_doc1.is_trashed)

    try:
      test_dir.trash()
      test_dir = Document2.objects.get(id=test_dir.id)
      test_doc = Document2.objects.get(id=test_doc.id)
      child_dir = Document2.objects.get(id=child_dir.id)
      test_doc1 = Document2.objects.get(id=test_doc1.id)
      assert_true(test_doc.is_trashed)
      assert_true(test_dir.is_trashed)
      assert_true(child_dir.is_trashed)
      assert_true(test_doc1.is_trashed)

      # Test restore
      test_dir.restore()
      test_dir = Document2.objects.get(id=test_dir.id)
      test_doc = Document2.objects.get(id=test_doc.id)
      child_dir = Document2.objects.get(id=child_dir.id)
      test_doc1 = Document2.objects.get(id=test_doc1.id)
      assert_false(test_doc.is_trashed)
      assert_false(test_dir.is_trashed)
      assert_false(child_dir.is_trashed)
      assert_false(test_doc1.is_trashed)
    finally:
      test_doc.delete()
      test_dir.delete()
      test_doc1.delete()
      child_dir.delete()


  def test_multiple_home_directories(self):
    home_dir = Directory.objects.get_home_directory(self.user)
    test_doc1 = Document2.objects.create(name='test-doc1',
                                         type='query-hive',
                                         owner=self.user,
                                         description='',
                                         parent_directory=home_dir)

    assert_equal(home_dir.children.exclude(name='.Trash').count(), 2)

    # Cannot create second home directory directly as it will fail in Document2.validate()
    second_home_dir = Document2.objects.create(owner=self.user, parent_directory=None, name='second_home_dir', type='directory')
    Document2.objects.filter(name='second_home_dir').update(name=Document2.HOME_DIR, parent_directory=None)
    assert_equal(Document2.objects.filter(owner=self.user, name=Document2.HOME_DIR).count(), 2)

    test_doc2 = Document2.objects.create(name='test-doc2',
                                              type='query-hive',
                                              owner=self.user,
                                              description='',
                                              parent_directory=second_home_dir)
    assert_equal(second_home_dir.children.count(), 1)

    merged_home_dir = Directory.objects.get_home_directory(self.user)
    children = merged_home_dir.children.all()
    assert_equal(children.exclude(name='.Trash').count(), 3)
    children_names = [child.name for child in children]
    assert_true(test_doc2.name in children_names)
    assert_true(test_doc1.name in children_names)

  def test_multiple_trash_directories(self):
    home_dir = Directory.objects.get_home_directory(self.user)
    test_doc1 = Document2.objects.create(name='test-doc1',
                                         type='query-hive',
                                         owner=self.user,
                                         description='',
                                         parent_directory=home_dir)

    assert_equal(home_dir.children.count(), 3)

    # Cannot create second trash directory directly as it will fail in Document2.validate()
    Document2.objects.create(owner=self.user, parent_directory=home_dir, name='second_trash_dir', type='directory')
    Document2.objects.filter(name='second_trash_dir').update(name=Document2.TRASH_DIR)
    assert_equal(Directory.objects.filter(owner=self.user, name=Document2.TRASH_DIR).count(), 2)


    test_doc2 = Document2.objects.create(name='test-doc2',
                                              type='query-hive',
                                              owner=self.user,
                                              description='',
                                              parent_directory=home_dir)
    assert_equal(home_dir.children.count(), 5) # Including the second trash
    assert_raises(Document2.MultipleObjectsReturned, Directory.objects.get, name=Document2.TRASH_DIR)

    test_doc1.trash()
    assert_equal(home_dir.children.count(), 3) # As trash documents are merged count is back to 3
    merged_trash_dir = Directory.objects.get(name=Document2.TRASH_DIR, owner=self.user)

    test_doc2.trash()
    children = merged_trash_dir.children.all()
    assert_equal(children.count(), 2)
    children_names = [child.name for child in children]
    assert_true(test_doc2.name in children_names)
    assert_true(test_doc1.name in children_names)


  def test_document_copy(self):
    name = 'Test Document2 Copy'

    self.doc2_count = Document2.objects.count()
    self.doc1_count = Document.objects.count()

    doc2 = self.document2.copy(name=name, owner=self.copy_user, description=self.document2.description)
    doc = self.document.copy(doc2, name=name, owner=self.copy_user, description=self.document2.description)

    # Test that copying creates another object
    assert_equal(Document2.objects.count(), self.doc2_count + 1)
    assert_equal(Document.objects.count(), self.doc1_count + 1)

    # Test that the content object is not pointing to the same object
    assert_not_equal(self.document2.doc, doc2.doc)

    # Test that the owner is attributed to the new user
    assert_equal(doc2.owner, self.copy_user)

    # Test that copying enables attribute overrides
    assert_equal(Document2.objects.filter(name=name).count(), 1)
    assert_equal(doc2.description, self.document2.description)

    # Test that the content object is not pointing to the same object
    assert_not_equal(self.document.content_object, doc.content_object)

    # Test that the owner is attributed to the new user
    assert_equal(doc.owner, self.copy_user)

    # Test that copying enables attribute overrides
    assert_equal(Document.objects.filter(name=name).count(), 1)
    assert_equal(doc.description, self.document.description)


  def test_redact_statements(self):
    old_policies = redaction.global_redaction_engine.policies
    redaction.global_redaction_engine.policies = [
      RedactionPolicy([
        RedactionRule('', 'ssn=\d{3}-\d{2}-\d{4}', 'ssn=XXX-XX-XXXX'),
      ])
    ]

    logfilter.add_log_redaction_filter_to_logger(redaction.global_redaction_engine, logging.root)

    sensitive_query = 'SELECT "ssn=123-45-6789"'
    redacted_query = 'SELECT "ssn=XXX-XX-XXXX"'
    nonsensitive_query = 'SELECT "hello"'

    snippets = [
      {
        'status': 'ready',
        'viewSettings': {
          'sqlDialect': True,
          'snippetImage': '/static/beeswax/art/icon_beeswax_48.png',
          'placeHolder': 'Example: SELECT * FROM tablename, or press CTRL + space',
          'aceMode': 'ace/mode/hive'
         },
        'id': '10a29cda-063f-1439-4836-d0c460154075',
        'statement_raw': sensitive_query,
        'statement': sensitive_query,
        'type': 'hive'
      },
      {
        'status': 'ready',
        'viewSettings': {
          'sqlDialect': True,
          'snippetImage': '/static/impala/art/icon_impala_48.png',
          'placeHolder': 'Example: SELECT * FROM tablename, or press CTRL + space',
          'aceMode': 'ace/mode/impala'
         },
        'id': 'e17d195a-beb5-76bf-7489-a9896eeda67a',
        'statement_raw': sensitive_query,
        'statement': sensitive_query,
        'type': 'impala'
      },
      {
        'status': 'ready',
        'viewSettings': {
          'sqlDialect': True,
          'snippetImage': '/static/beeswax/art/icon_beeswax_48.png',
          'placeHolder': 'Example: SELECT * FROM tablename, or press CTRL + space',
          'aceMode': 'ace/mode/hive'
         },
        'id': '10a29cda-063f-1439-4836-d0c460154075',
        'statement_raw': nonsensitive_query,
        'statement': nonsensitive_query,
        'type': 'hive'
      },
    ]

    try:
      self.document2.type = 'notebook'
      self.document2.update_data({'snippets': snippets})
      self.document2.search = sensitive_query
      self.document2.save()
      saved_snippets = self.document2.data_dict['snippets']

      # Make sure redacted queries are redacted.
      assert_equal(redacted_query, saved_snippets[0]['statement'])
      assert_equal(redacted_query, saved_snippets[0]['statement_raw'])
      assert_equal(True, saved_snippets[0]['is_redacted'])

      assert_equal(redacted_query, saved_snippets[1]['statement'])
      assert_equal(redacted_query, saved_snippets[1]['statement_raw'])
      assert_equal(True, saved_snippets[1]['is_redacted'])

      document = Document2.objects.get(pk=self.document2.pk)
      assert_equal(redacted_query, document.search)

      # Make sure unredacted queries are not redacted.
      assert_equal(nonsensitive_query, saved_snippets[2]['statement'])
      assert_equal(nonsensitive_query, saved_snippets[2]['statement_raw'])
      assert_false('is_redacted' in saved_snippets[2])
    finally:
      redaction.global_redaction_engine.policies = old_policies

  def test_get_document(self):
    c1 = make_logged_in_client(username='test_get_user', groupname='test_get_group', recreate=True, is_superuser=False)
    r1 = c1.get('/desktop/api/doc/get?id=1')
    assert_true(-1, json.loads(r1.content)['status'])

def test_session_secure_cookie():
  with tempfile.NamedTemporaryFile() as cert_file:
    with tempfile.NamedTemporaryFile() as key_file:
      resets = [
        desktop.conf.SSL_CERTIFICATE.set_for_testing(cert_file.name),
        desktop.conf.SSL_PRIVATE_KEY.set_for_testing(key_file.name),
        desktop.conf.SESSION.SECURE.set_for_testing(False),
      ]
      try:
        assert_true(desktop.conf.is_https_enabled())
        assert_false(desktop.conf.SESSION.SECURE.get())
      finally:
        for reset in resets:
          reset()

      resets = [
        desktop.conf.SSL_CERTIFICATE.set_for_testing(cert_file.name),
        desktop.conf.SSL_PRIVATE_KEY.set_for_testing(key_file.name),
        desktop.conf.SESSION.SECURE.set_for_testing(True),
      ]
      try:
        assert_true(desktop.conf.is_https_enabled())
        assert_true(desktop.conf.SESSION.SECURE.get())
      finally:
        for reset in resets:
          reset()

      resets = [
        desktop.conf.SSL_CERTIFICATE.set_for_testing(cert_file.name),
        desktop.conf.SSL_PRIVATE_KEY.set_for_testing(key_file.name),
        desktop.conf.SESSION.SECURE.set_for_testing(present=False),
      ]
      try:
        assert_true(desktop.conf.is_https_enabled())
        assert_true(desktop.conf.SESSION.SECURE.get())
      finally:
        for reset in resets:
          reset()

      resets = [
        desktop.conf.SSL_CERTIFICATE.set_for_testing(present=None),
        desktop.conf.SSL_PRIVATE_KEY.set_for_testing(present=None),
        desktop.conf.SESSION.SECURE.set_for_testing(present=False),
      ]
      try:
        assert_false(desktop.conf.is_https_enabled())
        assert_false(desktop.conf.SESSION.SECURE.get())
      finally:
        for reset in resets:
          reset()


def test_get_data_link():
  assert_equal(None, get_data_link({}))
  assert_equal('gethue.com', get_data_link({'type': 'link', 'link': 'gethue.com'}))

  assert_equal('/hbase/#Cluster/document_demo/query/20150527', get_data_link({'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527'}))
  assert_equal('/hbase/#Cluster/document_demo/query/20150527[f1]', get_data_link({'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1'}))
  assert_equal('/hbase/#Cluster/document_demo/query/20150527[f1:c1]', get_data_link({'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1', 'col': 'c1'}))

  assert_equal('/filebrowser/view=/data/hue/1', get_data_link({'type': 'hdfs', 'path': '/data/hue/1'}))
  assert_equal('/metastore/table/default/sample_07', get_data_link({'type': 'hive', 'database': 'default', 'table': 'sample_07'}))

def test_get_dn():
  assert_equal(['*'], desktop.conf.get_dn(''))
  assert_equal(['*'], desktop.conf.get_dn('localhost'))
  assert_equal(['*'], desktop.conf.get_dn('localhost.localdomain'))
  assert_equal(['*'], desktop.conf.get_dn('hue'))
  assert_equal(['*'], desktop.conf.get_dn('hue.com'))
  assert_equal(['.hue.com'], desktop.conf.get_dn('sql.hue.com'))
  assert_equal(['.hue.com'], desktop.conf.get_dn('finance.sql.hue.com'))
  assert_equal(['.hue.com'], desktop.conf.get_dn('bank.finance.sql.hue.com'))
