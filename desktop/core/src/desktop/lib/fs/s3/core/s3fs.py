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
from concurrent.futures import ThreadPoolExecutor
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

from botocore.exceptions import ClientError

from desktop.lib.fs.s3.clients.factory import S3ClientFactory
from desktop.lib.fs.s3.constants import DEFAULT_CHUNK_SIZE, MAX_POOL_CONNECTIONS, S3_DELIMITER
from desktop.lib.fs.s3.core.file import S3File
from desktop.lib.fs.s3.core.path import S3Path
from desktop.lib.fs.s3.core.stat import S3Stat

LOG = logging.getLogger(__name__)


class S3FileSystem:
  """
  S3FileSystem implementation using boto3.
  Supports multiple providers and auth methods.
  """

  def __init__(self, provider_id: str, user: str):
    """
    Initialize S3FileSystem.

    Args:
        provider_id: ID from S3_OBJECT_STORES config
        user: Username for operations
    """
    self.provider_id = provider_id
    self.user = user

    # Initialize client
    self.client = S3ClientFactory.get_client(provider_id, user)

    # Get boto3 clients
    self.s3_client = self.client.s3_client
    self.s3_resource = self.client.s3_resource

    # Initialize thread pool for parallel operations
    self.thread_pool = ThreadPoolExecutor(max_workers=MAX_POOL_CONNECTIONS)

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

  def write(self, path: Union[str, S3Path], data: Union[bytes, BinaryIO], overwrite: bool = False) -> None:
    """Write data to file"""
    if not overwrite and self.exists(path):
      raise FileExistsError(f"File already exists: {path}")

    with self.open(path, "wb") as f:
      if isinstance(data, bytes):
        f.write(data)
      else:
        while True:
          chunk = data.read(DEFAULT_CHUNK_SIZE)
          if not chunk:
            break
          f.write(chunk)

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
        response = self.s3_client.list_objects_v2(Bucket=path.bucket, Prefix=path.key, Delimiter=S3_DELIMITER, MaxKeys=1)
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
        # Create bucket
        self.s3_client.create_bucket(Bucket=path.bucket)
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
        # Delete bucket
        bucket = self._get_bucket(path.bucket)
        bucket.delete()
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
      bucket = self._get_bucket(path.bucket)

      if path.is_bucket():
        # Delete entire bucket
        bucket.objects.all().delete()
        bucket.delete()
      else:
        # Delete prefix
        prefix = path.key
        if not prefix.endswith("/"):
          prefix += "/"

        # Use bulk delete for efficiency
        bucket.objects.filter(Prefix=prefix).delete()
    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to delete: {path}")
      raise

  def copy(self, src: Union[str, S3Path], dst: Union[str, S3Path], recursive: bool = False) -> None:
    """Copy file or directory"""
    if isinstance(src, str):
      src = S3Path.from_path(src)
    if isinstance(dst, str):
      dst = S3Path.from_path(dst)

    if not recursive and self.isdir(src):
      raise IsADirectoryError(f"Source is a directory: {src}")

    try:
      if self.isfile(src):
        # Copy single file
        copy_source = {"Bucket": src.bucket, "Key": src.key}
        self.s3_client.copy(copy_source, dst.bucket, dst.key)
      else:
        # Copy directory
        src_prefix = src.key.rstrip("/") + "/"
        dst_prefix = dst.key.rstrip("/") + "/"

        paginator = self.s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=src.bucket, Prefix=src_prefix):
          for obj in page.get("Contents", []):
            src_key = obj["Key"]
            dst_key = dst_prefix + src_key[len(src_prefix) :]

            copy_source = {"Bucket": src.bucket, "Key": src_key}
            self.s3_client.copy(copy_source, dst.bucket, dst_key)
    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied for copy operation")
      raise

  def rename(self, old: Union[str, S3Path], new: Union[str, S3Path]) -> None:
    """Rename/move file or directory"""
    self.copy(old, new, recursive=True)
    self.rmtree(old)

  def upload(self, src_file: BinaryIO, dst_path: Union[str, S3Path], callback: Optional[callable] = None) -> None:
    """Upload file with progress callback"""
    if isinstance(dst_path, str):
      dst_path = S3Path.from_path(dst_path)

    try:
      if callback:

        def _callback(bytes_transferred):
          callback(bytes_transferred)

        self.s3_client.upload_fileobj(src_file, dst_path.bucket, dst_path.key, Callback=_callback)
      else:
        self.s3_client.upload_fileobj(src_file, dst_path.bucket, dst_path.key)
    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to upload to: {dst_path}")
      raise

  def download(self, src_path: Union[str, S3Path], dst_file: BinaryIO, callback: Optional[callable] = None) -> None:
    """Download file with progress callback"""
    if isinstance(src_path, str):
      src_path = S3Path.from_path(src_path)

    try:
      if callback:

        def _callback(bytes_transferred):
          callback(bytes_transferred)

        self.s3_client.download_fileobj(src_path.bucket, src_path.key, dst_file, Callback=_callback)
      else:
        self.s3_client.download_fileobj(src_path.bucket, src_path.key, dst_file)
    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to download from: {src_path}")
      raise

  def get_presigned_url(self, path: Union[str, S3Path], method: str = "GET", expiration: int = 3600) -> str:
    """Get presigned URL for object"""
    if isinstance(path, str):
      path = S3Path.from_path(path)

    try:
      return self.s3_client.generate_presigned_url(
        "get_object" if method == "GET" else "put_object", Params={"Bucket": path.bucket, "Key": path.key}, ExpiresIn=expiration
      )
    except ClientError as e:
      if e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to generate URL for: {path}")
      raise
