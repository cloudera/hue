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

import logging
import os
import posixpath
import re
import time
from builtins import object, str
from urllib.parse import urlparse as lib_urlparse

from boto.exception import BotoClientError, S3ResponseError
from boto.s3.connection import Location
from boto.s3.key import Key
from boto.s3.prefix import Prefix
from django.utils.translation import gettext as _

from aws import s3
from aws.conf import AWS_ACCOUNTS, get_default_region, get_locations, is_raz_s3, PERMISSION_ACTION_S3
from aws.s3 import normpath, S3A_ROOT, s3file, translate_s3_error
from aws.s3.s3stat import S3Stat
from filebrowser.conf import REMOTE_STORAGE_HOME

DEFAULT_READ_SIZE = 1024 * 1024  # 1MB
BUCKET_NAME_PATTERN = re.compile(
  r"^((?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9_\-]*[a-zA-Z0-9])\.)*(?:[A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9_\-]*[A-Za-z0-9]))$")
S3A_DELETE_CHUNK_SIZE = 1000  # S3 API limit for bulk delete operations

LOG = logging.getLogger()


class S3FileSystemException(IOError):
  def __init__(self, *args, **kwargs):
    super(S3FileSystemException, self).__init__(*args, **kwargs)


class S3ListAllBucketsException(S3FileSystemException):
  def __init__(self, *args, **kwargs):
    super(S3FileSystemException, self).__init__(*args, **kwargs)


def auth_error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except (S3ResponseError, IOError) as e:
      LOG.exception('S3 error: ' + str(e))
      if 'Forbidden' in str(e) or (hasattr(e, 'status') and e.status == 403):
        path = kwargs.get('path')
        if not path and len(args) > 1:
          path = args[1]  # We assume that the path is the first argument
        msg = _('User is not authorized to perform the attempted operation. Check that the user has appropriate permissions.')
        if path:
          msg = _('User is not authorized to write or modify path: %s. Check that the user has write permissions.') % path
        raise S3FileSystemException(msg)
      else:
        msg = str(e)
        if isinstance(e, S3ResponseError):
          msg = e.message or e.reason
        raise S3FileSystemException(msg)
    except Exception as e:
      raise e
  return decorator


def get_s3_home_directory(user=None):
  from desktop.models import _handle_user_dir_raz

  # REMOTE_STORAGE_HOME is deprecated in favor of DEFAULT_HOME_PATH per FS config level.
  # But for backward compatibility, we are still giving preference to REMOTE_STORAGE_HOME path first and if it's not set,
  # then check for DEFAULT_HOME_PATH which is set per FS config block. This helps in setting diff DEFAULT_HOME_PATH for diff FS in Hue.

  if hasattr(REMOTE_STORAGE_HOME, 'get') and REMOTE_STORAGE_HOME.get() and REMOTE_STORAGE_HOME.get().startswith('s3a://'):
    remote_home_s3 = REMOTE_STORAGE_HOME.get()
  elif (
    'default' in AWS_ACCOUNTS
    and AWS_ACCOUNTS['default'].DEFAULT_HOME_PATH.get()
    and AWS_ACCOUNTS['default'].DEFAULT_HOME_PATH.get().startswith('s3a://')
  ):
    remote_home_s3 = AWS_ACCOUNTS['default'].DEFAULT_HOME_PATH.get()
  else:
    remote_home_s3 = 's3a://'

  remote_home_s3 = _handle_user_dir_raz(user, remote_home_s3)

  return remote_home_s3


class S3FileSystem(object):
  def __init__(self, s3_connection, expiration=None, fs='s3a', headers=None, filebrowser_action=PERMISSION_ACTION_S3):
    self._s3_connection = s3_connection
    self._filebrowser_action = filebrowser_action
    self.user = None
    self.is_sentry_managed = lambda path: False
    self.superuser = None
    self.supergroup = None
    self.expiration = expiration
    self.fs = fs
    self.header_values = headers

  def _get_bucket(self, name):
    try:
      return self._s3_connection.get_bucket(name, headers=self.header_values)
    except S3ResponseError as e:
      if e.status == 301 or e.status == 400:
        raise S3FileSystemException(
          _('Failed to retrieve bucket "%s" in region "%s" with "%s". Your bucket is in region "%s"') %
          (name, self._get_location(), e.message or e.reason, self.get_bucket_location(name)))
      else:
        raise e

  def get_bucket_location(self, name):
    try:
      # We use make_request, because self._s3_connection.get_bucket does not returns headers which contains the bucket location
      resp = self._s3_connection.make_request('HEAD', name)
      return resp.getheader('x-amz-bucket-region')
    except Exception as e:
      LOG.warning('Failed to fetch bucket "%s" location with "%s"' % (name, e.message or e.reason))
      return None

  def _get_or_create_bucket(self, name):
    try:
      bucket = self._get_bucket(name)
    except BotoClientError as e:
      raise S3FileSystemException(_('Failed to create bucket "%s" with "%s"') % (name, e.message or e.reason))
    except S3ResponseError as e:
      if e.status == 403:
        raise S3FileSystemException(_('User is not authorized to access bucket named "%s". '
          'If you are attempting to create a bucket, this bucket name is already reserved.') % name)
      elif e.status == 404:
        kwargs = {}
        if self._get_location():
          kwargs['location'] = self._get_location()
        bucket = self._create_bucket(name, **kwargs)
      else:
        raise S3FileSystemException(e.message or e.reason)
    return bucket

  def _create_bucket(self, name, **kwargs):
    # S3 API throws an exception when using us-east-1 and specifying CreateBucketConfiguration
    # Boto specifies CreateBucketConfiguration whenever the location is not default
    # We change location to default to fix issue
    # More information: https://github.com/boto/boto3/issues/125

    if kwargs.get('location') == 'us-east-1':
      kwargs['location'] = ''

    return self._s3_connection.create_bucket(name, **kwargs)

  def _delete_bucket(self, name):
    try:
      # Verify that bucket exists and user has permissions to access it
      bucket = self._get_bucket(name)
      # delete keys from bucket first
      for key in bucket.list():
        key.delete()
      self._s3_connection.delete_bucket(name)
      LOG.info('Successfully deleted bucket name "%s" and all its contents.' % name)
    except S3ResponseError as e:
      if e.status == 403:
        raise S3FileSystemException(_('User is not authorized to access bucket named "%s". '
          'If you are attempting to create a bucket, this bucket name is already reserved.') % name)
      else:
        raise S3FileSystemException(e.message or e.reason)

  def _get_key(self, path, validate=True):
    bucket_name, key_name = s3.parse_uri(path)[:2]
    bucket = self._get_bucket(bucket_name)

    try:
      return bucket.get_key(key_name, validate=validate)
    except BotoClientError as e:
      raise S3FileSystemException(_('Failed to access path at "%s": %s') % (path, e.reason))
    except S3ResponseError as e:
      if e.status in (301, 400):
        raise S3FileSystemException(_('Failed to access path: "%s" '
          'Check that you have access to read this bucket and that the region is correct: %s') % (path, e.message or e.reason))
      elif e.status == 403:
        raise S3FileSystemException(_('User is not authorized to access path at "%s".' % path))
      else:
        raise S3FileSystemException(e.message or e.reason)

  def _get_location(self):
    if get_default_region() in get_locations():
      return get_default_region()
    else:
      return Location.DEFAULT

  def _stats(self, path):
    if S3FileSystem.isroot(path):
      return S3Stat.for_s3_root()

    try:
      key = self._get_key(path, validate=True)
    except BotoClientError as e:
      raise S3FileSystemException(_('Failed to access path "%s": %s') % (path, e.reason))
    except S3ResponseError as e:
      if e.status == 404:
        return None
      elif e.status == 403:
        raise S3FileSystemException(_('User is not authorized to access path: "%s"') % path)
      else:
        raise S3FileSystemException(_('Failed to access path "%s": %s') % (path, e.reason))
    except Exception as e:  # SSL errors show up here, because they've been remapped in boto
      raise S3FileSystemException(_('Failed to access path "%s": %s') % (path, str(e)))
    if key is None:
      key = self._get_key(path, validate=False)
    return self._stats_key(key, self.fs)

  @staticmethod
  def _stats_key(key, fs='s3a'):
    if key.size is not None:
      is_directory_name = not key.name or key.name[-1] == '/'
      return S3Stat.from_key(key, is_dir=is_directory_name, fs=fs)
    else:
      key.name = S3FileSystem._append_separator(key.name)
      ls = key.bucket.get_all_keys(prefix=key.name, max_keys=1)  # Not sure possible via signed request
      if len(ls) > 0:
        return S3Stat.from_key(key, is_dir=True, fs=fs)
    return None

  @staticmethod
  def _append_separator(path):
    if path and not path.endswith('/'):
      path += '/'
    return path

  @staticmethod
  def _cut_separator(path):
    return path.endswith('/') and path[:-1] or path

  @staticmethod
  def isroot(path):
    parsed = lib_urlparse(path)
    return (parsed.path == '/' or parsed.path == '') and parsed.netloc == ''

  @staticmethod
  def join(*comp_list):
    return s3.join(*comp_list)

  @staticmethod
  def normpath(path):
    return normpath(path)

  def netnormpath(self, path):
    return normpath(path)

  @staticmethod
  def parent_path(path):
    parent_dir = S3FileSystem._append_separator(path)
    if not S3FileSystem.isroot(parent_dir):
      bucket_name, key_name, basename = s3.parse_uri(path)
      if not basename:  # bucket is top-level so return root
        parent_dir = S3A_ROOT
      else:
        bucket_path = '%s%s' % (S3A_ROOT, bucket_name)
        key_path = '/'.join(key_name.split('/')[:-1])
        parent_dir = s3.abspath(bucket_path, key_path)
    return parent_dir

  @translate_s3_error
  def open(self, path, mode='r'):
    key = self._get_key(path, validate=True)
    if key is None:
      raise S3FileSystemException("No such file or directory: '%s'" % path)
    return s3file.open(key, mode=mode)

  @translate_s3_error
  def read(self, path, offset, length):
    fh = self.open(path, 'r')
    fh.seek(offset, os.SEEK_SET)
    return fh.read(length)

  @translate_s3_error
  def isfile(self, path):
    stat = self._stats(path)
    if stat is None:
      return False
    return not stat.isDir

  @translate_s3_error
  def isdir(self, path):
    stat = self._stats(path)
    if stat is None:
      return False
    return stat.isDir

  @translate_s3_error
  def exists(self, path):
    return self._stats(path) is not None

  @translate_s3_error
  def stats(self, path):
    path = normpath(path)
    stats = self._stats(path)
    if stats:
      return stats
    raise S3FileSystemException("No such file or directory: '%s'" % path)

  @translate_s3_error
  def listdir_stats(self, path, glob=None):
    if glob is not None:
      raise NotImplementedError(_("Option `glob` is not implemented"))

    if S3FileSystem.isroot(path):
      try:
        return sorted(
          [S3Stat.from_bucket(b, self.fs) for b in self._s3_connection.get_all_buckets(headers=self.header_values)], key=lambda x: x.name)
      except S3FileSystemException as e:
        raise e
      except S3ResponseError as e:
        if 'Forbidden' in str(e) or (hasattr(e, 'status') and e.status == 403):
          raise S3ListAllBucketsException(
            _('You do not have permissions to list all buckets. Please specify a bucket name you have access to.'))
        else:
          raise S3FileSystemException(_('Failed to retrieve buckets: %s') % e.reason)
      except Exception as e:
        raise S3FileSystemException(_('Failed to retrieve buckets: %s') % e)

    bucket_name, prefix = s3.parse_uri(path)[:2]
    bucket = self._get_bucket(bucket_name)
    prefix = self._append_separator(prefix)
    res = []
    for item in bucket.list(prefix=prefix, delimiter='/', headers=self.header_values):
      if isinstance(item, Prefix):
        res.append(S3Stat.from_key(Key(item.bucket, item.name), is_dir=True, fs=self.fs))
      else:
        if item.name == prefix:
          continue
        res.append(self._stats_key(item, self.fs))
    return res

  @translate_s3_error
  def listdir(self, path, glob=None):
    return [s3.parse_uri(x.path)[2] for x in self.listdir_stats(path, glob)]

  @translate_s3_error
  @auth_error_handler
  def rmtree(self, path, skipTrash=True):
    """
    Recursively deletes objects from an S3 path.

    This method can delete a single object, all objects under a given prefix (a "directory"),
    or an entire bucket. It handles paginating through keys for deletion to respect
    S3's 1000-key limit per bulk delete request.

    Args:
      path (str): The S3 URI to delete (e.g., 's3a://test-bucket/test-folder/').
      skipTrash (bool): If False, this operation is not supported and will fail.

    Raises:
      NotImplementedError: If `skipTrash` is set to False.
      S3FileSystemException: If any errors occur during the deletion process.
      ValueError: If the provided path is not a valid S3 URI.
    """
    if not skipTrash:
      raise NotImplementedError("Moving to trash is not implemented for S3.")

    try:
      bucket_name, key_name = s3.parse_uri(path)[:2]
    except Exception:
      raise ValueError(f"Invalid S3 URI provided: {path}")

    LOG.info(f"Attempting to recursively delete path: {path}")
    LOG.debug(f"Parsed bucket: '{bucket_name}', key: '{key_name}'")

    if bucket_name and not key_name:
      return self._delete_bucket(bucket_name)

    # Ensure directory-like paths end with a '/' to be used as a prefix
    if self.isdir(path):
      path = self._append_separator(path)
      key_name = self._append_separator(key_name)

    is_directory_key = key_name and key_name.endswith("/")

    try:
      key = self._get_key(path, validate=False)
      bucket = key.bucket
    except Exception as e:
      # Handle cases where the bucket might not exist or connection fails
      LOG.error(f"Failed to connect to bucket '{bucket_name}'. Error: {e}")
      raise S3FileSystemException(f"Could not access bucket '{bucket_name}'.") from e

    if key.exists() or is_directory_key:  # Check both key.exists() and isdir to handle virtual dirs
      keys_to_delete = []

      if is_directory_key:
        for k in bucket.list(prefix=key_name):
          keys_to_delete.append(k)

        # Explicitly add the current directory marker (empty object) if it exists but wasn't included
        dir_marker = bucket.get_key(key_name)
        if dir_marker is not None and dir_marker not in keys_to_delete:
          keys_to_delete.append(dir_marker)
      else:
        # Add the single key object
        keys_to_delete.append(key)

      LOG.info(f"Found {len(keys_to_delete)} S3 object(s) to delete under prefix '{key_name}'.")

      # Calculate total chunks using integer ceiling division.
      total_chunks = (len(keys_to_delete) + S3A_DELETE_CHUNK_SIZE - 1) // S3A_DELETE_CHUNK_SIZE
      all_errors = []

      # Process keys in chunks of 1000 (S3 API limit)
      for i in range(0, len(keys_to_delete), S3A_DELETE_CHUNK_SIZE):
        chunk = keys_to_delete[i : i + S3A_DELETE_CHUNK_SIZE]

        LOG.debug(f"Deleting chunk {i // S3A_DELETE_CHUNK_SIZE + 1} of {total_chunks} (size: {len(chunk)} keys).")
        try:
          result = bucket.delete_keys(chunk)
          if result.errors:
            LOG.warning(f"Encountered {len(result.errors)} errors in this deletion chunk.")
            all_errors.extend(result.errors)
        except S3ResponseError as e:
          # Catch potential connection errors or access denied on the delete call itself
          LOG.error(f"An S3 API error occurred during key deletion: {e}")
          raise S3FileSystemException(f"Failed to delete objects: {e.message}") from e

      # After deleting all keys, handle any accumulated errors
      if all_errors:
        error_details = "\n".join([f"- {err.key}: {err.message}" for err in all_errors])
        msg = f"{len(all_errors)} errors occurred while deleting objects from '{path}':\n{error_details}"
        LOG.error(msg)
        raise S3FileSystemException(msg)

      LOG.info(f"Successfully deleted {len(keys_to_delete)} object(s) from path: {path}")

  @translate_s3_error
  @auth_error_handler
  def remove(self, path, skip_trash=True):
    self.rmtree(path, skipTrash=skip_trash)

  def restore(self, *args, **kwargs):
    raise NotImplementedError(_('Moving to trash is not implemented for S3'))

  def filebrowser_action(self):
    return self._filebrowser_action

  def create_home_dir(self, home_path):
    # When S3 raz is enabled, try to create user home directory
    if is_raz_s3():
      LOG.debug('Attempting to create user directory for path: %s' % home_path)
      try:
        self.mkdir(home_path)
      except Exception as e:
        LOG.exception('Failed to create user home directory for path %s with error: %s' % (home_path, str(e)))
    else:
      LOG.info('Create home directory is not available for S3 filesystem')

  @translate_s3_error
  @auth_error_handler
  def mkdir(self, path, *args, **kwargs):
    """
    Creates a directory and any parent directory if necessary.

    Actually it creates an empty object: s3://[bucket]/[path]/
    """
    bucket_name, key_name = s3.parse_uri(path)[:2]
    if not BUCKET_NAME_PATTERN.match(bucket_name):
      raise S3FileSystemException(_('Invalid bucket name: %s') % bucket_name)

    try:
      self._get_or_create_bucket(bucket_name)
    except S3FileSystemException as e:
      raise e
    except S3ResponseError as e:
      raise S3FileSystemException(_('Failed to create S3 bucket "%s": %s: %s') % (bucket_name, e.reason, e.body))
    except Exception as e:
      raise S3FileSystemException(_('Failed to create S3 bucket "%s": %s') % (bucket_name, e))

    stats = self._stats(path)
    if stats:
      if stats.isDir:
        return None
      else:
        raise S3FileSystemException("'%s' already exists and is not a directory" % path)
    path = self._append_separator(path)  # folder-key should ends by /
    self.create(path)  # create empty object

  @translate_s3_error
  @auth_error_handler
  def copy(self, src, dst, recursive=False, *args, **kwargs):
    self._copy(src, dst, recursive=recursive, use_src_basename=True)

  @translate_s3_error
  @auth_error_handler
  def copyfile(self, src, dst, *args, **kwargs):
    if self.isdir(dst):
      raise S3FileSystemException("Copy dst '%s' is a directory" % dst)
    self._copy(src, dst, recursive=False, use_src_basename=False)

  @translate_s3_error
  @auth_error_handler
  def copy_remote_dir(self, src, dst, *args, **kwargs):
    self._copy(src, dst, recursive=True, use_src_basename=False)

  def _copy(self, src, dst, recursive, use_src_basename):
    src_st = self.stats(src)
    if src_st.isDir and not recursive:
      return  # omitting directory

    dst = s3.abspath(src, dst)
    dst_st = self._stats(dst)
    if src_st.isDir and dst_st and not dst_st.isDir:
      raise S3FileSystemException("Cannot overwrite non-directory '%s' with directory '%s'" % (dst, src))

    # Skip operation if destination path is same as source path
    if self._check_key_parent_path(src, dst):
      raise S3FileSystemException('Destination path is same as the source path, skipping the operation.')

    src_bucket, src_key = s3.parse_uri(src)[:2]
    dst_bucket, dst_key = s3.parse_uri(dst)[:2]

    keep_src_basename = use_src_basename and dst_st and dst_st.isDir
    src_bucket = self._get_bucket(src_bucket)
    dst_bucket = self._get_bucket(dst_bucket)

    if keep_src_basename:
      cut = len(posixpath.dirname(src_key))  # cut of an parent directory name
      if cut:
        cut += 1
    else:
      cut = len(src_key)
      if not src_key.endswith('/'):
        cut += 1

    # handling files and directories distinctly. When dealing with files, extract the key and copy the file to the specified location.
    # Regarding directories, when listing keys with the 'test1' prefix, it was including all directories or files starting with 'test1,'
    # such as test1, test123, and test1234. Since we need the test1 directory only, we add '/' after the source key name,
    # resulting in 'test1/'.
    if src_st.isDir:
      src_key = self._append_separator(src_key)
      for key in src_bucket.list(prefix=src_key):
        if not key.name.startswith(src_key):
          raise S3FileSystemException(_("Invalid key to transform: %s") % key.name)
        dst_name = posixpath.normpath(s3.join(dst_key, key.name[cut:]))

        if self.isdir(normpath(self.join(S3A_ROOT, key.bucket.name, key.name))):
          dst_name = self._append_separator(dst_name)

        key.copy(dst_bucket, dst_name)
    else:
      key = self._get_key(src)
      dst_name = posixpath.normpath(s3.join(dst_key, src_key[cut:]))
      key.copy(dst_bucket, dst_name)

  @translate_s3_error
  @auth_error_handler
  def rename(self, old, new):
    new = s3.abspath(old, new)

    # Skip operation if destination path is same as source path
    if not self._check_key_parent_path(old, new):
      self.copy(old, new, recursive=True)
      self.rmtree(old, skipTrash=True)
    else:
      raise S3FileSystemException('Destination path is same as source path, skipping the operation.')

  @translate_s3_error
  @auth_error_handler
  def _check_key_parent_path(self, src, dst):
    # Return True if parent path of source is same as destination path.
    if S3FileSystem.parent_path(src) == dst:
      return True
    else:
      return False

  @translate_s3_error
  @auth_error_handler
  def rename_star(self, old_dir, new_dir):
    if not self.isdir(old_dir):
      raise S3FileSystemException("'%s' is not a directory" % old_dir)
    if self.isfile(new_dir):
      raise S3FileSystemException("'%s' is not a directory" % new_dir)
    ls = self.listdir(old_dir)
    for entry in ls:
      self.rename(s3.join(old_dir, entry), s3.join(new_dir, entry))

  @translate_s3_error
  @auth_error_handler
  def create(self, path, overwrite=False, data=None):
    key = self._get_key(path, validate=False)
    key.set_contents_from_string(data or '', replace=overwrite)

  @translate_s3_error
  @auth_error_handler
  def copyFromLocal(self, local_src, remote_dst, *args, **kwargs):
    local_src = self._cut_separator(local_src)
    remote_dst = self._cut_separator(remote_dst)

    def _copy_file(src, dst):
      key = self._get_key(dst, validate=False)
      fp = open(src, 'r')
      key.set_contents_from_file(fp)

    if os.path.isdir(local_src):
      for (local_dir, sub_dirs, files) in os.walk(local_src, followlinks=False):
        remote_dir = local_dir.replace(local_src, remote_dst)

        if not sub_dirs and not files:
          self.mkdir(remote_dir)
        else:
          for file_name in files:
            _copy_file(os.path.join(local_dir, file_name), os.path.join(remote_dir, file_name))
    else:
      file_name = os.path.split(local_src)[1]
      if self.isdir(remote_dst):
        remote_file = os.path.join(remote_dst, file_name)
      else:
        remote_file = remote_dst
      _copy_file(local_src, remote_file)

  # Deprecated
  @translate_s3_error
  def upload(self, file, path, *args, **kwargs):
    pass  # upload is handled by S3FileUploadHandler

  @translate_s3_error
  @auth_error_handler
  def append(self, path, data):
    key = self._get_key(path, validate=False)
    current_data = key.get_contents_as_string() or ''
    new_data = data or ''
    key.set_contents_from_string(current_data + new_data, replace=True)

  @translate_s3_error
  def check_access(self, path, permission='READ'):
    permission = permission.upper()
    try:
      if permission == 'WRITE':
        tmp_file = 'temp_%s' % str(int(time.time() * 1000))
        tmp_path = '%s/%s' % (path, tmp_file)
        self.create(path=tmp_path, overwrite=True)
        self.remove(path=tmp_path)
      else:
        self.open(path)
    except Exception as e:
      LOG.warning('S3 check_access encountered error verifying %s permission at path "%s": %s' % (permission, path, str(e)))
      return False
    return True

  def setuser(self, user):
    self.user = user  # Only used in Cluster middleware request.fs

  def get_upload_chuck_size(self):
    from hadoop.conf import UPLOAD_CHUNK_SIZE  # circular dependency
    return UPLOAD_CHUNK_SIZE.get()

  def get_upload_handler(self, destination_path, overwrite):
    from aws.s3.upload import S3NewFileUploadHandler
    return S3NewFileUploadHandler(self, destination_path, overwrite)
