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
import tempfile
import unicodedata

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload, UploadFileException
from django.utils.translation import gettext as _

from desktop.conf import TASK_SERVER_V2
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.fsmanager import get_client
from filebrowser.conf import MAX_FILE_SIZE_UPLOAD_LIMIT
from filebrowser.utils import calculate_total_size, generate_chunks, is_file_upload_allowed, massage_stats
from hadoop.conf import UPLOAD_CHUNK_SIZE
from hadoop.fs.exceptions import WebHdfsException

LOG = logging.getLogger()


class OFSFineUploaderChunkedUpload(object):
  def __init__(self, request, *args, **kwargs):
    self.qquuid = kwargs.get('qquuid')
    self.qqtotalparts = kwargs.get('qqtotalparts')
    self.totalfilesize = kwargs.get('qqtotalfilesize')
    self.file_name = kwargs.get('qqfilename')
    if self.file_name:
      self.file_name = unicodedata.normalize('NFC', self.file_name)  # Normalize unicode
    self.chunk_size = UPLOAD_CHUNK_SIZE.get()
    if kwargs.get('chunk_size', None):
      self.chunk_size = kwargs.get('chunk_size')
    self.destination = kwargs.get('dest', None)  # GET param avoids infinite looping
    self.target_path = None
    self.file = None
    self._request = request
    self._part_size = UPLOAD_CHUNK_SIZE.get()

  def check_access(self):
    # Check file extension restrictions
    is_allowed, err_message = is_file_upload_allowed(self.file_name)
    if not is_allowed:
      LOG.error(err_message)
      self._request.META["upload_failed"] = err_message
      raise PopupException(err_message)

    if self._is_ofs_upload():
      self._fs = self._get_ofs(self._request)

      # Verify that the path exists
      try:
        self._fs.stats(self.destination)
      except Exception:
        raise PopupException(_('Destination path does not exist: %s' % self.destination))

      LOG.debug("Chunk size = %d" % UPLOAD_CHUNK_SIZE.get())
      LOG.info('OFSFineUploaderChunkedUpload: inside check_access function.')
      self.target_path = self._fs.join(self.destination, self.file_name)
      self.filepath = self.target_path

    if self.totalfilesize != calculate_total_size(self.qquuid, self.qqtotalparts):
      raise PopupException(
        _('OFSFineUploaderChunkedUpload: Sorry, the file size is not correct. %(name)s %(qquuid)s %(size)s')
        % {'name': self.file_name, 'qquuid': self.qquuid, 'size': self.totalfilesize}
      )

  def upload_chunks(self):
    LOG.debug("OFSFineUploaderChunkedUpload: upload_chunks")

    if TASK_SERVER_V2.ENABLED.get():
      if self._is_ofs_upload():
        self._fs = self._get_ofs(self._request)

        # Verify that the path exists
        try:
          self._fs.stats(self.destination)
        except Exception:
          raise PopupException(_('Destination path does not exist: %s' % self.destination))

        LOG.debug("Chunk size = %d" % UPLOAD_CHUNK_SIZE.get())
        LOG.info('OFSFineUploaderChunkedUpload: inside check_access function.')
        self.target_path = self._fs.join(self.destination, self.file_name)
        self.filepath = self.target_path

      if self.totalfilesize != calculate_total_size(self.qquuid, self.qqtotalparts):
        raise PopupException(
          _('OFSFineUploaderChunkedUpload: Sorry, the file size is not correct. %(name)s %(qquuid)s %(size)s')
          % {'name': self.file_name, 'qquuid': self.qquuid, 'size': self.totalfilesize}
        )

    try:
      LOG.debug("OFSFineUploaderChunkedUpload: uploading file part with size: %s" % self._part_size)
      fp = io.BytesIO()
      for i, (chunk, total) in enumerate(generate_chunks(self.qquuid, self.qqtotalparts, default_write_size=self.chunk_size), 1):
        logging.debug(
          "OFSFineUploaderChunkedUpload: uploading file %s, part %d, size %d, dest: %s" % (self.file_name, i, total, self.destination)
        )
        fp.write(chunk.getvalue())
      fp.seek(0)
      self._fs.create(self.target_path, data=fp.getvalue())
      fp.close()
    except Exception as e:
      LOG.exception('OFSFineUploaderChunkedUpload: Failed to upload file to ozone at %s: %s' % (self.target_path, e))
      raise PopupException("OFSFineUploaderChunkedUpload: uploading file %s failed with %s" % (self.target_path, e))
    finally:
      # Finish the upload
      LOG.info("OFSFineUploaderChunkedUpload: has completed file upload to OFS, total file size is: %d." % self.totalfilesize)
      LOG.debug("%s" % self._fs.stats(self.target_path))
      return True

  def upload(self):
    self.check_access()
    self.upload_chunks()

  def _get_ofs(self, request):
    fs = get_client(fs='ofs', user=request.user.username)
    if not fs:
      raise PopupException(_("OFSFineUploaderChunkedUpload: No OFS filesystem found."))
    return fs

  def _is_ofs_upload(self):
    return self._get_scheme() and self._get_scheme().startswith('ofs')

  def _get_scheme(self):
    if self.destination:
      dst_parts = self.destination.split('://')
      if dst_parts:
        return dst_parts[0].lower()
      else:
        raise PopupException('OFSFineUploaderChunkedUpload: Destination does not start with a valid scheme.')
    else:
      return None

  def file_complete(self, file_size):
    if self._is_ofs_upload():
      # Finish the upload
      LOG.info("OFSFineUploaderChunkedUpload: has completed file upload to OFS, total file size is: %d." % file_size)
      self.file.size = file_size
      LOG.debug("%s" % self._fs.stats(self.target_path))
      return self.file
    else:
      return None

  def _get_ofs(self, request):
    fs = get_client(fs='ofs', user=request.user.username)
    if not fs:
      raise PopupException(_("OFSFineUploaderChunkedUpload: No OFS filesystem found."))
    return fs

  def _is_ofs_upload(self):
    return self._get_scheme() and self._get_scheme().startswith('ofs')

  def _get_scheme(self):
    if self.destination:
      dst_parts = self.destination.split('://')
      if dst_parts:
        return dst_parts[0].lower()
      else:
        raise PopupException('OFSFineUploaderChunkedUpload: Destination does not start with a valid scheme.')
    else:
      return None


class OFSFileUploadError(UploadFileException):
  pass


# Deprecated and core logic to be replaced with OFSNewFileUploadHandler
class OFSFileUploadHandler(FileUploadHandler):
  """
  This handler is triggered by any upload field whose destination path starts with "OFS" (case insensitive).

  Streams data chunk directly to OFS.
  """

  def __init__(self, request):
    super(OFSFileUploadHandler, self).__init__(request)
    self.chunk_size = UPLOAD_CHUNK_SIZE.get()
    self.destination = request.GET.get('dest', None)  # GET param avoids infinite looping
    self.target_path = None
    self.file = None
    self._request = request
    self._part_size = UPLOAD_CHUNK_SIZE.get()
    self._upload_rejected = False

    if self._is_ofs_upload():
      self._fs = self._get_ofs(request)

      # Verify that the path exists
      try:
        self._fs.stats(self.destination)
      except Exception:
        raise OFSFileUploadError(_('Destination path does not exist: %s' % self.destination))

    LOG.debug("Chunk size = %d" % UPLOAD_CHUNK_SIZE.get())

  def new_file(self, field_name, file_name, *args, **kwargs):
    if self._is_ofs_upload():
      LOG.info('Using OFSFileUploadHandler to handle file upload.')

      # Check file extension restrictions
      is_allowed, err_message = is_file_upload_allowed(file_name)
      if not is_allowed:
        LOG.error(err_message)
        self._request.META['upload_failed'] = err_message
        self._upload_rejected = True
        return None

      super(OFSFileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

      self.target_path = self._fs.join(self.destination, file_name)

      try:
        # Check access permissions before attempting upload
        # self._check_access() # Not implemented
        LOG.debug("Initiating OFS upload to target path: %s" % self.target_path)
        self.file = SimpleUploadedFile(name=file_name, content='')
        raise StopFutureHandlers()
      except (OFSFileUploadError, WebHdfsException) as e:
        LOG.error("Encountered error in OFSUploadHandler check_access: %s" % e)
        self._request.META["upload_failed"] = e
        raise StopUpload()

  def receive_data_chunk(self, raw_data, start):
    if self._upload_rejected:
      return None
    if self._is_ofs_upload():
      LOG.debug("OFSfileUploadHandler receive_data_chunk")
      try:
        LOG.debug("OFSFileUploadHandler uploading file part with size: %s" % self._part_size)
        self._fs.create(self.target_path, data=raw_data)
        return None
      except Exception as e:
        LOG.exception('Failed to upload file to ozone at %s: %s' % (self.target_path, e))
        raise StopUpload()
    else:
      return raw_data

  def file_complete(self, file_size):
    if self._upload_rejected:
      return None
    if self._is_ofs_upload():
      # Finish the upload
      LOG.info("OFSFileUploadHandler has completed file upload to OFS, total file size is: %d." % file_size)
      self.file.size = file_size
      LOG.debug("%s" % self._fs.stats(self.target_path))
      return self.file
    else:
      return None

  def _get_ofs(self, request):
    fs = get_client(fs='ofs', user=request.user.username)
    if not fs:
      raise OFSFileUploadError(_("No OFS filesystem found."))
    return fs

  def _is_ofs_upload(self):
    return self._get_scheme() and self._get_scheme().startswith('ofs')

  def _get_scheme(self):
    if self.destination:
      dst_parts = self.destination.split('://')
      if dst_parts:
        return dst_parts[0].lower()
      else:
        raise OFSFileUploadError('Destination does not start with a valid scheme.')
    else:
      return None


class OFSNewFileUploadHandler(FileUploadHandler):
  """
  Handles file uploads to Ozone File System using temporary file buffering.

  Unlike direct streaming approaches, this handler uses a temporary file to buffer
  the entire upload before transferring to Ozone, as Ozone lacks native append/concat APIs.

  Key features:
  - Temporary file buffering for reliable uploads
  - Automatic cleanup of temp files on success/failure
  - Comprehensive validation and security checks
  - Memory-efficient handling of large files
  """

  def __init__(self, fs, dest_path, overwrite):
    self.chunk_size = UPLOAD_CHUNK_SIZE.get()
    self._fs = fs
    self.dest_path = dest_path
    self.overwrite = overwrite
    self.total_bytes_received = 0
    self.target_file_path = None
    self._temp_file = None
    self._temp_file_path = None

    LOG.info(f"OFSNewFileUploadHandler initialized - destination: {dest_path}, overwrite: {overwrite}")

  def new_file(self, field_name, file_name, *args, **kwargs):
    super(OFSNewFileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

    LOG.info(f"Starting OFS upload for file: {file_name}")

    # Validate upload prerequisites
    self._validate_upload_prerequisites(file_name)

    # Build the target path
    self.target_file_path = self._fs.join(self.dest_path, file_name)
    LOG.info(f"OFS upload target path: {self.target_file_path}")

    # Create a temporary file in the configured temp directory to buffer the upload data
    try:
      self._temp_file = tempfile.NamedTemporaryFile(
        mode="wb",
        dir=self._fs.temp_dir,
        prefix="ofs_upload_",
        suffix=".tmp",
        delete=False,  # We'll handle deletion manually for better error handling
      )
      self._temp_file_path = self._temp_file.name
      LOG.info(f"Created temporary file for OFS upload at {self._temp_file_path}")
    except Exception as ex:
      LOG.error(f"Failed to create temporary file for upload: {ex}")
      raise PopupException(f"Failed to create temporary upload file: {ex}", error_code=500)

    LOG.debug("OFS upload initialization completed successfully")

  def _validate_upload_prerequisites(self, file_name):
    """Validate all prerequisites before initiating file upload to Ozone.

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
      raise PopupException("The destination path %s does not exist." % self.dest_path, error_code=404)

    # Check if the destination path is a directory or not
    if not self._fs.isdir(self.dest_path):
      LOG.error(f"Destination path is not a directory: {self.dest_path}")
      raise PopupException("The destination path %s is not a directory." % self.dest_path, error_code=400)

    # Check if the file name contains a path separator
    # This prevents directory traversal attacks
    if os.path.sep in file_name:
      LOG.warning(f"Invalid filename with path separator: {file_name}")
      raise PopupException("Invalid filename. Path separators are not allowed.", error_code=400)

    # Check if the user has write access to the destination path
    if not self._fs.check_access(self.dest_path, "WRITE"):
      LOG.error(f"Insufficient permissions for destination: {self.dest_path}")
      raise PopupException("Insufficient permissions to write to OFS path %s." % self.dest_path, error_code=403)

    # Build the target path for file existence check
    target_file_path = self._fs.join(self.dest_path, file_name)

    # Check if file exists and handle overwrite
    if self._fs.exists(target_file_path):
      if self.overwrite:
        LOG.info(f"Overwriting existing file: {target_file_path}")
        self._fs.remove(target_file_path, skip_trash=True)
      else:
        LOG.warning(f"File already exists and overwrite is disabled: {target_file_path}")
        raise PopupException(f"File already exists: {target_file_path}", error_code=409)

    LOG.debug("Upload prerequisites validation completed successfully")

  def receive_data_chunk(self, raw_data, start):
    if not self._temp_file:
      LOG.error("Upload handler not properly initialized - temp file is None")
      raise PopupException("Upload handler not properly initialized", error_code=500)

    self.total_bytes_received += len(raw_data)
    max_size = MAX_FILE_SIZE_UPLOAD_LIMIT.get()

    # Perform max size check on the fly
    if max_size != -1 and max_size >= 0 and self.total_bytes_received > max_size:
      LOG.error(f"File size exceeded limit - received: {self.total_bytes_received}, max: {max_size}")
      self._cleanup_temp_file()
      raise PopupException(f"File exceeds maximum allowed size of {max_size} bytes.", error_code=413)

    # Write the data chunk to the temporary file
    try:
      self._temp_file.write(raw_data)
      self._temp_file.flush()  # Ensure data is written to disk
      LOG.debug(f"Written chunk to temp file - size: {len(raw_data)} bytes, total: {self.total_bytes_received} bytes")
    except Exception as e:
      LOG.exception(f"Error writing to temporary file {self._temp_file_path}")
      self._cleanup_temp_file()
      raise PopupException(f"Failed to buffer upload data: {e}", error_code=500)

    return None

  def file_complete(self, file_size):
    # Close the temp file for writing
    if self._temp_file and not self._temp_file.closed:
      self._temp_file.close()

    # Verify we received all data
    if self.total_bytes_received != file_size:
      LOG.error(f"OFS upload size mismatch - expected: {file_size} bytes, received: {self.total_bytes_received} bytes")
      self._cleanup_temp_file()
      raise PopupException(
        f"Upload data size mismatch: expected {file_size} bytes, received {self.total_bytes_received} bytes.", error_code=422
      )

    try:
      # Stream from temp file directly to Ozone
      LOG.info(f"Creating file {self.target_file_path} with {file_size} bytes from temporary file")

      # Open temp file for reading and pass the file handle
      # The requests library will stream from the file handle automatically
      with open(self._temp_file_path, "rb") as temp_file_handle:
        self._fs.create(
          self.target_file_path,
          overwrite=False,  # We already handled overwrite above
          permission=self._fs.getDefaultFilePerms(),  # Default file permissions
          data=temp_file_handle,
        )

      # Verify the upload succeeded by getting the file stats
      file_stats = self._fs.stats(self.target_file_path)

      # Perform size verification explicitly
      actual_size = file_stats.size

      if actual_size != file_size:
        LOG.error(f"OFS upload size mismatch after write for {self.target_file_path}: expected {file_size} bytes, got {actual_size} bytes")

        # Clean up the corrupted file
        try:
          self._fs.remove(self.target_file_path, skip_trash=True)
        except Exception as cleanup_error:
          LOG.warning(f"Failed to clean up corrupted file {self.target_file_path}: {cleanup_error}")

        # Raise exception to fail the upload
        raise PopupException(
          f"Upload verification failed: expected {file_size} bytes, but only {actual_size} bytes were written. "
          "The incomplete file has been removed.",
          error_code=422,
        )

      LOG.info(f"OFS upload completed successfully for {self.target_file_path}, {file_size} bytes written")

    except Exception as e:
      LOG.exception(f'Error creating file "{self.target_file_path}" in OFS')

      # Try to clean up if file was partially created
      try:
        if self._fs.exists(self.target_file_path):
          self._fs.remove(self.target_file_path, skip_trash=True)
      except Exception:
        pass

      if isinstance(e, PopupException):
        raise
      else:
        raise PopupException(f"Failed to upload file in OFS: {str(e)}", error_code=500)
    finally:
      # Always clean up the temporary file
      self._cleanup_temp_file()

    file_stats = massage_stats(file_stats)
    return file_stats

  def _cleanup_temp_file(self):
    """Clean up the temporary file if it exists."""
    if self._temp_file and not self._temp_file.closed:
      try:
        self._temp_file.close()
      except Exception:
        pass

    if self._temp_file_path:
      try:
        if os.path.exists(self._temp_file_path):
          os.unlink(self._temp_file_path)
          LOG.debug(f"Cleaned up temporary file: {self._temp_file_path}")
      except Exception as e:
        LOG.exception(f"Failed to clean up temporary file {self._temp_file_path}: {e}")
