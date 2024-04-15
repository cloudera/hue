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
import unittest

from aws import conf
from aws.client import Client, get_credential_provider
from django.test import TestCase

from desktop.lib.fsmanager import get_client, clear_cache
from desktop.lib.python_util import current_ms_from_utc
from desktop.conf import RAZ

from unittest.mock import patch


LOG = logging.getLogger()


class TestAWS(TestCase):
  def test_with_credentials(self):
    try:
      finish = conf.AWS_ACCOUNTS.set_for_testing({'default': {'access_key_id': 'access_key_id', 'secret_access_key': 'secret_access_key'}})
      with patch('aws.client.conf_idbroker.get_conf') as get_conf:
        with patch('aws.client.Client.get_s3_connection'):
          get_conf.return_value = {}
          client1 = get_client(name='default', fs='s3a')
          client2 = get_client(name='default', fs='s3a', user='test')

          provider = get_credential_provider('default', 'hue')
          assert provider.get_credentials().get('AccessKeyId') == conf.AWS_ACCOUNTS['default'].ACCESS_KEY_ID.get()
          assert client1 == client2 # Should be the same as no support for user based client with credentials & no Expiration
    finally:
      finish()
      clear_cache()
      conf.clear_cache()


  def test_with_idbroker(self):
    try:
      finish = conf.AWS_ACCOUNTS.set_for_testing({}) # Set empty to test when no configs are set
      with patch('aws.client.conf_idbroker.get_conf') as get_conf:
        with patch('aws.client.conf_idbroker.get_cab_address') as get_cab_address:
          with patch('aws.client.Client.get_s3_connection'):
            with patch('aws.client.IDBroker.get_cab') as get_cab:
              with patch('aws.client.aws_conf.has_iam_metadata') as has_iam_metadata:
                get_conf.return_value = {
                  'fs.s3a.ext.cab.address': 'address'
                }
                get_cab_address.return_value = 'address'
                get_cab.return_value = {
                  'Credentials': {'AccessKeyId': 'AccessKeyId', 'Expiration': 0}
                }
                has_iam_metadata.return_value = True
                provider = get_credential_provider('default', 'hue')

                assert provider.get_credentials().get('AccessKeyId') == 'AccessKeyId'

                client1 = get_client(name='default', fs='s3a', user='hue')
                client2 = get_client(name='default', fs='s3a', user='hue')

                assert client1 != client2 # Test that with Expiration 0 clients not equal

                get_cab.return_value = {
                  'Credentials': {'AccessKeyId': 'AccessKeyId', 'Expiration': int(current_ms_from_utc()) + 10*1000}
                }
                client3 = get_client(name='default', fs='s3a', user='hue')
                client4 = get_client(name='default', fs='s3a', user='hue')
                client5 = get_client(name='default', fs='s3a', user='test')

                assert client3 == client4 # Test that with 10 sec expiration, clients equal
                assert client4 != client5 # Test different user have different clients
    finally:
      finish()
      clear_cache()
      conf.clear_cache()


  def test_with_idbroker_and_config(self):
    try:
      finish = conf.AWS_ACCOUNTS.set_for_testing({'default': {'region': 'ap-northeast-1'}})
      with patch('aws.client.conf_idbroker.get_conf') as get_conf:
        with patch('aws.client.conf_idbroker.get_cab_address') as get_cab_address:
          with patch('aws.client.Client.get_s3_connection'):
            with patch('aws.client.IDBroker.get_cab') as get_cab:
              with patch('aws.client.aws_conf.has_iam_metadata') as has_iam_metadata:
                get_conf.return_value = {
                  'fs.s3a.ext.cab.address': 'address'
                }
                get_cab_address.return_value = 'address'
                get_cab.return_value = {
                  'Credentials': {'AccessKeyId': 'AccessKeyId', 'Expiration': 0}
                }
                has_iam_metadata.return_value = True

                provider = get_credential_provider('default', 'hue')
                assert provider.get_credentials().get('AccessKeyId') == 'AccessKeyId'

                client = Client.from_config(conf.AWS_ACCOUNTS['default'], get_credential_provider('default', 'hue'))
                assert client._region == 'ap-northeast-1'
    finally:
      finish()
      clear_cache()
      conf.clear_cache()


  def test_with_idbroker_on_ec2(self):
    try:
      finish = conf.AWS_ACCOUNTS.set_for_testing({}) # Set empty to test when no configs are set
      with patch('aws.client.aws_conf.get_region') as get_region:
        with patch('aws.client.conf_idbroker.get_conf') as get_conf:
          with patch('aws.client.conf_idbroker.get_cab_address') as get_cab_address:
            with patch('aws.client.Client.get_s3_connection'):
              with patch('aws.client.IDBroker.get_cab') as get_cab:
                with patch('aws.client.aws_conf.has_iam_metadata') as has_iam_metadata:
                  get_region.return_value = 'us-west-1'
                  get_conf.return_value = {
                    'fs.s3a.ext.cab.address': 'address'
                  }
                  get_cab_address.return_value = 'address'
                  get_cab.return_value = {
                    'Credentials': {'AccessKeyId': 'AccessKeyId', 'Expiration': 0}
                  }
                  has_iam_metadata.return_value = True
                  client = Client.from_config(None, get_credential_provider('default', 'hue'))

                  assert client._region == 'us-west-1' # Test different user have different clients
    finally:
      finish()
      clear_cache()
      conf.clear_cache()


  def test_with_raz_enabled(self):
    with patch('aws.client.RazS3Connection') as raz_s3_connection:
      resets = [
        RAZ.IS_ENABLED.set_for_testing(True),
        conf.AWS_ACCOUNTS.set_for_testing({'default': {
          'region': 'us-west-2',
          'host': 's3-us-west-2.amazonaws.com',
          'allow_environment_credentials': 'false'
        }})
      ]

      try:
        client = get_client(name='default', fs='s3a', user='hue')
        assert client
      finally:
        for reset in resets:
          reset()
        clear_cache()
        conf.clear_cache()
