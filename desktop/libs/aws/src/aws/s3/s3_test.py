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

from nose.plugins.skip import SkipTest
from nose.tools import assert_raises, eq_

from aws import s3


def test_parse_uri():
  p = s3.parse_uri

  eq_(('bucket', 'folder/key', 'key'), p('s3://bucket/folder/key'))
  eq_(('bucket', 'folder/key/', 'key'), p('s3://bucket/folder/key/'))
  eq_(('bucket', 'folder/key/', 'key'), p('S3://bucket/folder/key/'))
  eq_(('bucket', '', ''), p('s3://bucket'))
  eq_(('bucket', '', ''), p('s3://bucket/'))

  assert_raises(ValueError, p, '/local/path')
  assert_raises(ValueError, p, 'ftp://ancient/archive')
  assert_raises(ValueError, p, 's3:/missed/slash')
  assert_raises(ValueError, p, 's3://')


def test_join():
  j = s3.join
  eq_("s3://b", j("s3://", "b"))
  eq_("s3://b/f", j("s3://b", "f"))
  eq_("s3://b/f1/f2", j("s3://b", "f1", "f2"))
  eq_("s3://b/f1/f2/../f3", j("s3://b/f1/f2", "../f3"))


def test_abspath():
  a = s3.abspath
  eq_('s3://a/b/c/d', a('s3://a/b/c', 'd'))
  eq_('s3://a/b/c/d', a('/a/b/c', 'd'))


def test_is_root():
  i = s3.is_root
  eq_(True, i('s3://'))
  eq_(True, i('S3://'))
  eq_(False, i('s3:/'))
  eq_(False, i('s3://bucket'))
  eq_(False, i('/local/path'))


def test_s3datetime_to_timestamp():
  f = s3.s3datetime_to_timestamp
  eq_(1424983327, f('Thu, 26 Feb 2015 20:42:07 GMT'))
  eq_(1424983327, f('2015-02-26T20:42:07.000Z'))

  assert_raises(ValueError, f, '2/26/2015 20:42:07')

  assert_raises(AssertionError, f, 'Thu, 26 Feb 2015 20:42:07 PDT')
  assert_raises(AssertionError, f, '2015-02-26T20:42:07.040Z')
