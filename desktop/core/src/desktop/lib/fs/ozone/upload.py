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
import sys
import logging
import unicodedata

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload, UploadFileException
from django.utils.translation import gettext as _

from desktop.conf import TASK_SERVER_V2
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.fsmanager import get_client
from filebrowser.utils import calculate_total_size, generate_chunks
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
    if self._is_ofs_upload():
      self._fs = self._get_ofs(self._request)

      # Verify that the path exists
      try:
        self._fs.stats(self.destination)
      except Exception as e:
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
        except Exception as e:
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

    if self._is_ofs_upload():
      self._fs = self._get_ofs(request)

      # Verify that the path exists
      try:
        self._fs.stats(self.destination)
      except Exception as e:
        raise OFSFileUploadError(_('Destination path does not exist: %s' % self.destination))

    LOG.debug("Chunk size = %d" % UPLOAD_CHUNK_SIZE.get())

  def new_file(self, field_name, file_name, *args, **kwargs):
    if self._is_ofs_upload():
      super(OFSFileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

      LOG.info('Using OFSFileUploadHandler to handle file upload.')
      self.target_path = self._fs.join(self.destination, file_name)

      try:
        # Check access permissions before attempting upload
        # self._check_access() # Not implemented
        LOG.debug("Initiating OFS upload to target path: %s" % self.target_path)
        self.file = SimpleUploadedFile(name=file_name, content='')
        raise StopFutureHandlers()
      except (OFSFileUploadError, WebHdfsException) as e:
        LOG.error("Encountered error in OFSUploadHandler check_access: %s" % e)
        self.request.META['upload_failed'] = e
        raise StopUpload()

  def receive_data_chunk(self, raw_data, start):
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


class OFSNewFileUploadHandler(OFSFileUploadHandler):
  """
  This handler uploads the file to Apache Ozone if the destination path starts with "OFS" (case insensitive).
  Streams data chunks directly to OFS.
  """

  def __init__(self, dest_path, username):
    self.chunk_size = UPLOAD_CHUNK_SIZE.get()
    self.destination = dest_path
    self.username = username
    self.target_path = None
    self.file = None
    self._part_size = UPLOAD_CHUNK_SIZE.get()

    if self._is_ofs_upload():
      self._fs = self._get_ofs(self.username)

      # Verify that the path exists
      try:
        self._fs.stats(self.destination)
      except Exception as e:
        raise OFSFileUploadError(_('Destination path does not exist: %s' % self.destination))

    LOG.debug("Chunk size = %d" % UPLOAD_CHUNK_SIZE.get())

  def new_file(self, field_name, file_name, *args, **kwargs):
    if self._is_ofs_upload():
      super(OFSFileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

      LOG.info('Using OFSFileUploadHandler to handle file upload.')
      self.target_path = self._fs.join(self.destination, file_name)

      try:
        # Check access permissions before attempting upload
        # self._check_access() # Not implemented
        LOG.debug("Initiating OFS upload to target path: %s" % self.target_path)
        self.file = SimpleUploadedFile(name=file_name, content='')
        raise StopFutureHandlers()
      except (OFSFileUploadError, WebHdfsException) as e:
        LOG.error("Encountered error in OFSUploadHandler check_access: %s" % e)
        raise StopUpload()

  def _get_ofs(self, username):
    fs = get_client(fs='ofs', user=username)
    if not fs:
      raise OFSFileUploadError(_("No OFS filesystem found."))

    return fs
