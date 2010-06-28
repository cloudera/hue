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

from beeswax import common
from beeswax import db_utils
from beeswaxd.ttypes import QueryHandle

from desktop.lib.export_csvxls import CSVformatter, XLSformatter, TooBigToDownloadException


LOG = logging.getLogger(__name__)

_DATA_WAIT_SLEEP = 0.1                  # Sleep 0.1 sec before checking for data availability


def download(query_model, format):
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

  gen = data_generator(query_model, formatter)
  resp = HttpResponse(gen, mimetype=mimetype)
  resp['Content-Disposition'] = 'attachment; filename=query_result.%s' % (format,)
  return resp


def data_generator(query_model, formatter):
  """
  data_generator(query_model, formatter) -> generator object

  Return a generator object for a csv. The first line is the column names.

  This is similar to export_csvxls.generator, but has
  one or two extra complexities.
  """
  global _DATA_WAIT_SLEEP
  is_first_row = True
  next_row = 0
  results = None
  handle = QueryHandle(query_model.server_id, query_model.log_context)

  yield formatter.init_doc()

  while True:
    # Make sure that we have the next batch of ready results
    while results is None or not results.ready:
      results = db_utils.db_client().fetch(handle, start_over=is_first_row)
      if not results.ready:
        time.sleep(_DATA_WAIT_SLEEP)

    # Someone is reading the results concurrently. Abort.
    # But unfortunately, this current generator will produce incomplete data.
    if next_row != results.start_row:
      msg = 'Error: Potentially incomplete results as an error occur during data retrieval.'
      yield formatter.format_row([msg])
      err = ('Detected another client retrieving results for %s. '
             'Expect next row being %s and got %s. Aborting' %
             (query_model.server_id, next_row, results.start_row))
      LOG.error(err)
      raise RuntimeError(err)

    if is_first_row:
      is_first_row = False
      yield formatter.format_header(results.columns)
    else:
      for i, row in enumerate(results.data):
        # TODO(bc): Hive seems to always return tab delimited row data.
        # What if a cell has a tab?
        row = row.split('\t')
        try:
          yield formatter.format_row(row)
        except TooBigToDownloadException, ex:
          LOG.error(ex)
          # Exceeded limit. Stop.
          results.has_more = False
          break

      if results.has_more:
        next_row += len(results.data)
        results = None
      else:
        yield formatter.fini_doc()
        break
