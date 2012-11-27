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
import cStringIO
import csv
import logging

from django.http import HttpResponse
from django.utils.encoding import smart_str
from desktop.lib import i18n

LOG = logging.getLogger(__name__)
XLS_SIZE_LIMIT = 200 * 1024 * 1024      # 200MB

class TooBigToDownloadException(Exception):
  pass

class Formatter(object):
  """
  The interface for a helper class to write formatted data.
  """
  def init_doc(self):
    """
    init_doc() -> initial data to appear before the header
    """
    raise NotImplementedError()

  def format_header(self, header):
    """
    format_header(header) -> line
    header should be a list of column names
    """
    raise NotImplementedError()

  def format_row(self, row):
    """
    format_row(row) -> line
    row should be a list of datum

    May raise TooBigToDownloadException. In which case fini_doc() will still be
    invoked to make the partial results available to the user. Implementation may
    want to signify that the results are partial in the doc.
    """
    raise NotImplementedError()

  def fini_doc(self):
    """
    fini_doc() -> final data to appear after all rows
    """
    raise NotImplementedError()

def _force_string(x):
  """
  Forces argument to be some form of string.

  We are conservative about string/unicode issues, and only
  do the conversion if it's not already a string of some form.
  """
  if isinstance(x, basestring):
    return x
  else:
    return str(x)

def generator(header, data, formatter):
  yield formatter.init_doc()
  yield formatter.format_header(header)
  for datum in data:
    try:
      yield formatter.format_row(map(_force_string, datum))
    except TooBigToDownloadException, ex:
      # Truncate the results
      LOG.exception(ex)
      pass
  yield formatter.fini_doc()

def make_response(header, data, format, name, encoding=None):
  """
  @param header List of strings to form the header
  @param data An iterator of rows, where every row is a list of strings
  @param format Either "csv" or "xls"
  @param name Base name for output file
  @param encoding Unicode encoding for data
  """
  if format == 'csv':
    formatter = CSVformatter(encoding)
    mimetype = 'application/csv'
  elif format == 'xls':
    formatter = CSVformatter(encoding)
    mimetype = 'application/xls'
  else:
    raise Exception("Unknown format: %s" % (format,))

  resp = HttpResponse(generator(header, data, formatter), mimetype=mimetype)
  resp['Content-Disposition'] = 'attachment; filename=%s.%s' % (name, format)
  return resp

class CSVformatter(Formatter):
  def __init__(self, encoding=None):
    super(CSVformatter, self).__init__()
    dialect = csv.excel()
    dialect.quoting = csv.QUOTE_ALL
    self._encoding = encoding or i18n.get_site_encoding()
    self._csv_writer = csv.writer(self, dialect=dialect)
    self._line = None

  def write(self, line):
    self._line = line

  def init_doc(self):
    return ""

  def format_header(self, header):
    return self.format_row(header)

  def format_row(self, row):
    # writerow will call our write() method
    row = [smart_str(cell, self._encoding, strings_only=True, errors='replace') for cell in row]
    self._csv_writer.writerow(row)
    return self._line

  def fini_doc(self):
    return ""
