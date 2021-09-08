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
import unittest

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_false, assert_true, assert_raises

from desktop.conf import RAZ
from desktop.lib.raz.clients import S3RazClient, AdlsRazClient

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock

class S3RazClientLiveTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    if not RAZ.IS_ENABLED.get():
      raise SkipTest

  def test_check_access_s3_list_buckets(self):

    url = S3RazClient().get_url()

    assert_true('AWSAccessKeyId=' in url)
    assert_true('Signature=' in url)
    assert_true('Expires=' in url)


  def test_check_acccess_s3_list_file(self):
    # e.g. 'https://gethue-test.s3.amazonaws.com/data/query-hive-weblogs.csv?AWSAccessKeyId=AKIA23E77ZX2HVY76YGL&'
    # 'Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'

    url = S3RazClient().get_url(bucket='gethue-test', path='/data/query-hive-weblogs.csv')

    assert_true('data/query-hive-weblogs.csv' in url)
    assert_true('AWSAccessKeyId=' in url)
    assert_true('Signature=' in url)
    assert_true('Expires=' in url)

    url = S3RazClient().get_url(bucket='gethue-test', path='/data/query-hive-weblogs.csv', perm='read', action='write')

    assert_true('data/query-hive-weblogs.csv' in url)
    assert_true('AWSAccessKeyId=' in url)
    assert_true('Signature=' in url)
    assert_true('Expires=' in url)


  def test_check_acccess_s3_list_file_no_access(self): pass

class AdlsRazClientTest(unittest.TestCase):

  def setUp(self):
    self.username = 'csso_hueuser'
  
  def test_check_rename_operation(self):
    with patch('desktop.lib.raz.raz_client.RazToken.get_delegation_token') as raz_token:
      with patch('desktop.lib.raz.raz_client.requests.post') as requests_post:
        with patch('desktop.lib.raz.raz_client.uuid.uuid4') as uuid:
          with patch('desktop.lib.raz.raz_client.RazClient.check_access') as check_access:

            reset = RAZ.API_URL.set_for_testing('https://raz_url:8000')
            check_access.return_value = {'token': 'some_random_sas_token'}

            try:
              sas_token = AdlsRazClient(
                username=self.username
              ).get_url(
                action='PUT',
                path='https://gethuestorage.dfs.core.windows.net/data/user/csso_hueuser/rename_destination_dir',
                headers={'x-ms-version': '2019-12-12', 'x-ms-rename-source': '/data/user/csso_hueuser/rename_source_dir'})

              check_access.assert_called_with(
                headers={
                  'x-ms-version': '2019-12-12', 
                  'x-ms-rename-source': '/data/user/csso_hueuser/rename_source_dir?some_random_sas_token'
                },
                method='PUT',
                url='https://gethuestorage.dfs.core.windows.net/data/user/csso_hueuser/rename_destination_dir'
              )
            finally:
              reset()
