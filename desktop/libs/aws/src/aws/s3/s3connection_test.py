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
import requests
import six
import sys

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true

from desktop.conf import RAZ

from aws.client import _make_client
from aws.s3.s3connection import SelfSignedUrlClient, RazSignedUrlClient, SelfSignedUrlS3Connection, RazS3Connection
from aws.s3.s3test_utils import S3TestBase

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


LOG = logging.getLogger()


class TestRazS3Connection():

  def setUp(self):
    self.finish = [
      RAZ.IS_ENABLED.set_for_testing(True)
    ]

  def tearDown(self):
    for f in self.finish:
      f()

  def test_list_buckets(self):
    with patch('aws.s3.s3connection.S3RazClient.get_url') as get_url:
      with patch('aws.s3.s3connection.RazS3Connection._mexe') as _mexe:

        get_url.return_value = {
            'AWSAccessKeyId': 'AKIA23E77ZX2HVY76YGL',
            'Signature': '3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D',
            'Expires': '1617207304'
        }
        _mexe.return_value = ['<Bucket: demo-gethue>', '<Bucket: gethue-test>']

        client = RazS3Connection(username='test', host='s3-us-west-1.amazonaws.com')

        buckets = client.make_request(method='GET', bucket='', key='',)

        assert_equal(['<Bucket: demo-gethue>', '<Bucket: gethue-test>'], buckets)

        http_request = _mexe.call_args.args[0]

        if isinstance(http_request, six.string_types):
          raise SkipTest()  # Incorrect in Py3 CircleCi

        assert_equal('GET', http_request.method)
        assert_equal(
          's3-us-west-1.amazonaws.com:443' if sys.version_info[0] > 2 else 's3-us-west-1.amazonaws.com',
          http_request.host
        )
        assert_equal('/', http_request.path)
        assert_equal('/', http_request.auth_path)
        assert_equal({
            'AWSAccessKeyId': 'AKIA23E77ZX2HVY76YGL',
            'Signature': '3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D',
            'Expires': '1617207304'
          },
          http_request.headers
        )
        assert_equal({}, http_request.params)
        assert_equal('', http_request.body)


class TestSelfSignedUrlS3Connection():

  def test_get_file(self):
    with patch('aws.s3.s3connection.SelfSignedUrlS3Connection.generate_url') as generate_url:
      with patch('aws.s3.s3connection.SelfSignedUrlS3Connection._mexe') as _mexe:
        with patch('boto.connection.auth.get_auth_handler') as get_auth_handler:

          generate_url.return_value = 'https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv?' + \
              'AWSAccessKeyId=AKIA23E77ZX2HVY76YGL' + \
              '&Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'
          _mexe.return_value = '[<Bucket: demo-gethue>, <Bucket: gethue-test>]'

          client = SelfSignedUrlS3Connection(username='test')
          http_request = Mock(
            path='/gethue/data/customer.csv',
            protocol='https',
            host='s3.amazonaws.com'
          )
          client.build_base_http_request = Mock(return_value=http_request)

          buckets = client.make_request(method='GET', bucket='gethue', key='data/customer.csv',)

          assert_equal('[<Bucket: demo-gethue>, <Bucket: gethue-test>]', buckets)
          _mexe.assert_called_with(http_request, None, None, retry_handler=None)

          assert_equal('https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv', http_request.path)
          assert_equal(
            {
              'AWSAccessKeyId': 'AKIA23E77ZX2HVY76YGL',
              'Signature': '3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D',
              'Expires': '1617207304'
            },
            http_request.headers
          )


# -----------------------------------------------------------------------------------------------------------

class TestSelfSignedUrlClient():

  def setUp(self):
    raise SkipTest()

  def test_get_buckets(self):
    with patch('aws.s3.s3connection.SelfSignedUrlClient.get_url_request') as get_url_request:
      with patch('aws.s3.s3connection.requests.get') as requests_get:

        get_url_request.return_value = 'https://gethue-test.s3.amazonaws.com/?AWSAccessKeyId=AKIA23E77ZX2HVY76YGL' + \
            '&Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'
        requests_get.return_value = Mock(
          content=b'<?xml version="1.0" encoding="UTF-8"?>\n<ListAllMyBucketsResult '
            b'xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Owner><ID>0429b0aed2900f450655928a09e06e7aaac9939bc9141fc5aeeccd8b93b9778f'
            b'</ID><DisplayName>team</DisplayName></Owner><Buckets><Bucket><Name>demo-gethue</Name><CreationDate>2020-08-22T08:03:18.000Z'
            b'</CreationDate></Bucket><Bucket><Name>gethue-test</Name><CreationDate>2021-03-31T14:47:14.000Z</CreationDate></Bucket>'
            b'</Buckets></ListAllMyBucketsResult>'
        )

        connection = Mock()
        buckets = SelfSignedUrlClient(connection=connection).get_all_buckets()

        assert_equal('[<Bucket: demo-gethue>, <Bucket: gethue-test>]', str(buckets))


class TestRazSignedUrlClient():

  def setUp(self):
    raise SkipTest()

  def test_get_buckets(self):
    with patch('aws.s3.s3connection.RazSignedUrlClient.get_url_request') as get_url_request:
      with patch('aws.s3.s3connection.requests.get') as requests_get:

        # TODO: update with potentially slightly different URL/headers
        get_url_request.return_value = 'https://gethue-test.s3.amazonaws.com/?AWSAccessKeyId=AKIA23E77ZX2HVY76YGL' + \
            '&Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'

        requests_get.return_value = Mock(
          content=b'<?xml version="1.0" encoding="UTF-8"?>\n<ListAllMyBucketsResult '
            b'xmlns="http://s3.amazonaws.com/doc/2006-03-01/"><Owner><ID>0429b0aed2900f450655928a09e06e7aaac9939bc9141fc5aeeccd8b93b9778f'
            b'</ID><DisplayName>team</DisplayName></Owner><Buckets><Bucket><Name>demo-gethue</Name><CreationDate>2020-08-22T08:03:18.000Z'
            b'</CreationDate></Bucket><Bucket><Name>gethue-test</Name><CreationDate>2021-03-31T14:47:14.000Z</CreationDate></Bucket>'
            b'</Buckets></ListAllMyBucketsResult>'
        )

        buckets = RazSignedUrlClient().get_all_buckets()

        assert_equal('[<Bucket: demo-gethue>, <Bucket: gethue-test>]', str(buckets))


class TestSelfSignedUrlClientIntegration(S3TestBase):
  #
  # To trigger:
  # TEST_S3_BUCKET=gethue-test ./build/env/bin/hue test specific aws.s3.s3connection_test

  @classmethod
  def setUpClass(cls):
    S3TestBase.setUpClass()


  def setUp(self):
    super(TestSelfSignedUrlClientIntegration, self).setUp()

    self.c = _make_client(identifier='default', user=None)
    self.connection = self.c._s3_connection.connection


  def test_list_buckets(self):
    buckets = SelfSignedUrlClient(self.connection).get_all_buckets()

    assert_equal('[<Bucket: demo-gethue>, <Bucket: gethue-test>]', str(buckets))


  def test_list_file(self):
    kwargs = {'action': 'GET', 'bucket': 'gethue-test', 'key': 'data/query-hive-weblogs.csv'}
    url = SelfSignedUrlClient(self.connection).generate_url(**kwargs)

    url = 'https://gethue-test.s3.amazonaws.com/data/query-hive-weblogs.csv?'
    'AWSAccessKeyId=AKIA23E77ZX2HVY76YGL&Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'

    assert_true('data/query-hive-weblogs.csv' in url)
    assert_true('AWSAccessKeyId=' in url)
    assert_true('Signature=' in url)
    assert_true('Expires=' in url)

    response = requests.get(url)
