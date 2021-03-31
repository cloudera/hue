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

from nose.tools import assert_equal, assert_false, assert_true, assert_raises

from aws.client import _make_client
from aws.s3.s3connection import BotoUrlConnection
from aws.s3.s3test_utils import S3TestBase

# TEST_S3_BUCKET=gethue-test ./build/env/bin/hue test specific aws.s3.s3connection_test


class BotoUrlConnectionIntegrationTest(S3TestBase):

  @classmethod
  def setUpClass(cls):
    S3TestBase.setUpClass()


  def setUp(self):
    super(BotoUrlConnectionIntegrationTest, self).setUp()

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
