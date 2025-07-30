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

import json
import unittest.mock
from unittest.mock import Mock
from urllib.parse import unquote as urllib_unquote

from django.core.files.uploadhandler import InMemoryUploadedFile
from django.utils.datastructures import MultiValueDict

from desktop.settings import BASE_DIR
from indexer.api3 import guess_field_types, guess_format, upload_local_file


def test_xlsx_local_file_upload():

  csv_file = '''test 1,test.2,test_3,test_4
2010-10-10 00:00:00,2012-10-11 01:00:00,30,
2021-10-10 00:00:00,2012-10-11 03:00:00,0.12,
2010-10-10 00:00:00,2012-10-11 09:00:00,0.99,
2010-10-10 00:00:00,2012-10-11 04:00:00,500,
2010-10-10 00:00:00,2012-10-11 09:00:00,29830,
2010-10-10 00:00:00,2012-10-11 08:00:00,50,
2010-10-10 00:00:00,2012-10-11 07:00:00,,
2010-10-10 00:00:00,2012-10-11 03:00:00,,
2010-10-10 00:00:00,2012-10-11 09:00:00,,
2010-10-10 00:00:00,2022-10-10 14:00:00,,
2010-10-10 00:00:00,2021-10-10 15:00:00,,
2010-10-10 00:00:00,,,
2010-10-10 00:00:00,,,
2010-10-10 00:00:00,scattered,,
2010-10-10 00:00:00,,scattered,
2010-10-10 00:00:00,,,
,,,
,,,
scattered,,,
,,scattered,
,,,
,,,
,scattered,,
,,,
,,,
,,,
scattered,,,scattered
,,,
,,,
,,,
,,,
,scattered,,
'''
  with open(BASE_DIR + '/apps/beeswax/data/tables/book.xlsx', 'rb') as file:
    uploaded_file = InMemoryUploadedFile(file=file, field_name='test', name='book(1).xlsx', content_type='xlsx', size=100, charset='utf-8')
    request = Mock()
    request.user = Mock()
    request.FILES = MultiValueDict({'file': [uploaded_file]})

    response = upload_local_file(request)

  path = urllib_unquote(json.loads(response.content.decode('utf-8'))['local_file_url'])
  with open(path, 'r') as _test_file:
    test_file = _test_file.read().replace('\r\n', '\n')

    assert csv_file == test_file
    assert "book_1_xlsx" in path


def test_col_names():
  file_format = {
    'inputFormat': 'localfile',
    'path': BASE_DIR + '/apps/beeswax/data/tables/flights.csv',
    'format': {
      'hasHeader': True
    }
  }
  file_format = json.dumps(file_format)
  request = Mock()
  request.POST = {'fileFormat': file_format}

  response = guess_field_types(request)
  response = json.loads(response.content)

  columns_name = [col['name'] for col in response['columns']]

  assert 'date_1_' in columns_name
  assert 'hour_1' in columns_name
  assert 'minute' in columns_name


def test_guess_format_excel_remote_file():
  file_format = {
    'inputFormat': 'file',
    'path': 's3a://gethue/example1.xlsx',
    'file_type': ''
  }
  file_format = json.dumps(file_format)

  # Create a proper mock filesystem that can handle the S3 path
  mock_fs = Mock()
  mock_fs.isfile.return_value = True

  # Mock file object that simulates an Excel file
  mock_file_obj = Mock()
  mock_file_obj.read.return_value = b'PK\x03\x04'  # Excel file magic bytes
  mock_fs.open.return_value = mock_file_obj

  # Mock stream for CSV format detection
  mock_stream = Mock()
  mock_stream.read.return_value = b'col1,col2,col3\nval1,val2,val3\n'
  mock_stream.seek = Mock()

  request = Mock(
    POST={'fileFormat': file_format}
  )
  request.fs = mock_fs

  # Mock the file format instance to return expected format
  with unittest.mock.patch('indexer.api3.get_file_format_instance') as mock_format_instance:
    mock_format = Mock()
    mock_format.get_format.return_value = {
      'type': 'excel',
      'hasHeader': True,
      'fieldSeparator': ',',
      'recordSeparator': '\\n',
      'quoteChar': '"'
    }
    mock_format_instance.return_value = mock_format

    # Also mock pandas to avoid actual Excel processing
    with unittest.mock.patch('indexer.api3.pd.read_excel') as mock_read_excel:
      mock_df = Mock()
      mock_df.to_csv.return_value = 'col1,col2,col3\nval1,val2,val3\n'
      mock_read_excel.return_value = mock_df

      response = guess_format(request)
      response = json.loads(response.content)

      assert response['type'] == "excel"
