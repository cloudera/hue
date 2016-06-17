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

  content_generator = HS2DataAdapter(handle, db, conf.DOWNLOAD_ROW_LIMIT.get())
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

  content_generator = HS2DataAdapter(handle, db, -1, start_over=True)
  for header, data in content_generator:
    dataset = export_csvxls.dataset(None, data)
    fs.do_as_user(user.username, fs.append, path, dataset.csv)


def HS2DataAdapter(handle, db, max_rows=0, start_over=True):
  """
  HS2DataAdapter(query_model, db) -> headers, 2D array of data.
  """

  results = db.fetch(handle, start_over=start_over, rows=FETCH_SIZE)

  while not results.ready:
    time.sleep(_DATA_WAIT_SLEEP)
    results = db.fetch(handle, start_over=start_over, rows=FETCH_SIZE)

  headers = results.cols()

  num_rows_seen = 0
  limit_rows = max_rows > -1

  while results is not None:
    data = []
    for row in results.rows():
      num_rows_seen += 1
      if limit_rows and num_rows_seen > max_rows:
        break
      data.append(row)

    yield headers, data

    if limit_rows and num_rows_seen > max_rows:
      break

    if results.has_more:
      results = db.fetch(handle, start_over=False, rows=FETCH_SIZE)
    else:
      results = None
