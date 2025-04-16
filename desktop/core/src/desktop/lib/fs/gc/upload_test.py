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

from desktop.lib.fs.gc.upload import GSFileUploadHandler

from unittest.mock import patch, Mock


class TestGSFileUploadHandler(object):

  def test_is_gs_upload(self):
    with patch('desktop.lib.fs.gc.upload.get_client') as get_client:
      get_client.return_value = Mock()

      # Check for gs path
      request = Mock(GET={'dest': 'gs://buck1/key'})
      upload_handler = GSFileUploadHandler(request)

      assert upload_handler._is_gs_upload()

      # Check for ofs path
      request = Mock(GET={'dest': 'ofs://service-id/vol1/buck1/key'})
      upload_handler = GSFileUploadHandler(request)

      assert not upload_handler._is_gs_upload()

      # Check for s3a path
      request = Mock(GET={'dest': 's3a://buck1/key'})
      upload_handler = GSFileUploadHandler(request)

      assert not upload_handler._is_gs_upload()

      # Check for abfs path
      request = Mock(GET={'dest': 'abfs://container1/key'})
      upload_handler = GSFileUploadHandler(request)

      assert not upload_handler._is_gs_upload()

      # Check for hdfs path
      request = Mock(GET={'dest': '/user/gethue'})
      upload_handler = GSFileUploadHandler(request)

      assert not upload_handler._is_gs_upload()

      request = Mock(GET={'dest': 'hdfs://user/gethue'})
      upload_handler = GSFileUploadHandler(request)

      assert not upload_handler._is_gs_upload()

