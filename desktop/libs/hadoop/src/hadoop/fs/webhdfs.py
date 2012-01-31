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
import threading

from desktop.lib.rest import http_client, resource
from hadoop.fs import normpath, SEEK_SET, SEEK_CUR, SEEK_END
from hadoop.fs.hadoopfs import encode_fs_path, Hdfs
from hadoop.fs.exceptions import WebHdfsException
from hadoop.fs.webhdfs_types import WebHdfsStat


DEFAULT_USER = 'hue_webui'

# The number of bytes to read if not specified
DEFAULT_READ_SIZE = 1024*1024 # 1MB

LOG = logging.getLogger(__name__)

class WebHdfs(Hdfs):
  """
  WebHdfs implements the filesystem interface via the WebHDFS rest protocol.
  """
  def __init__(self, url,
               hdfs_superuser="hdfs",
               security_enabled=False,
               temp_dir="/tmp"):
    self._url = url
    self._superuser = hdfs_superuser
    self._security_enabled = security_enabled
    self._temp_dir = temp_dir

    self._client = http_client.HttpClient(url,
                                          exc_class=WebHdfsException,
                                          logger=LOG)
    self._root = resource.Resource(self._client)

    # To store user info
    self._thread_local = threading.local()
    self.setuser(DEFAULT_USER)

    LOG.debug("Initializing Hadoop HttpFs; %s (security: %s, superuser: %s)" %
              (self._url, self._security_enabled, self._superuser))

  @classmethod
  def from_config(cls, hdfs_config):
    host = hdfs_config.NN_HOST.get()
    port = hdfs_config.NN_HTTP_PORT.get()
    url = "http://%s:%s/webhdfs/v1" % (host, port)
    return cls(url=url,
               security_enabled=hdfs_config.SECURITY_ENABLED.get(),
               temp_dir=hdfs_config.TEMP_DIR.get())

  def __str__(self):
    return "WebHdfs at %s" % (self._url,)

  @property
  def uri(self):
    return self._url

  @property
  def superuser(self):
    return self._superuser
  
  @property
  def user(self):
    return self.thread_local

  def _getparams(self):
    return { "user.name" : self._thread_local.user }

  def setuser(self, user):
    self._thread_local.user = user


  def listdir_stats(self, path, glob=None):
    """
    listdir_stats(path, glob=None) -> [ WebhdfsStat ]

    Get directory listing with stats.
    """
    path = encode_fs_path(Hdfs.abspath(path))
    params = self._getparams()
    if glob is not None:
      params['filter'] = glob
    params['op'] = 'LISTSTATUS'
    json = self._root.get(path, **params)
    filestatus_list = json['FileStatuses']['FileStatus']
    return [ WebHdfsStat(st, path) for st in filestatus_list ]

  def listdir(self, path, glob=None):
    """
    listdir(path, glob=None) -> [ entry names ]

    Get directory entry names without stats.
    """
    dirents = self.listdir_stats(self, path, glob)
    return [ x.path for x in dirents ]

  def _stats(self, path):
    """This version of stats returns None if the entry is not found"""
    path = encode_fs_path(Hdfs.abspath(path))
    params = self._getparams()
    params['op'] = 'GETFILESTATUS'
    try:
      json = self._root.get(path, **params)
      return WebHdfsStat(json['FileStatus'], path)
    except WebHdfsException, ex:
      if ex.server_exc == 'FileNotFoundException':
        return None
      raise ex

  def stats(self, path):
    """
    stats(path) -> WebHdfsStat
    """
    res = self._stats(path)
    if res is not None:
      return res
    raise IOError(errno.ENOENT, "File %s not found" % (path,))

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

  def read(self, path, offset, length, bufsize=None):
    """
    read(path, offset, length[, bufsize]) -> data

    Read data from a file.
    """
    path = encode_fs_path(Hdfs.abspath(path))
    params = self._getparams()
    params['op'] = 'OPEN'
    params['offset'] = offset
    params['length'] = length
    if bufsize is not None:
      params['bufsize'] = bufsize
    return self._root.get_raw(path, **params)

  def open(self, path, mode='r'):
    """
    DEPRECATED!
    open(path, mode='r') -> File object

    This exists for legacy support and backwards compatibility only.
    Please use read().
    """
    return File(self, path, mode)



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

    stat = fs.stats(path)
    if stat.isDir:
      raise IOError(errno.EISDIR, "Is a directory: '%s'" % (path,))

  def seek(self, offset, whence=0):
    """Set the file pointer to the given spot. @see file.seek"""
    if whence == SEEK_SET:
      self._pos = offset
    elif whence == SEEK_CUR:
      self._pos += offset
    elif whence == SEEK_END:
      self._pos = self._fs.stats(self._path).length + offset
    else:
      raise IOError(errno.EINVAL, "Invalid argument to seek for whence")

  def tell(self):
    return self._pos

  def read(self, length=DEFAULT_READ_SIZE):
    data = self._fs.read(self._path, self._pos, length)
    self._pos += len(data)
    return data

  def close(self):
    pass
