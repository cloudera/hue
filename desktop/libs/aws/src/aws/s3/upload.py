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
Classes for a custom upload handler to stream into S3.

See http://docs.djangoproject.com/en/1.9/topics/http/file-uploads/
"""

import logging
import os
import unicodedata
from io import BytesIO as stream_io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload, UploadFileException
from django.utils.translation import gettext as _

from aws.s3 import parse_uri
from aws.s3.s3fs import S3FileSystemException
from desktop.conf import TASK_SERVER_V2
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.fsmanager import get_client
from filebrowser.conf import MAX_FILE_SIZE_UPLOAD_LIMIT
from filebrowser.utils import calculate_total_size, generate_chunks, is_file_upload_allowed, massage_stats

DEFAULT_WRITE_SIZE = 1024 * 1024 * 128  # TODO: set in configuration (currently 128 MiB)

LOG = logging.getLogger()


class S3FineUploaderChunkedUpload(object):
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
    self._fs = get_client(fs='s3a', user=self._request.user.username)
    self.bucket_name, self.key_name = parse_uri(self.destination)[:2]
    # Verify that the path exists
    self._fs._stats(self.destination)
    self._bucket = self._fs._get_bucket(self.bucket_name)
    self.filepath = self._fs.join(self.key_name, self.file_name)
    if kwargs.get('chunk_size', None):
      self.chunk_size = kwargs.get('chunk_size')

  def check_access(self):
    # Check file extension restrictions
    is_allowed, err_message = is_file_upload_allowed(self.file_name)
    if not is_allowed:
      LOG.error(err_message)
      self._request.META["upload_failed"] = err_message
      raise PopupException(err_message)

    if self._is_s3_upload():
      try:
        # Check access permissions before attempting upload
        self._check_access()
        # Create a multipart upload request
        LOG.debug("S3FineUploaderChunkedUpload: Initiating S3 multipart upload to target path: %s" % self.filepath)
        self._mp = self._bucket.initiate_multipart_upload(self.filepath)
      except (S3FileUploadError, S3FileSystemException) as e:
        LOG.error("S3FineUploaderChunkedUpload: Encountered error in S3UploadHandler check_access: %s" % e)
        self._request.META['upload_failed'] = e
        raise PopupException("S3FineUploaderChunkedUpload: Initiating S3 multipart upload to target path: %s failed" % self.filepath)

    self.chunk_size = DEFAULT_WRITE_SIZE
    logging.debug("Chunk size = %d" % self.chunk_size)

    if self.totalfilesize != calculate_total_size(self.qquuid, self.qqtotalparts):
      raise PopupException(_('S3FineUploaderChunkedUpload: Sorry, the file size is not correct. %(name)s %(qquuid)s %(size)s') %
                            {'name': self.file_name, 'qquuid': self.qquuid, 'size': self.totalfilesize})

  def upload_chunks(self):
    if TASK_SERVER_V2.ENABLED.get():
      try:
        self._mp = self._bucket.initiate_multipart_upload(self.filepath)
      except (S3FileUploadError, S3FileSystemException) as e:
        LOG.error("S3FineUploaderChunkedUpload: Encountered error in S3UploadHandler check_access: %s" % e)
        self._request.META['upload_failed'] = e
        raise PopupException("S3FineUploaderChunkedUpload: Initiating S3 multipart upload to target path: %s failed" % self.filepath)

    try:
      for i, (chunk, total) in enumerate(generate_chunks(self.qquuid, self.qqtotalparts, default_write_size=self.chunk_size), 1):
        LOG.debug("S3FineUploaderChunkedUpload: uploading file %s, part %d, size %d, dest: %s" %
                  (self.file_name, i, total, self.destination))
        self._mp.upload_part_from_file(fp=chunk, part_num=i)
    except Exception as e:
      self._mp.cancel_upload()
      LOG.exception('Failed to upload file to S3 at %s: %s' % (self.filepath, e))
      raise PopupException("S3FineUploaderChunkedUpload: uploading file %s failed with %s" % (self.filepath, e))
    finally:
      # Finish the upload
      LOG.info("S3FineUploaderChunkedUpload: has completed file upload to S3, total file size is: %d." % self.totalfilesize)
      self._mp.complete_upload()

  def upload(self):
    self.check_access()
    self.upload_chunks()

  def _is_s3_upload(self):
    return self._get_scheme() and self._get_scheme().startswith('S3')

  def _check_access(self):
    if not self._fs.check_access(self.destination, permission='WRITE'):
      raise S3FileSystemException('S3FineUploaderChunkedUpload: Insufficient permissions to write to S3 path "%s".' % self.destination)

  def _get_scheme(self):
    if self.destination:
      dst_parts = self.destination.split('://')
      if dst_parts:
        return dst_parts[0].upper()
      else:
        raise S3FileSystemException('S3FineUploaderChunkedUpload: Destination does not start with a valid scheme.')
    else:
      return None


class S3FileUploadError(UploadFileException):
  pass


# Deprecated and core logic to be replaced with S3NewFileUploadHandler
class S3FileUploadHandler(FileUploadHandler):
  """
  This handler is triggered by any upload field whose destination path starts with "S3" (case insensitive).

  Streams data chunks directly to S3
  """
  def __init__(self, request):
    super(S3FileUploadHandler, self).__init__(request)
    self.chunk_size = DEFAULT_WRITE_SIZE
    self.destination = request.GET.get('dest', None)  # GET param avoids infinite looping
    self.target_path = None
    self.file = None
    self._request = request
    self._mp = None
    self._part_num = 1
    self._upload_rejected = False

    if self._is_s3_upload():
      self._fs = get_client(fs='s3a', user=request.user.username)
      self.bucket_name, self.key_name = parse_uri(self.destination)[:2]
      # Verify that the path exists
      self._fs._stats(self.destination)
      self._bucket = self._fs._get_bucket(self.bucket_name)

  def new_file(self, field_name, file_name, *args, **kwargs):
    if self._is_s3_upload():
      LOG.info('Using S3FileUploadHandler to handle file upload.')

      # Check file extension restrictions
      is_allowed, err_message = is_file_upload_allowed(file_name)
      if not is_allowed:
        LOG.error(err_message)
        self._request.META['upload_failed'] = err_message
        self._upload_rejected = True
        return None

      super(S3FileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

      self.target_path = self._fs.join(self.key_name, file_name)

      try:
        # Check access permissions before attempting upload
        self._check_access()
        # Create a multipart upload request
        LOG.debug("Initiating S3 multipart upload to target path: %s" % self.target_path)
        self._mp = self._bucket.initiate_multipart_upload(self.target_path)
        self.file = SimpleUploadedFile(name=file_name, content='')
        raise StopFutureHandlers()
      except (S3FileUploadError, S3FileSystemException) as e:
        LOG.error("Encountered error in S3UploadHandler check_access: %s" % e)
        self.request.META['upload_failed'] = e
        raise StopUpload()

  def receive_data_chunk(self, raw_data, start):
    if self._upload_rejected:
      return None
    if self._is_s3_upload():
      try:
        LOG.debug("S3FileUploadHandler uploading file part: %d" % self._part_num)
        fp = self._get_file_part(raw_data)
        self._mp.upload_part_from_file(fp=fp, part_num=self._part_num)
        self._part_num += 1
        return None
      except Exception as e:
        self._mp.cancel_upload()
        LOG.exception('Failed to upload file to S3 at %s: %s' % (self.target_path, e))
        raise StopUpload()
    else:
      return raw_data

  def file_complete(self, file_size):
    if self._upload_rejected:
      return None
    if self._is_s3_upload():
      # Finish the upload
      LOG.info("S3FileUploadHandler has completed file upload to S3, total file size is: %d." % file_size)
      self._mp.complete_upload()
      self.file.size = file_size
      return self.file
    else:
      return None

  def _is_s3_upload(self):
    return self._get_scheme() and self._get_scheme().startswith('S3')

  def _check_access(self):
    if not self._fs.check_access(self.destination, permission='WRITE'):
      raise S3FileSystemException('Insufficient permissions to write to S3 path "%s".' % self.destination)

  def _get_scheme(self):
    if self.destination:
      dst_parts = self.destination.split('://')
      if dst_parts:
        return dst_parts[0].upper()
      else:
        raise S3FileSystemException('Destination does not start with a valid scheme.')
    else:
      return None

  def _get_file_part(self, raw_data):
    fp = stream_io()
    fp.write(raw_data)
    fp.seek(0)
    return fp


class S3NewFileUploadHandler(FileUploadHandler):
  """
  Handles direct file uploads to Amazon S3 using multipart streaming.

  This handler bypasses local storage and streams file chunks directly to S3,
  enabling efficient handling of large files without memory constraints.

  Key features:
  - Multipart upload for reliability and parallel processing
  - Streaming chunks directly to S3 (no temporary files)
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

    LOG.info(f"S3NewFileUploadHandler initialized - destination: {dest_path}, overwrite: {overwrite}")

  def new_file(self, field_name, file_name, *args, **kwargs):
    super(S3NewFileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

    LOG.info(f"Starting S3 upload for file: {file_name}")

    # Validate upload prerequisites
    self._validate_upload_prerequisites(file_name)

    self.target_key_path = self._fs.join(self.key_name, file_name)

    # Create a multipart upload request
    try:
      LOG.debug(f"Initiating S3 multipart upload to target path: {self.target_key_path}")
      self.multipart_upload = self._bucket.initiate_multipart_upload(self.target_key_path)
      LOG.info(f"Multipart upload initiated successfully for {self.target_key_path}")
    except Exception as e:
      LOG.error(f"Failed to initiate S3 multipart upload for {self.target_key_path}: {e}")
      raise PopupException(f"Failed to initiate S3 multipart upload to target path: {self.target_key_path}", error_code=500)

  def _validate_upload_prerequisites(self, file_name):
    """Validate all prerequisites before initiating file upload to S3.

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
      raise PopupException(f"Insufficient permissions to write to S3 path {self.dest_path}.", error_code=403)

    # Check if the file already exists at the destination path
    file_path = self._fs.join(self.dest_path, file_name)
    if self._fs.exists(file_path):
      if self.overwrite:
        LOG.info(f"Overwriting existing file: {file_path}")
        self._fs.remove(file_path)
      else:
        LOG.warning(f"File already exists and overwrite is disabled: {file_path}")
        raise PopupException(f"The file {file_name} already exists at the destination path.", error_code=409)

    LOG.debug("Upload prerequisites validation completed successfully")

  def receive_data_chunk(self, raw_data, start):
    self.total_bytes_received += len(raw_data)
    max_size = MAX_FILE_SIZE_UPLOAD_LIMIT.get()

    # Perform max size check on the fly
    if max_size != -1 and max_size >= 0 and self.total_bytes_received > max_size:
      LOG.error(f"File size exceeded limit - received: {self.total_bytes_received}, max: {max_size}")
      raise PopupException(f"File exceeds maximum allowed size of {max_size} bytes.", error_code=413)

    # This chunk must be uploaded by the child class
    self.upload_chunk(raw_data)
    return None  # Return None to signal you are handling the data

  def upload_chunk(self, raw_chunk):
    try:
      LOG.debug(f"Uploading part {self.part_number} for {self.target_key_path}, size: {len(raw_chunk)} bytes")
      self.multipart_upload.upload_part_from_file(fp=self._get_file_part(raw_chunk), part_num=self.part_number)
      self.part_number += 1
    except Exception as e:
      LOG.error(f"Failed to upload part {self.part_number} for {self.target_key_path}: {e}")
      self.multipart_upload.cancel_upload()
      raise PopupException(f"Failed to upload part: {e}", error_code=500)

  def _get_file_part(self, raw_chunk):
    fp = stream_io()
    fp.write(raw_chunk)
    fp.seek(0)
    return fp

  def file_complete(self, file_size):
    # Finish the upload
    LOG.info(f"Completing multipart upload for {self.target_key_path} - total size: {file_size} bytes, parts: {self.part_number - 1}")
    self.multipart_upload.complete_upload()

    file_stats = self._fs.stats(f"s3a://{self.bucket_name}/{self.target_key_path}")

    LOG.info(f"Upload completed successfully for {self.target_key_path}")

    file_stats = massage_stats(file_stats)

    return file_stats
