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


from nose.tools import assert_raises, assert_false, eq_
from nose import SkipTest

from django.contrib.auth.models import User

from desktop.lib.fs import ProxyFS
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_permission, remove_from_group


def test_fs_selection():
  try:
    from mock import MagicMock
  except ImportError:
    raise SkipTest("Skips until HUE-2947 is resolved")

  make_logged_in_client(username='test', groupname='default', recreate=True, is_superuser=False)
  add_permission('test', 'test', permname='s3_access', appname='filebrowser')

  s3fs, hdfs = MagicMock(), MagicMock()
  proxy_fs = ProxyFS({'s3a': s3fs, 'hdfs': hdfs}, 'hdfs', default_user='test')

  proxy_fs.isdir('s3a://bucket/key')
  s3fs.isdir.assert_called_once_with('s3a://bucket/key')
  assert_false(hdfs.isdir.called)

  proxy_fs.isfile('hdfs://localhost:42/user/alice/file')
  hdfs.isfile.assert_called_once_with('hdfs://localhost:42/user/alice/file')
  assert_false(s3fs.isfile.called)

  proxy_fs.open('/user/alice/file')
  hdfs.open.assert_called_once_with('/user/alice/file')
  assert_false(s3fs.open.called)

  assert_raises(IOError, proxy_fs.stats, 'ftp://host')
  assert_raises(IOError, proxy_fs.stats, 's3//bucket/key')


# TODO: remove after HUE-2947 is resolved
def test__get_fs():
  make_logged_in_client(username='test', groupname='default', recreate=True, is_superuser=False)
  add_permission('test', 'test', permname='s3_access', appname='filebrowser')

  s3fs, hdfs = 'fake_s3', 'fake_hdfs'
  proxy_fs = ProxyFS({'s3a': s3fs, 'hdfs': hdfs}, 'hdfs', default_user='test')
  f = proxy_fs._get_fs

  eq_(f('s3a://bucket'), s3fs)
  eq_(f('S3A://bucket/key'), s3fs)
  eq_(f('hdfs://path'), hdfs)
  eq_(f('/tmp'), hdfs)

  assert_raises(IOError, f, 'ftp://host')
  assert_raises(IOError, f, 's3//bucket/key')


def test_multi_fs_selection():
  try:
    from mock import MagicMock
  except ImportError:
    raise SkipTest("Skips until HUE-2947 is resolved")

  make_logged_in_client(username='test', groupname='default', recreate=True, is_superuser=False)
  add_permission('test', 'test', permname='s3_access', appname='filebrowser')

  s3fs, hdfs = MagicMock(), MagicMock()
  proxy_fs = ProxyFS({'s3a': s3fs, 'hdfs': hdfs}, 'hdfs', default_user='test')

  proxy_fs.copy('s3a://bucket1/key', 's3a://bucket2/key')
  s3fs.copy.assert_called_once_with('s3a://bucket1/key', 's3a://bucket2/key')
  assert_false(hdfs.copy.called)

  proxy_fs.copyfile('s3a://bucket/key', 'key2')
  s3fs.copyfile.assert_called_once_with('s3a://bucket/key', 'key2')
  assert_false(hdfs.copyfile.called)

  proxy_fs.rename('/tmp/file', 'shmile')
  hdfs.rename.assert_called_once_with('/tmp/file', 'shmile')
  assert_false(s3fs.rename.called)

  # Will be addressed in HUE-2934
  assert_raises(NotImplementedError, proxy_fs.copy_remote_dir, 's3a://bucket/key', '/tmp/dir')


# TODO: remove after HUE-2947 is resolved
def test__get_fs_pair():
  make_logged_in_client(username='test', groupname='default', recreate=True, is_superuser=False)
  add_permission('test', 'test', permname='s3_access', appname='filebrowser')

  s3fs, hdfs = 'fake_s3', 'fake_hdfs'
  proxy_fs = ProxyFS({'s3a': s3fs, 'hdfs': hdfs}, 'hdfs', default_user='test')

  f = proxy_fs._get_fs_pair

  eq_(f('s3a://bucket1/key', 's3a://bucket2/key'), (s3fs, s3fs))
  eq_(f('s3a://bucket/key', 'key2'), (s3fs, s3fs))
  eq_(f('/tmp/file', 'shmile'), (hdfs, hdfs))

  assert_raises(IOError, f, 'ftp://host', 'key2')
  assert_raises(IOError, f, 's3//bucket/key', 'hdfs://normal/path')


def test_constructor_given_invalid_arguments():
  assert_raises(ValueError, ProxyFS, {'s3a': {}}, 'hdfs')



class MockFs():
  def setuser(self, user): pass


class TestFsPermissions(object):

  def test_fs_permissions_regular_user(self):
    user_client = make_logged_in_client(username='test', groupname='default', recreate=True, is_superuser=False)
    user = User.objects.get(username='test')

    proxy_fs = ProxyFS({'s3a': MockFs(), 'hdfs': MockFs()}, 'hdfs')
    f = proxy_fs._get_fs

    proxy_fs.setuser(user)

    # No perms by default
    assert_raises(Exception, f, 's3a://bucket')
    assert_raises(Exception, f, 'S3A://bucket/key')
    f('hdfs://path')
    f('/tmp')

    try:
      # Add perm
      add_permission(user.username, 'has_s3', permname='s3_access', appname='filebrowser')

      f('s3a://bucket')
      f('S3A://bucket/key')
      f('hdfs://path')
      f('/tmp')
    finally:
      remove_from_group(user.username, 'has_s3')


  def test_fs_permissions_admin_user(self):
    user_client = make_logged_in_client(username='admin', groupname='default', recreate=True, is_superuser=True)
    user = User.objects.get(username='admin')

    proxy_fs = ProxyFS({'s3a': MockFs(), 'hdfs': MockFs()}, 'hdfs')
    f = proxy_fs._get_fs

    proxy_fs.setuser(user)

    f('s3a://bucket')
    f('S3A://bucket/key')
    f('hdfs://path')
    f('/tmp')
