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
import sys
import tempfile
import time

import desktop
import desktop.conf
import desktop.urls
import desktop.views as views
import proxy.conf

from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal, assert_raises, nottest
from django.conf.urls import patterns, url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.db.models import query, CharField, SmallIntegerField

from useradmin.models import GroupPermission

from beeswax.conf import HIVE_SERVER_HOST
from desktop.lib import django_mako
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.paginator import Paginator
from desktop.lib.conf import validate_path
from desktop.lib.django_util import TruncatingModel
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.test_utils import grant_access
from desktop.models import Document
from desktop.views import check_config, home
from pig.models import PigScript


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


def test_prefs():
  c = make_logged_in_client()

  # Get everything
  response = c.get('/desktop/prefs/')
  assert_equal('{}', response.content)

  # Set and get
  response = c.get('/desktop/prefs/foo', dict(set="bar"))
  assert_equal('true', response.content)
  response = c.get('/desktop/prefs/foo')
  assert_equal('"bar"', response.content)

  # Reset (use post this time)
  c.post('/desktop/prefs/foo', dict(set="baz"))
  response = c.get('/desktop/prefs/foo')
  assert_equal('"baz"', response.content)

  # Check multiple values
  c.post('/desktop/prefs/elephant', dict(set="room"))
  response = c.get('/desktop/prefs/')
  assert_true("baz" in response.content)
  assert_true("room" in response.content)

  # Delete everything
  c.get('/desktop/prefs/elephant', dict(delete=""))
  c.get('/desktop/prefs/foo', dict(delete=""))
  response = c.get('/desktop/prefs/')
  assert_equal('{}', response.content)

  # Check non-existent value
  response = c.get('/desktop/prefs/doesNotExist')
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

  # Access to nothing
  assert_equal(401, c.get('/beeswax', follow=True).status_code)
  assert_equal(401, c.get('/impala', follow=True).status_code)
  assert_equal(401, c.get('/hbase', follow=True).status_code)

  # Add access to beeswax
  grant_access(USERNAME, GROUPNAME, "beeswax")
  assert_equal(200, c.get('/beeswax', follow=True).status_code)
  assert_equal(401, c.get('/impala', follow=True).status_code)
  assert_equal(401, c.get('/hbase', follow=True).status_code)

  # Add access to hbase
  grant_access(USERNAME, GROUPNAME, "hbase")
  assert_equal(200, c.get('/beeswax', follow=True).status_code)
  assert_equal(401, c.get('/impala', follow=True).status_code)
  assert_equal(200, c.get('/hbase', follow=True).status_code)

  # Reset all perms
  GroupPermission.objects.filter(group__name=GROUPNAME).delete()

  assert_equal(401, c.get('/beeswax', follow=True).status_code)
  assert_equal(401, c.get('/impala', follow=True).status_code)
  assert_equal(401, c.get('/hbase', follow=True).status_code)

  # Test only impala perm
  grant_access(USERNAME, GROUPNAME, "impala")
  assert_equal(401, c.get('/beeswax', follow=True).status_code)
  assert_equal(200, c.get('/impala', follow=True).status_code)
  assert_equal(401, c.get('/hbase', follow=True).status_code)


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
  assert_true('Not Found' in response.content)
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
  reset = desktop.conf.SSL_PRIVATE_KEY.set_for_testing('/')
  assert_equal([], validate_path(desktop.conf.SSL_PRIVATE_KEY, is_dir=True))
  reset()

  reset = desktop.conf.SSL_PRIVATE_KEY.set_for_testing('/tmm/does_not_exist')
  assert_not_equal([], validate_path(desktop.conf.SSL_PRIVATE_KEY, is_dir=True))
  reset()

@attr('requires_hadoop')
def test_config_check():
  reset = (
    desktop.conf.SECRET_KEY.set_for_testing(''),
    desktop.conf.SSL_CERTIFICATE.set_for_testing('foobar'),
    desktop.conf.SSL_PRIVATE_KEY.set_for_testing(''),
    desktop.conf.DEFAULT_SITE_ENCODING.set_for_testing('klingon')
  )

  try:
    cli = make_logged_in_client()
    resp = cli.get('/desktop/debug/check_config')
    assert_true('Secret key should be configured' in resp.content, resp)
    assert_true('desktop.ssl_certificate' in resp.content, resp)
    assert_true('Path does not exist' in resp.content, resp)
    assert_true('SSL private key file should be set' in resp.content, resp)
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
  custom_banner = 'test ui customization'
  reset = (
    desktop.conf.CUSTOM.BANNER_TOP_HTML.set_for_testing(custom_banner),
  )

  try:
    c = make_logged_in_client()
    resp = c.get('/about', follow=True)
    assert_true(custom_banner in resp.content, resp)
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

  @nottest
  def run_test_read_password_from_script(self):
    resets = [
      self.get_config_password().set_for_testing(None),
      self.get_config_password_script().set_for_testing(self.SCRIPT)
    ]

    try:
      assert_equal(self.get_password(), ' password from script ')
    finally:
      for reset in resets:
        reset()

  @nottest
  def run_test_config_password_overrides_script_password(self):
    resets = [
      self.get_config_password().set_for_testing(' password from config '),
      self.get_config_password_script().set_for_testing(self.SCRIPT),
    ]

    try:
      assert_equal(self.get_password(), ' password from config ')
    finally:
      for reset in resets:
        reset()


class TestDatabasePasswordConfig(BaseTestPasswordConfig):

  def get_config_password(self):
    return desktop.conf.DATABASE.PASSWORD

  def get_config_password_script(self):
    return desktop.conf.DATABASE.PASSWORD_SCRIPT

  def get_password(self):
    return desktop.conf.get_database_password()

  def test_read_password_from_script(self):
    self.run_test_read_password_from_script()

  def test_config_password_overrides_script_password(self):
    self.run_test_config_password_overrides_script_password()


class TestLDAPPasswordConfig(BaseTestPasswordConfig):

  def get_config_password(self):
    return desktop.conf.LDAP_PASSWORD

  def get_config_password_script(self):
    return desktop.conf.LDAP_PASSWORD_SCRIPT

  def get_password(self):
    return desktop.conf.get_ldap_password()

  def test_read_password_from_script(self):
    self.run_test_read_password_from_script()

  def test_config_password_overrides_script_password(self):
    self.run_test_config_password_overrides_script_password()

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

  def test_read_password_from_script(self):
    self.run_test_read_password_from_script()

  def test_config_password_overrides_script_password(self):
    self.run_test_config_password_overrides_script_password()

class TestSMTPPasswordConfig(BaseTestPasswordConfig):

  def get_config_password(self):
    return desktop.conf.SMTP.PASSWORD

  def get_config_password_script(self):
    return desktop.conf.SMTP.PASSWORD_SCRIPT

  def get_password(self):
    return desktop.conf.get_smtp_password()

  def test_read_password_from_script(self):
    self.run_test_read_password_from_script()

  def test_config_password_overrides_script_password(self):
    self.run_test_config_password_overrides_script_password()
