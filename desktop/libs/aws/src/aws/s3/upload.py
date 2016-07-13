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
import StringIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadhandler import FileUploadHandler, SkipFile, StopFutureHandlers, StopUpload

from aws import get_s3fs
from aws.s3 import parse_uri


DEFAULT_WRITE_SIZE = 1024 * 1024 * 50  # TODO: set in configuration (currently 50 MiB)

LOG = logging.getLogger(__name__)


class S3FileUploadError(Exception):
  pass


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
    self._fs = self._get_s3fs(request)
    self._mp = None
    self._part_num = 1

    if self._is_s3_upload():
      self.bucket_name, self.key_name = parse_uri(self.destination)[:2]
      # Verify that the path exists
      self._fs._stats(self.destination)
      self._bucket = self._fs._get_bucket(self.bucket_name)


  def new_file(self, field_name, file_name, *args, **kwargs):
    if self._is_s3_upload():
      super(S3FileUploadHandler, self).new_file(field_name, file_name, *args, **kwargs)

      LOG.info('Using S3FileUploadHandler to handle file upload.')
      self.target_path = self._fs.join(self.key_name, file_name)

      # Create a multipart upload request
      LOG.debug("Initiating S3 multipart upload to target path: %s" % self.target_path)
      self._mp = self._bucket.initiate_multipart_upload(self.target_path)
      self.file = SimpleUploadedFile(name=file_name, content='')
      raise StopFutureHandlers()


  def receive_data_chunk(self, raw_data, start):
    if self._is_s3_upload():
      try:
        LOG.debug("S3FileUploadHandler uploading file part: %d" % self._part_num)
        fp = self._get_file_part(raw_data)
        self._mp.upload_part_from_file(fp=fp, part_num=self._part_num)
        self._part_num += 1
        return None
      except Exception, e:
        self._mp.cancel_upload()
        LOG.exception('Failed to upload file to S3 at %s: %s' % (self.target_path, e))
        raise StopUpload()
    else:
      return raw_data


  def file_complete(self, file_size):
    if self._is_s3_upload():
      # Finish the upload
      LOG.info("S3FileUploadHandler has completed file upload to S3, total file size is: %d." % file_size)
      self._mp.complete_upload()
      self.file.size = file_size
      return self.file
    else:
      return None


  def _get_s3fs(self, request):
    try:
      fs = request.fs
    except AttributeError:
      fs = get_s3fs()

    if not fs:
      raise S3FileUploadError("No S3 filesystem found.")

    return fs


  def _is_s3_upload(self):
    return self._get_scheme() and self._get_scheme().startswith('S3')


  def _get_scheme(self):
    if self.destination:
      dst_parts = self.destination.split('://')
      if dst_parts > 0:
        return dst_parts[0].upper()
      else:
        raise IOError('Destination does not start with a valid scheme.')
    else:
      return None


  def _get_file_part(self, raw_data):
    fp = StringIO.StringIO()
    fp.write(raw_data)
    fp.seek(0)
    return fp
