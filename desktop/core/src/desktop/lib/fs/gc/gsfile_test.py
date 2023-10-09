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

from nose.tools import assert_true, assert_false, assert_equal, assert_raises
from unittest.mock import Mock

from desktop.lib.fs.gc.gsfile import open, _ReadableGSFile

class TestGSFile(object):

  def test_open_read_mode(self):
    mock_gs_key = Mock()
    mock_gs_key.name = "gethue_dir/test.csv"
    mock_gs_key.bucket.get_key.return_value = mock_gs_key
    
    gs_file = open(mock_gs_key, mode='r')

    assert_true(isinstance(gs_file, _ReadableGSFile))
    mock_gs_key.bucket.get_key.assert_called_once_with('gethue_dir/test.csv')
  
  def test_open_invalid_mode(self):
    mock_gs_key = Mock()
    mock_gs_key.side_effect = IOError('Unavailable mode "w"')

    assert_raises(IOError, open, mock_gs_key, 'w')

