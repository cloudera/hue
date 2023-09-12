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
import re
import logging

from boto.exception import BotoClientError, S3ResponseError, GSResponseError
from boto.gs.connection import Location
from boto.gs.key import Key
from boto.s3.prefix import Prefix

from desktop.conf import PERMISSION_ACTION_GS
from desktop.lib.fs.gc import GS_ROOT, abspath, parse_uri, translate_s3_error, normpath, join as gs_join

from aws.s3.s3fs import S3FileSystem
from aws.s3.s3stat import S3Stat


DEFAULT_READ_SIZE = 1024 * 1024  # 1MB
BUCKET_NAME_PATTERN = re.compile(
  "^((?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9_\-]*[a-zA-Z0-9])\.)*(?:[A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9_\-]*[A-Za-z0-9]))$")


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


def get_gs_home_directory(user=None):
  from desktop.models import _handle_user_dir_raz

  remote_home_gs = 'gs://'
  if hasattr(REMOTE_STORAGE_HOME, 'get') and REMOTE_STORAGE_HOME.get() and REMOTE_STORAGE_HOME.get().startswith('gs://'):
    remote_home_gs = REMOTE_STORAGE_HOME.get()

  remote_home_gs = _handle_user_dir_raz(user, remote_home_gs)

  return remote_home_gs


class GSFileSystem(S3FileSystem):

  def __init__(self, gs_connection, expiration=None, fs='gs', headers=None, filebrowser_action=PERMISSION_ACTION_GS):
    super(GSFileSystem, self).__init__(
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
    parent_dir = GSFileSystem._append_separator(path)
    if not S3FileSystem.isroot(parent_dir):
      bucket_name, key_name, basename = parse_uri(path)
      if not basename:  # bucket is top-level so return root
        parent_dir = GS_ROOT
      else:
        bucket_path = '%s%s' % (GS_ROOT, bucket_name)
        key_path = '/'.join(key_name.split('/')[:-1])
        parent_dir = abspath(bucket_path, key_path)
    return parent_dir
  
  @translate_s3_error
  def stats(self, path):
    path = normpath(path)
    stats = self._stats(path)
    if stats:
      return stats
    raise S3FileSystemException("No such file or directory: '%s'" % path)


  @translate_s3_error
  @auth_error_handler
  def create(self, path, overwrite=False, data=None):

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

    # print('++++++++++++++++++++++++++++++++++++++++++++++++')
    # print(bucket_name, key_name)
    # print('++++++++++++++++++++++++++++++++++++++++++++++++')

    bucket = self._get_bucket(bucket_name)

    # print('-------------------------------- bucket ')
    # print(bucket)
    # print('--------------------------------')

    try:
      # get_key() expects key name ending with '/' for directory in GS
      # Check for directory
      key_name_with_slash = self._append_separator(key_name)
      key = bucket.get_key(key_name_with_slash, headers=self.header_values)

      if not key:
        # get_key() expects key name as it is for file like object in GS
        # Check for file like object now
        key = bucket.get_key(key_name, headers=self.header_values)

      # import pdb
      # pdb.set_trace()

      return key

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
    except GSResponseError as e:
      raise e


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
        raise S3FileSystemException(('Failed to retrieve buckets: %s') % e)

    bucket_name, prefix = parse_uri(path)[:2]
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
    return [parse_uri(x.path)[2] for x in self.listdir_stats(path, glob)]
  

  @translate_s3_error
  @auth_error_handler
  def rmtree(self, path, skipTrash=True):
    if not skipTrash:
      raise NotImplementedError(_('Moving to trash is not implemented for S3'))

    bucket_name, key_name = parse_uri(path)[:2]
    if bucket_name and not key_name:
      self._delete_bucket(bucket_name)
    else:
      if self.isdir(path):
        path = self._append_separator(path)  # Really need to make sure we end with a '/'

      key = self._get_key(path, validate=False)

      if key.exists():
        to_delete = [key]
        dir_keys = []

        if self.isdir(path):
          dir_keys = key.bucket.list(prefix=path)
          to_delete = itertools.chain(dir_keys, to_delete)

        if not dir_keys:
          # Avoid Raz bulk delete issue
          deleted_key = key.delete()
          if deleted_key.exists():
            raise S3FileSystemException('Could not delete key %s' % deleted_key)
        else:
          result = key.bucket.delete_keys(to_delete)
          if result.errors:
            msg = "%d errors occurred while attempting to delete the following S3 paths:\n%s" % (
              len(result.errors), '\n'.join(['%s: %s' % (error.key, error.message) for error in result.errors])
            )
            LOG.error(msg)
            raise S3FileSystemException(msg)
  

  @translate_s3_error
  @auth_error_handler
  def mkdir(self, path, *args, **kwargs):
    """
    Creates a directory and any parent directory if necessary.

    Actually it creates an empty object: s3://[bucket]/[path]/
    """
    bucket_name, key_name = parse_uri(path)[:2]
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
  

  def _copy(self, src, dst, recursive, use_src_basename):
    src_st = self.stats(src)
    if src_st.isDir and not recursive:
      return # omitting directory

    dst = abspath(src, dst)
    dst_st = self._stats(dst)
    if src_st.isDir and dst_st and not dst_st.isDir:
      raise S3FileSystemException("Cannot overwrite non-directory '%s' with directory '%s'" % (dst, src))

    src_bucket, src_key = parse_uri(src)[:2]
    dst_bucket, dst_key = parse_uri(dst)[:2]

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

    for key in src_bucket.list(prefix=src_key):
      if not key.name.startswith(src_key):
        raise S3FileSystemException(_("Invalid key to transform: %s") % key.name)
      dst_name = posixpath.normpath(s3.join(dst_key, key.name[cut:]))

      if self.isdir(normpath(self.join(GS_ROOT, key.bucket.name, key.name))):
        dst_name = self._append_separator(dst_name)

      key.copy(dst_bucket, dst_name)
  
  @translate_s3_error
  @auth_error_handler
  def rename(self, old, new):
    new = abspath(old, new)
    self.copy(old, new, recursive=True)
    self.rmtree(old, skipTrash=True)
  