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

import unittest
import os

from nose.tools import assert_true, assert_equal

import archives


class ArchiveTest(unittest.TestCase):

  def test_zip(self):
    FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/test.zip')

    # Extract the file
    # This file should only have 'test.txt' in it
    directory = archives.archive_factory(FILE, 'zip').extract()
    assert_true(os.path.exists(directory))
    assert_true(os.path.isdir(directory))
    assert_true(os.path.isfile(directory + '/test.txt'))
    assert_equal(os.path.getsize(directory + '/test.txt'), 4)


if __name__ == "__main__":
  unittest.main()
