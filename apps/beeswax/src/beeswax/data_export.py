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
FETCH_ROWS = 10


def download(handle, format, db):
  """
  download(query_model, format) -> HttpResponse

  Retrieve the query result in the format specified. Return an HttpResponse object.
  """
  if format not in common.DL_FORMATS:
    LOG.error('Unknown download format "%s"' % (format,))
    return

  data, has_more = HS2DataAdapter(handle, db, conf.DOWNLOAD_ROW_LIMIT.get())
  return export_csvxls.make_response(data[0], data[1:], format, 'query_result')


def upload(path, handle, user, db, fs):
  """
  upload(query_model, path, user, db, fs) -> None

  Retrieve the query result in the format specified and upload to hdfs.
  """
  has_more = True
  start_over = True

  fs.do_as_user(user.username, fs.create, path, overwrite=True)

  while has_more:
    data, has_more = HS2DataAdapter(handle, db, conf.DOWNLOAD_ROW_LIMIT.get(), start_over=start_over)
    dataset = export_csvxls.dataset(None, data[1:])
    fs.do_as_user(user.username, fs.append, path, dataset.csv)

    if start_over:
      start_over = False


def HS2DataAdapter(handle, db, max_rows=0, start_over=True):
  """
  HS2DataAdapter(query_model, db) -> 2D array of data.

  First line should be the headers.
  """
  fetch_rows = max_rows if max_rows > -1 else FETCH_ROWS

  results = db.fetch(handle, start_over=start_over, rows=fetch_rows)
  while not results.ready:
    time.sleep(_DATA_WAIT_SLEEP)
    results = db.fetch(handle, start_over=start_over, rows=fetch_rows)

  data = [results.cols()]

  while results is not None:
    for row in results.rows():
      if max_rows > -1 and len(data) > max_rows:
        break
      data.append(row)

    if max_rows > -1 and len(data) > max_rows:
      break

    if results.has_more:
      results = db.fetch(handle, start_over=False, rows=fetch_rows)
    else:
      results = None

  return data, results.has_more if results else False
