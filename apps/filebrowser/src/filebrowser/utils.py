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
import stat
import time
from abc import ABC, abstractmethod
from bz2 import decompress as decompress_bz2
from datetime import datetime
from gzip import decompress as decompress_gzip
from io import BytesIO
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import redis
from django.contrib.auth.models import Group, User

from aws.s3.s3fs import get_s3_home_directory
from azure.abfs.__init__ import get_abfs_home_directory
from desktop.conf import TASK_SERVER_V2
from desktop.lib import fsmanager
from desktop.lib.django_util import JsonResponse
from desktop.lib.fs.gc.gs import get_gs_home_directory
from desktop.lib.fs.ozone.ofs import get_ofs_home_directory
from desktop.lib.fs.proxyfs import ProxyFS
from filebrowser.conf import ALLOW_FILE_EXTENSIONS, ARCHIVE_UPLOAD_TEMPDIR, RESTRICT_FILE_EXTENSIONS
from filebrowser.lib.rwx import filetype, rwx
from hadoop.conf import is_hdfs_trash_enabled

try:
  import pandas as pd

  PANDAS_AVAILABLE = True
except ImportError:
  PANDAS_AVAILABLE = False

try:
  from avro import datafile, io as avro_io

  AVRO_AVAILABLE = True
except ImportError:
  AVRO_AVAILABLE = False

try:
  import snappy

  SNAPPY_AVAILABLE = True
except ImportError:
  SNAPPY_AVAILABLE = False

from filebrowser.conf import MAX_SNAPPY_DECOMPRESSION_SIZE

LOG = logging.getLogger()

# Constants
PARQUET_MAGIC_NUMBER = b"PAR1"
DEFAULT_PARQUET_BUFFER_SIZE = 128 * 1024 * 1024  # 128 MiB
DEFAULT_WRITE_SIZE = 1024 * 1024 * 128


def get_user_fs(username: str) -> ProxyFS:
  """Get a filesystem proxy for the given user.

  This function returns a ProxyFS instance, which is a filesystem-like object
  that routes operations to the appropriate underlying filesystem based on the
  path's URI scheme (e.g., 'abfs://', 's3a://').

  If a path has no scheme, it defaults to the first available filesystem
  configured in Hue (e.g. HDFS). All operations are performed on behalf
  of the specified user.

  Args:
    username: The name of the user to impersonate for filesystem operations.

  Returns:
    A ProxyFS object that can be used to access any configured filesystem.

  Raises:
    ValueError: If the username is empty.
  """
  if not username:
    raise ValueError("Username is required")

  fs = fsmanager.get_filesystem("default")
  fs.setuser(username)

  return fs


def calculate_total_size(uuid, totalparts):
  total = 0
  files = [os.path.join(ARCHIVE_UPLOAD_TEMPDIR.get(), f"{uuid}_{i}") for i in range(totalparts)]
  for file_path in files:
    try:
      total += os.path.getsize(file_path)
    except FileNotFoundError:
      LOG.error(f"calculate_total_size: The file '{file_path}' does not exist.")
    except OSError as e:
      LOG.error(f"calculate_total_size: For the file '{file_path}' error occurred: {e}")
  return total


def generate_chunks(uuid, totalparts, default_write_size=DEFAULT_WRITE_SIZE):
  fp = io.BytesIO()
  total = 0
  files = [os.path.join(ARCHIVE_UPLOAD_TEMPDIR.get(), f"{uuid}_{i}") for i in range(totalparts)]
  for file_path in files:
    with open(file_path, "rb") as f:
      while True:
        # Read the file in portions, e.g., 1MB at a time
        portion = f.read(1 * 1024 * 1024)
        if not portion:
          break
        fp.write(portion)
        total = total + len(portion)
        # If buffer size is more than 128MB, yield the chunk
        if fp.tell() >= default_write_size:
          fp.seek(0)
          yield fp, total
          fp.close()
          fp = io.BytesIO()
  # Yield any remaining data in the buffer
  if fp.tell() > 0:
    fp.seek(0)
    yield fp, total + fp.tell()
    fp.close()
  # chances are the chunk is zero and we never yielded
  else:
    fp.close()
  for file_path in files:
    os.remove(file_path)


def parse_broker_url(broker_url):
  parsed_url = urlparse(broker_url)
  host = parsed_url.hostname
  port = parsed_url.port
  db = int(parsed_url.path.lstrip("/"))
  return redis.Redis(host=host, port=port, db=db)


def get_available_space_for_file_uploads(request):
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    upload_available_space = int(redis_client.get("upload_available_space"))
    if upload_available_space is None:
      raise ValueError("upload_available_space key not set in Redis")
    return JsonResponse({"upload_available_space": upload_available_space})
  except Exception as e:
    LOG.exception("Failed to get available space: %s", str(e))
    return JsonResponse({"error": str(e)}, status=500)
  finally:
    redis_client.close()


def reserve_space_for_file_uploads(uuid, file_size):
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    upload_available_space = int(redis_client.get("upload_available_space"))
    if upload_available_space is None:
      raise ValueError("upload_available_space key not set in Redis")
    if upload_available_space >= file_size:
      redis_client.decrby("upload_available_space", file_size)
      redis_client.set(f"upload__{uuid}", file_size)
      redis_client.set(f"upload__{uuid}_timestamp", int(datetime.now().timestamp()))
      return True
    else:
      return False
  except Exception as e:
    LOG.exception("Failed to reserve space: %s", str(e))
    return False
  finally:
    redis_client.close()


def release_reserved_space_for_file_uploads(uuid):
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    reserved_space = redis_client.get(f"upload__{uuid}")
    if reserved_space:
      file_size = int(redis_client.get(f"upload__{uuid}"))
      redis_client.incrby("upload_available_space", file_size)
      redis_client.delete(f"upload__{uuid}")
      redis_client.delete(f"upload__{uuid}_timestamp")
  except Exception as e:
    LOG.exception("Failed to release reserved space: %s", str(e))
  finally:
    redis_client.close()


def is_file_upload_allowed(file_name):
  """
  Check if a file upload is allowed based on file extension restrictions.

  Args:
    file_name: The name of the file being uploaded

  Returns:
    tuple: (is_allowed, error_message)
      - is_allowed: Boolean indicating if the file upload is allowed
      - error_message: String with error message if not allowed, None otherwise
  """
  if not file_name:
    return True, None

  _, file_type = os.path.splitext(file_name)
  if file_type:
    file_type = file_type.lower()

  # Check allow list first - if set, only these extensions are allowed
  allow_list = ALLOW_FILE_EXTENSIONS.get()
  if allow_list:
    # Normalize extensions to lowercase with dots
    normalized_allow_list = [ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in allow_list]
    if file_type not in normalized_allow_list:
      return False, f'File type "{file_type}" is not permitted. Modify file extension settings to allow this type.'

  # Check restrict list - if set, these extensions are not allowed
  restrict_list = RESTRICT_FILE_EXTENSIONS.get()
  if restrict_list:
    # Normalize extensions to lowercase with dots
    normalized_restrict_list = [ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in restrict_list]
    if file_type in normalized_restrict_list:
      return False, f'File type "{file_type}" is restricted. Update file extension restrictions to allow this type.'

  return True, None


def massage_stats(stats):
  """Converts a file stats object into a dictionary with extra fields.

  This function takes a file stats object (typically from an underlying
  filesystem), converts it to a JSON-compatible dictionary, and enriches it
  with 'type' (e.g., 'file', 'dir') and 'rwx' (e.g., 'rwxr-x---') fields.

  Args:
    stats: A file stats object from a filesystem implementation.

  Returns:
    A dictionary containing the file's stats and additional metadata.
  """
  stats_dict = stats.to_json_dict()
  stats_dict.update(
    {
      "type": filetype(stats.mode),
      "rwx": rwx(stats.mode, stats.aclBit),
    }
  )

  return stats_dict


class FileReader(ABC):
  """
  Abstract base class for file content readers.

  Implements the Strategy Pattern for handling different file formats and
  compression types, providing a consistent interface for reading file contents.
  """

  @abstractmethod
  def read(self, fhandle: Any, path: str, offset: int, length: int, stats: Dict[str, Any], **kwargs) -> bytes:
    """
    Read and return file contents.

    Args:
      fhandle: File handle from filesystem
      path: File path for logging/error purposes
      offset: Byte offset to start reading from
      length: Number of bytes to read
      stats: File statistics dictionary
      **kwargs: Additional reader-specific options

    Returns:
      Raw bytes content

    Raises:
      ValueError: For invalid parameters or unsupported operations
      RuntimeError: For reader-specific errors
    """
    pass


class SimpleReader(FileReader):
  """Reads plain/uncompressed files with optional newline-aware reading."""

  def read(
    self, fhandle: Any, path: str, offset: int, length: int, stats: Dict[str, Any], read_until_newline: bool = False, **kwargs
  ) -> bytes:
    """
    Read from a regular file with optional newline-aware functionality.

    This provides generic readline-like functionality that works across all
    filesystem types, including those that don't support native readline().
    """
    try:
      fhandle.seek(offset)
      contents = fhandle.read(length)

      # If enabled and the initial read didn't end with a newline
      if read_until_newline and contents and not contents.endswith(b"\n"):
        # Generic readline implementation for cross-filesystem compatibility
        extra_bytes = []
        while True:
          byte = fhandle.read(1)
          if not byte:  # End of file
            break
          extra_bytes.append(byte)
          if byte == b"\n":
            break

        if extra_bytes:
          contents += b"".join(extra_bytes)

      return contents

    except Exception as e:
      LOG.exception(f'Failed to read file at "{path}": {e}')
      raise RuntimeError(f"Failed to read file: {e}")


class GzipReader(FileReader):
  """Reads gzip-compressed files."""

  def read(self, fhandle: Any, path: str, offset: int, length: int, stats: Dict[str, Any], **kwargs) -> bytes:
    """Read and decompress gzip file content."""
    if offset != 0:
      raise ValueError("Offsets are not supported with Gzip compression")

    try:
      compressed_data = fhandle.read()
      return decompress_gzip(compressed_data)
    except Exception as e:
      LOG.exception(f'Failed to decompress gzip file at "{path}": {e}')
      raise RuntimeError(f"Failed to decompress gzip file: {e}")


class Bz2Reader(FileReader):
  """Reads bzip2-compressed files."""

  def read(self, fhandle: Any, path: str, offset: int, length: int, stats: Dict[str, Any], **kwargs) -> bytes:
    """Read and decompress bzip2 file content."""
    try:
      # For bz2, we read the requested length from the compressed stream
      compressed_data = fhandle.read(length)
      return decompress_bz2(compressed_data)
    except Exception as e:
      LOG.exception(f'Failed to decompress bz2 file at "{path}": {e}')
      raise RuntimeError(f"Failed to decompress bz2 file: {e}")


class SnappyReader(FileReader):
  """Reads snappy-compressed files."""

  def read(self, fhandle: Any, path: str, offset: int, length: int, stats: Dict[str, Any], **kwargs) -> bytes:
    """Read and decompress snappy file content."""
    if not SNAPPY_AVAILABLE:
      raise RuntimeError("Snappy compression library is not available")

    max_size = MAX_SNAPPY_DECOMPRESSION_SIZE.get()
    if stats["size"] > max_size:
      raise ValueError(f"File size ({stats['size']} bytes) exceeds maximum allowed snappy decompression size ({max_size} bytes)")

    try:
      compressed_data = fhandle.read()
      decompressed_data = snappy.decompress(compressed_data)

      # Create a BytesIO object and delegate to SimpleReader for offset/length handling
      decompressed_fhandle = BytesIO(decompressed_data)
      simple_reader = SimpleReader()
      return simple_reader.read(decompressed_fhandle, path, offset, length, stats)

    except Exception as e:
      LOG.exception(f'Failed to decompress snappy file at "{path}": {e}')
      raise RuntimeError(f"Failed to decompress snappy file: {e}")


class AvroReader(FileReader):
  """Reads Apache Avro files."""

  def read(self, fhandle: Any, path: str, offset: int, length: int, stats: Dict[str, Any], **kwargs) -> bytes:
    """Read Avro file content as JSON-like string records."""
    if not AVRO_AVAILABLE:
      raise RuntimeError("Apache Avro library is not available")

    try:
      fhandle.seek(offset)
      reader = datafile.DataFileReader(fhandle, avro_io.DatumReader())

      try:
        contents_list = []
        read_start = fhandle.tell()

        # Iterate through records and accumulate until we reach the length limit
        for datum in reader:
          current_length = fhandle.tell() - read_start
          if current_length > length and len(contents_list) > 0:
            break

          # Convert each record to string with newline
          record_str = str(datum) + "\n"
          contents_list.append(record_str)

        result = "".join(contents_list)
        return result.encode("utf-8")

      finally:
        reader.close()

    except Exception as e:
      LOG.exception(f'Failed to read Avro file at "{path}": {e}')
      raise RuntimeError(f"Failed to read Avro file: {e}")


class ParquetReader(FileReader):
  """Reads Apache Parquet files."""

  def read(self, fhandle: Any, path: str, offset: int, length: int, stats: Dict[str, Any], **kwargs) -> bytes:
    """Read Parquet file content as string representation."""
    if not PANDAS_AVAILABLE:
      raise RuntimeError("Pandas library is not available for Parquet reading")

    try:
      # Use buffered reading to control memory usage
      buffer_size = min(DEFAULT_PARQUET_BUFFER_SIZE, stats.get("size", DEFAULT_PARQUET_BUFFER_SIZE))

      fhandle.seek(offset)
      file_data = BytesIO(fhandle.read(buffer_size))

      # Read the Parquet file into a DataFrame
      data_frame = pd.read_parquet(file_data, engine="pyarrow")

      # Convert to string representation, considering offset and length as row indices
      data_chunk = data_frame.iloc[offset : offset + length].to_string()

      return data_chunk.encode("utf-8")

    except Exception as e:
      LOG.exception(f'Failed to read Parquet file at "{path}": {e}')
      raise RuntimeError(f"Failed to read Parquet file: {e}")


def get_reader(codec_type: str) -> FileReader:
  """
  Factory function to get the appropriate file reader based on codec type.

  Args:
    codec_type: The compression/format type ('none', 'gzip', 'bz2', 'snappy', 'avro', 'parquet')

  Returns:
    Appropriate FileReader instance

  Raises:
    ValueError: For unsupported codec types
  """
  readers = {
    "none": SimpleReader,
    "gzip": GzipReader,
    "bz2": Bz2Reader,
    "snappy": SnappyReader,
    "avro": AvroReader,
    "parquet": ParquetReader,
  }

  reader_class = readers.get(codec_type)
  if not reader_class:
    raise ValueError(f"Unsupported codec type: {codec_type}")

  return reader_class()


def detect_gzip(contents: bytes) -> bool:
  """Check if file content has gzip magic number."""
  return contents[:2] == b"\x1f\x8b"


def detect_bz2(contents: bytes) -> bool:
  """Check if file content has bzip2 magic number."""
  return contents[:3] == b"BZh"


def detect_avro(contents: bytes) -> bool:
  """Check if file content has Avro magic number."""
  return contents[:3] == b"\x4f\x62\x6a"  # 'Obj' in ASCII


def detect_snappy(contents: bytes) -> bool:
  """
  Check if file content is valid snappy compressed data.

  Note: Requires the entire compressed file contents for validation.
  Returns False if snappy library is not available.
  """
  if not SNAPPY_AVAILABLE:
    return False

  try:
    return snappy.isValidCompressed(contents)
  except Exception:
    LOG.exception("Failed to validate snappy compression")
    return False


def detect_parquet(fhandle: Any) -> bool:
  """Check if file has Parquet magic number."""
  try:
    current_pos = fhandle.tell()
    fhandle.seek(0)
    magic_number = fhandle.read(4)
    fhandle.seek(current_pos)
    return magic_number == PARQUET_MAGIC_NUMBER
  except Exception:
    return False


def _auto_detect_codec(path: str, fhandle: Any, stats: Dict[str, Any]) -> str:
  """
  Auto-detect the codec type based on file extension and content analysis.

  Args:
    path: File path
    fhandle: File handle for content inspection
    stats: File statistics

  Returns:
    Detected codec type string
  """
  # Read first few bytes for magic number detection
  current_pos = fhandle.tell()
  fhandle.seek(0)
  header = fhandle.read(4)  # Read enough for most magic numbers
  fhandle.seek(current_pos)

  # Check by extension and magic number
  if path.endswith(".gz") and detect_gzip(header):
    return "gzip"
  elif (path.endswith(".bz2") or path.endswith(".bzip2")) and detect_bz2(header):
    return "bz2"
  elif path.endswith(".avro") and detect_avro(header):
    return "avro"
  elif detect_parquet(fhandle):
    return "parquet"
  elif path.endswith(".snappy") and SNAPPY_AVAILABLE:
    return "snappy"
  elif SNAPPY_AVAILABLE and stats.get("size", 0) <= MAX_SNAPPY_DECOMPRESSION_SIZE.get():
    # For small files, check if they're snappy compressed
    fhandle.seek(0)
    content = fhandle.read()
    fhandle.seek(current_pos)
    if detect_snappy(content):
      return "snappy"

  return "none"


def read_contents(
  codec_type: Optional[str], path: str, fs: Any, offset: int, length: int, read_until_newline: bool = False
) -> Tuple[str, int, int, bytes]:
  """
  Enhanced file content reader with support for multiple formats and compression types.

  This function provides a robust, extensible way to read file contents with proper
  error handling, memory management, and support for various file formats.

  Args:
    codec_type: Compression/format type (auto-detected if None)
    path: Path to the file
    fs: Filesystem instance
    offset: Byte offset to start reading from
    length: Number of bytes to read
    read_until_newline: If True, read until next newline (simple files only)

  Returns:
    Tuple of (detected_codec, actual_offset, actual_length, content_bytes)

  Raises:
    FileNotFoundError: If file doesn't exist
    ValueError: For invalid parameters
    RuntimeError: For reading/decompression errors
  """
  LOG.debug(f"Reading contents from '{path}' with codec '{codec_type}', offset={offset}, length={length}")

  fhandle = None
  try:
    fhandle = fs.open(path)
    stats = fs.stats(path)

    # Auto-detect codec if not specified
    if not codec_type:
      codec_type = _auto_detect_codec(path, fhandle, stats)
      if codec_type == "gzip":
        offset = 0  # Gzip doesn't support offsets

    # Reset file handle position
    fhandle.seek(0)

    # Get appropriate reader and read content
    reader = get_reader(codec_type)
    contents = reader.read(fhandle, path, offset, length, stats, read_until_newline=read_until_newline)

    # Return actual length of content read (important for read_until_newline)
    actual_length = len(contents)

    LOG.debug(f"Successfully read {actual_length} bytes from '{path}' using {codec_type} codec")

    return (codec_type, offset, actual_length, contents)

  except Exception as e:
    LOG.error(f"Failed to read contents from '{path}': {e}")
    raise

  finally:
    if fhandle:
      try:
        fhandle.close()
      except Exception:
        LOG.warning(f"Failed to close file handle for '{path}'")


def atomic_save_file(fs: Any, path: str, data: bytes) -> None:
  """
  Atomically save file content using a simple, reliable approach.

  This is an improved version of the original do_overwrite_save with:
  - Better error handling and logging
  - Unique temporary file names to prevent conflicts
  - Graceful permission copying (best effort)
  - Comprehensive cleanup on failures

  Args:
    fs: Filesystem instance (ProxyFS or specific FS implementation)
    path: Target file path to save
    data: File content as bytes

  Raises:
    ValueError: For invalid input parameters
    RuntimeError: For filesystem operation failures
  """
  LOG.info(f"Starting atomic save for file: {path} ({len(data)} bytes)")

  temp_path = f"{path}._hue_save_{int(time.time() * 1000)}.tmp"
  temp_created = False

  try:
    # Create temporary file with new content
    LOG.debug(f"Creating temporary file: {temp_path}")
    fs.create(temp_path, overwrite=False, data=data)
    temp_created = True

    # Copy permissions and ownership from original file (best effort)
    _copy_permissions_simple(fs, path, temp_path)

    # Replace original file with temporary file
    LOG.debug(f"Replacing {path} with {temp_path}")
    fs.remove(path, skip_trash=True)
    fs.rename(temp_path, path)
    temp_created = False  # Successfully moved, no cleanup needed

    LOG.info(f"Atomic save completed successfully for: {path}")

  except Exception as e:
    LOG.error(f"Failed to save file {path}: {e}")

    # Clean up temporary file if it still exists
    if temp_created:
      try:
        LOG.debug(f"Cleaning up temporary file: {temp_path}")
        fs.remove(temp_path, skip_trash=True)
      except Exception as cleanup_e:
        LOG.warning(f"Failed to cleanup temporary file {temp_path}: {cleanup_e}")

    raise RuntimeError(f"Failed to save file {path}: {e}")


def _copy_permissions_simple(fs: Any, source_path: str, dest_path: str) -> None:
  """
  Simple permission copying with graceful fallback.

  Attempts to copy permissions and ownership but continues on failure.
  This handles different filesystem capabilities automatically.
  """
  try:
    source_stats = fs.stats(source_path)

    # Try to copy file permissions
    try:
      mode = stat.S_IMODE(source_stats.get("mode", 0o644))

      # Try with superuser operations first, fallback to regular
      if hasattr(fs, "do_as_superuser"):
        fs.do_as_superuser(fs.chmod, dest_path, mode)
      else:
        fs.chmod(dest_path, mode)

      LOG.debug(f"Copied permissions ({oct(mode)}) to {dest_path}")
    except Exception as e:
      LOG.debug(f"Could not copy permissions to {dest_path}: {e}")

    # Try to copy ownership
    try:
      user = source_stats.get("user")
      group = source_stats.get("group")

      if user and group:
        if hasattr(fs, "do_as_superuser"):
          fs.do_as_superuser(fs.chown, dest_path, user, group)
        else:
          fs.chown(dest_path, user, group)

        LOG.debug(f"Copied ownership ({user}:{group}) to {dest_path}")
    except Exception as e:
      LOG.debug(f"Could not copy ownership to {dest_path}: {e}")

  except Exception as e:
    # Continue without copying metadata - not critical for functionality
    LOG.debug(f"Could not read source file metadata from {source_path}: {e}")


def is_destination_parent_of_source(fs: Any, source_path: str, destination_path: str) -> bool:
  """Check if the destination path is the parent directory of the source path."""
  return fs.parent_path(source_path) == fs.normpath(destination_path)


def calculate_permission_mode(
  user_read: bool = False,
  user_write: bool = False,
  user_execute: bool = False,
  group_read: bool = False,
  group_write: bool = False,
  group_execute: bool = False,
  other_read: bool = False,
  other_write: bool = False,
  other_execute: bool = False,
  sticky: bool = False,
) -> int:
  """
  Calculate Unix file permission mode from individual permission flags.

  Converts individual boolean permission flags into a Unix octal permission mode
  suitable for use with chmod operations using efficient bitwise OR operations.

  Args:
    user_read: Owner read permission (r)
    user_write: Owner write permission (w)
    user_execute: Owner execute permission (x)
    group_read: Group read permission (r)
    group_write: Group write permission (w)
    group_execute: Group execute permission (x)
    other_read: Other users read permission (r)
    other_write: Other users write permission (w)
    other_execute: Other users execute permission (x)
    sticky: Sticky bit for special directory behavior

  Returns:
    Integer representing the octal permission mode (e.g., 0o755, 0o644)

  Examples:
    >>> # rwx------ (0o700) - Owner full access
    >>> calculate_permission_mode(user_read=True, user_write=True, user_execute=True)
    448

    >>> # rw-r--r-- (0o644) - Owner read/write, others read-only
    >>> calculate_permission_mode(user_read=True, user_write=True, group_read=True, other_read=True)
    420

    >>> # rwxr-xr-x (0o755) - Owner full, others read/execute
    >>> calculate_permission_mode(
    ...   user_read=True, user_write=True, user_execute=True, group_read=True, group_execute=True, other_read=True, other_execute=True
    ... )
    493

  Note:
    The returned integer can be used directly with os.chmod() or filesystem
    operations that expect octal permission modes.
  """
  mode = 0

  # User permissions
  if user_read:
    mode |= stat.S_IRUSR
  if user_write:
    mode |= stat.S_IWUSR
  if user_execute:
    mode |= stat.S_IXUSR

  # Group permissions
  if group_read:
    mode |= stat.S_IRGRP
  if group_write:
    mode |= stat.S_IWGRP
  if group_execute:
    mode |= stat.S_IXGRP

  # Other permissions
  if other_read:
    mode |= stat.S_IROTH
  if other_write:
    mode |= stat.S_IWOTH
  if other_execute:
    mode |= stat.S_IXOTH

  # Special permissions
  if sticky:
    mode |= stat.S_ISVTX

  return mode


def get_filesystem_home_directory(filesystem_name: str, user) -> str:
  """
  Get the home directory for a user on a specific filesystem.

  Args:
    filesystem_name (str): Name of the filesystem (hdfs, s3a, gs, abfs, ofs)
    user: User object

  Returns:
    str: Home directory path for the user on the specified filesystem
  """

  fs_home_dir_mapping = {
    "hdfs": lambda u: u.get_home_directory(),
    "s3a": get_s3_home_directory,
    "gs": get_gs_home_directory,
    "abfs": get_abfs_home_directory,
    "ofs": get_ofs_home_directory,
  }

  if filesystem_name not in fs_home_dir_mapping:
    raise ValueError(f"Unsupported filesystem: {filesystem_name}")

  return fs_home_dir_mapping[filesystem_name](user)


def get_filesystem_config(username: str) -> dict:
  """
  Get filesystem-specific configuration.

  Args:
    username: Username of the user

  Returns:
    dict: Configuration dictionary for the filesystem
  """
  fs = get_user_fs(username)

  def _is_hdfs_superuser(fs: Any):
    return fs and hasattr(fs, "superuser") and fs.superuser == fs.user

  config = {}
  if type(fs).__name__.lower() == "hdfs":
    is_hdfs_superuser = _is_hdfs_superuser(fs)
    config = {
      "is_trash_enabled": is_hdfs_trash_enabled(),
      # TODO: Check if any of the below fields should be part of new Hue user and group management APIs
      "is_hdfs_superuser": is_hdfs_superuser,
      "groups": [str(x) for x in Group.objects.values_list("name", flat=True)] if is_hdfs_superuser else [],
      "users": [str(x) for x in User.objects.values_list("username", flat=True)] if is_hdfs_superuser else [],
      "superuser": fs.superuser,
      "supergroup": fs.supergroup,
    }
  return config
