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


from nose.tools import assert_equal, assert_false, assert_true

from desktop.lib.rest.raz_http_client import RazHttpClient


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


class TestRazHttpClient():

  def test_get_file(self):
    with patch('desktop.lib.rest.raz_http_client.AdlsRazClient.get_url') as get_url:
      with patch('desktop.lib.rest.raz_http_client.HttpClient.execute') as execute:

        get_url.return_value = 'https://gethue.blob.core.windows.net/hue/data/customer.csv?sv=2014-02-14&sr=b&' + \
          'sig=pJL%2FWyed41tptiwBM5ymYre4qF8wzrO05tS5MCjkutc%3D&st=2015-01-02T01%3A40%3A51Z&se=2015-01-02T02%3A00%3A51Z&sp=r'
        execute.return_value = 'my file'

        client = RazHttpClient()
        f = client.execute(http_method='GET', path='/gethue/data/customer.csv')

        assert_equal('my file', f)
        get_url.assert_called_with('gethue.dfs.core.windows.net', 'hue', relative_path='/gethue/data/customer.csv', perm='read')
        execute.assert_called_with(http_method='GET', path='https://gethue.blob.core.windows.net/hue/data/customer.csv?' + \
          'sv=2014-02-14&sr=b&sig=pJL%2FWyed41tptiwBM5ymYre4qF8wzrO05tS5MCjkutc%3D&' + \
          'st=2015-01-02T01%3A40%3A51Z&se=2015-01-02T02%3A00%3A51Z&sp=r'
        )
