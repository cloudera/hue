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

import StringIO

from nose.tools import assert_equal
from openpyxl import load_workbook

from desktop.lib.export_csvxls import create_generator, make_response


def content_generator(header, data):
  yield header, data


def test_export_csv():
  headers = ["x", "y"]
  data = [ ["1", "2"], ["3", "4"], ["5,6", "7"], [None, None], ["http://gethue.com", "http://gethue.com"] ]

  # Check CSV
  generator = create_generator(content_generator(headers, data), "csv")
  response = make_response(generator, "csv", "foo")
  assert_equal("application/csv", response["content-type"])
  content = ''.join(response.streaming_content)
  assert_equal('x,y\r\n1,2\r\n3,4\r\n"5,6",7\r\nNULL,NULL\r\nhttp://gethue.com,http://gethue.com\r\n', content)
  assert_equal('attachment; filename="foo.csv"', response["content-disposition"])

  # Check non-ASCII for any browser except FF or no browser info
  generator = create_generator(content_generator(headers, data), "csv")
  response = make_response(generator, "csv", u'gんtbhんjk？￥n')
  assert_equal("application/csv", response["content-type"])
  content = ''.join(response.streaming_content)
  assert_equal('x,y\r\n1,2\r\n3,4\r\n"5,6",7\r\nNULL,NULL\r\nhttp://gethue.com,http://gethue.com\r\n', content)
  assert_equal('attachment; filename="g%E3%82%93tbh%E3%82%93jk%EF%BC%9F%EF%BF%A5n.csv"', response["content-disposition"])

  # Check non-ASCII for FF browser
  generator = create_generator(content_generator(headers, data), "csv")
  response = make_response(generator, "csv", u'gんtbhんjk？￥n',
                           user_agent='Mozilla / 5.0(Macintosh; Intel Mac OS X 10.12;rv:59.0) Gecko / 20100101 Firefox / 59.0)')
  assert_equal("application/csv", response["content-type"])
  content = ''.join(response.streaming_content)
  assert_equal('x,y\r\n1,2\r\n3,4\r\n"5,6",7\r\nNULL,NULL\r\nhttp://gethue.com,http://gethue.com\r\n', content)
  assert_equal('attachment; filename*="g%E3%82%93tbh%E3%82%93jk%EF%BC%9F%EF%BF%A5n.csv"',
               response["content-disposition"])



def test_export_xls():
  headers = ["x", "y"]
  data = [ ["1", "2"], ["3", "4"], ["5,6", "7"], [None, None], ["http://gethue.com", "http://gethue.com"] ]
  sheet = [headers] + data

  # Check XLS
  generator = create_generator(content_generator(headers, data), "xls")
  response = make_response(generator, "xls", "foo")
  assert_equal("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", response["content-type"])

  expected_data = [[cell is not None and cell.replace("http://gethue.com", '=HYPERLINK("http://gethue.com")') or "NULL" for cell in row] for row in sheet]
  sheet_data = _read_xls_sheet_data(response)

  assert_equal(expected_data, sheet_data)
  assert_equal('attachment; filename="foo.xlsx"', response["content-disposition"])


def _read_xls_sheet_data(response):
  content = ''.join(response.content)

  data = StringIO.StringIO()
  data.write(content)

  wb = load_workbook(filename=data, read_only=True)
  ws = wb.active

  return [[cell.value if cell else cell for cell in row] for row in ws.rows]
