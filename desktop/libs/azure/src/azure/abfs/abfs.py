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


from azure.conf import PERMISSION_ACTION_ABFS
import azure.abfs.__init__
from urllib.parse import urlparse

from hadoop.hdfs_site import get_umask_mode

from hadoop.fs.exceptions import WebHdfsException

from desktop.lib.rest import http_client, resource
from nose.tools import assert_true, assert_equal, assert_false


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
    """
    Checks if the path is a directory
    """
    resp = self.stats(path)
    return (resp is not None) and (resp['x-ms-resource-type'] == 'directory') 

  def isfile(self, path):
    """
    Checks if the path is a file
    """
    resp = self.stats(path)
    return (resp is not None) and (resp['x-ms-resource-type'] == 'file') 

  def stats(self, path):
    """
    List the stat of the actual file/directory
    """
    file_system, dir_name = azure.abfs.__init__.parse_uri(path)[:2]
    if dir_name == '':
      res = self._root._invoke('HEAD', file_system, { 'resource' : 'filesystem'}, headers = self._getheaders())
      return res.headers
    return self._stats(file_system + '/' +dir_name)
  
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
    """
    Lists the names of the File Systems  
    """
    resp = self._root.get('',{'resource': 'account'}, headers= self._getheaders())
    return [x['name'] for x in resp['filesystems']]
    
  def normpath(self, path):
    raise NotImplementedError("")

  def netnormpath(self, path):
    raise NotImplementedError("")

  def open(self, path, *args, **kwargs):
    raise NotImplementedError("")

  def exists(self, path):
    """
    Test if a path exists
    """
    try:
      self.stats(path)
    except WebHdfsException as e:
      if e.code == 404:
        return False
      raise WebHdfsException
    return True

  def isroot(self, path):
    return azure.abfs.__init__.is_root(path)

  def parent_path(self, path):
    assert_false(self.isroot(path))
    
    raise NotImplementedError("")

  def join(self, first, *comp_list):
    raise NotImplementedError("")

  def mkdir(self, path, *args, **kwargs):
    """
    Makes a directory
    """
    self._create_path(path, 'directory')
    
  def read(self, path, *args, **kwargs):
    path = azure.abfs.__init__.strip_scheme(path)
    return self._root.get(path, headers = self._getheaders())

  def append(self, path, data = None, *args, **kwargs):
    """
    Appends the Data
    """
    path = azure.abfs.__init__.strip_scheme(path)
    resp = self_stats(path)
    params = {'position' : resp['Content-Length'], 'action' : 'append'}
    headers= {'Content-Length' : '0'}
    self._patching_sl( path, params, data, headers,  **kwargs)
    raise NotImplementedError("")
  
  def flush(self, path, params, headers = None, *args, **kwargs):
    """
    Flushes the data
    """
    path = azure.abfs.__init__.strip_scheme(path)
    if params is None:
      params = {}
    params['action'] = 'flush'
    if headers is None:
      headers = {}
    headers['Content-Length'] = '0'
    self._patching_sl( path, params, header = headers,  **kwargs)

  def rmtree(self, path, *args, **kwargs):
    """
    Remove everything in a given directory
    """
    self._delete(path, 'true')

  def remove(self, path, skip_trash=False):
    """
    Removes an item indicated in the path
    Also includes empty directories
    """
    self._delete(path, 'false', skip_trash)
    
  def _delete(self, path, recursive, skip_trash=False):
    """
    Wrapper function for calling delete
    """
    if azure.abfs.__init__.is_root(path):
      raise RuntimeError("Cannot Remove Root")
    file_system, dir_name = azure.abfs.__init__.parse_uri(path)[:2]
    if dir_name == '':
      return self._root.delete(file_system,{'resource': 'filesystem'}, headers= self._getheaders())
    new_path = file_system + '/' + dir_name
    param = None
    if self.isdir(path):
      param = {'recursive' : recursive}
    self._root.delete(new_path,param , headers= self._getheaders())
    
  def restore(self, path):
    raise NotImplementedError("")

  def create(self, path, *args, **kwargs):
    """
    Makes a File
    """
    self._create_path(path, 'file')

  def create_home_dir(self, home_path=None):
    """
    Make a home directory (i.e File system)
    """
    raise NotImplementedError("")

  def chown(self, path, user = None, group = None, *args, **kwargs):
    """
    Changes ownership
    """
    header = {}
    if user is not None:
      header['x-ms-owner'] = user
    if group is not None:
      header['x-,ms-group'] = group
    self.setAccessControl(path, headers, **kwargs)
    raise NotImplementedError("")
  
  def chmod(self, path, permissionNumber = None, *args, **kwargs):
    """
    Set File Permissions
    """
    header = {}
    if permissionNumber is not None:
      header['x-ms-permissions'] = permissionNumber
    self.setAccessControl(path, headers, **kwargs)
  
  def setAccessControl(self, path, headers, **kwargs):
    """
    Set Access Controls (Can do both chmod and chown)
    """
    path = azure.abfs.__init__.strip_scheme(path)
    params= {'action': 'setAccessControl'}
    self._patching_sl( path, params, header = headers,  **kwargs)

  def copyFromLocal(self, local_src, remote_dst, *args, **kwargs):
    raise NotImplementedError("")

  def mktemp(self, subdir='', prefix='tmp', basedir=None):
    raise NotImplementedError("")

  def purge_trash(self):
    raise NotImplementedError("")
  
  def _create_path(self,path, resource = None, source = None, create = True):
    """
    Conatiner method for Create
    """
    file_system, dir_name = azure.abfs.__init__.parse_uri(path)[:2]
    if dir_name == '':
      return self._create_fs(file_system)
    no_scheme = file_system + '/' + dir_name
    params = {}
    additional_header = self._getheaders()
    if create:
      additional_header['If-None-Match'] = '*'
      assert_true(resource is not None)
      params['resource'] = resource
    else:
      source = '/' + azure.abfs.__init__.strip_scheme(source)
      additional_header['x-ms-rename-source'] = source
      if resource is not None:
        params['resource'] = resource
    self._root.put(no_scheme,params, headers= additional_header)
    
  def _create_fs(self, file_system):
    self._root.put(file_system,{'resource': 'filesystem'}, headers= self._getheaders())
  
  # Handle file systems interactions
  # --------------------------------
  def copy(self, src, dst, *args, **kwargs):
    raise NotImplementedError("")

  def copyfile(self, src, dst, *args, **kwargs):
    raise NotImplementedError("")

  def copy_remote_dir(self, src, dst, *args, **kwargs):
    raise NotImplementedError("")

  def rename(self, old, new): 
    """
    Renames a file
    """
    self._create_path(new, source = old, create= False)

  def rename_star(self, old_dir, new_dir):
    """
    Renames a directory
    """
    self._create_path(new_dir, source = old_dir, create= False)

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
  
  #Methods to condense stuff
  #----------------------------
  def _patching_sl(self, schemeless_path, param, data = None, header = None, **kwargs):
    """
    A wraper function for patch
    Kwargs would be the parameters to add
    """
    if header is None:
      header = {}
    header.update(self._getheaders())
    res = self._root.invoke('PATCH', schemeless_path, param, data, headers = header)
    
      
      
      