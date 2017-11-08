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

from requests import Response
from requests.exceptions import HTTPError
from desktop.conf import REST_CONN_TIMEOUT

from nose.tools import assert_equal, assert_false, assert_true

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


class MockedSession():

  def __init__(self, cookies=None):
    self.cookies = cookies or {}

  def put(self, relpath=None, params=None, data=None, contenttype=None, allow_redirects=False, clear_cookies=False, timeout=REST_CONN_TIMEOUT.get()):
    return MockedResponse()


class MockedResponse():
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
