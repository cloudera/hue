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
"""
Tests for Hadoop FS.
"""
from nose.tools import assert_false, assert_true, assert_equals, assert_raises
from nose.plugins.attrib import attr
import logging
import posixfile
import random
from threading import Thread

from hadoop import pseudo_hdfs4
from hadoop.fs.exceptions import WebHdfsException
from hadoop.fs.hadoopfs import Hdfs

LOG = logging.getLogger(__name__)

@attr('requires_hadoop')
def test_webhdfs():
  """
  Minimal tests for a few basic file system operations.
  """
  cluster = pseudo_hdfs4.shared_cluster()
  fs = cluster.fs
  fs.setuser(cluster.superuser)
  f = fs.open("/fortest.txt", "w")
  try:
    f.write("hello")
    f.close()
    assert_equals("hello", fs.open("/fortest.txt").read())
    assert_equals(5, fs.stats("/fortest.txt")["size"])
    assert_true(fs.isfile("/fortest.txt"))
    assert_false(fs.isfile("/"))
    assert_true(fs.isdir("/"))
    assert_false(fs.isdir("/fortest.txt"))
  finally:
    fs.remove("/fortest.txt")

@attr('requires_hadoop')
def test_seek():
  """Test for DESKTOP-293 - ensure seek works in python2.4"""
  cluster = pseudo_hdfs4.shared_cluster()
  fs = cluster.fs
  fs.setuser(cluster.superuser)
  f = fs.open("/fortest.txt", "w")
  try:
    f.write("hello")
    f.close()

    f = fs.open("/fortest.txt", "r")
    f.seek(0, posixfile.SEEK_SET)
    assert_equals("he", f.read(2))
    f.seek(1, posixfile.SEEK_SET)
    assert_equals("el", f.read(2))
    f.seek(-1, posixfile.SEEK_END)
    assert_equals("o", f.read())
    f.seek(0, posixfile.SEEK_SET)
    f.seek(2, posixfile.SEEK_CUR)
    assert_equals("ll", f.read(2))
  finally:
    fs.remove("/fortest.txt")

@attr('requires_hadoop')
def test_seek_across_blocks():
  """Makes a file with a lot of blocks, seeks around"""
  cluster = pseudo_hdfs4.shared_cluster()
  fs = cluster.fs
  fs.setuser(cluster.superuser)
  fs.create("/fortest-blocks.txt", replication=1, blocksize=1024)
  f = fs.open("/fortest-blocks.txt", "w")
  try:
    data = "abcdefghijklmnopqrstuvwxyz" * 3000
    f.write(data)
    f.close()

    for i in xrange(1, 10):
      f = fs.open("/fortest-blocks.txt", "r")

      for j in xrange(1, 100):
        offset = random.randint(0, len(data) - 1)
        f.seek(offset, posixfile.SEEK_SET)
        assert_equals(data[offset:offset+50], f.read(50))
      f.close()

  finally:
    fs.remove("/fortest-blocks.txt")


@attr('requires_hadoop')
def test_exceptions():
  """
  Tests that appropriate exceptions are raised.
  """
  cluster = pseudo_hdfs4.shared_cluster()
  fs = cluster.fs
  fs.setuser(cluster.superuser)
  f = fs.open("/for_exception_test.txt", "w")
  f.write("foo")
  f.close()
  fs.chmod("/for_exception_test.txt", 0400)
  fs.setuser("notsuperuser")
  f = fs.open("/for_exception_test.txt")

  assert_raises(WebHdfsException, f.read)
  assert_raises(IOError, fs.open, "/test/doesnotexist.txt")

@attr('requires_hadoop')
def test_two_files_open():
  """
  See DESKTOP-510.  There was a bug where you couldn't open two files at
  the same time.  It boils down to a close_fds=True issue.  If this doesn't
  hang, all is good.
  """
  cluster = pseudo_hdfs4.shared_cluster()
  fs = cluster.fs
  fs.setuser(cluster.superuser)
  f1 = fs.open("/test_one.txt", "w")
  f2 = fs.open("/test_two.txt", "w")
  f1.write("foo")
  f2.write("bar")
  f1.close()
  f2.close()
  # This should work, not hang, etc.


def test_urlsplit():
  """Test Hdfs urlsplit"""
  url = 'hdfs://nn.no.port/foo/bar'
  assert_equals(('hdfs', 'nn.no.port', '/foo/bar', '', ''), Hdfs.urlsplit(url))
  url = 'hdfs://nn:8020/foo/bar'
  assert_equals(('hdfs', 'nn:8020', '/foo/bar', '', ''), Hdfs.urlsplit(url))
  url = 'hdfs://nn:8020//foo//bar'
  assert_equals(('hdfs', 'nn:8020', '/foo/bar', '', ''), Hdfs.urlsplit(url))
  url = 'hdfs://nn:8020'
  assert_equals(('hdfs', 'nn:8020', '/', '', ''), Hdfs.urlsplit(url))
  url = '/foo/bar'
  assert_equals(('hdfs', '', '/foo/bar', '', ''), Hdfs.urlsplit(url))
  url = 'foo//bar'
  assert_equals(('hdfs', '', 'foo/bar', '', ''), Hdfs.urlsplit(url))


@attr('requires_hadoop')
def test_i18n_namespace():
  cluster = pseudo_hdfs4.shared_cluster()
  cluster.fs.setuser(cluster.superuser)

  def check_existence(name, parent, present=True):
    assertion = present and assert_true or assert_false
    listing = cluster.fs.listdir(parent)
    assertion(name in listing, "%s should be in %s" % (name, listing))

  name = u'''pt-Olá_ch-你好_ko-안녕_ru-Здравствуйте%20,.<>~`!@#$%^&()_-+='"'''
  prefix = '/tmp/i18n'
  dir_path = '%s/%s' % (prefix, name)
  file_path = '%s/%s' % (dir_path, name)

  try:
    # Create a directory
    cluster.fs.mkdir(dir_path)
    # Directory is there
    check_existence(name, prefix)

    # Create a file (same name) in the directory
    cluster.fs.open(file_path, 'w').close()
    # File is there
    check_existence(name, dir_path)

    # Test rename
    new_file_path = file_path + '.new'
    cluster.fs.rename(file_path, new_file_path)
    # New file is there
    check_existence(name + '.new', dir_path)

    # Test remove
    cluster.fs.remove(new_file_path)
    check_existence(name + '.new', dir_path, present=False)

    # Test rmtree
    cluster.fs.rmtree(dir_path)
    check_existence(name, prefix, present=False)

    # Test exception can handle non-ascii characters
    try:
      cluster.fs.rmtree(dir_path)
    except IOError, ex:
      LOG.info('Successfully caught error: %s' % (ex,))
  finally:
    try:
      cluster.fs.rmtree(prefix)
    except Exception, ex:
      LOG.error('Failed to cleanup %s: %s' % (prefix, ex))

@attr('requires_hadoop')
def test_threadedness():
  # Start a second thread to change the user, and
  # make sure that isn't reflected.
  cluster = pseudo_hdfs4.shared_cluster()
  fs = cluster.fs
  fs.setuser("alpha")
  class T(Thread):
    def run(self):
      fs.setuser("beta")
      assert_equals("beta", fs.user)
  t = T()
  t.start()
  t.join()
  assert_equals("alpha", fs.user)
  fs.setuser("gamma")
  assert_equals("gamma", fs.user)
