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

import base64
import sys
import unittest

from datetime import timedelta
from nose.tools import assert_equal, assert_false, assert_true, assert_raises

from desktop.conf import RAZ
from desktop.lib.raz.raz_client import RazToken, RazClient, get_raz_client

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


class RazTokenTest(unittest.TestCase):

  def setUp(self):
    self.username = 'gethue'

  def test_create(self):
    kerb_auth = Mock()

    token = RazToken(raz_url='https://raz.gethue.com:8080', auth_handler=kerb_auth)

    assert_equal('raz.gethue.com', token.raz_hostname)
    assert_equal('8080', token.raz_port)
    assert_equal('https', token.scheme)

  def test_get_delegation_token(self):
    kerb_auth = Mock()

    with patch('desktop.lib.raz.raz_client.requests.get') as requests_get:
      with patch('desktop.lib.raz.raz_client.socket.gethostbyname') as gethostbyname:
        requests_get.return_value = Mock(
          text='{"Token":{"urlString":"https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv?' + \
                'AWSAccessKeyId=AKIA23E77ZX2HVY76YGL' + \
                '&Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304"}}'
        )
        gethostbyname.return_value = '128.0.0.1'

        token = RazToken(raz_url='https://raz.gethue.com:8080', auth_handler=kerb_auth)

        t = token.get_delegation_token(user=self.username)

        assert_equal(
          'https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv?AWSAccessKeyId=AKIA23E77ZX2HVY76YGL&'
          'Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304',
          t
        )

  def test_renew_delegation_token(self):
    kerb_auth = Mock()

    with patch('desktop.lib.raz.raz_client.requests.get') as requests_get:
      with patch('desktop.lib.raz.raz_client.socket.gethostbyname') as gethostbyname:
          requests_get.return_value = Mock(
            text='{"Token":{"urlString":"https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv?' + \
                  'AWSAccessKeyId=AKIA23E77ZX2HVY76YGL' + \
                  '&Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304"}}'
          )
          gethostbyname.return_value = '128.0.0.1'
          token = RazToken(raz_url='https://raz.gethue.com:8080', auth_handler=kerb_auth)

          t = token.renew_delegation_token(user=self.username)

          assert_equal(t,
            'https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv?AWSAccessKeyId=AKIA23E77ZX2HVY76YGL&'
            'Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'
          )

          with patch('desktop.lib.raz.raz_client.requests.put') as requests_put:
            token.init_time += timedelta(hours=9)

            t = token.renew_delegation_token(user=self.username)

            requests_put.assert_called()


class RazClientTest(unittest.TestCase):

  def setUp(self):
    self.username = 'gethue'
    self.raz_url = 'https://raz.gethue.com:8080'

    self.s3_path = 'https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv'
    self.adls_path = 'https://gethuestorageaccount.blob.core.windows.net/demo-gethue-container/demo-dir1/customer.csv'

  def test_get_raz_client_adls(self):
    with patch('desktop.lib.raz.raz_client.RazToken') as RazToken:
      with patch('desktop.lib.raz.raz_client.requests_kerberos.HTTPKerberosAuth') as HTTPKerberosAuth:
        client = get_raz_client(
          raz_url=self.raz_url,
          username=self.username,
          auth='kerberos',
          service='adls',
          service_name='gethue_adls',
          cluster_name='gethueCluster'
        )

        assert_true(isinstance(client, RazClient))

        HTTPKerberosAuth.assert_called()
        assert_equal(client.raz_url, self.raz_url)
        assert_equal(client.service_name, 'gethue_adls')
        assert_equal(client.cluster_name, 'gethueCluster')

  def test_check_access_adls(self):
    with patch('desktop.lib.raz.raz_client.requests.post') as requests_post:
      with patch('desktop.lib.raz.raz_client.uuid.uuid4') as uuid:
        raz_token = "mock_RAZ_token"

        requests_post.return_value = Mock(
          json=Mock(return_value=
          {
            'operResult': {
              'result': 'ALLOWED',
              'additionalInfo': {
                "ADLS_DSAS": "nulltenantIdnullnullbnullALLOWEDnullnull1.05nSlN7t/QiPJ1OFlCruTEPLibFbAhEYYj5wbJuaeQqs="
                }
              }
            }
          )
        )
        uuid.return_value = 'mock_request_id'

        client = RazClient(self.raz_url, raz_token, username=self.username, service="adls", service_name="adls", cluster_name="cl1")

        resp = client.check_access(method='GET', url=self.adls_path)

        requests_post.assert_called_with(
          "https://raz.gethue.com:8080/api/authz/adls/access?delegation=" + raz_token,
          headers={"Content-Type": "application/json"},
          json={
            'requestId': 'mock_request_id', 
            'serviceType': 'adls', 
            'serviceName': 'adls', 
            'user': 'gethue', 
            'userGroups': [], 
            'clientIpAddress': '', 
            'clientType': 'adls', 
            'clusterName': 'cl1', 
            'clusterType': '', 
            'sessionId': '', 
            'accessTime': '', 
            'context': {}, 
            'operation': {
              'resource': {
                'storageaccount': 'gethuestorageaccount', 
                'container': 'demo-gethue-container', 
                'relativepath': 'demo-dir1/customer.csv'
              }, 
              'resourceOwner': '', 
              'action': 'read', 
              'accessTypes': ['read']
            }
          },
          verify=False
        )
        assert_equal(resp['token'], "nulltenantIdnullnullbnullALLOWEDnullnull1.05nSlN7t/QiPJ1OFlCruTEPLibFbAhEYYj5wbJuaeQqs=")

  def test_get_raz_client_s3(self):
    with patch('desktop.lib.raz.raz_client.RazToken') as RazToken:
      with patch('desktop.lib.raz.raz_client.requests_kerberos.HTTPKerberosAuth') as HTTPKerberosAuth:
        client = get_raz_client(
          raz_url=self.raz_url,
          username=self.username,
          auth='kerberos',
          service='s3',
          service_name='gethue_s3',
          cluster_name='gethueCluster'
        )

        assert_true(isinstance(client, RazClient))

        HTTPKerberosAuth.assert_called()
        assert_equal(client.raz_url, self.raz_url)
        assert_equal(client.service_name, 'gethue_s3')
        assert_equal(client.cluster_name, 'gethueCluster')

  def test_check_access_s3(self):
    raz_token = Mock()

    client = RazClient(self.raz_url, raz_token, username=self.username)

    with patch('desktop.lib.raz.raz_client.requests.post') as requests_post:
      with patch('desktop.lib.raz.raz_client.raz_signer.SignResponseProto') as SignResponseProto:
        with patch('desktop.lib.raz.raz_client.base64.b64decode') as b64decode:
          requests_post.return_value = Mock(
            json=Mock(return_value=
              {
                'operResult': {
                  'result': 'ALLOWED',
                  'additionalInfo': {
                      'S3_SIGN_RESPONSE': 'My signed URL'
                  }
                }
              }
            )
          )
          b64decode.return_value = 'https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv?AWSAccessKeyId=AKIA23E77ZX2HVY76YGL&' \
              'Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'

          SignResponseProto.return_value = Mock(
            FromString=Mock(
              return_value=Mock(
                signer_generated_headers=[
                  Mock(key='AWSAccessKeyId', value='AKIA23E77ZX2HVY76YGL')
                ]
              )
            )
          )

          resp = client.check_access(method='GET', url=self.s3_path)

          assert_true(resp)
          assert_equal(resp['AWSAccessKeyId'], 'AKIA23E77ZX2HVY76YGL')
