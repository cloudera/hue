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

from django.utils.encoding import smart_str

from desktop.lib import export_csvxls


LOG = logging.getLogger(__name__)
DL_FORMATS = [ 'csv', 'xls' ]


def download(api, session, cell, format, user_agent=None):
  if format not in DL_FORMATS:
    LOG.error('Unknown download format "%s"' % format)
    return

  content_generator = SparkDataAdapter(api, session, cell)
  generator = export_csvxls.create_generator(content_generator, format)
  return export_csvxls.make_response(generator, format, 'script_result', user_agent=user_agent)


def SparkDataAdapter(api, session, cell):
  response = api.fetch_data(session, cell)

  content = response['output']
  data = content['data']

  table = data['application/vnd.livy.table.v1+json']

  rows = table['data']
  headers = table['headers']

  yield headers, rows
