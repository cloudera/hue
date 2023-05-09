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
from nose.tools import assert_equal, assert_true, assert_raises

from desktop.conf import RAZ
from desktop.lib.raz.raz_client import RazToken, RazClient, get_raz_client
from desktop.lib.exceptions_renderable import PopupException

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


class RazTokenTest(unittest.TestCase):

  def setUp(self):
    self.username = 'gethue'

  def test_create(self):
    with patch('desktop.lib.raz.raz_client.requests_kerberos.HTTPKerberosAuth') as HTTPKerberosAuth:
      token = RazToken(raz_url='https://raz.gethue.com:8080', auth_type='kerberos')

      assert_equal('raz.gethue.com', token.raz_hostname)
      assert_equal('8080', token.raz_port)
      assert_equal('https', token.scheme)
      assert_equal('kerberos', token.auth_type)


  def test_get_delegation_token(self):
    with patch('desktop.lib.raz.raz_client.requests_kerberos.HTTPKerberosAuth') as HTTPKerberosAuth:
      with patch('desktop.lib.raz.raz_client.requests.get') as requests_get:
        with patch('desktop.lib.raz.raz_client.socket.gethostbyname') as gethostbyname:
          with patch('desktop.lib.raz.raz_client.fetch_jwt') as fetch_jwt:
            
            gethostbyname.return_value = '128.0.0.1'
            requests_get.return_value = Mock(
              text='{"Token":{"urlString":"f3VLQVkuBCfGSyOLzI9PoxqHTjANUzMgZGVsZWdhdGlvbhExMC44MC4xNjQuMzc6NjA4Mg"}}'
            )

            # When auth type is Kerberos
            token = RazToken(raz_url='https://raz.gethue.com:8080', auth_type='kerberos')
            t = token.get_delegation_token(user=self.username)

            fetch_jwt.assert_not_called()
            assert_equal('f3VLQVkuBCfGSyOLzI9PoxqHTjANUzMgZGVsZWdhdGlvbhExMC44MC4xNjQuMzc6NjA4Mg', t)

            # When auth type is JWT
            fetch_jwt.return_value = 'test_jwt_token'

            token = RazToken(raz_url='https://raz.gethue.com:8080', auth_type='jwt')
            t = token.get_delegation_token(user=self.username)

            fetch_jwt.assert_called()
            assert_equal('f3VLQVkuBCfGSyOLzI9PoxqHTjANUzMgZGVsZWdhdGlvbhExMC44MC4xNjQuMzc6NjA4Mg', t)

            fetch_jwt.return_value = None # Should raise PopupException

            token = RazToken(raz_url='https://raz.gethue.com:8080', auth_type='jwt')
            assert_raises(PopupException, token.get_delegation_token, user=self.username)


  def test_renew_delegation_token(self):
    with patch('desktop.lib.raz.raz_client.requests.get') as requests_get:
      with patch('desktop.lib.raz.raz_client.socket.gethostbyname') as gethostbyname:
        requests_get.return_value = Mock(
          text='{"Token":{"urlString":"f3VLQVkuBCfGSyOLzI9PoxqHTjANUzMgZGVsZWdhdGlvbhExMC44MC4xNjQuMzc6NjA4Mg"}}'
        )
        gethostbyname.return_value = '128.0.0.1'
        token = RazToken(raz_url='https://raz.gethue.com:8080', auth_type='kerberos')

        t = token.renew_delegation_token(user=self.username)

        assert_equal(t, 'f3VLQVkuBCfGSyOLzI9PoxqHTjANUzMgZGVsZWdhdGlvbhExMC44MC4xNjQuMzc6NjA4Mg')

        with patch('desktop.lib.raz.raz_client.requests.put') as requests_put:
          token.init_time += timedelta(hours=9)

          t = token.renew_delegation_token(user=self.username)

          requests_put.assert_called()


class RazClientTest(unittest.TestCase):

  def setUp(self):
    self.username = 'gethue'
    self.raz_url = 'https://raz.gethue.com:8080'
    self.raz_token = "mock_RAZ_token"

    self.s3_path = 'https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv'
    self.adls_path = 'https://gethuestorage.dfs.core.windows.net/gethue-container/user/csso_hueuser/customer.csv'


  def test_get_raz_client_adls(self):
    with patch('desktop.lib.raz.raz_client.RazToken') as RazToken:
      client = get_raz_client(
        raz_url=self.raz_url,
        username=self.username,
        auth='kerberos',
        service='adls',
        service_name='gethue_adls',
        cluster_name='gethueCluster'
      )

      assert_true(isinstance(client, RazClient))

      assert_equal(client.raz_url, self.raz_url)
      assert_equal(client.service_name, 'gethue_adls')
      assert_equal(client.cluster_name, 'gethueCluster')


  def test_check_access_adls(self):
    with patch('desktop.lib.raz.raz_client.requests.post') as requests_post:
      with patch('desktop.lib.raz.raz_client.uuid.uuid4') as uuid:

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

        client = RazClient(self.raz_url, self.raz_token, username=self.username, service="adls", service_name="cm_adls", cluster_name="cl1")

        # Read file operation
        resp = client.check_access(method='GET', url=self.adls_path)

        requests_post.assert_called_with(
          "https://raz.gethue.com:8080/api/authz/adls/access?delegation=mock_RAZ_token",
          headers={"Content-Type": "application/json"},
          json={
            'requestId': 'mock_request_id', 
            'serviceType': 'adls', 
            'serviceName': 'cm_adls', 
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
                'storageaccount': 'gethuestorage', 
                'container': 'gethue-container', 
                'relativepath': '/user/csso_hueuser/customer.csv'
              },
              'action': 'read', 
              'accessTypes': ['read']
            }
          },
          verify=False
        )
        assert_equal(resp['token'], "nulltenantIdnullnullbnullALLOWEDnullnull1.05nSlN7t/QiPJ1OFlCruTEPLibFbAhEYYj5wbJuaeQqs=")


  def test_handle_adls_action_types_mapping(self):
    client = RazClient(self.raz_url, self.raz_token, username=self.username, service="adls", service_name="cm_adls", cluster_name="cl1")

    # List directory
    method = 'GET'
    relative_path = '/'
    url_params = {'directory': 'user%2Fcsso_hueuser', 'resource': 'filesystem', 'recursive': 'false'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'list')

    # Stats
    method = 'HEAD'
    relative_path = '/user/csso_hueuser'
    url_params = {'action': 'getStatus'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'get-status')

    method = 'HEAD'
    relative_path = '/user'
    url_params = {'resource': 'filesystem'} # Stats call for first-level directories like /user

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'get-status')

    method = 'HEAD'
    relative_path = '/'
    url_params = {'action': 'getAccessControl'} # Stats call for root directory path

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'get-acl')

    # Delete path
    method = 'DELETE'
    relative_path = '/user/csso_hueuser/test_dir/customer.csv'
    url_params = {}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'delete')

    # Delete with recursive as true
    method = 'DELETE'
    relative_path = '/user/csso_hueuser/test_dir'
    url_params = {'recursive': 'true'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'delete-recursive')

    # Create directory
    method = 'PUT'
    relative_path = '/user/csso_hueuser/test_dir'
    url_params = {'resource': 'directory'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'create-directory')

    # Create file
    method = 'PUT'
    relative_path = '/user/csso_hueuser/customers.csv'
    url_params = {'resource': 'file'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'create-file')

    # Append
    method = 'PATCH'
    relative_path = '/user/csso_hueuser/customers.csv'
    url_params = {'action': 'append'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'write')

    # Flush
    method = 'PATCH'
    relative_path = '/user/csso_hueuser/customers.csv'
    url_params = {'action': 'flush'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'write')

    # Chmod
    method = 'PATCH'
    relative_path = '/user/csso_hueuser/customers.csv'
    url_params = {'action': 'setAccessControl'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert_equal(access_type, 'set-permission')


  def test_handle_relative_path(self):
    client = RazClient(self.raz_url, self.raz_token, username=self.username, service="adls", service_name="cm_adls", cluster_name="cl1")

    # No relative path condition
    method = 'GET'
    resource_path = ['gethue-container']
    url_params = {}

    relative_path = client._handle_relative_path(method, url_params, resource_path, "/")
    assert_equal(relative_path, "/")

    # When relative path is present in URL
    method = 'GET'
    resource_path = ['gethue-container', 'user/csso_hueuser/customer.csv']
    url_params = {}

    relative_path = client._handle_relative_path(method, url_params, resource_path, "/")
    assert_equal(relative_path, "/user/csso_hueuser/customer.csv")

    # When relative path present in URL is having quoted whitespaces (%20)
    method = 'GET'
    resource_path = ['gethue-container', 'user/csso_hueuser/customer%20(1).csv']
    url_params = {}

    relative_path = client._handle_relative_path(method, url_params, resource_path, "/")
    assert_equal(relative_path, "/user/csso_hueuser/customer (1).csv")

    # When list operation
    method = 'GET'
    resource_path = ['gethue-container']
    url_params = {'directory': 'user%2Fcsso_hueuser', 'resource': 'filesystem', 'recursive': 'false'}

    relative_path = client._handle_relative_path(method, url_params, resource_path, "/")
    assert_equal(relative_path, "/user/csso_hueuser")


  def test_get_raz_client_s3(self):
    with patch('desktop.lib.raz.raz_client.RazToken') as RazToken:
      client = get_raz_client(
        raz_url=self.raz_url,
        username=self.username,
        auth='kerberos',
        service='s3',
        service_name='gethue_s3',
        cluster_name='gethueCluster'
      )

      assert_true(isinstance(client, RazClient))

      assert_equal(client.raz_url, self.raz_url)
      assert_equal(client.service_name, 'gethue_s3')
      assert_equal(client.cluster_name, 'gethueCluster')


  def test_check_access_s3(self):
    with patch('desktop.lib.raz.raz_client.requests.post') as requests_post:
      with patch('desktop.lib.raz.raz_client.raz_signer.SignResponseProto') as SignResponseProto:
        with patch('desktop.lib.raz.raz_client.base64.b64decode') as b64decode:
          with patch('desktop.lib.raz.raz_client.uuid.uuid4') as uuid:

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
            uuid.return_value = 'mock_request_id'

            client = RazClient(self.raz_url, self.raz_token, username=self.username)

            resp = client.check_access(method='GET', url=self.s3_path)

            if sys.version_info[0] > 2:
              signed_request = 'CiRodHRwczovL2dldGh1ZS10ZXN0LnMzLmFtYXpvbmF3cy5jb20Q' \
                'ATIYZ2V0aHVlL2RhdGEvY3VzdG9tZXIuY3N2OABCAnMzSgJzMw=='
            else:
              signed_request = b'CiRodHRwczovL2dldGh1ZS10ZXN0LnMzLmFtYXpvbmF3cy5jb20Q' \
                b'ATIYZ2V0aHVlL2RhdGEvY3VzdG9tZXIuY3N2OABCAnMzSgJzMw=='

            requests_post.assert_called_with(
              'https://raz.gethue.com:8080/api/authz/s3/access?delegation=mock_RAZ_token', 
              headers={'Content-Type': 'application/json', 'Accept-Encoding': 'gzip,deflate'}, 
              json={
                'requestId': 'mock_request_id',
                'serviceType': 's3',
                'serviceName': 'cm_s3',
                'user': 'gethue',
                'userGroups': [],
                'clientIpAddress': '',
                'clientType': '',
                'clusterName': 'myCluster',
                'clusterType': '',
                'sessionId': '',
                'accessTime': '',
                'context': {
                  'S3_SIGN_REQUEST': signed_request
                }
              },
              verify=False
            )
            assert_true(resp)
            assert_equal(resp['AWSAccessKeyId'], 'AKIA23E77ZX2HVY76YGL')
