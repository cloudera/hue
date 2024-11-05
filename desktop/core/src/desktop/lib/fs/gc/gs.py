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
import os
import re
import time
import logging
import posixpath

from boto.exception import BotoClientError, GSResponseError
from boto.gs.connection import Location
from boto.gs.key import Key
from boto.s3.prefix import Prefix
from django.http.multipartparser import MultiPartParser
from django.utils.translation import gettext as _

from aws.s3.s3fs import S3FileSystem
from desktop.conf import GC_ACCOUNTS, PERMISSION_ACTION_GS, is_raz_gs
from desktop.lib.fs.gc import GS_ROOT, abspath, join as gs_join, normpath, parse_uri, translate_gs_error
from desktop.lib.fs.gc.gsfile import open as gsfile_open
from desktop.lib.fs.gc.gsstat import GSStat
from filebrowser.conf import REMOTE_STORAGE_HOME

DEFAULT_READ_SIZE = 1024 * 1024  # 1MB
BUCKET_NAME_PATTERN = re.compile(
r"^((?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9_\-]*[a-zA-Z0-9])\.)*(?:[A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9_\-]*[A-Za-z0-9]))$")


LOG = logging.getLogger()


class GSFileSystemException(IOError):
  def __init__(self, *args, **kwargs):
    super(GSFileSystemException, self).__init__(*args, **kwargs)


class GSListAllBucketsException(GSFileSystemException):
  def __init__(self, *args, **kwargs):
    super(GSFileSystemException, self).__init__(*args, **kwargs)


def auth_error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except (GSResponseError, IOError) as e:
      LOG.exception('GS error: ' + str(e))
      if 'Forbidden' in str(e) or (hasattr(e, 'status') and e.status == 403):
        path = kwargs.get('path')
        if not path and len(args) > 1:
          path = args[1]  # We assume that the path is the first argument
        msg = _('User is not authorized to perform the attempted operation. Check that the user has appropriate permissions.')
        if path:
          msg = _('User is not authorized to write or modify path: %s. Check that the user has write permissions.') % path
        raise GSFileSystemException(msg)
      else:
        msg = str(e)
        if isinstance(e, GSResponseError):
          msg = e.message or e.reason
        raise GSFileSystemException(msg)
    except Exception as e:
      raise e
  return decorator


def get_gs_home_directory(user=None):
  from desktop.models import _handle_user_dir_raz

  # REMOTE_STORAGE_HOME is deprecated in favor of DEFAULT_HOME_PATH per FS config level.
  # But for backward compatibility, we are still giving preference to REMOTE_STORAGE_HOME path first and if it's not set,
  # then check for DEFAULT_HOME_PATH which is set per FS config block. This helps in setting diff DEFAULT_HOME_PATH for diff FS in Hue.

  if hasattr(REMOTE_STORAGE_HOME, 'get') and REMOTE_STORAGE_HOME.get() and REMOTE_STORAGE_HOME.get().startswith('gs://'):
    remote_home_gs = REMOTE_STORAGE_HOME.get()
  elif 'default' in GC_ACCOUNTS and GC_ACCOUNTS['default'].DEFAULT_HOME_PATH.get() and GC_ACCOUNTS['default'].DEFAULT_HOME_PATH.get().startswith('gs://'):
    remote_home_gs = GC_ACCOUNTS['default'].DEFAULT_HOME_PATH.get()
  else:
    remote_home_gs = 'gs://'

  remote_home_gs = _handle_user_dir_raz(user, remote_home_gs)

  return remote_home_gs


class GSFileSystem(S3FileSystem):

  def __init__(self, gs_connection, expiration=None, fs='gs', headers=None, filebrowser_action=PERMISSION_ACTION_GS):
    super().__init__(
      gs_connection,
      expiration=expiration,
      fs=fs,
      headers=headers,
      filebrowser_action=filebrowser_action
    )

  @staticmethod
  def join(*comp_list):
    return gs_join(*comp_list)

  @staticmethod
  def normpath(path):
    return normpath(path)

  def netnormpath(self, path):
    return normpath(path)

  @staticmethod
  def parent_path(path):
    """Get the parent path of a GS path.

    Args:
      path (str): The GS path for which to find the parent path.

    Returns:
      str: The parent path.
    """
    parent_dir = GSFileSystem._append_separator(path)

    if not GSFileSystem.isroot(parent_dir):
      bucket_name, key_name, basename = parse_uri(path)

      if not basename:  # bucket is top-level, so return root
        parent_dir = GS_ROOT
      else:
        bucket_path = '%s%s' % (GS_ROOT, bucket_name)
        key_path = '/'.join(key_name.split('/')[:-1])
        parent_dir = abspath(bucket_path, key_path)

    return parent_dir

  def create_home_dir(self, home_path):
    # When GS raz is enabled, try to create user home directory
    if is_raz_gs():
      LOG.debug('Attempting to create user directory for path: %s' % home_path)
      try:
        self.mkdir(home_path)
      except Exception as e:
        LOG.exception('Failed to create user home directory for path %s with error: %s' % (home_path, str(e)))
    else:
      LOG.info('Create home directory is not available for GS filesystem')

  @translate_gs_error
  def stats(self, path):
    """Get file or directory stats for a GS path.

    Args:
      path (str): The GS path to get stats for.

    Returns:
      GSStat: An object representing the stats of the file or directory.

    Raises:
      GSFileSystemException: If the file or directory does not exist.
    """
    path = normpath(path)
    stats = self._stats(path)
    if stats:
      return stats
    raise GSFileSystemException("No such file or directory: '%s'" % path)

  @translate_gs_error
  @auth_error_handler
  def create(self, path, overwrite=False, data=None):
    """Create a file in GS at the specified path.

    Args:
      path (str): The GS path where the file should be created.
      overwrite (bool): Whether to overwrite the file if it already exists.
      data (str): The data to write to the file.

    Raises:
      Exception: If the create operation fails or some problem occurs when fetching the GS bucket or creating new key in it.
    """
    key = self._get_key(path)
    if not key:
      try:
        bucket_name, key_name = parse_uri(path)[:2]
        bucket = self._get_bucket(bucket_name)

        key = bucket.new_key(key_name)
      except Exception as e:
        raise e

    if key:
      key.set_contents_from_string(data or '', replace=overwrite)
    else:
      raise Exception('Cannot perform create operation.')

  def _get_key(self, path, validate=True):
    bucket_name, key_name = parse_uri(path)[:2]
    bucket = self._get_bucket(bucket_name)

    try:
      return bucket.get_key(key_name, headers=self.header_values)
    except BotoClientError as e:
      raise GSFileSystemException(_('Failed to access path at "%s": %s') % (path, e.reason))
    except GSResponseError as e:
      if e.status in (301, 400):
        raise GSFileSystemException(_('Failed to access path: "%s" '
          'Check that you have access to read this bucket and that the region is correct: %s') % (path, e.message or e.reason))
      elif e.status == 403:
        raise GSFileSystemException(_('User is not authorized to access path at "%s".' % path))
      else:
        raise GSFileSystemException(e.message or e.reason)
    except GSResponseError as e:
      raise e

  @translate_gs_error
  def open(self, path, mode='r'):
    key = self._get_key(path)
    if key is None:
      raise GSFileSystemException("No such file or directory: '%s'" % path)
    return gsfile_open(key, mode=mode)

  @translate_gs_error
  def listdir_stats(self, path, glob=None):
    """List and get stats for files and directories in a GS bucket.
    For path 'gs://', it gets stats for all listed buckets in GS filesystem.

    Args:
      path (str): The GS path to list.
      glob (str, optional): Glob pattern for filtering files. Default is None.

    Returns:
      list of GSStat: A list of GSStat objects representing files and directories in the path.
                      For 'gs://' path, it return a list of GSStat objects for all listed buckets.
    """
    if glob is not None:
      raise NotImplementedError(_("Option `glob` is not implemented"))

    if GSFileSystem.isroot(path):
      # Return sorted stats of all listed buckets for path gs://
      try:
        return sorted(
          [GSStat.from_bucket(b, self.fs) for b in self._s3_connection.get_all_buckets(headers=self.header_values)], key=lambda x: x.name)
      except GSFileSystemException as e:
        raise e
      except GSResponseError as e:
        if 'Forbidden' in str(e) or (hasattr(e, 'status') and e.status == 403):
          raise GSListAllBucketsException(
            _('You do not have permissions to list all buckets. Please specify a bucket name you have access to.'))
        else:
          raise GSFileSystemException(_('Failed to retrieve buckets: %s') % e.reason)
      except Exception as e:
        raise GSFileSystemException(('Failed to retrieve buckets: %s') % e)

    bucket_name, prefix = parse_uri(path)[:2]
    bucket = self._get_bucket(bucket_name)
    prefix = self._append_separator(prefix)

    res = []
    for item in bucket.list(prefix=prefix, delimiter='/', headers=self.header_values):
      if isinstance(item, Prefix):
        res.append(GSStat.from_key(Key(item.bucket, item.name), is_dir=True, fs=self.fs))
      else:
        if item.name == prefix:
          continue
        res.append(self._stats_key(item, self.fs))

    return res

  @translate_gs_error
  def listdir(self, path, glob=None):
    return [parse_uri(x.path)[2] for x in self.listdir_stats(path, glob)]

  @translate_gs_error
  @auth_error_handler
  def rmtree(self, path, skipTrash=True):
    """Remove keys from GS filesystem.

    Args:
      path (str): The GS key path of the file or directory to remove.
      skipTrash (bool): Whether to skip the trash when deleting.

    Raises:
      NotImplementedError: Since moving to trash is not implemented.
      GSFileSystemException: If the removal operation fails.
    """
    if not skipTrash:
      raise NotImplementedError(_('Moving to trash is not implemented for GS'))

    bucket_name, key_name = parse_uri(path)[:2]
    if bucket_name and not key_name:
      self._delete_bucket(bucket_name)
    else:
      if self.isdir(path):
        # Really need to make sure we end with a '/' for directory and it reflects in key_name
        path = self._append_separator(path)
        _, key_name = parse_uri(path)[:2]

      key = self._get_key(path)
      if key:
        dir_keys = []
        if self.isdir(path):
          dir_keys = key.bucket.list(prefix=key_name)

        if not dir_keys:
          # Avoid Raz bulk delete issue
          deleted_key = key.delete()
          if deleted_key.exists():
            raise GSFileSystemException('Could not delete key %s' % deleted_key)
        else:
          # key.bucket.delete_keys() call is not supported from GS side
          # So, try deleting the all keys with directory prefix one by one
          for key in list(dir_keys):
            deleted_key = key.delete()

  @translate_gs_error
  @auth_error_handler
  def mkdir(self, path, *args, **kwargs):
    """Creates a directory and any parent directory if necessary.

    Actually it creates an empty object: gs://[bucket]/[path]/
    """
    bucket_name, key_name = parse_uri(path)[:2]

    if not BUCKET_NAME_PATTERN.match(bucket_name):
      raise GSFileSystemException(_('Invalid bucket name: %s') % bucket_name)

    try:
      self._get_or_create_bucket(bucket_name)
    except GSFileSystemException as e:
      raise e
    except GSResponseError as e:
      raise GSFileSystemException(_('Failed to create GS bucket "%s": %s: %s') % (bucket_name, e.reason, e.body))
    except Exception as e:
      raise GSFileSystemException(_('Failed to create GS bucket "%s": %s') % (bucket_name, e))

    stats = self._stats(path)
    if stats:
      if stats.isDir:
        return None
      else:
        raise GSFileSystemException("'%s' already exists and is not a directory" % path)

    path = self._append_separator(path)  # directory-key should ends by /
    self.create(path)  # create empty object

  def _stats(self, path):
    if GSFileSystem.isroot(path):
      return GSStat.for_gs_root()

    try:
      key = self._get_key(path)
    except BotoClientError as e:
      raise GSFileSystemException(_('Failed to access path "%s": %s') % (path, e.reason))
    except GSResponseError as e:
      if e.status == 404:
        return None
      elif e.status == 403:
        raise GSFileSystemException(_('User is not authorized to access path: "%s"') % path)
      else:
        raise GSFileSystemException(_('Failed to access path "%s": %s') % (path, e.reason))
    except Exception as e:  # SSL errors show up here, because they've been remapped in boto
      raise GSFileSystemException(_('Failed to access path "%s": %s') % (path, str(e)))

    if key is None:
      bucket_name, key_name = parse_uri(path)[:2]
      bucket = self._get_bucket(bucket_name)

      key = Key(bucket, key_name)

    return self._stats_key(key, self.fs)

  @staticmethod
  def _stats_key(key, fs='gs'):
    if key.size is not None:
      is_directory_name = not key.name or key.name[-1] == '/'

      return GSStat.from_key(key, is_dir=is_directory_name, fs=fs)
    else:
      key.name = GSFileSystem._append_separator(key.name)
      ls = key.bucket.get_all_keys(prefix=key.name, max_keys=1)  # Not sure possible via signed request

      if len(ls) > 0:
        return GSStat.from_key(key, is_dir=True, fs=fs)

    return None

  def _copy(self, src, dst, recursive, use_src_basename):
    """Copy files and directories from a source GS path to a destination GS path.

    Args:
      src (str): The source GS path.
      dst (str): The destination GS path.
      recursive (bool): Whether to copy recursively for directories.
      use_src_basename (bool): Whether to use the source basename when copying directories.

    Returns:
      None: If copying is successful.

    Raises:
      GSFileSystemException: If any errors occur during the copy operation.
    """
    src_st = self.stats(src)
    if src_st.isDir and not recursive:
      return None  # omitting directory

    # Check if the source is a directory and destination is not a directory
    dst = abspath(src, dst)
    dst_st = self._stats(dst)
    if src_st.isDir and dst_st and not dst_st.isDir:
      raise GSFileSystemException("Cannot overwrite non-directory '%s' with directory '%s'" % (dst, src))

    # Skip operation if destination path is same as source path
    if self._check_key_parent_path(src, dst):
      raise GSFileSystemException('Destination path is same as the source path, skipping the operation.')

    src_bucket, src_key = parse_uri(src)[:2]
    dst_bucket, dst_key = parse_uri(dst)[:2]

    keep_src_basename = use_src_basename and dst_st and dst_st.isDir
    src_bucket = self._get_bucket(src_bucket)
    dst_bucket = self._get_bucket(dst_bucket)

    # Determine whether to keep the source basename when copying directories and
    # calculate the cut-off length for key names accordingly.
    if keep_src_basename:
      cut = len(posixpath.dirname(src_key))  # cut of the parent directory name
      if cut:
        cut += 1
    else:
      cut = len(src_key)
      if not src_key.endswith('/'):
        cut += 1

    for key in src_bucket.list(prefix=src_key):
      if not key.name.startswith(src_key):
        raise GSFileSystemException(_("Invalid key to transform: %s") % key.name)

      dst_name = posixpath.normpath(gs_join(dst_key, key.name[cut:]))

      # Ensure directory paths end with a separator
      if self.isdir(normpath(self.join(GS_ROOT, key.bucket.name, key.name))):
        dst_name = self._append_separator(dst_name)

      key.copy(dst_bucket, dst_name)

  @translate_gs_error
  @auth_error_handler
  def rename(self, old, new):
    """Rename a file or directory in GS.

    Copies the content to the new key and then deletes the old one.
    The new key is created if it didn't exists earlier.

    Args:
      old (str): The current GS path of the file or directory.
      new (str): The new GS path to rename to.
    """
    new = abspath(old, new)

    # Skip operation if destination path is same as source path
    if not self._check_key_parent_path(old, new):
      self.copy(old, new, recursive=True)
      self.rmtree(old, skipTrash=True)
    else:
      raise GSFileSystemException('Destination path is same as source path, skipping the operation.')

  @translate_gs_error
  @auth_error_handler
  def _check_key_parent_path(self, src, dst):
    # Return True if parent path of source is same as destination path.
    if GSFileSystem.parent_path(src) == dst:
      return True
    else:
      return False

  @translate_gs_error
  @auth_error_handler
  def upload(self, META, input_data, destination, username):
    from desktop.lib.fs.gc.upload import GSNewFileUploadHandler  # Circular dependency

    gs_upload_handler = GSNewFileUploadHandler(destination, username)

    parser = MultiPartParser(META, input_data, [gs_upload_handler])
    return parser.parse()
