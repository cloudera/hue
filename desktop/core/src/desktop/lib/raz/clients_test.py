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
from unittest.mock import Mock, patch

import pytest
from django.test import TestCase

from desktop.conf import RAZ
from desktop.lib.raz.clients import AdlsRazClient, S3RazClient


class S3RazClientLiveTest(TestCase):

  @classmethod
  def setup_class(cls):
    if not RAZ.IS_ENABLED.get():
      pytest.skip("Skipping Test")

  def test_check_access_s3_list_buckets(self):

    url = S3RazClient().get_url()

    assert 'AWSAccessKeyId=' in url
    assert 'Signature=' in url
    assert 'Expires=' in url

  def test_check_acccess_s3_list_file(self):
    # e.g. 'https://gethue-test.s3.amazonaws.com/data/query-hive-weblogs.csv?AWSAccessKeyId=AKIA23E77ZX2HVY76YGL&'
    # 'Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'

    url = S3RazClient().get_url(bucket='gethue-test', path='/data/query-hive-weblogs.csv')

    assert 'data/query-hive-weblogs.csv' in url
    assert 'AWSAccessKeyId=' in url
    assert 'Signature=' in url
    assert 'Expires=' in url

    url = S3RazClient().get_url(bucket='gethue-test', path='/data/query-hive-weblogs.csv', perm='read', action='write')

    assert 'data/query-hive-weblogs.csv' in url
    assert 'AWSAccessKeyId=' in url
    assert 'Signature=' in url
    assert 'Expires=' in url

  def test_check_acccess_s3_list_file_no_access(self): pass


class AdlsRazClientTest(TestCase):

  def setup_method(self, method):
    self.username = 'csso_hueuser'

  def test_check_rename_operation(self):
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
