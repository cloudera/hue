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

import pytest
from django.test import TestCase

from desktop.conf import GC_ACCOUNTS, RAZ, is_gs_enabled
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.fs.gc.gs import get_gs_home_directory
from desktop.lib.fsmanager import get_client
from filebrowser.conf import REMOTE_STORAGE_HOME
from useradmin.models import User

LOG = logging.getLogger()


@pytest.mark.django_db
def test_get_gs_home_directory():
  client = make_logged_in_client(username="test", groupname="test", recreate=True, is_superuser=False)
  user = User.objects.get(username="test")

  client_not_me = make_logged_in_client(username="test_not_me", groupname="test_not_me", recreate=True, is_superuser=False)
  user_not_me = User.objects.get(username="test_not_me")

  # When REMOTE_STORAGE_HOME ends with /user in RAZ GS environment.
  resets = [RAZ.IS_ENABLED.set_for_testing(True), REMOTE_STORAGE_HOME.set_for_testing('gs://gethue-bucket/user')]

  try:
    default_gs_home_path = get_gs_home_directory(user)
    assert default_gs_home_path == 'gs://gethue-bucket/user/test'

    default_gs_home_path = get_gs_home_directory(user_not_me)
    assert default_gs_home_path == 'gs://gethue-bucket/user/test_not_me'
  finally:
    for reset in resets:
      reset()

  # When GS filesystem's DEFAULT_HOME_PATH ends with /user in RAZ GS environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    GC_ACCOUNTS.set_for_testing({'default': {'default_home_path': 'gs://gethue-other-bucket/user'}}),
  ]

  try:
    default_gs_home_path = get_gs_home_directory(user)
    assert default_gs_home_path == 'gs://gethue-other-bucket/user/test'

    default_gs_home_path = get_gs_home_directory(user_not_me)
    assert default_gs_home_path == 'gs://gethue-other-bucket/user/test_not_me'
  finally:
    for reset in resets:
      reset()

  # When GS filesystem's DEFAULT_HOME_PATH is set in non-RAZ GS environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(False),
    GC_ACCOUNTS.set_for_testing({'default': {'default_home_path': 'gs://gethue-other-bucket/test-dir'}}),
  ]

  try:
    default_gs_home_path = get_gs_home_directory(user)
    assert default_gs_home_path == 'gs://gethue-other-bucket/test-dir'

    default_gs_home_path = get_gs_home_directory(user_not_me)
    assert default_gs_home_path == 'gs://gethue-other-bucket/test-dir'
  finally:
    for reset in resets:
      reset()

  # When both REMOTE_STORAGE_HOME and GS filesystem's DEFAULT_HOME_PATH are set in RAZ GS environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    REMOTE_STORAGE_HOME.set_for_testing('gs://gethue-bucket/user'),
    GC_ACCOUNTS.set_for_testing({'default': {'default_home_path': 'gs://gethue-other-bucket/user'}}),
  ]

  try:
    # Gives preference to REMOTE_STORAGE_HOME for of backward compatibility.
    default_gs_home_path = get_gs_home_directory(user)
    assert default_gs_home_path == 'gs://gethue-bucket/user/test'

    default_gs_home_path = get_gs_home_directory(user_not_me)
    assert default_gs_home_path == 'gs://gethue-bucket/user/test_not_me'
  finally:
    for reset in resets:
      reset()

  # When GS filesystem's DEFAULT_HOME_PATH is set but path does not end with ../user or ../user/ in RAZ GS environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    GC_ACCOUNTS.set_for_testing({'default': {'default_home_path': 'gs://gethue-other-bucket/dir'}}),
  ]

  try:
    default_gs_home_path = get_gs_home_directory(user)
    assert default_gs_home_path == 'gs://gethue-other-bucket/dir'

    default_gs_home_path = get_gs_home_directory(user_not_me)
    assert default_gs_home_path == 'gs://gethue-other-bucket/dir'
  finally:
    for reset in resets:
      reset()

  # When some different path is set in both RAZ and non-RAZ GS environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    REMOTE_STORAGE_HOME.set_for_testing('abfs://gethue-container/user'),
    GC_ACCOUNTS.set_for_testing({'default': {'default_home_path': 'abfs://gethue-other-container/dir'}}),
  ]

  try:
    default_gs_home_path = get_gs_home_directory(user)
    assert default_gs_home_path == 'gs://'

    default_gs_home_path = get_gs_home_directory(user_not_me)
    assert default_gs_home_path == 'gs://'
  finally:
    for reset in resets:
      reset()


class TestGCS(TestCase):
  def setup_method(self, method):
    if not is_gs_enabled():
      pytest.skip('gs not enabled')

  def test_with_credentials(self):
    # Simple test that makes sure no errors are thrown.
    client = get_client(fs='gs')
    buckets = client.listdir_stats('gs://')
    LOG.info(len(buckets))
