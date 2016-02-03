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
import math
import numbers
import uuid

from django.utils.html import escape

from desktop.lib.i18n import smart_unicode

from notebook.connectors.base import Notebook


# Materialize and HTML escape results
def escape_rows(rows, nulls_only=False):
  data = []

  for row in rows:
    escaped_row = []
    for field in row:
      if isinstance(field, numbers.Number):
        if math.isnan(field) or math.isinf(field):
          escaped_field = json.dumps(field)
        else:
          escaped_field = field
      elif field is None:
        escaped_field = 'NULL'
      else:
        escaped_field = smart_unicode(field, errors='replace') # Prevent error when getting back non utf8 like charset=iso-8859-1
        if not nulls_only:
          escaped_field = escape(escaped_field).replace(' ', '&nbsp;')
      escaped_row.append(escaped_field)
    data.append(escaped_row)

  return data


def make_notebook(name='Browse', description='', editor_type='hive', statement='', status='ready', files=None, functions=None, settings=None):
  editor = Notebook()

  editor.data = json.dumps({
    'name': name,
    'description': description,
    'sessions': [
      {
         'type': editor_type,
         'properties': [

         ],
         'id': None
      }
    ],
    'selectedSnippet': editor_type,
    'type': 'query-%s' % editor_type,

    'snippets': [
      {
         'status': status,
         'id': str(uuid.uuid4()),
         'statement_raw': statement,
         'statement': statement,
         'type': editor_type,
         'properties': {
            'files': [] if files is None else files,
            'functions': [] if functions is None else functions,
            'settings': [] if settings is None else settings
         },
         'name': name,
         'database': 'default',
         'result': {}
      }
    ]
  })
  
  return editor

