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

from __future__ import absolute_import

import itertools
import logging
import os
import posixpath
import re
import time

from boto.exception import BotoClientError, S3ResponseError
from boto.s3.connection import Location
from boto.s3.key import Key
from boto.s3.prefix import Prefix

from django.utils.translation import ugettext as _

from aws import s3
from aws.conf import get_default_region, get_locations
from aws.s3 import normpath, s3file, translate_s3_error, S3A_ROOT
from aws.s3.s3stat import S3Stat


DEFAULT_READ_SIZE = 1024 * 1024  # 1MB
PERMISSION_ACTION_S3 = "s3_access"
BUCKET_NAME_PATTERN = re.compile("^((?:(?:[a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9_\-]*[a-zA-Z0-9])\.)*(?:[A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9_\-]*[A-Za-z0-9]))$")

LOG = logging.getLogger(__name__)


class S3FileSystemException(IOError):

  def __init__(self, *args, **kwargs):
    super(S3FileSystemException, self).__init__(*args, **kwargs)


def auth_error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except (S3ResponseError, IOError), e:
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
    except Exception, e:
      raise e
  return decorator


class S3FileSystem(object):
  def __init__(self, s3_connection):
    self._s3_connection = s3_connection
    self._filebrowser_action = PERMISSION_ACTION_S3
    self.user = None
    self.is_sentry_managed = lambda path: False
    self.superuser = None
    self.supergroup = None

  def _get_bucket(self, name):
    return self._s3_connection.get_bucket(name)

  def _get_or_create_bucket(self, name):
    try:
      bucket = self._get_bucket(name)
    except BotoClientError, e:
      raise S3FileSystemException(_('Failed to create bucket named "%s": %s') % (name, e.reason))
    except S3ResponseError, e:
      if e.status == 403 or e.status == 301:
        raise S3FileSystemException(_('User is not authorized to access bucket named "%s". '
          'If you are attempting to create a bucket, this bucket name is already reserved.') % name)
      elif e.status == 404:
        kwargs = {}
        if self._get_location():
          kwargs['location'] = self._get_location()
        bucket = self._create_bucket(name, **kwargs)
      elif e.status == 400:
        raise S3FileSystemException(_('Failed to create bucket named "%s": %s') % (name, e.reason))
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
    except S3ResponseError, e:
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
    except BotoClientError, e:
      raise S3FileSystemException(_('Failed to access path at "%s": %s') % (path, e.reason))
    except S3ResponseError, e:
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
    if s3.is_root(path):
      return S3Stat.for_s3_root()

    try:
      key = self._get_key(path, validate=True)
    except BotoClientError, e:
      raise S3FileSystemException(_('Failed to access path "%s": %s') % (path, e.reason))
    except S3ResponseError as e:
      if e.status == 404:
        return None
      elif e.status == 403:
        raise S3FileSystemException(_('User is not authorized to access path: "%s"') % path)
      else:
        raise S3FileSystemException(_('Failed to access path "%s": %s') % (path, e.reason))

    if key is None:
      key = self._get_key(path, validate=False)
    return self._stats_key(key)

  @staticmethod
  def _stats_key(key):
    if key.size is not None:
      is_directory_name = not key.name or key.name[-1] == '/'
      return S3Stat.from_key(key, is_dir=is_directory_name)
    else:
      key.name = S3FileSystem._append_separator(key.name)
      ls = key.bucket.get_all_keys(prefix=key.name, max_keys=1)
      if len(ls) > 0:
        return S3Stat.from_key(key, is_dir=True)
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
    return s3.is_root(path)

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
    if not s3.is_root(parent_dir):
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

    if s3.is_root(path):
      try:
        return sorted([S3Stat.from_bucket(b) for b in self._s3_connection.get_all_buckets()], key=lambda x: x.name)
      except S3FileSystemException, e:
        raise e
      except S3ResponseError, e:
        raise S3FileSystemException(_('Failed to retrieve buckets: %s') % e.reason)
      except Exception, e:
        raise S3FileSystemException(_('Failed to retrieve buckets: %s') % e)

    bucket_name, prefix = s3.parse_uri(path)[:2]
    bucket = self._get_bucket(bucket_name)
    prefix = self._append_separator(prefix)
    res = []
    for item in bucket.list(prefix=prefix, delimiter='/'):
      if isinstance(item, Prefix):
        res.append(S3Stat.from_key(Key(item.bucket, item.name), is_dir=True))
      else:
        if item.name == prefix:
          continue
        res.append(self._stats_key(item))
    return res

  @translate_s3_error
  def listdir(self, path, glob=None):
    return [s3.parse_uri(x.path)[2] for x in self.listdir_stats(path, glob)]

  @translate_s3_error
  @auth_error_handler
  def rmtree(self, path, skipTrash=True):
    if not skipTrash:
      raise NotImplementedError(_('Moving to trash is not implemented for S3'))

    bucket_name, key_name = s3.parse_uri(path)[:2]
    if bucket_name and not key_name:
      self._delete_bucket(bucket_name)
    else:
      key = self._get_key(path, validate=False)

      if key.exists():
        to_delete = iter([key])
      else:
        to_delete = iter([])

      if self.isdir(path):
        # add `/` to prevent removing of `s3://b/a_new` trying to remove `s3://b/a`
        prefix = self._append_separator(key.name)
        keys = key.bucket.list(prefix=prefix)
        to_delete = itertools.chain(keys, to_delete)
      result = key.bucket.delete_keys(to_delete)
      if result.errors:
        msg = "%d errors occurred while attempting to delete the following S3 paths:\n%s" % (
          len(result.errors), '\n'.join(['%s: %s' % (error.key, error.message) for error in result.errors])
        )
        LOG.error(msg)
        raise S3FileSystemException(msg)

  @translate_s3_error
  @auth_error_handler
  def remove(self, path, skip_trash=True):
    self.rmtree(path, skipTrash=skip_trash)

  def restore(self, *args, **kwargs):
    raise NotImplementedError(_('Moving to trash is not implemented for S3'))

  def filebrowser_action(self):
    return self._filebrowser_action


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
    except S3FileSystemException, e:
      raise e
    except S3ResponseError, e:
      raise S3FileSystemException(_('Failed to create S3 bucket "%s": %s: %s') % (bucket_name, e.reason, e.body))
    except Exception, e:
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
      return # omitting directory

    dst = s3.abspath(src, dst)
    dst_st = self._stats(dst)
    if src_st.isDir and dst_st and not dst_st.isDir:
      raise S3FileSystemException("Cannot overwrite non-directory '%s' with directory '%s'" % (dst, src))

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

    for key in src_bucket.list(prefix=src_key):
      if not key.name.startswith(src_key):
        raise S3FileSystemException(_("Invalid key to transform: %s") % key.name)
      dst_name = posixpath.normpath(s3.join(dst_key, key.name[cut:]))

      if self.isdir(normpath(self.join(S3A_ROOT, key.bucket.name, key.name))):
        dst_name = self._append_separator(dst_name)

      key.copy(dst_bucket, dst_name)

  @translate_s3_error
  @auth_error_handler
  def rename(self, old, new):
    new = s3.abspath(old, new)
    self.copy(old, new, recursive=True)
    self.rmtree(old, skipTrash=True)

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
    except Exception, e:
      LOG.warn('S3 check_access encountered error verifying %s permission at path "%s": %s' % (permission, path, str(e)))
      return False
    return True

  def setuser(self, user):
    self.user = user  # Only used in Cluster middleware request.fs

  def get_upload_chuck_size(self):
    from hadoop.conf import UPLOAD_CHUNK_SIZE # circular dependency
    return UPLOAD_CHUNK_SIZE.get()
