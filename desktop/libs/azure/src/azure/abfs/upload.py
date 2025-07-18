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
import unicodedata
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload, UploadFileException
from django.utils.translation import gettext as _

from azure.abfs.__init__ import parse_uri
from azure.abfs.abfs import ABFSFileSystemException
from desktop.conf import TASK_SERVER_V2
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.fsmanager import get_client
from filebrowser.conf import MAX_FILE_SIZE_UPLOAD_LIMIT
from filebrowser.utils import calculate_total_size, generate_chunks, is_file_upload_allowed, massage_stats

DEFAULT_WRITE_SIZE = 100 * 1024 * 1024  # As per Azure doc, maximum blob size is 100MB

LOG = logging.getLogger()


class ABFSFineUploaderChunkedUpload(object):
  def __init__(self, request, *args, **kwargs):
    self._mp = None
    self._request = request
    self.qquuid = kwargs.get('qquuid')
    self.qqtotalparts = kwargs.get('qqtotalparts')
    self.totalfilesize = kwargs.get('qqtotalfilesize')
    self.file_name = kwargs.get('qqfilename')
    if self.file_name:
      self.file_name = unicodedata.normalize('NFC', self.file_name)  # Normalize unicode
    self.destination = kwargs.get('dest', None)  # GET param avoids infinite looping
    self.target_path = None

    if kwargs.get('chunk_size', None):
      self.chunk_size = kwargs.get('chunk_size')

    if self._is_abfs_upload():
      self._fs = self._get_abfs(request)
      self.filesystem, self.directory = parse_uri(self.destination)[:2]
      # Verify that the path exists
      self._fs.stats(self.destination)

  def check_access(self):
    # Check file extension restrictions
    is_allowed, err_message = is_file_upload_allowed(self.file_name)
    if not is_allowed:
      LOG.error(err_message)
      self._request.META["upload_failed"] = err_message
      raise PopupException(err_message)

    LOG.info('ABFSFineUploaderChunkedUpload: handle file upload wit temp file %s.' % self.file_name)
    self.target_path = self._fs.join(self.destination, self.file_name)
    self.filepath = self.target_path
    self.chunk_size = DEFAULT_WRITE_SIZE
    logging.debug("Chunk size = %d" % self.chunk_size)

    try:
      # Check access permissions before attempting upload
      # self._check_access() #implement later
      LOG.debug("ABFSFineUploaderChunkedUpload: Initiating ABFS upload to target path: %s" % self.target_path)
      if not TASK_SERVER_V2.ENABLED.get():
        self._fs.create(self.target_path)
    except (ABFSFileUploadError, ABFSFileSystemException) as e:
      LOG.error("ABFSFineUploaderChunkedUpload: Encountered error in ABFSUploadHandler check_access: %s" % e)
      self._request.META["upload_failed"] = e
      raise PopupException("ABFSFineUploaderChunkedUpload: Initiating ABFS upload to target path: %s failed %s" % (self.target_path, e))

    if self.totalfilesize != calculate_total_size(self.qquuid, self.qqtotalparts):
      raise PopupException(
        _('ABFSFineUploaderChunkedUpload: Sorry, the file size is not correct. %(name)s %(qquuid)s %(size)s')
        % {'name': self.file_name, 'qquuid': self.qquuid, 'size': self.totalfilesize}
      )

  def upload_chunks(self):
    if TASK_SERVER_V2.ENABLED.get():
      self.target_path = self._fs.join(self.destination, self.file_name)
      try:
        LOG.debug("ABFSFineUploaderChunkedUpload: Initiating ABFS upload to target path: %s" % self.target_path)
        self._fs.create(self.target_path)
      except (ABFSFileUploadError, ABFSFileSystemException) as e:
        LOG.error("ABFSFineUploaderChunkedUpload: Encountered error in ABFSUploadHandler check_access: %s" % e)
        self._request.META['upload_failed'] = e
        raise PopupException("ABFSFineUploaderChunkedUpload: Initiating ABFS upload to target path: %s failed %s" % (self.target_path, e))

    try:
      current_position = 0  # keeps track of position and uploaded_size
      for i, (chunk, total) in enumerate(generate_chunks(self.qquuid, self.qqtotalparts, default_write_size=DEFAULT_WRITE_SIZE), 1):
        chunk_size = len(chunk.getvalue())
        LOG.debug(
          "ABFSFineUploaderChunkedUpload: uploading file %s, part %d, size %d, dest: %s, current_position: %d"
          % (self.file_name, i, chunk_size, self.destination, current_position)
        )
        params = {'position': current_position}
        self._fs._append(self.target_path, chunk, size=chunk_size, offset=0, params=params)
        current_position += chunk_size

    except Exception as e:
      self._fs.remove(self.target_path)
      LOG.exception('ABFSFineUploaderChunkedUpload: Failed to upload file to ABFS at %s: %s' % (self.target_path, e))
      raise PopupException("ABFSFineUploaderChunkedUpload: S3FileUploadHandler uploading file %s part: %d failed" % (self.filepath, i))
    finally:
      # finish the upload using the tracked upload size
      self._fs.flush(self.target_path, {'position': current_position})
      LOG.info("ABFSFineUploaderChunkedUpload: has completed file upload to ABFS, total file size is: %d." % current_position)
      LOG.debug("%s" % self._fs.stats(self.target_path))

  def upload(self):
    self.filepath = self.target_path
    self.check_access()
    self.upload_chunks()

  def _get_abfs(self, request):
    fs = get_client(fs='abfs', user=request.user.username)

    if not fs:
      raise ABFSFileUploadError(_("ABFSFineUploaderChunkedUpload: No ABFS filesystem found"))

    return fs

  def _is_abfs_upload(self):
    return self._get_scheme() and self._get_scheme().startswith('ABFS')

  def _get_scheme(self):
    if self.destination:
      dst_parts = self.destination.split('://')
      if dst_parts:
        return dst_parts[0].upper()
      else:
        raise ABFSFileSystemException('Destination does not start with a valid scheme.')
    else:
      return None


class ABFSFileUploadError(UploadFileException):
  pass


# Deprecated and core logic to be replaced with ABFSNewFileUploadHandler
class ABFSFileUploadHandler(FileUploadHandler):
  """
  This handler is triggered by any upload field whose destination path starts with "ABFS" (case insensitive).

  Streams data chunks directly to ABFS
  """

  def __init__(self, request):
    super(ABFSFileUploadHandler, self).__init__(request)
    self.chunk_size = DEFAULT_WRITE_SIZE
    self.destination = request.GET.get('dest', None)  # GET param avoids infinite looping
    self.target_path = None
    self.file = None
    self._request = request
    self._part_size = DEFAULT_WRITE_SIZE
    self._upload_rejected = False

    if self._is_abfs_upload():
      self._fs = self._get_abfs(request)
      self.filesystem, self.directory = parse_uri(self.destination)[:2]
      # Verify that the path exists
      self._fs.stats(self.destination)

    LOG.debug("Chunk size = %d" % DEFAULT_WRITE_SIZE)

  def new_file(self, field_name, file_name, *args, **kwargs):
    if self._is_abfs_upload():
      LOG.info('Using ABFSFileUploadHandler to handle file upload wit temp file%s.' % file_name)

      # Check file extension restrictions
      is_allowed, err_message = is_file_upload_allowed(file_name)
      if not is_allowed:
        LOG.error(err_message)
        self._request.META['upload_failed'] = err_message
        self._upload_rejected = True
        return None

      super(ABFSFileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

      self.target_path = self._fs.join(self.destination, file_name)

      try:
        # Check access permissions before attempting upload
        # self._check_access() #implement later
        LOG.debug("Initiating ABFS upload to target path: %s" % self.target_path)
        self._fs.create(self.target_path)
        self.file = SimpleUploadedFile(name=file_name, content='')
        raise StopFutureHandlers()
      except (ABFSFileUploadError, ABFSFileSystemException) as e:
        LOG.error("Encountered error in ABFSUploadHandler check_access: %s" % e)
        self.request.META['upload_failed'] = e
        raise StopUpload()

  def receive_data_chunk(self, raw_data, start):
    if self._upload_rejected:
      return None
    if self._is_abfs_upload():
      try:
        LOG.debug("ABFSFileUploadHandler uploading file part with size: %s" % self._part_size)
        buffered_data = BytesIO(raw_data)
        self._fs._append(self.target_path, buffered_data, params={'position': int(start)})
        return None
      except Exception as e:
        self._fs.remove(self.target_path)
        LOG.exception('Failed to upload file to S3 at %s: %s' % (self.target_path, e))
        raise StopUpload()
    else:
      return raw_data

  def file_complete(self, file_size):
    if self._upload_rejected:
      return None
    if self._is_abfs_upload():
      # finish the upload
      self._fs.flush(self.target_path, {'position': int(file_size)})
      LOG.info("ABFSFileUploadHandler has completed file upload to ABFS, total file size is: %d." % file_size)
      self.file.size = file_size
      LOG.debug("%s" % self._fs.stats(self.target_path))
      return self.file
    else:
      return None

  def _get_abfs(self, request):
    fs = get_client(fs='abfs', user=request.user.username)

    if not fs:
      raise ABFSFileUploadError(_("No ABFS filesystem found"))

    return fs

  def _is_abfs_upload(self):
    return self._get_scheme() and self._get_scheme().startswith('ABFS')

  def _get_scheme(self):
    if self.destination:
      dst_parts = self.destination.split('://')
      if dst_parts:
        return dst_parts[0].upper()
      else:
        raise ABFSFileSystemException('Destination does not start with a valid scheme.')
    else:
      return None


class ABFSNewFileUploadHandler(FileUploadHandler):
  """
  Handles direct file uploads to Azure Blob File System using streaming append operations.

  This handler creates the file directly in ABFS and appends chunks as they arrive,
  leveraging ABFS's append capabilities for efficient streaming uploads.

  Key features:
  - Direct streaming to ABFS (no temporary files)
  - Uses ABFS append API with position-based writes
  - Flush operation ensures data persistence
  - Comprehensive validation and security checks
  """

  def __init__(self, fs, dest_path, overwrite):
    self.chunk_size = DEFAULT_WRITE_SIZE
    self._fs = fs
    self.dest_path = dest_path
    self.overwrite = overwrite
    self.total_bytes_received = 0

    LOG.info(f"ABFSNewFileUploadHandler initialized - destination: {dest_path}, overwrite: {overwrite}")

  def new_file(self, field_name, file_name, *args, **kwargs):
    super(ABFSNewFileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

    LOG.info(f"Starting ABFS upload for file: {file_name}")

    # Validate upload prerequisites
    self._validate_upload_prerequisites(file_name)

    self.target_path = self._fs.join(self.dest_path, file_name)

    # Create the file
    try:
      LOG.debug(f"Creating ABFS file at: {self.target_path}")
      self._fs.create(self.target_path)
      LOG.info(f"ABFS file created successfully: {self.target_path}")
    except Exception as e:
      LOG.error(f"Failed to create ABFS file for upload: {e}")
      raise PopupException(f"Failed to initiate ABFS upload to target path: {self.target_path}", error_code=500)

  def _validate_upload_prerequisites(self, file_name):
    """Validate all prerequisites before initiating file upload to ABFS.

    Performs security and permission checks including:
    - File extension restrictions
    - Destination path existence and type validation
    - Directory traversal attack prevention
    - Write permission verification
    - File overwrite handling based on policy

    Args:
      file_name: Name of the file to be uploaded.

    Raises:
      PopupException: With appropriate HTTP error codes:
        - 400: Invalid file extension or filename
        - 403: Insufficient permissions
        - 404: Destination path not found
        - 409: File exists and overwrite is disabled
    """
    LOG.debug(f"Validating upload prerequisites for file: {file_name}")

    # Check file extension restrictions
    is_allowed, err_message = is_file_upload_allowed(file_name)
    if not is_allowed:
      LOG.warning(f"File upload rejected - {err_message}")
      raise PopupException(err_message, error_code=400)

    # Check if the destination path already exists or not
    if not self._fs.exists(self.dest_path):
      LOG.error(f"Destination path does not exist: {self.dest_path}")
      raise PopupException(f"The destination path {self.dest_path} does not exist.", error_code=404)

    # Check if the destination path is a directory or not
    if not self._fs.isdir(self.dest_path):
      LOG.error(f"Destination path is not a directory: {self.dest_path}")
      raise PopupException(f"The destination path {self.dest_path} is not a directory.", error_code=400)

    # Check if the file name contains a path separator
    # This prevents directory traversal attacks
    if os.path.sep in file_name:
      LOG.warning(f"Invalid filename with path separator: {file_name}")
      raise PopupException("Invalid filename. Path separators are not allowed.", error_code=400)

    # Check if the user has write access to the destination path
    if not self._fs.check_access(self.dest_path, permission="WRITE"):
      LOG.error(f"Insufficient permissions for destination: {self.dest_path}")
      raise PopupException(f"Insufficient permissions to write to ABFS path {self.dest_path}.", error_code=403)

    # Check if the file already exists at the destination path
    target_path = self._fs.join(self.dest_path, file_name)
    if self._fs.exists(target_path):
      if self.overwrite:
        LOG.info(f"Overwriting existing file: {target_path}")
        self._fs.remove(target_path)
      else:
        LOG.warning(f"File already exists and overwrite is disabled: {target_path}")
        raise PopupException(f"The file {file_name} already exists at the destination path.", error_code=409)

    LOG.debug("Upload prerequisites validation completed successfully")

  def receive_data_chunk(self, raw_data, start):
    self.total_bytes_received += len(raw_data)
    max_size = MAX_FILE_SIZE_UPLOAD_LIMIT.get()

    # Perform max size check on the fly
    if max_size != -1 and max_size >= 0 and self.total_bytes_received > max_size:
      LOG.error(f"File size exceeded limit - received: {self.total_bytes_received}, max: {max_size}")
      raise PopupException(f"File exceeds maximum allowed size of {max_size} bytes.", error_code=413)

    # Upload the chunk
    self.upload_chunk(raw_data, start)
    return None

  def upload_chunk(self, raw_chunk, start):
    try:
      LOG.debug(f"Appending chunk to ABFS file - position: {start}, size: {len(raw_chunk)} bytes")
      buffered_data = BytesIO(raw_chunk)
      # TODO: Try encapsulating the _append method in the ABFS class with correct refactoring
      self._fs._append(self.target_path, buffered_data, params={"position": int(start)})
    except Exception as e:
      LOG.error(f"Failed to append chunk at position {start}: {e}")
      self._fs.remove(self.target_path)
      raise PopupException(f"Failed to upload part: {e}", error_code=500)

  def file_complete(self, file_size):
    # Finish the upload by flushing
    LOG.info(f"Flushing ABFS file - total size: {file_size} bytes")
    self._fs.flush(self.target_path, {"position": int(file_size)})

    file_stats = self._fs.stats(self.target_path)

    # Perform size verification explicitly
    actual_size = file_stats.size if hasattr(file_stats, "size") else file_stats.get("size", 0)
    if actual_size != file_size:
      LOG.error(f"ABFS upload size mismatch for {self.target_path}: expected {file_size} bytes, got {actual_size} bytes")

      # Clean up the corrupted file
      try:
        self._fs.remove(self.target_path)
        LOG.info(f"Successfully cleaned up corrupted file: {self.target_path}")
      except Exception as cleanup_error:
        LOG.warning(f"Failed to clean up corrupted file {self.target_path}: {cleanup_error}")

      raise PopupException(
        f"Upload verification failed: expected {file_size} bytes, but only {actual_size} bytes were written. "
        f"The incomplete file has been removed.",
        error_code=422,
      )

    LOG.info(f"ABFS upload completed successfully: {file_size} bytes written to {self.target_path}")

    file_stats = massage_stats(file_stats)

    return file_stats
