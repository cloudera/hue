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

import logging
import time

from django.utils.translation import ugettext as _

from desktop.lib import export_csvxls

from beeswax import common, conf


LOG = logging.getLogger(__name__)

_DATA_WAIT_SLEEP = 0.1                  # Sleep 0.1 sec before checking for data availability
FETCH_SIZE = 1000


def download(handle, format, db):
  """
  download(query_model, format) -> HttpResponse

  Retrieve the query result in the format specified. Return an HttpResponse object.
  """
  if format not in common.DL_FORMATS:
    LOG.error('Unknown download format "%s"' % (format,))
    return

  max_cells = conf.DOWNLOAD_CELL_LIMIT.get()

  content_generator = HS2DataAdapter(handle, db, max_cells=max_cells, start_over=True)
  generator = export_csvxls.create_generator(content_generator, format)
  return export_csvxls.make_response(generator, format, 'query_result')


def upload(path, handle, user, db, fs):
  """
  upload(query_model, path, user, db, fs) -> None

  Retrieve the query result in the format specified and upload to hdfs.
  """
  if fs.do_as_user(user.username, fs.exists, path):
    raise Exception(_("%s already exists.") % path)
  else:
    fs.do_as_user(user.username, fs.create, path)

  content_generator = HS2DataAdapter(handle, db, max_cells=-1, start_over=True)
  for header, data in content_generator:
    dataset = export_csvxls.dataset(None, data)
    fs.do_as_user(user.username, fs.append, path, dataset.csv)


def HS2DataAdapter(handle, db, max_cells=-1, start_over=True):
  """
  HS2DataAdapter(query_model, db) -> headers, 2D array of data.
  """
  results = db.fetch(handle, start_over=start_over, rows=FETCH_SIZE)

  while not results.ready:
    time.sleep(_DATA_WAIT_SLEEP)
    results = db.fetch(handle, start_over=start_over, rows=FETCH_SIZE)

  headers = results.cols()
  num_cols = len(headers)

  # For result sets with high num of columns, fetch in smaller batches to avoid serialization cost
  if num_cols > 100:
    LOG.warn('The query results contain %d columns and may take an extremely long time to download, will reduce fetch size to 100.' % num_cols)
    fetch_size = 100
  else:
    fetch_size = FETCH_SIZE

  row_ctr = 1
  limit_cells = max_cells > -1

  while results is not None:
    data = []
    for row in results.rows():
      row_ctr += 1
      if limit_cells and (row_ctr * num_cols) > max_cells:
        LOG.warn('The query results exceeded the maximum cell limit of %d. Data has been truncated to first %d rows.' % (max_cells, row_ctr))
        break
      data.append(row)

    yield headers, data

    if limit_cells and (row_ctr * num_cols) > max_cells:
      break

    if results.has_more:
      results = db.fetch(handle, start_over=False, rows=fetch_size)
    else:
      results = None
