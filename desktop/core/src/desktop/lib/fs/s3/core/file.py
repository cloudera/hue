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
import os
from typing import Union

from botocore.exceptions import ClientError

from desktop.lib.fs.s3.constants import DEFAULT_CHUNK_SIZE
from desktop.lib.fs.s3.core.path import S3Path


class S3File:
  """
  File-like object for S3.
  Supports both reading and writing with buffering.
  """

  def __init__(self, fs, path: Union[str, S3Path], mode: str = "rb"):
    """
    Initialize S3File.

    Args:
        fs: Parent S3FileSystem instance
        path: File path
        mode: File mode ('rb' or 'wb')

    Raises:
        ValueError: If mode is not supported
    """
    if mode not in ("rb", "wb"):
      raise ValueError(f"Unsupported file mode: {mode}")

    self.fs = fs
    self.path = S3Path.from_path(path) if isinstance(path, str) else path
    self.mode = mode
    self.closed = False

    # Initialize buffers
    self._read_buffer = io.BytesIO()
    self._write_buffer = io.BytesIO()
    self._buffer_size = DEFAULT_CHUNK_SIZE

    # Initialize position tracking
    self._position = 0
    self._size = None

    if mode == "rb":
      self._load_size()

  def _load_size(self) -> None:
    """Load file size for reading"""
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
        IOError: If file not open for reading
    """
    if self.closed:
      raise ValueError("I/O operation on closed file")
    if self.mode != "rb":
      raise IOError("File not open for reading")

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
        if e.response["Error"]["Code"] == "404":
          raise FileNotFoundError(f"File not found: {self.path}")
        elif e.response["Error"]["Code"] == "403":
          raise PermissionError(f"Access denied to file: {self.path}")
        raise

    self._position += len(data)
    return data

  def write(self, data: Union[bytes, bytearray]) -> int:
    """
    Write to file.

    Args:
        data: Data to write

    Returns:
        Number of bytes written

    Raises:
        ValueError: If file is closed
        IOError: If file not open for writing
    """
    if self.closed:
      raise ValueError("I/O operation on closed file")
    if self.mode != "wb":
      raise IOError("File not open for writing")

    # Write to buffer
    bytes_written = self._write_buffer.write(data)
    self._position += bytes_written

    # Flush if buffer is full
    if self._write_buffer.tell() >= self._buffer_size:
      self.flush()

    return bytes_written

  def flush(self) -> None:
    """
    Flush write buffer to S3.

    Raises:
        ValueError: If file is closed
    """
    if self.closed:
      raise ValueError("I/O operation on closed file")

    if self.mode == "wb" and self._write_buffer.tell() > 0:
      try:
        # Upload buffer contents
        self._write_buffer.seek(0)
        self.fs.s3_client.put_object(Bucket=self.path.bucket, Key=self.path.key, Body=self._write_buffer.read())

        # Reset buffer
        self._write_buffer = io.BytesIO()

      except ClientError as e:
        if e.response["Error"]["Code"] == "403":
          raise PermissionError(f"Access denied to file: {self.path}")
        raise

  def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
    """
    Seek to position in file.

    Args:
        offset: Offset in bytes
        whence: Reference point (SEEK_SET, SEEK_CUR, SEEK_END)

    Returns:
        New position

    Raises:
        ValueError: If file is closed
        IOError: If seeking is not supported
    """
    if self.closed:
      raise ValueError("I/O operation on closed file")

    if self.mode == "wb":
      raise IOError("Seek not supported in write mode")

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
    """Close file and flush buffers"""
    if not self.closed:
      if self.mode == "wb":
        self.flush()
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
    """Read a line from file"""
    if self.mode != "rb":
      raise IOError("File not open for reading")

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
