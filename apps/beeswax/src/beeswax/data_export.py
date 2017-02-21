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

import json
import logging

from django.utils.translation import ugettext as _

from desktop.lib import export_csvxls
from beeswax import common, conf


LOG = logging.getLogger(__name__)


FETCH_SIZE = 1000
DOWNLOAD_COOKIE_AGE = 1800 # 30 minutes


def download(handle, format, db, id=None, file_name='query_result'):
  """
  download(query_model, format) -> HttpResponse

  Retrieve the query result in the format specified. Return an HttpResponse object.
  """
  if format not in common.DL_FORMATS:
    LOG.error('Unknown download format "%s"' % (format,))
    return

  max_rows = conf.DOWNLOAD_ROW_LIMIT.get()

  content_generator = HS2DataAdapter(handle, db, max_rows=max_rows, start_over=True)
  generator = export_csvxls.create_generator(content_generator, format)

  resp = export_csvxls.make_response(generator, format, file_name)

  if id:
    resp.set_cookie(
      'download-%s' % id,
      json.dumps({
        'truncated': content_generator.is_truncated,
        'row_counter': content_generator.row_counter
      }),
      max_age=DOWNLOAD_COOKIE_AGE
    )

  return resp


def upload(path, handle, user, db, fs, max_rows=-1):
  """
  upload(query_model, path, user, db, fs) -> None

  Retrieve the query result in the format specified and upload to hdfs.
  """
  if fs.do_as_user(user.username, fs.exists, path):
    raise Exception(_("%s already exists.") % path)
  else:
    fs.do_as_user(user.username, fs.create, path)

  content_generator = HS2DataAdapter(handle, db, max_rows=max_rows, start_over=True)
  for header, data in content_generator:
    dataset = export_csvxls.dataset(None, data)
    fs.do_as_user(user.username, fs.append, path, dataset.csv)


class HS2DataAdapter:

  def __init__(self, handle, db, max_rows=-1, start_over=True):
    self.handle = handle
    self.db = db
    self.max_rows = max_rows
    self.start_over = start_over
    self.fetch_size = FETCH_SIZE
    self.limit_rows = max_rows > -1

    self.first_fetched = True
    self.headers = None
    self.num_cols = None
    self.row_counter = 1
    self.is_truncated = False
    self.has_more = True

  def __iter__(self):
    return self

  def next(self):
    results = self.db.fetch(self.handle, start_over=self.start_over, rows=self.fetch_size)

    if self.first_fetched:
      self.first_fetched = False
      self.start_over = False
      self.headers = results.cols()
      self.num_cols = len(self.headers)

      # For result sets with high num of columns, fetch in smaller batches to avoid serialization cost
      if self.num_cols > 100:
        LOG.warn('The query results contain %d columns and may take long time to download, reducing fetch size to 100.' % self.num_cols)
        self.fetch_size = 100

    if self.has_more and not self.is_truncated:
      self.has_more = results.has_more
      data = []

      for row in results.rows():
        self.row_counter += 1
        if self.limit_rows and self.row_counter > self.max_rows:
          LOG.warn('The query results exceeded the maximum row limit of %d and has been truncated to first %d rows.' % (self.max_rows, self.row_counter))
          self.is_truncated = True
          break
        data.append(row)

      return self.headers, data
    else:
      raise StopIteration
