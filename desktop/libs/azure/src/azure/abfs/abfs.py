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
import os
import sys
import threading
import re

from math import ceil
from posixpath import join

from hadoop.hdfs_site import get_umask_mode
from hadoop.fs.exceptions import WebHdfsException

from desktop.conf import RAZ
from desktop.lib.rest import http_client, resource
from desktop.lib.rest.raz_http_client import RazHttpClient

import azure.abfs.__init__ as Init_ABFS
from azure.abfs.abfsfile import ABFSFile
from azure.abfs.abfsstats import ABFSStat
from azure.conf import PERMISSION_ACTION_ABFS, is_raz_abfs

if sys.version_info[0] > 2:
  import urllib.request, urllib.error
  from urllib.parse import quote as urllib_quote
  from urllib.parse import urlparse as lib_urlparse
else:
  from urlparse import urlparse as lib_urlparse
  from urllib import quote as urllib_quote

LOG = logging.getLogger(__name__)

# Azure has a 30MB block limit on upload.
UPLOAD_CHUCK_SIZE = 30 * 1000 * 1000

class ABFSFileSystemException(IOError):

  def __init__(self, *args, **kwargs):
    super(ABFSFileSystemException, self).__init__(*args, **kwargs)


class ABFS(object):

  def __init__(
      self,
      url,
      fs_defaultfs,
      logical_name=None,
      hdfs_superuser=None,
      security_enabled=False,
      ssl_cert_ca_verify=True,
      temp_dir="/tmp",
      umask=0o1022,
      hdfs_supergroup=None,
      access_token=None,
      token_type=None,
      expiration=None,
      username=None
    ):
    self._url = url
    self._superuser = hdfs_superuser
    self._security_enabled = security_enabled
    self._ssl_cert_ca_verify = ssl_cert_ca_verify
    self._temp_dir = temp_dir
    self._umask = umask
    self.is_sentry_managed = lambda path: False
    self._fs_defaultfs = fs_defaultfs
    self._logical_name = logical_name
    self._supergroup = hdfs_supergroup
    self._access_token = access_token
    self._token_type = token_type
    split = lib_urlparse(fs_defaultfs)
    self._scheme = split.scheme
    self._netloc = split.netloc
    self._is_remote = True
    self._has_trash_support = False
    self._filebrowser_action = PERMISSION_ACTION_ABFS
    self.expiration = expiration
    self._user = username

    # To store user info
    self._thread_local = threading.local()  # Unused
    self._root = self.get_client(url)

    LOG.debug("Initializing ABFS : %s (security: %s, superuser: %s)" % (self._url, self._security_enabled, self._superuser))

  @classmethod
  def from_config(cls, hdfs_config, auth_provider):
    credentials = auth_provider.get_credentials()
    return cls(
        url=hdfs_config.WEBHDFS_URL.get(),
        fs_defaultfs=hdfs_config.FS_DEFAULTFS.get(),
        logical_name=None,
        security_enabled=False,
        ssl_cert_ca_verify=False,
        temp_dir=None,
        umask=get_umask_mode(),
        hdfs_supergroup=None,
        access_token=credentials.get('access_token'),
        token_type=credentials.get('token_type'),
        expiration=int(credentials.get('expires_on')) * 1000 if credentials.get('expires_on') is not None else None,
        username=credentials.get('username')
    )

  def get_client(self, url):
    if RAZ.IS_ENABLED.get():
      client = RazHttpClient(self._user, url, exc_class=WebHdfsException, logger=LOG)
    else:
      client = http_client.HttpClient(url, exc_class=WebHdfsException, logger=LOG)

    return resource.Resource(client)

  def _getheaders(self):
    headers = {
      "x-ms-version": "2019-12-12" # For latest SAS support
    }

    if self._token_type and self._access_token:
      headers["Authorization"] = self._token_type + " " + self._access_token

    return headers

  @property
  def superuser(self):
    return self._superuser

  @property
  def supergroup(self):
    return self._supergroup

  # Parse info about filesystems, directories, and files
  # --------------------------------
  def isdir(self, path):
    """
    Checks if the path is a directory (note diabled because filebrowser/views is bugged)
    """
    resp = self.stats(path)
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
      if ABFS.isroot(path):
        return True
      self.stats(path)
    except WebHdfsException as e:
      if e.code == 404:
        return False
      raise WebHdfsException
    except IOError:
      return False
    return True

  def stats(self, path, params=None, **kwargs):
    """
    List the stat of the actual file/directory
    Returns the ABFFStat object
    """
    if ABFS.isroot(path):
      return ABFSStat.for_root(path)
    try:
      file_system, dir_name = Init_ABFS.parse_uri(path)[:2]
    except:
      raise IOError

    if dir_name == '':
      return ABFSStat.for_filesystem(self._statsf(file_system, params, **kwargs), path)

    return ABFSStat.for_single(self._stats(file_system + '/' + dir_name, params, **kwargs), path)

  def listdir_stats(self, path, params=None, **kwargs):
    """
    List the stats for the directories inside the specified path
    Returns the Multiple ABFFStat object #note change later for recursive cases
    """
    if ABFS.isroot(path):
      return self.listfilesystems_stats(params=None, **kwargs)

    dir_stats = []
    file_system, directory_name, account = Init_ABFS.parse_uri(path)
    root = Init_ABFS.ABFS_ROOT
    if path.lower().startswith(Init_ABFS.ABFS_ROOT_S):
      root = Init_ABFS.ABFS_ROOT_S
    if params is None:
      params = {}
    if 'recursive' not in params:
      params['recursive'] = 'false'
    params['resource'] = 'filesystem'
    if directory_name != "":
      params['directory'] = directory_name

    res = self._root._invoke("GET", file_system, params, headers=self._getheaders(), **kwargs)
    resp = self._root._format_response(res)

    if account != '':
      file_system = file_system + account
    for x in resp['paths']:
      dir_stats.append(ABFSStat.for_directory(res.headers, x, root + file_system + "/" + x['name']))

    return dir_stats

  def listfilesystems_stats(self, root=Init_ABFS.ABFS_ROOT, params=None, **kwargs):
    """
    Lists the stats inside the File Systems, No functionality for params
    """
    stats = []
    if params is None:
      params = {}
    params["resource"] = "account"

    res = self._root._invoke("GET", params=params, headers=self._getheaders())
    resp = self._root._format_response(res)

    for x in resp['filesystems']:
      stats.append(ABFSStat.for_filesystems(res.headers, x, root))

    return stats

  def _stats(self, schemeless_path, params=None, **kwargs):
    """
    Container function for both stats,
    Returns the header of the result
    """
    if params is None:
      params = {}
    params['action'] = 'getStatus'

    res = self._root._invoke('HEAD', schemeless_path, params, headers=self._getheaders(), **kwargs)

    return res.headers

  def _statsf(self, schemeless_path, params=None, **kwargs):
    """
    Continer function for both stats but if it's a file system
    Returns the header of the result
    """
    if params is None:
      params = {}

    # For RAZ ABFS, the root path stats should have 'getAccessControl' param.
    if is_raz_abfs():
      params['action'] = 'getAccessControl'
    else:
      params['resource'] = 'filesystem'

    res = self._root._invoke('HEAD', schemeless_path, params, headers=self._getheaders(), **kwargs)

    return res.headers

  def listdir(self, path, params=None, glob=None, **kwargs):
    """
    Lists the names inside the current directories
    """
    if ABFS.isroot(path):
      return self.listfilesystems(params=params, **kwargs)

    listofDir = self.listdir_stats(path, params)

    return [x.name for x in listofDir]


  def listfilesystems(self, root=Init_ABFS.ABFS_ROOT, params=None, **kwargs):
    """
    Lists the names of the File Systems, limited arguements
    """
    listofFileSystems = self.listfilesystems_stats(root=root, params=params)
    return [x.name for x in listofFileSystems]

  @staticmethod
  def get_home_dir():
    """
    Attempts to go to the directory set by the user in the configuration file. If not defaults to abfs://
    """
    return Init_ABFS.get_home_dir_for_abfs()

  # Find or alter information about the URI path
  # --------------------------------
  @staticmethod
  def isroot(path):
    """
    Checks if the path is the root path
    """
    return Init_ABFS.is_root(path)

  @staticmethod
  def normpath(path):
    """
    Normalizes a path
    """
    resp = Init_ABFS.normpath(path)
    return resp

  @staticmethod
  def netnormpath(path):
    """
    Normalizes a path
    """
    return Init_ABFS.normpath(path)

  @staticmethod
  def parent_path(path):
    """
    Returns the Parent Path
    """
    return Init_ABFS.parent_path(path)

  @staticmethod
  def join(first, *comp_list):
    """
    Joins two paths together
    """
    return Init_ABFS.join(first, *comp_list)

  # Create Files,directories, or File Systems
  # --------------------------------
  def mkdir(self, path, params=None, headers=None, *args, **kwargs):
    """
    Makes a directory
    """
    if params is None:
      params = {}
    params['resource'] = 'directory'

    self._create_path(path, params=params, headers=params, overwrite=False)

  def create(self, path, overwrite=False, data=None, headers=None, *args, **kwargs):
    """
    Makes a File (Put text in data if adding data)
    """
    params = {'resource': 'file'}

    self._create_path(path, params=params, headers=headers, overwrite=overwrite)

    if data:
      self._writedata(path, data, len(data))

  def create_home_dir(self, home_path):
    # When ABFS raz is enabled, try to create user home dir for REMOTE_STORAGE_HOME path
    if is_raz_abfs():
      LOG.debug('Attempting to create user directory for path: %s' % home_path)
      try:
        if not self.exists(home_path):
          self.mkdir(home_path)
        else:
          LOG.debug('Skipping user directory creation, the path already exists: %s' % home_path)
      except Exception as e:
        LOG.exception('Failed to create user home directory for path %s with error: %s' % (home_path, str(e)))
    else:
      LOG.info('Create home directory is not available for Azure filesystem')

  def _create_path(self, path, params=None, headers=None, overwrite=False):
    """
    Container method for Create
    """
    file_system, dir_name = Init_ABFS.parse_uri(path)[:2]
    if dir_name == '':
      return self._create_fs(file_system)
    no_scheme = file_system + '/' + dir_name
    additional_header = self._getheaders()
    if headers is not None:
      additional_header.update(headers)
    if not overwrite:
      additional_header['If-None-Match'] = '*'

    self._root.put(no_scheme, params, headers=additional_header)

  def _create_fs(self, file_system):
    """
    Creates a File System
    """
    self._root.put(file_system, {'resource': 'filesystem'}, headers=self._getheaders())

  # Read Files
  # --------------------------------
  def read(self, path, offset='0', length=0, *args, **kwargs):
    """
    Read data from a file
    """
    path = Init_ABFS.strip_scheme(path)
    headers = self._getheaders()
    if length != 0 and length != '0':
      headers['range'] = 'bytes=%s-%s' % (str(offset), str(int(offset) + int(length)))

    return self._root.get(path, headers=headers)

  def open(self, path, option='r', *args, **kwargs):
    """
    Returns an ABFSFile object that pretends that a file is open
    """
    return ABFSFile(self, path, option)

  # Alter Files
  # --------------------------------
  def append(self, path, data, offset=0):
    if not data:
      LOG.warning("There is no data to append to")
      return
    self._append(path, data)

    return self.flush(path, {'position': int(len(data)) + int(offset)})

  def _append(self, path, data, size=0, offset=0, params=None, **kwargs):
    """
    Appends the data to a file
    """
    path = Init_ABFS.strip_scheme(path)

    if params is None:
      LOG.warning("Params not specified, Append will take longer")
      resp = self._stats(path)
      params = {'position': int(resp['Content-Length']) + offset, 'action': 'append'}
    else:
      params['action'] = 'append'
    headers = {}
    if size == 0 or size == '0':
      headers['Content-Length'] = str(len(data))
      if headers['Content-Length'] == '0':
        return
    else:
      headers['Content-Length'] = str(size)

    return self._patching_sl(path, params, data, headers, **kwargs)

  def flush(self, path, params=None, headers=None, **kwargs):
    """
    Flushes the data(i.e. writes appended data to File)
    """
    path = Init_ABFS.strip_scheme(path)
    if params is None:
      LOG.warning("Params not specified")
      params = {'position': 0}
    if 'position' not in params:
      LOG.warning("Position is not specified")
      params['position'] = 0
    params['action'] = 'flush'
    if headers is None:
      headers = {}
    headers['Content-Length'] = '0'

    self._patching_sl(path, params, header=headers, **kwargs)

  # Remove Filesystems, directories. or Files
  # --------------------------------
  def remove(self, path, skip_trash=True):
    """
    Removes an item indicated in the path
    Also removes empty directories
    """
    self._delete(path, recursive='false', skip_trash=skip_trash)

  def rmtree(self, path, skip_trash=True):
    """
    Remove everything in a given directory
    """
    self._delete(path, recursive='true', skip_trash=skip_trash)

  def _delete(self, path, recursive='false', skip_trash=True):
    """
    Wrapper function for calling delete, no support for trash or
    """
    if not skip_trash:
      raise NotImplementedError("Trash not implemented for ABFS")

    if ABFS.isroot(path):
      raise RuntimeError("Cannot Remove Root")
    file_system, dir_name = Init_ABFS.parse_uri(path)[:2]
    if dir_name == '':
      return self._root.delete(file_system, {'resource': 'filesystem'}, headers=self._getheaders())

    new_path = file_system + '/' + dir_name
    param = None
    if self.isdir(path):
      param = {'recursive': recursive}

    self._root.delete(new_path, param, headers=self._getheaders())

  def restore(self, path):
    raise NotImplementedError("")

  # Edit permissions of Filesystems, directories. or Files
  # --------------------------------
  def chown(self, path, user=None, group=None, *args, **kwargs):
    """
    Changes ownership (not implemented)
    """
    headers = {}
    if user is not None:
      headers['x-ms-owner'] = user
    if group is not None:
      headers['x-ms-group'] = group

    self.setAccessControl(path, headers=headers, **kwargs)

  def chmod(self, path, permissionNumber=None, *args, **kwargs):
    """
    Set File Permissions (passing as an int converts said integer to octal. Passing as a string assumes the string is in octal)
    """
    header = {}
    if permissionNumber is not None:
      if isinstance(permissionNumber, basestring):
        header['x-ms-permissions'] = str(permissionNumber)
      else:
        header['x-ms-permissions'] = oct(permissionNumber)

    self.setAccessControl(path, headers=header)

  def setAccessControl(self, path, headers, **kwargs):
    """
    Set Access Controls (Can do both chmod and chown) (not implemented)
    """
    path = Init_ABFS.strip_scheme(path)
    params = {'action': 'setAccessControl'}
    if headers is None:
      headers = {}

    self._patching_sl(path, params, header=headers, **kwargs)

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
      return self.copyfile(src, dst)
    self.copy_remote_dir(src, dst)

  def copyfile(self, src, dst, *args, **kwargs):
    """
    Copies a File to another location
    """
    new_path = dst + '/' + Init_ABFS.strip_path(src)
    self.create(new_path)
    chunk_size = self.get_upload_chuck_size()
    file = self.read(src)
    size = len(file)
    self._writedata(new_path, file, size)

  def copy_remote_dir(self, src, dst, *args, **kwargs):
    """
    Copies the entire contents of a directory to another location
    """
    dst = dst + '/' + Init_ABFS.strip_path(src)
    self.mkdir(dst)
    other_files = self.listdir(src)
    for x in other_files:
      x = src + '/' + Init_ABFS.strip_path(x)
      self.copy(x, dst)

  def rename(self, old, new):
    """
    Renames a file
    """
    headers = {'x-ms-rename-source': '/' + urllib_quote(Init_ABFS.strip_scheme(old))}

    try:
      self._create_path(new, headers=headers, overwrite=True)
    except WebHdfsException as e:
      if e.code == 409:
        self.copy(old, new)
        self.rmtree(old)
      else:
        raise e

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
    """
    Copy a directory or file from Local (Testing)
    """
    local_src = local_src.endswith('/') and local_src[:-1] or local_src
    remote_dst = remote_dst.endswith('/') and remote_dst[:-1] or remote_dst

    if os.path.isdir(local_src):
      self._local_copy_dir(local_src, remote_dst)
    else:
      (basename, filename) = os.path.split(local_src)
      self._local_copy_file(local_src, self.isdir(remote_dst) and self.join(remote_dst, filename) or remote_dst)

  def _local_copy_dir(self, local_src, remote_dst):
    """
    A wraper function for copying local directories
    """
    self.mkdir(remote_dir)

    for f in os.listdir(local_dir):
      local_src = os.path.join(local_dir, f)
      remote_dst = self.join(remote_dir, f)

      if os.path.isdir(local_src):
        self._copy_dir(local_src, remote_dst, mode)
      else:
        self._copy_file(local_src, remote_dst)

  def _local_copy_file(self, local_src, remote_dst, chunk_size=UPLOAD_CHUCK_SIZE):
    """
    A wraper function for copying local Files
    """
    if os.path.isfile(local_src):
      if self.exists(remote_dst):
        LOG.info('%s already exists. Skipping.' % remote_dst)
        return

      src = file(local_src)
      try:
        try:
          self.create(remote_dst)
          chunk = src.read(chunk_size)
          offset = 0
          while chunk:
            size = len(chunk)
            self._append(remote_dst, chunk, size=size, params={'position': offset})
            offset += size
            chunk = src.read(chunk_size)
          self.flush(remote_dst, params={'position': offset})
        except:
          LOG.exception(_('Copying %s -> %s failed.') % (local_src, remote_dst))
          raise
      finally:
        src.close()
    else:
      LOG.info(_('Skipping %s (not a file).') % local_src)

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

  # Other Methods to condense stuff
  #----------------------------
  # Write Files on creation
  #----------------------------
  def _writedata(self, path, data, size):
    """
    Adds text to a given file
    """
    chunk_size = self.get_upload_chuck_size()
    cycles = ceil(float(size) / chunk_size)
    for i in range(0, cycles):
      chunk = size % chunk_size
      if i != cycles or chunk == 0:
        length = chunk_size
      else:
        length = chunk
      self._append(path, data[i*chunk_size:i*chunk_size + length], length)
    self.flush(path, {'position': int(size)})

  # Use Patch HTTP request
  #----------------------------
  def _patching_sl(self, schemeless_path, param, data=None, header=None, **kwargs):
    """
    A wraper function for patch
    """
    if header is None:
      header = {}
    header.update(self._getheaders())
    return self._root.invoke('PATCH', schemeless_path, param, data, headers=header, **kwargs)
