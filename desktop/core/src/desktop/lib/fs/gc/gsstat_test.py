#!/usr/bin/env python
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

from unittest.mock import Mock

from desktop.lib.fs.gc.gsstat import GSStat


class TestGSStat(object):
  def setup_method(self):
    self.mock_gs_bucket = Mock()
    self.mock_gs_bucket.name = 'gethue_bucket'

    self.mock_gs_key = Mock()
    self.mock_gs_key.name = 'test.csv'
    self.mock_gs_key.bucket = self.mock_gs_bucket
    self.mock_gs_key.size = 123
    self.mock_gs_key.last_modified = '2023-09-21T12:03:00.000Z' # Some mock timestamp


  def test_from_bucket(self):
    gs_bucket_stat = GSStat.from_bucket(self.mock_gs_bucket)

    assert gs_bucket_stat.name == 'gethue_bucket'
    assert gs_bucket_stat.path == 'gs://gethue_bucket'
    assert gs_bucket_stat.isDir == True
    assert gs_bucket_stat.size == 0
    assert gs_bucket_stat.mtime == None


  def test_from_key(self):
    gs_key_stat = GSStat.from_key(self.mock_gs_key)

    assert gs_key_stat.name == 'test.csv'
    assert gs_key_stat.path == 'gs://gethue_bucket/test.csv'
    assert gs_key_stat.isDir == False
    assert gs_key_stat.size == 123
    assert gs_key_stat.mtime == 1695297780  # Replace with the expected timestamp


  def test_for_gs_root(self):
    gs_root_stat = GSStat.for_gs_root()

    assert gs_root_stat.name == 'GS'
    assert gs_root_stat.path == 'gs://'
    assert gs_root_stat.isDir == True
    assert gs_root_stat.size == 0
    assert gs_root_stat.mtime == None


  def test_to_json_dict(self):
    gs_key_stat = GSStat.from_key(self.mock_gs_key)

    json_dict = gs_key_stat.to_json_dict()
    expected_dict = {
      'path': 'gs://gethue_bucket/test.csv',
      'size': 123,
      'atime': 1695297780,
      'mtime': 1695297780,
      'mode': 33206,
      'user': '',
      'group': '',
      'aclBit': False
    }

    assert json_dict == expected_dict
