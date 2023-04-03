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

from nose.tools import assert_true, assert_false
from desktop.lib.fs.ozone.upload import OFSFileUploadHandler

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


class TestOFSFileUploadHandler(object):

  def test_is_ofs_upload(self):
    with patch('desktop.lib.fs.ozone.upload.get_client') as get_client:
      get_client.return_value = Mock()

      # Check for ofs path
      request = Mock(GET={'dest': 'ofs://service-id/vol1/buck1/key'})
      upload_handler = OFSFileUploadHandler(request)

      assert_true(upload_handler._is_ofs_upload())

      # Check for s3a path
      request = Mock(GET={'dest': 's3a://buck1/key'})
      upload_handler = OFSFileUploadHandler(request)

      assert_false(upload_handler._is_ofs_upload())

      # Check for abfs path
      request = Mock(GET={'dest': 'abfs://container1/key'})
      upload_handler = OFSFileUploadHandler(request)

      assert_false(upload_handler._is_ofs_upload())

      # Check for hdfs path
      request = Mock(GET={'dest': '/user/gethue'})
      upload_handler = OFSFileUploadHandler(request)

      assert_false(upload_handler._is_ofs_upload())

      request = Mock(GET={'dest': 'hdfs://user/gethue'})
      upload_handler = OFSFileUploadHandler(request)

      assert_false(upload_handler._is_ofs_upload())