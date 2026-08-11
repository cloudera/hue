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
from typing import Any, Dict

from django.core.paginator import EmptyPage, Paginator

from desktop.conf import TASK_SERVER_V2
from desktop.lib import i18n
from desktop.lib.fsmanager import get_filesystems
from desktop.lib.tasks.compress_files.compress_utils import compress_files_in_hdfs
from desktop.lib.tasks.extract_archive.extract_utils import extract_archive_in_hdfs
from filebrowser.conf import ENABLE_EXTRACT_UPLOADED_ARCHIVE
from filebrowser.schemas import (
  CheckExistsSchema,
  CompressFilesSchema,
  CopyOperationSchema,
  CreateDirectorySchema,
  CreateFileSchema,
  DeleteOperationSchema,
  ExtractArchiveSchema,
  GetFileContentsSchema,
  GetStatsSchema,
  GetTrashPathSchema,
  ListDirectorySchema,
  MoveOperationSchema,
  RenameSchema,
  SaveFileSchema,
  SetOwnershipSchema,
  SetPermissionsSchema,
  SetReplicationSchema,
  TrashRestoreSchema,
)
from filebrowser.utils import (
  atomic_save_file,
  calculate_permission_mode,
  get_filesystem_config,
  get_filesystem_home_directory,
  get_user_fs,
  is_destination_parent_of_source,
  massage_stats,
  parse_broker_url,
  read_contents,
)
from filebrowser.views import MAX_FILEEDITOR_SIZE
from useradmin.models import User

LOG = logging.getLogger()


def rename_file_or_directory(data: RenameSchema, username: str) -> Dict[str, Any]:
  """
  Rename a file or directory.

  Args:
    data: RenameSchema containing source and destination paths
    username: The username of the user performing the operation

  Returns:
    Dictionary with the result of the operation

  Raises:
    ValueError: If validation fails
    Exception: For other errors during rename
  """
  if not username:
    raise ValueError("Username is required and cannot be empty.")

  source_path = data.source_path
  destination_path = data.destination_path

  fs = get_user_fs(username)

  # Handle relative destination paths
  if "/" not in destination_path:
    source_dir = os.path.dirname(source_path)
    destination_path = fs.join(source_dir, destination_path)

  # Normalize destination path after potential modification
  destination_path_normalized = fs.normpath(destination_path)

  # Check if source exists
  if not fs.exists(source_path):
    raise ValueError(f"Source path does not exist: {source_path}")

  # Check if destination already exists
  if fs.exists(destination_path_normalized):
    raise ValueError(f"Destination path already exists: {destination_path_normalized}")

  LOG.info(f"User {username} is renaming {source_path} to {destination_path_normalized}")

  try:
    fs.rename(source_path, destination_path_normalized)
  except Exception as e:
    LOG.exception(f"Error during rename operation: {e}")
    raise Exception(f"Failed to rename file: {str(e)}")

  return {"message": f"Renamed '{source_path}' to '{destination_path_normalized}' successfully"}


def get_file_contents(data: GetFileContentsSchema, username: str) -> Dict[str, Any]:
  """
  Reads and decodes a portion of a file's contents.

  This function is designed to be agnostic of the caller and handles path
  normalization, validation, and content decoding. It is designed to be used by
  APIs, SDKs, or CLIs.

  Args:
    data: GetFileContentsSchema containing validation parameters
    username: The username of the user performing the operation

  Returns:
    Dictionary containing the file contents and metadata

  Raises:
    FileNotFoundError: If the path does not exist or is not a file
    ValueError: For invalid input parameters or if the file cannot be decoded
  """
  LOG.info(f"User '{username}' is reading contents from path: {data.path}")
  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  if not fs.isfile(data.path):
    # This check handles both non-existence and being a directory.
    raise FileNotFoundError(f"Path is not a file or does not exist: {data.path}")

  _, read_offset, actual_length, contents = read_contents(
    data.compression, data.path, fs, data.offset, data.length, read_until_newline=data.read_until_newline
  )

  mode = "binary"
  try:
    file_contents = contents.decode(data.encoding or i18n.get_site_encoding())
    mode = "text"
  except (UnicodeDecodeError, AttributeError):
    LOG.warning(f"Failed to decode contents from '{data.path}' with encoding '{data.encoding}'.")
    raise ValueError(f"Cannot decode file with '{data.encoding}' encoding. Please select a different encoding or download the file.")

  return {
    "contents": file_contents,
    "offset": read_offset,
    "length": actual_length,
    "end": read_offset + len(contents),
    "mode": mode,
  }


def create_file(data: CreateFileSchema, username: str) -> Dict[str, Any]:
  """
  Create a new file with comprehensive validation and error handling.

  This function is designed to be agnostic of the caller and handles path
  normalization, parent directory creation, file content initialization,
  and proper error handling. It is designed to be used by APIs, SDKs, or CLIs.

  Args:
    data: CreateFileSchema containing validated creation parameters
    username: The username of the user performing the operation

  Returns:
    Dictionary containing the creation result and file metadata

  Raises:
    ValueError: For invalid input parameters or validation failures
    FileExistsError: If file exists and overwrite is False
    RuntimeError: For filesystem or permission errors
  """
  LOG.info(f"User '{username}' is creating file at path: {data.path}")
  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  # Check if file already exists
  if fs.exists(data.path):
    if not data.overwrite:
      raise FileExistsError(f"File already exists: {data.path}")

    # Verify it's actually a file, not a directory
    if fs.isdir(data.path):
      raise ValueError(f"Cannot overwrite directory with file: {data.path}")

    LOG.info(f"Overwriting existing file at '{data.path}' for user '{username}'")

  file_data = None
  if data.initial_content is not None:
    try:
      file_data = data.initial_content.encode(data.encoding)
      LOG.debug(f"Creating file with initial content ({len(file_data)} bytes)")
    except UnicodeEncodeError as e:
      raise ValueError(f"Cannot encode initial content with '{data.encoding}' encoding: {e}")

  try:
    fs.create(data.path, overwrite=data.overwrite, data=file_data)

    LOG.info(f"File created successfully at '{data.path}' by user '{username}'")
    return {"message": f"File created successfully: {data.path}"}

  except Exception as e:
    LOG.exception(f"Unexpected error creating file '{data.path}' for user '{username}': {e}")
    raise RuntimeError(f"Failed to create file: {e}")


def save_file(data: SaveFileSchema, username: str) -> Dict[str, Any]:
  """
  Save/update file contents with comprehensive validation and error handling.

  This function is designed to be agnostic of the caller and handles path
  normalization, parent directory creation, content encoding validation,
  and proper error handling. It is designed to be used by APIs, SDKs, or CLIs.

  Args:
    data: SaveFileSchema containing validated save parameters
    username: The username of the user performing the operation

  Returns:
    Dictionary containing the save result and file metadata

  Raises:
    ValueError: For invalid input parameters or validation failures
    UnicodeEncodeError: If content cannot be encoded with specified encoding
    RuntimeError: For filesystem or permission errors
  """
  LOG.info(f"User '{username}' is saving file at path: {data.path}")
  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  file_exists = fs.exists(data.path)
  if file_exists:
    if fs.isdir(data.path):
      raise ValueError(f"Cannot save content to a directory: {data.path}")

    # Check if file is too large to edit
    current_stats = fs.stats(data.path)
    file_size = current_stats.get("size", 0)

    if file_size > MAX_FILEEDITOR_SIZE:
      LOG.error(f"Attempting to save large file '{data.path}' (size: {file_size} bytes)")
      raise ValueError(
        f"File '{data.path}' is too large to edit. File size: {file_size} bytes, maximum allowed: {MAX_FILEEDITOR_SIZE} bytes"
      )

    LOG.debug(f"Updating existing file at '{data.path}' for user '{username}'")

  try:
    encoded_data = data.contents.encode(data.encoding)
    content_size = len(encoded_data)
    LOG.debug(f"Encoded file content: {content_size} bytes using {data.encoding} encoding")
  except UnicodeEncodeError as e:
    LOG.error(f"Failed to encode content for '{data.path}' with encoding '{data.encoding}': {e}")
    raise UnicodeEncodeError(e.encoding, e.object, e.start, e.end, f"Content cannot be encoded with '{data.encoding}' encoding")

  try:
    if file_exists:
      atomic_save_file(fs, data.path, encoded_data)
    else:
      fs.create(data.path, overwrite=False, data=encoded_data)

    LOG.info(f"File saved successfully at '{data.path}' by user '{username}' (size: {content_size} bytes)")
    return {"message": f"File saved successfully: {data.path}"}

  except Exception as e:
    LOG.exception(f"Unexpected error saving file '{data.path}' for user '{username}': {e}")
    raise RuntimeError(f"Failed to save file: {e}")


def list_directory(data: ListDirectorySchema, username: str) -> Dict[str, Any]:
  """
  List directory contents with comprehensive validation and error handling.

  This function is designed to be agnostic of the caller and handles path
  normalization, permission validation, filtering, sorting, and pagination.
  It is designed to be used by APIs, SDKs, or CLIs.

  Args:
    data: ListDirectorySchema containing validated listing parameters
    username: The username of the user performing the operation

  Returns:
    Dictionary containing directory listing and pagination metadata

  Raises:
    ValueError: For invalid input parameters or validation failures
    FileNotFoundError: If the directory doesn't exist
    PermissionError: If user lacks permission to list the directory
    RuntimeError: For filesystem or other system errors
  """
  LOG.info(f"User '{username}' is listing directory: {data.path}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  # Verify the path exists and is a directory
  if not fs.exists(data.path):
    raise FileNotFoundError(f"Directory does not exist: {data.path}")

  if not fs.isdir(data.path):
    raise ValueError(f"Path is not a directory: {data.path}")

  # Get directory listing with proper error handling
  try:
    all_stats = fs.listdir_stats(data.path)
  except Exception as e:
    LOG.error(f"Error listing directory '{data.path}': {e}")

    # Handle specific cloud storage exceptions
    exception_name = e.__class__.__name__
    if exception_name in ["S3ListAllBucketsException", "GSListAllBucketsException"]:
      raise PermissionError(f"Bucket listing is not allowed: {e}")
    elif exception_name == "WebHdfsException" and hasattr(e, "code"):
      if e.code == 403:
        raise PermissionError(f"Permission denied accessing directory: {data.path}")
      elif e.code == 404:
        raise FileNotFoundError(f"Directory not found: {data.path}")

    raise RuntimeError(f"Failed to list directory: {e}")

  LOG.debug(f"Retrieved {len(all_stats)} items from directory '{data.path}'")

  try:
    # Apply filename filter
    if data.filter:
      all_stats = [stat for stat in all_stats if data.filter.lower() in stat.name.lower()]
      LOG.debug(f"After filter '{data.filter}': {len(all_stats)} items")

    # Sort the results
    numeric_fields = {"size", "atime", "mtime"}

    def sorting_key(item):
      """Generate sorting key handling None values appropriately."""
      try:
        value = getattr(item, data.sortby, None)
        if data.sortby in numeric_fields:
          return 0 if value is None else value
        else:
          return "" if value is None else str(value).lower()
      except Exception:
        return 0 if data.sortby in numeric_fields else ""

    try:
      all_stats = sorted(all_stats, key=sorting_key, reverse=data.descending)
    except Exception as e:
      LOG.warning(f"Error during sorting with field '{data.sortby}': {e}")
      # Fallback to name sorting
      all_stats = sorted(all_stats, key=lambda x: getattr(x, "name", "").lower())

    # Pagination
    paginator = Paginator(all_stats, data.pagesize, allow_empty_first_page=True)
    try:
      page = paginator.page(data.pagenum)
    except EmptyPage:
      raise ValueError(f"Page {data.pagenum} does not exist (total pages: {paginator.num_pages})")

    # Format results with optional detailed stats
    items = []
    for stat in page.object_list:
      stat_dict = massage_stats(fs, stat)
      items.append(stat_dict)

    result = {
      "items": items,
      "page": {
        "page_number": page.number,
        "page_size": paginator.per_page,
        "total_pages": paginator.num_pages,
        "total_size": paginator.count,
        "has_next": page.has_next(),
        "has_previous": page.has_previous(),
      },
    }

    LOG.info(f"Directory listing completed for '{data.path}' by user '{username}': {paginator.count} items")
    return result

  except Exception as e:
    LOG.exception(f"Unexpected error listing directory '{data.path}' for user '{username}': {e}")
    raise RuntimeError(f"Failed to list directory: {e}")


def create_directory(data: CreateDirectorySchema, username: str) -> Dict[str, Any]:
  """
  Create a new directory with comprehensive validation and error handling.

  This function is designed to be agnostic of the caller and handles path
  normalization, parent directory creation, permission setting, and proper
  error handling. It is designed to be used by APIs, SDKs, or CLIs.

  Args:
    data: CreateDirectorySchema containing validated creation parameters
    username: The username of the user performing the operation

  Returns:
    Dictionary containing the creation result and directory metadata

  Raises:
    ValueError: For invalid input parameters or validation failures
    FileExistsError: If directory already exists
    PermissionError: If user lacks permission to create the directory
    RuntimeError: For filesystem or other system errors
  """
  LOG.info(f"User '{username}' is creating directory at path: {data.path}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  # Check if directory already exists
  if fs.exists(data.path):
    if fs.isdir(data.path):
      raise FileExistsError(f"Directory already exists: {data.path}")
    else:
      LOG.warning(f"File exists at path: {data.path} but still attempting to create directory")

  try:
    fs.mkdir(data.path)
    LOG.debug(f"Created directory with default permissions: {data.path}")
  except Exception as e:
    LOG.exception(f"Unexpected error creating directory '{data.path}' for user '{username}': {e}")

    # Check for specific error types
    if "Permission denied" in str(e) or "Access denied" in str(e):
      raise PermissionError(f"Permission denied creating directory: {data.path}")

    raise RuntimeError(f"Failed to create directory: {str(e)}")


def get_path_stats(data: GetStatsSchema, username: str) -> Dict[str, Any]:
  """Get stats for a path."""
  LOG.info(f"User '{username}' is getting stats for path: {data.path}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  if not fs.exists(data.path):
    raise ValueError(f"Path does not exist: {data.path}")

  stats = fs.stats(data.path)
  result = massage_stats(fs, stats)

  # Include content summary if requested
  if data.include_content_summary:
    if hasattr(fs, "get_content_summary") and callable(getattr(fs, "get_content_summary")):
      try:
        content_summary = fs.get_content_summary(data.path)

        replication_factor = stats.get("replication")
        content_summary.summary.update({"replication": replication_factor})

        result["content_summary"] = content_summary.summary
      except Exception as e:
        LOG.warning(f"Failed to get content summary: {e}")
        result["content_summary"] = None
    else:
      LOG.debug(f"Filesystem {type(fs).__name__} does not support get_content_summary method")
      result["content_summary"] = None

  return result


def check_path_exists(data: CheckExistsSchema, username: str) -> Dict[str, Any]:
  """Check if multiple paths exist."""
  LOG.info(f"User '{username}' is checking if paths exist: {data.paths}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)
  results = {"success": [], "errors": {}}

  for path in data.paths:
    try:
      exists = fs.exists(path)
      results["success"].append({"path": path, "exists": exists})

    except Exception as e:
      results["errors"][path] = str(e)

  return results


def copy_paths(data: CopyOperationSchema, username: str) -> Dict[str, Any]:
  """Copy files/directories to destination."""
  LOG.info(f"User '{username}' is copying paths: {data.source_paths} to destination: {data.destination_path}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  if not fs.isdir(data.destination_path):
    raise ValueError("Destination path must be a directory.")

  results = {"success": [], "errors": {}}

  for source_path in data.source_paths:
    try:
      _validate_copy_and_move_actions(fs, source_path, data.destination_path)

      if source_path.startswith("ofs://"):
        ofs_skip_files = fs.copy(source_path, data.destination_path, recursive=True, owner=username)
        if ofs_skip_files:
          results["errors"][source_path] = f"Some files skipped: {ofs_skip_files}"
        else:
          results["success"].append(source_path)
      else:
        fs.copy(source_path, data.destination_path, recursive=True, owner=username)
        results["success"].append(source_path)

    except Exception as e:
      results["errors"][source_path] = str(e)

  return results


def _validate_copy_and_move_actions(fs: Any, source_path: str, destination_path: str) -> None:
  """Validate the input parameters for copy and move operations for different scenarios."""

  if not fs.exists(source_path):
    raise ValueError("Source does not exist")

  if fs.normpath(source_path) == fs.normpath(destination_path):
    raise ValueError("Source and destination paths must be different.")

  if is_destination_parent_of_source(fs, source_path, destination_path):
    raise ValueError("Destination cannot be the parent directory of source")

  dest_full_path = fs.join(destination_path, os.path.basename(source_path))
  if fs.exists(dest_full_path):
    raise ValueError("Already exists at destination")


def move_paths(data: MoveOperationSchema, username: str) -> Dict[str, Any]:
  """Move files/directories to destination."""
  LOG.info(f"User '{username}' is moving paths: {data.source_paths} to destination: {data.destination_path}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  if not fs.isdir(data.destination_path):
    raise ValueError("Destination path must be a directory.")

  results = {"success": [], "errors": {}}

  for source_path in data.source_paths:
    try:
      _validate_copy_and_move_actions(fs, source_path, data.destination_path)

      fs.rename(source_path, data.destination_path)
      results["success"].append(source_path)

    except Exception as e:
      results["errors"][source_path] = str(e)

  return results


def delete_paths(data: DeleteOperationSchema, username: str) -> Dict[str, Any]:
  """Delete files/directories."""
  LOG.info(f"User '{username}' is deleting paths: {data.paths}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)
  results = {"success": [], "errors": {}}

  for path in data.paths:
    try:
      if not fs.exists(path):
        raise ValueError("Path does not exist")

      fs.rmtree(path, skip_trash=data.skip_trash)
      results["success"].append(path)

    except Exception as e:
      results["errors"][path] = str(e)

  return results


def restore_from_trash(data: TrashRestoreSchema, username: str) -> Dict[str, Any]:
  """Restore files/directories from trash."""
  LOG.info(f"User '{username}' is restoring paths from trash: {data.paths}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)
  results = {"success": [], "errors": {}}

  for path in data.paths:
    try:
      fs.restore(path)
      results["success"].append(path)

    except Exception as e:
      results["errors"][path] = str(e)

  return results


def set_permissions(data: SetPermissionsSchema, username: str) -> Dict[str, Any]:
  """Set file/directory permissions."""
  LOG.info(f"User '{username}' is setting permissions for paths: {data.paths}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)
  results = {"success": [], "errors": {}}

  mode = calculate_permission_mode(
    user_read=data.user_read,
    user_write=data.user_write,
    user_execute=data.user_execute,
    group_read=data.group_read,
    group_write=data.group_write,
    group_execute=data.group_execute,
    other_read=data.other_read,
    other_write=data.other_write,
    other_execute=data.other_execute,
    sticky=data.sticky,
  )

  for path in data.paths:
    try:
      if not fs.exists(path):
        raise ValueError("Path does not exist")

      fs.chmod(path, mode, recursive=data.recursive)
      results["success"].append(path)

    except Exception as e:
      results["errors"][path] = str(e)

  return results


def set_ownership(data: SetOwnershipSchema, username: str) -> Dict[str, Any]:
  """Set file/directory ownership."""
  LOG.info(f"User '{username}' is setting ownership for paths: {data.paths}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)
  results = {"success": [], "errors": {}}

  for path in data.paths:
    try:
      if not fs.exists(path):
        raise ValueError("Path does not exist")

      fs.chown(path, data.user, data.group, recursive=data.recursive)
      results["success"].append(path)

    except Exception as e:
      results["errors"][path] = str(e)

  return results


def set_replication(data: SetReplicationSchema, username: str) -> Dict[str, Any]:
  """Set replication factor for a path."""
  LOG.info(f"User '{username}' is setting replication factor for path: {data.path}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  if not fs.exists(data.path):
    raise ValueError(f"Path does not exist: {data.path}")

  error_message = f"Failed to set the replication factor for path: {data.path}"
  try:
    result = fs.set_replication(data.path, data.replication_factor)
  except Exception as e:
    LOG.error(f"{error_message}: {e}")
    raise Exception(error_message)

  if not result:
    raise ValueError(error_message)
  else:
    return {"message": f"Replication factor {data.replication_factor} set successfully"}


def compress_files(data: CompressFilesSchema, username: str) -> Dict[str, Any]:
  """Compress files into an archive."""
  LOG.info(f"User '{username}' is compressing files: {data.file_names} into archive: {data.archive_name}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  if not ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
    raise ValueError("Compress files operation is disabled by configuration.")

  fs = get_user_fs(username)
  upload_path = fs.netnormpath(data.upload_path)

  # Create a mock request object for the legacy function
  class MockRequest:
    def __init__(self, user, filesystem):
      self.user = user
      self.fs = filesystem

  mock_request = MockRequest(User.objects.get(username=username), fs)

  try:
    response = compress_files_in_hdfs(mock_request, data.file_names, upload_path, data.archive_name)
    return response
  except Exception as e:
    raise ValueError(f"Failed to compress files: {str(e)}")


def extract_archive(data: ExtractArchiveSchema, username: str) -> Dict[str, Any]:
  """Extract an archive."""
  LOG.info(f"User '{username}' is extracting archive: {data.archive_name}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  if not ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
    raise ValueError("Extract archive operation is disabled by configuration.")

  fs = get_user_fs(username)
  upload_path = fs.netnormpath(data.upload_path)

  # Create a mock request object for the legacy function
  class MockRequest:
    def __init__(self, user, filesystem):
      self.user = user
      self.fs = filesystem

  mock_request = MockRequest(User.objects.get(username=username), fs)

  try:
    response = extract_archive_in_hdfs(mock_request, upload_path, data.archive_name)
    return response
  except Exception as e:
    raise ValueError(f"Failed to extract archive: {str(e)}")


def get_trash_path(data: GetTrashPathSchema, username: str) -> Dict[str, Any]:
  """Get trash path for a given path."""
  LOG.info(f"User '{username}' is getting trash path for path: {data.path}")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  try:
    trash_path = fs.trash_path(data.path)
    user_home_trash_path = fs.join(fs.current_trash_path(trash_path), User.objects.get(username=username).get_home_directory().lstrip("/"))

    if fs.isdir(user_home_trash_path):
      result_path = user_home_trash_path
    elif fs.isdir(trash_path):
      result_path = trash_path
    else:
      result_path = None

    return {"trash_path": result_path}
  except Exception as e:
    LOG.exception(f"Error getting trash path for path: {data.path}: {e}")
    raise Exception("Failed to get trash path")


def purge_trash(username: str) -> Dict[str, Any]:
  """Purge all trash for the user."""
  LOG.info(f"User '{username}' is purging all trash")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  fs = get_user_fs(username)

  try:
    fs.purge_trash()
    return {"message": "Trash purged successfully"}
  except Exception as e:
    LOG.exception(f"Error purging trash for user: {username}: {e}")
    raise Exception("Failed to purge trash")


def get_available_space_for_upload(username: str) -> Dict[str, Any]:
  """Get available space for file uploads."""
  LOG.info(f"User '{username}' is getting available space for file uploads")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    upload_available_space = redis_client.get("upload_available_space")
    if upload_available_space is None:
      raise ValueError("upload_available_space key is not set in Redis.")

    return {"upload_available_space": int(upload_available_space)}
  finally:
    redis_client.close()


def get_all_filesystems(username: str) -> Dict[str, Any]:
  """
  Get all configured filesystems with their home directories and configurations.

  Args:
    username: Username of the requesting user

  Returns:
    Dict containing list of filesystems with their details
  """
  LOG.info(f"User '{username}' is getting information about all configured filesystems")

  if not username:
    raise ValueError("Username is required and cannot be empty.")

  user = User.objects.get(username=username)
  available_filesystems = get_filesystems(user)

  result = {"filesystems": [], "errors": {}}
  for fs_name in available_filesystems:
    try:
      user_home_dir = get_filesystem_home_directory(fs_name, user)
      config = get_filesystem_config(username)

      filesystem_info = {"name": fs_name, "user_home_directory": user_home_dir, "config": config}
      result["filesystems"].append(filesystem_info)

    except Exception as fs_error:
      result["errors"][fs_name] = str(fs_error)

  LOG.info(f"Successfully retrieved information about {len(result['filesystems'])} filesystems for user '{username}'")
  return result
