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
from io import BytesIO as stream_io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload, UploadFileException

from desktop.lib.fs.gc import parse_uri
from desktop.lib.fs.gc.gs import GSFileSystemException
from desktop.lib.fsmanager import get_client

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
      super().new_file(field_name, file_name, *args, **kwargs)

      LOG.info('Using GSFileUploadHandler to handle file upload.')
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


class GSNewFileUploadHandler(GSFileUploadHandler):
  """This handler uploads the file to Google Storage if the destination path starts with "GS" (case insensitive).
  Streams data chunks directly to Google Cloud Storage (GS).
  """

  def __init__(self, dest_path, username):
    self.chunk_size = DEFAULT_WRITE_SIZE
    self.destination = dest_path
    self.username = username
    self.target_path = None
    self.file = None
    self._mp = None
    self._part_num = 1

    if self._is_gs_upload():
      self._fs = get_client(fs='gs', user=self.username)
      self.bucket_name, self.key_name = parse_uri(self.destination)[:2]

      # Verify that the path exists
      self._fs._stats(self.destination)
      self._bucket = self._fs._get_bucket(self.bucket_name)

  def new_file(self, field_name, file_name, *args, **kwargs):
    """Handle the start of a new file upload.

    This method is called when a new file is encountered during the upload process.
    """
    if self._is_gs_upload():
      super().new_file(field_name, file_name, *args, **kwargs)

      LOG.info('Using GSFileUploadHandler to handle file upload.')
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
        raise StopUpload()
