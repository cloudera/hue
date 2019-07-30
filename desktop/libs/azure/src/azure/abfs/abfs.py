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

from math import ceil
from posixpath import join

import azure.abfs.__init__
from azure.conf import PERMISSION_ACTION_ABFS
from azure.abfs.abfsfile import ABFSFile
from azure.abfs.abfsstats import ABFSStat

from urllib.parse import urlparse
from hadoop.hdfs_site import get_umask_mode

from hadoop.fs.exceptions import WebHdfsException

from desktop.lib.rest import http_client, resource
from nose.tools import assert_true, assert_equal, assert_false


LOG = logging.getLogger(__name__)

#Azure has a 30MB block limit on upload.
UPLOAD_CHUCK_SIZE = 30 * 1000 * 1000


class ABFSFileSystemException(IOError):

  def __init__(self, *args, **kwargs):
    super(ABFSFileSystemException, self).__init__(*args, **kwargs)
    

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
  
  # Parse info about filesystems, directories, and files
  # --------------------------------
  def isdir(self, path):
    """
    Checks if the path is a directory (note diabled because filebrowser/views is bugged)
    """
    resp = self.stats(path)
    #LOG.debug("checking directoty or not")
    return resp.isDir

  def isfile(self, path):
    """
    Checks if the path is a file
    """
    return not self.isdir(path) 
  
  def exists(self, path):
    """
    Test if a path exists
    """
    try:
      #LOG.debug("checking existence")
      if ABFS.isroot(path):
        return True
      self.stats(path)
    except WebHdfsException as e:
      if e.code == 404:
        return False
      raise WebHdfsException
    return True

  def stats(self, path, params = None, **kwargs):
    """
    List the stat of the actual file/directory
    Returns the ABFFStat object
    """
    #LOG.debug("%s" %path)
    if ABFS.isroot(path):
      return ABFSStat.for_root()
    file_system, dir_name = azure.abfs.__init__.parse_uri(path)[:2]
    if dir_name == '':
      LOG.debug("Path being called is a Filesystem")
      return ABFSStat.for_filesystem(self._statsf(file_system, params, **kwargs), path)
    #LOG.debug("%s" %resp)
    #LOG.debug("%s" %res.path)
    return ABFSStat.for_single(self._stats(file_system + '/' +dir_name, params, **kwargs), path)
  
  def listdir_stats(self,path, params = None, **kwargs):
    """
    List the stats for the directories inside the specified path
    Returns the Multiple ABFFStat object #note change later for recursive cases
    """
    if ABFS.isroot(path):
      LOG.warn("Path: %s is a Filesystem" %path)
      return self.listfilesystems_stats(params = None, **kwargs)
    dir_stats = []
    file_system, directory_name = azure.abfs.__init__.parse_uri(path)[:2]
    if params is None:
      params = {}
    if 'recursive' not in params.keys():
      params['recursive'] = 'false'
    params['resource'] = 'filesystem'
    if directory_name != "":
      params['directory'] = directory_name
    res = self._root._invoke("GET",file_system, params, headers= self._getheaders(), **kwargs)
    resp = self._root._format_response(res)
    for x in resp['paths']:
      dir_stats.append(ABFSStat.for_directory(res.headers, x, azure.abfs.__init__.ABFS_ROOT +file_system + "/" + x['name']))
    #LOG.debug("%s%s" %(dir_stats,[x.isDir for x in dir_stats ]))
    return dir_stats
  
  def listfilesystems_stats(self, params = None, **kwargs):
    """
    Lists the stats inside the File Systems, No functionality for params
    """
    stats = []
    res = self._root._invoke("GET", params = {"resource" : "account"}, headers = self._getheaders() )
    resp = self._root._format_response(res)
    LOG.debug("%s" %res)
    for x in resp['filesystems']:
      stats.append(ABFSStat.for_filesystems(res.headers, x))
    return stats
  
  def _stats(self, schemeless_path, params = None, **kwargs):
    """
    Container function for both stats,
    Returns the header of the result
    """
    if params is None:
      params = {}
    params['action'] = 'getStatus'
    res = self._root._invoke('HEAD', schemeless_path, params, headers = self._getheaders(), **kwargs)
    return res.headers
  
  def _statsf(self, schemeless_path, params = None, **kwargs):
    """
    Continer function for both stats but if it's a file system
    Returns the header of the result
    """
    if params is None:
      params = {}
    params['resource'] = 'filesystem'
    res = self._root._invoke('HEAD', schemeless_path, params, headers = self._getheaders(), **kwargs)
    return res.headers
    
  def listdir(self, path, params = None, **kwargs):
    """
    Lists the names inside the current directories 
    """
    if ABFS.isroot(path):
      LOG.warn("Path being called is a Filesystem")
      return self.listfilesystems(params, **kwargs)
    listofDir = self.listdir_stats(path, params)
    return [x.name for x in listofDir]
  
  
  def listfilesystems(self, params=None,**kwargs):
    """
    Lists the names of the File Systems, limited arguements  
    """
    listofFileSystems = self.listfilesystems_stats(params)
    return [x.name for x in listofFileSystems]
  
  # Find or alter information about the URI path
  # --------------------------------
  @staticmethod
  def isroot(path):
    """
    Checks if the path is the root path
    """
    return azure.abfs.__init__.is_root(path)  
  
  @staticmethod
  def normpath(path):
    """
    Normalizes a path
    """
    resp = azure.abfs.__init__.normpath(path)
    #LOG.debug("%s" %resp)
    return resp

  @staticmethod
  def netnormpath(path):
    """
    Normalizes a path
    """
    #LOG.debug("ok")
    return azure.abfs.__init__.normpath(path)

  def open(self, path, option = 'r', *args, **kwargs):
    return ABFSFile(self,path, option )
  
  @staticmethod
  def parent_path(path):
    """
    Returns the Parent Path
    """
    #LOG.debug("parent")
    return azure.abfs.__init__.parent_path(path)

  @staticmethod
  def join(first, *comp_list):
    """
    Joins two paths together
    """
    return azure.abfs.__init__.join(first,*comp_list)

  # Create Files,directories, or File Systems
  # --------------------------------
  def mkdir(self, path, params = None, headers = None, *args, **kwargs):
    """
    Makes a directory
    """
    if params is None:
      params = {}
    params['resource'] = 'directory'
    self._create_path(path, params = params, headers = params, create = 'true')
  
  def create(self, path, params = None, headers = None, *args, **kwargs):
    """
    Makes a File
    """
    if params is None:
      params = {}
    params['resource'] = 'file'
    self._create_path(path, params = params, headers =headers, create = 'true')

  def create_home_dir(self, home_path=None):
    raise NotImplementedError("File System not named")
  
  def _create_path(self,path, params = None, headers = None, create = True):
    """
    Container method for Create
    """
    file_system, dir_name = azure.abfs.__init__.parse_uri(path)[:2]
    if dir_name == '':
      return self._create_fs(file_system)
    no_scheme = file_system + '/' + dir_name
    additional_header = self._getheaders()
    if headers is not None:
      additional_header.update(headers)
    if create:
      additional_header['If-None-Match'] = '*'
    self._root.put(no_scheme,params, headers= additional_header)
    
  def _create_fs(self, file_system):
    """
    Creates a File System
    """
    self._root.put(file_system,{'resource': 'filesystem'}, headers= self._getheaders())
    
  # Read Files
  # --------------------------------
  def read(self, path, offset = '0', length = 0, *args, **kwargs):
    """
    Read data from a file
    """
    path = azure.abfs.__init__.strip_scheme(path)
    headers = self._getheaders()
    if length != 0 and length != '0':
      headers['range']= 'bytes=%s-%s' %(str(offset), str(int(offset) + int(length)))
    return self._root.get(path, headers = headers)
  
  # Alter Files
  # --------------------------------
  def append(self, path, data, size = 0, offset =0 ,params = None, *args, **kwargs):
    """
    Appends the data to a file
    """
    path = azure.abfs.__init__.strip_scheme(path)
    if params is None:
      LOG.warn("Params not specified, Append will take longer")
      resp = self._stats(path)
      params = {'position' : int(resp['Content-Length']) + offset, 'action' : 'append'}
      LOG.debug("%s" %params)
    else:
      params['action'] = 'append'
    headers = {}
    if size == 0:
      headers['Content-Length'] = str(len(data))
    else:
      headers['Content-Length'] = str(size)
    LOG.debug("%s" %headers['Content-Length'])
    return self._patching_sl( path, params, data, headers,  **kwargs)
  
  def flush(self, path, params = None, headers = None, *args, **kwargs):
    """
    Flushes the data(i.e. writes appended data to File)
    """
    path = azure.abfs.__init__.strip_scheme(path)
    if params is None:
      LOG.warn("Params not specified")
      params = {'position' : 0}
    if 'position' not in params.keys():
      LOG.warn("Position is not specified")
      params['position'] = 0
    params['action'] = 'flush'
    if headers is None:
      headers = {}
    headers['Content-Length'] = '0'
    self._patching_sl( path, params, header = headers,  **kwargs)

  # Remove Filesystems, directories. or Files
  # --------------------------------
  def remove(self, path, skip_trash=False):
    """
    Removes an item indicated in the path
    Also removes empty directories
    """
    self._delete(path, 'false', skip_trash)
    
  def rmtree(self, path, *args, **kwargs):
    """
    Remove everything in a given directory
    """
    self._delete(path, 'true')
    
  def _delete(self, path, recursive = 'false', skip_trash=False):
    """
    Wrapper function for calling delete, no support for trash or 
    """
    if ABFS.isroot(path):
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
  
  # Edit permissions of Filesystems, directories. or Files
  # --------------------------------
  def chown(self, path, user = None, group = None, *args, **kwargs):
    """
    Changes ownership (not implemented)
    """
    headers = {}
    if user is not None:
      headers['x-ms-owner'] = user
    if group is not None:
      headers['x-ms-group'] = group
    self.setAccessControl(path, headers = headers, **kwargs)
  
  def chmod(self, path, permissionNumber = None, *args, **kwargs):
    """
    Set File Permissions (not implemented)
    """
    header = {}
    if permissionNumber is not None:
      header['x-ms-permissions'] = str(permissionNumber)
    self.setAccessControl(path, headers = header)
  
  def setAccessControl(self, path, headers, **kwargs):
    """
    Set Access Controls (Can do both chmod and chown) (not implemented)
    """
    path = azure.abfs.__init__.strip_scheme(path)
    params= {'action': 'setAccessControl'}
    if headers is None:
      headers ={}
    self._patching_sl( path, params, header = headers,  **kwargs)

  def mktemp(self, subdir='', prefix='tmp', basedir=None):
    raise NotImplementedError("")

  def purge_trash(self):
    raise NotImplementedError("")
  
  
  # Handle file systems interactions
  # --------------------------------
  def copy(self, src, dst, *args, **kwargs):
    """
    General Copying
    """
    if self.isfile(src):
      return self.copyfile(src ,dst)    
    self.copy_remote_dir(src, dst)
          
  
  def copyfile(self, src, dst, *args, **kwargs):
    """
    Copies a File to another location
    """
    new_path = dst + '/' + azure.abfs.__init__.strip_path(src)
    self.create(new_path)
    chunk_size = self.get_upload_chuck_size()
    file = self.read(src)
    size = len(file)
    cycles = ceil(float(size) / chunk_size)
    for i in range(0,cycles):
      chunk = size % chunk_size
      if i != cycles or chunk == 0:
        length = chunk_size
      else:
        length = chunk
      self.append(new_path, file[i*chunk_size:i*chunk_size + length], length)
    LOG.debug("%s" %size)
    self.flush(new_path, {'position' : int(size) })

  def copy_remote_dir(self, src, dst, *args, **kwargs):
    """
    Copies the entire contents of a directory to another location (Bug here possibly)
    """
    dst = dst + '/' + azure.abfs.__init__.strip_path(src)
    LOG.debug("%s" %dst)
    self.mkdir(dst)
    other_files = self.listdir(src)
    for x in other_files:
      x = src + '/' + azure.abfs.__init__.strip_path(x)
      LOG.debug("%s" %x)
      self.copy(x, dst)

  def rename(self, old, new): 
    """
    Renames a file
    """ 
    headers = {'x-ms-rename-source' : '/' + azure.abfs.__init__.strip_scheme(old) }
    self._create_path(new, headers = headers, create= False)

  def rename_star(self, old_dir, new_dir):
    """
    Renames a directory
    """
    self.rename(old_dir, new_dir)

  def upload(self, file, path, *args, **kwargs):
    """
    Upload is done by the client
    """
    pass
  
  def copyFromLocal(self, local_src, remote_dst, *args, **kwargs):
    #Implement Later
    raise NotImplementedError("")

  def check_access(self, path, *args, **kwargs):
    """
    Check access of a file/directory (Work in Progress/Not Ready)
    """
    raise NotImplementedError("")
    try:
      status = self.stats(path)
      if 'x-ms-permissions' not in status.keys():
        raise b
    except b:
      LOG.debug("Permisions have not been set")
    except:
      Exception

  def mkswap(self, filename, subdir='', suffix='swp', basedir=None):
    """
    Makes a directory and returns a potential filename for that directory
    """
    base = self.join(basedir or self._temp_dir, subdir)
    if not self.isdir(base):
      self.mkdir(base)

    candidate = self.join(base, "%s.%s" % (filename, suffix))
    return candidate
  
  def setuser(self, user):
    """
    Changes the User
    """
    self._user = user
  
  def get_upload_chuck_size(self):
    """
    Gets the maximum size allowed to upload
    """
    return UPLOAD_CHUCK_SIZE
  
  def filebrowser_action(self):
    return self._filebrowser_action
  
  #Methods to condense stuff
  #----------------------------
  def _patching_sl(self, schemeless_path, param, data = None, header = None, **kwargs):
    """
    A wraper function for patch
    """
    if header is None:
      header = {}
    header.update(self._getheaders())
    LOG.debug("%s" %kwargs)
    return self._root.invoke('PATCH', schemeless_path, param, data, headers = header, **kwargs)
      