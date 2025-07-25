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
import stat
import time
import uuid
from urllib.parse import urlparse as lib_urlparse

from django.utils.encoding import smart_str
from django.utils.translation import gettext as _

from desktop.conf import PERMISSION_ACTION_OFS
from desktop.lib.fs.ozone import _serviceid_join, is_root, join as ofs_join, normpath, OFS_ROOT, parent_path
from desktop.lib.fs.ozone.ofsstat import OzoneFSStat
from hadoop.fs.exceptions import WebHdfsException
from hadoop.fs.webhdfs import WebHdfs
from hadoop.hdfs_site import get_umask_mode

LOG = logging.getLogger()


def get_ofs_home_directory(user=None):
  # TODO: Check if Ozone bring the concept of home directory in the future
  return OFS_ROOT


class OzoneFS(WebHdfs):
  """
  OzoneFS implements the filesystem interface via the WebHDFS/HttpFS REST protocol.
  """

  def __init__(self, url, fs_defaultfs, logical_name=None, security_enabled=False, ssl_cert_ca_verify=True, temp_dir="/tmp", umask=0o1022):
    super(OzoneFS, self).__init__(
      url,
      fs_defaultfs,
      logical_name=logical_name,
      security_enabled=security_enabled,
      ssl_cert_ca_verify=ssl_cert_ca_verify,
      temp_dir=temp_dir,
      umask=umask,
    )

    split = lib_urlparse(fs_defaultfs)
    self._scheme = split.scheme
    self._netloc = split.netloc

    self._filebrowser_action = PERMISSION_ACTION_OFS
    self._has_trash_support = False
    self._is_remote = True

    LOG.debug("Initializing Ozone client: %s (security: %s, superuser: %s)" % (self._url, self._security_enabled, self._superuser))

  @classmethod
  def from_config(cls, ofs_config):
    return cls(
      url=ofs_config.WEBHDFS_URL.get(),
      fs_defaultfs=ofs_config.FS_DEFAULTFS.get(),
      logical_name=ofs_config.LOGICAL_NAME.get(),
      security_enabled=ofs_config.SECURITY_ENABLED.get(),
      ssl_cert_ca_verify=ofs_config.SSL_CERT_CA_VERIFY.get(),
      temp_dir=ofs_config.TEMP_DIR.get(),
      umask=get_umask_mode(),
    )

  @property
  def temp_dir(self):
    return self._temp_dir

  def strip_normpath(self, path):
    if path.startswith(OFS_ROOT + self._netloc):
      path = path.split(OFS_ROOT + self._netloc)[1]
    elif path.startswith("ofs:/" + self._netloc):
      path = path.split("ofs:/" + self._netloc)[1]

    return path

  def normpath(self, path):
    return normpath(path)

  def netnormpath(self, path):
    return normpath(path)

  def isroot(self, path):
    return is_root(path)

  def parent_path(self, path):
    return parent_path(path, self._netloc)

  def listdir_stats(self, path, glob=None):
    """
    listdir_stats(path, glob=None) -> [ OzoneFSStat ]

    Get directory listing with stats.
    """
    if path == OFS_ROOT:
      json = self._handle_serviceid_path_status()
    else:
      path = self.strip_normpath(path)
      params = self._getparams()

      if glob is not None:
        params["filter"] = glob
      params["op"] = "LISTSTATUS"
      headers = self._getheaders()

      json = self._root.get(path, params, headers)

    filestatus_list = json["FileStatuses"]["FileStatus"]
    return [OzoneFSStat(st, path, self._netloc) for st in filestatus_list]

  def _stats(self, path):
    """
    This stats method returns None if the entry is not found.
    """
    if path == OFS_ROOT:
      serviceid_path_status = self._handle_serviceid_path_status()["FileStatuses"]["FileStatus"][0]
      json = {"FileStatus": serviceid_path_status}
    else:
      path = self.strip_normpath(path)
      params = self._getparams()
      params["op"] = "GETFILESTATUS"
      headers = self._getheaders()

      try:
        json = self._root.get(path, params, headers)
      except WebHdfsException as ex:
        if ex.server_exc == "FileNotFoundException" or ex.code == 404:
          return None
        raise ex

    return OzoneFSStat(json["FileStatus"], path, self._netloc)

  def _handle_serviceid_path_status(self):
    json = {
      "FileStatuses": {
        "FileStatus": [
          {
            "pathSuffix": self._netloc,
            "type": "DIRECTORY",
            "length": 0,
            "owner": "",
            "group": "",
            "permission": "777",
            "accessTime": 0,
            "modificationTime": 0,
            "blockSize": 0,
            "replication": 0,
          }
        ]
      }
    }
    return json

  def stats(self, path):
    """
    stats(path) -> OzoneFSStat
    """
    res = self._stats(path)
    if res is not None:
      return res
    raise IOError(errno.ENOENT, _("File %s not found") % path)

  def check_access(self, path, permission="READ"):
    """
    Check if the user has the requested permission for a given path.

    Since Ozone doesn't have a native check access API, this method verifies access
    by attempting operations that would require the specified permission level.

    Args:
      path (str): The OFS path to check access for
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
            # Use a small limit for efficiency
            self.listdir_stats(path)[:1]
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

    except WebHdfsException as e:
      LOG.debug(f'Ozone filesystem error checking {permission} permission at path "{path}": {str(e)}')
      return False
    except Exception as e:
      # Log unexpected errors but don't crash
      LOG.warning(f'Unexpected error checking {permission} permission at path "{path}": {str(e)}')
      return False

  def filebrowser_action(self):
    return self._filebrowser_action

  # Deprecated
  def upload(self, file, path, *args, **kwargs):
    """
    Upload is done by the OFSFileUploadHandler
    """
    pass

  def rename(self, old, new):
    """rename(old, new)"""
    old = self.strip_normpath(old)
    if not self.is_absolute(new):
      new = _serviceid_join(ofs_join(self.dirname(old), new), self._netloc)
    new = self.strip_normpath(new)

    params = self._getparams()
    params["op"] = "RENAME"
    # Encode `new' because it's in the params
    params["destination"] = smart_str(new)
    headers = self._getheaders()

    result = self._root.put(old, params, headers=headers)

    if not result["boolean"]:
      raise IOError(_("Rename failed: %s -> %s") % (smart_str(old, errors="replace"), smart_str(new, errors="replace")))

  def rename_star(self, old_dir, new_dir):
    """Equivalent to `mv old_dir/* new"""
    if not self.isdir(old_dir):
      raise IOError(errno.ENOTDIR, _("'%s' is not a directory") % old_dir)

    if not self.exists(new_dir):
      self.mkdir(new_dir)
    elif not self.isdir(new_dir):
      raise IOError(errno.ENOTDIR, _("'%s' is not a directory") % new_dir)

    ls = self.listdir(old_dir)
    for dirent in ls:
      self.rename(_serviceid_join(ofs_join(old_dir, dirent), self._netloc), _serviceid_join(ofs_join(new_dir, dirent), self._netloc))

  def copy_remote_dir(self, source, destination, dir_mode=None, owner=None, skip_file_list=None):
    if owner is None:
      owner = self.DEFAULT_USER

    if dir_mode is None:
      dir_mode = self.getDefaultDirPerms()

    if not self.exists(destination):
      self.do_as_user(owner, self.mkdir, destination, mode=dir_mode)

    for s in self.listdir_stats(source):
      source_file = s.path
      destination_file = posixpath.join(destination, s.name)
      if s.isDir:
        self.copy_remote_dir(source_file, destination_file, dir_mode, owner, skip_file_list)
      else:
        if s.size > self.get_upload_chuck_size():
          if skip_file_list is not None:
            skip_file_list += " \n- " + source_file
        else:
          self.do_as_user(owner, self.copyfile, source_file, destination_file)
    return skip_file_list

  def copy(self, src, dest, recursive=False, dir_mode=None, owner=None):
    """
    Copy file, or directory, in HDFS to another location in HDFS.

    ``src`` -- The directory, or file, to copy from.
    ``dest`` -- the directory, or file, to copy to.
            If 'dest' is a directory that exists, copy 'src' into dest.
            If 'dest' is a file that exists and 'src' is a file, overwrite dest.
            If 'dest' does not exist, create 'src' as 'dest'.
    ``recursive`` -- Recursively copy contents of 'src' to 'dest'.
                This is required for directories.
    ``dir_mode`` and ``owner`` are used to define permissions on the newly
    copied files and directories.

    This method will overwrite any pre-existing files that collide with what is being copied.
    Copying a directory to a file is not allowed.
    """
    if owner is None:
      owner = self.user

    # Hue was defaulting permissions on copying files to the permissions
    # of the original file, but was not doing the same for directories
    # changed below for directories to remain consistent
    if dir_mode is None:
      sb = self._stats(src)
      dir_mode = oct(stat.S_IMODE(sb.mode))

    src = self.strip_normpath(src)
    dest = self.strip_normpath(dest)

    if not self.exists(src):
      raise IOError(errno.ENOENT, _("File not found: %s") % src)

    skip_file_list = ""  # Store the files to skip copying which are greater than the upload_chunck_size()

    if self.isdir(src):
      # 'src' is directory.
      # Skip if not recursive copy and 'src' is directory.
      if not recursive:
        LOG.debug("Skipping contents of %s" % src)
        return None

      # If 'dest' is a directory change 'dest'
      # to include 'src' basename.
      # create 'dest' if it doesn't already exist.
      if self.exists(dest):
        if self.isdir(dest):
          dest = self.join(dest, self.basename(src))
        else:
          raise IOError(errno.EEXIST, _("Destination file %s exists and is not a directory.") % dest)

      self.do_as_user(owner, self.mkdir, dest, mode=dir_mode)

      # Copy files in 'src' directory to 'dest'.

      skip_file_list = self.copy_remote_dir(src, dest, dir_mode, owner, skip_file_list)
    else:
      # 'src' is a file.
      # If 'dest' is a directory, then copy 'src' into that directory.
      # Other wise, copy to 'dest'.
      stats = self.listdir_stats(src)[0]
      if stats.size < self.get_upload_chuck_size():
        if self.exists(dest) and self.isdir(dest):
          self.copyfile(src, self.join(dest, self.basename(src)))
        else:
          self.copyfile(src, dest)
      else:
        skip_file_list += " \n- " + src

    return skip_file_list

  def get_upload_handler(self, destination_path, overwrite):
    from desktop.lib.fs.ozone.upload import OFSNewFileUploadHandler

    return OFSNewFileUploadHandler(self, destination_path, overwrite)
