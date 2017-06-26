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

from boto.s3.connection import Location
from nose.tools import assert_equal, assert_raises, eq_

from aws import s3
from aws import conf
from aws.conf import get_default_region


def test_parse_uri():
  p = s3.parse_uri

  eq_(('bucket', 'folder/key', 'key'), p('s3a://bucket/folder/key'))
  eq_(('bucket', 'folder/key/', 'key'), p('s3a://bucket/folder/key/'))
  eq_(('bucket', 'folder/key/', 'key'), p('S3A://bucket/folder/key/'))
  eq_(('bucket', '', ''), p('s3a://bucket'))
  eq_(('bucket', '', ''), p('s3a://bucket/'))

  assert_raises(ValueError, p, '/local/path')
  assert_raises(ValueError, p, 'ftp://ancient/archive')
  assert_raises(ValueError, p, 's3a:/missed/slash')
  assert_raises(ValueError, p, 's3a://')


def test_join():
  j = s3.join
  eq_("s3a://b", j("s3a://", "b"))
  eq_("s3a://b/f", j("s3a://b", "f"))
  eq_("s3a://b/f1/f2", j("s3a://b", "f1", "f2"))
  eq_("s3a://b/f1/f2/../f3", j("s3a://b/f1/f2", "../f3"))


def test_abspath():
  a = s3.abspath
  eq_('s3a://a/b/c/d', a('s3a://a/b/c', 'd'))
  eq_('s3a://a/b/c/d', a('/a/b/c', 'd'))


def test_is_root():
  i = s3.is_root
  eq_(True, i('s3a://'))
  eq_(True, i('S3A://'))
  eq_(False, i('s3a:/'))
  eq_(False, i('s3a://bucket'))
  eq_(False, i('/local/path'))


def test_s3datetime_to_timestamp():
  f = s3.s3datetime_to_timestamp
  eq_(1424983327, f('Thu, 26 Feb 2015 20:42:07 GMT'))
  eq_(1424983327, f('2015-02-26T20:42:07.000Z'))

  assert_raises(ValueError, f, '2/26/2015 20:42:07')

  assert_raises(AssertionError, f, 'Thu, 26 Feb 2015 20:42:07 PDT')
  assert_raises(AssertionError, f, '2015-02-26T20:42:07.040Z')


def test_get_default_region():
  # Verify that Hue can infer region from subdomain hosts
  finish = conf.AWS_ACCOUNTS.set_for_testing({'default': {'host': 's3.ap-northeast-2.amazonaws.com'}})
  try:
    assert_equal('ap-northeast-2', get_default_region())
  finally:
    if finish:
      finish()

  # Verify that Hue can infer region from hyphenated hosts
  finish = conf.AWS_ACCOUNTS.set_for_testing({'default': {'host': 's3-ap-south-1.amazonaws.com'}})
  try:
    assert_equal('ap-south-1', get_default_region())
  finally:
    if finish:
      finish()

  # Verify that Hue can infer region from hyphenated hosts
  finish = conf.AWS_ACCOUNTS.set_for_testing({'default': {'host': 's3.dualstack.ap-southeast-2.amazonaws.com'}})
  try:
    assert_equal('ap-southeast-2', get_default_region())
  finally:
    if finish:
      finish()

  # Verify that Hue falls back to the default if the region is not valid
  finish = conf.AWS_ACCOUNTS.set_for_testing({'default': {'host': 's3-external-1.amazonaws.com'}})
  try:
    assert_equal(Location.DEFAULT, get_default_region())
  finally:
    if finish:
      finish()

  # Verify that Hue uses the region if specified
  finish = conf.AWS_ACCOUNTS.set_for_testing({'default': {'host': '', 'region': 'ca-central-1'}})
  try:
    assert_equal('ca-central-1', get_default_region())
  finally:
    if finish:
      finish()
