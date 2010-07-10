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
Interfaces for Hadoop filesystem access via the HADOOP-4707 Thrift APIs.
"""
import errno
import logging
import os
import posixpath
import stat as statconsts
import subprocess
import sys
import urlparse

from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol

from desktop.lib import thrift_util
from hadoop.api.hdfs import Namenode, Datanode
from hadoop.api.hdfs.constants import QUOTA_DONT_SET, QUOTA_RESET
from hadoop.api.common.ttypes import RequestContext, IOException
from hadoop.fs import normpath
from hadoop.fs.exceptions import PermissionDeniedException

# SEEK_SET and family is found in posixfile or os, depending on the python version
if sys.version_info[:2] < (2, 5):
  import posixfile
  _tmp_mod = posixfile
else:
  _tmp_mod = os
SEEK_SET, SEEK_CUR, SEEK_END = _tmp_mod.SEEK_SET, _tmp_mod.SEEK_CUR, _tmp_mod.SEEK_END
del _tmp_mod

LOG = logging.getLogger(__name__)

DEFAULT_USER = "webui"
DEFAULT_GROUPS = ["webui"]

# The number of bytes to read if not specified
DEFAULT_READ_SIZE = 1024*1024 # 1MB

# The buffer size of the pipe to hdfs -put during upload
WRITE_BUFFER_SIZE = 128*1024 # 128K

# Class that we translate into PermissionDeniedException
HADOOP_ACCESSCONTROLEXCEPTION="org.apache.hadoop.security.AccessControlException"

# Timeout for thrift calls to NameNode
NN_THRIFT_TIMEOUT = 15
DN_THRIFT_TIMEOUT = 3

class HadoopFileSystem(object):
  """
  Implementation of Filesystem APIs through Thrift to a Hadoop cluster.
  """

  def __init__(self, host, thrift_port, hdfs_port=8020, hadoop_bin_path="hadoop"):
    """
    @param host hostname or IP of the namenode
    @param thrift_port port on which the Thrift plugin is listening
    @param hdfs_port port on which NameNode IPC is listening
    @param hadoop_bin_path path to find the hadoop wrapper script on the
                           installed system - default is fine if it is in
                           the user's PATH env
    """
    self.host = host
    self.thrift_port = thrift_port
    self.hdfs_port = hdfs_port
    self.hadoop_bin_path = hadoop_bin_path
    self._resolve_hadoop_path()

    self.nn_client = thrift_util.get_client(Namenode.Client, host, thrift_port, service_name="HDFS Namenode",
                                            timeout_seconds=NN_THRIFT_TIMEOUT)

    self.request_context = RequestContext()
    self.setuser(DEFAULT_USER, DEFAULT_GROUPS)
    LOG.debug("Initialized HadoopFS: %s:%d (%s)", host, thrift_port, hadoop_bin_path)

  def _get_hdfs_base(self):
    return "hdfs://%s:%d" % (self.host, self.hdfs_port) # TODO(todd) fetch the port from the NN thrift


  def _coerce_exceptions(function):
    """
    Decorator that causes exceptions thrown by the decorated function
    to be coerced into generic exceptions from the hadoop.fs.exceptions
    module.
    """
    def wrapper(*args, **kwargs):
      try:
        return function(*args, **kwargs)
      except IOException, e:
        LOG.exception("Exception in Hadoop FS call " + function.__name__)
        if e.clazz == HADOOP_ACCESSCONTROLEXCEPTION:
          raise PermissionDeniedException(e.msg, e)
        else:
          raise
    return wrapper

  def _resolve_hadoop_path(self):
    """The hadoop_bin_path configuration may be a non-absolute path, in which case
    it's checked against $PATH.

    If the hadoop binary can't be found anywhere, raises an Exception.
    """
    for path_dir in os.getenv("PATH", "").split(os.pathsep):
      path = os.path.join(path_dir, self.hadoop_bin_path)
      if os.path.exists(path):
        self.hadoop_bin_path = os.path.abspath(path)
        return

    raise Exception("Hadoop binary (%s) does not exist." % self.hadoop_bin_path)


  @property
  def uri(self):
    return self._get_hdfs_base()

  @property
  def superuser(self):
    """
    Retrieves the user that Hadoop considers as
    "superuser" by looking at ownership of /.
    This is slightly inaccurate.
    """
    return self.stats("/")["user"]

  def setuser(self, user, groups=None):
    # Hadoop UGI *must* have at least one group, so we mirror
    # the username as a group if not specified
    if not groups:
      groups = [user]
    if not self.request_context.confOptions:
      self.request_context.confOptions = {}
    self.ugi = ",".join([user] + groups)
    self.request_context.confOptions['hadoop.job.ugi'] = self.ugi
    self.user = user
    self.groups = groups

  @_coerce_exceptions
  def open(self, path, mode="r", *args, **kwargs):
    if mode == "w":
      return FileUpload(self, path, mode, *args, **kwargs)
    return File(self, path, mode, *args, **kwargs)

  @_coerce_exceptions
  def remove(self, path):
    stat = self._hadoop_stat(path)
    if not stat:
      raise IOError("File not found: %s" % path)
    if stat.isDir:
      raise IOError("Is a directory: %s" % path)

    success = self.nn_client.unlink(
      self.request_context, normpath(path), recursive=False)
    if not success:
      raise IOError("Unlink failed")

  @_coerce_exceptions
  def mkdir(self, path, mode=0755):
    # TODO(todd) there should be a mkdir that isn't mkdirHIER
    # (this is mkdir -p I think)
    success = self.nn_client.mkdirhier(self.request_context, normpath(path), mode)
    if not success:
      raise IOError("mkdir failed")

  def _rmdir(self, path, recursive=False):
    stat = self._hadoop_stat(path)
    if not stat:
      raise IOError("Directory not found: %s" % (path,))
    if not stat.isDir:
      raise IOError("Is not a directory: %s" % (path,))

    success = self.nn_client.unlink(
      self.request_context, normpath(path), recursive=recursive)
    if not success:
      raise IOError("Unlink failed")

  @_coerce_exceptions
  def rmdir(self, path):
    return self._rmdir(path)

  @_coerce_exceptions
  def rmtree(self, path):
    return self._rmdir(path, True)

  @_coerce_exceptions
  def listdir(self, path):
    stats = self.nn_client.ls(self.request_context, normpath(path))
    return [self.basename(stat.path) for stat in stats]

  @_coerce_exceptions
  def listdir_stats(self, path):
    stats = self.nn_client.ls(self.request_context, normpath(path))
    return [self._unpack_stat(s) for s in stats]

  @_coerce_exceptions
  def get_content_summaries(self, paths):
    return self.nn_client.multiGetContentSummary(self.request_context, [normpath(path) for path in paths])

  @_coerce_exceptions
  def rename(self, old, new):
    success = self.nn_client.rename(
      self.request_context, normpath(old), normpath(new))
    if not success: #TODO(todd) these functions should just throw if failed
      raise IOError("Rename failed")

  @_coerce_exceptions
  def rename_star(self, old_dir, new_dir):
    """Equivalent to `mv old_dir/* new"""
    if not self.isdir(old_dir):
      raise IOError("'%s' is not a directory" % (old_dir,))
    if not self.exists(new_dir):
      self.mkdir(new_dir)
    elif not self.isdir(new_dir):
      raise IOError("'%s' is not a directory" % (new_dir,))
    ls = self.listdir(old_dir)
    for dirent in ls:
      self.rename(HadoopFileSystem.join(old_dir, dirent),
                  HadoopFileSystem.join(new_dir, dirent))

  @_coerce_exceptions
  def exists(self, path):
    stat = self._hadoop_stat(path)
    return stat is not None

  @_coerce_exceptions
  def isfile(self, path):
    stat = self._hadoop_stat(path)
    if stat is None:
      return False
    return not stat.isDir

  @_coerce_exceptions
  def isdir(self, path):
    stat = self._hadoop_stat(path)
    if stat is None:
      return False
    return stat.isDir

  @_coerce_exceptions
  def stats(self, path, raise_on_fnf=True):
    stat = self._hadoop_stat(path)
    if not stat:
      if raise_on_fnf:
        raise IOError("File %s not found" % path)
      else:
        return None
    ret = self._unpack_stat(stat)
    return ret

  @_coerce_exceptions
  def chmod(self, path, mode):
    self.nn_client.chmod(self.request_context, normpath(path), mode)

  @_coerce_exceptions
  def chown(self, path, user, group):
    self.nn_client.chown(self.request_context, normpath(path), user, group)

  @_coerce_exceptions
  def get_namenode_info(self):
    (capacity, used, available) = self.nn_client.df(self.request_context)
    return dict(
      usage=dict(capacity_bytes=capacity,
                 used_bytes=used,
                 available_bytes=available),
      )
  @_coerce_exceptions
  def _get_blocks(self, path, offset, length):
    """
    Get block locations from the Name Node. Returns an array of Block
    instances that might look like:
      [ Block(path='/user/todd/motd', genStamp=1001, blockId=5564389078175231298,
        nodes=[DatanodeInfo(xceiverCount=1, capacity=37265149952, name='127.0.0.1:50010',
        thriftPort=53417, state=1, remaining=18987925504, host='127.0.0.1',
        storageID='DS-1238582576-127.0.1.1-50010-1240968238474', dfsUsed=36864)], numBytes=424)]
    """
    return self.nn_client.getBlocks(self.request_context, normpath(path), offset, length)


  def _hadoop_stat(self, path):
    """Returns None if file does not exist."""
    try:
      stat = self.nn_client.stat(self.request_context, normpath(path))
      return stat
    except IOException, ioe:
      if ioe.clazz == 'java.io.FileNotFoundException':
        return None
      raise

  @_coerce_exceptions
  def _read_block(self, block, offset, len):
    """
    Reads a chunk of data from the given block from the first available
    datanode that serves it.

    @param block a thrift Block object
    @param offset offset from the beginning of the block (not file)
    @param len the number of bytes to read
    """
    errs = []
    for node in block.nodes:
      dn_conn = self._connect_dn(node)
      try:
        try:
          data = dn_conn.readBlock(self.request_context, block, offset, len)
          return data.data
        except Exception, e:
          errs.append(e)
      finally:
        dn_conn.close()

    raise IOError("Could not read block %s from any replicas: %s" % (block, repr(errs)))

  @_coerce_exceptions
  def set_diskspace_quota(self, path, size):
    """
    Set the diskspace quota of a given path.
    @param path The path to the given hdfs resource
    @param size The amount of bytes that a given subtree of files can grow to.
    """

    if normpath(path) == '/':
      raise ValueError('Cannot set quota for "/"')

    if size < 0:
      raise ValueError("The size quota should be 0 or positive or unset")

    self.nn_client.setQuota(self.request_context, normpath(path), QUOTA_DONT_SET, size)


  @_coerce_exceptions
  def set_namespace_quota(self, path, num_files):
    """
    Set the maximum number of files of a given path.
    @param path The path to the given hdfs resource
    @param num_files The amount of files that can exist within that subtree.
    """

    if normpath(path) == '/':
      raise ValueError('Cannot set quota for "/"')

    if num_files < 0:
      raise ValueError("The number of files quota should be 0 or positive or unset")

    self.nn_client.setQuota(self.request_context, normpath(path), num_files, QUOTA_DONT_SET)

  @_coerce_exceptions
  def clear_diskspace_quota(self, path):
    """
    Remove the diskspace quota at a given path
    """
    self.nn_client.setQuota(self.request_context, normpath(path), QUOTA_DONT_SET, QUOTA_RESET)

  @_coerce_exceptions
  def clear_namespace_quota(self, path):
    """
    Remove the namespace quota at a given path
    """
    self.nn_client.setQuota(self.request_context, normpath(path), QUOTA_RESET, QUOTA_DONT_SET)


  @_coerce_exceptions
  def get_diskspace_quota(self, path):
    """
    Get the current space quota in bytes for disk space. None if it is unset
    """
    space_quota = self.nn_client.getContentSummary(self.request_context, normpath(path)).spaceQuota
    if space_quota == QUOTA_RESET or space_quota == QUOTA_DONT_SET:
      return None
    else:
      return space_quota


  @_coerce_exceptions
  def get_namespace_quota(self, path):
    """
    Get the current quota in number of files. None if it is unset
    """
    file_count_quota = self.nn_client.getContentSummary(self.request_context, normpath(path)).quota
    if file_count_quota == QUOTA_RESET or file_count_quota == QUOTA_DONT_SET:
      return None
    else:
      return file_count_quota

  @_coerce_exceptions
  def get_usage_and_quota(self, path):
    """
    Returns a dictionary with "file_count", "file_quota",
    "space_used", and "space_quota".  The quotas
    may be None.
    """
    summary = self.nn_client.getContentSummary(self.request_context, normpath(path))
    ret = dict()
    ret["file_count"] = summary.fileCount
    ret["space_used"] = summary.spaceConsumed
    if summary.quota in (QUOTA_RESET, QUOTA_DONT_SET):
      ret["file_quota"] = None
    else:
      ret["file_quota"] = summary.quota
    if summary.spaceQuota in (QUOTA_RESET, QUOTA_DONT_SET):
      ret["space_quota"] = None
    else:
      ret["space_quota"] = summary.spaceQuota
    return ret

  def _connect_dn(self, node):
    sock = TSocket.TSocket(node.host, node.thriftPort)
    sock.setTimeout(int(DN_THRIFT_TIMEOUT * 1000))
    transport = TTransport.TBufferedTransport(sock)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Datanode.Client(protocol)
    transport.open()
    client.close = lambda: transport.close()
    return client


  @staticmethod
  def _unpack_stat(stat):
    """Unpack a Thrift "Stat" object into a dictionary that looks like fs.stat"""
    mode = stat.perms
    if stat.isDir:
      mode |= statconsts.S_IFDIR
    else:
      mode |= statconsts.S_IFREG

    return {
      'path': stat.path,
      'size': stat.length,
      'mtime': stat.mtime / 1000,
      'mode': mode,
      'user': stat.owner,
      'group': stat.group,
      }

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
  def urlsplit(url):
    """
    Take an HDFS path (hdfs://nn:port/foo) or just (/foo) and split it into
    the standard urlsplit's 5-tuple.
    """
    i = url.find('://')
    if i == -1:
      # Not found. Treat the entire argument as an HDFS path
      return ('hdfs', '', normpath(url), '', '')
    if url[:i] != 'hdfs':
      # Default to standard for non-hdfs
      return urlparse.urlsplit(url)
    url = url[i+3:]
    i = url.find('/')
    if i == -1:
      # Everything is netloc. Assume path is root.
      return ('hdfs', url, '/', '', '')
    netloc = url[:i]
    path = url[i:]
    return ('hdfs', netloc, normpath(path), '', '')


def require_open(func):
  """
  Decorator that ensures that the file instance isn't closed when the
  function is run.
  """
  def wrapper(self, *args, **kwargs):
    if self.closed:
      raise IOError("I/O operation on closed file")
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
      raise IOError("No such file or directory: '%s'" % path)
    if stat.isDir:
      raise IOError("Is a directory: '%s'" % path)
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
      raise IOError("Invalid argument to seek for whence")

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
                           "dfs",
                           "-Dfs.default.name=" + self.fs._get_hdfs_base(),
                           "-Dhadoop.job.ugi=" + self.fs.ugi] + \
                           extra_confs + \
                           ["-put", "-", path]
    self.path = path
    self.putter = subprocess.Popen(self.subprocess_cmd,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
           close_fds=True,
                                   bufsize=WRITE_BUFFER_SIZE)
  @require_open
  def write(self, data):
    self.putter.stdin.write(data)

  @require_open
  def close(self):
    try:
      (stdout, stderr) = self.putter.communicate()
    except IOError, ioe:
        logging.debug("Saw IOError writing %r" % self.path, exc_info=1)
        if ioe.errno == 32: # Broken Pipe
           stdout, stderr = self.putter.communicate()
    self.closed = True
    if stderr:
      LOG.warn("HDFS FileUpload (cmd='%s')outputted stderr:\n%s" %
                   (repr(self.subprocess_cmd), stderr))
    if stdout:
      LOG.info("HDFS FileUpload (cmd='%s')outputted stdout:\n%s" %
                   (repr(self.subprocess_cmd), stdout))
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
