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

import archives
import unittest
import os

from archives import IllegalPathException
from nose.tools import assert_true, assert_equal

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

    FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/test5.zip')

    # Extract the file
    # This file should only have 'test.txt' in it
    directory = archives.archive_factory(FILE, 'zip').extract()
    assert_true(os.path.exists(directory))
    assert_true(os.path.isdir(directory))
    assert_true(os.path.isfile(directory + '/tmp/temp/test.txt'))
    assert_equal(os.path.getsize(directory + '/tmp/temp/test.txt'), 5)

  def test_tgz(self):
    FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/test.tar.gz')

    # Extract the file
    # This file should only have 'test.txt' in it
    directory = archives.archive_factory(FILE, 'tgz').extract()
    assert_true(os.path.exists(directory))
    assert_true(os.path.isdir(directory))
    assert_true(os.path.isfile(directory + '/test.txt'))
    assert_equal(os.path.getsize(directory + '/test.txt'), 4)

    FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/test2.tar.gz')

    # Extract the file
    # This file should only have 'test.txt' in it
    directory = archives.archive_factory(FILE, 'tar.gz').extract()
    assert_true(os.path.exists(directory))
    assert_true(os.path.isdir(directory))
    assert_true(os.path.isfile(directory + '/home/docs/test.txt'))
    assert_equal(os.path.getsize(directory + '/home/docs/test.txt'), 4)

    # This file should not be extracted as it contains illegal path '../../../Desktop/test.txt'
    FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/test3.tar.gz')

    factory = archives.archive_factory(FILE, 'tar.gz')
    self.assertRaises(IllegalPathException, factory.extract)

    # This file should not be extracted as it contains absolute path
    FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/test4.tar.gz')

    factory = archives.archive_factory(FILE, 'tar.gz')
    self.assertRaises(IllegalPathException, factory.extract)

if __name__ == "__main__":
  unittest.main()
