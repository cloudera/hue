#!/usr/bin/env python
# encoding: utf-8
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

import json
from unittest.mock import Mock, patch

from desktop.lib.i18n import smart_str
from desktop.lib.rest.resource import Resource


def test_concat_unicode_with_ascii_python2():
  try:
    u'The currency is: %s' % '€'
  except UnicodeDecodeError:
    pass

  assert u'The currency is: €' == u'The currency is: %s' % smart_str('€')

  try:
    u'%s' % '/user/domain/Джейкоб'
  except UnicodeDecodeError:
    pass

  try:
    u'%s' % smart_str('/user/domain/Джейкоб')
  except UnicodeDecodeError:
    pass

  u'%s' % smart_str('/user/domain/Джейкоб')


def test_avoid_concat_unicode_with_ascii():
  '''
  Without smart_unicode() we get:
  UnicodeDecodeError: 'ascii' codec can't decode byte 0xd0 in position 39: ordinal not in range(128)
  '''

  with patch('desktop.lib.rest.http_client.HttpClient') as HttpClient:
    with patch('desktop.lib.rest.resource.LOG.exception') as exception:
      client = HttpClient()
      client.execute = Mock(
        return_value=Mock(
          headers={},
          content='Good'
        )
      )

      resource = Resource(client)
      resp = resource.get('/user/domain/')

      assert not exception.called
      assert 'Good' == resp

      client.execute = Mock(
        return_value=Mock(
          headers={},
          content='{"FileStatus":{"pathSuffix":"/user/hue/Джейкоб","type":"DIRECTORY","length":0,"owner":"admin","group":"admin","permission":"755","accessTime":0,"modificationTime":1578458822492,"blockSize":0,"replication":0,"childrenNum":0,"fileId":149137,"storagePolicy":0}}'
        )
      )

      resp = resource.get('/user/domain/Джейкоб')

      assert client.execute.called
      assert not exception.called  # Should not fail anymore now

      resp = resource.post('/user/domain/Джейкоб', data=json.dumps({'€': '€'}))

      assert client.execute.called
      assert not exception.called
