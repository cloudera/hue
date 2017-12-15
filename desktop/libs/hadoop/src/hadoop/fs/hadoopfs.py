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
Deprecated! Use WebHdfs instead.

Only some utils and Hdfs are still used.

Interfaces for Hadoop filesystem access via the HADOOP-4707 Thrift APIs.
"""
import errno
import logging
import os
import posixpath
import random
import subprocess
import urlparse

from django.utils.encoding import smart_str, force_unicode
from django.utils.translation import ugettext as _

from desktop.lib import i18n

import hadoop.conf
from hadoop.fs import normpath, SEEK_SET, SEEK_CUR, SEEK_END
from hadoop.fs.exceptions import PermissionDeniedException


LOG = logging.getLogger(__name__)

DEFAULT_USER = "webui"

# The number of bytes to read if not specified
DEFAULT_READ_SIZE = 1024*1024 # 1MB

# The buffer size of the pipe to hdfs -put during upload
WRITE_BUFFER_SIZE = 128*1024 # 128K

# Class that we translate into PermissionDeniedException
HADOOP_ACCESSCONTROLEXCEPTION = "org.apache.hadoop.security.AccessControlException"

# Timeout for thrift calls to NameNode
NN_THRIFT_TIMEOUT = 15
DN_THRIFT_TIMEOUT = 3

# Encoding used by HDFS namespace
HDFS_ENCODING = 'utf-8'

def encode_fs_path(path):
  """encode_fs_path(path) -> byte string in utf8"""
  return smart_str(path, HDFS_ENCODING, errors='strict')

def decode_fs_path(path):
  """decode_fs_path(bytestring) -> unicode path"""
  return force_unicode(path, HDFS_ENCODING, errors='strict')


def _coerce_exceptions(function):
  """
  Decorator that causes exceptions thrown by the decorated function
  to be coerced into generic exceptions from the hadoop.fs.exceptions
  module.
  """
  def wrapper(*args, **kwargs):
    try:
      return function(*args, **kwargs)
    except Exception, e:
      e.msg = force_unicode(e.msg, errors='replace')
      e.stack = force_unicode(e.stack, errors='replace')
      LOG.exception("Exception in Hadoop FS call " + function.__name__)
      if e.clazz == HADOOP_ACCESSCONTROLEXCEPTION:
        raise PermissionDeniedException(e.msg, e)
      else:
        raise
  return wrapper


class Hdfs(object):
  """
  An abstract HDFS proxy
  """

  @staticmethod
  def basename(path):
    return posixpath.basename(path)

  @staticmethod
  def dirname(path):
    return posixpath.dirname(path)

  @staticmethod
  def split(path):
    return posixpath.split(path)

  @staticmethod
  def join(first, *comp_list):
    return posixpath.join(first, *comp_list)

  @staticmethod
  def abspath(path):
    return posixpath.abspath(path)

  @staticmethod
  def normpath(path):
    res = posixpath.normpath(path)
    # Python normpath() doesn't eliminate leading double slashes
    if res.startswith('//'):
      return res[1:]
    return res

  @staticmethod
  def parent_path(path):
    return Hdfs.join(path, "..")

  @staticmethod
  def urlsplit(url):
    """
    Take an HDFS path (hdfs://nn:port/foo) or just (/foo) and split it into
    the standard urlsplit's 5-tuple.
    """
    i = url.find('://')
    if i == -1:
      # Not found. Treat the entire argument as an HDFS path
      return ('hdfs', '', normpath(url), '', '')
    schema = url[:i]
    if schema not in ('hdfs', 'viewfs'):
      # Default to standard for non-hdfs
      return urlparse.urlsplit(url)
    url = url[i+3:]
    i = url.find('/')
    if i == -1:
      # Everything is netloc. Assume path is root.
      return (schema, url, '/', '', '')
    netloc = url[:i]
    path = url[i:]
    return (schema, netloc, normpath(path), '', '')

  def listdir_recursive(self, path, glob=None):
    """
    listdir_recursive(path, glob=None) -> [ entry names ]

    Get directory entry names without stats, recursively.
    """
    paths = [path]
    while paths:
      path = paths.pop()
      if self.isdir(path):
        hdfs_paths = self.listdir_stats(path, glob)
        paths[:0] = [x.path for x in hdfs_paths]
      yield path

  def create_home_dir(self, home_path=None):
    if home_path is None:
      home_path = self.get_home_dir()

    from useradmin.conf import HOME_DIR_PERMISSIONS
    mode = int(HOME_DIR_PERMISSIONS.get(), 8)
    if not self.exists(home_path):
      user = self.user
      try:
        try:
          self.setuser(self.superuser)
          self.mkdir(home_path)
          self.chmod(home_path, mode)
          self.chown(home_path, user, user)
        except IOError:
          msg = 'Failed to create home dir ("%s") as superuser %s' % (home_path, self.superuser)
          LOG.exception(msg)
          raise
      finally:
        self.setuser(user)

  def copyFromLocal(self, local_src, remote_dst, mode=0755):
    remote_dst = remote_dst.endswith(posixpath.sep) and remote_dst[:-1] or remote_dst
    local_src = local_src.endswith(posixpath.sep) and local_src[:-1] or local_src

    if os.path.isdir(local_src):
      self._copy_dir(local_src, remote_dst, mode)
    else:
      (basename, filename) = os.path.split(local_src)
      self._copy_file(local_src, self.isdir(remote_dst) and self.join(remote_dst, filename) or remote_dst)

  def _copy_dir(self, local_dir, remote_dir, mode=0755):
    self.mkdir(remote_dir, mode=mode)

    for f in os.listdir(local_dir):
      local_src = os.path.join(local_dir, f)
      remote_dst = self.join(remote_dir, f)

      if os.path.isdir(local_src):
        self._copy_dir(local_src, remote_dst, mode)
      else:
        self._copy_file(local_src, remote_dst)

  def _copy_file(self, local_src, remote_dst, chunk_size=1024 * 1024 * 64):
    if os.path.isfile(local_src):
      if self.exists(remote_dst):
        LOG.info(_('%(remote_dst)s already exists. Skipping.') % {'remote_dst': remote_dst})
        return
      else:
        LOG.info(_('%(remote_dst)s does not exist. Trying to copy.') % {'remote_dst': remote_dst})

      src = file(local_src)
      try:
        try:
          self.create(remote_dst, permission=0755)
          chunk = src.read(chunk_size)
          while chunk:
            self.append(remote_dst, chunk)
            chunk = src.read(chunk_size)
          LOG.info(_('Copied %s -> %s.') % (local_src, remote_dst))
        except:
          LOG.exception(_('Copying %s -> %s failed.') % (local_src, remote_dst))
          raise
      finally:
        src.close()
    else:
      LOG.info(_('Skipping %s (not a file).') % local_src)


  @_coerce_exceptions
  def mktemp(self, subdir='', prefix='tmp', basedir=None):
    """
    mktemp(prefix) ->  <temp_dir or basedir>/<subdir>/prefix.<rand>
    Return a unique temporary filename with prefix in the cluster's temp dir.
    """
    RANDOM_BITS = 64

    base = self.join(basedir or self._temp_dir, subdir)
    if not self.isdir(base):
      self.mkdir(base)

    while True:
      name = prefix + '.' + str(random.getrandbits(RANDOM_BITS))
      candidate = self.join(base, name)
      if not self.exists(candidate):
        return candidate

  def mkswap(self, filename, subdir='', suffix='swp', basedir=None):
    """
    mkswap(filename, suffix) ->  <temp_dir or basedir>/<subdir>/filename.<suffix>
    Return a unique temporary filename with prefix in the cluster's temp dir.
    """
    RANDOM_BITS = 64

    base = self.join(basedir or self._temp_dir, subdir)
    if not self.isdir(base):
      self.mkdir(base)

    candidate = self.join(base, "%s.%s" % (filename, suffix))
    return candidate

  def exists(self):
    raise NotImplementedError(_("%(function)s has not been implemented.") % {'function': 'exists'})

  def do_as_user(self):
    raise NotImplementedError(_("%(function)s has not been implemented.") % {'function': 'do_as_user'})

  def create(self):
    raise NotImplementedError(_("%(function)s has not been implemented.") % {'function': 'exists'})

  def append(self):
    raise NotImplementedError(_("%(function)s has not been implemented.") % {'function': 'append'})

  def mkdir(self):
    raise NotImplementedError(_("%(function)s has not been implemented.") % {'function': 'mkdir'})

  def isdir(self):
    raise NotImplementedError(_("%(function)s has not been implemented.") % {'function': 'isdir'})

  def listdir_stats(self):
    raise NotImplementedError(_("%(function)s has not been implemented.") % {'function': 'listdir_stats'})





def require_open(func):
  """
  Decorator that ensures that the file instance isn't closed when the
  function is run.
  """
  def wrapper(self, *args, **kwargs):
    if self.closed:
      raise IOError(errno.EBADF, "I/O operation on closed file")
    return func(self, *args, **kwargs)
  return wrapper




class File(object):
  """ Represents an open file on HDFS. """

  def __init__(self, fs, path, mode="r", buffering=False):
    self.fs = fs
    self.path = normpath(path)
    self.pos = 0
    self.closed = False
    self._block_cache = BlockCache()

    if buffering or mode != "r":
      raise Exception("buffering and write support not yet implemented") # NYI

    stat = self._stat()

    if stat is None:
      raise IOError(errno.ENOENT, "No such file or directory: '%s'" % path)
    if stat.isDir:
      raise IOError(errno.EISDIR, "Is a directory: '%s'" % path)
    #TODO(todd) somehow we need to check permissions here - maybe we need an access() call?

  # Minimal context manager implementation.
  # See: http://www.python.org/doc/2.5.2/lib/typecontextmanager.html
  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()
    return False # don't supress exceptions.

  @require_open
  def seek(self, offset, whence=0):
    """ Set the file pointer to the given spot. @see file.seek """
    if whence == SEEK_SET:
      self.pos = offset
    elif whence == SEEK_CUR:
      self.pos += offset
    elif whence == SEEK_END:
      self.pos = self._stat().length + offset
    else:
      raise IOError(errno.EINVAL, "Invalid argument to seek for whence")

  @require_open
  def tell(self):
    return self.pos


  def _get_block(self, pos):
    """Return the Block instance that contains the given offset"""
    cached_block = self._block_cache.find_block(pos)
    if cached_block:
      return cached_block

    # Cache "miss" - fetch ahead 500MB worth of blocks
    new_blocks = self.fs._get_blocks(self.path, pos, 500*1024*1024)
    self._block_cache.insert_new_blocks(new_blocks)
    result = self._block_cache.find_block(pos)
    if not result:
      raise IOError("No block for position %d in file %s" % (pos, self.path))

    return result

  @require_open
  def _read_in_block(self, length=DEFAULT_READ_SIZE):
    """
    Tries to read up to length bytes, but will often read fewer, since
    a single call will not read across a block boundary.
    """
    end_pos = min(self.pos + length, self._stat().length)
    # If we're at EOF, return empty string
    if end_pos == self.pos:
      return ""

    block = self._get_block(self.pos)
    assert _block_contains_pos(block, self.pos)
    assert block.path == self.path
    in_block_pos = self.pos - block.startOffset
    assert in_block_pos >= 0
    in_block_len = min(length, block.numBytes - in_block_pos)
    result = self.fs._read_block(block, in_block_pos, in_block_len)
    self.pos += len(result)
    assert self.pos <= end_pos
    return result

  @require_open
  def read(self, length=DEFAULT_READ_SIZE):
    """
    Read the given number of bytes from this file.
    If EOF has been reached, returns the empty string.

    @param length the number of bytes wanted
    """
    result = []
    read_so_far = 0
    while read_so_far < length:
      this_data = self._read_in_block(length - read_so_far)
      if this_data == "": # eof
        break
      read_so_far += len(this_data)
      result.append(this_data)
    return "".join(result)

  def close(self):
    self.closed = True

  def _stat(self):
    if not hasattr(self, "_stat_cache"):
      self._stat_cache = self.fs._hadoop_stat(self.path)
    return self._stat_cache


class FileUpload(object):
  """A write-only file that supports no seeking and cannot exist prior to
  opening.
  """
  def __init__(self, fs, path, mode="w", block_size=None):
    self.fs = fs
    self.closed = False
    assert mode == "w"
    extra_confs = []
    if block_size:
      extra_confs.append("-Ddfs.block.size=%d" % block_size)
    self.subprocess_cmd = [self.fs.hadoop_bin_path,
                           "jar",
                           hadoop.conf.SUDO_SHELL_JAR.get(),
                           self.fs.user,
                           "-Dfs.default.name=" + self.fs.uri] + \
                           extra_confs + \
                           ["-put", "-", encode_fs_path(path)]

    self.subprocess_env = i18n.make_utf8_env()

    if self.subprocess_env.has_key('HADOOP_CLASSPATH'):
      self.subprocess_env['HADOOP_CLASSPATH'] += ':' + hadoop.conf.HADOOP_EXTRA_CLASSPATH_STRING.get()
    else:
      self.subprocess_env['HADOOP_CLASSPATH'] = hadoop.conf.HADOOP_EXTRA_CLASSPATH_STRING.get()

    if hadoop.conf.HADOOP_CONF_DIR.get():
      self.subprocess_env['HADOOP_CONF_DIR'] = hadoop.conf.HADOOP_CONF_DIR.get()

    self.path = path
    self.putter = subprocess.Popen(self.subprocess_cmd,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   close_fds=True,
                                   env=self.subprocess_env,
                                   bufsize=WRITE_BUFFER_SIZE)
  @require_open
  def write(self, data):
    """May raise IOError, particularly EPIPE"""
    self.putter.stdin.write(data)

  @require_open
  def close(self):
    try:
      (stdout, stderr) = self.putter.communicate()
    except IOError, ioe:
      logging.debug("Saw IOError writing %r" % self.path, exc_info=1)
      if ioe.errno == errno.EPIPE:
        stdout, stderr = self.putter.communicate()

    self.closed = True
    if stderr:
      LOG.warn("HDFS FileUpload (cmd='%s', env='%s') outputted stderr:\n%s" %
                   (repr(self.subprocess_cmd), repr(self.subprocess_env), stderr))
    if stdout:
      LOG.info("HDFS FileUpload (cmd='%s', env='%s') outputted stdout:\n%s" %
                   (repr(self.subprocess_cmd), repr(self.subprocess_env), stdout))
    if self.putter.returncode != 0:
      raise IOError("hdfs put returned bad code: %d\nstderr: %s" %
                    (self.putter.returncode, stderr))
    LOG.info("Completed upload: %s" % repr(self.subprocess_cmd))

  @require_open
  def flush(self):
    self.putter.stdin.flush()


def _block_contains_pos(block, pos):
  return pos >= block.startOffset and pos < block.startOffset + block.numBytes


class BlockCache(object):
  """
  A cache of block locations used by a single HDFS input file.
  Essentially this keeps the blocks in sorted order and does
  binary search to find the block that contains a given offset.
  It also provides the ability to merge in the response of a NN
  getBlocks response to the cache.
  """

  def __init__(self):
    self.blocks = []

  def find_block(self, pos, _min_idx=0, _max_idx=None):
    """
    Return the Block object that contains the specified
    position pos, or None if it is not in the cache.
    """
    if _max_idx is None:
      _max_idx = len(self.blocks) - 1

    if _max_idx < _min_idx:
      return None

    pivot_idx = (_max_idx + _min_idx) / 2
    pivot_block = self.blocks[pivot_idx]
    if pos < pivot_block.startOffset:
      return self.find_block(pos, _min_idx, pivot_idx - 1)
    elif pos >= pivot_block.startOffset + pivot_block.numBytes:
      return self.find_block(pos, pivot_idx + 1, _max_idx)
    else:
      return pivot_block

  def insert_new_blocks(self, new_blocks):
    """
    Merge a list of Block objects from the NN into the list
    of cached blocks.

    If the set of blocks overlaps, the new blocks take precedence.
    """

    # We could do a more efficient merge here since both lists
    # are already sorted, but these data structures are small, so let's
    # do the easy thing.
    blocks_dict = dict( (b.blockId, b) for b in self.blocks )

    # Merge in new data to dictionary
    for nb in new_blocks:
      blocks_dict[nb.blockId] = nb

    # Convert back to sorted list
    block_list = blocks_dict.values()
    block_list.sort(cmp=lambda a,b: cmp(a.startOffset, b.startOffset))

    # Update cache with new data
    self.blocks = block_list
