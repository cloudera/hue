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

import json
import logging
import os
import tempfile
import time
from unittest.mock import Mock

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


class TestABFS:
  @pytest.mark.django_db
  def test_get_abfs_home_directory(self):
    make_logged_in_client(username="test", groupname="test", recreate=True, is_superuser=False)
    user = User.objects.get(username="test")

    make_logged_in_client(username="test_not_me", groupname="test_not_me", recreate=True, is_superuser=False)
    user_not_me = User.objects.get(username="test_not_me")

    # When REMOTE_STORAGE_HOME ends with /user in RAZ ABFS environment.
    resets = [RAZ.IS_ENABLED.set_for_testing(True), REMOTE_STORAGE_HOME.set_for_testing("abfs://gethue-container/user")]

    try:
      default_abfs_home_path = get_abfs_home_directory(user)
      assert default_abfs_home_path == "abfs://gethue-container/user/test"

      default_abfs_home_path = get_abfs_home_directory(user_not_me)
      assert default_abfs_home_path == "abfs://gethue-container/user/test_not_me"
    finally:
      for reset in resets:
        reset()

    # When ABFS filesystem's DEFAULT_HOME_PATH ends with /user in RAZ ABFS environment.
    resets = [
      RAZ.IS_ENABLED.set_for_testing(True),
      ABFS_CLUSTERS.set_for_testing({"default": {"default_home_path": "abfs://gethue-other-container/user"}}),
    ]

    try:
      default_abfs_home_path = get_abfs_home_directory(user)
      assert default_abfs_home_path == "abfs://gethue-other-container/user/test"

      default_abfs_home_path = get_abfs_home_directory(user_not_me)
      assert default_abfs_home_path == "abfs://gethue-other-container/user/test_not_me"
    finally:
      for reset in resets:
        reset()

    # When ABFS filesystem's DEFAULT_HOME_PATH is set in non-RAZ ABFS environment.
    resets = [
      RAZ.IS_ENABLED.set_for_testing(False),
      ABFS_CLUSTERS.set_for_testing({"default": {"default_home_path": "abfs://gethue-other-container/test-dir"}}),
    ]

    try:
      default_abfs_home_path = get_abfs_home_directory(user)
      assert default_abfs_home_path == "abfs://gethue-other-container/test-dir"

      default_abfs_home_path = get_abfs_home_directory(user_not_me)
      assert default_abfs_home_path == "abfs://gethue-other-container/test-dir"
    finally:
      for reset in resets:
        reset()

    # When both REMOTE_STORAGE_HOME and ABFS filesystem's DEFAULT_HOME_PATH are set in RAZ ABFS environment.
    resets = [
      RAZ.IS_ENABLED.set_for_testing(True),
      REMOTE_STORAGE_HOME.set_for_testing("abfs://gethue-container/user"),
      ABFS_CLUSTERS.set_for_testing({"default": {"default_home_path": "abfs://gethue-other-container/user"}}),
    ]

    try:
      # Gives preference to REMOTE_STORAGE_HOME for of backward compatibility.
      default_abfs_home_path = get_abfs_home_directory(user)
      assert default_abfs_home_path == "abfs://gethue-container/user/test"

      default_abfs_home_path = get_abfs_home_directory(user_not_me)
      assert default_abfs_home_path == "abfs://gethue-container/user/test_not_me"
    finally:
      for reset in resets:
        reset()

    # When ABFS filesystem's DEFAULT_HOME_PATH is set but path does not end with ../user or ../user/ in RAZ ABFS environment.
    resets = [
      RAZ.IS_ENABLED.set_for_testing(True),
      ABFS_CLUSTERS.set_for_testing({"default": {"default_home_path": "abfs://gethue-other-container/dir"}}),
    ]

    try:
      default_abfs_home_path = get_abfs_home_directory(user)
      assert default_abfs_home_path == "abfs://gethue-other-container/dir"

      default_abfs_home_path = get_abfs_home_directory(user_not_me)
      assert default_abfs_home_path == "abfs://gethue-other-container/dir"
    finally:
      for reset in resets:
        reset()

    # When some different path is set in both RAZ and non-RAZ ABFS environment.
    resets = [
      RAZ.IS_ENABLED.set_for_testing(True),
      REMOTE_STORAGE_HOME.set_for_testing("s3a://gethue-bucket/user"),
      ABFS_CLUSTERS.set_for_testing({"default": {"default_home_path": "s3a://gethue-other-bucket/dir"}}),
    ]

    try:
      default_abfs_home_path = get_abfs_home_directory(user)
      assert default_abfs_home_path == "abfs://"

      default_abfs_home_path = get_abfs_home_directory(user_not_me)
      assert default_abfs_home_path == "abfs://"
    finally:
      for reset in resets:
        reset()

  @pytest.mark.parametrize(
    "data_size,chunk_size,expected_chunks",
    [
      # Small data - single chunk
      (100, 1024, 1),
      # Exact chunk size
      (1024, 1024, 1),
      # One byte over chunk size
      (1025, 1024, 2),
      # Multiple full chunks
      (3072, 1024, 3),
      # Multiple chunks with partial last chunk
      (3500, 1024, 4),
      # Large data
      (1048576, 65536, 16),  # 1MB data, 64KB chunks
      # Zero size
      (0, 1024, 0),
    ],
  )
  def test_writedata_various_sizes(self, data_size, chunk_size, expected_chunks):
    """Test _writedata with various data sizes and chunk configurations."""

    abfs = ABFS(url="abfs://hue_container@hue_storage.dfs.core.windows.net", fs_defaultfs="https://hue_storage.dfs.core.windows.net/")
    abfs.get_upload_chuck_size = Mock(return_value=chunk_size)
    abfs._append = Mock()
    abfs.flush = Mock()

    path = "abfs://hue_container/test/file.txt"
    data = b"x" * data_size

    abfs._writedata(path, data, data_size)

    assert abfs._append.call_count == expected_chunks

    # Verify each chunk call
    for i in range(expected_chunks):
      start = i * chunk_size
      if i == expected_chunks - 1:  # Last chunk
        length = data_size - start
      else:
        length = chunk_size

      expected_chunk_data = data[start : start + length]
      abfs._append.assert_any_call(path, expected_chunk_data, size=length, params={"position": start})

    # Verify flush is called once with final position
    abfs.flush.assert_called_once_with(path, {"position": data_size})

  def test_writedata_empty_data(self):
    abfs = ABFS(url="abfs://hue_container@hue_storage.dfs.core.windows.net", fs_defaultfs="https://hue_storage.dfs.core.windows.net/")
    abfs.get_upload_chuck_size = Mock(return_value=1024)
    abfs._append = Mock()
    abfs.flush = Mock()

    path = "abfs://hue_container/test/empty.txt"
    data = b""

    abfs._writedata(path, data, 0)

    abfs._append.assert_not_called()  # No append calls for empty data
    abfs.flush.assert_called_once_with(path, {"position": 0})

  def test_writedata_single_byte(self):
    abfs = ABFS(url="abfs://hue_container@hue_storage.dfs.core.windows.net", fs_defaultfs="https://hue_storage.dfs.core.windows.net/")
    abfs.get_upload_chuck_size = Mock(return_value=1024)
    abfs._append = Mock()
    abfs.flush = Mock()

    path = "abfs://hue_container/test/single.txt"
    data = b"a"

    abfs._writedata(path, data, 1)

    abfs._append.assert_called_once_with(path, b"a", size=1, params={"position": 0})
    abfs.flush.assert_called_once_with(path, {"position": 1})

  def test_writedata_boundary_conditions(self):
    """Test _writedata with data at chunk size boundaries."""

    abfs = ABFS(url="abfs://hue_container@hue_storage.dfs.core.windows.net", fs_defaultfs="https://hue_storage.dfs.core.windows.net/")
    chunk_size = 1000
    abfs.get_upload_chuck_size = Mock(return_value=chunk_size)
    abfs._append = Mock()
    abfs.flush = Mock()

    test_cases = [
      (chunk_size - 1, 1),  # 999 bytes = 1 chunk
      (chunk_size, 1),  # 1000 bytes = 1 chunk
      (chunk_size + 1, 2),  # 1001 bytes = 2 chunks
    ]

    for data_size, expected_chunks in test_cases:
      # Reset mocks for each test case
      abfs._append.reset_mock()
      abfs.flush.reset_mock()

      path = f"abfs://hue_container/test/boundary_{data_size}.txt"
      data = b"x" * data_size

      abfs._writedata(path, data, data_size)

      assert abfs._append.call_count == expected_chunks, (
        f"Expected {expected_chunks} chunks for {data_size} bytes, got {abfs._append.call_count}"
      )

  def test_writedata_append_exception_handling(self):
    """Test _writedata behavior when _append raises an exception."""

    abfs = ABFS(url="abfs://hue_container@hue_storage.dfs.core.windows.net", fs_defaultfs="https://hue_storage.dfs.core.windows.net/")
    abfs.get_upload_chuck_size = Mock(return_value=1024)
    abfs._append = Mock(side_effect=Exception("Network error"))
    abfs.flush = Mock()

    path = "abfs://hue_container/test/error.txt"
    data = b"x" * 2048  # 2 chunks

    with pytest.raises(Exception) as exc_info:
      abfs._writedata(path, data, 2048)

    assert str(exc_info.value) == "Network error"
    abfs._append.assert_called_once()  # Should fail on first append
    abfs.flush.assert_not_called()  # Should not reach flush

  def test_writedata_unicode_path(self):
    """Test _writedata with Unicode characters in path."""

    abfs = ABFS(url="abfs://hue_container@hue_storage.dfs.core.windows.net", fs_defaultfs="https://hue_storage.dfs.core.windows.net/")
    abfs.get_upload_chuck_size = Mock(return_value=1024)
    abfs._append = Mock()
    abfs.flush = Mock()

    path = "abfs://hue_container/test/文件名.txt"
    data = b"Hello World"

    abfs._writedata(path, data, 11)

    abfs._append.assert_called_once_with(path, b"Hello World", size=11, params={"position": 0})
    abfs.flush.assert_called_once_with(path, {"position": 11})

  def test_writedata_order_of_operations(self):
    """Test that _append calls happen in correct order and flush is called last."""

    abfs = ABFS(url="abfs://hue_container@hue_storage.dfs.core.windows.net", fs_defaultfs="https://hue_storage.dfs.core.windows.net/")
    abfs.get_upload_chuck_size = Mock(return_value=10)
    append_calls = []
    flush_calls = []

    def track_append(*args, **kwargs):
      append_calls.append(("append", args, kwargs))

    def track_flush(*args, **kwargs):
      flush_calls.append(("flush", args, kwargs))

    abfs._append = Mock(side_effect=track_append)
    abfs.flush = Mock(side_effect=track_flush)

    path = "abfs://hue_container/test/order.txt"
    data = b"0123456789abcdefghij"  # 20 bytes = 2 chunks of 10

    abfs._writedata(path, data, 20)

    all_calls = append_calls + flush_calls

    # Verify order: append(chunk1), append(chunk2), flush
    assert len(all_calls) == 3
    assert all_calls[0][0] == "append"
    assert all_calls[0][2]["params"]["position"] == 0
    assert all_calls[1][0] == "append"
    assert all_calls[1][2]["params"]["position"] == 10
    assert all_calls[2][0] == "flush"

  @pytest.mark.parametrize(
    "data_type",
    [
      b"bytes data",
      bytearray(b"bytearray data"),
    ],
  )
  def test_writedata_different_data_types(self, data_type):
    """Test _writedata with different data types (bytes and bytearray)."""

    abfs = ABFS(url="abfs://hue_container@hue_storage.dfs.core.windows.net", fs_defaultfs="https://hue_storage.dfs.core.windows.net/")
    abfs.get_upload_chuck_size = Mock(return_value=1024)
    abfs._append = Mock()
    abfs.flush = Mock()

    path = "abfs://hue_container/test/types.txt"
    size = len(data_type)

    abfs._writedata(path, data_type, size)

    abfs._append.assert_called_once()
    # Check that the data was passed correctly (may be converted internally)
    call_args = abfs._append.call_args
    assert len(call_args[0][1]) == size  # Second argument is the data

  def test_writedata_large_chunk_size(self):
    """Test _writedata with very large chunk size (larger than data)."""

    abfs = ABFS(url="abfs://hue_container@hue_storage.dfs.core.windows.net", fs_defaultfs="https://hue_storage.dfs.core.windows.net/")
    abfs.get_upload_chuck_size = Mock(return_value=1048576)  # 1MB chunk
    abfs._append = Mock()
    abfs.flush = Mock()

    path = "abfs://hue_container/test/small.txt"
    data = b"Small data"

    abfs._writedata(path, data, 10)

    # Should still make one append call even though chunk size >> data size
    abfs._append.assert_called_once_with(path, b"Small data", size=10, params={"position": 0})
    abfs.flush.assert_called_once_with(path, {"position": 10})


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
    except Exception:
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
      local_file.write(b'0' * file_size)
      local_file.flush()
      self.client.mkdir(self.test_fs + '/test_upload')
      dest_dir = self.test_fs + '/test_upload'
      local_file = local_file.name
      dest_path = '%s/%s' % (dest_dir, os.path.basename(local_file))

      add_permission(self.user.username, 'has_abfs', permname='abfs_access', appname='filebrowser')
      # Just upload the current python file
      try:
        resp = self.c.post('/filebrowser/upload/file?dest=%s' % dest_dir, dict(dest=dest_dir, hdfs_file=open(local_file, 'rb')))
        response = json.loads(resp.content)
      finally:
        remove_from_group(self.user.username, 'has_abfs')

      assert 0 == response['status'], response

      actual = self.client.read(dest_path)
      expected = open(local_file, 'rb').read()
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
