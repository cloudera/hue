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
#
# Handling of data export

import logging
import time

from django.http import HttpResponse

from desktop.lib.export_csvxls import CSVformatter, XLSformatter, TooBigToDownloadException

from beeswax import common


LOG = logging.getLogger(__name__)

_DATA_WAIT_SLEEP = 0.1                  # Sleep 0.1 sec before checking for data availability


def download(handle, format, db):
  """
  download(query_model, format) -> HttpResponse

  Retrieve the query result in the format specified. Return an HttpResponse object.
  """
  if format not in common.DL_FORMATS:
    LOG.error('Unknown download format "%s"' % (format,))
    return

  if format == 'csv':
    formatter = CSVformatter()
    mimetype = 'application/csv'
  elif format == 'xls':
    formatter = XLSformatter()
    mimetype = 'application/xls'

  gen = data_generator(handle, formatter, db)
  resp = HttpResponse(gen, mimetype=mimetype)
  resp['Content-Disposition'] = 'attachment; filename=query_result.%s' % (format,)

  return resp


def data_generator(handle, formatter, db):
  """
  data_generator(query_model, formatter) -> generator object

  Return a generator object for a csv. The first line is the column names.

  This is similar to export_csvxls.generator, but has
  one or two extra complexities.
  """
  _DATA_WAIT_SLEEP
  is_first_row = True

  yield formatter.init_doc()

  results = db.fetch(handle, start_over=is_first_row, rows=None)

  while results is not None:
    while not results.ready:   # For Beeswax
      time.sleep(_DATA_WAIT_SLEEP)
      results = db.fetch(handle, start_over=is_first_row, rows=None)

    # TODO Check for concurrent reading when HS2 supports start_row
    if is_first_row:
      is_first_row = False
      yield formatter.format_header(results.cols())

    for row in results.rows():
      try:
        yield formatter.format_row(row)
      except TooBigToDownloadException, ex:
        LOG.error(ex)

    if results.has_more:
      results = db.fetch(handle, start_over=is_first_row, rows=None)
    else:
      results = None

  yield formatter.fini_doc()
