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

import sys

from nose.tools import assert_equal, assert_false, assert_true

from desktop.lib.rest.resource import Resource


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


def test_resource_ascii():

  with patch('desktop.lib.rest.http_client.HttpClient') as HttpClient:
    client = HttpClient()
    client.execute = Mock(
      return_value=Mock(
        headers={},
        content='{"FileStatus":{"pathSuffix":"/user/hue/Джейкоб","type":"DIRECTORY","length":0,"owner":"admin","group":"admin","permission":"755","accessTime":0,"modificationTime":1578458822492,"blockSize":0,"replication":0,"childrenNum":0,"fileId":149137,"storagePolicy":0}}'
      )
    )

    resource = Resource(client)
    resource.get('/user/domain/Джейкоб')

    assert_true(client._session)
