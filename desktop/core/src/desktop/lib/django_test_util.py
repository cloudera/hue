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

import re
import json
from unittest.mock import Mock

import django.test.client

from desktop.conf import ENABLE_ORGANIZATIONS
from useradmin.models import Group, User


class Client(django.test.client.Client):
  """
  Extends client to have a get_json method.
  """

  def get_json(self, *args, **kwargs):
    response = self.get(*args, **kwargs)
    return json.JSONDecoder().decode(response.content)


def make_logged_in_client(
  username="test", password="test", is_superuser=True, recreate=False, groupname=None, is_admin=False, request=None
):
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


_MULTI_WHITESPACE = re.compile(r"\s+", flags=re.MULTILINE)


def compact_whitespace(s):
  """
  Replaces redundant whitespace from strings with a single space.
  Also removes leading and trailing whitespace.
  """
  return _MULTI_WHITESPACE.sub(" ", s).strip()


def assert_equal_mod_whitespace(first, second, msg=None):
  """
  Asserts that two strings are equal, ignoring whitespace.
  """
  assert compact_whitespace(first) == compact_whitespace(second), msg


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
  """Create all tables for the given model.

  This is a subset of django.core.management.commands.migrate
  """
  from django.db import connection
  from django.db.models import Model

  with connection.schema_editor() as editor:
    editor.create_model(model)
