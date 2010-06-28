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
"""
Tests for Hadoop FS.
"""
from nose.tools import assert_false, assert_true, assert_equals, assert_raises
from nose.plugins.attrib import attr
import posixfile
import random

from hadoop import mini_cluster
from hadoop.fs.exceptions import PermissionDeniedException
from hadoop.fs.hadoopfs import HadoopFileSystem

@attr('requires_hadoop')
def test_hadoopfs():
  """
  Minimal tests for a few basic file system operations.
  """
  cluster = mini_cluster.shared_cluster()
  try:
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
  finally:
    cluster.shutdown()

@attr('requires_hadoop')
def test_seek():
  """Test for DESKTOP-293 - ensure seek works in python2.4"""
  cluster = mini_cluster.shared_cluster()
  try:
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
  finally:
    cluster.shutdown()

@attr('requires_hadoop')
def test_seek_across_blocks():
  """Makes a file with a lot of blocks, seeks around"""
  cluster = mini_cluster.shared_cluster()
  try:
    fs = cluster.fs
    fs.setuser(cluster.superuser)
    f = fs.open("/fortest-blocks.txt", "w", block_size=1024)
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
  finally:
    cluster.shutdown()


@attr('requires_hadoop')
def test_exceptions():
  """
  Tests that appropriate exceptions are raised.
  """
  cluster = mini_cluster.shared_cluster()
  try:
    fs = cluster.fs
    fs.setuser(cluster.superuser)
    f = fs.open("/for_exception_test.txt", "w")
    f.write("foo")
    f.close()
    fs.chmod("/for_exception_test.txt", 0400)
    fs.setuser("notsuperuser")
    f = fs.open("/for_exception_test.txt")
    # Arguably, this should have thrown already, at open, but
    # we throw the exception lazily, when getting block locations.
    assert_raises(PermissionDeniedException, f.read)

    assert_raises(IOError, fs.open, "/test/doesnotexist.txt")
  finally:
    cluster.shutdown()

@attr('requires_hadoop')
def test_two_files_open():
  """
  See DESKTOP-510.  There was a bug where you couldn't open two files at
  the same time.  It boils down to a close_fds=True issue.  If this doesn't
  hang, all is good.
  """
  cluster = mini_cluster.shared_cluster()
  try:
    fs = cluster.fs
    fs.setuser(cluster.superuser)
    f1 = fs.open("/test_one.txt", "w")
    f2 = fs.open("/test_two.txt", "w")
    f1.write("foo")
    f2.write("bar")
    f1.close()
    f2.close()
    # This should work, not hang, etc.
  finally:
    cluster.shutdown()


def test_urlsplit():
  """Test HadoopFS urlsplit"""
  url = 'hdfs://nn.no.port/foo/bar'
  assert_equals(('hdfs', 'nn.no.port', '/foo/bar', '', ''), HadoopFileSystem.urlsplit(url))
  url = 'hdfs://nn:8020/foo/bar'
  assert_equals(('hdfs', 'nn:8020', '/foo/bar', '', ''), HadoopFileSystem.urlsplit(url))
  url = 'hdfs://nn:8020//foo//bar'
  assert_equals(('hdfs', 'nn:8020', '/foo/bar', '', ''), HadoopFileSystem.urlsplit(url))
  url = 'hdfs://nn:8020'
  assert_equals(('hdfs', 'nn:8020', '/', '', ''), HadoopFileSystem.urlsplit(url))
  url = '/foo/bar'
  assert_equals(('hdfs', '', '/foo/bar', '', ''), HadoopFileSystem.urlsplit(url))
  url = 'foo//bar'
  assert_equals(('hdfs', '', 'foo/bar', '', ''), HadoopFileSystem.urlsplit(url))

@attr('requires_hadoop')
def test_quota_argument_smarts():
  """
  Test invalid quota parameters
  """
  cluster = mini_cluster.shared_cluster()
  fs = cluster.fs
  try:
    fs.setuser(cluster.superuser)
    fs.mkdir("/tmp/foo2", 0777)

    fs.set_diskspace_quota("/tmp/foo2", 1)
    fs.set_namespace_quota("/tmp/foo2", 1)

    assert_raises(ValueError, fs.set_diskspace_quota, "/tmp/foo2", -5)

    assert_raises(ValueError, fs.set_diskspace_quota, '/', 10)
    assert_raises(ValueError, fs.set_namespace_quota, '/', 10)

    fs.set_diskspace_quota("/tmp/foo2", 1.1) # This should actually fail i think
  finally:
    fs.rmtree("/tmp/foo2")
    cluster.shutdown()

@attr('requires_hadoop')
def test_quota_space():
  """
  Lets make sure we can violate the quota in regards to diskspace
  """

  cluster = mini_cluster.shared_cluster()
  fs = cluster.fs
  try:
    fs.setuser(cluster.superuser)
    if fs.exists('/tmp/foo2'):
      fs.rmtree('/tmp/foo2')
    fs.mkdir("/tmp/foo2", 0777) # this also tests more restrictive subdirectories
    ONE_HUNDRED_192_MEGS = 1024 * 1024 * 192
    
    fs.set_diskspace_quota("/tmp/foo2", ONE_HUNDRED_192_MEGS) 
    assert_equals(fs.get_diskspace_quota("/tmp/foo2"), ONE_HUNDRED_192_MEGS)

    f = fs.open('/tmp/foo2/asdf', 'w')	 # we should be able to do this 
    f.write('a') 
    f.close()

    assert_equals(fs.get_diskspace_quota("/tmp/foo2"), ONE_HUNDRED_192_MEGS)

    fs.set_diskspace_quota("/tmp/foo2", 1) 
    assert_equals(fs.get_diskspace_quota("/tmp/foo2"), 1)

    f = fs.open('/tmp/foo2/asdfsd', 'w')	 
    f.write('a')
    assert_raises(IOError, f.close)

    fs.clear_diskspace_quota("/tmp/foo2")
    assert_equals(fs.get_diskspace_quota("/tmp/foo2"), None)

    f = fs.open('/tmp/foo2/asdfsda', 'w')	 
    f.write('a') 
    f.close()

    fs.mkdir("/tmp/baz/bar", 0777)  # this tests more permissive subdirectories
    fs.set_diskspace_quota("/tmp/baz", 1)
    fs.set_diskspace_quota("/tmp/baz/bar", ONE_HUNDRED_192_MEGS) 

    f = fs.open('/tmp/baz/bar', 'w')	 
    f.write('aaaa') #should violate the subquota
    assert_raises(IOError, f.close)

  finally:
    if fs.exists('/tmp/baz'):
      fs.rmtree("/tmp/baz")
    if fs.exists('/tmp/foo2'):
      fs.rmtree("/tmp/foo2")
    cluster.shutdown()

@attr('requires_hadoop')
def test_quota_namespace_count():
  """
  Lets make sure we can violate the number of names in a directory limitation
  """
  cluster = mini_cluster.shared_cluster()
  try:
    fs = cluster.fs
    fs.setuser(cluster.superuser)
    if fs.exists('/tmp/foo2'):
      fs.rmtree('/tmp/foo2')
    fs.mkdir("/tmp/foo2", 0777)

    # check the get_namespace_quota function
    fs.set_namespace_quota("/tmp/foo2", 4) 
    assert_equals(fs.get_namespace_quota("/tmp/foo2"), 4)

    # violate the namespace count
    for i in range(3):
      f = fs.open('/tmp/foo2/works' + str(i), 'w')
      f.write('a') 
      f.close()

    f = fs.open('/tmp/foo2/asdfsdc', 'w')
    f.write('a') 
    assert_raises(IOError, f.close)

    # Check summary stats
    summary = fs.get_usage_and_quota('/tmp/foo2')
    assert_equals(3, summary["file_count"])
    assert_equals(4, summary["file_quota"])
    assert_equals(None, summary["space_quota"])
    assert_true(None is not summary["space_used"])

    # make sure the clear works
    fs.clear_namespace_quota("/tmp/foo2")
    assert_equals(fs.get_namespace_quota("/tmp/foo2"), None)

    f = fs.open('/tmp/foo2/asdfsdd', 'w')
    f.write('a') 
    f.close()
  finally:
    if fs.exists('/tmp/foo2'):
      fs.rmtree("/tmp/foo2")
    cluster.shutdown()
