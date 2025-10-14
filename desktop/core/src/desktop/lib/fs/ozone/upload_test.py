#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import sys
from unittest.mock import Mock, patch, MagicMock

import pytest
from django.core.files.uploadhandler import StopUpload

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.fs.ozone.upload import OFSFileUploadHandler, OFSFineUploaderChunkedUpload
from hadoop.fs.exceptions import WebHdfsException


class TestOFSFileUploadHandler(object):

  def test_is_ofs_upload(self):
    with patch('desktop.lib.fs.ozone.upload.get_client') as get_client:
      get_client.return_value = Mock()

      # Check for ofs path
      request = Mock(GET={'dest': 'ofs://service-id/vol1/buck1/key'})
      upload_handler = OFSFileUploadHandler(request)

      assert upload_handler._is_ofs_upload()

      # Check for s3a path
      request = Mock(GET={'dest': 's3a://buck1/key'})
      upload_handler = OFSFileUploadHandler(request)

      assert not upload_handler._is_ofs_upload()

      # Check for gs path
      request = Mock(GET={'dest': 'gs://buck1/key'})
      upload_handler = OFSFileUploadHandler(request)

      assert not upload_handler._is_ofs_upload()

      # Check for abfs path
      request = Mock(GET={'dest': 'abfs://container1/key'})
      upload_handler = OFSFileUploadHandler(request)

      assert not upload_handler._is_ofs_upload()

      # Check for hdfs path
      request = Mock(GET={'dest': '/user/gethue'})
      upload_handler = OFSFileUploadHandler(request)

      assert not upload_handler._is_ofs_upload()

      request = Mock(GET={'dest': 'hdfs://user/gethue'})
      upload_handler = OFSFileUploadHandler(request)

      assert not upload_handler._is_ofs_upload()

  def test_receive_data_chunk_webhdfs_exception_message(self):
    """Test that WebHdfsException error messages are properly extracted and passed to request.META"""
    with patch('desktop.lib.fs.ozone.upload.get_client') as get_client:
      # Create a mock filesystem that raises WebHdfsException with JSON error
      mock_fs = Mock()
      json_error = '{"RemoteException":{"message":"FILE_ALREADY_EXISTS: File /path/to/file already exists","exception":"FileAlreadyExistsException"}}'
      mock_fs.create.side_effect = WebHdfsException(json_error)
      get_client.return_value = mock_fs

      # Create mock request with ofs destination
      request = Mock(GET={'dest': 'ofs://service-id/vol1/buck1'}, META={}, user=Mock(username='test'))
      upload_handler = OFSFileUploadHandler(request)
      upload_handler.target_path = 'ofs://service-id/vol1/buck1/testfile.txt'

      # Call receive_data_chunk which should catch WebHdfsException and store message in META
      with pytest.raises(StopUpload):
        upload_handler.receive_data_chunk(b'test data', 0)

      # Verify the error message was extracted and stored in request.META
      assert 'upload_failed' in request.META
      error_message = request.META['upload_failed']
      # WebHdfsException extracts and formats the message as "ExceptionType: message"
      assert 'FileAlreadyExistsException' in error_message
      assert 'FILE_ALREADY_EXISTS' in error_message or 'already exists' in error_message


class TestOFSFineUploaderChunkedUpload(object):

  def test_upload_chunks_webhdfs_exception_message(self):
    """Test that WebHdfsException error messages are properly passed in PopupException"""
    with patch('desktop.lib.fs.ozone.upload.get_client') as get_client, \
         patch('desktop.lib.fs.ozone.upload.generate_chunks') as generate_chunks:
      
      # Create a mock filesystem that raises WebHdfsException with JSON error
      mock_fs = Mock()
      json_error = '{"RemoteException":{"message":"Cannot create file under root or volume.","exception":"IOException"}}'
      mock_fs.create.side_effect = WebHdfsException(json_error)
      mock_fs.join = Mock(return_value='ofs://service-id/testfile.txt')
      mock_fs.stats = Mock(return_value=Mock())
      get_client.return_value = mock_fs

      # Mock generate_chunks to return test data
      mock_chunk = Mock()
      mock_chunk.getvalue.return_value = b'test data'
      generate_chunks.return_value = [(mock_chunk, 100)]

      # Create mock request
      mock_request = Mock(user=Mock(username='test'))
      
      # Create uploader instance
      uploader = OFSFineUploaderChunkedUpload(
        mock_request,
        qquuid='test-uuid',
        qqtotalparts=1,
        qqtotalfilesize=100,
        qqfilename='testfile.txt',
        dest='ofs://service-id/vol1/buck1'
      )
      uploader._fs = mock_fs
      uploader.target_path = 'ofs://service-id/testfile.txt'

      # Call upload_chunks which should catch WebHdfsException and raise PopupException with proper message
      with pytest.raises(PopupException) as exc_info:
        uploader.upload_chunks()

      # Verify the error message was extracted from WebHdfsException
      error_message = str(exc_info.value)
      # WebHdfsException extracts and formats the message as "ExceptionType: message"
      assert 'IOException' in error_message
      assert 'Cannot create file under root or volume' in error_message
