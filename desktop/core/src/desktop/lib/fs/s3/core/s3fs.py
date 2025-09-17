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

import logging
import os
import time
from typing import Any, List, Optional, Union

from botocore.exceptions import ClientError

from desktop.conf import PERMISSION_ACTION_S3
from desktop.lib.fs.s3.clients.factory import S3ClientFactory
from desktop.lib.fs.s3.constants import DEFAULT_CHUNK_SIZE, S3_DELIMITER
from desktop.lib.fs.s3.core.file import S3File
from desktop.lib.fs.s3.core.path import S3Path
from desktop.lib.fs.s3.core.stat import S3Stat

LOG = logging.getLogger()


def make_s3_client(connector_id: str, user: str) -> "S3FileSystem":
  return S3FileSystem(connector_id, user)


class S3FileSystem:
  """
  Simplified S3FileSystem implementation using boto3.
  Takes connector_id and user, extracts bucket from paths during operations.
  """

  def __init__(self, connector_id: str, user: str):
    """
    Initialize S3FileSystem for a specific connector.

    Args:
      connector_id: ID of the S3 connector to use
      user: Username for operations
    """
    self.connector_id = connector_id
    self.user = user

    # Backward compatibility attributes
    self.is_sentry_managed = lambda path: False  # S3 doesn't use Sentry
    self.superuser = None  # No superuser concept in S3
    self.supergroup = None  # No supergroup concept in S3
    self.expiration = None  # No expiration for S3
    self._filebrowser_action = PERMISSION_ACTION_S3  # S3 uses filebrowser_action

    # Initialize client
    self._initialize_client()

  def _initialize_client(self) -> None:
    """Initialize the S3 client using connector configuration"""
    try:
      # Create client using factory
      self.client = S3ClientFactory.get_client_for_connector(self.connector_id, self.user)

      # Get boto3 clients for direct use
      self.s3_client = self.client.s3_client
      self.s3_resource = self.client.s3_resource

    except Exception as e:
      LOG.error(f"Failed to initialize S3 client: {e}")
      raise

  def _get_bucket(self, bucket_name: str, validate: bool = True):
    """Get bucket by name"""
    try:
      bucket = self.s3_resource.Bucket(bucket_name)
      if validate:
        # Force validation of bucket
        self.s3_client.head_bucket(Bucket=bucket_name)
      return bucket
    except ClientError as e:
      error_code = e.response["Error"]["Code"]
      if error_code == "404":
        raise FileNotFoundError(f"Bucket not found: {bucket_name}")
      elif error_code == "403":
        raise PermissionError(f"Access denied to bucket: {bucket_name}")
      raise

  def _create_bucket(self, bucket_name: str) -> Any:
    """Create bucket in the correct region"""
    region = self.client.get_region(bucket_name)
    kwargs = {}

    if region and region != "us-east-1":
      kwargs["CreateBucketConfiguration"] = {"LocationConstraint": region}

    return self.s3_client.create_bucket(Bucket=bucket_name, **kwargs)

  def _delete_bucket(self, bucket_name: str) -> None:
    """Delete bucket and all its contents"""
    try:
      bucket = self._get_bucket(bucket_name)

      # Delete objects in batches
      paginator = self.s3_client.get_paginator("list_objects_v2")
      for page in paginator.paginate(Bucket=bucket_name):
        objects_to_delete = [{"Key": obj["Key"]} for obj in page.get("Contents", [])]
        if objects_to_delete:
          self.s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": objects_to_delete})

      # Delete the empty bucket
      bucket.delete()

    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to delete bucket: {bucket_name}")
      raise

  def _get_object(self, path: Union[str, S3Path], validate: bool = True):
    """Get object by path"""
    if isinstance(path, str):
      path = S3Path.from_path(path)

    try:
      obj = self.s3_resource.Object(path.bucket, path.key)
      if validate:
        obj.load()
      return obj
    except ClientError as e:
      error_code = e.response["Error"]["Code"]
      if error_code == "404":
        raise FileNotFoundError(f"Object not found: {path}")
      elif error_code == "403":
        raise PermissionError(f"Access denied to object: {path}")
      raise

  def open(self, path: Union[str, S3Path], mode: str = "rb") -> S3File:
    """Open file for reading or writing"""
    return S3File(self, path, mode)

  def read(self, path: Union[str, S3Path], offset: int = 0, length: int = -1) -> bytes:
    """Read file contents"""
    with self.open(path, "rb") as f:
      f.seek(offset)
      return f.read(length)

  def create(self, path: Union[str, S3Path], overwrite: bool = False, data: Optional[Union[str, bytes]] = None) -> None:
    """
    Create a new file with optional initial content.

    Args:
      path: S3 path for new file
      overwrite: If True, overwrite existing file. If False, raise error if file exists
      data: Optional initial content (string or bytes)

    Raises:
      FileExistsError: If file exists and overwrite=False
      ClientError: For S3 API errors
    """
    if isinstance(path, str):
      path = S3Path.from_path(path)

    # Check if file exists
    if not overwrite and self.exists(path):
      raise FileExistsError(f"File already exists: {path}")

    # Convert string data to bytes if needed
    if isinstance(data, str):
      data = data.encode("utf-8")
    elif data is None:
      data = b""

    try:
      self.s3_client.put_object(Bucket=path.bucket, Key=path.key, Body=data)
    except ClientError as e:
      error_code = e.response["Error"]["Code"]
      if error_code == "NoSuchBucket":
        raise FileNotFoundError(f"Bucket does not exist: {path.bucket}")
      elif error_code == "AccessDenied":
        raise PermissionError(f"Access denied creating file: {path}")
      raise

  def exists(self, path: Union[str, S3Path]) -> bool:
    """Check if path exists"""
    try:
      self.stats(path)
      return True
    except (FileNotFoundError, PermissionError):
      return False

  def stats(self, path: Union[str, S3Path]) -> S3Stat:
    """Get path stats"""
    if isinstance(path, str):
      path = S3Path.from_path(path)

    if path.is_root():
      return S3Stat.for_root()

    try:
      if path.is_bucket():
        bucket = self._get_bucket(path.bucket)
        return S3Stat.from_bucket(bucket)
      else:
        obj = self._get_object(path)
        return S3Stat.from_object(obj)
    except FileNotFoundError:
      # Check if it's a prefix (directory)
      try:
        # For directory check, append '/' to avoid matching files that start with same prefix
        directory_prefix = path.key.rstrip("/") + "/"
        response = self.s3_client.list_objects_v2(Bucket=path.bucket, Prefix=directory_prefix, Delimiter=S3_DELIMITER, MaxKeys=1)
        if response.get("CommonPrefixes") or response.get("Contents"):
          return S3Stat.for_directory(path)
        raise FileNotFoundError(f"Path not found: {path}")
      except ClientError as e:
        if e.response["Error"]["Code"] == "403":
          raise PermissionError(f"Access denied to path: {path}")
        raise

  def isfile(self, path: Union[str, S3Path]) -> bool:
    """Check if path is a file"""
    try:
      stats = self.stats(path)
      return not stats.is_dir
    except FileNotFoundError:
      return False

  def isdir(self, path: Union[str, S3Path]) -> bool:
    """Check if path is a directory"""
    try:
      stats = self.stats(path)
      return stats.is_dir
    except FileNotFoundError:
      return False

  def listdir_stats(self, path: Union[str, S3Path], glob_pattern: Optional[str] = None) -> List[S3Stat]:
    """List directory with stats"""
    if isinstance(path, str):
      path = S3Path.from_path(path)

    if path.is_root():
      # List buckets
      buckets = self.s3_client.list_buckets()["Buckets"]
      return [S3Stat.from_bucket(self.s3_resource.Bucket(b["Name"])) for b in buckets]

    # List objects with prefix
    prefix = path.key if path.key else ""
    if prefix and not prefix.endswith(S3_DELIMITER):
      prefix += S3_DELIMITER

    paginator = self.s3_client.get_paginator("list_objects_v2")

    stats = []
    try:
      for page in paginator.paginate(Bucket=path.bucket, Prefix=prefix, Delimiter=S3_DELIMITER):
        # Add common prefixes (directories)
        for prefix_dict in page.get("CommonPrefixes", []):
          prefix_path = S3Path(bucket=path.bucket, key=prefix_dict["Prefix"])
          stats.append(S3Stat.for_directory(prefix_path))

        # Add objects (files)
        for obj_dict in page.get("Contents", []):
          if obj_dict["Key"] == prefix:
            continue  # Skip current directory marker
          obj = self.s3_resource.Object(path.bucket, obj_dict["Key"])
          stats.append(S3Stat.from_object(obj))

    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to path: {path}")
      raise

    return stats

  def listdir(self, path: Union[str, S3Path], glob_pattern: Optional[str] = None) -> List[str]:
    """List directory contents"""
    stats = self.listdir_stats(path, glob_pattern)
    return [stat.name for stat in stats]

  def mkdir(self, path: Union[str, S3Path]) -> None:
    """Create directory (empty object with trailing slash)"""
    if isinstance(path, str):
      path = S3Path.from_path(path)

    if path.is_root():
      raise ValueError("Cannot create root directory")

    try:
      if path.is_bucket():
        self._create_bucket(path.bucket)
      else:
        # Create directory marker
        key = path.key.rstrip("/") + "/"
        self.s3_client.put_object(Bucket=path.bucket, Key=key, Body=b"")
    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to create: {path}")
      raise

  def remove(self, path: Union[str, S3Path], skip_trash: bool = True) -> None:
    """Remove file or empty directory"""
    if not skip_trash:
      raise NotImplementedError("Trash not supported for S3")

    if isinstance(path, str):
      path = S3Path.from_path(path)

    try:
      if path.is_bucket():
        self._delete_bucket(path.bucket)
      else:
        # Delete object
        self.s3_client.delete_object(Bucket=path.bucket, Key=path.key)
    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to delete: {path}")
      raise

  def rmtree(self, path: Union[str, S3Path], skip_trash: bool = True) -> None:
    """Remove directory and contents recursively"""
    if not skip_trash:
      raise NotImplementedError("Trash not supported for S3")

    if isinstance(path, str):
      path = S3Path.from_path(path)

    try:
      if path.is_bucket():
        self._delete_bucket(path.bucket)
      elif self.isfile(path):
        self.remove(path, skip_trash=skip_trash)  # Delete file in rmtree for backward compatibility
      else:
        # Get prefix for directory
        prefix = path.key
        if not prefix.endswith("/"):
          prefix += "/"

        # Delete objects in batches
        paginator = self.s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=path.bucket, Prefix=prefix):
          objects_to_delete = [{"Key": obj["Key"]} for obj in page.get("Contents", [])]
          if objects_to_delete:
            self.s3_client.delete_objects(Bucket=path.bucket, Delete={"Objects": objects_to_delete})

    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to delete: {path}")
      raise

  def copy(self, src: Union[str, S3Path], dst: Union[str, S3Path], recursive: bool = False, *args, **kwargs) -> None:
    """Copy file or directory"""
    if isinstance(src, str):
      src = S3Path.from_path(src)
    if isinstance(dst, str):
      dst = S3Path.from_path(dst)

    # Validate source exists
    if not self.exists(src):
      raise FileNotFoundError(f"Source does not exist: {src}")

    src_is_dir = self.isdir(src)

    # Check if we can copy directory
    if src_is_dir and not recursive:
      raise IsADirectoryError(f"Source is a directory (use recursive=True): {src}")

    try:
      if not src_is_dir:
        # Handle file-to-directory copy case
        if self.exists(dst) and self.isdir(dst):
          src_filename = src.name()
          dst = dst.join(src_filename)
          LOG.debug(f"File-to-directory copy: appending filename to destination → {dst}")

        # Copy single file
        self._copy_file(src, dst)
      else:
        # Handle directory-to-directory copy case
        if self.exists(dst) and self.isdir(dst):
          src_dirname = src.name()
          dst = dst.join(src_dirname)
          LOG.debug(f"Directory-to-directory copy: appending source name to destination → {dst}")

        # Copy directory recursively
        self._copy_directory(src, dst)

    except ClientError as e:
      error_code = e.response["Error"]["Code"]
      if error_code == "403":
        raise PermissionError(f"Access denied for copy operation: {src} → {dst}")
      elif error_code == "NoSuchBucket":
        raise FileNotFoundError(f"Destination bucket does not exist: {dst.bucket}")
      elif error_code == "NoSuchKey":
        raise FileNotFoundError(f"Source not found: {src}")
      else:
        LOG.error(f"S3 copy operation failed: {error_code} - {e.response['Error'].get('Message', str(e))}")
        raise

  def _copy_file(self, src: S3Path, dst: S3Path) -> None:
    """Copy a single file using boto3 copy_object API"""
    copy_source = {"Bucket": src.bucket, "Key": src.key}

    LOG.debug(f"Copying file: {src} → {dst}")

    self.s3_client.copy_object(CopySource=copy_source, Bucket=dst.bucket, Key=dst.key)

  def _copy_directory(self, src: S3Path, dst: S3Path) -> None:
    """Copy directory recursively using boto3"""
    src_prefix = src.key.rstrip("/") + "/" if src.key else ""
    dst_prefix = dst.key.rstrip("/") + "/" if dst.key else ""

    LOG.debug(f"Copying directory: {src} → {dst} (src_prefix='{src_prefix}', dst_prefix='{dst_prefix}')")

    copied_files = 0
    paginator = self.s3_client.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=src.bucket, Prefix=src_prefix):
      for obj in page.get("Contents", []):
        src_key = obj["Key"]

        # Calculate destination key by replacing src_prefix with dst_prefix
        relative_key = src_key[len(src_prefix) :]
        dst_key = dst_prefix + relative_key

        # Copy each file
        copy_source = {"Bucket": src.bucket, "Key": src_key}
        self.s3_client.copy_object(CopySource=copy_source, Bucket=dst.bucket, Key=dst_key)

        copied_files += 1

    LOG.debug(f"Directory copy completed: {copied_files} files copied")

  def rename(self, old: Union[str, S3Path], new: Union[str, S3Path]) -> None:
    """Rename/move file or directory"""
    self.copy(old, new, recursive=True)
    self.rmtree(old)

  # Deprecated
  def upload(self, file, path, *args, **kwargs):
    pass  # upload is handled by S3ConnectorUploadHandler

  def create_home_dir(self, home_path: Optional[str] = None) -> None:
    """
    Create home directory for the user with smart path resolution.

    Args:
      home_path: Optional explicit home path, if not provided will be determined from config

    Raises:
      PermissionError: If user doesn't have permission to create directory
      IOError: If directory creation fails
    """
    try:
      # Get home directory path using smart defaults
      if not home_path:
        home_path = self._get_smart_home_directory()

      # Create directory if it doesn't exist
      if not self.exists(home_path):
        LOG.info(f"Creating home directory at: {home_path}")
        self.mkdir(home_path)

    except Exception as e:
      LOG.error(f"Failed to create home directory at {home_path}: {e}")
      raise IOError(f"Failed to create home directory: {e}")

  def _get_smart_home_directory(self) -> str:
    """
    Get smart home directory using connector bucket configuration.

    Logic:
    - Single bucket configured: Use that bucket's home path
    - Multiple buckets: Use generic s3a://
    - No buckets: Use generic s3a://
    """
    from desktop.lib.fs.s3.conf_utils import get_default_bucket_home_path

    return get_default_bucket_home_path(self.connector_id, self.user)

  # Backward compatibility methods

  def filebrowser_action(self):
    return self._filebrowser_action

  def setuser(self, user):
    self.user = user

  def get_upload_chuck_size(self):
    return DEFAULT_CHUNK_SIZE

  def get_upload_handler(self, destination_path, overwrite):
    # TODO: Implement upload flow for new S3 filesystem
    return None

  def normpath(self, path: str) -> str:
    """
    Normalize S3 path.
    Converts 's3://' to 's3a://' and handles path components.
    """
    if path.startswith("s3://"):
      path = "s3a://" + path[5:]
    s3path = S3Path.from_path(path)
    return str(s3path)

  def netnormpath(self, path: str) -> str:
    """
    Network normalize path - same as normpath for S3.
    """
    return self.normpath(path)

  def parent_path(self, path: str) -> str:
    """Get parent path"""
    s3path = S3Path.from_path(path)
    return str(s3path.parent())

  def join(self, first: str, *comp_list: str) -> str:
    """Join path components"""
    s3path = S3Path.from_path(first)
    return str(s3path.join(*comp_list))

  def isroot(self, path: str) -> bool:
    """Check if path is root"""
    s3path = S3Path.from_path(path)
    return s3path.is_root()

  def restore(self, *args, **kwargs):
    raise NotImplementedError("restore is not implemented for S3")

  def chmod(self, path: Union[str, S3Path], mode: int) -> None:
    """Change file mode"""
    raise NotImplementedError("chmod is not implemented for S3")

  def chown(self, path: Union[str, S3Path], user: str, group: str, *args, **kwargs) -> None:
    """Change file owner"""
    raise NotImplementedError("chown is not implemented for S3")

  def copyfile(self, src: Union[str, S3Path], dst: Union[str, S3Path], *args, **kwargs) -> None:
    """Copy single file (no recursion)"""
    if isinstance(src, str):
      src = S3Path.from_path(src)
    if isinstance(dst, str):
      dst = S3Path.from_path(dst)

    # Validate source is a file
    if not self.exists(src):
      raise FileNotFoundError(f"Source file does not exist: {src}")
    if self.isdir(src):
      raise IsADirectoryError(f"Source is a directory, use copy() with recursive=True: {src}")
    if self.isdir(dst):
      raise IsADirectoryError(f"Destination is a directory, specify file path: {dst}")

    return self._copy_file(src, dst)

  def copy_remote_dir(self, src: Union[str, S3Path], dst: Union[str, S3Path], *args, **kwargs) -> None:
    """Copy directory recursively"""
    if isinstance(src, str):
      src = S3Path.from_path(src)
    if isinstance(dst, str):
      dst = S3Path.from_path(dst)

    # Validate source is a directory
    if not self.exists(src):
      raise FileNotFoundError(f"Source directory does not exist: {src}")
    if not self.isdir(src):
      raise NotADirectoryError(f"Source is not a directory: {src}")

    return self._copy_directory(src, dst)

  def rename_star(self, old_dir: Union[str, S3Path], new_dir: Union[str, S3Path]) -> None:
    """
    Rename contents of old_dir to new_dir without renaming the directory itself.
    Useful when you want to move directory contents but preserve the directory.

    Args:
      old_dir: Source directory
      new_dir: Destination directory

    Raises:
      NotADirectoryError: If old_dir is not a directory
      ClientError: For S3 API errors
    """
    if isinstance(old_dir, str):
      old_dir = S3Path.from_path(old_dir)
    if isinstance(new_dir, str):
      new_dir = S3Path.from_path(new_dir)

    if not self.isdir(old_dir):
      raise NotADirectoryError(f"Source is not a directory: {old_dir}")

    # Get directory contents and rename each entry
    entries = self.listdir(old_dir)
    for entry in entries:
      src = old_dir.join(entry)
      dst = new_dir.join(entry)
      self.rename(src, dst)

  def copyFromLocal(self, local_src: str, remote_dst: str, *args, **kwargs) -> None:
    """
    Copy local file or directory to S3.

    The method preserves directory structure when copying directories.
    For single files, if remote_dst is a directory, the file is copied into it.
    Otherwise remote_dst is used as the destination file path.

    Args:
      local_src: Local file/directory path
      remote_dst: S3 destination path
      *args, **kwargs: Additional arguments (for backward compatibility)
    """
    if isinstance(remote_dst, str):
      remote_dst = S3Path.from_path(remote_dst)

    # Handle directory copy
    if os.path.isdir(local_src):
      # Walk directory tree
      for root, dirs, files in os.walk(local_src, followlinks=False):
        # Calculate relative path
        rel_path = os.path.relpath(root, local_src)

        # Create remote directory path
        remote_dir = remote_dst.join(rel_path) if rel_path != "." else remote_dst

        # Create empty directory if no contents
        if not dirs and not files:
          self.mkdir(remote_dir)
          continue

        # Copy each file
        for file_name in files:
          local_file = os.path.join(root, file_name)
          remote_file = remote_dir.join(file_name)

          self.s3_client.upload_file(Filename=local_file, Bucket=remote_file.bucket, Key=remote_file.key)

    # Handle single file copy
    else:
      if self.isdir(remote_dst):
        remote_file = remote_dst.join(os.path.basename(local_src))
      else:
        remote_file = remote_dst

      self.s3_client.upload_file(Filename=local_src, Bucket=remote_file.bucket, Key=remote_file.key)

  def append(self, path: Union[str, S3Path], data: Union[str, bytes]) -> None:
    """
    Append data to file by reading existing content and writing back.
    Not recommended for large files.

    Args:
      path: S3 path
      data: Data to append
    """
    if isinstance(path, str):
      path = S3Path.from_path(path)

    # Convert string data to bytes
    if isinstance(data, str):
      data = data.encode("utf-8")

    try:
      # Get existing content
      try:
        response = self.s3_client.get_object(Bucket=path.bucket, Key=path.key)
        current = response["Body"].read()
      except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
          current = b""
        else:
          raise

      # Write back with appended data
      self.s3_client.put_object(Bucket=path.bucket, Key=path.key, Body=current + data)
    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to path: {path}")
      raise

  def check_access(self, path: Union[str, S3Path], permission: str = "READ") -> bool:
    """
    Check if user has specified permission on path.

    This method verifies access permissions by attempting actual operations:
    - READ: Tries to access the file/directory
    - WRITE: Tries to create a temporary file and delete it

    Args:
      path: Path to check
      permission: Permission type ("READ" or "WRITE")

    Returns:
      True if access is allowed, False otherwise
    """
    path = S3Path.from_path(path) if isinstance(path, str) else path
    permission = permission.upper()

    try:
      # For write permission, try creating and deleting a temporary file
      if permission == "WRITE":
        temp_filename = f"temp_{int(time.time() * 1000)}"

        if path.is_root():
          return False  # Can't write to root
        elif path.is_bucket():
          # For bucket, try creating a temp file in the bucket
          temp_path = S3Path(bucket=path.bucket, key=temp_filename)
        else:
          # For directory/file path, create temp file in same directory
          if self.isdir(str(path)):
            temp_path = path.join(temp_filename)  # It's a directory, create temp file inside it
          else:
            # It's a file, create temp file in parent directory
            parent = path.parent()
            if parent.is_root():
              return False
            temp_path = parent.join(temp_filename)

        try:
          self.s3_client.put_object(Bucket=temp_path.bucket, Key=temp_path.key, Body=b"")
          self.s3_client.delete_object(Bucket=temp_path.bucket, Key=temp_path.key)  # Delete the temporary file
          return True
        except ClientError as e:
          error_code = e.response["Error"]["Code"]
          if error_code in ("AccessDenied", "Forbidden", "NoSuchBucket"):
            return False
          raise
      else:  # READ permission
        if path.is_root():
          try:
            self.s3_client.list_buckets()  # Root is always readable (list buckets)
            return True
          except ClientError:
            return False
        elif path.is_bucket():
          try:
            self.s3_client.list_objects_v2(Bucket=path.bucket, MaxKeys=1)  # Try to list bucket contents
            return True
          except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("AccessDenied", "Forbidden", "NoSuchBucket"):
              return False
            raise
        else:
          # Try to access the specific object
          try:
            self.s3_client.head_object(Bucket=path.bucket, Key=path.key)
            return True
          except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("AccessDenied", "Forbidden", "NoSuchKey"):
              # For NoSuchKey, check if we can at least list the parent directory
              if error_code == "NoSuchKey":
                parent = path.parent()
                if not parent.is_root():
                  return self.check_access(str(parent), "READ")
              return False
            raise

    except Exception as e:
      LOG.warning(f"S3 check_access encountered error verifying {permission} permission at path '{path}': {e}")
      return False
