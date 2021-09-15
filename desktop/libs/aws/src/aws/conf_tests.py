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
from __future__ import absolute_import

import logging
import sys
import unittest

from nose.tools import assert_equal, assert_true, assert_not_equal, assert_false

from aws import conf

from desktop.conf import RAZ
from desktop.lib.django_test_util import make_logged_in_client

from useradmin.models import User

if sys.version_info[0] > 2:
  from unittest.mock import patch
else:
  from mock import patch

LOG = logging.getLogger(__name__)

class TestAWSConf(unittest.TestCase):
  def setUp(self):
    self.client = make_logged_in_client(username="test_user", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test_user")


  def test_is_enabled(self):
    # When RAZ is not enabled
    assert_false(conf.is_enabled())

    # When only RAZ is enabled (S3 in Azure cluster)
    reset = RAZ.IS_ENABLED.set_for_testing(True)
    try:
      assert_false(conf.is_enabled())
    finally:
      reset()
      conf.clear_cache()

    # When RAZ is enabled along with S3 config
    resets = [
      RAZ.IS_ENABLED.set_for_testing(True),
      conf.AWS_ACCOUNTS.set_for_testing({'default': {
        'region': 'us-west-2',
        'host': 's3-us-west-2.amazonaws.com',
        'allow_environment_credentials': 'false'
      }})
    ]

    try:
      assert_true(conf.is_enabled())
    finally:
      for reset in resets:
        reset()
      conf.clear_cache()


  def test_has_s3_access(self):
    # When RAZ is not enabled
    assert_false(conf.has_s3_access(self.user))

    # When only RAZ is enabled (S3 in Azure cluster)
    reset = RAZ.IS_ENABLED.set_for_testing(True)
    try:
      assert_false(conf.has_s3_access(self.user))
    finally:
      reset()
      conf.clear_cache()

    # When RAZ is enabled along with S3 config
    resets = [
      RAZ.IS_ENABLED.set_for_testing(True),
      conf.AWS_ACCOUNTS.set_for_testing({'default': {
        'region': 'us-west-2',
        'host': 's3-us-west-2.amazonaws.com',
        'allow_environment_credentials': 'false'
      }})
    ]
    try:
      assert_true(conf.has_s3_access(self.user))
    finally:
      for reset in resets:
        reset()
      conf.clear_cache()


  def test_is_raz_s3(self):
    # When RAZ is not enabled
    assert_false(conf.is_raz_s3())

    # When only RAZ is enabled (S3 in Azure cluster)
    reset = RAZ.IS_ENABLED.set_for_testing(True)
    try:
      assert_false(conf.is_raz_s3())
    finally:
      reset()
      conf.clear_cache()

    # When RAZ is enabled along with S3 config
    resets = [
      RAZ.IS_ENABLED.set_for_testing(True),
      conf.AWS_ACCOUNTS.set_for_testing({'default': {
        'region': 'us-west-2',
        'host': 's3-us-west-2.amazonaws.com',
        'allow_environment_credentials': 'false'
      }})
    ]
    try:
      assert_true(conf.is_raz_s3())
    finally:
      for reset in resets:
        reset()
      conf.clear_cache()
