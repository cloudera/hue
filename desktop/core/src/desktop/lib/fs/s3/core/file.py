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

import io
import logging
import os
from typing import Union

from botocore.exceptions import ClientError

from desktop.lib.fs.s3.constants import DEFAULT_CHUNK_SIZE
from desktop.lib.fs.s3.core.path import S3Path

LOG = logging.getLogger()


class S3File:
  """
  File-like object for reading from S3.
  Provides buffered read access with seek support.
  Only supports read modes ('r' or 'rb').
  """

  def __init__(self, fs, path: Union[str, S3Path], mode: str = "rb"):
    """
    Initialize S3File for reading.

    Args:
      fs: Parent S3FileSystem instance
      path: File path
      mode: File mode ('r' or 'rb' only)

    Raises:
      ValueError: If mode is not supported
    """
    # Only allow read modes
    if mode not in ("r", "rb"):
      raise ValueError(f"Unsupported file mode: {mode}. Only 'r' and 'rb' modes are supported")

    self.fs = fs
    self.path = S3Path.from_path(path) if isinstance(path, str) else path
    self.mode = mode
    self.closed = False

    # Initialize read buffer and position tracking
    self._read_buffer = io.BytesIO()
    self._buffer_size = DEFAULT_CHUNK_SIZE
    self._position = 0
    self._size = None

    # Load file size
    self._load_size()

  def _load_size(self) -> None:
    """
    Load file size for reading.

    Raises:
      FileNotFoundError: If file does not exist
      PermissionError: If access is denied
      ClientError: For other S3 API errors
    """
    try:
      response = self.fs.s3_client.head_object(Bucket=self.path.bucket, Key=self.path.key)
      self._size = response["ContentLength"]
    except ClientError as e:
      if e.response["Error"]["Code"] == "404":
        raise FileNotFoundError(f"File not found: {self.path}")
      elif e.response["Error"]["Code"] == "403":
        raise PermissionError(f"Access denied to file: {self.path}")
      raise

  def read(self, size: int = -1) -> bytes:
    """
    Read from file.

    Args:
      size: Number of bytes to read (-1 for all)

    Returns:
      Bytes read

    Raises:
      ValueError: If file is closed
      ClientError: For S3 API errors
    """
    if self.closed:
      raise ValueError("I/O operation on closed file")

    # Handle empty files
    if self._size == 0:
      return b""

    # Handle full file read
    if size < 0:
      size = self._size - self._position

    # Read from buffer first
    data = self._read_buffer.read(size)
    read_size = len(data)

    # If we need more data
    if read_size < size:
      try:
        # Calculate range
        start = self._position + read_size
        end = start + (size - read_size) - 1

        # Get data from S3
        response = self.fs.s3_client.get_object(Bucket=self.path.bucket, Key=self.path.key, Range=f"bytes={start}-{end}")

        # Add to buffer
        new_data = response["Body"].read()
        self._read_buffer = io.BytesIO(new_data)
        data += self._read_buffer.read(size - read_size)

      except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidRange":
          # Should never happen with our range checks
          LOG.error(f"Invalid range request: bytes={start}-{end} for file size {self._size}")
          return data
        elif e.response["Error"]["Code"] == "404":
          raise FileNotFoundError(f"File not found: {self.path}")
        elif e.response["Error"]["Code"] == "403":
          raise PermissionError(f"Access denied to file: {self.path}")
        raise

    self._position += len(data)
    return data

  def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
    """
    Seek to position in file.

    Args:
      offset: Offset in bytes
      whence: Reference point (SEEK_SET, SEEK_CUR, SEEK_END)

    Returns:
      New position

    Raises:
      ValueError: If file is closed or position invalid
    """
    if self.closed:
      raise ValueError("I/O operation on closed file")

    # Calculate new position
    if whence == os.SEEK_SET:
      new_pos = offset
    elif whence == os.SEEK_CUR:
      new_pos = self._position + offset
    elif whence == os.SEEK_END:
      new_pos = self._size + offset
    else:
      raise ValueError(f"Invalid whence value: {whence}")

    # Validate position
    if new_pos < 0:
      raise ValueError("Negative seek position")

    # Update position
    self._position = new_pos
    return self._position

  def tell(self) -> int:
    """
    Get current position in file.

    Returns:
      Current position

    Raises:
      ValueError: If file is closed
    """
    if self.closed:
      raise ValueError("I/O operation on closed file")
    return self._position

  def close(self) -> None:
    """Close file"""
    self.closed = True

  def __enter__(self) -> "S3File":
    """Context manager enter"""
    return self

  def __exit__(self, exc_type, exc_val, exc_tb) -> None:
    """Context manager exit"""
    self.close()

  def __iter__(self) -> "S3File":
    """Iterator interface"""
    return self

  def __next__(self) -> bytes:
    """Get next line"""
    line = self.readline()
    if not line:
      raise StopIteration
    return line

  def readline(self, size: int = -1) -> bytes:
    """
    Read a line from file.

    Args:
      size: Maximum bytes to read (-1 for no limit)

    Returns:
      Line of bytes

    Raises:
      ValueError: If file is closed
    """
    if self.closed:
      raise ValueError("I/O operation on closed file")

    # Read until newline or size
    line = b""
    while size < 0 or len(line) < size:
      byte = self.read(1)
      if not byte:
        break
      line += byte
      if byte == b"\n":
        break

    return line
