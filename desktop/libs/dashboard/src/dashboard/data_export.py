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

from django.utils.encoding import smart_str

from desktop.lib import export_csvxls


LOG = logging.getLogger(__name__)
DL_FORMATS = [ 'csv', 'xls' ]


def download(results, format, collection, user_agent=None):
  """
  download(results, format) -> HttpResponse

  Transform the search result set to the specified format and download.
  """
  if format not in DL_FORMATS:
    LOG.error('Unknown download format "%s"' % format)
    return

  content_generator = SearchDataAdapter(results, format, collection)
  generator = export_csvxls.create_generator(content_generator, format)
  return export_csvxls.make_response(generator, format, 'query_result', user_agent=user_agent)


def SearchDataAdapter(results, format, collection):
  """
  SearchDataAdapter(results, format, db) -> headers, 2D array of data.
  """
  if results and results['response'] and results['response']['docs']:
    search_data = results['response']['docs']

    if collection['template']['fieldsSelected']:
      headers = collection['template']['fieldsSelected']
    else:
      headers = [field['name'] for field in collection['fields']]

    rows = []

    for data in search_data:
      row = []
      for column in headers:
        if column not in data:
          row.append("")
        elif isinstance(data[column], basestring) or isinstance(data[column], (int, long, float, complex)):
          row.append(data[column])
        elif isinstance(data[column], list): # Multivalue field
          row.append([smart_str(val, errors='replace') for val in data[column]])
        else:
          row.append(smart_str(data[column]))
      rows.append(row)
  else:
    rows = [[]]

  yield headers, rows
