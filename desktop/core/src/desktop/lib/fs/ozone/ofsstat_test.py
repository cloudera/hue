#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from nose.tools import assert_equal
from desktop.lib.fs.ozone.ofsstat import OzoneFSStat


class TestOzoneFSStat(object):
  def setUp(self):
    test_file_status = {
      'pathSuffix': 'testfile.csv', 'type': 'FILE', 'length': 32, 'owner': 'hueadmin', 'group': 'huegroup',
      'permission': '666', 'accessTime': 1677914460588, 'modificationTime': 1677914460588, 'blockSize': 268435456, 'replication': 3}

    test_parent_path = '/ozone1/gethue/'

    self.stat = OzoneFSStat(test_file_status, test_parent_path)


  def test_stat_attributes(self):
    assert_equal(self.stat.name, 'testfile.csv')
    assert_equal(self.stat.path, 'ofs://ozone1/gethue/testfile.csv')
    assert_equal(self.stat.isDir, False)
    assert_equal(self.stat.type, 'FILE')
    assert_equal(self.stat.atime, 1677914460)
    assert_equal(self.stat.mtime, 1677914460)
    assert_equal(self.stat.user, 'hueadmin')
    assert_equal(self.stat.group, 'huegroup')
    assert_equal(self.stat.size, 32)
    assert_equal(self.stat.blockSize, 268435456)
    assert_equal(self.stat.replication, 3)
    assert_equal(self.stat.aclBit, None)
    assert_equal(self.stat.fileId, None)
    assert_equal(self.stat.mode, 33206)


  def test_to_json_dict(self):
    expected_json_dict = {
      'path': 'ofs://ozone1/gethue/testfile.csv', 'size': 32, 'atime': 1677914460, 'mtime': 1677914460, 'mode': 33206, 'user': 'hueadmin',
      'group': 'huegroup', 'blockSize': 268435456, 'replication': 3}

    assert_equal(self.stat.to_json_dict(), expected_json_dict)
