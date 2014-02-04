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

from desktop.lib import export_csvxls

from beeswax import common, conf


LOG = logging.getLogger(__name__)

_DATA_WAIT_SLEEP = 0.1                  # Sleep 0.1 sec before checking for data availability
FETCH_ROWS = 100000

def download(handle, format, db):
  """
  download(query_model, format) -> HttpResponse

  Retrieve the query result in the format specified. Return an HttpResponse object.
  """
  if format not in common.DL_FORMATS:
    LOG.error('Unknown download format "%s"' % (format,))
    return

  data = HS2DataAdapter(handle, format, db, conf.DOWNLOAD_ROW_LIMIT.get())
  return export_csvxls.make_response(data[0], data[1:], format, 'query_result')


def HS2DataAdapter(handle, format, db, max_rows=0):
  """
  HS2DataAdapter(query_model, format, db) -> 2D array of data.

  First line should be the headers.
  """
  results = db.fetch(handle, start_over=True, rows=FETCH_ROWS)
  while not results.ready:   # For Beeswax
    time.sleep(_DATA_WAIT_SLEEP)
    results = db.fetch(handle, start_over=True, rows=FETCH_ROWS)

  data = [results.cols()]

  while results is not None:
    for row in results.rows():
      if max_rows > -1 and len(data) > max_rows:
        break
      data.append(row)

    if max_rows > -1 and len(data) > max_rows:
      break

    if results.has_more:
      results = db.fetch(handle, start_over=False, rows=FETCH_ROWS)
    else:
      results = None

  return data
