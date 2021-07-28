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

import logging
import re
import json
import sys

import django.test.client
import nose.tools

from useradmin.models import User, Group, Organization

from desktop.conf import ENABLE_ORGANIZATIONS

if sys.version_info[0] > 2:
  from unittest.mock import Mock
else:
  from mock import Mock


class Client(django.test.client.Client):
  """
  Extends client to have a get_json method.
  """
  def get_json(self, *args, **kwargs):
    response = self.get(*args, **kwargs)
    return json.JSONDecoder().decode(response.content)


def assert_ok_response(response):
  """
  Checks that the response returned successfully.

  Returns the response.
  """
  nose.tools.assert_true(200, response.status_code)
  return response


def make_logged_in_client(username="test", password="test", is_superuser=True, recreate=False, groupname=None, is_admin=False, request=None):
  """
  Create a client with a user already logged in.

  Sometimes we recreate the user, because some tests like to mess with is_active and such.
  Note: could be combined with backend.create_user and other standart utils.
  """
  request = Mock()
  try:
    user = User.objects.get(username=username)
    if recreate:
      user.delete()
      raise User.DoesNotExist
  except User.DoesNotExist:
    user = User.objects.create_user(username=username, password=password)
    user.is_superuser = is_superuser
    if ENABLE_ORGANIZATIONS.get():
      user.is_admin = is_admin
    else:
      user.is_superuser = user.is_superuser or is_admin
    user.save()
  else:
    if user.is_superuser != is_superuser:
      user.is_superuser = is_superuser
      user.save()

  if groupname is not None:
    attributes = {'name': groupname}

    if ENABLE_ORGANIZATIONS.get():
      attributes['organization'] = user.organization

    group, created = Group.objects.get_or_create(**attributes)
    if not user.groups.filter(**attributes).exists():
      user.groups.add(group)
      user.save()

  c = Client()
  ret = c.login(username=username, password=password, request=request)

  assert ret, "Login failed (user '%s')." % username
  return c


_MULTI_WHITESPACE = re.compile("\s+", flags=re.MULTILINE)

def compact_whitespace(s):
  """
  Replaces redundant whitespace from strings with a single space.
  Also removes leading and trailing whitespce.
  """
  return _MULTI_WHITESPACE.sub(" ", s).strip()

def assert_equal_mod_whitespace(first, second, msg=None):
  """
  Asserts that two strings are equal, ignoring whitespace.
  """
  nose.tools.assert_equal(compact_whitespace(first),
    compact_whitespace(second), msg)

def assert_similar_pages(first, second, ratio=0.9, msg=None):
  """
  Asserts that most of the lines (90% by default) in the two pages are identical,
  ignoring leading/trailing spaces.
  """
  lines_a = set([l.strip() for l in first.split('\n')])
  lines_b = set([l.strip() for l in second.split('\n')])
  common = lines_a.intersection(lines_b)
  similarity = 1.0 * len(common) / max(len(lines_a), len(lines_b))
  nose.tools.assert_true(similarity >= ratio, msg)


def configure_django_for_test():
  from django.conf import settings

  # Django's test runner has already done this typically.
  if settings.configured:
    return

  # This must be run before importing models
  # Be sure not to include any INSTALLED_APPS, since then the models
  # code will try very hard to load it.
  settings.configure(DATABASE_ENGINE="sqlite3", DATABASE_NAME=":memory:", INSTALLED_APPS=())


def create_tables(model):
  """ Create all tables for the given model.

  This is a subset of django.core.management.commands.migrate
  """
  from django.db import connection
  from django.db.models import Model

  with connection.schema_editor() as editor:
    editor.create_model(model)
