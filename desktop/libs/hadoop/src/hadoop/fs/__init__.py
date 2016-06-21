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
Interfaces and abstractions for filesystem access.

We should be agnostic whether we're using a "temporary" file
system, rooted in a local tmp dir, or whether we're using
a true HDFS.  This file defines the interface.

Note that PEP 355 (Path - object oriented filesystem paths) did
not pass.  Many file system methods are in __builtin__, os, or
os.path, and take strings representing filenames as arguments.
We maintain this usage of paths as arguments.

When possible, the interfaces here have fidelity to the
native python interfaces.
"""

import __builtin__
import errno
import grp
import logging
import os
import posixpath
import pwd
import re
import shutil
import stat
import sys

SEEK_SET, SEEK_CUR, SEEK_END = os.SEEK_SET, os.SEEK_CUR, os.SEEK_END


# The web (and POSIX) always uses forward slash as a separator
LEADING_DOUBLE_SEPARATORS = re.compile("^" + posixpath.sep*2)

def normpath(path):
  """
  Eliminates double-slashes.

  Oddly, posixpath.normpath doesn't eliminate leading double slashes,
  but it does clean-up triple-slashes.
  """
  p = posixpath.normpath(path)
  return LEADING_DOUBLE_SEPARATORS.sub(posixpath.sep, p)


class IllegalPathException(Exception):
  pass

class LocalSubFileSystem(object):
  """
  Facade around normal python filesystem calls, for a temporary/local
  file system rooted in a root directory.  This is intended for testing,
  and is not a secure chroot alternative.

  So far, this doesn't have a notion of current working dir, so all
  paths are "absolute".  I dislike the state that having cwd's implies,
  but it may be convenient.

  TODO(philip):
  * chown: want to implement with names, not uids.
  * chmod
  * stat: perhaps implement "stats" which returns a dictionary;
    Hadoop and posix have different stats
  * set_replication: no equivalent

  * file-system level stats

  I think this covers all the functionality in "src/contrib/thriftfs/if/hadoopfs.thrift",
  but there may be some bits missing.  The implementation of the file-like object
  for HDFS will be a bit tricky: open(f, "w") is generally the equivalent
  of createFile, but it has to handle the case where f already
  exists (in which case the best we can do is append, if that).
  """

  def __init__(self, root):
    """
    A file system rooted in root.
    """
    self.root = root
    self.name = "file://%s" % self.root
    if not os.path.isdir(root):
      logging.fatal("Root(%s) not found." % root + 
        "  Perhaps you need to run manage.py create_test_fs")

  def _resolve_path(self, path):
    """
    Returns path to use in native file system.
    """
    # Strip leading "/"
    if not path.startswith("/"):
      raise IllegalPathException("Path %s must start with leading /." % path)

    path = path.lstrip("/")
    joined = os.path.join(self.root, path)
    absolute = os.path.abspath(joined)
    normalized = os.path.normpath(absolute)
    prefix = os.path.commonprefix([self.root, normalized])
    if prefix != self.root:
      raise IllegalPathException("Path %s is not valid." % path)
    return joined

  def _unresolve_path(self, path):
    """
    Given an absolute path within the wrapped filesystem,
    return the path that the user of this class sees.
    """
    # Resolve it to make it realy absolute
    assert path.startswith(self.root)
    return path[len(self.root):]

  def _wrap(f, paths=None, users=None, groups=None):
    """
    Wraps an existing function f, and transforms
    path arguments to "resolved paths" and
    user arguments to uids.

    By default transforms the first (zeroth) argument as
    a path, but can be customized.

    This lets us write:
      def open(self, name, mode="r"):
        return open(self._resolve_path(name), mode)
    as
      open = _wrap(__builtin__.open)

    NOTE: No transformation is done on the keyword args;
    they are not accepted.  (The alternative would be to
    require the names of the keyword transformations.)
    """
    if users is None:
      users = []
    if groups is None:
      groups = []
    if paths is None and 0 not in users and 0 not in groups:
      paths = [0]
    # complicated way of taking the intersection of three lists.
    assert not reduce(set.intersection, map(set, [paths, users, groups]))
    def wrapped(*args):
      self = args[0]
      newargs = list(args[1:])
      for i in paths:
        newargs[i] = self._resolve_path(newargs[i])
      for i in users:
        newargs[i] = pwd.getpwnam(newargs[i]).pw_uid
      for i in groups:
        newargs[i] = grp.getgrnam(newargs[i]).gr_gid

      return f(*newargs)

    return wrapped

  # These follow their namesakes.
  open = _wrap(__builtin__.open)
  remove = _wrap(os.remove)
  mkdir = _wrap(os.mkdir)
  rmdir = _wrap(os.rmdir)
  listdir = _wrap(os.listdir)
  rename = _wrap(os.rename, paths=[0,1])
  exists = _wrap(os.path.exists)
  isfile = _wrap(os.path.isfile)
  isdir = _wrap(os.path.isdir)
  chmod = _wrap(os.chmod)
  join = _wrap(os.path.join)
  # This could be provided with an error_handler
  rmtree = _wrap(shutil.rmtree)
  chown = _wrap(os.chown, paths=[0], users=[1], groups=[2])

  @property
  def uri(self):
    return self.name

  def stats(self, path, raise_on_fnf=True):
    path = self._resolve_path(path)
    try:
      statobj = os.stat(path)
    except OSError, ose:
      if ose.errno == errno.ENOENT and not raise_on_fnf:
        return None
      raise
    ret = dict()
    ret["path"] = self._unresolve_path(path)
    ret["size"] = statobj[stat.ST_SIZE]
    ret["mtime"] = statobj[stat.ST_MTIME]
    ret["mode"] = statobj[stat.ST_MODE]
    ret["user"] = pwd.getpwuid(statobj[stat.ST_UID]).pw_name
    ret["group"] = grp.getgrgid(statobj[stat.ST_GID]).gr_name

    return ret

  def setuser(self, user, groups=None):
    pass

  def status(self):
    return FakeStatus()

  def listdir_stats(self, path):
    """
    This is an equivalent of listdir that, instead of returning file names,
    returns a list of stats instead.
    """
    listdir_files = self.listdir(path)
    paths = [posixpath.join(path, f) for f in listdir_files]
    return [self.stats(path) for path in paths]

  def __repr__(self):
    return "LocalFileSystem(%s)" % repr(self.root)

class FakeStatus(object):
  """
  A fake implementation of HDFS health RPCs.

  These follow the thrift naming conventions,
  but return dicts or arrays of dicts,
  because they will be encoded as JSON.
  """
  def get_messages(self):
    """Warnings/lint checks."""
    return [
      dict(type="WARNING",message="All your base belong to us."),
      dict(type="INFO", message="Hamster Dance!")
    ]

  def get_health(self):
    o = dict()
    GB = 1024*1024*1024
    o["bytesTotal"] = 5*GB
    o["bytesUsed"] = 5*GB/2
    o["bytesRemaining"] = 2*GB
    o["bytesNonDfs"] = GB/2
    o["liveDataNodes"] = 13
    o["deadDataNodes"] = 2
    o["upgradeStatus"] = dict(version=13, percentComplete=100, finalized=True)
    return o

  def get_datanode_report(self):
    r = []
    for i in range(0, 13):
      dinfo = dict()
      dinfo["name"] = "fake-%d" % i
      dinfo["storageID"] = "fake-id-%d" % i
      dinfo["host"] = "fake-host-%d" % i
      dinfo["capacity"] =  123456789
      dinfo["dfsUsed"] =    23456779
      dinfo["remaining"] = 100000010
      dinfo["xceiverCount"] = 3
      dinfo["state"] = "NORMAL_STATE"
      r.append(dinfo)
    for i in range(0, 2):
      dinfo = dict()
      dinfo["name"] = "fake-dead-%d" % i
      dinfo["storageID"] = "fake-dead-id-%d" % i
      dinfo["host"] = "fake-dead-host-%d" % i
      dinfo["capacity"] =  523456789
      dinfo["dfsUsed"] =    23456779
      dinfo["remaining"] = 500000010
      dinfo["xceiverCount"] = 3
      dinfo["state"] = "DECOMISSION_INPROGRESS"
      r.append(dinfo)
    return r
