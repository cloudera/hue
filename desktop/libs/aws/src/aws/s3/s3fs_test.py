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
import os
import string
import tempfile
from unittest.mock import MagicMock, Mock

import pytest

from aws.conf import AWS_ACCOUNTS
from aws.s3 import join, parse_uri
from aws.s3.s3fs import get_s3_home_directory, S3A_DELETE_CHUNK_SIZE, S3FileSystem, S3FileSystemException
from aws.s3.s3test_utils import generate_id, S3TestBase
from aws.s3.upload import DEFAULT_WRITE_SIZE
from desktop.conf import RAZ
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_permission, add_to_group, grant_access, remove_from_group
from filebrowser.conf import REMOTE_STORAGE_HOME
from useradmin.models import User


@pytest.mark.django_db
def test_get_s3_home_directory():
  make_logged_in_client(username="test", groupname="test", recreate=True, is_superuser=False)
  user = User.objects.get(username="test")

  make_logged_in_client(username="test_not_me", groupname="test_not_me", recreate=True, is_superuser=False)
  user_not_me = User.objects.get(username="test_not_me")

  # When REMOTE_STORAGE_HOME ends with /user in RAZ S3 environment.
  resets = [RAZ.IS_ENABLED.set_for_testing(True), REMOTE_STORAGE_HOME.set_for_testing("s3a://gethue-bucket/user")]

  try:
    default_s3_home_path = get_s3_home_directory(user)
    assert default_s3_home_path == "s3a://gethue-bucket/user/test"

    default_s3_home_path = get_s3_home_directory(user_not_me)
    assert default_s3_home_path == "s3a://gethue-bucket/user/test_not_me"
  finally:
    for reset in resets:
      reset()

  # When S3 filesystem's DEFAULT_HOME_PATH ends with /user in RAZ S3 environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    AWS_ACCOUNTS.set_for_testing(
      {"default": {"region": "us-west-2", "host": "s3-us-west-2.amazonaws.com", "default_home_path": "s3a://gethue-other-bucket/user"}}
    ),
  ]

  try:
    default_s3_home_path = get_s3_home_directory(user)
    assert default_s3_home_path == "s3a://gethue-other-bucket/user/test"

    default_s3_home_path = get_s3_home_directory(user_not_me)
    assert default_s3_home_path == "s3a://gethue-other-bucket/user/test_not_me"
  finally:
    for reset in resets:
      reset()

  # When S3 filesystem's DEFAULT_HOME_PATH is set in non-RAZ S3 environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(False),
    AWS_ACCOUNTS.set_for_testing(
      {"default": {"region": "us-west-2", "host": "s3-us-west-2.amazonaws.com", "default_home_path": "s3a://gethue-other-bucket/test-dir"}}
    ),
  ]

  try:
    default_s3_home_path = get_s3_home_directory(user)
    assert default_s3_home_path == "s3a://gethue-other-bucket/test-dir"

    default_s3_home_path = get_s3_home_directory(user_not_me)
    assert default_s3_home_path == "s3a://gethue-other-bucket/test-dir"
  finally:
    for reset in resets:
      reset()

  # When both REMOTE_STORAGE_HOME and S3 filesystem's DEFAULT_HOME_PATH are set in RAZ S3 environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    REMOTE_STORAGE_HOME.set_for_testing("s3a://gethue-bucket/user"),
    AWS_ACCOUNTS.set_for_testing(
      {"default": {"region": "us-west-2", "host": "s3-us-west-2.amazonaws.com", "default_home_path": "s3a://gethue-other-bucket/user"}}
    ),
  ]

  try:
    # Gives preference to REMOTE_STORAGE_HOME for of backward compatibility.
    default_s3_home_path = get_s3_home_directory(user)
    assert default_s3_home_path == "s3a://gethue-bucket/user/test"

    default_s3_home_path = get_s3_home_directory(user_not_me)
    assert default_s3_home_path == "s3a://gethue-bucket/user/test_not_me"
  finally:
    for reset in resets:
      reset()

  # When S3 filesystem's DEFAULT_HOME_PATH is set but path does not end with ../user or ../user/ in RAZ S3 environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    AWS_ACCOUNTS.set_for_testing(
      {"default": {"region": "us-west-2", "host": "s3-us-west-2.amazonaws.com", "default_home_path": "s3a://gethue-other-bucket/dir"}}
    ),
  ]

  try:
    default_s3_home_path = get_s3_home_directory(user)
    assert default_s3_home_path == "s3a://gethue-other-bucket/dir"

    default_s3_home_path = get_s3_home_directory(user_not_me)
    assert default_s3_home_path == "s3a://gethue-other-bucket/dir"
  finally:
    for reset in resets:
      reset()

  # When some different path is set in both RAZ and non-RAZ S3 environment.
  resets = [
    RAZ.IS_ENABLED.set_for_testing(True),
    REMOTE_STORAGE_HOME.set_for_testing("abfs://gethue-container/user"),
    AWS_ACCOUNTS.set_for_testing(
      {"default": {"region": "us-west-2", "host": "s3-us-west-2.amazonaws.com", "default_home_path": "abfs://gethue-other-container/dir"}}
    ),
  ]

  try:
    default_s3_home_path = get_s3_home_directory(user)
    assert default_s3_home_path == "s3a://"

    default_s3_home_path = get_s3_home_directory(user_not_me)
    assert default_s3_home_path == "s3a://"
  finally:
    for reset in resets:
      reset()


class TestS3FileSystemRmtree:
  def test_rmtree_skip_trash_false_raises_error(self):
    fs = S3FileSystem(s3_connection=Mock())

    with pytest.raises(NotImplementedError, match="Moving to trash is not implemented"):
      fs.rmtree("s3a://test-bucket/test-path", skipTrash=False)

  @pytest.mark.parametrize("invalid_path", ["/local/path", "http://a.com", "s3:/oops"])
  def test_rmtree_invalid_uri_raises_value_error(self, invalid_path):
    fs = S3FileSystem(s3_connection=Mock())

    with pytest.raises(ValueError, match=f"Invalid S3 URI provided: {invalid_path}"):
      fs.rmtree(invalid_path)

  def test_rmtree_bucket_connection_fails_raises_s3_exception(self):
    fs = S3FileSystem(s3_connection=Mock())
    fs._get_key = Mock(side_effect=Exception("Connection timeout"))
    fs.isdir = Mock(return_value=True)

    with pytest.raises(S3FileSystemException, match="Could not access bucket 'test-bucket'"):
      fs.rmtree("s3a://test-bucket/test-path")

  def test_rmtree_deletes_single_file(self):
    fs = S3FileSystem(s3_connection=Mock())
    fs._get_key = Mock(return_value=Mock(exists=Mock(return_value=True), bucket=Mock(delete_keys=Mock(return_value=Mock(errors=[])))))
    fs.isdir = Mock(return_value=False)

    fs.rmtree("s3a://test-bucket/file.txt")

    fs._get_key.assert_called_once_with("s3a://test-bucket/file.txt", validate=False)
    fs._get_key.return_value.exists.assert_called_once()
    fs._get_key.return_value.bucket.delete_keys.assert_called_once_with([fs._get_key.return_value])

  def test_rmtree_deletes_directory_with_files(self):
    fs = S3FileSystem(s3_connection=Mock())
    fs._get_key = Mock(return_value=Mock(exists=Mock(return_value=True), bucket=Mock(delete_keys=Mock(return_value=Mock(errors=[])))))
    fs.isdir = Mock(return_value=True)

    # Simulate bucket.list() returning a list of mock keys
    keys_in_dir = [
      Mock(name="folder/file1.txt", bucket=fs._get_key.return_value.bucket),
      Mock(name="folder/file2.txt", bucket=fs._get_key.return_value.bucket),
    ]
    fs._get_key.return_value.bucket.list.return_value = keys_in_dir

    # The explicit directory marker doesn't exist
    fs._get_key.return_value.bucket.get_key.return_value = None

    fs.rmtree("s3a://test-bucket/folder")

    fs._get_key.return_value.bucket.list.assert_called_once_with(prefix="folder/")
    fs._get_key.return_value.bucket.delete_keys.assert_called_once_with(keys_in_dir)

  def test_rmtree_deletes_directory_with_explicit_marker(self):
    fs = S3FileSystem(s3_connection=Mock())
    fs._get_key = Mock(return_value=Mock(exists=Mock(return_value=True), bucket=Mock(delete_keys=Mock(return_value=Mock(errors=[])))))
    fs.isdir = Mock(return_value=True)

    keys_in_dir = [Mock(name="folder/file1.txt", bucket=fs._get_key.return_value.bucket)]
    dir_marker_key = Mock(name="folder/", bucket=fs._get_key.return_value.bucket)

    fs._get_key.return_value.bucket.list.return_value = keys_in_dir
    fs._get_key.return_value.bucket.get_key.return_value = dir_marker_key  # The marker exists

    fs.rmtree("s3a://test-bucket/folder")

    fs._get_key.return_value.bucket.get_key.assert_called_once_with("folder/")
    # Check that both the file and the directory marker itself are deleted
    fs._get_key.return_value.bucket.delete_keys.assert_called_once_with([keys_in_dir[0], dir_marker_key])

  def test_rmtree_does_not_delete_for_non_existent_path(self):
    fs = S3FileSystem(s3_connection=Mock())
    fs._get_key = Mock(return_value=Mock(bucket=Mock(delete_keys=Mock())))
    fs.isdir = Mock(return_value=False)

    fs._get_key.return_value.exists.return_value = False  # The key doesn't exist
    fs.isdir.return_value = False  # It's not a directory path

    fs.rmtree("s3a://test-bucket/not-real")

    fs._get_key.return_value.bucket.delete_keys.assert_not_called()

  def test_rmtree_deletes_entire_bucket(self):
    fs = S3FileSystem(s3_connection=Mock())
    fs._delete_bucket = Mock()

    fs.rmtree("s3a://test-bucket")

    fs._delete_bucket.assert_called_once_with("test-bucket")

  def test_rmtree_handles_large_directory_with_chunking(self):
    fs = S3FileSystem(s3_connection=Mock())
    fs._get_key = Mock(return_value=Mock(bucket=Mock(list=Mock(), delete_keys=Mock(return_value=Mock(errors=[]))), get_key=Mock()))
    fs.isdir = Mock(return_value=True)

    # Create more keys than the chunk size
    num_keys = S3A_DELETE_CHUNK_SIZE + 27

    large_key_list = [Mock(name=f"big-folder/file{i}.txt", bucket=fs._get_key.return_value.bucket) for i in range(num_keys)]
    fs._get_key.return_value.bucket.list.return_value = large_key_list
    fs._get_key.return_value.bucket.get_key.return_value = None

    fs.rmtree("s3a://test-bucket/big-folder/")

    # It should have been called twice: once for the first 1000, then for the remaining 27
    assert fs._get_key.return_value.bucket.delete_keys.call_count == 2
    # Check the contents of the calls
    first_call_args, _ = fs._get_key.return_value.bucket.delete_keys.call_args_list[0]
    second_call_args, _ = fs._get_key.return_value.bucket.delete_keys.call_args_list[1]
    assert len(first_call_args[0]) == S3A_DELETE_CHUNK_SIZE
    assert len(second_call_args[0]) == 27
    assert first_call_args[0] == large_key_list[:S3A_DELETE_CHUNK_SIZE]
    assert second_call_args[0] == large_key_list[S3A_DELETE_CHUNK_SIZE:]

  def test_rmtree_handles_partial_deletion_failure(self):
    fs = S3FileSystem(s3_connection=Mock())
    fs._get_key = Mock(return_value=Mock(bucket=Mock(list=Mock(), delete_keys=Mock()), get_key=Mock()))
    fs.isdir = Mock(return_value=True)

    fs._get_key.return_value.bucket.list.return_value = [Mock(name="folder/locked-file.txt", bucket=fs._get_key.return_value.bucket)]
    fs._get_key.return_value.bucket.get_key.return_value = None

    # Simulate some keys that will fail
    error_key = MagicMock()
    error_key.key = "folder/locked-file.txt"
    error_key.message = "Access Denied"

    mock_delete_result = MagicMock()
    mock_delete_result.errors = [error_key]  # Simulate one error
    fs._get_key.return_value.bucket.delete_keys.return_value = mock_delete_result

    with pytest.raises(S3FileSystemException) as excinfo:
      fs.rmtree("s3a://test-bucket/folder/")

    # Check that the exception message is informative
    assert "1 errors occurred" in str(excinfo.value)
    assert "folder/locked-file.txt: Access Denied" in str(excinfo.value)


class S3FSTest(S3TestBase):
  @classmethod
  def setup_class(cls):
    S3TestBase.setup_class()
    if not cls.shouldSkip():
      cls.fs = S3FileSystem(cls.s3_connection)

      cls.c = make_logged_in_client(username="test", is_superuser=False)
      grant_access("test", "test", "filebrowser")
      add_to_group("test")
      cls.user = User.objects.get(username="test")

  def test_open(self):
    path = self.get_test_path("test_open.txt")

    with self.cleaning(path):
      with pytest.raises(S3FileSystemException):
        self.fs.open(path)

      key = self.get_key(path)
      key.set_contents_from_string("Hello")

      fh1 = self.fs.open(path)
      assert "He" == fh1.read(length=2)

      fh2 = self.fs.open(path, mode="r")
      assert "Hello" == fh2.read()

      assert "llo" == fh1.read()

      with pytest.raises(Exception):
        self.fs.open(path, mode="w")
      with pytest.raises(Exception):
        self.fs.open(path, mode="?r")

  def test_read(self):
    path = self.get_test_path("test_read.txt")
    with self.cleaning(path):
      key = self.get_key(path)
      key.set_contents_from_string("Hello")

      assert "Hel" == self.fs.read(path, 0, 3)
      assert "ell" == self.fs.read(path, 1, 3)

  def test_isfile(self):
    pass

  def test_isdir(self):
    pass

  def test_exists(self):
    dir_path = self.get_test_path("test_exists")
    file_path = join(dir_path, "file")

    assert not self.fs.exists(dir_path)
    assert not self.fs.exists(file_path)

    self.fs.create(file_path)

    assert self.fs.exists(dir_path)
    assert self.fs.exists(file_path)

    assert self.fs.exists("s3a://%s" % self.bucket_name)
    assert self.fs.exists("s3a://")
    fake_bucket = "fake%s" % generate_id(8, string.ascii_lowercase + string.digits)
    assert not self.fs.exists("s3a://%s" % fake_bucket)

  def test_stats(self):
    with pytest.raises(ValueError):
      self.fs.stats("ftp://archive")
    not_exists = self.get_test_path("does_not_exist")
    with pytest.raises(S3FileSystemException):
      self.fs.stats(not_exists)

    root_stat = self.fs.stats("s3a://")
    assert True is root_stat.isDir
    assert "s3a://" == root_stat.path

    bucket_stat = self.fs.stats("s3a://%s" % self.bucket_name)
    assert True is bucket_stat.isDir
    assert "s3a://%s" % self.bucket_name == bucket_stat.path

  def test_copyfile(self):
    src_path = self.get_test_path("test_copy_file_src")
    dst_path = self.get_test_path("test_copy_file_dst")
    with self.cleaning(src_path, dst_path):
      data = "To boldly go where no one has gone before\n" * 2000
      self.fs.create(src_path, data=data)
      self.fs.create(dst_path, data="some initial data")

      self.fs.copyfile(src_path, dst_path)
      actual = self.fs.read(dst_path, 0, len(data) + 100)
      assert data == actual

  def test_full_copy(self):
    src_path = self.get_test_path("test_full_copy_src")
    dst_path = self.get_test_path("test_full_copy_dst")

    src_file_path = join(src_path, "file.txt")
    dst_file_path = join(dst_path, "file.txt")

    with self.cleaning(src_path, dst_path):
      self.fs.mkdir(src_path)
      self.fs.mkdir(dst_path)

      data = "To boldly go where no one has gone before\n" * 2000
      self.fs.create(src_file_path, data=data)

      # File to directory copy.
      self.fs.copy(src_file_path, dst_path)
      assert self.fs.exists(dst_file_path)

      # Directory to directory copy.
      self.fs.copy(src_path, dst_path, True)
      base_name = parse_uri(src_path)[2]
      dst_folder_path = join(dst_path, base_name)
      assert self.fs.exists(dst_folder_path)
      assert self.fs.exists(join(dst_folder_path, "file.txt"))

      # Copy directory to file should fail.
      with pytest.raises(S3FileSystemException):
        self.fs.copy(src_path, dst_file_path, True)

  def test_copy_remote_dir(self):
    src_dir = self.get_test_path("test_copy_remote_dir_src")
    dst_dir = self.get_test_path("test_copy_remote_dir_dst")

    with self.cleaning(src_dir, dst_dir):
      self.fs.mkdir(src_dir)

      self.fs.create(join(src_dir, "file_one.txt"), data="foo")
      self.fs.create(join(src_dir, "file_two.txt"), data="bar")

      self.fs.mkdir(dst_dir)
      self.fs.copy_remote_dir(src_dir, dst_dir)

      src_stat = self.fs.listdir_stats(src_dir)
      dst_stat = self.fs.listdir_stats(dst_dir)

      src_names = set([stat.name for stat in src_stat])
      dst_names = set([stat.name for stat in dst_stat])
      assert src_names
      assert src_names == dst_names

  def test_copy_from_local(self):
    src_name = "test_copy_from_local_src"
    src_path = os.path.join(tempfile.gettempdir(), src_name)
    dst_path = self.get_test_path("test_copy_from_local_dst")

    data = "To boldly go where no one has gone before\n" * 2000
    f = open(src_path, "w")
    f.write(data)
    f.close()

    with self.cleaning(dst_path):
      self.fs.copyFromLocal(src_path, dst_path)
      actual = self.fs.read(dst_path, 0, len(data) + 100)
      assert data == actual

  def test_rename_dir(self):
    src_dir = self.get_test_path("test_rename_dir_src")
    dst_dir = self.get_test_path("test_rename_dir_dst")

    with self.cleaning(src_dir, dst_dir):
      self.fs.mkdir(src_dir)
      self.fs.create(join(src_dir, "file_one.txt"), data="foo")
      self.fs.create(join(src_dir, "file_two.txt"), data="bar")

      src_ls = self.fs.listdir(src_dir)
      assert 2 == len(src_ls)
      assert "file_one.txt" in src_ls
      assert "file_two.txt" in src_ls

      # Assert that no directories with dst_dir name exist yet
      assert not self.fs.exists(dst_dir)

      # Rename src to dst
      self.fs.rename(src_dir, dst_dir)
      assert self.fs.exists(dst_dir)
      assert not self.fs.exists(src_dir)

      dst_ls = self.fs.listdir(dst_dir)
      assert 2 == len(dst_ls)
      assert "file_one.txt" in dst_ls
      assert "file_two.txt" in dst_ls

      # Assert that the children files are not duplicated at top-level destination
      bucket_ls = self.bucket.list()
      assert "file_one.txt" not in bucket_ls
      assert "file_two.txt" not in bucket_ls

      # Assert that only the renamed directory, and not an empty file, exists
      assert 1 == len([key for key in bucket_ls if key.name.strip("/") == self.get_key(dst_dir).name.strip("/")])

  def test_rename_star(self):
    src_dir = self.get_test_path("test_rename_star_src")
    dst_dir = self.get_test_path("test_rename_star_dst")

    with self.cleaning(src_dir, dst_dir):
      self.fs.mkdir(src_dir)
      self.fs.create(join(src_dir, "file_one.txt"), data="foo")
      self.fs.create(join(src_dir, "file_two.txt"), data="bar")

      src_ls = self.fs.listdir(src_dir)
      assert 2 == len(src_ls)
      assert "file_one.txt" in src_ls
      assert "file_two.txt" in src_ls

      src_stat = self.fs.listdir_stats(src_dir)

      self.fs.mkdir(dst_dir)
      self.fs.rename_star(src_dir, dst_dir)

      dst_stat = self.fs.listdir_stats(dst_dir)

      src_names = set([stat.name for stat in src_stat])
      dst_names = set([stat.name for stat in dst_stat])
      assert src_names
      assert src_names == dst_names

  def test_rmtree(self):
    with pytest.raises(NotImplementedError):
      self.fs.rmtree("universe", skipTrash=False)

    directory = self.get_test_path("test_rmtree")
    with self.cleaning(directory):
      self.fs.mkdir(directory)
      nested_dir = join(directory, "nested_dir")
      self.fs.mkdir(nested_dir)
      file_path = join(nested_dir, "file")
      key = self.get_key(file_path)
      key.set_contents_from_string("Some content")

      self.fs.rmtree(directory, skipTrash=True)

      assert not self.fs.exists(file_path)
      assert not self.fs.exists(nested_dir)
      assert not self.fs.exists(directory)

  def test_listing_buckets(self):
    buckets = self.fs.listdir("s3a://")
    assert len(buckets) > 0

  def test_mkdir(self):
    dir_path = self.get_test_path("test_mkdir")
    assert not self.fs.exists(dir_path)

    self.fs.mkdir(dir_path)
    assert self.fs.exists(dir_path)

  def test_upload_file(self):
    with tempfile.NamedTemporaryFile() as local_file:
      # Make sure we can upload larger than the UPLOAD chunk size
      file_size = DEFAULT_WRITE_SIZE * 2
      local_file.write("0" * file_size)
      local_file.flush()

      dest_dir = self.get_test_path("test_upload")
      local_file = local_file.name
      dest_path = "%s/%s" % (dest_dir, os.path.basename(local_file))

      add_permission(self.user.username, "has_s3", permname="s3_access", appname="filebrowser")
      try:
        # Just upload the current python file
        resp = self.c.post("/filebrowser/upload/file?dest=%s" % dest_dir, dict(dest=dest_dir, hdfs_file=open(local_file)))
        response = json.loads(resp.content)
      finally:
        remove_from_group(self.user.username, "has_s3")

      assert 0 == response["status"], response
      self.fs.stats(dest_path)

      f = self.fs.open(dest_path)
      actual = f.read(file_size)
      expected = open(local_file).read()
      assert actual == expected, "files do not match: %s != %s" % (len(actual), len(expected))

  def test_check_access(self):
    dir_path = self.get_test_path("test_check_access")
    self.fs.mkdir(dir_path)

    assert self.fs.check_access(dir_path, permission="WRITE")
