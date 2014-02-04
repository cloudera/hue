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

import tablib

from desktop.lib.export_csvxls import make_response
from nose.tools import assert_equal

def test_export_csv():
  header = ["x", "y"]
  data = [ ["1", "2"], ["3", "4"], ["5,6", "7"], [None, None] ]

  # Check CSV
  response = make_response(header, data, "csv", "foo")
  assert_equal("application/csv", response["content-type"])
  assert_equal('x,y\r\n1,2\r\n3,4\r\n"5,6",7\r\nNULL,NULL\r\n', response.content)
  assert_equal("attachment; filename=foo.csv", response["content-disposition"])

def test_export_xls():
  header = ["x", "y"]
  data = [ ["1", "2"], ["3", "4"], ["5,6", "7"], [None, None] ]

  dataset = tablib.Dataset(headers=header)
  for row in data:
    dataset.append([cell is not None and cell or "NULL" for cell in row])

  # Check XLS
  response = make_response(header, data, "xls", "foo")
  assert_equal("application/xls", response["content-type"])
  assert_equal(dataset.xls, response.content)
  assert_equal("attachment; filename=foo.xls", response["content-disposition"])
