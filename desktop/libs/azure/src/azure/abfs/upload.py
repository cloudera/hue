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
from future import standard_library
standard_library.install_aliases()
import logging
import sys
import unicodedata


if sys.version_info[0] > 2:
  from io import StringIO as string_io
else:
  from cStringIO import StringIO as string_io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, SkipFile, StopFutureHandlers, StopUpload, UploadFileException
from desktop.conf import TASK_SERVER

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.fsmanager import get_client
from azure.abfs.__init__ import parse_uri
from azure.abfs.abfs import ABFSFileSystemException

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

DEFAULT_WRITE_SIZE = 100 * 1024 * 1024 # As per Azure doc, maximum blob size is 100MB

LOG = logging.getLogger()

from filebrowser.utils import generate_chunks, calculate_total_size

class ABFSFineUploaderChunkedUpload(object):
  def __init__(self, request, *args, **kwargs):
    self._mp = None
    self._request = request
    self.qquuid = kwargs.get('qquuid')
    self.qqtotalparts = kwargs.get('qqtotalparts')
    self.totalfilesize = kwargs.get('qqtotalfilesize')
    self.file_name = kwargs.get('qqfilename')
    if self.file_name:
      self.file_name = unicodedata.normalize('NFC', self.file_name) # Normalize unicode
    self.destination = kwargs.get('dest', None)  # GET param avoids infinite looping
    self.target_path = None

    if kwargs.get('chunk_size', None) != None:
      self.chunk_size = kwargs.get('chunk_size')

    if self._is_abfs_upload():
      self._fs = self._get_abfs(request)
      self.filesystem, self.directory = parse_uri(self.destination)[:2]
       # Verify that the path exists
      self._fs.stats(self.destination)

  def check_access(self):
    LOG.info('ABFSFineUploaderChunkedUpload: handle file upload wit temp file %s.' % self.file_name)
    self.target_path = self._fs.join(self.destination, self.file_name)
    self.filepath = self.target_path
    self.chunk_size = DEFAULT_WRITE_SIZE
    logging.debug("Chunk size = %d" % self.chunk_size)

    try:
      # Check access permissions before attempting upload
      #self._check_access() #implement later
      LOG.debug("ABFSFineUploaderChunkedUpload: Initiating ABFS upload to target path: %s" % self.target_path)
      if not TASK_SERVER.ENABLED.get():
        self._fs.create(self.target_path)
    except (ABFSFileUploadError, ABFSFileSystemException) as e:
      LOG.error("ABFSFineUploaderChunkedUpload: Encountered error in ABFSUploadHandler check_access: %s" % e)
      self.request.META['upload_failed'] = e
      raise PopupException("ABFSFineUploaderChunkedUpload: Initiating ABFS upload to target path: %s failed %s" % (self.target_path, e))

    if self.totalfilesize != calculate_total_size(self.qquuid, self.qqtotalparts):
      raise PopupException(_('ABFSFineUploaderChunkedUpload: Sorry, the file size is not correct. %(name)s %(qquuid)s %(size)s') %
                            {'name': self.file_name, 'qquuid': self.qquuid, 'size': self.totalfilesize})

  def upload_chunks(self):
    if TASK_SERVER.ENABLED.get():
      self.target_path = self._fs.join(self.destination, self.file_name)
      try:
        LOG.debug("ABFSFineUploaderChunkedUpload: Initiating ABFS upload to target path: %s" % self.target_path)
        self._fs.create(self.target_path)
      except (ABFSFileUploadError, ABFSFileSystemException) as e:
        LOG.error("ABFSFineUploaderChunkedUpload: Encountered error in ABFSUploadHandler check_access: %s" % e)
        self.request.META['upload_failed'] = e
        raise PopupException("ABFSFineUploaderChunkedUpload: Initiating ABFS upload to target path: %s failed %s" % (self.target_path, e))

    try:
      for i, (chunk, total) in enumerate(generate_chunks(self.qquuid, self.qqtotalparts, default_write_size=DEFAULT_WRITE_SIZE), 1):
        LOG.debug("ABFSFineUploaderChunkedUpload: uploading file %s, part %d, size %d, dest: %s" %
                  (self.file_name, i, total, self.destination))
        self._fs._append(self.target_path, chunk)
    except Exception as e:
      self._fs.remove(self.target_path)
      LOG.exception('ABFSFineUploaderChunkedUpload: Failed to upload file to ABFS at %s: %s' % (self.target_path, e))
      raise PopupException("ABFSFineUploaderChunkedUpload: S3FileUploadHandler uploading file %s part: %d failed" % (self.filepath, i))
    finally:
      #finish the upload
      self._fs.flush(self.target_path, {'position': self.totalfilesize})
      LOG.info("ABFSFineUploaderChunkedUpload: has completed file upload to ABFS, total file size is: %d." % self.totalfilesize)
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

    if self._is_abfs_upload():
      self._fs = self._get_abfs(request)
      self.filesystem, self.directory = parse_uri(self.destination)[:2]
       # Verify that the path exists
      self._fs.stats(self.destination)

    LOG.debug("Chunk size = %d" % DEFAULT_WRITE_SIZE)


  def new_file(self, field_name, file_name, *args, **kwargs):
    if self._is_abfs_upload():
      super(ABFSFileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

      LOG.info('Using ABFSFileUploadHandler to handle file upload wit temp file%s.' % file_name)
      self.target_path = self._fs.join(self.destination, file_name)

      try:
        # Check access permissions before attempting upload
        #self._check_access() #implement later
        LOG.debug("Initiating ABFS upload to target path: %s" % self.target_path)
        self._fs.create(self.target_path)
        self.file = SimpleUploadedFile(name=file_name, content='')
        raise StopFutureHandlers()
      except (ABFSFileUploadError, ABFSFileSystemException) as e:
        LOG.error("Encountered error in ABFSUploadHandler check_access: %s" % e)
        self.request.META['upload_failed'] = e
        raise StopUpload()


  def receive_data_chunk(self, raw_data, start):
    if self._is_abfs_upload():
      try:
        LOG.debug("ABFSFileUploadHandler uploading file part with size: %s" % self._part_size)
        self._fs._append(self.target_path, raw_data, params={'position': int(start)})
        return None
      except Exception as e:
        self._fs.remove(self.target_path)
        LOG.exception('Failed to upload file to S3 at %s: %s' % (self.target_path, e))
        raise StopUpload()
    else:
      return raw_data

  def file_complete(self, file_size):
    if self._is_abfs_upload():
      #finish the upload
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
