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
import logging
import tablib

from django.http import HttpResponse
from django.utils.encoding import smart_str
from desktop.lib import i18n

LOG = logging.getLogger(__name__)
XLS_SIZE_LIMIT = 1024 * 1024 * 1024      # 1GB

class TooBigToDownloadException(Exception):
  pass

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
  dataset.headers = format(headers, encoding)

  for row in data:
    dataset.append(format(row, encoding))

  return dataset

def make_response(headers, data, format, name, encoding=None):
  """
  @param headers List of strings to form the header
  @param data An iterator of rows, where every row is a list of strings
  @param format Either "csv" or "xls"
  @param name Base name for output file
  @param encoding Unicode encoding for data
  """
  if format == 'csv':
    mimetype = 'application/csv'
  elif format == 'xls':
    mimetype = 'application/xls'
  else:
    raise Exception("Unknown format: %s" % format)

  formatted_data = getattr(dataset(headers, data, encoding), format)

  if len(formatted_data) > XLS_SIZE_LIMIT:
    raise TooBigToDownloadException()

  resp = HttpResponse(formatted_data, mimetype=mimetype)
  resp['Content-Disposition'] = 'attachment; filename=%s.%s' % (name, format)
  return resp
