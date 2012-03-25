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
Interfaces for Hadoop filesystem access via HttpFs/WebHDFS
"""

import errno
import logging
import posixpath
import random
import stat
import threading

from django.utils.encoding import smart_str
from desktop.lib.rest import http_client, resource
from hadoop.fs import normpath, SEEK_SET, SEEK_CUR, SEEK_END
from hadoop.fs.hadoopfs import Hdfs
from hadoop.fs.exceptions import WebHdfsException
from hadoop.fs.webhdfs_types import WebHdfsStat, WebHdfsContentSummary

import hadoop.conf


DEFAULT_HDFS_SUPERUSER = 'hdfs'

# The number of bytes to read if not specified
DEFAULT_READ_SIZE = 1024*1024 # 1MB

LOG = logging.getLogger(__name__)

class WebHdfs(Hdfs):
  """
  WebHdfs implements the filesystem interface via the WebHDFS rest protocol.
  """
  DEFAULT_USER = 'hue'        # This should be the user running Hue

  def __init__(self, url,
               fs_defaultfs,
               hdfs_superuser=None,
               security_enabled=False,
               temp_dir="/tmp"):
    self._url = url
    self._superuser = hdfs_superuser
    self._security_enabled = security_enabled
    self._temp_dir = temp_dir
    self._fs_defaultfs = fs_defaultfs

    self._client = self._make_client(url, security_enabled)
    self._root = resource.Resource(self._client)

    # To store user info
    self._thread_local = threading.local()

    LOG.debug("Initializing Hadoop WebHdfs: %s (security: %s, superuser: %s)" %
              (self._url, self._security_enabled, self._superuser))

  @classmethod
  def from_config(cls, hdfs_config):
    fs_defaultfs = hdfs_config.FS_DEFAULTFS.get()
    return cls(url=_get_service_url(hdfs_config),
               fs_defaultfs=fs_defaultfs,
               security_enabled=hdfs_config.SECURITY_ENABLED.get(),
               temp_dir=hdfs_config.TEMP_DIR.get())

  def __str__(self):
    return "WebHdfs at %s" % (self._url,)

  def _make_client(self, url, security_enabled):
    client = http_client.HttpClient(
        url, exc_class=WebHdfsException, logger=LOG)
    if security_enabled:
      client.set_kerberos_auth()
    return client

  @property
  def uri(self):
    return self._url

  @property
  def fs_defaultfs(self):
    return self._fs_defaultfs

  @property
  def security_enabled(self):
    return self._security_enabled

  @property
  def superuser(self):
    if self._superuser is None:
      try:
        # The owner of '/' is usually the superuser
        sb = self.stats('/')
        self._superuser = sb.user
      except Exception, ex:
        LOG.exception('Failed to determine superuser of %s: %s' % (self, ex))
        self._superuser = DEFAULT_HDFS_SUPERUSER

    return self._superuser
  
  @property
  def user(self):
    try:
      return self._thread_local.user
    except AttributeError:
      return WebHdfs.DEFAULT_USER

  def _getparams(self):
    if self.security_enabled:
      return {
        "user.name" : WebHdfs.DEFAULT_USER,
        "doas" : self.user
      }
    else:
      return { "user.name" : self.user }

  def setuser(self, user):
    """Set a new user. Return the current user."""
    curr = self.user
    self._thread_local.user = user
    return curr


  def listdir_stats(self, path, glob=None):
    """
    listdir_stats(path, glob=None) -> [ WebHdfsStat ]

    Get directory listing with stats.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    if glob is not None:
      params['filter'] = glob
    params['op'] = 'LISTSTATUS'
    json = self._root.get(path, params)
    filestatus_list = json['FileStatuses']['FileStatus']
    return [ WebHdfsStat(st, path) for st in filestatus_list ]

  def listdir(self, path, glob=None):
    """
    listdir(path, glob=None) -> [ entry names ]

    Get directory entry names without stats.
    """
    dirents = self.listdir_stats(path, glob)
    return [ Hdfs.basename(x.path) for x in dirents ]

  def get_content_summary(self, path):
    """
    get_content_summary(path) -> WebHdfsContentSummary
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'GETCONTENTSUMMARY'
    json = self._root.get(path, params)
    return WebHdfsContentSummary(json['ContentSummary'])


  def _stats(self, path):
    """This version of stats returns None if the entry is not found"""
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'GETFILESTATUS'
    try:
      json = self._root.get(path, params)
      return WebHdfsStat(json['FileStatus'], path)
    except WebHdfsException, ex:
      if ex.server_exc == 'FileNotFoundException' or ex.code == 404:
        return None
      raise ex

  def stats(self, path):
    """
    stats(path) -> WebHdfsStat
    """
    res = self._stats(path)
    if res is not None:
      return res
    raise IOError(errno.ENOENT, "File %s not found" % (smart_str(path),))

  def exists(self, path):
    return self._stats(path) is not None

  def isdir(self, path):
    sb = self._stats(path)
    if sb is None:
      return False
    return sb.isDir

  def isfile(self, path):
    sb = self._stats(path)
    if sb is None:
      return False
    return not sb.isDir

  def _delete(self, path, recursive=False):
    """
    _delete(path, recursive=False)

    Delete a file or directory.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'DELETE'
    params['recursive'] = recursive and 'true' or 'false'
    result = self._root.delete(path, params)
    # This part of the API is nonsense.
    # The lack of exception should indicate success.
    if not result['boolean']:
      raise IOError('Delete failed: %s' % (smart_str(path),))

  def remove(self, path):
    """Delete a file."""
    self._delete(path, recursive=False)

  def rmdir(self, path):
    """Delete a file."""
    self._delete(path, recursive=False)

  def rmtree(self, path):
    """Delete a tree recursively."""
    self._delete(path, recursive=True)

  def mkdir(self, path, mode=None):
    """
    mkdir(path, mode=None)

    Creates a directory and any parent directory if necessary.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'MKDIRS'
    if mode is not None:
      params['permission'] = safe_octal(mode)
    success = self._root.put(path, params)
    if not success:
      raise IOError("Mkdir failed: %s" % (smart_str(path),))

  def mktemp(self, subdir='', prefix='tmp'):
    """
    mktemp(subdir, prefix) ->  <temp_dir>/subdir/prefix.<rand>
    Return a unique temporary filename with prefix in the cluster's temp dir.
    """
    RANDOM_BITS = 64

    base = self.join(self._temp_dir, subdir)
    if not self.isdir(base):
      self.mkdir(base)

    while True:
      name = "%s.%s" % (prefix, random.getrandbits(RANDOM_BITS))
      candidate = self.join(base, name)
      if not self.exists(candidate):
        return candidate

  def rename(self, old, new):
    """rename(old, new)"""
    old = Hdfs.normpath(old)
    if not new.startswith('/'):
      new = Hdfs.join(Hdfs.dirname(old), new)
    new = Hdfs.normpath(new)
    params = self._getparams()
    params['op'] = 'RENAME'
    # Encode `new' because it's in the params
    params['destination'] = smart_str(new)
    result = self._root.put(old, params)
    if not result['boolean']:
      raise IOError("Rename failed: %s -> %s" %
                    (smart_str(old), smart_str(new)))


  def chown(self, path, user=None, group=None):
    """chown(path, user=None, group=None)"""
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'SETOWNER'
    if user is not None:
      params['owner'] = user
    if group is not None:
      params['group'] = group
    self._root.put(path, params)

  def chmod(self, path, mode):
    """
    chmod(path, mode)

    `mode' should be an octal integer or string.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'SETPERMISSION'
    params['permission'] = safe_octal(mode)
    self._root.put(path, params)

  def get_home_dir(self):
    """get_home_dir() -> Home directory for the current user"""
    params = self._getparams()
    params['op'] = 'GETHOMEDIRECTORY'
    res = self._root.get(params=params)
    return res['Path']


  def read(self, path, offset, length, bufsize=None):
    """
    read(path, offset, length[, bufsize]) -> data

    Read data from a file.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'OPEN'
    params['offset'] = long(offset)
    params['length'] = long(length)
    if bufsize is not None:
      params['bufsize'] = bufsize
    try:
      return self._root.get(path, params)
    except WebHdfsException, ex:
      if "out of the range" in ex.message:
        return ""
      raise ex
      

  def open(self, path, mode='r'):
    """
    DEPRECATED!
    open(path, mode='r') -> File object

    This exists for legacy support and backwards compatibility only.
    Please use read().
    """
    return File(self, path, mode)


  def create(self, path, overwrite=False, blocksize=None,
             replication=None, permission=None, data=None):
    """
    create(path, overwrite=False, blocksize=None, replication=None, permission=None)

    Creates a file with the specified parameters.
    `permission' should be an octal integer or string.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'CREATE'
    params['overwrite'] = overwrite and 'true' or 'false'
    if blocksize is not None:
      params['blocksize'] = long(blocksize)
    if replication is not None:
      params['replication'] = int(replication)
    if permission is not None:
      params['permission'] = safe_octal(permission)

    self._invoke_with_redirect('PUT', path, params, data)


  def append(self, path, data):
    """
    append(path, data)

    Append data to a given file.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'APPEND'
    self._invoke_with_redirect('POST', path, params, data)


  def copyfile(self, src, dst):
    sb = self._stats(src)
    if sb is None:
      raise IOError(errno.ENOENT, "Copy src '%s' does not exist" % (src,))
    if sb.isDir:
      raise IOError(errno.INVAL, "Copy src '%s' is a directory" % (src,))
    if self.isdir(dst):
      raise IOError(errno.INVAL, "Copy dst '%s' is a directory" % (dst,))

    CHUNK_SIZE = 65536
    offset = 0
    
    while True:
      data = self.read(src, offset, CHUNK_SIZE)
      if offset == 0:
        self.create(dst,
                    overwrite=True,
                    blocksize=sb.blockSize,
                    replication=sb.replication,
                    permission=oct(stat.S_IMODE(sb.mode)),
                    data=data)

      cnt = len(data)
      if cnt == 0:
        break

      if offset != 0:
        self.append(dst, data)
      offset += cnt


  @staticmethod
  def urlsplit(url):
    return Hdfs.urlsplit(url)


  def get_hdfs_path(self, path):
    return posixpath.join(self.fs_defaultfs, path.lstrip('/'))


  def _invoke_with_redirect(self, method, path, params=None, data=None):
    """
    Issue a request, and expect a redirect, and then submit the data to
    the redirected location. This is used for create, write, etc.

    Returns the response from the redirected request.
    """
    next_url = None
    try:
      # Do not pass data in the first leg.
      self._root.invoke(method, path, params)
    except WebHdfsException, ex:
      # This is expected. We get a 307 redirect.
      # The following call may throw.
      next_url = self._get_redirect_url(ex)

    if next_url is None:
      raise WebHdfsException(
        "Failed to create '%s'. HDFS did not return a redirect" % (path,))

    # Now talk to the real thing. The redirect url already includes the params.
    client = self._make_client(next_url, self.security_enabled)
    return resource.Resource(client).invoke(method, data=data)


  def _get_redirect_url(self, webhdfs_ex):
    """Retrieve the redirect url from an exception object"""
    try:
      # The actual HttpError (307) is wrapped inside
      http_error = webhdfs_ex.get_parent_ex()
      if http_error is None:
        raise webhdfs_ex

      if http_error.code not in (301, 302, 303, 307):
        LOG.error("Response is not a redirect: %s" % (webhdfs_ex,))
        raise webhdfs_ex
      return http_error.headers.getheader('location')
    except Exception, ex:
      LOG.error("Failed to read redirect from response: %s (%s)" %
                (webhdfs_ex, ex))
      raise webhdfs_ex

  def get_delegation_token(self, renewer):
    """get_delegation_token(user) -> Delegation token"""
    params = self._getparams()
    params['op'] = 'GETDELEGATIONTOKEN'
    params['renewer'] = renewer
    res = self._root.get(params=params)
    return res['Token']['urlString']



class File(object):
  """
  DEPRECATED!

  Represent an open file on HDFS. This exists to mirror the old thriftfs
  interface, for backwards compatibility only.
  """
  def __init__(self, fs, path, mode='r'):
    self._fs = fs
    self._path = normpath(path)
    self._pos = 0
    self._mode = mode

    try:
      self._stat = fs.stats(path)
      if self._stat.isDir:
        raise IOError(errno.EISDIR, "Is a directory: '%s'" % (smart_str(path),))
    except IOError, ex:
      if ex.errno == errno.ENOENT and 'w' in self._mode:
        self._fs.create(self._path)
        self.stat()
      else:
        raise ex

  def seek(self, offset, whence=0):
    """Set the file pointer to the given spot. @see file.seek"""
    if whence == SEEK_SET:
      self._pos = offset
    elif whence == SEEK_CUR:
      self._pos += offset
    elif whence == SEEK_END:
      self.stat()
      self._pos = self._fs.stats(self._path).size + offset
    else:
      raise IOError(errno.EINVAL, "Invalid argument to seek for whence")

  def stat(self):
    self._stat = self._fs.stats(self._path)
    return self._stat

  def tell(self):
    return self._pos

  def read(self, length=DEFAULT_READ_SIZE):
    data = self._fs.read(self._path, self._pos, length)
    self._pos += len(data)
    return data

  def write(self, data):
    """Append the data to the end of the file"""
    self.append(data)

  def append(self, data):
    if 'w' not in self._mode:
      raise IOError(errno.EINVAL, "File not open for writing")
    self._fs.append(self._path, data=data)

  def flush(self):
    pass

  def close(self):
    pass


def safe_octal(octal_value):
  """
  safe_octal(octal_value) -> octal value in string

  This correctly handles octal values specified as a string or as a numeric.
  """
  try:
    return oct(octal_value)
  except TypeError:
    return str(octal_value)


def _get_service_url(hdfs_config):
  override = hdfs_config.WEBHDFS_URL.get()
  if override:
    return override

  fs_defaultfs = hdfs_config.FS_DEFAULTFS.get()
  netloc = Hdfs.urlsplit(fs_defaultfs)[1]
  host = netloc.split(':')[0]
  port = hadoop.conf.DEFAULT_NN_HTTP_PORT
  return "http://%s:%s/webhdfs/v1" % (host, port)


def test_fs_configuration(fs_config):
  """
  This is a config validation method. Returns a list of
    [ (config_variable, error_message) ]
  """
  fs = WebHdfs.from_config(fs_config)
  fs.setuser(fs.superuser)

  # Access root
  try:
    statbuf = fs.stats('/')
  except Exception, ex:
    LOG.info("%s -- Validation error: %s" % (fs, ex))
    return [(fs_config.WEBHDFS_URL, 'Failed to access filesystem root')]

  # Write a file
  tmpname = fs.mktemp(prefix='hue_config_validation')
  try:
    fs.create(tmpname)
  except Exception, ex:
    LOG.info("%s -- Validation error: %s" % (fs, ex))
    return [(fs_config.WEBHDFS_URL,
            'Failed to create temporary file "%s"' % (tmpname,))]

  # Check superuser has super power
  try:  # Finally: delete tmpname
    try:
      fs.chown(tmpname, fs.superuser)
    except Exception, ex:
      LOG.info("%s -- Validation error: %s" % (fs, ex))
      return [(fs_config.WEBHDFS_URL,
              'Failed to chown file. Please make sure that the filesystem root '
              'is owned by the cluster superuser ("hdfs" in most cases).')]
  finally:
    try:
      fs.remove(tmpname)
    except Exception, ex:
      LOG.error("Failed to remove '%s': %s" % (tmpname, ex))
      return [(fs_config.WEBHDFS_URL,
              'Failed to remove temporary file "%s"' % (tmpname,))]

  return [ ]
