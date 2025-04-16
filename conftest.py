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

import pytest

from django.conf import settings
from desktop.lib import django_mako
from django.utils.translation import deactivate
from mako.template import Template
from types import SimpleNamespace


class _TestState(object):
  pass


@pytest.fixture(scope='session', autouse=True)
def setup_test_environment(debug=None):
  """
  Perform global pre-test setup, such as installing the instrumented template
  renderer and setting the email backend to the locmem email backend.
  """
  if hasattr(_TestState, 'saved_data'):
    # Executing this function twice would overwrite the saved values.
    raise RuntimeError(
        "setup_test_environment() was already called and can't be called "
        "again without first calling teardown_test_environment()."
    )

  if debug is None:
    debug = settings.DEBUG

  saved_data = SimpleNamespace()
  _TestState.saved_data = saved_data

  saved_data.allowed_hosts = settings.ALLOWED_HOSTS
  # Add the default host of the test client.
  settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']

  saved_data.debug = settings.DEBUG
  settings.DEBUG = debug

  django_mako.render_to_string = django_mako.render_to_string_test

  deactivate()

  yield
  teardown_test_environment()


def teardown_test_environment():
  # Teardown test environment
  """
  Perform any global post-test teardown, such as restoring the original
  template renderer and restoring the email sending functions.
  """
  saved_data = _TestState.saved_data

  settings.ALLOWED_HOSTS = saved_data.allowed_hosts
  settings.DEBUG = saved_data.debug
  django_mako.render_to_string = django_mako.render_to_string_normal

  del _TestState.saved_data
