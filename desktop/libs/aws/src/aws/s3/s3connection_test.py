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

import sys
import logging
from unittest.mock import Mock, patch

import six
import requests

from aws.client import _make_client
from aws.s3.s3connection import RazS3Connection
from aws.s3.s3test_utils import S3TestBase
from desktop.conf import RAZ

LOG = logging.getLogger()


class TestRazS3Connection():

  def setup_method(self):
    self.finish = [
      RAZ.IS_ENABLED.set_for_testing(True)
    ]

  def teardown_method(self):
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

        assert ['<Bucket: demo-gethue>', '<Bucket: gethue-test>'] == buckets

        http_request = _mexe.call_args.args[0]

        if isinstance(http_request, six.string_types):
          raise SkipTest()  # Incorrect in Py3 CircleCi

        assert 'GET' == http_request.method
        assert 's3-us-west-1.amazonaws.com:443' == http_request.host
        assert '/' == http_request.path
        assert '/' == http_request.auth_path
        assert ({
            'AWSAccessKeyId': 'AKIA23E77ZX2HVY76YGL',
            'Signature': '3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D',
            'Expires': '1617207304'
          } ==
          http_request.headers)
        assert {} == http_request.params
        assert '' == http_request.body
