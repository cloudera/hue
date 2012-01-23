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
from hadoop.fs.hadoopfs import encode_fs_path, Hdfs
from hadoop.fs.exceptions import WebHdfsException
from hadoop.fs.webhdfs_types import WebHdfsStat

DEFAULT_USER = 'hue_webui'

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

    self._client = http_client.HttpClient(url, exc_class=WebHdfsException)
    self._root = resource.Resource(self._client)

    # To store user info
    self._thread_local = threading.local()
    self._thread_local.params = { }

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

  def _rest_call(member_fn):
    """Decorator to reset the api related params."""
    def reset_params(fs, *args, **kwargs):
      PRESERVE_KEYS = set(['user.name'])
      new_dict = { }
      for key, val in fs._thread_local.params.iteritems():
        if key in PRESERVE_KEYS:
          new_dict[key] = val
      fs._thread_local.params = new_dict
      return member_fn(fs, *args, **kwargs)
    return reset_params

  @property
  def uri(self):
    return self._url

  @property
  def superuser(self):
    return self._superuser
  
  @property
  def user(self):
    return self.thread_local

  def _setop(self, op):
    return self._setparam("op", op)

  def _setparam(self, key, val):
    self._thread_local.params[key] = val
    return self._thread_local.params

  def _getparams(self):
    return self._thread_local.params

  def setuser(self, user):
    self._thread_local.user = user
    self._setparam("user.name", user)


  @_rest_call
  def listdir_stats(self, path, glob=None):
    """
    listdir_stats(path, glob=None) -> [ WebhdfsStat ]

    Get directory listing with stats.
    """
    path = encode_fs_path(Hdfs.abspath(path))
    if glob is not None:
      self._setparam("filter", glob)
    params = self._setop("LISTSTATUS")
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

  @_rest_call
  def _stats(self, path):
    """This version of stats returns None if the entry is not found"""
    path = encode_fs_path(Hdfs.abspath(path))
    params = self._setop('GETFILESTATUS')
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
