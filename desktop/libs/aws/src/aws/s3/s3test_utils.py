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
import os
import random
import string
import unittest

from nose.plugins.skip import SkipTest

import aws

from contextlib import contextmanager

from aws.s3 import parse_uri, join


def get_test_bucket():
  return os.environ.get('TEST_S3_BUCKET', '')


def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for x in range(size))


class S3TestBase(unittest.TestCase):
  integration = True

  @classmethod
  def setUpClass(cls):
    cls.bucket_name = get_test_bucket()

    cls._should_skip = False
    if not cls.bucket_name:
      cls._should_skip = True
      cls._skip_msg = 'TEST_S3_BUCKET environment variable isn\'t set'
      return

    cls.path_prefix = 'test-hue/%s' % generate_id(size=16)
    cls.s3_connection = aws.get_client('default').get_s3_connection()
    cls.bucket = cls.s3_connection.get_bucket(cls.bucket_name, validate=True)

  @classmethod
  def shouldSkip(cls):
    return cls._should_skip

  def setUp(self):
    if self.shouldSkip():
      raise SkipTest(self._skip_msg)

  @classmethod
  def tearDownClass(cls):
    if not cls.shouldSkip():
      cls.clean_up(cls.get_test_path())

  @classmethod
  def get_test_path(cls, path=None):
    base_path = join('s3a://', cls.bucket_name, cls.path_prefix)
    if path:
      return join(base_path, path)
    return base_path

  @classmethod
  def get_key(cls, path, validate=False):
    bucket_name, key_name = parse_uri(path)[:2]
    bucket = cls.s3_connection.get_bucket(bucket_name)
    return bucket.get_key(key_name, validate=validate)

  @classmethod
  def clean_up(cls, *paths):
    for path in paths:
      key = cls.get_key(path, validate=False)
      try:
        listing = key.bucket.list(prefix=key.name)
        key.bucket.delete_keys(listing)
      except:
        pass

  @classmethod
  @contextmanager
  def cleaning(cls, *paths):
    try:
      yield paths
    finally:
      cls.clean_up(*paths)
