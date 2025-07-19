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

from unittest.mock import MagicMock, patch

import pytest

from filebrowser.conf import ALLOW_FILE_EXTENSIONS, RESTRICT_FILE_EXTENSIONS
from filebrowser.utils import get_user_fs, is_file_upload_allowed


class TestIsFileUploadAllowed:
  def test_no_file_name(self):
    # Test with None
    is_allowed, error_msg = is_file_upload_allowed(None)
    assert is_allowed is True
    assert error_msg is None

    # Test with empty string
    is_allowed, error_msg = is_file_upload_allowed("")
    assert is_allowed is True
    assert error_msg is None

  def test_no_restrictions_configured(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing(None)
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)

    try:
      # All file types should be allowed
      test_files = ["document.pdf", "script.exe", "archive.zip", "data.csv", "image.png", "video.mp4"]

      for file_name in test_files:
        is_allowed, error_msg = is_file_upload_allowed(file_name)
        assert is_allowed is True, f"File '{file_name}' should be allowed when no restrictions are configured"
        assert error_msg is None
    finally:
      reset_allow()
      reset_restrict()

  def test_allow_list_with_dots(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".csv", ".txt", ".json"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)

    try:
      # Allowed files
      allowed_files = ["data.csv", "notes.txt", "config.json", "DATA.CSV", "NOTES.TXT"]
      for file_name in allowed_files:
        is_allowed, error_msg = is_file_upload_allowed(file_name)
        assert is_allowed is True, f"File '{file_name}' should be allowed"
        assert error_msg is None

      # Not allowed files
      not_allowed_files = ["script.exe", "archive.zip", "image.png"]
      for file_name in not_allowed_files:
        is_allowed, error_msg = is_file_upload_allowed(file_name)
        assert is_allowed is False, f"File '{file_name}' should not be allowed"
        assert error_msg is not None
        assert "is not permitted" in error_msg
        assert "Modify file extension settings" in error_msg
    finally:
      reset_allow()
      reset_restrict()

  def test_allow_list_without_dots(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing(["csv", "txt", "json"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing(None)

    try:
      # Should still work - extensions are normalized
      allowed_files = ["data.csv", "notes.txt", "config.json"]
      for file_name in allowed_files:
        is_allowed, error_msg = is_file_upload_allowed(file_name)
        assert is_allowed is True, f"File '{file_name}' should be allowed"
        assert error_msg is None
    finally:
      reset_allow()
      reset_restrict()

  def test_restrict_list_with_dots(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing(None)
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe", ".zip", ".rar"])

    try:
      # Restricted files
      restricted_files = ["malware.exe", "archive.zip", "compressed.rar", "MALWARE.EXE"]
      for file_name in restricted_files:
        is_allowed, error_msg = is_file_upload_allowed(file_name)
        assert is_allowed is False, f"File '{file_name}' should be restricted"
        assert error_msg is not None
        assert "is restricted" in error_msg
        assert "Update file extension restrictions" in error_msg

      # Allowed files
      allowed_files = ["document.pdf", "data.csv", "image.png"]
      for file_name in allowed_files:
        is_allowed, error_msg = is_file_upload_allowed(file_name)
        assert is_allowed is True, f"File '{file_name}' should be allowed"
        assert error_msg is None
    finally:
      reset_allow()
      reset_restrict()

  def test_restrict_list_without_dots(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing(None)
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing(["exe", "zip", "rar"])

    try:
      # Should still work - extensions are normalized
      restricted_files = ["malware.exe", "archive.zip", "compressed.rar"]
      for file_name in restricted_files:
        is_allowed, error_msg = is_file_upload_allowed(file_name)
        assert is_allowed is False, f"File '{file_name}' should be restricted"
        assert error_msg is not None
        assert "is restricted" in error_msg
    finally:
      reset_allow()
      reset_restrict()

  def test_both_allow_and_restrict_lists(self):
    # Allow list takes precedence - if file type is not in allow list, it's rejected
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".csv", ".txt", ".exe"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe", ".zip"])

    try:
      # File in allow list but also in restrict list - should check restrict list
      is_allowed, error_msg = is_file_upload_allowed("script.exe")
      assert is_allowed is False
      assert error_msg is not None
      assert "is restricted" in error_msg

      # File in allow list and not in restrict list - should be allowed
      is_allowed, error_msg = is_file_upload_allowed("data.csv")
      assert is_allowed is True
      assert error_msg is None

      # File not in allow list - should be rejected regardless of restrict list
      is_allowed, error_msg = is_file_upload_allowed("image.png")
      assert is_allowed is False
      assert error_msg is not None
      assert "is not permitted" in error_msg
    finally:
      reset_allow()
      reset_restrict()

  def test_case_insensitive_extensions(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".CSV", ".TXT"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".EXE", ".ZIP"])

    try:
      # Test allow list with different cases
      test_cases = [
        ("data.csv", True),
        ("data.CSV", True),
        ("data.CsV", True),
        ("notes.txt", True),
        ("notes.TXT", True),
        ("notes.TxT", True),
      ]

      for file_name, expected in test_cases:
        is_allowed, error_msg = is_file_upload_allowed(file_name)
        assert is_allowed is expected, f"File '{file_name}' case handling failed"

      # Reset for restrict list test
      reset_allow()
      reset_restrict()

      reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing(None)
      reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".EXE", ".ZIP"])

      # Test restrict list with different cases
      restricted_cases = [
        ("malware.exe", False),
        ("malware.EXE", False),
        ("malware.ExE", False),
        ("archive.zip", False),
        ("archive.ZIP", False),
        ("archive.ZiP", False),
      ]

      for file_name, expected in restricted_cases:
        is_allowed, error_msg = is_file_upload_allowed(file_name)
        assert is_allowed is expected, f"File '{file_name}' case handling failed"
        if not expected:
          assert error_msg is not None
          assert "is restricted" in error_msg
    finally:
      reset_allow()
      reset_restrict()

  def test_files_without_extensions(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".txt", ".csv"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe"])

    try:
      # File without extension with allow list - should not be in allow list
      is_allowed, error_msg = is_file_upload_allowed("README")
      assert is_allowed is False
      assert error_msg is not None
      assert "is not permitted" in error_msg

      # Reset for restrict list only test
      reset_allow()
      reset_restrict()

      reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing(None)
      reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe"])

      # File without extension with only restrict list - should be allowed
      is_allowed, error_msg = is_file_upload_allowed("README")
      assert is_allowed is True
      assert error_msg is None
    finally:
      reset_allow()
      reset_restrict()

  def test_files_with_multiple_dots(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".gz", ".txt"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe"])

    try:
      # Should use the last extension
      is_allowed, error_msg = is_file_upload_allowed("archive.tar.gz")
      assert is_allowed is True
      assert error_msg is None

      is_allowed, error_msg = is_file_upload_allowed("document.backup.txt")
      assert is_allowed is True
      assert error_msg is None

      is_allowed, error_msg = is_file_upload_allowed("file.backup.exe")
      assert is_allowed is False
      assert error_msg is not None
      assert "is not permitted" in error_msg
    finally:
      reset_allow()
      reset_restrict()

  def test_hidden_files(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".txt", ".conf"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe"])

    try:
      # Hidden file with extension
      is_allowed, error_msg = is_file_upload_allowed(".bashrc.txt")
      assert is_allowed is True
      assert error_msg is None

      # Hidden file without what looks like an extension
      is_allowed, error_msg = is_file_upload_allowed(".bashrc")
      assert is_allowed is False
      assert error_msg is not None
      assert "is not permitted" in error_msg
    finally:
      reset_allow()
      reset_restrict()

  def test_edge_cases(self):
    reset_allow = ALLOW_FILE_EXTENSIONS.set_for_testing([".txt"])
    reset_restrict = RESTRICT_FILE_EXTENSIONS.set_for_testing([".exe"])

    try:
      # File ending with dot
      is_allowed, error_msg = is_file_upload_allowed("file.")
      assert is_allowed is False
      assert error_msg is not None
      assert "is not permitted" in error_msg

      # Just a dot
      is_allowed, error_msg = is_file_upload_allowed(".")
      assert is_allowed is False
      assert error_msg is not None
      assert "is not permitted" in error_msg

      # Multiple consecutive dots
      is_allowed, error_msg = is_file_upload_allowed("file..txt")
      assert is_allowed is True
      assert error_msg is None
    finally:
      reset_allow()
      reset_restrict()


class TestGetUserFs:
  @patch("filebrowser.utils.fsmanager.get_filesystem")
  def test_get_user_fs_success(self, mock_get_filesystem):
    mock_fs = MagicMock()
    mock_get_filesystem.return_value = mock_fs

    result = get_user_fs("test_user")

    assert result == mock_fs
    mock_get_filesystem.assert_called_once_with("default")
    mock_fs.setuser.assert_called_once_with("test_user")

  @patch("filebrowser.utils.fsmanager.get_filesystem")
  def test_get_user_fs_empty_username(self, mock_get_filesystem):
    with pytest.raises(ValueError) as exc_info:
      get_user_fs("")

    assert str(exc_info.value) == "Username is required"
    mock_get_filesystem.assert_not_called()

  @patch("filebrowser.utils.fsmanager.get_filesystem")
  def test_get_user_fs_none_username(self, mock_get_filesystem):
    with pytest.raises(ValueError) as exc_info:
      get_user_fs(None)

    assert str(exc_info.value) == "Username is required"
    mock_get_filesystem.assert_not_called()

  @patch("filebrowser.utils.fsmanager.get_filesystem")
  def test_get_user_fs_various_usernames(self, mock_get_filesystem):
    mock_fs = MagicMock()
    mock_get_filesystem.return_value = mock_fs

    test_usernames = [
      "user1",
      "test-user",
      "user.name",
      "user_name",
      "user123",
      "user@domain.com",
      "user with spaces",  # Unusual but should work
      "user_with_unicode_ñáme",
      "用户名",
      "very_long_username_that_is_still_valid_123456789",
    ]

    for username in test_usernames:
      mock_get_filesystem.reset_mock()
      mock_fs.reset_mock()

      result = get_user_fs(username)

      assert result == mock_fs, f"Failed for username: {username}"
      mock_get_filesystem.assert_called_once_with("default")
      mock_fs.setuser.assert_called_once_with(username)
