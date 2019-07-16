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
from nose.tools import assert_true

"""
Interfaces for ABFS
"""
from future import standard_library
standard_library.install_aliases()
from builtins import object
import logging
import threading

from urllib.parse import urlparse
from azure.conf import PERMISSION_ACTION_ABFS
import azure.abfs.__init__

from hadoop.hdfs_site import get_umask_mode

from hadoop.fs.exceptions import WebHdfsException

from desktop.lib.rest import http_client, resource
from nose.tools import assert_true


LOG = logging.getLogger(__name__)

#Azure has a 30MB block limit on upload.
UPLOAD_CHUCK_SIZE = 30 * 1000 * 1000


class ABFS(object):

  def __init__(self, url,
               fs_defaultfs,
               logical_name=None,
               hdfs_superuser=None,
               security_enabled=False,
               ssl_cert_ca_verify=True,
               temp_dir="/tmp",
               umask=0o1022,
               hdfs_supergroup=None,
               auth_provider=None):
    self._url = url
    self._superuser = hdfs_superuser
    self._security_enabled = security_enabled
    self._ssl_cert_ca_verify = ssl_cert_ca_verify
    self._temp_dir = temp_dir
    self._umask = umask
    self._fs_defaultfs = fs_defaultfs
    self._logical_name = logical_name
    self._supergroup = hdfs_supergroup
    self._auth_provider = auth_provider
    split = urlparse(fs_defaultfs)
    self._scheme = split.scheme
    self._netloc = split.netloc
    self._is_remote = True
    self._has_trash_support = False
    self._filebrowser_action = PERMISSION_ACTION_ABFS

    self._client = http_client.HttpClient(url, exc_class=WebHdfsException, logger=LOG)
    self._root = resource.Resource(self._client)

    # To store user info
    self._thread_local = threading.local()

    LOG.debug("Initializing ABFS : %s (security: %s, superuser: %s)" % (self._url, self._security_enabled, self._superuser))

  @classmethod
  def from_config(cls, hdfs_config, auth_provider):
    return cls(url=hdfs_config.WEBHDFS_URL.get(),
               fs_defaultfs=hdfs_config.FS_DEFAULTFS.get(),
               logical_name=None,
               security_enabled=False,
               ssl_cert_ca_verify=False,
               temp_dir=None,
               umask=get_umask_mode(),
               hdfs_supergroup=None,
               auth_provider=auth_provider)

  def _getheaders(self):
    return {
      "Authorization": self._auth_provider.get_token(),
    }

  def isdir(self, path):
    raise NotImplementedError("")

  def isfile(self, path):
    raise NotImplementedError("")

  def stats(self, path):
    file_system, dir_name = azure.abfs.__init__.parse_uri(path)[:2]
    norm_path = file_system + '/' + dir_name
    LOG.debug('%s' %self._getheaders())
    res = self._root._invoke('HEAD', norm_path, { 'action' : 'getStatus', 'upn' : 'true'}, headers = self._getheaders())
    return res.headers
  
  def listdir_stats(self,path, **kwargs):
    pass
  
  def listdir(self, path, glob=None):
    """
    Lists the names for directories 
    """
    resp = self._listdir(path)
    if azure.abfs.__init__.is_root(path):
      return [x['name'] for x in resp['filesystems']]
    else:
      return [x['name'] for x in resp['paths']]
    
  def _listdir(self, path, **kwargs):
    """
    Lists direct with more info
    """
    if azure.abfs.__init__.is_root(path):
      return self._root.get('',{'resource': 'account'}, headers= self._getheaders())
      #return self._client.execute('GET', '/', headers =  self._getheaders())
    LOG.debug("%s" %path)
    file_system, directory_name = azure.abfs.__init__.parse_uri(path)[:2]
    LOG.debug("%s, %s" %(file_system, directory_name))
    if directory_name == "":
      res = self._root.get(file_system,{'resource': 'filesystem', 'recursive':'false'}, headers= self._getheaders())
    else:
      res = self._root.get(file_system,{'resource': 'filesystem', 'recursive':'false', 'directory' : directory_name}, headers= self._getheaders())
    LOG.debug("%s" %res)
    return res

  def normpath(self, path):
    raise NotImplementedError("")

  def netnormpath(self, path):
    raise NotImplementedError("")

  def open(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def exists(self, path):
    raise NotImplementedError("")

  def isroot(self, path):
    raise NotImplementedError("")

  def parent_path(self, path):
    raise NotImplementedError("")

  def join(self, first, *comp_list):
    raise NotImplementedError("")

  def mkdir(self, path, *args, **kwargs):
    res = self.listdir(path)
    other_path = azure.abfs.__init__.strip_scheme(path)
    assert_true((other_path not in res) or self.isfile(path))
    
    
    raise NotImplementedError("")

  def read(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def append(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def rmtree(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def remove(self, path, skip_trash=False):
    raise NotImplementedError("")

  def restore(self, path):
    raise NotImplementedError("")

  def create(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def create_home_dir(self, home_path=None):
    raise NotImplementedError("")

  def chown(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def chmod(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def copyFromLocal(self, local_src, remote_dst, *args, **kwargs):
    raise NotImplementedError("")

  def mktemp(self, subdir='', prefix='tmp', basedir=None):
    raise NotImplementedError("")

  def purge_trash(self):
    raise NotImplementedError("")

  # Handle file systems interactions
  # --------------------------------
  def copy(self, src, dst, *args, **kwargs):
    raise NotImplementedError("")

  def copyfile(self, src, dst, *args, **kwargs):
    raise NotImplementedError("")

  def copy_remote_dir(self, src, dst, *args, **kwargs):
    raise NotImplementedError("")

  def rename(self, old, new):
    raise NotImplementedError("")

  def rename_star(self, old_dir, new_dir):
    raise NotImplementedError("")

  def upload(self, file, path, *args, **kwargs):
    raise NotImplementedError("")

  def check_access(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def mkswap(self, filename, subdir='', suffix='swp', basedir=None):
    raise NotImplementedError("")
  
  def setuser(self, user):
    self._user = user

  def get_upload_chuck_size(self, path):
    raise NotImplementedError("")