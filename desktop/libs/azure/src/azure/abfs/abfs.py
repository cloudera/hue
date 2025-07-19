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

import logging
import os
import threading
import time
import uuid
from builtins import object
from urllib.parse import quote as urllib_quote, urlparse as lib_urlparse

import azure.abfs.__init__ as Init_ABFS
from azure.abfs.abfsfile import ABFSFile
from azure.abfs.abfsstats import ABFSStat
from azure.conf import is_raz_abfs, PERMISSION_ACTION_ABFS
from desktop.conf import RAZ
from desktop.lib.rest import http_client, resource
from desktop.lib.rest.raz_http_client import RazHttpClient
from hadoop.fs.exceptions import WebHdfsException
from hadoop.hdfs_site import get_umask_mode

LOG = logging.getLogger()

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
    username=None,
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
      username=credentials.get('username'),
    )

  def get_client(self, url):
    if RAZ.IS_ENABLED.get():
      client = RazHttpClient(self._user, url, exc_class=WebHdfsException, logger=LOG)
    else:
      client = http_client.HttpClient(url, exc_class=WebHdfsException, logger=LOG)

    return resource.Resource(client)

  def _getheaders(self):
    headers = {
      "x-ms-version": "2019-12-12"  # For latest SAS support
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
    """Check if the given path is a directory or not."""
    try:
      stats = self.stats(path)
      return stats.isDir
    except Exception as e:
      # If checking stats for path here gives 404 error, it means the path does not exist and therefore is not a directory.
      if e.code == 404:
        return False
      raise e

  def isfile(self, path):
    """Check if the given path is a file or not."""
    try:
      stats = self.stats(path)
      return not stats.isDir
    except Exception as e:
      # If checking stats for path here gives 404 error, it means the path does not exist and therefore is not a file.
      if e.code == 404:
        return False
      raise e

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
    except Exception:
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

    while True:
      res = self._root._invoke("GET", file_system, params, headers=self._getheaders(), **kwargs)
      resp = self._root._format_response(res)
      if account:
        file_system += account
      for x in resp['paths']:
        dir_stats.append(ABFSStat.for_directory(res.headers, x, root + file_system + "/" + x['name']))
      # If the number of paths returned exceeds the 5000, a continuation token is provided in the response header x-ms-continuation,
      # which must be used in subsequent invocations to continue listing the paths.
      if 'x-ms-continuation' in res.headers:
        params['continuation'] = res.headers['x-ms-continuation']
      else:
        break

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
    return Init_ABFS.get_abfs_home_directory()

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
    # When ABFS raz is enabled, try to create user home directory
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
      headers['range'] = 'bytes=%s-%s' % (str(offset), str(int(offset) + int(length) - 1))

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
    actual_data = data.getvalue() if hasattr(data, 'getvalue') else data

    if size == 0 or size == '0':
      headers['Content-Length'] = str(len(actual_data))
      if headers['Content-Length'] == '0':
        return
    else:
      headers['Content-Length'] = str(size)

    return self._patching_sl(path, params, actual_data, headers, **kwargs)

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
      if isinstance(permissionNumber, str):
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
    rename_source = Init_ABFS.strip_scheme(old)
    headers = {'x-ms-rename-source': '/' + urllib_quote(rename_source)}

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

  # Deprecated
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
    self.mkdir(remote_dst)

    for f in os.listdir(local_src):
      local_src = os.path.join(local_src, f)
      remote_dst = self.join(remote_dst, f)

      if os.path.isdir(local_src):
        self._local_copy_dir(local_src, remote_dst)
      else:
        self._local_copy_file(local_src, remote_dst)

  def _local_copy_file(self, local_src, remote_dst, chunk_size=UPLOAD_CHUCK_SIZE):
    """
    A wraper function for copying local Files
    """
    if os.path.isfile(local_src):
      if self.exists(remote_dst):
        LOG.info(f'{remote_dst} already exists. Skipping.')
        return

      src = open(local_src, 'rb')
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
        except Exception:
          LOG.exception(f'Copying {local_src} -> {remote_dst} failed.')
          raise
      finally:
        src.close()
    else:
      LOG.info(f'Skipping {local_src} (not a file).')

  def check_access(self, path, permission="READ"):
    """
    Check if the user has the requested permission for a given path.

    This method verifies access by attempting operations that would require the
    specified permission level. It handles both files and directories gracefully.

    Args:
      path (str): The ABFS path to check access for
      permission (str): Permission type to check - 'READ' or 'WRITE' (case-insensitive)

    Returns:
      bool: True if user has the requested permission, False otherwise

    Note:
      - For READ permission: Checks if path exists and tries to access its metadata
      - For WRITE permission: For directories, attempts to create a temporary file;
        for files or non-existent paths, checks parent directory write access
    """
    permission = permission.upper()

    if permission not in ("READ", "WRITE"):
      LOG.warning(f'Invalid permission type "{permission}". Must be READ or WRITE.')
      return False

    try:
      if permission == "READ":
        # For read access, we need to verify the path exists and is accessible
        if not self.exists(path):
          LOG.debug(f'Path "{path}" does not exist, cannot read.')
          return False

        try:
          if self.isdir(path):
            # For directories, attempt to list contents
            self.listdir_stats(path, params={"maxResults": 1})  # Limit results for efficiency
          else:
            # For files, get file stats
            self.stats(path)
          return True
        except WebHdfsException as e:
          if e.code in (401, 403):  # Unauthorized or Forbidden
            LOG.debug(f'No read permission for path "{path}": {str(e)}')
            return False
          # Re-raise unexpected errors
          raise

      # Check WRITE permission
      else:
        # For non-existent paths, check parent directory
        if not self.exists(path):
          parent = self.parent_path(path)

          # If we can't determine parent or we're at root, deny access
          if not parent or parent == path:
            LOG.debug(f'Cannot determine parent for non-existent path "{path}"')
            return False

          # Recursively check parent write access
          return self.check_access(parent, permission="WRITE")

        # For existing paths
        if self.isdir(path):
          # For directories, try creating a temporary marker file
          temp_file = None
          try:
            # Generate unique temporary filename with timestamp
            temp_file = self.join(path, f".hue_access_check_{str(int(time.time() * 1000))}_{str(uuid.uuid4())[:8]}")

            # Attempt to create the temporary file
            self.create(temp_file, overwrite=True, data="")

            # Clean up the temporary file if creation succeeded
            try:
              self.remove(temp_file)
            except Exception as cleanup_error:
              LOG.warning(f'Failed to clean up temporary file "{temp_file}": {cleanup_error}')

            return True

          except WebHdfsException as e:
            if e.code in (401, 403):  # Unauthorized or Forbidden
              LOG.debug(f'No write permission for directory "{path}": {str(e)}')
              return False
            # Re-raise unexpected errors
            raise

        else:
          # For files, check write permission on parent directory
          parent = self.parent_path(path)
          if parent and parent != path:
            return self.check_access(parent, permission="WRITE")
          else:
            LOG.debug(f'Cannot check write access for file "{path}", no valid parent found')
            return False

    except ABFSFileSystemException as e:
      LOG.debug(f'ABFS filesystem error checking {permission} permission at path "{path}": {str(e)}')
      return False
    except Exception as e:
      # Log unexpected errors but don't crash
      LOG.warning(f'Unexpected error checking {permission} permission at path "{path}": {str(e)}')
      return False

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

  def get_upload_handler(self, destination_path, overwrite):
    from azure.abfs.upload import ABFSNewFileUploadHandler
    return ABFSNewFileUploadHandler(self, destination_path, overwrite)

  def filebrowser_action(self):
    return self._filebrowser_action

  # Other Methods to condense stuff
  # ----------------------------
  def _writedata(self, path, data, size):
    """
    Write data to a file in chunks.

    This method splits the input data into chunks of the maximum allowed upload size and appends each chunk to the specified path.
    After all chunks are written, it flushes the file to ensure all data is committed.

    Args:
      path (str): The destination file path in ABFS.
      data (bytes or bytearray): The data to be written.
      size (int): The total size of the data to be written.

    Returns:
      None
    """
    chunk_size = self.get_upload_chuck_size()
    # Calculate number of chunks needed using integer ceiling division
    cycles = (size + chunk_size - 1) // chunk_size

    for i in range(cycles):
      start = i * chunk_size
      if i == cycles - 1:  # Last chunk
        # For the last chunk, only write the remaining data
        length = size - start
      else:
        # For all other chunks, write full chunk size
        length = chunk_size

      end = start + length
      chunk_data = data[start:end]

      # Only append if we have data to write
      if chunk_data:
        self._append(path, chunk_data, size=length, params={"position": start})

    # Flush at the end with the total size
    self.flush(path, {"position": int(size)})

  # Use Patch HTTP request
  # ----------------------------
  def _patching_sl(self, schemeless_path, param, data=None, header=None, **kwargs):
    """
    A wraper function for patch
    """
    if header is None:
      header = {}
    header.update(self._getheaders())
    return self._root.invoke('PATCH', schemeless_path, param, data, headers=header, **kwargs)
