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
Common library to export either CSV or XLS.
"""
import gc
import logging
import tablib

from django.http import StreamingHttpResponse
from django.utils.encoding import smart_str
from desktop.lib import i18n


LOG = logging.getLogger(__name__)
MAX_XLS_ROWS = 30000


def nullify(cell):
  return cell if cell is not None else "NULL"

def format(row, encoding=None):
  return [smart_str(nullify(cell), encoding or i18n.get_site_encoding(), strings_only=True, errors='replace') for cell in row]

def dataset(headers, data, encoding=None):
  """
  dataset(headers, data) -> Dataset object

  Return a dataset object for a csv or excel document.
  """
  dataset = tablib.Dataset()

  if headers:
    dataset.headers = format(headers, encoding)

  for row in data:
    dataset.append(format(row, encoding))

  return dataset


def create_generator(content_generator, format, encoding=None):
  if format == 'csv':
    show_headers = True
    while True:
      headers, data = content_generator.next()
      yield dataset(show_headers and headers or None, data, encoding).csv
      show_headers = False
  elif format == 'xls':
    headers = None
    data = []
    for _headers, _data in content_generator:
      # Forced limit on size from tablib
      if len(data) > MAX_XLS_ROWS:
        data = data[:MAX_XLS_ROWS]
        break
      headers = _headers
      data.extend(_data)
    yield dataset(headers, data, encoding).xls
    gc.collect()


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
    content_type = 'application/xls'
  else:
    raise Exception("Unknown format: %s" % format)

  resp = StreamingHttpResponse(generator, content_type=content_type)
  resp['Content-Disposition'] = 'attachment; filename=%s.%s' % (name, format)

  try:
    del resp['Content-Length']
  except KeyError:
    pass

  return resp
