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

"""
Classes for a custom upload handler to stream into GS.

See http://docs.djangoproject.com/en/1.9/topics/http/file-uploads/
"""

import logging
import os
from io import BytesIO as stream_io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload, UploadFileException

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.fs.gc import parse_uri
from desktop.lib.fs.gc.gs import GSFileSystemException
from desktop.lib.fsmanager import get_client
from filebrowser.conf import MAX_FILE_SIZE_UPLOAD_LIMIT
from filebrowser.utils import is_file_upload_allowed, massage_stats

LOG = logging.getLogger()

DEFAULT_WRITE_SIZE = 1024 * 1024 * 50  # TODO: set in configuration (currently 50 MiB)


class GSFileUploadError(UploadFileException):
  pass


# Deprecated and core logic to be replaced with GSNewFileUploadHandler
class GSFileUploadHandler(FileUploadHandler):
  """
  This handler is triggered by any upload field whose destination path starts with "GS" (case insensitive).

  Streams data chunks directly to Google Cloud Storage (GS).
  """

  def __init__(self, request):
    super().__init__(request)
    self.chunk_size = DEFAULT_WRITE_SIZE
    self.destination = request.GET.get('dest')  # GET param avoids infinite looping
    self.target_path = None
    self.file = None
    self._request = request
    self._mp = None
    self._part_num = 1
    self._upload_rejected = False

    if self._is_gs_upload():
      self._fs = get_client(fs='gs', user=request.user.username)
      self.bucket_name, self.key_name = parse_uri(self.destination)[:2]

      # Verify that the path exists
      self._fs._stats(self.destination)
      self._bucket = self._fs._get_bucket(self.bucket_name)

  def new_file(self, field_name, file_name, *args, **kwargs):
    """Handle the start of a new file upload.

    This method is called when a new file is encountered during the upload process.
    """
    if self._is_gs_upload():
      LOG.info('Using GSFileUploadHandler to handle file upload.')

      # Check file extension restrictions
      is_allowed, err_message = is_file_upload_allowed(file_name)
      if not is_allowed:
        LOG.error(err_message)
        self._request.META['upload_failed'] = err_message
        self._upload_rejected = True
        return None

      super().new_file(field_name, file_name, *args, **kwargs)

      self.target_path = self._fs.join(self.key_name, file_name)

      try:
        # Check access permissions before attempting upload
        self._check_access()

        # Create a multipart upload request
        LOG.debug("Initiating GS multipart upload to target path: %s" % self.target_path)
        self._mp = self._bucket.initiate_multipart_upload(self.target_path)
        self.file = SimpleUploadedFile(name=file_name, content='')

        raise StopFutureHandlers()
      except (GSFileUploadError, GSFileSystemException) as e:
        LOG.error("Encountered error in GSUploadHandler check_access: %s" % e)
        self.request.META['upload_failed'] = e
        raise StopUpload()

  def receive_data_chunk(self, raw_data, start):
    """Receive and process a data chunk from the uploaded file.

    This method is called for each data chunk received during the upload process.
    """
    if self._upload_rejected:
      return None
    if self._is_gs_upload():
      try:
        LOG.debug("GSFileUploadHandler uploading file part: %d" % self._part_num)
        fp = self._get_file_part(raw_data)
        self._mp.upload_part_from_file(fp=fp, part_num=self._part_num)
        self._part_num += 1
        return None
      except Exception as e:
        self._mp.cancel_upload()
        LOG.exception('Failed to upload file to GS at %s: %s' % (self.target_path, e))
        raise StopUpload()
    else:
      return raw_data

  def file_complete(self, file_size):
    """Finalize the file upload process.

    This method is called when the entire file has been uploaded.
    """
    if self._upload_rejected:
      return None
    if self._is_gs_upload():
      LOG.info("GSFileUploadHandler has completed file upload to GS, total file size is: %d." % file_size)
      self._mp.complete_upload()
      self.file.size = file_size
      return self.file
    else:
      return None

  def _is_gs_upload(self):
    """Check if the upload destination is Google Cloud Storage (GS).

    Returns:
      bool: True if the destination is GS, False otherwise.
    """
    return self._get_scheme() and self._get_scheme().startswith('gs')

  def _check_access(self):
    """Check if the user has write access to the GS destination path.

    Raises:
      GSFileSystemException: If access permission is insufficient.
    """
    if not self._fs.check_access(self.destination, permission='WRITE'):
      raise GSFileSystemException('Insufficient permissions to write to GS path "%s".' % self.destination)

  def _get_scheme(self):
    """Get the scheme (protocol) of the destination.

    Returns:
      str or None: The scheme (e.g., 'gs') if present in the destination, or None if not present.
    """
    if self.destination:
      dst_parts = self.destination.split('://')
      if dst_parts:
        return dst_parts[0].lower()
      else:
        raise GSFileSystemException('Destination does not start with a valid scheme.')
    else:
      return None

  def _get_file_part(self, raw_data):
    """Create a file-like object from raw data.

    Args:
      raw_data (bytes): Raw data chunk.

    Returns:
      File-like object: A file-like object containing the raw data.
    """
    fp = stream_io()
    fp.write(raw_data)
    fp.seek(0)
    return fp


class GSNewFileUploadHandler(FileUploadHandler):
  """
  Handles direct file uploads to Google Cloud Storage using multipart streaming.

  This handler bypasses local storage and streams file chunks directly to GCS,
  enabling efficient handling of large files without memory constraints.

  Key features:
  - Multipart upload for reliability and resumability
  - Streaming chunks directly to GCS (no temporary files)
  - Comprehensive validation and security checks
  - Automatic cleanup on failure
  """

  def __init__(self, fs, dest_path, overwrite):
    self.chunk_size = DEFAULT_WRITE_SIZE
    self._fs = fs
    self.dest_path = dest_path
    self.overwrite = overwrite
    self.part_number = 1
    self.multipart_upload = None
    self.total_bytes_received = 0

    self.bucket_name, self.key_name = parse_uri(self.dest_path)[:2]

    self._bucket = self._fs._get_bucket(self.bucket_name)

    LOG.info(f"GSNewFileUploadHandler initialized - destination: {dest_path}, overwrite: {overwrite}")

  def new_file(self, field_name, file_name, *args, **kwargs):
    super(GSNewFileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

    LOG.info(f"Starting GCS upload for file: {file_name}")

    # Validate the file upload
    self._validate_upload_prerequisites(file_name)

    self.target_key_path = self._fs.join(self.key_name, file_name)

    # Create a multipart upload request
    try:
      LOG.debug(f"Initiating GS multipart upload to target path: {self.target_key_path}")
      self.multipart_upload = self._bucket.initiate_multipart_upload(self.target_key_path)
      LOG.info(f"Multipart upload initiated successfully for {self.target_key_path}")
    except Exception as e:
      LOG.error(f"Failed to initiate GS multipart upload for {self.target_key_path}: {e}")
      raise PopupException(f"Failed to initiate GS multipart upload to target path: {self.target_key_path}", error_code=500)

  def _validate_upload_prerequisites(self, file_name):
    """Validate all prerequisites before initiating file upload to GS.

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
      raise PopupException(f"Insufficient permissions to write to GS path {self.dest_path}.", error_code=403)

    # Check if the file already exists at the destination path
    target_file_path = self._fs.join(self.dest_path, file_name)
    if self._fs.exists(target_file_path):
      if self.overwrite:
        LOG.info(f"Overwriting existing file: {target_file_path}")
        self._fs.remove(target_file_path)
      else:
        LOG.warning(f"File already exists and overwrite is disabled: {target_file_path}")
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
    self.upload_chunk(raw_data)
    return None

  def upload_chunk(self, raw_chunk):
    try:
      LOG.debug(f"Uploading part {self.part_number} for {self.target_key_path}, size: {len(raw_chunk)} bytes")
      self.multipart_upload.upload_part_from_file(fp=stream_io(raw_chunk), part_num=self.part_number)
      self.part_number += 1
    except Exception as e:
      LOG.error(f"Failed to upload part {self.part_number} for {self.target_key_path}: {e}")
      self.multipart_upload.cancel_upload()
      raise PopupException(f"Failed to upload part: {e}", error_code=500)

  def file_complete(self, file_size):
    # Finish the upload
    LOG.info(f"Completing multipart upload for {self.target_key_path} - total size: {file_size} bytes, parts: {self.part_number - 1}")
    self.multipart_upload.complete_upload()

    file_stats = self._fs.stats(f"gs://{self.bucket_name}/{self.target_key_path}")
    file_stats = massage_stats(file_stats)

    LOG.info(f"Upload completed successfully for {self.target_key_path}")

    return file_stats
