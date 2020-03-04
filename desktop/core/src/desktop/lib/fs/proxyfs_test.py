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

import sys

from builtins import object
from nose.plugins.attrib import attr
from nose.tools import assert_raises, assert_false, eq_
from nose import SkipTest

from useradmin.models import User

from desktop.auth.backend import rewrite_user
from desktop.lib.fs import ProxyFS
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_permission, remove_from_group

if sys.version_info[0] > 2:
  from unittest.mock import patch, MagicMock
else:
  from mock import patch, MagicMock


def test_fs_selection():
  make_logged_in_client(username='test', groupname='default', recreate=True, is_superuser=False)
  user = User.objects.get(username='test')
  with patch('desktop.lib.fs.ProxyFS._has_access') as _has_access:
    _has_access.return_value = True

    s3fs, adls, hdfs, abfs, gs = MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
    proxy_fs = ProxyFS({'s3a': wrapper(s3fs), 'hdfs': wrapper(hdfs), 'adl': wrapper(adls), 'abfs': wrapper(abfs), 'gs': wrapper(gs)}, 'hdfs')
    proxy_fs.setuser(user)

    proxy_fs.isdir('s3a://bucket/key')
    s3fs.isdir.assert_called_once_with('s3a://bucket/key')
    assert_false(hdfs.isdir.called)

    proxy_fs.isfile('hdfs://localhost:42/user/alice/file')
    hdfs.isfile.assert_called_once_with('hdfs://localhost:42/user/alice/file')
    assert_false(s3fs.isfile.called)

    proxy_fs.isdir('adl://net/key')
    adls.isdir.assert_called_once_with('adl://net/key')
    assert_false(hdfs.isdir.called)

    proxy_fs.isdir('abfs://net/key')
    abfs.isdir.assert_called_once_with('abfs://net/key')
    assert_false(hdfs.isdir.called)

    proxy_fs.isdir('gs://net/key')
    gs.isdir.assert_called_once_with('gs://net/key')
    assert_false(hdfs.isdir.called)

    assert_raises(IOError, proxy_fs.stats, 'ftp://host')

def wrapper(mock):
  def tmp(*args, **kwargs):
    return mock
  return tmp


def test_multi_fs_selection():
  make_logged_in_client(username='test', groupname='default', recreate=True, is_superuser=False)
  user = User.objects.get(username='test')

  with patch('desktop.lib.fs.ProxyFS._has_access') as _has_access:
    _has_access.return_value = True

    s3fs, adls, hdfs, abfs, gs = MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
    proxy_fs = ProxyFS({'s3a': wrapper(s3fs), 'hdfs': wrapper(hdfs), 'adl': wrapper(adls), 'abfs': wrapper(abfs), 'gs': wrapper(gs)}, 'hdfs')
    proxy_fs.setuser(user)

    proxy_fs.copy('s3a://bucket1/key', 's3a://bucket2/key')
    s3fs.copy.assert_called_once_with('s3a://bucket1/key', 's3a://bucket2/key')
    assert_false(hdfs.copy.called)

    proxy_fs.copyfile('s3a://bucket/key', 'key2')
    s3fs.copyfile.assert_called_once_with('s3a://bucket/key', 'key2')
    assert_false(hdfs.copyfile.called)

    proxy_fs.copyfile('adl://net/key', 'key2')
    adls.copyfile.assert_called_once_with('adl://net/key', 'key2')
    assert_false(hdfs.copyfile.called)

    proxy_fs.copyfile('abfs:/key', 'key2')
    abfs.copyfile.assert_called_once_with('abfs:/key', 'key2')
    assert_false(hdfs.copyfile.called)

    proxy_fs.rename('/tmp/file', 'shmile')
    hdfs.rename.assert_called_once_with('/tmp/file', 'shmile')
    assert_false(s3fs.rename.called)

    proxy_fs.copyfile('gs://bucket/key', 'key2')
    gs.copyfile.assert_called_once_with('gs://bucket/key', 'key2')
    assert_false(hdfs.copyfile.called)

    # Will be addressed in HUE-2934
    assert_raises(NotImplementedError, proxy_fs.copy_remote_dir, 's3a://bucket/key', 'adl://tmp/dir') # Exception can only be thrown if scheme is specified, else default to 1st scheme


def test_constructor_given_invalid_arguments():
  assert_raises(ValueError, ProxyFS, {'s3a': {}}, 'hdfs')


class MockFs(object):
  def __init__(self, filebrowser_action=None):
    self.user = None
    self._filebrowser_action = filebrowser_action

  def setuser(self, user):
    self.user = user

  def filebrowser_action(self):
    return self._filebrowser_action



class TestFsPermissions(object):

  def test_fs_permissions_regular_user(self):
    user_client = make_logged_in_client(username='test', groupname='default', recreate=True, is_superuser=False)
    user = User.objects.get(username='test')

    s3fs, adls, hdfs, abfs, gs = MockFs("s3_access"), MockFs("adls_access"), MockFs(), MockFs("abfs_access"), MockFs("gs_access")
    proxy_fs = ProxyFS({'s3a': wrapper(s3fs), 'hdfs': wrapper(hdfs), 'adl': wrapper(adls), 'abfs': wrapper(abfs), 'gs': wrapper(gs)}, 'hdfs')
    proxy_fs.setuser(user)

    f = proxy_fs._get_fs

    remove_from_group(user.username, 'has_s3')
    remove_from_group(user.username, 'has_adls')
    remove_from_group(user.username, 'has_abfs')
    remove_from_group(user.username, 'has_gs')

    # No perms by default
    assert_raises(Exception, f, 's3a://bucket')
    assert_raises(Exception, f, 'S3A://bucket/key')
    assert_raises(Exception, f, 'adl://net/key')
    assert_raises(Exception, f, 'adl:/key')
    assert_raises(Exception, f, 'abfs:/key')
    assert_raises(Exception, f, 'gs://bucket/key')
    f('hdfs://path')
    f('/tmp')

    try:
      # Add perm
      add_permission('test', 'has_s3', permname='s3_access', appname='filebrowser')
      add_permission('test', 'has_adls', permname='adls_access', appname='filebrowser')
      add_permission('test', 'has_abfs', permname='abfs_access', appname='filebrowser')
      add_permission('test', 'has_gs', permname='gs_access', appname='filebrowser')

      f('s3a://bucket')
      f('S3A://bucket/key')
      f('adl://net/key')
      f('adl:/key')
      f('abfs:/key')
      f('hdfs://path')
      f('/tmp')
      f('gs://bucket')
    finally:
      remove_from_group(user.username, 'has_s3')
      remove_from_group(user.username, 'has_adls')
      remove_from_group(user.username, 'has_abfs')
      remove_from_group(user.username, 'has_gs')

  def test_fs_permissions_admin_user(self):
    user_client = make_logged_in_client(username='admin', groupname='default', recreate=True, is_superuser=True)
    user = User.objects.get(username='admin')

    s3fs, adls, hdfs, abfs, gs = MockFs("s3_access"), MockFs("adls_access"), MockFs(), MockFs("abfs_access"), MockFs("gs_access")
    proxy_fs = ProxyFS({'s3a': wrapper(s3fs), 'hdfs': wrapper(hdfs), 'adl': wrapper(adls), 'abfs': wrapper(abfs), 'gs': wrapper(gs)}, 'hdfs')
    proxy_fs.setuser(user)

    f = proxy_fs._get_fs

    f('s3a://bucket')
    f('S3A://bucket/key')
    f('adl://net/key')
    f('adl:/key')
    f('abfs:/key')
    f('hdfs://path')
    f('/tmp')
    f('gs://bucket/key')
