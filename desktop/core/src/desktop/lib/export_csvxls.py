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
import StringIO
"""
Common library to export either CSV or XLS.
"""
import gc
import logging
import tablib
import openpyxl

from django.http import StreamingHttpResponse
from django.utils.encoding import smart_str
from desktop.lib import i18n


LOG = logging.getLogger(__name__)


def nullify(cell):
  return cell if cell is not None else "NULL"


def encode_row(row, encoding=None):
  return [smart_str(nullify(cell), encoding or i18n.get_site_encoding(), strings_only=True, errors='replace') for cell in row]


def dataset(headers, data, encoding=None):
  """
  dataset(headers, data) -> Dataset object

  Return a dataset object for a csv or excel document.
  """
  dataset = tablib.Dataset()

  if headers:
    dataset.headers = encode_row(headers, encoding)

  for row in data:
    dataset.append(encode_row(row, encoding))

  return dataset


class XlsWrapper():
  def __init__(self, xls):
    self.xls = xls


def xls_dataset(workbook):
  output = StringIO.StringIO()
  workbook.save(output)
  output.seek(0)
  return XlsWrapper(output.read())


def create_generator(content_generator, format, encoding=None):
  if format == 'csv':
    show_headers = True
    for headers, data in content_generator:
      yield dataset(show_headers and headers or None, data, encoding).csv
      show_headers = False
  elif format == 'xls':
    workbook = openpyxl.Workbook(write_only=True)
    worksheet = workbook.create_sheet()
    row_ctr = 0

    for _headers, _data in content_generator:
      # Write headers to workbook once
      if _headers and row_ctr == 0:
        worksheet.append(encode_row(_headers, encoding))
        row_ctr += 1

      # Write row data to workbook
      for row in _data:
        worksheet.append(encode_row(row, encoding))
        row_ctr += 1

    yield xls_dataset(workbook).xls
    gc.collect()
  else:
    raise Exception("Unknown format: %s" % format)


def make_response(generator, format, name, encoding=None):
  """
  @param data An iterator of rows, where every row is a list of strings
  @param format Either "csv" or "xls"
  @param name Base name for output file
  @param encoding Unicode encoding for data
  """
  if format == 'csv':
    content_type = 'application/csv'
  elif format == 'xls':
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    format = 'xlsx'
  elif format == 'json':
    content_type = 'application/json'
  else:
    raise Exception("Unknown format: %s" % format)

  resp = StreamingHttpResponse(generator, content_type=content_type)
  resp['Content-Disposition'] = 'attachment; filename=%s.%s' % (name, format)

  try:
    del resp['Content-Length']
  except KeyError:
    pass

  return resp
