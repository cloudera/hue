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

from urllib2 import HTTPError, URLError

from nose.tools import assert_equal

from desktop.lib.rest.http_client import RestException


class MockFile:
  def read(self):
    return 'my data'
  def readline(self):
    return 'my data'


def test_url_error_rest_exception():
  exception = RestException(URLError('My error'))
  assert_equal({}, exception._headers)


def test_http_error_rest_exception():
  headers = {'my header': 'one value'}

  exception = RestException(HTTPError('url', 404, 'My error', headers, MockFile()))
  assert_equal(headers, exception._headers)
