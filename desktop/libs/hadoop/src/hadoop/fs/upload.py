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
Classes for a custom upload handler to stream into HDFS.
"""

import errno
import logging
import os
import posixpath
import time
import unicodedata
from builtins import object

from django.core.files.uploadhandler import FileUploadHandler, SkipFile, StopFutureHandlers, StopUpload, UploadFileException
from django.urls import reverse
from django.utils.translation import gettext as _

import hadoop.cluster
from desktop.lib import fsmanager
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.fsmanager import get_client
from filebrowser.conf import ARCHIVE_UPLOAD_TEMPDIR
from filebrowser.utils import calculate_total_size, generate_chunks, is_file_upload_allowed
from hadoop.conf import UPLOAD_CHUNK_SIZE
from hadoop.fs.exceptions import WebHdfsException

LOG = logging.getLogger()

UPLOAD_SUBDIR = 'hue-uploads'


class LocalFineUploaderChunkedUpload(object):
  def __init__(self, request, *args, **kwargs):
    self._request = request
    self.qquuid = kwargs.get('qquuid')
    self.qqtotalparts = kwargs.get('qqtotalparts')
    self.totalfilesize = kwargs.get('qqtotalfilesize')
    self.file_name = kwargs.get('qqfilename')
    if self.file_name:
      self.file_name = unicodedata.normalize('NFC', self.file_name)  # Normalize unicode
    local = "local:/"
    if local in kwargs.get('dest', ""):
      self.dest = kwargs.get('dest')[len(local):]
    else:
      self.dest = kwargs.get('dest')
    self.file_name = kwargs.get('qqfilename')
    self.filepath = request.fs.join(self.dest, self.file_name)
    self._file = None
    self.chunk_size = 0

  def check_access(self):
    # Check file extension restrictions
    is_allowed, err_message = is_file_upload_allowed(self.file_name)
    if not is_allowed:
      LOG.error(err_message)
      self._request.META["upload_failed"] = err_message
      raise PopupException(err_message)
    pass

  def upload_chunks(self):
    pass

  def upload(self):
    self.check_access()
    self.upload_chunks()


class HDFSFineUploaderChunkedUpload(object):
  def __init__(self, request, *args, **kwargs):
    self._request = request
    self.qquuid = kwargs.get('qquuid')
    self.qqtotalparts = kwargs.get('qqtotalparts')
    self.totalfilesize = kwargs.get('qqtotalfilesize')
    self.file_name = kwargs.get('qqfilename')
    if self.file_name:
      self.file_name = unicodedata.normalize('NFC', self.file_name)  # Normalize unicode
    self.dest = kwargs.get('dest')
    self.file_name = kwargs.get('qqfilename')
    if kwargs.get('filepath', None):
      self.filepath = kwargs.get('filepath')
    else:
      self.filepath = request.fs.join(self.dest, self.file_name)
      kwargs['filepath'] = self.filepath
    self._file = None
    if kwargs.get('chunk_size', None):
      self.chunk_size = kwargs.get('chunk_size')

  def check_access(self):
    # Check file extension restrictions
    is_allowed, err_message = is_file_upload_allowed(self.file_name)
    if not is_allowed:
      LOG.error(err_message)
      self._request.META["upload_failed"] = err_message
      raise PopupException(err_message)

    if self._request.fs.isdir(self.dest) and posixpath.sep in self.file_name:
      raise PopupException(_('HDFSFineUploaderChunkedUpload: Sorry, no "%(sep)s" in the filename %(name)s.' %
                             {'sep': posixpath.sep, 'name': self.file_name}))

    fs = fsmanager.get_filesystem('default')
    if not fs:
      logging.warning('HDFSFineUploaderChunkedUpload: No HDFS set for HDFS upload')
      raise PopupException(_('HDFSFineUploaderChunkedUpload: No HDFS set for HDFS upload'))
    else:
      fs.setuser(self._request.user.username)
      self.chunk_size = fs.get_upload_chuck_size(self.dest) if self.dest else UPLOAD_CHUNK_SIZE.get()
      logging.debug("Chunk size = %d" % self.chunk_size)

    if self.totalfilesize != calculate_total_size(self.qquuid, self.qqtotalparts):
      raise PopupException(_('HDFSFineUploaderChunkedUpload: Sorry, the file size is not correct. %(name)s %(qquuid)s %(size)s') %
                            {'name': self.file_name, 'qquuid': self.qquuid, 'size': self.totalfilesize})

  def upload_chunks(self):
    self._file = HDFStemporaryUploadedFile(self._request, self.file_name, self.dest)
    logging.debug('HDFSFineUploaderChunkedUpload: Upload attempt to %s' % (self._file.get_temp_path(),))
    for i, (chunk, total) in enumerate(generate_chunks(self.qquuid, self.qqtotalparts, default_write_size=self.chunk_size), 1):
      logging.debug("HDFSFineUploaderChunkedUpload: uploading file %s, part %d, size %d, dest: %s" %
                    (self.file_name, i, total, self.dest))
      self._file.write(chunk)
      percentcomplete = int((total * 100) / self.totalfilesize)
      logging.debug("HDFSFineUploaderChunkedUpload: progress %d" % percentcomplete)
    self._file.flush()
    self._file.finish_upload(self.totalfilesize)
    self._file._do_cleanup = False
    self._file.close()

    try:
      self._request.fs.upload(file=self._file, path=self.dest, username=self._request.user.username)
    except IOError as ex:
      already_exists = False
      try:
        already_exists = self._request.fs.exists(self.dest)
      except Exception:
        pass
      if already_exists:
        msg = _('Destination %(name)s already exists.') % {'name': self.filepath}
      else:
        msg = _('Copy to %(name)s failed: %(error)s') % {'name': self.filepath, 'error': ex}
      raise PopupException(msg)

  def upload(self):
    self.check_access()
    self.upload_chunks()


class HDFSerror(UploadFileException):
  pass


class HDFStemporaryUploadedFile(object):
  """
  A temporary HDFS file to store upload data.
  This class does not have any file read methods.
  """
  def __init__(self, request, name, destination):
    self.name = name
    self.size = None
    self._do_cleanup = False
    try:
      self._fs = request.fs
    except AttributeError:
      self._fs = hadoop.cluster.get_hdfs()

    # Don't want to handle this upload if we don't have an HDFS
    if not self._fs:
      raise HDFSerror(_("No HDFS found"))

    # We want to set the user to be the user doing the upload
    self._fs.setuser(request.user.username)
    self._path = self._fs.mkswap(name, suffix='tmp', basedir=destination)

    # Check access permissions before attempting upload
    try:
      self._fs.check_access(destination, 'rw-')
    except WebHdfsException as e:
      LOG.exception(e)
      raise HDFSerror(_('User %s does not have permissions to write to path "%s".') % (request.user.username, destination))

    if self._fs.exists(self._path):
      self._fs._delete(self._path)
    self._file = self._fs.open(self._path, 'w')

    self._do_cleanup = True

  def __del__(self):
    if self._do_cleanup:
      # Do not do cleanup here. It's hopeless. The self._fs threadlocal states
      # are going to be all wrong.

      # TODO: Check if this is required with new upload handler flow
      LOG.debug(f"Check for left-over upload file for cleanup if the upload op was unsuccessful: {self._path}")

  def get_temp_path(self):
    return self._path

  def finish_upload(self, size):
    try:
      self.size = size
      self.close()
    except Exception:
      LOG.exception('Error uploading file to %s' % (self._path,))
      raise

  def remove(self):
    try:
      self._fs.remove(self._path, True)
      self._do_cleanup = False
    except IOError as ex:
      if ex.errno != errno.ENOENT:
        LOG.exception('Failed to remove temporary upload file "%s". Please cleanup manually: %s' % (self._path, ex))

  def write(self, data):
    self._file.write(data)

  def flush(self):
    self._file.flush()

  def close(self):
    self._file.close()


class CustomDocumentsUploadHandler(FileUploadHandler):
  """
  Delegates the upload handling based on the request URL.

  When the request URL starts with "/desktop/api2/doc/import" (indicating a document
  import), delegate all processing to HDFSfileUploadHandler.
  Otherwise, delegate to FineUploaderChunkedUploadHandler.
  """

  def __init__(self, request, *args, **kwargs):
    super().__init__(request, *args, **kwargs)
    import_path = reverse('import_documents')

    if request.path.startswith(import_path):
      self.delegate = HDFSfileUploadHandler(request)
    else:
      self.delegate = FineUploaderChunkedUploadHandler(request, *args, **kwargs)

  def new_file(self, field_name, file_name, *args, **kwargs):
    try:
      if hasattr(self.delegate, 'new_file'):
        result = self.delegate.new_file(field_name, file_name, *args, **kwargs)
    except StopFutureHandlers:
      result = None
    return result

  def receive_data_chunk(self, raw_data, start):
    if hasattr(self.delegate, 'receive_data_chunk'):
      return self.delegate.receive_data_chunk(raw_data, start)
    return raw_data

  def file_complete(self, file_size):
    if hasattr(self.delegate, 'file_complete'):
      return self.delegate.file_complete(file_size)
    return None


class FineUploaderChunkedUploadHandler(FileUploadHandler):
  """
  A custom file upload handler for handling chunked uploads using FineUploader.

  Attributes:
  - qquuid (str): The unique identifier for the uploaded file.
  - qqpartindex (int): The index of the current chunk being uploaded.
  - qqpartbyteoffset (int): The byte offset of the current chunk within the file.
  - qqtotalfilesize (int): The total size of the uploaded file.
  - qqtotalparts (int): The total number of chunks that make up the file.
  - qqfilename (str): The name of the uploaded file.
  - qqchunksize (int): The size of each chunk being uploaded.
  """
  def __init__(self, request=None, *args, **kwargs):
    super().__init__(request, *args, **kwargs)
    # Capture FineUploader parameters from the request
    self.qquuid = self.request.GET.get('qquuid', "")
    self.qqpartindex = int(self.request.GET.get('qqpartindex', 0))
    self.qqpartbyteoffset = int(self.request.GET.get('qqpartbyteoffset', 0))
    self.qqtotalfilesize = int(self.request.GET.get('qqtotalfilesize', 0))
    self.qqtotalparts = int(self.request.GET.get('qqtotalparts', 1))
    self.qqfilename = self.request.GET.get('qqfilename', "")
    self.qqchunksize = int(self.request.GET.get('qqchunksize', 0))
    self._starttime = time.time()
    self.chunk_file_path = os.path.join(ARCHIVE_UPLOAD_TEMPDIR.get(), f'{self.qquuid}_{self.qqpartindex}')

  def receive_data_chunk(self, raw_data, start):
    """
    Receives a chunk of data and writes it to a temporary file.
    Args:
    - raw_data (bytes): The raw data of the chunk being uploaded.
    - start (int): The starting byte offset of the chunk within the file.
    """
    with open(self.chunk_file_path, 'ab+') as dest:
      dest.seek(0)  # This will overwrite the file if it already exists
      dest.write(raw_data)

  def file_complete(self, file_size):
    """
    Called when the entire file has been uploaded and all chunks have been processed.
    Args:
    - file_size (int): The total size of the uploaded file.
    """
    elapsed = time.time() - self._starttime
    LOG.debug('Uploaded %s bytes %s to in %s seconds' % (file_size, self.chunk_file_path, elapsed))


# Deprecated and core logic to be replaced with HDFSNewFileUploadHandler
class HDFSfileUploadHandler(FileUploadHandler):
  """
  Handle file upload by storing data in a temp HDFS file.

  This handler is triggered by any upload field whose name starts with
  "HDFS" (case insensitive).

  In practice, the middlewares (which access the request.REQUEST/POST/FILES objects) triggers
  the upload before reaching the view in case of permissions error. Read about Django
  uploading documentation.

  This might trigger the upload before executing the hue auth middleware. HDFS destination
  permissions will be doing the checks.
  """
  def __init__(self, request):
    FileUploadHandler.__init__(self, request)
    self._file = None
    self._starttime = 0
    self._activated = False
    self._destination = request.GET.get('dest', None)  # GET param avoids infinite looping
    self.request = request
    self._upload_rejected = False
    fs = fsmanager.get_filesystem('default')
    if not fs:
      LOG.warning('No HDFS set for HDFS upload')
    else:
      fs.setuser(request.user.username)
      FileUploadHandler.chunk_size = fs.get_upload_chuck_size(self._destination) if self._destination else UPLOAD_CHUNK_SIZE.get()
      LOG.debug("Chunk size = %d" % FileUploadHandler.chunk_size)

  def new_file(self, field_name, file_name, *args, **kwargs):
    # Detect "HDFS" in the field name.
    if field_name.upper().startswith('HDFS'):
      LOG.info('Using HDFSfileUploadHandler to handle file upload.')

      # Check file extension restrictions
      is_allowed, err_message = is_file_upload_allowed(file_name)
      if not is_allowed:
        LOG.error(err_message)
        self.request.META['upload_failed'] = err_message
        self._upload_rejected = True
        return None

      try:
        fs_ref = self.request.GET.get('fs', 'default')
        self.request.fs = fsmanager.get_filesystem(fs_ref)
        self.request.fs.setuser(self.request.user.username)
        self._file = HDFStemporaryUploadedFile(self.request, file_name, self._destination)
        LOG.debug('Upload attempt to %s' % (self._file.get_temp_path(),))
        self._activated = True
        self._starttime = time.time()
      except Exception as ex:
        LOG.error("Not using HDFS upload handler: %s" % (ex,))
        self.request.META['upload_failed'] = ex

      raise StopFutureHandlers()

  def receive_data_chunk(self, raw_data, start):
    if self._upload_rejected:
      return None

    LOG.debug("HDFSfileUploadHandler receive_data_chunk")

    if not self._activated:
      if self.request.META.get('PATH_INFO').startswith('/filebrowser') and \
         self.request.META.get('PATH_INFO') != '/filebrowser/upload/archive':
        raise SkipFile()
      return raw_data

    try:
      self._file.write(raw_data)
      self._file.flush()
      return None
    except IOError:
      LOG.exception('Error storing upload data in temporary file "%s"' % (self._file.get_temp_path(),))
      raise StopUpload()

  def file_complete(self, file_size):
    if self._upload_rejected:
      return None

    if not self._activated:
      return None

    try:
      self._file.finish_upload(file_size)
    except IOError:
      LOG.exception('Error closing uploaded temporary file "%s"' % (self._file.get_temp_path(),))
      raise

    elapsed = time.time() - self._starttime
    LOG.info('Uploaded %s bytes to HDFS in %s seconds' % (file_size, elapsed))
    return self._file


class HDFSNewFileUploadHandler(FileUploadHandler):
  """
  Handle file upload by storing data in a temp HDFS file.
  """
  def __init__(self, dest_path, username):
    self.chunk_size = UPLOAD_CHUNK_SIZE.get()
    self._file = None
    self._starttime = 0
    self._destination = dest_path
    self.username = username

    self._fs = self._get_hdfs(self.username)

    LOG.debug("Chunk size = %d" % self.chunk_size)

  def new_file(self, field_name, file_name, *args, **kwargs):
    super(HDFSNewFileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

    LOG.info('Using HDFSfileUploadHandler to handle file upload.')
    try:
      self._file = HDFSNewTemporaryUploadedFile(self._fs, file_name, self._destination, self.username)
      LOG.debug('Upload attempt to %s' % (self._file.get_temp_path()))

      self._starttime = time.time()
    except Exception as ex:
      LOG.error("Not using HDFS upload handler: %s" % (ex))
      raise ex

    raise StopFutureHandlers()

  def receive_data_chunk(self, raw_data, start):
    LOG.debug("HDFSfileUploadHandler receive_data_chunk")

    try:
      self._file.write(raw_data)
      self._file.flush()
      return None
    except IOError:
      LOG.exception('Error storing upload data in temporary file "%s"' % (self._file.get_temp_path()))
      raise StopUpload()

  def file_complete(self, file_size):
    try:
      self._file.finish_upload(file_size)
    except IOError:
      LOG.exception('Error closing uploaded temporary file "%s"' % (self._file.get_temp_path()))
      raise

    elapsed = time.time() - self._starttime
    LOG.info('Uploaded %s bytes to HDFS in %s seconds' % (file_size, elapsed))
    return self._file

  def upload_complete(self):
    LOG.debug("HDFSFileUploadHandler: Running after upload complete task")
    original_file_path = self._fs.join(self._destination, self._file.name)
    tmp_file = self._file.get_temp_path()

    self._fs.do_as_user(self.username, self._fs.rename, tmp_file, original_file_path)

  def upload_interrupted(self):
    LOG.debug("HDFSFileUploadHandler: Attempting cleanup after upload interruption")
    if self._file and hasattr(self._file, 'remove'):
      self._file.remove()

  def _get_hdfs(self, username):
    fs = get_client(fs='hdfs', user=username)
    if not fs:
      raise HDFSerror(_("No HDFS found for upload operation."))

    return fs


class HDFSNewTemporaryUploadedFile(object):
  """
  A temporary HDFS file to store upload data.
  This class does not have any file read methods.
  """
  def __init__(self, fs, name, destination, username):
    self.name = name
    self.size = None
    self._do_cleanup = False
    self._fs = fs

    self._path = self._fs.mkswap(name, suffix='tmp', basedir=destination)

    # Check access permissions before attempting upload
    try:
      self._fs.check_access(destination, 'rw-')
    except WebHdfsException:
      raise HDFSerror(_('User %s does not have permissions to write to path "%s".') % (username, destination))

    if self._fs.exists(self._path):
      self._fs._delete(self._path)

    self._file = self._fs.open(self._path, 'w')

    self._do_cleanup = True

  def __del__(self):
    if self._do_cleanup:
      # Do not do cleanup here. It's hopeless. The self._fs threadlocal states
      # are going to be all wrong.
      LOG.debug(f"Check for left-over upload file for cleanup if the upload op was unsuccessful: {self._path}")

  def get_temp_path(self):
    return self._path

  def finish_upload(self, size):
    try:
      self.size = size
      self.close()
    except Exception:
      LOG.exception('Error uploading file to %s' % (self._path))
      raise

  def remove(self):
    try:
      self._fs.remove(self._path, skip_trash=True)
      self._do_cleanup = False
    except IOError as ex:
      if ex.errno != errno.ENOENT:
        LOG.exception('Failed to remove temporary upload file "%s". Please cleanup manually: %s' % (self._path, ex))

  def write(self, data):
    self._file.write(data)

  def flush(self):
    self._file.flush()

  def close(self):
    self._file.close()
