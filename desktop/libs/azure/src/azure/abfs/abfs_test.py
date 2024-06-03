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
import json
import time
import logging
import tempfile

import pytest
from django.contrib.auth.models import User
from django.test import TestCase

from azure.abfs.__init__ import abfspath, get_abfs_home_directory
from azure.abfs.abfs import ABFS
from azure.abfs.upload import DEFAULT_WRITE_SIZE
from azure.active_directory import ActiveDirectory
from azure.conf import ABFS_CLUSTERS, AZURE_ACCOUNTS, is_abfs_enabled
from desktop.conf import RAZ
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_permission, add_to_group, grant_access, remove_from_group
from filebrowser.conf import REMOTE_STORAGE_HOME

LOG = logging.getLogger()


@pytest.mark.django_db
def test_get_abfs_home_directory():
  client = make_logged_in_client(username="test", groupname="test", recreate=True, is_superuser=False)
  user = User.objects.get(username="test")

  client_not_me = make_logged_in_client(username="test_not_me", groupname="test_not_me", recreate=True, is_superuser=False)
  user_not_me = User.objects.get(username="test_not_me")

  # When REMOTE_STORAGE_HOME ends with /user in RAZ ABFS environment.
  resets = [RAZ.IS_ENABLED.set_for_testing(True), REMOTE_STORAGE_HOME.set_for_testing('abfs://gethue-container/user')]

  try:
    default_abfs_home_path = get_abfs_home_directory(user)
    assert default_abfs_home_path == 'abfs://gethue-container/user/test'

    default_abfs_home_path = get_abfs_home_directory(user_not_me)
    assert default_abfs_home_path == 'abfs://gethue-container/user/test_not_me'
  finally:
    for reset in resets:
      reset()

  # When ABFS filesystem's DEFAULT_HOME_PATH ends with /user in RAZ ABFS environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    ABFS_CLUSTERS.set_for_testing({'default': {'default_home_path': 'abfs://gethue-other-container/user'}}),
  ]

  try:
    default_abfs_home_path = get_abfs_home_directory(user)
    assert default_abfs_home_path == 'abfs://gethue-other-container/user/test'

    default_abfs_home_path = get_abfs_home_directory(user_not_me)
    assert default_abfs_home_path == 'abfs://gethue-other-container/user/test_not_me'
  finally:
    for reset in resets:
      reset()

  # When ABFS filesystem's DEFAULT_HOME_PATH is set in non-RAZ ABFS environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(False),
    ABFS_CLUSTERS.set_for_testing({'default': {'default_home_path': 'abfs://gethue-other-container/test-dir'}}),
  ]

  try:
    default_abfs_home_path = get_abfs_home_directory(user)
    assert default_abfs_home_path == 'abfs://gethue-other-container/test-dir'

    default_abfs_home_path = get_abfs_home_directory(user_not_me)
    assert default_abfs_home_path == 'abfs://gethue-other-container/test-dir'
  finally:
    for reset in resets:
      reset()

  # When both REMOTE_STORAGE_HOME and ABFS filesystem's DEFAULT_HOME_PATH are set in RAZ ABFS environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    REMOTE_STORAGE_HOME.set_for_testing('abfs://gethue-container/user'),
    ABFS_CLUSTERS.set_for_testing({'default': {'default_home_path': 'abfs://gethue-other-container/user'}}),
  ]

  try:
    # Gives preference to REMOTE_STORAGE_HOME for of backward compatibility.
    default_abfs_home_path = get_abfs_home_directory(user)
    assert default_abfs_home_path == 'abfs://gethue-container/user/test'

    default_abfs_home_path = get_abfs_home_directory(user_not_me)
    assert default_abfs_home_path == 'abfs://gethue-container/user/test_not_me'
  finally:
    for reset in resets:
      reset()

  # When ABFS filesystem's DEFAULT_HOME_PATH is set but path does not end with ../user or ../user/ in RAZ ABFS environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    ABFS_CLUSTERS.set_for_testing({'default': {'default_home_path': 'abfs://gethue-other-container/dir'}}),
  ]

  try:
    default_abfs_home_path = get_abfs_home_directory(user)
    assert default_abfs_home_path == 'abfs://gethue-other-container/dir'

    default_abfs_home_path = get_abfs_home_directory(user_not_me)
    assert default_abfs_home_path == 'abfs://gethue-other-container/dir'
  finally:
    for reset in resets:
      reset()

  # When some different path is set in both RAZ and non-RAZ ABFS environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    REMOTE_STORAGE_HOME.set_for_testing('s3a://gethue-bucket/user'),
    ABFS_CLUSTERS.set_for_testing({'default': {'default_home_path': 's3a://gethue-other-bucket/dir'}}),
  ]

  try:
    default_abfs_home_path = get_abfs_home_directory(user)
    assert default_abfs_home_path == 'abfs://'

    default_abfs_home_path = get_abfs_home_directory(user_not_me)
    assert default_abfs_home_path == 'abfs://'
  finally:
    for reset in resets:
      reset()


@pytest.mark.integration
class ABFSTestBase(TestCase):
  def setup_method(self, method):
    if not is_abfs_enabled():
      pytest.skip("Skipping Test")
    self.client = ABFS.from_config(ABFS_CLUSTERS['default'], ActiveDirectory.from_config(AZURE_ACCOUNTS['default'], version='v2.0'))
    self.c = make_logged_in_client(username='test', is_superuser=False)
    grant_access('test', 'test', 'filebrowser')
    add_to_group('test')
    self.user = User.objects.get(username="test")

    self.test_fs = 'abfs://test' + (str(int(time.time())))
    LOG.debug("%s" % self.test_fs)
    self.client.mkdir(self.test_fs)

  def teardown_method(self, method):
    self.client.rmtree(self.test_fs)

  def test_list(self):
    testfile = 'abfs://'
    filesystems = self.client.listdir(testfile)
    LOG.debug("%s" % filesystems)
    assert filesystems is not None, filesystems

    pathing = self.client.listdir(testfile + filesystems[0], {"recursive": "true"})
    LOG.debug("%s" % pathing)
    assert pathing is not None, pathing

    directory = self.client.listdir(testfile + filesystems[0] + '/' + pathing[0])
    LOG.debug("%s" % directory)
    assert directory is not None, directory

    directory = self.client.listdir(self.test_fs)
    LOG.debug("%s" % directory)
    assert directory is not None, directory

    directory = self.client.listdir(abfspath(self.test_fs))
    LOG.debug("%s" % directory)
    assert directory is not None, directory

    pathing = self.client._statsf(filesystems[276])
    LOG.debug("%s" % pathing)
    assert pathing is not None, pathing

    pathing = self.client._statsf(filesystems[277])
    LOG.debug("%s" % pathing)
    assert pathing is not None, pathing

  def test_existence(self):
    test_fs = self.test_fs
    test_dir = test_fs + '/test_existence'
    test_file = test_dir + '/test.txt'
    self.client.mkdir(test_dir)
    self.client.create(test_file)

    # Testing root and filesystems
    assert self.client.exists('abfs://')
    assert self.client.exists(test_fs)

    # testing created directories and files
    assert self.client.exists(test_dir)
    assert self.client.exists(test_file)
    assert not self.client.exists(test_dir + 'a')

  def test_stat_output(self):
    """
    Only tests if the stat outputs something
    """
    test_fs = self.test_fs
    test_dir = test_fs + '/test_stats'
    test_dir2 = test_dir + '/test2'
    test_dir3 = test_dir2 + '/test3'
    self.client.mkdir(test_dir)
    self.client.mkdir(test_dir2)
    self.client.mkdir(test_dir3)

    # testing filesystems
    result = self.client.stats(test_fs)
    LOG.debug("%s" % result)
    assert result is not None, result
    result = self.client.listdir_stats(test_fs)
    LOG.debug("%s" % result)

    # testing directories
    result = self.client.stats(test_dir)
    LOG.debug("%s" % result)
    result = self.client.listdir_stats(test_dir)
    LOG.debug("%s" % result)

    result = self.client.stats(test_dir2)
    LOG.debug("%s" % result)
    result = self.client.listdir_stats(test_dir2)
    LOG.debug("%s" % result)

    result = self.client.stats(test_dir3)
    LOG.debug("%s" % result)
    result = self.client.listdir_stats(test_dir3)
    LOG.debug("%s" % result)

  def test_mkdir(self):
    test_dir = self.test_fs + '/test_mkdir'
    assert not self.client.exists(test_dir)

    self.client.mkdir(test_dir)
    assert self.client.exists(test_dir)
    self.client.isdir(test_dir)

  def test_append_and_flush(self):
    test_fs = self.test_fs
    test_file = test_fs + '/test.txt'
    self.client.create(test_file)

    test_string = "This is a test."
    test_len = len(test_string)
    resp = self.client._append(test_file, test_string)  # only works with strings
    LOG.debug("%s" % self.client.stats(test_file))
    try:
      LOG.debug("%s" % resp)
      resp = self.client.read(test_file, length=test_len)
    except:
      LOG.debug("Not written yet")

    self.client.flush(test_file, {"position": test_len})
    resp = self.client.read(test_file)
    assert resp == test_string
    self.client.remove(test_file)

  def test_rename(self):
    test_fs = self.test_fs
    test_dir = test_fs + '/test'
    test_dir2 = test_fs + '/test2'
    test_dir3 = test_fs + '/test 3'
    test_file = test_fs + '/test.txt'
    test_file2 = test_fs + '/test2.txt'
    test_file3 = test_fs + '/test 3.txt'

    self.client.mkdir(test_dir)
    assert self.client.exists(test_dir)
    assert not self.client.exists(test_dir2)

    self.client.rename(test_dir, test_dir2)
    assert not self.client.exists(test_dir)
    assert self.client.exists(test_dir2)

    self.client.create(test_file)
    assert self.client.exists(test_file)
    assert not self.client.exists(test_file2)

    self.client.rename(test_file, test_file2)
    assert not self.client.exists(test_file)
    assert self.client.exists(test_file2)

    self.client.rename(test_dir2, test_dir3)
    assert not self.client.exists(test_dir2)
    assert self.client.exists(test_dir3)

    self.client.rename(test_dir3, test_dir2)
    assert not self.client.exists(test_dir3)
    assert self.client.exists(test_dir2)

  def test_chmod(self):
    test_dir = self.test_fs + '/test_chmod'
    self.client.mkdir(test_dir)
    test_dir_permission = test_dir + '/test'
    test_file_permission = test_dir + '/test.txt'

    self.client.create(test_file_permission)
    self.client.chmod(test_file_permission, '0777')
    self.client.stats(test_file_permission)

    self.client.mkdir(test_dir_permission)
    self.client.chmod(test_dir_permission, '0000')
    self.client.chmod(test_dir_permission, '0777')
    self.client.stats(test_dir_permission)

  def test_chown(self):
    test_dir = self.test_fs + '/test_chown'
    self.client.mkdir(test_dir)
    test_dir_permission = test_dir + '/test'
    test_file_permission = test_dir + '/test.txt'

    self.client.create(test_file_permission)
    self.client.chown(test_file_permission, group='$superuser')
    self.client.stats(test_file_permission)

    self.client.mkdir(test_dir_permission)
    self.client.chown(test_dir_permission, group='$superuser')
    self.client.stats(test_dir_permission)

  def test_create_with_file_permissions(self):
    test_dir = self.test_fs + '/test_chown'
    test_file = test_dir + '/test.txt'
    self.client.mkdir(test_dir)
    self.client.create(test_file, headers={'x-ms-permissions': '0777'})

  def test_upload(self):
    with tempfile.NamedTemporaryFile() as local_file:
      # Make sure we can upload larger than the UPLOAD chunk size
      file_size = DEFAULT_WRITE_SIZE * 2
      local_file.write('0' * file_size)
      local_file.flush()
      self.client.mkdir(self.test_fs + '/test_upload')
      dest_dir = self.test_fs + '/test_upload'
      local_file = local_file.name
      dest_path = '%s/%s' % (dest_dir, os.path.basename(local_file))

      add_permission(self.user.username, 'has_abfs', permname='abfs_access', appname='filebrowser')
      # Just upload the current python file
      try:
        resp = self.c.post('/filebrowser/upload/file?dest=%s' % dest_dir, dict(dest=dest_dir, hdfs_file=file(local_file)))
        response = json.loads(resp.content)
      finally:
        remove_from_group(self.user.username, 'has_abfs')

      assert 0 == response['status'], response
      stats = self.client.stats(dest_path)

      actual = self.client.read(dest_path)
      expected = file(local_file).read()
      assert actual == expected, 'files do not match: %s != %s' % (len(actual), len(expected))

  def test_copy_file(self):
    test_fs = self.test_fs
    testdir1 = test_fs + '/testcpy1'
    testdir2 = test_fs + '/testcpy2'
    test_file = testdir1 + '/test.txt'
    self.client.mkdir(testdir1)
    self.client.mkdir(testdir2)
    self.client.create(test_file)

    test_string = "This is a test."
    test_len = len(test_string)
    resp = self.client._append(test_file, test_string)
    self.client.flush(test_file, {"position": test_len})

    self.client.copy(test_file, testdir2)
    self.client.stats(testdir2 + '/test.txt')
    resp = self.client.read(testdir2 + '/test.txt')
    resp2 = self.client.read(test_file)
    assert resp == resp2, "Files %s and %s are not equal" % (test_file, testdir2 + '/test.txt')

  def test_copy_dir(self):
    test_fs = self.test_fs
    testdir1 = test_fs + '/testcpy1'
    testdir2 = test_fs + '/testcpy2'
    test_dir3 = testdir1 + '/test'
    test_dir4 = test_dir3 + '/test2'
    self.client.mkdir(testdir1)
    self.client.mkdir(testdir2)
    self.client.mkdir(test_dir3)
    self.client.mkdir(test_dir4)

    self.client.copy(test_dir3, testdir2)
    self.client.stats(testdir2 + '/test')
    self.client.stats(testdir2 + '/test/test2')

  @staticmethod
  def test_static_methods():
    test_dir = 'abfss://testfs/test_static/'
    LOG.debug("%s" % test_dir)
    norm_path = ABFS.normpath(test_dir)
    LOG.debug("%s" % norm_path)
    parent = ABFS.parent_path(test_dir)
    LOG.debug("%s" % parent)
    join_path = ABFS.join(test_dir, 'test1')
    LOG.debug("%s" % join_path)
