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

from builtins import object
from requests import Response
from requests_kerberos import HTTPKerberosAuth, OPTIONAL, REQUIRED, DISABLED
from requests.exceptions import HTTPError
from desktop.conf import KERBEROS, REST_CONN_TIMEOUT

from nose.tools import assert_equal, assert_false, assert_true, assert_is_not_none, assert_is_instance

from desktop.lib.rest.http_client import RestException, HttpClient


def build_response(reason=None, status_code=200, headers={}):
  response = Response()
  response.status_code = status_code
  response.headers = headers
  response.reason = reason
  return response


def test_http_error_rest_exception():
  headers = {'my header': 'one value'}
  response = build_response('Not found', 404, headers)
  exception = RestException(HTTPError(response=response))
  assert_equal(headers, exception._headers)


class MockedSession(object):

  def __init__(self, cookies=None, verify=True, auth=None):
    self.cookies = cookies or {}
    self.verify = verify
    self.auth = auth

  def put(self, relpath=None, params=None, data=None, verify=True, contenttype=None, allow_redirects=False,
          clear_cookies=False, timeout=REST_CONN_TIMEOUT.get()):
    return MockedResponse()


class MockedResponse(object):
  def __init__(self, status_code=200, cookies=None):
    self.status_code = status_code
    self.cookies = cookies


def test_clear_cookies():

  client = HttpClient('gethue')
  client._session = MockedSession({'hue': 'rocks'})

  client.execute('put', '/path')
  assert_true(client._session.cookies)

  client.execute('put', '/path', clear_cookies=True)
  assert_false(client._session.cookies)

def test_set_kerberos_auth():
  client = HttpClient('gethue')

  for hostname_override in ['gethue.com', None]:
    for _, (mutual_authentication_conf, expected_mutual_authentication) in \
            enumerate([(None, OPTIONAL), ('OPTIONAL', OPTIONAL), ('REQUIRED', REQUIRED), ('DISABLED', DISABLED)]):

      reset_mutual_authentication = KERBEROS.MUTUAL_AUTHENTICATION.set_for_testing(
        data=mutual_authentication_conf, present=mutual_authentication_conf != None)
      reset_hostname_override = KERBEROS.HOSTNAME_OVERRIDE.set_for_testing(
        data=hostname_override, present=hostname_override != None)

      try:
        client._session = MockedSession()

        client.set_kerberos_auth(service='srv')

        assert_is_not_none(client._session.auth)
        assert_is_instance(client._session.auth, HTTPKerberosAuth)
        assert_equal(client._session.auth.service, 'srv')
        assert_equal(client._session.auth.mutual_authentication, expected_mutual_authentication)
        assert_equal(client._session.auth.hostname_override, hostname_override)
      finally:
        reset_mutual_authentication()
        reset_hostname_override()
