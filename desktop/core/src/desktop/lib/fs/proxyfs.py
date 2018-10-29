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

import logging

from urlparse import urlparse
from django.contrib.auth.models import User

from desktop.auth.backend import is_admin

LOG = logging.getLogger(__name__)


class ProxyFS(object):

  def __init__(self, filesystems_dict, default_scheme):
    if default_scheme not in filesystems_dict:
      raise ValueError(
        'Default scheme "%s" is not a member of provided schemes: %s' % (default_scheme, filesystems_dict.keys()))

    self._fs_dict = filesystems_dict
    self._fs_set = set(self._fs_dict.values())
    self._default_scheme = default_scheme
    self._default_fs = self._fs_dict[self._default_scheme]

  def __getattr__(self, item):
    return getattr(object.__getattribute__(self, "_default_fs"), item)

  def __setattr__(self, key, value):
    if hasattr(self, "_default_fs") and hasattr(self._default_fs, key):
      setattr(self._default_fs, key, value)
    else:
      object.__setattr__(self, key, value)

  def _get_scheme(self, path):
    split = urlparse(path)
    return split.scheme if split.scheme else self._default_scheme

  def _has_access(self, fs):
    from desktop.auth.backend import rewrite_user  # Avoid cyclic loop
    try:
      filebrowser_action = fs.filebrowser_action()
      #if not filebrowser_action (hdfs) then handle permission via doas else check permission in hue
      if not filebrowser_action:
        return True
      user = rewrite_user(User.objects.get(username=self.user))
      return user.is_authenticated() and user.is_active and (is_admin(user) or not filebrowser_action or user.has_hue_permission(action=filebrowser_action, app="filebrowser"))
    except User.DoesNotExist:
      LOG.exception('proxyfs.has_access()')
      return False

  def _get_fs(self, path):
    scheme = self._get_scheme(path)
    if not scheme:
      raise IOError('Can not figure out scheme for path "%s"' % path)
    try:
      fs = self._fs_dict[scheme]
      if (self._has_access(fs)):
        return fs
      else:
        raise IOError("Missing permissions for %s on %s" % (self.user, path))
    except KeyError:
      raise IOError('Unknown scheme %s, available schemes: %s' % (scheme, self._fs_dict.keys()))

  def _get_fs_pair(self, src, dst):
    """
    Returns two FS for source and destination paths respectively.
    If `dst` is not self-contained path assumes it's relative path to `src`.
    """

    src_fs = self._get_fs(src)
    dst_scheme = urlparse(dst).scheme
    if not dst_scheme:
      return src_fs, src_fs
    return src_fs, self._get_fs(dst)

  def setuser(self, user):
    """Set a new user. Return the past current user."""
    curr = self.user
    for fs in self._fs_set:
      fs.setuser(user)
    return curr

  def do_as_user(self, username, fn, *args, **kwargs):
    prev = self.user
    try:
      self.setuser(username)
      return fn(*args, **kwargs)
    finally:
      self.setuser(prev)

  def do_as_superuser(self, fn, *args, **kwargs):
    return self.do_as_user(self._default_fs.superuser, fn, *args, **kwargs)

  # Proxy methods to suitable filesystem
  # ------------------------------------
  def isdir(self, path):
    return self._get_fs(path).isdir(path)

  def isfile(self, path):
    return self._get_fs(path).isfile(path)

  def stats(self, path):
    return self._get_fs(path).stats(path)

  def listdir_stats(self, path, **kwargs):
    return self._get_fs(path).listdir_stats(path, **kwargs)

  def listdir(self, path, glob=None):
    return self._get_fs(path).listdir(path, glob)

  def normpath(self, path):
    return self._get_fs(path).normpath(path)

  def netnormpath(self, path):
    return self._get_fs(path).netnormpath(path)

  def open(self, path, *args, **kwargs):
    return self._get_fs(path).open(path, *args, **kwargs)

  def exists(self, path):
    return self._get_fs(path).exists(path)

  def isroot(self, path):
    return self._get_fs(path).isroot(path)

  def parent_path(self, path):
    return self._get_fs(path).parent_path(path)

  def join(self, first, *comp_list):
    return self._get_fs(first).join(first, *comp_list)

  def mkdir(self, path, *args, **kwargs):
    return self._get_fs(path).mkdir(path, *args, **kwargs)

  def read(self, path, *args, **kwargs):
    return self._get_fs(path).read(path, *args, **kwargs)

  def append(self, path, *args, **kwargs):
    return self._get_fs(path).append(path, *args, **kwargs)

  def rmtree(self, path, *args, **kwargs):
    self._get_fs(path).rmtree(path, *args, **kwargs)

  def remove(self, path, skip_trash=False):
    self._get_fs(path).remove(path, skip_trash)

  def restore(self, path):
    self._get_fs(path).restore(path)

  def create(self, path, *args, **kwargs):
    self._get_fs(path).create(path, *args, **kwargs)

  def create_home_dir(self, home_path=None):
    if home_path is None:
      home_path = self.get_home_dir()
    self._get_fs(home_path).create_home_dir(home_path)

  def chown(self, path, *args, **kwargs):
    self._get_fs(path).chown(path, *args, **kwargs)

  def chmod(self, path, *args, **kwargs):
    self._get_fs(path).chmod(path, *args, **kwargs)

  def copyFromLocal(self, local_src, remote_dst, *args, **kwargs):
    self._get_fs(remote_dst).copyFromLocal(local_src, remote_dst, *args, **kwargs)

  def mktemp(self, subdir='', prefix='tmp', basedir=None):
    fs = basedir and self._get_fs(basedir) or self.default_fs
    return fs.mktemp(subdir=subdir, prefix=prefix, basedir=basedir)

  def purge_trash(self):
    for fs in self._fs_set:
      if hasattr(fs, 'purge_trash'):
        fs.purge_trash()

  # Handle file systems interactions
  # --------------------------------
  def copy(self, src, dst, *args, **kwargs):
    src_fs, dst_fs = self._get_fs_pair(src, dst)
    op = src_fs.copy if src_fs is dst_fs else self._copy_between_filesystems
    return op(src, dst, *args, **kwargs)

  def _copy_between_filesystems(self, src, dst, recursive=False, *args, **kwargs):
    raise NotImplementedError("Will be addressed in HUE-2934")

  def copyfile(self, src, dst, *args, **kwargs):
    src_fs, dst_fs = self._get_fs_pair(src, dst)
    op = src_fs.copyfile if src_fs is dst_fs else self._copyfile_between_filesystems
    return op(src, dst, *args, **kwargs)

  def _copyfile_between_filesystems(self, src, dst, *args, **kwargs):
    raise NotImplementedError("Will be addressed in HUE-2934")

  def copy_remote_dir(self, src, dst, *args, **kwargs):
    src_fs, dst_fs = self._get_fs_pair(src, dst)
    op = src_fs.copy_remote_dir if src_fs is dst_fs else self._copy_remote_dir_between_filesystems
    return op(src, dst, *args, **kwargs)

  def _copy_remote_dir_between_filesystems(self, src, dst, *args, **kwargs):
    raise NotImplementedError("Will be addressed in HUE-2934")

  def rename(self, old, new):
    old_fs, new_fs = self._get_fs_pair(old, new)
    op = old_fs.rename if old_fs is new_fs else self._rename_between_filesystems
    return op(old, new)

  def _rename_between_filesystems(self, old, new):
    raise NotImplementedError("Will be addressed in HUE-2934")

  def rename_star(self, old_dir, new_dir):
    old_fs, new_fs = self._get_fs_pair(old_dir, new_dir)
    op = old_fs.rename_star if old_fs is new_fs else self._rename_star_between_filesystems
    return op(old_dir, new_dir)

  def _rename_star_between_filesystems(self, old, new):
    raise NotImplementedError("Will be addressed in HUE-2934")

  def upload(self, file, path, *args, **kwargs):
    self._get_fs(path).upload(file, path, *args, **kwargs)

  def check_access(self, path, *args, **kwargs):
    self._get_fs(path).check_access(path, *args, **kwargs)

  def mkswap(self, filename, subdir='', suffix='swp', basedir=None):
    return self._get_fs(basedir).mkswap(filename, subdir, suffix, basedir)

  def get_upload_chuck_size(self, path):
    return self._get_fs(path).get_upload_chuck_size()
