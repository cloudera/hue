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
import sys

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, StopFutureHandlers, StopUpload, UploadFileException

from desktop.lib.fsmanager import get_client
from hadoop.conf import UPLOAD_CHUNK_SIZE
from hadoop.fs.exceptions import WebHdfsException

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger()


class OFSFileUploadError(UploadFileException):
  pass


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
