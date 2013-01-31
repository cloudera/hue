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

import logging
import os
import stat
import tempfile
import unittest

from hadoop import fs, pseudo_hdfs4
from nose.plugins.attrib import attr
from nose.tools import assert_equal, assert_true

logger = logging.getLogger(__name__)

class LocalSubFileSystemTest(unittest.TestCase):
  def setUp(self):
    self.root = tempfile.mkdtemp()
    self.fs = fs.LocalSubFileSystem(self.root)

  def tearDown(self):
    if not os.listdir(self.root):
      os.rmdir(self.root)
    else:
      logger.warning("Tests did not clean up after themselves in %s" % self.root)

  def test_resolve_path(self):
    self.assertEquals(self.root + "/", self.fs._resolve_path("/"))
    self.assertEquals(self.root + "/foo", self.fs._resolve_path("/foo"))
    self.assertRaises(fs.IllegalPathException, self.fs._resolve_path, "/../foo")
    # These are preserved, but that should be ok.
    self.assertEquals(self.root + "/bar/../foo", self.fs._resolve_path("/bar/../foo"))

  def test_open_and_remove(self):
    self.assertRaises(IOError, self.fs.open, "/notfound", "r")
    f = self.fs.open("/x", "w")
    f.write("Hello world\n")
    f.close()

    f = self.fs.open("/x")
    self.assertEquals("Hello world\n", f.read())
    f.close()

    self.fs.remove("/x")

  def test_rename(self):
    # No exceptions means this worked fine.
    self.fs.open("/x", "w").close()
    self.fs.rename("/x", "/y")
    self.fs.remove("/y")

  def test_listdir(self):
    self.fs.mkdir("/abc")
    self.fs.open("/abc/x", "w").close()
    self.fs.open("/abc/y", "w").close()

    self.assertEquals(["abc"], self.fs.listdir("/"))
    self.assertEquals(["x", "y"], sorted(self.fs.listdir("/abc")))

    self.fs.remove("/abc/x")
    self.fs.remove("/abc/y")
    self.fs.rmdir("/abc")

  def test_listdir_stats(self):
    self.fs.mkdir("/abc")
    self.fs.open("/abc/x", "w").close()
    self.fs.open("/abc/y", "w").close()

    stats = self.fs.listdir_stats("/")
    self.assertEquals(["/abc"], [s['path'] for s in stats])
    self.assertEquals(["/abc/x", "/abc/y"],
                      sorted(s['path'] for s in self.fs.listdir_stats("/abc")))

    self.fs.remove("/abc/x")
    self.fs.remove("/abc/y")
    self.fs.rmdir("/abc")


  def test_keyword_args(self):
    # This shouldn't work!
    self.assertRaises(TypeError, self.fs.open, name="/foo", mode="w")


@attr('requires_hadoop')
def test_hdfs_copy():
  minicluster = pseudo_hdfs4.shared_cluster()
  minifs = minicluster.fs

  try:
    olduser = minifs.setuser(minifs.superuser)
    minifs.chmod('/', 0777)
    minifs.setuser(olduser)

    data = "I will not make flatuent noises in class\n" * 2000
    minifs.create('/copy_test_src', permission=0646, data=data)
    minifs.create('/copy_test_dst', data="some initial data")

    minifs.copyfile('/copy_test_src', '/copy_test_dst')
    actual = minifs.read('/copy_test_dst', 0, len(data) + 100)
    assert_equal(data, actual)

    sb = minifs.stats('/copy_test_dst')
    assert_equal(0646, stat.S_IMODE(sb.mode))

  finally:
    minifs.rmtree('/copy_test_src')
    minifs.rmtree('/copy_test_dst')

@attr('requires_hadoop')
def test_hdfs_full_copy():
  minicluster = pseudo_hdfs4.shared_cluster()
  minifs = minicluster.fs

  try:
    minifs.do_as_superuser(minifs.chmod, '/', 0777)
    minifs.mkdir('/copy_test')
    minifs.mkdir('/copy_test/src')
    minifs.mkdir('/copy_test/dest')

    # File to directory copy.
    # No guarantees on file permissions at the moment.
    data = "I will not make flatuent noises in class\n" * 2000
    minifs.create('/copy_test/src/file.txt', permission=0646, data=data)
    minifs.copy('/copy_test/src/file.txt', '/copy_test/dest')
    assert_true(minifs.exists('/copy_test/dest/file.txt'))

    # Directory to directory copy.
    # No guarantees on directory permissions at the moment.
    minifs.copy('/copy_test/src', '/copy_test/dest', True)
    assert_true(minifs.exists('/copy_test/dest/src'))

    # Copy directory to file should fail.
    try:
      minifs.copy('/copy_test/src', '/copy_test/dest/file.txt', True)
    except IOError, e:
      pass
    except Exception, e:
      raise

  finally:
    minifs.rmtree('/copy_test')

@attr('requires_hadoop')
def test_hdfs_copy_from_local():
  minicluster = pseudo_hdfs4.shared_cluster()
  minifs = minicluster.fs

  olduser = minifs.setuser(minifs.superuser)
  minifs.chmod('/', 0777)
  minifs.setuser(olduser)

  path = os.path.join(tempfile.gettempdir(), 'copy_test_src')
  logging.info(path)

  data = "I will not make flatuent noises in class\n" * 2000
  f = open(path, 'w')
  f.write(data)
  f.close()

  minifs.copyFromLocal(path, '/copy_test_dst')
  actual = minifs.read('/copy_test_dst', 0, len(data) + 100)
  assert_equal(data, actual)


if __name__ == "__main__":
  logging.basicConfig()
  unittest.main()
