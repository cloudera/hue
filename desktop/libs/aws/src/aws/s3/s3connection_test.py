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

import requests
import sys

from nose.tools import assert_equal, assert_false, assert_true, assert_raises

from aws.client import _make_client
from aws.s3.s3connection import BotoUrlConnection, UrlBucket
from aws.s3.s3test_utils import S3TestBase


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


class TestBotoUrlConnection():

  def test_get_buckets(self):
    with patch('aws.s3.s3connection.BotoUrlConnection._generate_url') as _generate_url:
      with patch('aws.s3.s3connection.requests.get') as requests_get:

        _generate_url.return_value = 'https://gethue-test.s3.amazonaws.com/?AWSAccessKeyId=AKIA23E77ZX2HVY76YGL' + \
            '&Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'
        requests_get.return_value = Mock(
          content=b'<?xml version="1.0" encoding="UTF-8"?>\n<ListAllMyBucketsResult '
            b'xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Owner><ID>0429b0aed2900f450655928a09e06e7aaac9939bc9141fc5aeeccd8b93b9778f'
            b'</ID><DisplayName>team</DisplayName></Owner><Buckets><Bucket><Name>demo-gethue</Name><CreationDate>2020-08-22T08:03:18.000Z'
            b'</CreationDate></Bucket><Bucket><Name>gethue-test</Name><CreationDate>2021-03-31T14:47:14.000Z</CreationDate></Bucket>'
            b'</Buckets></ListAllMyBucketsResult>'
        )

        connection = Mock()
        connection.bucket_class = UrlBucket
        buckets = BotoUrlConnection(connection=connection).get_all_buckets()

        assert_equal('[<Bucket: demo-gethue>, <Bucket: gethue-test>]', str(buckets))


class TestBotoUrlConnectionIntegration(S3TestBase):
  #
  # To trigger:
  # TEST_S3_BUCKET=gethue-test ./build/env/bin/hue test specific aws.s3.s3connection_test

  @classmethod
  def setUpClass(cls):
    S3TestBase.setUpClass()


  def setUp(self):
    super(TestBotoUrlConnectionIntegration, self).setUp()

    self.c = _make_client(identifier='default', user=None)
    self.connection = self.c._s3_connection.connection


  def test_list_buckets(self):
    buckets = BotoUrlConnection(self.connection).get_all_buckets()

    assert_equal('[<Bucket: demo-gethue>, <Bucket: gethue-test>]', str(buckets))


  def test_list_file(self):
    kwargs = {'action': 'GET', 'bucket': 'gethue-test', 'key': 'data/query-hive-weblogs.csv'}
    url = BotoUrlConnection(self.connection).generate_url(**kwargs)

    url = 'https://gethue-test.s3.amazonaws.com/data/query-hive-weblogs.csv?AWSAccessKeyId=AKIA23E77ZX2HVY76YGL&Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'

    assert_true('data/query-hive-weblogs.csv' in url)
    assert_true('AWSAccessKeyId=' in url)
    assert_true('Signature=' in url)
    assert_true('Expires=' in url)

    response = requests.get(url)
