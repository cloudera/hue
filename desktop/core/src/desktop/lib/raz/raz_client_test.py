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

import pytest
import unittest
from django.test import TestCase

from desktop.lib.raz.raz_client import RazClient, get_raz_client
from desktop.lib.exceptions_renderable import PopupException

from unittest.mock import patch, Mock


class RazClientTest(TestCase):

  def setup_method(self, method):
    self.username = 'gethue'
    self.raz_url = 'https://raz.gethue.com:8080'
    self.raz_urls_ha = 'https://raz_host_1.gethue.com:8080/, https://raz_host_2.gethue.com:8080/'

    self.s3_path = 'https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv'
    self.adls_path = 'https://gethuestorage.dfs.core.windows.net/gethue-container/user/csso_hueuser/customer.csv'


  def test_get_raz_client_adls(self):
    client = get_raz_client(
      raz_url=self.raz_url,
      username=self.username,
      auth='kerberos',
      service='adls',
      service_name='gethue_adls',
      cluster_name='gethueCluster'
    )

    assert isinstance(client, RazClient)

    assert client.raz_url == self.raz_url
    assert client.service_name == 'gethue_adls'
    assert client.cluster_name == 'gethueCluster'


  def test_check_access_adls(self):
    with patch('desktop.lib.sdxaas.knox_jwt.requests_kerberos.HTTPKerberosAuth') as HTTPKerberosAuth:
      with patch('desktop.lib.raz.raz_client.requests.post') as requests_post:
        with patch('desktop.lib.raz.raz_client.uuid.uuid4') as uuid:

          requests_post.return_value = Mock(
            status_code=200,
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

          client = RazClient(
            self.raz_url, 'kerberos', username=self.username, service="adls", service_name="cm_adls", cluster_name="cl1"
          )

          # Read file operation
          resp = client.check_access(method='GET', url=self.adls_path)

          requests_post.assert_called_with(
            "https://raz.gethue.com:8080/api/authz/adls/access?doAs=gethue",
            auth=HTTPKerberosAuth(),
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
          assert resp['token'] == "nulltenantIdnullnullbnullALLOWEDnullnull1.05nSlN7t/QiPJ1OFlCruTEPLibFbAhEYYj5wbJuaeQqs="


  def test_handle_raz_req(self):
    with patch('desktop.lib.sdxaas.knox_jwt.requests_kerberos.HTTPKerberosAuth') as HTTPKerberosAuth:
      with patch('desktop.lib.raz.raz_client.requests.post') as requests_post:
        with patch('desktop.lib.raz.raz_client.fetch_jwt') as fetch_jwt:
          request_headers = {}
          request_data = Mock()

          # When auth type is Kerberos
          client = RazClient(self.raz_url, 'kerberos', username=self.username, service="adls", service_name="cm_adls", cluster_name="cl1")
          client._handle_raz_ha = Mock()

          raz_req = client._handle_raz_req(self.raz_url, request_headers, request_data)

          client._handle_raz_ha.assert_called_with(
            'https://raz.gethue.com:8080',
            auth_handler=HTTPKerberosAuth(),
            data=request_data,
            headers={}
          )
          fetch_jwt.assert_not_called()

          # When auth type is JWT
          fetch_jwt.return_value = 'test_jwt_token'

          client = RazClient(self.raz_url, 'jwt', username=self.username, service="adls", service_name="cm_adls", cluster_name="cl1")
          client._handle_raz_ha = Mock()

          raz_req = client._handle_raz_req(self.raz_url, request_headers, request_data)

          client._handle_raz_ha.assert_called_with(
            'https://raz.gethue.com:8080',
            data=request_data,
            headers={'Authorization': 'Bearer test_jwt_token'}
          )
          fetch_jwt.assert_called()

          # Should raise PopupException when RAZ response is None
          client = RazClient(self.raz_url, 'jwt', username=self.username, service="adls", service_name="cm_adls", cluster_name="cl1")
          client._handle_raz_ha = Mock(return_value=None)

          with pytest.raises(PopupException):
            client._handle_raz_req(self.raz_url, request_headers, request_data)

          # Should raise PopupException when JWT is None
          fetch_jwt.return_value = None
          client._handle_raz_ha = Mock()

          with pytest.raises(PopupException):
            client._handle_raz_req(self.raz_url, request_headers, request_data)


  def test_handle_adls_action_types_mapping(self):
    client = RazClient(self.raz_url, 'kerberos', username=self.username, service="adls", service_name="cm_adls", cluster_name="cl1")

    # List directory
    method = 'GET'
    relative_path = '/'
    url_params = {'directory': 'user%2Fcsso_hueuser', 'resource': 'filesystem', 'recursive': 'false'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'list'

    # Stats
    method = 'HEAD'
    relative_path = '/user/csso_hueuser'
    url_params = {'action': 'getStatus'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'get-status'

    method = 'HEAD'
    relative_path = '/user'
    url_params = {'resource': 'filesystem'} # Stats call for first-level directories like /user

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'get-status'

    method = 'HEAD'
    relative_path = '/'
    url_params = {'action': 'getAccessControl'} # Stats call for root directory path

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'get-acl'

    # Delete path
    method = 'DELETE'
    relative_path = '/user/csso_hueuser/test_dir/customer.csv'
    url_params = {}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'delete'

    # Delete with recursive as true
    method = 'DELETE'
    relative_path = '/user/csso_hueuser/test_dir'
    url_params = {'recursive': 'true'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'delete-recursive'

    # Create directory
    method = 'PUT'
    relative_path = '/user/csso_hueuser/test_dir'
    url_params = {'resource': 'directory'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'create-directory'

    # Create file
    method = 'PUT'
    relative_path = '/user/csso_hueuser/customers.csv'
    url_params = {'resource': 'file'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'create-file'

    # Append
    method = 'PATCH'
    relative_path = '/user/csso_hueuser/customers.csv'
    url_params = {'action': 'append'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'write'

    # Flush
    method = 'PATCH'
    relative_path = '/user/csso_hueuser/customers.csv'
    url_params = {'action': 'flush'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'write'

    # Chmod
    method = 'PATCH'
    relative_path = '/user/csso_hueuser/customers.csv'
    url_params = {'action': 'setAccessControl'}

    access_type = client.handle_adls_req_mapping(method, url_params)
    assert access_type == 'set-permission'


  def test_handle_relative_path(self):
    client = RazClient(self.raz_url, 'kerberos', username=self.username, service="adls", service_name="cm_adls", cluster_name="cl1")

    # No relative path condition
    method = 'GET'
    resource_path = ['gethue-container']
    url_params = {}

    relative_path = client._handle_relative_path(method, url_params, resource_path, "/")
    assert relative_path == "/"

    # When relative path is present in URL
    method = 'GET'
    resource_path = ['gethue-container', 'user/csso_hueuser/customer.csv']
    url_params = {}

    relative_path = client._handle_relative_path(method, url_params, resource_path, "/")
    assert relative_path == "/user/csso_hueuser/customer.csv"

    # When relative path present in URL is having quoted whitespaces (%20)
    method = 'GET'
    resource_path = ['gethue-container', 'user/csso_hueuser/customer%20(1).csv']
    url_params = {}

    relative_path = client._handle_relative_path(method, url_params, resource_path, "/")
    assert relative_path == "/user/csso_hueuser/customer (1).csv"

    # When list operation
    method = 'GET'
    resource_path = ['gethue-container']
    url_params = {'directory': 'user%2Fcsso_hueuser', 'resource': 'filesystem', 'recursive': 'false'}

    relative_path = client._handle_relative_path(method, url_params, resource_path, "/")
    assert relative_path == "/user/csso_hueuser"


  def test_get_raz_client_s3(self):
    client = get_raz_client(
      raz_url=self.raz_url,
      username=self.username,
      auth='kerberos',
      service='s3',
      service_name='gethue_s3',
      cluster_name='gethueCluster'
    )

    assert isinstance(client, RazClient)

    assert client.raz_url == self.raz_url
    assert client.service_name == 'gethue_s3'
    assert client.cluster_name == 'gethueCluster'


  def test_check_access_s3(self):
    with patch('desktop.lib.sdxaas.knox_jwt.requests_kerberos.HTTPKerberosAuth') as HTTPKerberosAuth:
      with patch('desktop.lib.raz.raz_client.requests.post') as requests_post:
        with patch('desktop.lib.raz.raz_client.raz_signer.SignResponseProto') as SignResponseProto:
          with patch('desktop.lib.raz.raz_client.base64.b64decode') as b64decode:
            with patch('desktop.lib.raz.raz_client.uuid.uuid4') as uuid:

              requests_post.return_value = Mock(
                status_code=200,
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
              b64decode.return_value = 'https://gethue-test.s3.amazonaws.com/gethue/data/customer.csv' \
                  '?AWSAccessKeyId=AKIA23E77ZX2HVY76YGL&Signature=3lhK%2BwtQ9Q2u5VDIqb4MEpoY3X4%3D&Expires=1617207304'

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

              client = RazClient(self.raz_url, 'kerberos', username=self.username)

              resp = client.check_access(method='GET', url=self.s3_path)

              signed_request = 'CiRodHRwczovL2dldGh1ZS10ZXN0LnMzLmFtYXpvbmF3cy5jb20Q' \
                'ATIYZ2V0aHVlL2RhdGEvY3VzdG9tZXIuY3N2OABCAnMzSgJzMw=='

              requests_post.assert_called_with(
                'https://raz.gethue.com:8080/api/authz/s3/access?doAs=gethue',
                auth=HTTPKerberosAuth(),
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
              assert resp
              assert resp['AWSAccessKeyId'] == 'AKIA23E77ZX2HVY76YGL'


  def test_handle_raz_ha(self):
    with patch('desktop.lib.sdxaas.knox_jwt.requests_kerberos.HTTPKerberosAuth') as HTTPKerberosAuth:
      with patch('desktop.lib.raz.raz_client.requests.post') as requests_post:
        request_data = Mock()

        # Non-HA mode
        requests_post.return_value = Mock(status_code=200)
        client = RazClient(self.raz_url, 'kerberos', username=self.username, service="s3", service_name="cm_s3", cluster_name="cl1")
        raz_response = client._handle_raz_ha(self.raz_url, auth_handler=HTTPKerberosAuth(), data=request_data, headers={})

        requests_post.assert_called_with(
          'https://raz.gethue.com:8080/api/authz/s3/access?doAs=gethue',
          auth=HTTPKerberosAuth(), 
          headers={}, 
          json=request_data, 
          verify=False
        )
        assert raz_response.status_code == 200
        assert requests_post.call_count == 1
        requests_post.reset_mock()

        # HA mode - When RAZ instance1 is healthy and RAZ instance2 is unhealthy
        client = RazClient(self.raz_urls_ha, 'kerberos', username=self.username, service="s3", service_name="cm_s3", cluster_name="cl1")

        requests_post.side_effect = [Mock(status_code=200), Mock(status_code=404)]
        raz_response = client._handle_raz_ha(self.raz_urls_ha, auth_handler=HTTPKerberosAuth(), data=request_data, headers={})

        requests_post.assert_called_with(
          'https://raz_host_1.gethue.com:8080/api/authz/s3/access?doAs=gethue',
          auth=HTTPKerberosAuth(), 
          headers={}, 
          json=request_data, 
          verify=False
        )
        assert raz_response.status_code == 200
        assert requests_post.call_count == 1
        requests_post.reset_mock()

        # HA mode - When RAZ instance1 is unhealthy and RAZ instance2 is healthy
        requests_post.side_effect = [Mock(status_code=404), Mock(status_code=200)]
        raz_response = client._handle_raz_ha(self.raz_urls_ha, auth_handler=HTTPKerberosAuth(), data=request_data, headers={})

        requests_post.assert_called_with(
          'https://raz_host_2.gethue.com:8080/api/authz/s3/access?doAs=gethue',
          auth=HTTPKerberosAuth(),
          headers={}, 
          json=request_data, 
          verify=False
        )
        assert raz_response.status_code == 200
        assert requests_post.call_count == 2
        requests_post.reset_mock()

        # When no RAZ instance is healthy
        requests_post.side_effect = [Mock(status_code=404), Mock(status_code=404)]
        raz_response = client._handle_raz_ha(self.raz_urls_ha, auth_handler=HTTPKerberosAuth(), data=request_data, headers={})

        assert raz_response == None
        assert requests_post.call_count == 2

