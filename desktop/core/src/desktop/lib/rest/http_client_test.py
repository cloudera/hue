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

from requests.exceptions import HTTPError
from requests import Response

from nose.tools import assert_equal

from desktop.lib.rest.http_client import RestException


def build_response(reason=None, status_code=200, headers={}):
  response = Response()
  response.status_code = status_code
  response.headers = headers
  response.reason = reason
  return response


def test_http_error_rest_exception():
  headers ={'my header': 'one value'}
  response = build_response('Not found', 404, headers)
  exception = RestException(HTTPError(response=response))
  assert_equal(headers, exception._headers)
