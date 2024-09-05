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

import os
import sys
import json
import time
import uuid
import logging
import tempfile
import subprocess
from io import StringIO as string_io
from unittest.mock import Mock, patch

import pytest
from configobj import ConfigObj
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import CharField, SmallIntegerField, query
from django.http import HttpResponse
from django.test.client import Client
from django.urls import re_path, reverse
from django.views.static import serve

import desktop
import desktop.conf
import desktop.urls
import desktop.views as views
import notebook.conf
import desktop.redaction as redaction
from dashboard.conf import HAS_SQL_ENABLED
from desktop.appmanager import DESKTOP_APPS
from desktop.auth.backend import rewrite_user
from desktop.lib.conf import _configs_from_dir, validate_path
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.django_util import TruncatingModel
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.paths import get_desktop_root
from desktop.lib.python_util import force_dict_to_strings
from desktop.lib.test_utils import grant_access
from desktop.middleware import DJANGO_VIEW_AUTH_WHITELIST
from desktop.models import HUE_VERSION, ClusterConfig, Directory, Document, Document2, _version_from_properties, get_data_link
from desktop.redaction import logfilter
from desktop.redaction.engine import RedactionPolicy, RedactionRule
from desktop.settings import DATABASES
from desktop.views import _get_config_errors, check_config, collect_validation_messages, generate_configspec, home, load_confs
from notebook.conf import ENABLE_ALL_INTERPRETERS, SHOW_NOTEBOOKS
from useradmin.models import GroupPermission, User

LOG = logging.getLogger()


@pytest.mark.django_db
def test_home():
  c = make_logged_in_client(username="test_home", groupname="test_home", recreate=True, is_superuser=False)
  user = User.objects.get(username="test_home")

  response = c.get(reverse(home))
  assert sorted(["notmine", "trash", "mine", "history"]) == sorted(list(json.loads(response.context[0]['json_tags']).keys()))
  assert 200 == response.status_code

  from pig.models import PigScript

  script, created = PigScript.objects.get_or_create(owner=user)
  doc = Document.objects.link(script, owner=script.owner, name='test_home')

  response = c.get(reverse(home))
  assert str(doc.id) in json.loads(response.context[0]['json_documents'])

  response = c.get(reverse(home))
  tags = json.loads(response.context[0]['json_tags'])
  assert [doc.id] == tags['mine'][0]['docs'], tags
  assert [] == tags['trash']['docs'], tags
  assert [] == tags['history']['docs'], tags

  doc.send_to_trash()

  response = c.get(reverse(home))
  tags = json.loads(response.context[0]['json_tags'])
  assert [] == tags['mine'][0]['docs'], tags
  assert [doc.id] == tags['trash']['docs'], tags
  assert [] == tags['history']['docs'], tags

  doc.restore_from_trash()

  response = c.get(reverse(home))
  tags = json.loads(response.context[0]['json_tags'])
  assert [doc.id] == tags['mine'][0]['docs'], tags
  assert [] == tags['trash']['docs'], tags
  assert [] == tags['history']['docs'], tags

  doc.add_to_history()

  response = c.get(reverse(home))
  tags = json.loads(response.context[0]['json_tags'])
  assert [] == tags['mine'][0]['docs'], tags
  assert [] == tags['trash']['docs'], tags
  assert [] == tags['history']['docs'], tags  # We currently don't fetch [doc.id]


@pytest.mark.django_db
def test_skip_wizard():
  pytest.skip("Skipping due to failures with pytest, investigation ongoing.")
  c = make_logged_in_client()  # is_superuser

  response = c.get('/', follow=True)
  assert ['admin_wizard.mako' in _template.filename for _template in response.templates], [
    _template.filename for _template in response.templates
  ]

  c.cookies['hueLandingPage'] = 'home'
  response = c.get('/', follow=True)
  assert ['home.mako' in _template.filename for _template in response.templates], [_template.filename for _template in response.templates]

  c.cookies['hueLandingPage'] = ''
  response = c.get('/', follow=True)
  assert ['admin_wizard.mako' in _template.filename for _template in response.templates], [
    _template.filename for _template in response.templates
  ]

  c = make_logged_in_client(username="test_skip_wizard", password="test_skip_wizard", is_superuser=False)

  response = c.get('/', follow=True)
  assert ['home.mako' in _template.filename for _template in response.templates], [_template.filename for _template in response.templates]

  c.cookies['hueLandingPage'] = 'home'
  response = c.get('/', follow=True)
  assert ['home.mako' in _template.filename for _template in response.templates], [_template.filename for _template in response.templates]

  c.cookies['hueLandingPage'] = ''
  response = c.get('/', follow=True)
  assert ['home.mako' in _template.filename for _template in response.templates], [_template.filename for _template in response.templates]


@pytest.mark.django_db
def test_public_views():
  c = Client()

  for view in DJANGO_VIEW_AUTH_WHITELIST:
    if view is serve:
      url = reverse(view, kwargs={'path': 'desktop/art/favicon.ico'})
    else:
      url = reverse(view)
    response = c.get(url)
    assert 200 == response.status_code


def test_prometheus_view():
  if not desktop.conf.ENABLE_PROMETHEUS.get():
    pytest.skip("Skipping Test")

  ALL_PROMETHEUS_METRICS = [
    'django_http_requests_before_middlewares_total',
    'django_http_responses_before_middlewares_total',
    'django_http_requests_latency_including_middlewares_seconds',
    'django_http_requests_unknown_latency_including_middlewares_total',
    'django_http_requests_latency_seconds_by_view_method',
    'django_http_requests_unknown_latency_total',
    'django_http_ajax_requests_total',
    'django_http_requests_total_by_method',
    'django_http_requests_total_by_transport',
    'django_http_requests_total_by_view_transport_method',
    'django_http_requests_body_total_bytes',
    'django_http_responses_total_by_templatename',
    'django_http_responses_total_by_status',
    'django_http_responses_body_total_bytes',
    'django_http_responses_total_by_charset',
    'django_http_responses_streaming_total',
    'django_http_exceptions_total_by_type',
    'django_http_exceptions_total_by_view',
  ]

  c = Client()
  response = c.get('/metrics')
  for metric in ALL_PROMETHEUS_METRICS:
    metric = metric if isinstance(metric, bytes) else metric.encode('utf-8')
    if metric not in desktop.metrics.ALLOWED_DJANGO_PROMETHEUS_METRICS:
      assert metric not in response.content, 'metric: %s \n %s' % (metric, response.content)
    else:
      assert metric in response.content, 'metric: %s \n %s' % (metric, response.content)


@pytest.mark.django_db
def test_log_view():
  c = make_logged_in_client()

  URL = reverse(views.log_view)

  LOG = logging.getLogger()
  LOG.warning('une voix m’a réveillé')

  # UnicodeDecodeError: 'ascii' codec can't decode byte... should not happen
  response = c.get(URL)
  assert 200 == response.status_code

  c = make_logged_in_client()

  URL = reverse(views.log_view)

  LOG = logging.getLogger()
  LOG.warning('Got response: PK\x03\x04\n\x00\x00\x08\x00\x00\xad\x0cN?\x00\x00\x00\x00')

  # DjangoUnicodeDecodeError: 'utf8' codec can't decode byte 0xad in position 75: invalid start byte... should not happen
  response = c.get(URL)
  assert 200 == response.status_code


def test_download_log_view():
  pytest.skip("Skipping Test")
  c = make_logged_in_client()

  URL = reverse(views.download_log_view)

  LOG = logging.getLogger()
  LOG.warning('une voix m’a réveillé')

  # UnicodeDecodeError: 'ascii' codec can't decode byte... should not happen
  response = c.get(URL)
  assert "application/zip" == response.get('Content-Type', '')


def hue_version():
  global HUE_VERSION
  HUE_VERSION_BAK = HUE_VERSION

  try:
    assert 'cdh6.x-SNAPSHOT' == _version_from_properties(
      string_io(
        """# Autogenerated build properties
      version=3.9.0-cdh5.9.0-SNAPSHOT
      git.hash=f5fbe90b6a1d0c186b0ddc6e65ce5fc8d24725c8
      cloudera.cdh.release=cdh6.x-SNAPSHOT
      cloudera.hash=f5fbe90b6a1d0c186b0ddc6e65ce5fc8d24725c8aaaaa"""
      )
    )

    assert not _version_from_properties(
      string_io(
        """# Autogenerated build properties
      version=3.9.0-cdh5.9.0-SNAPSHOT
      git.hash=f5fbe90b6a1d0c186b0ddc6e65ce5fc8d24725c8
      cloudera.hash=f5fbe90b6a1d0c186b0ddc6e65ce5fc8d24725c8aaaaa"""
      )
    )

    assert not _version_from_properties(string_io(''))
  finally:
    HUE_VERSION = HUE_VERSION_BAK


@pytest.mark.django_db
def test_prefs():
  c = make_logged_in_client()

  # Get everything
  response = c.get('/desktop/api2/user_preferences/')
  assert {} == json.loads(response.content)['data']

  # Set and get
  response = c.post('/desktop/api2/user_preferences/foo', {'set': 'bar'})
  assert 'bar' == json.loads(response.content)['data']['foo']
  response = c.get('/desktop/api2/user_preferences/')
  assert 'bar' == json.loads(response.content)['data']['foo']

  # Reset (use post this time)
  c.post('/desktop/api2/user_preferences/foo', {'set': 'baz'})
  response = c.get('/desktop/api2/user_preferences/foo')
  assert 'baz' == json.loads(response.content)['data']['foo']

  # Check multiple values
  c.post('/desktop/api2/user_preferences/elephant', {'set': 'room'})
  response = c.get('/desktop/api2/user_preferences/')
  assert "baz" in list(json.loads(response.content)['data'].values()), response.content
  assert "room" in list(json.loads(response.content)['data'].values()), response.content

  # Delete everything
  c.post('/desktop/api2/user_preferences/elephant', {'delete': ''})
  c.post('/desktop/api2/user_preferences/foo', {'delete': ''})
  response = c.get('/desktop/api2/user_preferences/')
  assert {} == json.loads(response.content)['data']

  # Check non-existent value
  response = c.get('/desktop/api2/user_preferences/doesNotExist')
  assert None is json.loads(response.content)['data']


@pytest.mark.django_db
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
  assert b"foobar" == response.content

  views._status_bar_views = backup


def test_paginator():
  """
  Test that the paginator works with partial list.
  """

  def assert_page(page, data, start, end):
    assert page.object_list == data
    assert page.start_index() == start
    assert page.end_index() == end

  # First page 1-20
  obj = list(range(20))
  pgn = Paginator(obj, per_page=20)
  assert_page(pgn.page(1), obj, 1, 20)

  # Handle extra data on first page (22 items on a 20-page)
  obj = list(range(22))
  pgn = Paginator(obj, per_page=20)
  assert_page(pgn.page(1), list(range(20)), 1, 20)

  # Handle total < len(obj). Only works for QuerySet.
  obj = query.QuerySet()
  obj._result_cache = list(range(10))
  pgn = Paginator(obj, per_page=10)
  assert_page(pgn.page(1), list(range(10)), 1, 10)

  # Still works with a normal complete list
  obj = list(range(25))
  pgn = Paginator(obj, per_page=20)
  assert_page(pgn.page(1), list(range(20)), 1, 20)
  assert_page(pgn.page(2), list(range(20, 25)), 21, 25)


def test_truncating_model():
  class TinyModel(TruncatingModel):
    short_field = CharField(max_length=10)
    non_string_field = SmallIntegerField()

  a = TinyModel()

  a.short_field = 'a' * 9  # One less than it's max length
  assert a.short_field == 'a' * 9, 'Short-enough field does not get truncated'

  a.short_field = 'a' * 11  # One more than it's max_length
  assert a.short_field == 'a' * 10, 'Too-long field gets truncated'

  a.non_string_field = 10**10
  assert a.non_string_field == 10**10, 'non-string fields are not truncated'


def test_error_handling():
  pytest.skip("Skipping Test")

  restore_django_debug = desktop.conf.DJANGO_DEBUG_MODE.set_for_testing(False)
  restore_500_debug = desktop.conf.HTTP_500_DEBUG_MODE.set_for_testing(False)

  exc_msg = "error_raising_view: Test earráid handling"

  def error_raising_view(request, *args, **kwargs):
    raise Exception(exc_msg)

  def popup_exception_view(request, *args, **kwargs):
    raise PopupException(exc_msg, title="earráid", detail=exc_msg)

  # Add an error view
  error_url_pat = [re_path('^500_internal_error$', error_raising_view), re_path('^popup_exception$', popup_exception_view)]
  desktop.urls.urlpatterns.extend(error_url_pat)
  try:

    def store_exc_info(*args, **kwargs):
      pass

    # Disable the test client's exception forwarding
    c = make_logged_in_client()
    c.store_exc_info = store_exc_info

    response = c.get('/500_internal_error')
    assert any(["500.mako" in _template.filename for _template in response.templates])
    assert 'Thank you for your patience' in response.content
    assert exc_msg not in response.content

    # Now test the 500 handler with backtrace
    desktop.conf.HTTP_500_DEBUG_MODE.set_for_testing(True)
    response = c.get('/500_internal_error')
    assert response.template.name == 'Technical 500 template'
    assert exc_msg in response.content

    # PopupException
    response = c.get('/popup_exception')
    assert any(["popup_error.mako" in _template.filename for _template in response.templates])
    assert exc_msg in response.content
  finally:
    # Restore the world
    for i in error_url_pat:
      desktop.urls.urlpatterns.remove(i)
    restore_django_debug()
    restore_500_debug()


@pytest.mark.django_db
def test_desktop_permissions():
  USERNAME = 'test_core_permissions'
  GROUPNAME = 'default'

  desktop.conf.REDIRECT_WHITELIST.set_for_testing(r'^\/.*$,^http:\/\/testserver\/.*$')

  c = make_logged_in_client(USERNAME, groupname=GROUPNAME, recreate=True, is_superuser=False)

  # Access to the basic works
  assert 200 == c.get('/hue/accounts/login/', follow=True).status_code
  assert 200 == c.get('/accounts/logout', follow=True).status_code
  assert 200 == c.get('/home', follow=True).status_code


@pytest.mark.django_db
def test_app_permissions():
  USERNAME = 'test_app_permissions'
  GROUPNAME = 'impala_only'
  resets = [
    desktop.conf.REDIRECT_WHITELIST.set_for_testing(r'^\/.*$,^http:\/\/testserver\/.*$'),
    HAS_SQL_ENABLED.set_for_testing(False),
    ENABLE_ALL_INTERPRETERS.set_for_testing(True),
    SHOW_NOTEBOOKS.set_for_testing(True)
  ]

  try:
    c = make_logged_in_client(USERNAME, groupname=GROUPNAME, recreate=True, is_superuser=False)
    user = rewrite_user(User.objects.get(username=USERNAME))

    # Reset all perms
    GroupPermission.objects.filter(group__name=GROUPNAME).delete()

    def check_app(status_code, app_name):
      if app_name in DESKTOP_APPS:
        assert status_code == c.get('/' + app_name, follow=True).status_code, 'status_code=%s app_name=%s' % (status_code, app_name)

    # Access to nothing
    check_app(401, 'beeswax')
    check_app(401, 'hive')
    check_app(401, 'impala')
    check_app(401, 'hbase')
    check_app(401, 'pig')
    check_app(401, 'search')
    check_app(401, 'spark')
    check_app(401, 'oozie')

    # Clean INTERPRETERS_CACHE before every get_apps() call to have dynamic interpreters value for test_user
    # because every testcase below needs clean INTERPRETERS_CACHE value as ENABLE_ALL_INTERPRETERS is now false by default.
    notebook.conf.INTERPRETERS_CACHE = None
    apps = ClusterConfig(user=user).get_apps()
    assert 'hive' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'impala' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'pig' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'solr' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'spark' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'browser' not in apps, apps
    assert 'scheduler' not in apps, apps
    assert 'dashboard' not in apps, apps
    assert 'scheduler' not in apps, apps
    assert 'sdkapps' not in apps, apps

    # Should always be enabled as it is a lib
    grant_access(USERNAME, GROUPNAME, "beeswax")

    # Add access to hive
    grant_access(USERNAME, GROUPNAME, "hive")
    check_app(200, 'beeswax')
    check_app(200, 'hive')
    check_app(401, 'impala')
    check_app(401, 'hbase')
    check_app(401, 'pig')
    check_app(401, 'search')
    check_app(401, 'spark')
    check_app(401, 'oozie')

    notebook.conf.INTERPRETERS_CACHE = None
    apps = ClusterConfig(user=user).get_apps()
    assert 'hive' in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'impala' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'pig' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'solr' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'spark' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'browser' not in apps, apps
    assert 'scheduler' not in apps, apps
    assert 'dashboard' not in apps, apps
    assert 'scheduler' not in apps, apps
    assert 'sdkapps' not in apps, apps

    # Add access to hbase
    grant_access(USERNAME, GROUPNAME, "hbase")
    check_app(200, 'beeswax')
    check_app(200, 'hive')
    check_app(401, 'impala')
    check_app(200, 'hbase')
    check_app(401, 'pig')
    check_app(401, 'search')
    check_app(401, 'spark')
    check_app(401, 'oozie')

    notebook.conf.INTERPRETERS_CACHE = None
    apps = ClusterConfig(user=user).get_apps()
    assert 'hive' in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'impala' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'pig' not in apps.get('editor', {}).get('interpreter_names', []), apps
    if 'hbase' not in desktop.conf.APP_BLACKLIST.get():
      assert 'browser' in apps, apps
      assert 'hbase' in apps['browser']['interpreter_names'], apps['browser']
    assert 'solr' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'spark' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'scheduler' not in apps, apps
    assert 'dashboard' not in apps, apps
    assert 'scheduler' not in apps, apps
    assert 'sdkapps' not in apps, apps

    # Reset all perms
    GroupPermission.objects.filter(group__name=GROUPNAME).delete()
    check_app(401, 'beeswax')
    check_app(401, 'impala')
    check_app(401, 'hbase')
    check_app(401, 'pig')
    check_app(401, 'search')
    check_app(401, 'spark')
    check_app(401, 'oozie')

    notebook.conf.INTERPRETERS_CACHE = None
    apps = ClusterConfig(user=user).get_apps()
    assert 'hive' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'impala' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'pig' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'solr' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'spark' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'browser' not in apps, apps
    assert 'scheduler' not in apps, apps
    assert 'dashboard' not in apps, apps
    assert 'scheduler' not in apps, apps
    assert 'sdkapps' not in apps, apps

    # Test only impala perm
    grant_access(USERNAME, GROUPNAME, "impala")
    check_app(401, 'beeswax')
    check_app(200, 'impala')
    check_app(401, 'hbase')
    check_app(401, 'pig')
    check_app(401, 'search')
    check_app(401, 'spark')
    check_app(401, 'oozie')

    notebook.conf.INTERPRETERS_CACHE = None
    apps = ClusterConfig(user=user).get_apps()
    assert 'hive' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'impala' in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'pig' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'solr' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'spark' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'browser' not in apps, apps
    assert 'scheduler' not in apps, apps
    assert 'dashboard' not in apps, apps
    assert 'scheduler' not in apps, apps
    assert 'sdkapps' not in apps, apps

    # Oozie Editor and Browser
    grant_access(USERNAME, GROUPNAME, "oozie")
    check_app(401, 'hive')
    check_app(200, 'impala')
    check_app(401, 'hbase')
    check_app(401, 'pig')
    check_app(401, 'search')
    check_app(401, 'spark')
    check_app(200, 'oozie')

    notebook.conf.INTERPRETERS_CACHE = None
    apps = ClusterConfig(user=user).get_apps()
    assert 'scheduler' in apps, apps
    assert 'browser' not in apps, apps  # Actually should be true, but logic not implemented
    assert 'solr' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'spark' not in apps.get('editor', {}).get('interpreter_names', []), apps

    grant_access(USERNAME, GROUPNAME, "pig")
    check_app(401, 'hive')
    check_app(200, 'impala')
    check_app(401, 'hbase')
    check_app(200, 'pig')
    check_app(401, 'search')
    check_app(401, 'spark')
    check_app(200, 'oozie')

    notebook.conf.INTERPRETERS_CACHE = None
    apps = ClusterConfig(user=user).get_apps()
    assert 'hive' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'impala' in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'pig' in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'solr' not in apps.get('editor', {}).get('interpreter_names', []), apps
    assert 'spark' not in apps.get('editor', {}).get('interpreter_names', []), apps

    if 'search' not in desktop.conf.APP_BLACKLIST.get():
      grant_access(USERNAME, GROUPNAME, "search")
      check_app(401, 'hive')
      check_app(200, 'impala')
      check_app(401, 'hbase')
      check_app(200, 'pig')
      check_app(200, 'search')
      check_app(401, 'spark')
      check_app(200, 'oozie')

      notebook.conf.INTERPRETERS_CACHE = None
      apps = ClusterConfig(user=user).get_apps()
      assert 'hive' not in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'impala' in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'pig' in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'solr' in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'spark' not in apps.get('editor', {}).get('interpreter_names', []), apps

    if 'spark' not in desktop.conf.APP_BLACKLIST.get():
      grant_access(USERNAME, GROUPNAME, "spark")
      check_app(401, 'hive')
      check_app(200, 'impala')
      check_app(401, 'hbase')
      check_app(200, 'pig')
      check_app(200, 'search')
      check_app(200, 'spark')
      check_app(200, 'oozie')

      notebook.conf.INTERPRETERS_CACHE = None
      apps = ClusterConfig(user=user).get_apps()
      assert 'hive' not in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'impala' in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'pig' in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'solr' in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'spark' in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'pyspark' in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'r' in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'jar' in apps.get('editor', {}).get('interpreter_names', []), apps
      assert 'py' in apps.get('editor', {}).get('interpreter_names', []), apps

  finally:
    for f in resets:
      f()
    notebook.conf.INTERPRETERS_CACHE = None


@pytest.mark.django_db
def test_error_handling_failure():
  # Change rewrite_user to call has_hue_permission
  # Try to get logs page
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
    with pytest.raises(AttributeError):
      c.get(reverse('desktop.views.log_view'))
  finally:
    # Restore the world
    restore_django_debug()
    restore_500_debug()
    desktop.auth.backend.rewrite_user = original_rewrite_user


@pytest.mark.django_db
def test_404_handling():
  pytest.skip("Skipping due to failures with pytest, investigation ongoing.")
  view_name = '/the-view-that-is-not-there'
  c = make_logged_in_client()
  response = c.get(view_name)
  assert any(['404.mako' in _template.filename for _template in response.templates]), response.templates
  assert b'not found' in response.content
  if not isinstance(view_name, bytes):
    view_name = view_name.encode('utf-8')
  assert view_name in response.content


class RecordingHandler(logging.Handler):
  def __init__(self, *args, **kwargs):
    logging.Handler.__init__(self, *args, **kwargs)
    self.records = []

  def emit(self, r):
    self.records.append(r)


@pytest.mark.django_db
def test_log_event():
  c = make_logged_in_client()
  root = logging.getLogger("desktop.views.log_frontend_event")
  handler = RecordingHandler()
  root.addHandler(handler)

  c.get("/desktop/log_frontend_event?level=info&message=foo")
  assert "INFO" == handler.records[-1].levelname
  assert "Untrusted log event from user test: foo" == handler.records[-1].message
  assert "desktop.views.log_frontend_event" == handler.records[-1].name

  c.get("/desktop/log_frontend_event?level=error&message=foo2")
  assert "ERROR" == handler.records[-1].levelname
  assert "Untrusted log event from user test: foo2" == handler.records[-1].message

  c.get("/desktop/log_frontend_event?message=foo3")
  assert "INFO" == handler.records[-1].levelname
  assert "Untrusted log event from user test: foo3" == handler.records[-1].message

  c.post("/desktop/log_frontend_event", {"message": "01234567" * 1024})
  assert "INFO" == handler.records[-1].levelname
  assert "Untrusted log event from user test: " == handler.records[-1].message

  root.removeHandler(handler)


def test_validate_path():
  with tempfile.NamedTemporaryFile() as local_file:
    reset = desktop.conf.SSL_PRIVATE_KEY.set_for_testing(local_file.name)
    assert [] == validate_path(desktop.conf.SSL_PRIVATE_KEY, is_dir=False)
    reset()

  try:
    reset = desktop.conf.SSL_PRIVATE_KEY.set_for_testing('/tmm/does_not_exist')
    assert [] != validate_path(desktop.conf.SSL_PRIVATE_KEY, is_dir=True)
    assert False
  except Exception as ex:
    assert 'does not exist' in str(ex), ex
  finally:
    reset()


@pytest.mark.integration
@pytest.mark.requires_hadoop
@pytest.mark.django_db
def test_config_check():
  with tempfile.NamedTemporaryFile() as cert_file:
    with tempfile.NamedTemporaryFile() as key_file:
      reset = (
        desktop.conf.SECRET_KEY.set_for_testing(''),
        desktop.conf.SECRET_KEY_SCRIPT.set_for_testing(present=False),
        desktop.conf.SSL_CERTIFICATE.set_for_testing(cert_file.name),
        desktop.conf.SSL_PRIVATE_KEY.set_for_testing(key_file.name),
        desktop.conf.DEFAULT_SITE_ENCODING.set_for_testing('klingon'),
      )

      cli = make_logged_in_client()
      try:
        resp = cli.get('/desktop/debug/check_config')
        assert 'Secret key should be configured' in resp.content, resp
        assert 'klingon' in resp.content, resp
        assert 'Encoding not supported' in resp.content, resp
      finally:
        for old_conf in reset:
          old_conf()

      prev_env_conf = os.environ.get("HUE_CONF_DIR")
      try:
        # Set HUE_CONF_DIR and make sure check_config returns appropriate conf
        os.environ["HUE_CONF_DIR"] = "/tmp/test_hue_conf_dir"

        def validate_by_spec(error_list):
          pass

        # Monkey patch as this will fail as the conf dir doesn't exist
        if not hasattr(desktop.views, 'real_validate_by_spec'):
          desktop.views.real_validate_by_spec = desktop.views.validate_by_spec

        desktop.views.validate_by_spec = validate_by_spec
        resp = cli.get('/desktop/debug/check_config')
        assert '/tmp/test_hue_conf_dir' in resp.content, resp
      finally:
        if prev_env_conf is None:
          os.environ.pop("HUE_CONF_DIR", None)
        else:
          os.environ["HUE_CONF_DIR"] = prev_env_conf
        desktop.views.validate_by_spec = desktop.views.real_validate_by_spec


def test_last_access_time():
  pytest.skip("Skipping Test")

  c = make_logged_in_client(username="access_test")
  c.post('/hue/accounts/login/')
  login = desktop.auth.views.get_current_users()
  before_access_time = time.time()
  response = c.get('/home')
  after_access_time = time.time()
  access = desktop.auth.views.get_current_users()

  user = response.context[0]['user']
  login_time = login[user]['time']
  access_time = access[user]['time']

  # Check that 'last_access_time' is later than login time
  assert login_time < access_time
  # Check that 'last_access_time' is in between the timestamps before and after the last access path
  assert before_access_time < access_time
  assert access_time < after_access_time


@pytest.mark.django_db
def test_ui_customizations():
  if desktop.conf.is_lb_enabled():  # Assumed that live cluster connects to direct Hue
    custom_message = 'You are accessing a non-optimized Hue, please switch to one of the available addresses'
  else:
    custom_message = 'test ui customization'
  reset = (
    desktop.conf.CUSTOM.BANNER_TOP_HTML.set_for_testing(custom_message),
    desktop.conf.CUSTOM.LOGIN_SPLASH_HTML.set_for_testing(custom_message),
  )

  try:
    c = make_logged_in_client()
    c.logout()
    if not isinstance(custom_message, bytes):
      custom_message = custom_message.encode('utf-8')
    resp = c.get('/hue/accounts/login/', follow=False)
    assert custom_message in resp.content, resp
    resp = c.get('/hue/about', follow=True)
    assert custom_message in resp.content, resp
  finally:
    for old_conf in reset:
      old_conf()


@pytest.mark.integration
@pytest.mark.requires_hadoop
@pytest.mark.django_db
def test_check_config_ajax():
  c = make_logged_in_client()
  response = c.get(reverse(check_config))
  content = response.content.decode('utf-8')
  assert "misconfiguration" in response.content, response.content


def test_cx_Oracle():
  """
  Tests that cx_Oracle (external dependency) is built correctly.
  """
  if 'ORACLE_HOME' not in os.environ and 'ORACLE_INSTANTCLIENT_HOME' not in os.environ:
    pytest.skip("Skipping Test")

  try:
    import cx_Oracle

    return
  except ImportError as ex:
    if "No module named" in ex.message:
      assert (
        False,
        "cx_Oracle skipped its build. This happens if "
        "env var ORACLE_HOME or ORACLE_INSTANTCLIENT_HOME is not defined. "
        "So ignore this test failure if your build does not need to work "
        "with an oracle backend.",
      )


@pytest.mark.django_db
class TestStrictRedirection(object):
  def setup_method(self):
    self.finish = desktop.conf.AUTH.BACKEND.set_for_testing(['desktop.auth.backend.AllowFirstUserDjangoBackend'])
    self.client = make_logged_in_client()
    self.user = dict(username="test", password="test")
    desktop.conf.REDIRECT_WHITELIST.set_for_testing(r'^\/.*$,^http:\/\/example.com\/.*$')

  def teardown_method(self):
    self.finish()

  def test_redirection_blocked(self):
    # Redirection with code 301 should be handled properly
    # Redirection with Status code 301 example reference: http://www.somacon.com/p145.php
    self._test_redirection(redirection_url='http://www.somacon.com/color/html_css_table_border_styles.php', expected_status_code=403)
    # Redirection with code 302 should be handled properly
    self._test_redirection(redirection_url='http://www.google.com', expected_status_code=403)

  def test_redirection_allowed(self):
    # Redirection to the host where Hue is running should be OK.
    self._test_redirection(redirection_url='/', expected_status_code=302)
    self._test_redirection(redirection_url='/pig', expected_status_code=302)
    self._test_redirection(redirection_url='http://testserver/', expected_status_code=302)
    self._test_redirection(
      redirection_url='https://testserver/',
      expected_status_code=302,
      **{
        'SERVER_PORT': '443',
        'wsgi.url_scheme': 'https',
      },
    )
    self._test_redirection(redirection_url='http://example.com/', expected_status_code=302)

  def _test_redirection(self, redirection_url, expected_status_code, **kwargs):
    data = self.user.copy()
    data['next'] = redirection_url
    response = self.client.post('/hue/accounts/login/', data, **kwargs)
    assert expected_status_code == response.status_code
    if expected_status_code == 403:
      error_msg = 'Redirect to ' + redirection_url + ' is not allowed.'
      if not isinstance(error_msg, bytes):
        error_msg = error_msg.encode('utf-8')
      assert error_msg in response.content, response.content


class BaseTestPasswordConfig(object):
  SCRIPT = '%s -c "print(\'\\n password from script \\n\')"' % sys.executable

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
      assert self.get_password() == ' password from script ', 'pwd: %s, kwargs: %s' % (self.get_password(), kwargs)
    finally:
      for reset in resets:
        reset()

  def test_config_password_overrides_script_password(self):
    resets = [
      self.get_config_password().set_for_testing(' password from config '),
      self.get_config_password_script().set_for_testing(self.SCRIPT),
    ]

    try:
      assert self.get_password() == ' password from config '
    finally:
      for reset in resets:
        reset()

  def test_password_script_raises_exception(self):
    resets = [
      self.get_config_password().set_for_testing(present=False),
      self.get_config_password_script().set_for_testing('%s -c "import sys; sys.exit(1)"' % sys.executable),
    ]

    try:
      with pytest.raises(subprocess.CalledProcessError):
        self.get_password()
    finally:
      for reset in resets:
        reset()

    resets = [
      self.get_config_password().set_for_testing(present=False),
      self.get_config_password_script().set_for_testing('/does-not-exist'),
    ]

    try:
      with pytest.raises(subprocess.CalledProcessError):
        self.get_password()
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


@pytest.mark.django_db
class TestLDAPBindPasswordConfig(BaseTestPasswordConfig):
  def setup_method(self):
    self.finish = desktop.conf.LDAP.LDAP_SERVERS.set_for_testing({'test': {}})

  def teardown_method(self):
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


@pytest.mark.django_db
class TestDocument(object):
  def setup_method(self):
    make_logged_in_client(username="original_owner", groupname="test_doc", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="original_owner")

    make_logged_in_client(username="copy_owner", groupname="test_doc", recreate=True, is_superuser=False)
    self.copy_user = User.objects.get(username="copy_owner")

    self.document2 = Document2.objects.create(name='Test Document2', type='search-dashboard', owner=self.user, description='Test Document2')

    self.document = Document.objects.link(
      content_object=self.document2, owner=self.user, name='Test Document', description='Test Document', extra='test'
    )

    self.document.save()
    self.document2.doc.add(self.document)

  def teardown_method(self):
    # Get any Doc2 objects that were created and delete them, Doc1 child objects will be deleted in turn
    test_docs = Document2.objects.filter(name__contains='Test Document2')
    test_docs.delete()

  def test_document_create(self):
    assert Document2.objects.filter(name='Test Document2').exists()
    assert Document.objects.filter(name='Test Document').exists()
    assert Document2.objects.get(name='Test Document2').id == self.document2.id
    assert Document.objects.get(name='Test Document').id == self.document.id

  def test_document_trashed_and_restore(self):
    home_dir = Directory.objects.get_home_directory(self.user)
    test_dir, created = Directory.objects.get_or_create(parent_directory=home_dir, owner=self.user, name='test_dir')
    test_doc = Document2.objects.create(
      name='Test Document2', type='search-dashboard', owner=self.user, description='Test Document2', parent_directory=test_dir
    )

    child_dir, created = Directory.objects.get_or_create(parent_directory=test_dir, owner=self.user, name='child_dir')
    test_doc1 = Document2.objects.create(
      name='Test Document2', type='search-dashboard', owner=self.user, description='Test Document2', parent_directory=child_dir
    )

    assert not test_dir.is_trashed
    assert not test_doc.is_trashed
    assert not child_dir.is_trashed
    assert not test_doc1.is_trashed

    try:
      test_dir.trash()
      test_dir = Document2.objects.get(id=test_dir.id)
      test_doc = Document2.objects.get(id=test_doc.id)
      child_dir = Document2.objects.get(id=child_dir.id)
      test_doc1 = Document2.objects.get(id=test_doc1.id)
      assert test_doc.is_trashed
      assert test_dir.is_trashed
      assert child_dir.is_trashed
      assert test_doc1.is_trashed

      # Test restore
      test_dir.restore()
      test_dir = Document2.objects.get(id=test_dir.id)
      test_doc = Document2.objects.get(id=test_doc.id)
      child_dir = Document2.objects.get(id=child_dir.id)
      test_doc1 = Document2.objects.get(id=test_doc1.id)
      assert not test_doc.is_trashed
      assert not test_dir.is_trashed
      assert not child_dir.is_trashed
      assert not test_doc1.is_trashed
    finally:
      test_doc.delete()
      test_dir.delete()
      test_doc1.delete()
      child_dir.delete()

  def test_multiple_home_directories(self):
    home_dir = Directory.objects.get_home_directory(self.user)
    test_doc1 = Document2.objects.create(name='test-doc1', type='query-hive', owner=self.user, description='', parent_directory=home_dir)

    assert home_dir.children.exclude(name__in=['.Trash', 'Gist']).count() == 2

    # Cannot create second home directory directly as it will fail in Document2.validate()
    second_home_dir = Document2.objects.create(owner=self.user, parent_directory=None, name='second_home_dir', type='directory')
    Document2.objects.filter(name='second_home_dir').update(name=Document2.HOME_DIR, parent_directory=None)
    assert Document2.objects.filter(owner=self.user, name=Document2.HOME_DIR).count() == 2

    test_doc2 = Document2.objects.create(
      name='test-doc2', type='query-hive', owner=self.user, description='', parent_directory=second_home_dir
    )
    assert second_home_dir.children.count() == 1

    merged_home_dir = Directory.objects.get_home_directory(self.user)
    children = merged_home_dir.children.all()
    assert children.exclude(name__in=['.Trash', 'Gist']).count() == 3
    children_names = [child.name for child in children]
    assert test_doc2.name in children_names
    assert test_doc1.name in children_names

  def test_multiple_trash_directories(self):
    home_dir = Directory.objects.get_home_directory(self.user)
    test_doc1 = Document2.objects.create(name='test-doc1', type='query-hive', owner=self.user, description='', parent_directory=home_dir)

    assert home_dir.children.count() == 3

    # Cannot create second trash directory directly as it will fail in Document2.validate()
    Document2.objects.create(owner=self.user, parent_directory=home_dir, name='second_trash_dir', type='directory')
    Document2.objects.filter(name='second_trash_dir').update(name=Document2.TRASH_DIR)
    assert Directory.objects.filter(owner=self.user, name=Document2.TRASH_DIR).count() == 2

    test_doc2 = Document2.objects.create(name='test-doc2', type='query-hive', owner=self.user, description='', parent_directory=home_dir)
    assert home_dir.children.count() == 5  # Including the second trash
    with pytest.raises(Document2.MultipleObjectsReturned):
      Directory.objects.get(name=Document2.TRASH_DIR)

    test_doc1.trash()
    assert home_dir.children.count() == 3  # As trash documents are merged count is back to 3
    merged_trash_dir = Directory.objects.get(name=Document2.TRASH_DIR, owner=self.user)

    test_doc2.trash()
    children = merged_trash_dir.children.all()
    assert children.count() == 2
    children_names = [child.name for child in children]
    assert test_doc2.name in children_names
    assert test_doc1.name in children_names

  def test_document_copy(self):
    pytest.skip("Skipping Test")
    name = 'Test Document2 Copy'

    self.doc2_count = Document2.objects.count()
    self.doc1_count = Document.objects.count()

    doc2 = self.document2.copy(name=name, owner=self.copy_user, description=self.document2.description)
    doc = self.document.copy(doc2, name=name, owner=self.copy_user, description=self.document2.description)

    # Test that copying creates another object
    assert Document2.objects.count() == self.doc2_count + 1
    assert Document.objects.count() == self.doc1_count

    # Test that the content object is not pointing to the same object
    assert self.document2.doc != doc2.doc

    # Test that the owner is attributed to the new user
    assert doc2.owner == self.copy_user

    # Test that copying enables attribute overrides
    assert Document2.objects.filter(name=name).count() == 1
    assert doc2.description == self.document2.description

    # Test that the content object is not pointing to the same object
    assert self.document.content_object != doc.content_object

    # Test that the owner is attributed to the new user
    assert doc.owner == self.copy_user

    # Test that copying enables attribute overrides
    assert Document.objects.filter(name=name).count() == 1
    assert doc.description == self.document.description

  def test_redact_statements(self):
    old_policies = redaction.global_redaction_engine.policies
    redaction.global_redaction_engine.policies = [
      RedactionPolicy(
        [
          RedactionRule('', r'ssn=\d{3}-\d{2}-\d{4}', 'ssn=XXX-XX-XXXX'),
        ]
      )
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
          'aceMode': 'ace/mode/hive',
        },
        'id': '10a29cda-063f-1439-4836-d0c460154075',
        'statement_raw': sensitive_query,
        'statement': sensitive_query,
        'type': 'hive',
      },
      {
        'status': 'ready',
        'viewSettings': {
          'sqlDialect': True,
          'snippetImage': '/static/impala/art/icon_impala_48.png',
          'placeHolder': 'Example: SELECT * FROM tablename, or press CTRL + space',
          'aceMode': 'ace/mode/impala',
        },
        'id': 'e17d195a-beb5-76bf-7489-a9896eeda67a',
        'statement_raw': sensitive_query,
        'statement': sensitive_query,
        'type': 'impala',
      },
      {
        'status': 'ready',
        'viewSettings': {
          'sqlDialect': True,
          'snippetImage': '/static/beeswax/art/icon_beeswax_48.png',
          'placeHolder': 'Example: SELECT * FROM tablename, or press CTRL + space',
          'aceMode': 'ace/mode/hive',
        },
        'id': '10a29cda-063f-1439-4836-d0c460154075',
        'statement_raw': nonsensitive_query,
        'statement': nonsensitive_query,
        'type': 'hive',
      },
    ]

    try:
      self.document2.type = 'notebook'
      self.document2.update_data({'snippets': snippets})
      self.document2.search = sensitive_query
      self.document2.save()
      saved_snippets = self.document2.data_dict['snippets']

      # Make sure redacted queries are redacted.
      assert redacted_query == saved_snippets[0]['statement']
      assert redacted_query == saved_snippets[0]['statement_raw']
      assert True is saved_snippets[0]['is_redacted']

      assert redacted_query == saved_snippets[1]['statement']
      assert redacted_query == saved_snippets[1]['statement_raw']
      assert True is saved_snippets[1]['is_redacted']

      document = Document2.objects.get(pk=self.document2.pk)
      assert redacted_query == document.search

      # Make sure unredacted queries are not redacted.
      assert nonsensitive_query == saved_snippets[2]['statement']
      assert nonsensitive_query == saved_snippets[2]['statement_raw']
      assert 'is_redacted' not in saved_snippets[2]
    finally:
      redaction.global_redaction_engine.policies = old_policies

  def test_get_document(self):
    c1 = make_logged_in_client(username='test_get_user', groupname='test_get_group', recreate=True, is_superuser=False)
    r1 = c1.get('/desktop/api/doc/get?id=1')
    assert -1, json.loads(r1.content)['status']


def test_session_secure_cookie():
  with tempfile.NamedTemporaryFile() as cert_file:
    with tempfile.NamedTemporaryFile() as key_file:
      resets = [
        desktop.conf.SSL_CERTIFICATE.set_for_testing(cert_file.name),
        desktop.conf.SSL_PRIVATE_KEY.set_for_testing(key_file.name),
        desktop.conf.SESSION.SECURE.set_for_testing(False),
      ]
      try:
        assert desktop.conf.is_https_enabled()
        assert not desktop.conf.SESSION.SECURE.get()
      finally:
        for reset in resets:
          reset()

      resets = [
        desktop.conf.SSL_CERTIFICATE.set_for_testing(cert_file.name),
        desktop.conf.SSL_PRIVATE_KEY.set_for_testing(key_file.name),
        desktop.conf.SESSION.SECURE.set_for_testing(True),
      ]
      try:
        assert desktop.conf.is_https_enabled()
        assert desktop.conf.SESSION.SECURE.get()
      finally:
        for reset in resets:
          reset()

      resets = [
        desktop.conf.SSL_CERTIFICATE.set_for_testing(cert_file.name),
        desktop.conf.SSL_PRIVATE_KEY.set_for_testing(key_file.name),
        desktop.conf.SESSION.SECURE.set_for_testing(present=False),
      ]
      try:
        assert desktop.conf.is_https_enabled()
        assert desktop.conf.SESSION.SECURE.get()
      finally:
        for reset in resets:
          reset()

      resets = [
        desktop.conf.SSL_CERTIFICATE.set_for_testing(present=None),
        desktop.conf.SSL_PRIVATE_KEY.set_for_testing(present=None),
        desktop.conf.SESSION.SECURE.set_for_testing(present=False),
      ]
      try:
        assert not desktop.conf.is_https_enabled()
        assert not desktop.conf.SESSION.SECURE.get()
      finally:
        for reset in resets:
          reset()


def test_get_data_link():
  assert None is get_data_link({})
  assert 'gethue.com' == get_data_link({'type': 'link', 'link': 'gethue.com'})

  assert '/hbase/#Cluster/document_demo/query/20150527' == get_data_link({'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527'})
  assert '/hbase/#Cluster/document_demo/query/20150527[f1]' == get_data_link(
    {'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1'}
  )
  assert '/hbase/#Cluster/document_demo/query/20150527[f1:c1]' == get_data_link(
    {'type': 'hbase', 'table': 'document_demo', 'row_key': '20150527', 'fam': 'f1', 'col': 'c1'}
  )

  assert '/filebrowser/view=/data/hue/1' == get_data_link({'type': 'hdfs', 'path': '/data/hue/1'})
  assert '/metastore/table/default/sample_07' == get_data_link({'type': 'hive', 'database': 'default', 'table': 'sample_07'})


def test_get_dn():
  assert ['*'] == desktop.conf.get_dn('')
  assert ['*'] == desktop.conf.get_dn('localhost')
  assert ['*'] == desktop.conf.get_dn('localhost.localdomain')
  assert ['*'] == desktop.conf.get_dn('hue')
  assert ['*'] == desktop.conf.get_dn('hue.com')
  assert ['.hue.com'] == desktop.conf.get_dn('sql.hue.com')
  assert ['.hue.com'] == desktop.conf.get_dn('finance.sql.hue.com')
  assert ['.hue.com'] == desktop.conf.get_dn('bank.finance.sql.hue.com')


def test_collect_validation_messages_default():
  try:
    # Generate the spec file
    configspec = generate_configspec()
    # Load the .ini files
    config_dir = os.getenv("HUE_CONF_DIR", get_desktop_root("conf"))
    conf = load_confs(configspec.name, _configs_from_dir(config_dir))
    # This is for the hue.ini file only
    error_list = []
    collect_validation_messages(conf, error_list)
    assert len(error_list) == 0, error_list
  finally:
    os.remove(configspec.name)


def test_collect_validation_messages_extras():
  try:
    # Generate the spec file
    configspec = generate_configspec()
    # Load the .ini files
    config_dir = os.getenv("HUE_CONF_DIR", get_desktop_root("conf"))
    conf = load_confs(configspec.name, _configs_from_dir(config_dir))

    test_conf = ConfigObj()
    test_conf['extrasection'] = {'key1': 'value1', 'key2': 'value1'}
    extrasubsection = {'key1': 'value1', 'key2': 'value1'}
    # Test with extrasections as well as existing subsection, keyvalues in existing section [desktop]
    test_conf['desktop'] = {
      'extrasubsection': extrasubsection,
      'extrakey': 'value1',
      'auth': {'ignore_username_case': 'true', 'extrasubsubsection': {'extrakey': 'value1'}},
    }
    conf.merge(test_conf)
    error_list = []
    collect_validation_messages(conf, error_list)
  finally:
    os.remove(configspec.name)
  assert len(error_list) == 1
  assert (
    'Extra section, extrasection in the section: top level, Extra keyvalue, extrakey in the section: [desktop] , '
    'Extra section, extrasubsection in the section: [desktop] , Extra section, extrasubsubsection in the section: [desktop] [[auth]] '
    == error_list[0]['message']
  )


# Test db migration from 5.7,...,5.15 to latest
@pytest.mark.django_db
def test_db_migrations_sqlite():
  versions = ['5.' + str(i) for i in range(7, 16)]
  for version in versions:
    name = 'hue_' + version + '_' + uuid.uuid4().hex
    file_name = 'hue_' + version + '.db'
    path = get_desktop_root('./core/src/desktop/test_data/' + file_name)
    DATABASES[name] = {
      'ENGINE': 'django.db.backends.sqlite3',
      'NAME': path,
      'USER': '',
      'SCHEMA': 'public',
      'PASSWORD': '',
      'HOST': '',
      'PORT': '',
      'OPTIONS': {} if sys.version_info[0] > 2 else '',
      'ATOMIC_REQUESTS': True,
      'CONN_MAX_AGE': 0,
    }
    try:
      call_command('migrate', '--fake-initial', '--database=' + name)
    finally:
      del DATABASES[name]


def test_db_migrations_mysql():
  if desktop.conf.DATABASE.ENGINE.get().find('mysql') < 0:
    pytest.skip("Skipping Test")
  versions = ['5_' + str(i) for i in range(7, 16)]
  os.putenv('PATH', '$PATH:/usr/local/bin')
  try:
    subprocess.check_output('type mysql', shell=True)
  except subprocess.CalledProcessError as e:
    LOG.warning('mysql not found')
    pytest.skip("Skipping Test")
  for version in versions:
    file_name = 'hue_' + version + '_mysql.sql'
    name = 'hue_' + version + '_' + uuid.uuid4().hex
    path = get_desktop_root('./core/src/desktop/test_data/' + file_name)
    DATABASES[name] = {
      'ENGINE': desktop.conf.DATABASE.ENGINE.get(),
      'NAME': name,
      'USER': desktop.conf.DATABASE.USER.get(),
      'SCHEMA': name,
      'PASSWORD': desktop.conf.get_database_password(),
      'HOST': desktop.conf.DATABASE.HOST.get(),
      'PORT': str(desktop.conf.DATABASE.PORT.get()),
      'OPTIONS': force_dict_to_strings(desktop.conf.DATABASE.OPTIONS.get()),
      'ATOMIC_REQUESTS': True,
      'PATH': path,
      'CONN_MAX_AGE': desktop.conf.DATABASE.CONN_MAX_AGE.get(),
    }
    try:
      subprocess.check_output(
        'mysql -u%(USER)s -p%(PASSWORD)s -e "CREATE DATABASE %(SCHEMA)s"' % DATABASES[name], stderr=subprocess.STDOUT, shell=True
      )  # No way to run this command with django
      subprocess.check_output(
        'mysql -u%(USER)s -p%(PASSWORD)s %(SCHEMA)s < %(PATH)s' % DATABASES[name], stderr=subprocess.STDOUT, shell=True
      )
      call_command('migrate', '--fake-initial', '--database=%(SCHEMA)s' % DATABASES[name])
    except subprocess.CalledProcessError as e:
      LOG.warning('stderr: {}'.format(e.output))
      raise e
    finally:
      del DATABASES[name]


# @raises(ImportError)
def test_forbidden_libs():
  if sys.version_info[0] > 2:
    pytest.skip("Skipping Test")
  import chardet  # chardet license (LGPL) is not compatible and should not be bundled


@pytest.mark.django_db
class TestGetConfigErrors:
  def setup_method(self):
    self.client = make_logged_in_client(username="test", groupname="empty", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")

  def test_get_config_errors_unicode(self):
    """
    Avoid a Python 2 issue:
    AttributeError: 'unicode' object has no attribute 'get_fully_qualifying_key'
    """
    request = Mock(user=self.user)

    with patch('desktop.views.appmanager') as appmanager:
      appmanager.DESKTOP_MODULES = [Mock(conf=Mock(config_validator=lambda user: [('Connector 1', 'errored because of ...')]))]
      assert [{'name': 'Connector 1', 'message': 'errored because of ...'}] == _get_config_errors(request, cache=False)
