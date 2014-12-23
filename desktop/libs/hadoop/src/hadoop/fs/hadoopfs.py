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
import stat as statconsts
import subprocess
import urlparse
import threading

from thrift.transport import TTransport

from django.utils.encoding import smart_str, force_unicode
from django.utils.translation import ugettext as _
from desktop.lib import thrift_util, i18n
from desktop.lib.conf import validate_port
from hadoop.api.hdfs import Namenode, Datanode
from hadoop.api.hdfs.constants import QUOTA_DONT_SET, QUOTA_RESET
from hadoop.api.common.ttypes import RequestContext, IOException
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


def test_fs_configuration(fs_config, hadoop_bin_conf):
  """Test FS configuration. Returns list of (confvar, error)."""
  TEST_FILE = '/tmp/.hue_config_test.%s' % (random.randint(0, 9999999999))
  res = [ ]

  res.extend(validate_port(fs_config.NN_THRIFT_PORT))
  res.extend(validate_port(fs_config.NN_HDFS_PORT))
  if res:
    return res

  # Check thrift plugin
  try:
    fs = HadoopFileSystem.from_config(
      fs_config, hadoop_bin_path=hadoop_bin_conf.get())

    fs.setuser(fs.superuser)
    ls = fs.listdir('/')
  except TTransport.TTransportException:
    msg = 'Failed to contact Namenode plugin at %s:%s.' % \
            (fs_config.NN_HOST.get(), fs_config.NN_THRIFT_PORT.get())
    LOG.exception(msg)
    res.append((fs_config, msg))
    return res
  except (IOError, IOException):
    msg = 'Failed to see HDFS root directory at %s. Please check HDFS configuration.' % (fs.uri,)
    LOG.exception(msg)
    res.append((fs_config, msg))
    return res

  if 'tmp' not in ls:
    return res

  # Check nn port (via upload)
  try:
    w_file = fs.open(TEST_FILE, 'w')
  except OSError, ex:
    msg = 'Failed to execute Hadoop (%s)' % (hadoop_bin_conf.get(),)
    LOG.exception(msg)
    res.append((hadoop_bin_conf, msg))
    return res

  try:
    try:
      w_file.write('hello world')
      w_file.close()
    except IOError:
      msg = 'Failed to upload files using %s' % (fs.uri,)
      LOG.exception(msg)
      res.append((fs_config.NN_HDFS_PORT, msg))
      return res

    # Check dn plugin (via read)
    try:
      r_file = fs.open(TEST_FILE, 'r')
      r_file.read()
    except Exception:
      msg = 'Failed to read file. Are all datanodes configured with the HUE plugin?'
      LOG.exception(msg)
      res.append((fs_config, msg))
  finally:
    # Cleanup. Ignore if file not found.
    try:
      if fs.exists(TEST_FILE):
        fs.remove(TEST_FILE)
    except Exception, ex:
      LOG.error('Failed to cleanup test file "%s:%s": %s' % (fs.uri, TEST_FILE, ex))
  return res


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

    if not self.exists(home_path):
      user = self.user
      try:
        try:
          self.setuser(self.superuser)
          self.mkdir(home_path)
          self.chmod(home_path, 0755)
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
          LOG.error(_('Copying %s -> %s failed.') % (local_src, remote_dst))
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


"""
Deprecated! Use WebHdfs instead
"""
class HadoopFileSystem(Hdfs):
  """
  Implementation of Filesystem APIs through Thrift to a Hadoop cluster.
  """

  def __init__(self, host, thrift_port, hdfs_port=8020,
               nn_kerberos_principal="hdfs",
               dn_kerberos_principal="hdfs",
               security_enabled=False,
               hadoop_bin_path="hadoop",
               temp_dir='/tmp'):
    """
    @param host hostname or IP of the namenode
    @param thrift_port port on which the Thrift plugin is listening
    @param hdfs_port port on which NameNode IPC is listening
    @param hadoop_bin_path path to find the hadoop wrapper script on the
                           installed system - default is fine if it is in
                           the user's PATH env
    @param temp_dir Temporary directory, for mktemp()
    """
    self.host = host
    self.thrift_port = thrift_port
    self.hdfs_port = hdfs_port
    self.security_enabled = security_enabled
    self.nn_kerberos_principal = nn_kerberos_principal
    self.dn_kerberos_principal = dn_kerberos_principal
    self.hadoop_bin_path = hadoop_bin_path
    self._resolve_hadoop_path()
    self.security_enabled = security_enabled
    self._temp_dir = temp_dir

    self.nn_client = thrift_util.get_client(
      Namenode.Client, host, thrift_port,
      service_name="HDFS Namenode HUE Plugin",
      use_sasl=security_enabled,
      kerberos_principal=nn_kerberos_principal,
      timeout_seconds=NN_THRIFT_TIMEOUT)

    # The file systems are cached globally.  We store
    # user information in a thread-local variable so that
    # safety can be preserved there.
    self.thread_local = threading.local()
    self.setuser(DEFAULT_USER)
    LOG.debug("Initialized HadoopFS: %s:%d (%s)", host, thrift_port, hadoop_bin_path)

  @classmethod
  def from_config(cls, fs_config, hadoop_bin_path="hadoop"):
    return cls(host=fs_config.NN_HOST.get(),
               thrift_port=fs_config.NN_THRIFT_PORT.get(),
               hdfs_port=fs_config.NN_HDFS_PORT.get(),
               security_enabled=fs_config.SECURITY_ENABLED.get(),
               nn_kerberos_principal=fs_config.NN_KERBEROS_PRINCIPAL.get(),
               dn_kerberos_principal=fs_config.DN_KERBEROS_PRINCIPAL.get(),
               hadoop_bin_path=hadoop_bin_path)


  def _get_hdfs_base(self):
    return "hdfs://%s:%d" % (self.host, self.hdfs_port) # TODO(todd) fetch the port from the NN thrift

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
    raise OSError(errno.ENOENT, "Hadoop binary (%s) does not exist." % (self.hadoop_bin_path,))

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

  def setuser(self, user):
    # Hadoop determines the groups the user belongs to on the server side.
    self.thread_local.request_context = RequestContext()
    if not self.request_context.confOptions:
      self.request_context.confOptions = {}
    self.thread_local.request_context.confOptions['effective_user'] = user
    self.thread_local.user = user

  @property
  def user(self):
    return self.thread_local.user

  @property
  def groups(self):
    return self.thread_local.groups

  @property
  def request_context(self):
    return self.thread_local.request_context

  @_coerce_exceptions
  def open(self, path, mode="r", *args, **kwargs):
    if mode == "w":
      return FileUpload(self, path, mode, *args, **kwargs)
    return File(self, path, mode, *args, **kwargs)

  @_coerce_exceptions
  def remove(self, path):
    path = encode_fs_path(path)
    stat = self._hadoop_stat(path)
    if not stat:
      raise IOError(errno.ENOENT, "File not found: %s" % path)
    if stat.isDir:
      raise IOError(errno.EISDIR, "Is a directory: %s" % path)

    success = self.nn_client.unlink(
      self.request_context, normpath(path), recursive=False)
    if not success:
      raise IOError("Unlink failed")

  @_coerce_exceptions
  def mkdir(self, path, mode=0755):
    # TODO(todd) there should be a mkdir that isn't mkdirHIER
    # (this is mkdir -p I think)
    path = encode_fs_path(path)
    success = self.nn_client.mkdirhier(self.request_context, normpath(path), mode)
    if not success:
      raise IOError("mkdir failed")

  def _rmdir(self, path, recursive=False):
    path = encode_fs_path(path)
    stat = self._hadoop_stat(path)
    if not stat:
      raise IOError(errno.ENOENT, "Directory not found: %s" % (path,))
    if not stat.isDir:
      raise IOError(errno.EISDIR, "Is not a directory: %s" % (path,))

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
    path = encode_fs_path(path)
    stats = self.nn_client.ls(self.request_context, normpath(path))
    return [self.basename(decode_fs_path(stat.path)) for stat in stats]

  @_coerce_exceptions
  def listdir_stats(self, path):
    path = encode_fs_path(path)
    stats = self.nn_client.ls(self.request_context, normpath(path))
    return [self._unpack_stat(s) for s in stats]

  @_coerce_exceptions
  def get_content_summaries(self, paths):
    paths = [ normpath(encode_fs_path(path)) for path in paths ]
    summaries = self.nn_client.multiGetContentSummary(self.request_context, paths)
    def _fix_summary(summary):
      summary.path = decode_fs_path(summary.path)
      return summary
    return [_fix_summary(s) for s in summaries]

  @_coerce_exceptions
  def rename(self, old, new):
    old = encode_fs_path(old)
    new = encode_fs_path(new)
    success = self.nn_client.rename(
      self.request_context, normpath(old), normpath(new))
    if not success: #TODO(todd) these functions should just throw if failed
      raise IOError("Rename failed")

  @_coerce_exceptions
  def rename_star(self, old_dir, new_dir):
    """Equivalent to `mv old_dir/* new"""
    if not self.isdir(old_dir):
      raise IOError(errno.ENOTDIR, "'%s' is not a directory" % (old_dir,))
    if not self.exists(new_dir):
      self.mkdir(new_dir)
    elif not self.isdir(new_dir):
      raise IOError(errno.ENOTDIR, "'%s' is not a directory" % (new_dir,))
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
        raise IOError(errno.ENOENT, "File %s not found" % (path,))
      else:
        return None
    ret = self._unpack_stat(stat)
    return ret

  @_coerce_exceptions
  def chmod(self, path, mode):
    path = encode_fs_path(path)
    self.nn_client.chmod(self.request_context, normpath(path), mode)

  @_coerce_exceptions
  def chown(self, path, user, group):
    path = encode_fs_path(path)
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
    path = encode_fs_path(path)
    blocks = self.nn_client.getBlocks(self.request_context, normpath(path), offset, length)
    def _fix_block(blk):
      blk.path = decode_fs_path(blk.path)
      return blk
    return [_fix_block(blk) for blk in blocks]


  def _hadoop_stat(self, path):
    """Returns None if file does not exist."""
    path = encode_fs_path(path)
    try:
      stat = self.nn_client.stat(self.request_context, normpath(path))
      stat.path = decode_fs_path(stat.path)
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
    unipath = block.path
    block.path = encode_fs_path(block.path)
    try:
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
    finally:
      block.path = unipath

    raise IOError("Could not read block %s from any replicas: %s" % (block, repr(errs)))

  @_coerce_exceptions
  def set_diskspace_quota(self, path, size):
    """
    Set the diskspace quota of a given path.
    @param path The path to the given hdfs resource
    @param size The amount of bytes that a given subtree of files can grow to.
    """
    path = encode_fs_path(path)
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
    path = encode_fs_path(path)
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
    path = encode_fs_path(path)
    self.nn_client.setQuota(self.request_context, normpath(path), QUOTA_DONT_SET, QUOTA_RESET)

  @_coerce_exceptions
  def clear_namespace_quota(self, path):
    """
    Remove the namespace quota at a given path
    """
    path = encode_fs_path(path)
    self.nn_client.setQuota(self.request_context, normpath(path), QUOTA_RESET, QUOTA_DONT_SET)


  @_coerce_exceptions
  def get_diskspace_quota(self, path):
    """
    Get the current space quota in bytes for disk space. None if it is unset
    """
    path = encode_fs_path(path)
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
    path = encode_fs_path(path)
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
    path = encode_fs_path(path)
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

  @_coerce_exceptions
  def get_delegation_token(self):
    # TODO(atm): The second argument here should really be the Hue kerberos
    # principal, which doesn't exist yet. Todd's working on that.
    return self.nn_client.getDelegationToken(self.request_context, 'hadoop')

  def _connect_dn(self, node):
    dn_conf = thrift_util.ConnectionConfig(
      Datanode.Client,
      node.host,
      node.thriftPort,
      "HDFS Datanode Thrift",
      use_sasl=self.security_enabled,
      kerberos_principal=self.dn_kerberos_principal,
      timeout_seconds=DN_THRIFT_TIMEOUT)

    service, protocol, transport = \
        thrift_util.connect_to_thrift(dn_conf)
    transport.open()
    service.close = lambda: transport.close()
    return service

  @staticmethod
  def _unpack_stat(stat):
    """Unpack a Thrift "Stat" object into a dictionary that looks like fs.stat"""
    mode = stat.perms
    if stat.isDir:
      mode |= statconsts.S_IFDIR
    else:
      mode |= statconsts.S_IFREG

    return {
      'path': decode_fs_path(stat.path),
      'size': stat.length,
      'mtime': stat.mtime / 1000,
      'mode': mode,
      'user': stat.owner,
      'group': stat.group,
      'atime': stat.atime
      }

  @staticmethod
  def urlsplit(url):
    """
    Take an HDFS path (hdfs://nn:port/foo) or just (/foo) and split it into
    the standard urlsplit's 5-tuple.
    """
    return Hdfs.urlsplit(url)


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
