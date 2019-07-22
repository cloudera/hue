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

import logging
import unittest

import time

from azure.abfs.abfs import ABFS
from azure.active_directory import ActiveDirectory
from azure.conf import ABFS_CLUSTERS, is_abfs_enabled

from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_false

LOG = logging.getLogger(__name__)

"""
Interfaces for ADLS via HttpFs/WebHDFS
"""
class ABFSTestBase(unittest.TestCase):
  integration = True

  def setUp(self):
    if not is_abfs_enabled():
      raise SkipTest
    self.client = ABFS.from_config(ABFS_CLUSTERS['default'], ActiveDirectory.from_config(None, version='v2.0'))
    self.test_fs = 'abfss://testfs' + (str(int(time.time()) ))
    LOG.debug("%s" %self.test_fs)
    self.client.mkdir(self.test_fs)

  def tearDown(self):
    self.client.rmtree(self.test_fs)
    
  def test_list(self):
    filesystems = self.client.listdir('abfss://')
    LOG.debug("%s" %filesystems)
    assert_true(filesystems is not None, filesystems)
    
    pathing = self.client.listdir('abfss://' + filesystems[0])
    LOG.debug("%s" %pathing)
    assert_true(pathing is not None, pathing)
    
    directory = self.client.listdir('abfss://' + filesystems[0] + '/' + pathing[0], 'true')
    LOG.debug("%s" %directory)
    assert_true(directory is not None, directory)
    
    directory = self.client.listdir(self.test_fs)
    LOG.debug("%s" %directory)
    assert_true(directory is not None, directory)
    
  def test_existence(self):
    test_fs = self.test_fs
    test_dir = test_fs + '/test_existence'
    test_file = test_dir + '/test.txt'
    self.client.mkdir(test_dir)
    self.client.create(test_file)
    
    #Testing root and filesystems
    assert_true(self.client.exists('abfss://'))
    assert_true(self.client.exists(test_fs))
    
    #testing created directories and files
    assert_true(self.client.exists(test_dir))
    assert_true(self.client.exists(test_file))
    assert_false(self.client.exists(test_dir + 'a'))
     
  def test_stat_output(self):
    """
    Only tests if the stat outputs something
    """
    test_fs = self.test_fs
    test_dir = test_fs + '/test_stats'
    self.client.mkdir(test_dir)
    
    #testing filesystems
    result = self.client.stats(test_fs)
    LOG.debug("%s" %result)
    assert_true(result is not None, result)
    result = self.client.listdir_stats(test_fs)
    LOG.debug("%s" %result)
    
    #testing directories
    result = self.client.stats(test_dir)
    LOG.debug("%s" %result)
    result = self.client.listdir_stats(test_dir)
    LOG.debug("%s" %result)
    
  def test_mkdir(self):
    test_dir = self.test_fs + '/test_mkdir'
    assert_false(self.client.exists(test_dir))
    
    self.client.mkdir(test_dir)
    assert_true(self.client.exists(test_dir))
    
  def test_append_and_flush(self):
    test_fs = self.test_fs
    test_file = test_fs + '/test.txt'
    self.client.create(test_file)
    
    test_string = "This is a test. Do Not Panic"
    test_len = len(test_string)
    resp = self.client.append(test_file, test_string) #oly works with strings
    try:
      resp = self.client.read(test_file, length = test_len)
      LOG.debug("%s" %resp)
    except:
      LOG.debug("Not written yet")
    
    self.client.flush(test_file, {"position" : test_len} )
    resp = self.client.read(test_file)
    self.client.remove(test_file)
  
  def test_rename(self):
    test_fs = self.test_fs
    test_dir = test_fs + '/test'
    test_dir2 = test_fs + '/test2'
    test_file = test_fs + '/test.txt'
    test_file2 = test_fs + '/test2.txt'
    
    self.client.mkdir(test_dir)
    assert_true(self.client.exists(test_dir))
    assert_false(self.client.exists(test_dir2))
    
    self.client.rename(test_dir, test_dir2)
    assert_false(self.client.exists(test_dir))
    assert_true(self.client.exists(test_dir2))
    
    self.client.create(test_file)
    assert_true(self.client.exists(test_file))
    assert_false(self.client.exists(test_file2))
    
    self.client.rename(test_file, test_file2)
    assert_false(self.client.exists(test_file))
    assert_true(self.client.exists(test_file2))
    
  def test_chmod(self):
    test_dir = self.test_fs + '/test_chmod'
    self.client.mkdir(test_dir)
    test_dir_permission = test_dir +'/test'
    test_file_permission = test_dir +'/test.txt'
    
    self.client.create(test_file_permission)
    self.client.chmod(test_file_permission)
    self.client.stats(test_file_permission)
    
    self.client.mkdir(test_dir_permission)
    self.client.chmod(test_dir_permission)
    self.client.stats(test_dir_permission)
    
  def test_chown(self):
    test_dir = self.test_fs + '/test_chown'
    self.client.mkdir(test_dir)
    test_dir_permission = test_dir +'/test'
    test_file_permission = test_dir +'/test.txt'
    
    self.client.create(test_file_permission)
    self.client.chown(test_file_permission, 'temp')
    self.client.stats(test_file_permission)
    
    self.client.mkdir(test_dir_permission)
    self.client.chown(test_dir_permission, 'temp')
    self.client.stats(test_dir_permission)
    
  def test_create_with_file_perm(self):
    test_dir = self.test_fs + '/test_chown'
    test_file = test_dir + '/test.txt'
    self.client.mkdir(test_dir)
    self.client.create(test_file, headers = {'x-ms-permissions' : '0777'})
    

    