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
    resp = self.stats(path)
    return (resp is not None) and (resp['x-ms-resource-type'] == 'directory') 

  def isfile(self, path):
    raise NotImplementedError("")

  def stats(self, path):
    """
    List the stat of the actual name
    """
    return self._stats(azure.abfs.__init__.strip_scheme(path) )
  
  def listdir_stats(self,path, **kwargs):
    """
    List the stats for the directories
    """
    if azure.abfs.__init__.is_root(path):
      return self.listfilesystems_stats()
    dir_stats = []
    file_system = azure.abfs.__init__.parse_uri(path)[0]
    for direct in self.listdir(path):
      res = self._stats(file_system + '/' + direct)
      dir_stats.append(res)  
    return dir_stats
  
  def _stats(self, schemeless_path):
    """
    Container function for both stats
    """
    res = self._root._invoke('HEAD', schemeless_path, { 'action' : 'getStatus', 'upn' : 'true'}, headers = self._getheaders())
    if res is None:
      return None
    return res.headers
  
  def listdir(self, path, glob=None):
    """
    Lists the names inside the current directories 
    """
    if azure.abfs.__init__.is_root(path):
      return self.listfilesystems()
    file_system, directory_name = azure.abfs.__init__.parse_uri(path)[:2]
    params = {'resource': 'filesystem', 'recursive':'false'}
    if directory_name != "":
      params['directory'] = directory_name
    resp = self._root.get(file_system, params, headers= self._getheaders())
    return [x['name'] for x in resp['paths']]
  
  def listfilesystems_stats(self):
    """
    Lists the stats inside the File Systems  
    """
    stats = []
    for file_system in self.listfilesystems():
      resp = self._root._invoke('HEAD', file_system, {'resource': 'filesystem'}, headers = self._getheaders())
      stats.append(resp.headers)
    return stats
  
  def listfilesystems(self):
    resp = self._root.get('',{'resource': 'account'}, headers= self._getheaders())
    return [x['name'] for x in resp['filesystems']]
    
  def normpath(self, path):
    raise NotImplementedError("")

  def netnormpath(self, path):
    raise NotImplementedError("")

  def open(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def exists(self, path):
    return self.stats(path) is not None

  def isroot(self, path):
    raise NotImplementedError("")

  def parent_path(self, path):
    raise NotImplementedError("")

  def join(self, first, *comp_list):
    raise NotImplementedError("")

  def mkdir(self, path, *args, **kwargs):
    """
    file_system, dir_name = azure.abfs.__init__.parse_uri(path)[:2]
    if dir_name == '':
      return self.create_home_dir(path)
    no_scheme = file_system + '/' + dir_name
    additional_header = self._getheaders()
    additional_header['If-None-Match'] = '*'
    res = self._root.put(no_scheme,{'resource': 'directory'}, headers= additional_header)
    """
    self._create_path(path, 'directory')
    
  def read(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def append(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def rmtree(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def remove(self, path, skip_trash=False):
    if azure.abfs.__init__.is_root(path):
      raise NotImplementedError("")
    new_path = azure.abfs.__init__.strip_scheme(path)
    if self.isdir(path):
      self._root.delete(new_path,{'recursive':'false'}, headers= self._getheaders())
    elif self.isfile(path):
      self._root.delete(new_path, headers= self._getheaders())
    else:
      raise NotImplementedError

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
  
  def _create_path(self,path, resource = None, recursive = None, create = True):
    file_system, dir_name = azure.abfs.__init__.parse_uri(path)[:2]
    LOG.debug("%s,%s" %(file_system, dir_name))
    if dir_name == '':
      return self.create_home_dir(path)
    no_scheme = file_system + '/' + dir_name
    params = {}
    additional_header = self._getheaders()
    if create:
      additional_header['If-None-Match'] = '*'
    if resource is not None:
      params['resource'] = resource
    if recursive is not None:
      params['recursive'] = recursive
    res = self._root.put(no_scheme,params, headers= additional_header)
  
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