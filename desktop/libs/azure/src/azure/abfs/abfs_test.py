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
from nose.tools import assert_true

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
    
    directory = self.client.listdir('abfss://' + filesystems[0] + '/' + pathing[0])
    LOG.debug("%s" %directory)
    assert_true(directory is not None, directory)
    
    directory = self.client.listdir(self.test_fs)
    LOG.debug("%s" %directory)
    assert_true(directory is not None, directory)
    
    ok = self.client.exists('abfss://oeigfnjiorsdjngioj')
    LOG.debug("%s" %ok)
  
    
  def test_stats(self):
    ok2 = self.client.stats(self.test_fs)
    LOG.debug("%s" %ok2)
    
    ok2 = self.client.listdir_stats(self.test_fs)
    LOG.debug("%s" %ok2)
    
    
  def test_mkdir(self):
    filesystems = self.client.listdir('abfss://')
    LOG.debug("%s" %filesystems)
    assert_true(None not in filesystems, filesystems)
    
    self.client.mkdir('abfss://' + filesystems[1] + "/test")
    
    pathing = self.client.listdir('abfss://' + filesystems[1])
    LOG.debug("%s" %pathing)
    assert_true(None not in pathing, pathing)
    self.client.remove('abfss://' + filesystems[1] + "/test")
    
    pathing = self.client.listdir('abfss://' + filesystems[1])
    LOG.debug("%s" %pathing)
    
  def test_createandread(self):
    test_fs = self.test_fs
    test_file = test_fs + '/test.txt'
    self.client.create(test_file)
    self.client.read(test_file)
    self.client.remove(test_file)
  
  def test_rename(self):
    test_fs = self.test_fs
    test_dir = test_fs + '/test'
    test_file = test_fs + '/test.txt'
    self.client.mkdir(test_dir)
    ok2 = self.client.listdir_stats(self.test_fs)
    LOG.debug("%s" %ok2)
    
    self.client.rename(test_dir, test_fs + '/' + 'help')
    ok2 = self.client.listdir_stats(self.test_fs)
    LOG.debug("%s" %ok2)
    
    self.client.create(test_file)
    ok2 = self.client.listdir_stats(self.test_fs)
    LOG.debug("%s" %ok2)
    
    self.client.rename(test_file, test_fs + '/' + 'help.txt')
    ok2 = self.client.listdir_stats(self.test_fs)
    LOG.debug("%s" %ok2)