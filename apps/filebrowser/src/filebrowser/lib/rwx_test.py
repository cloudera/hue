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

from __future__ import absolute_import
from builtins import range
from . import rwx

import unittest

class RwxTest(unittest.TestCase):

  def test_file_type(self):
    self.assertEquals("dir", rwx.filetype(0o40330))
    self.assertEquals("file", rwx.filetype(0o100770))
    self.assertEquals("link", rwx.filetype(0o120000))
    self.assertEquals("unknown", rwx.filetype(0))

  def test_expand_mode(self):
    self.assertEquals( [True, True, False, True, True, False, False, False, True, False], rwx.expand_mode(0o661))
    self.assertEquals( [True, True, False, True, True, False, False, False, True, True], rwx.expand_mode(0o1661))

  def test_compress_mode(self):
    self.assertEquals(0o661, rwx.compress_mode( (True, True, False, True, True, False, False, False, True, False) ))
    self.assertEquals(0o1661, rwx.compress_mode( (True, True, False, True, True, False, False, False, True, True) ))

  def check_inverseness_and_uniqueness(self):
    all = set()
    for i in range(0, 2*8*8*8-1):
      t = rwx.expand_mode(i)
      self.assertEquals(i, rwx.compress_mode(t))
      all.add(t)
    self.assertEquals(2*8*8*8, len(all))

  def test_aclbit(self):
    self.assertEquals('?rw-rw---x', rwx.rwx(0o661))
    self.assertEquals('?rw-rw---x+', rwx.rwx(0o661, True))

    self.assertEquals('?-wx-wx-wxt', rwx.rwx(1755))
    self.assertEquals('?-wx-wx-wxt+', rwx.rwx(1755, True))

if __name__ == "__main__":
  unittest.main()
