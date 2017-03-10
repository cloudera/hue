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
import re
import uuid

from django.utils.html import escape

from desktop.lib.i18n import smart_unicode
from desktop.models import DOC2_NAME_INVALID_CHARS

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


def make_notebook(name='Browse', description='', editor_type='hive', statement='', status='ready',
                  files=None, functions=None, settings=None, is_saved=False, database='default', snippet_properties=None, batch_submit=False,
                  on_success_url=None, skip_historify=False, is_task=False):
  '''
  skip_historify: do not add the task to the query history. e.g. SQL Dashboard
  isManaged: true when being a managed by Hue operation (include_managed=True in document), e.g. exporting query result, dropping some tables
  '''
  from notebook.connectors.hiveserver2 import HS2Api

  editor = Notebook()
  if snippet_properties is None:
    snippet_properties = {}

  if editor_type == 'hive':
    sessions_properties = HS2Api.get_properties(editor_type)
    if files is not None:
      _update_property_value(sessions_properties, 'files', files)

    if functions is not None:
      _update_property_value(sessions_properties, 'functions', functions)

    if settings is not None:
      _update_property_value(sessions_properties, 'settings', settings)
  elif editor_type == 'impala':
    sessions_properties = HS2Api.get_properties(editor_type)
    if settings is not None:
      _update_property_value(sessions_properties, 'files', files)
  elif editor_type == 'java':
    sessions_properties = [] # Java options
  else:
    sessions_properties = []

  data = {
    'name': name,
    'uuid': str(uuid.uuid4()),
    'description': description,
    'sessions': [
      {
         'type': editor_type,
         'properties': sessions_properties,
         'id': None
      }
    ],
    'selectedSnippet': editor_type,
    'type': 'query-%s' % editor_type,
    'showHistory': True,
    'isSaved': is_saved,
    'onSuccessUrl': on_success_url,
    'skipHistorify': skip_historify,
    'isManaged': is_task,
    'snippets': [
      {
         'status': status,
         'id': str(uuid.uuid4()),
         'statement_raw': statement,
         'statement': statement,
         'type': editor_type,
         'wasBatchExecuted': batch_submit,
         'properties': {
            'files': [] if files is None else files,
            'functions': [] if functions is None else functions,
            'settings': [] if settings is None else settings
         },
         'name': name,
         'database': database,
         'result': {'handle':{}},
         'variables': []
      }
    ]
  }

  if snippet_properties:
    data['snippets'][0]['properties'].update(snippet_properties)

  editor.data = json.dumps(data)

  return editor


def make_notebook2(name='Browse', description='', is_saved=False, snippets=None):

  from notebook.connectors.hiveserver2 import HS2Api

  editor = Notebook()

  _snippets = []

  for snippet in snippets:
    default_properties = {
        'files': [],
        'functions': [],
        'settings': []
    }

    default_properties.update(snippet['properties'])
    snippet['properties'] = default_properties

    _snippets.append(snippet)

  data = {
    'name': name,
    'uuid': str(uuid.uuid4()),
    'type': 'notebook',
    'description': description,
    'sessions': [
      {
         'type': _snippet['type'],
         'properties': HS2Api.get_properties(snippet['type']),
         'id': None
      } for _snippet in _snippets # Non unique types currently
    ],
    'selectedSnippet': _snippets[0]['type'],
    'showHistory': False,
    'isSaved': is_saved,
    'snippets': [
      {
         'status': _snippet.get('status', 'ready'),
         'id': str(uuid.uuid4()),
         'statement_raw': _snippet.get('statement', ''),
         'statement': _snippet.get('statement', ''),
         'type': _snippet.get('type'),
         'properties': _snippet['properties'],
         'name': name,
         'database': _snippet.get('database'),
         'result': {'handle':{}},
         'variables': []
      } for _snippet in _snippets
    ]
  }

  editor.data = json.dumps(data)

  return editor


def import_saved_beeswax_query(bquery):
  design = bquery.get_design()

  return make_notebook(
      name=re.sub(DOC2_NAME_INVALID_CHARS, '', bquery.name),
      description=bquery.desc,
      editor_type=_convert_type(bquery.type, bquery.data),
      statement=design.hql_query,
      status='ready',
      files=design.file_resources,
      functions=design.functions,
      settings=design.settings,
      is_saved=True,
      database=design.database
  )


def _convert_type(btype, bdata):
  from beeswax.models import HQL, IMPALA, RDBMS, SPARK

  if btype == HQL:
    return 'hive'
  elif btype == IMPALA:
    return 'impala'
  elif btype == RDBMS:
    data = json.loads(bdata)
    return data['query']['server']
  elif btype == SPARK: # We should not import
    return 'spark'
  else:
    return 'hive'


def _update_property_value(properties, key, value):
  """
  Update property dict in list of properties where prop has "key": key, set "value": value
  """
  for prop in properties:
    if prop['key'] == key:
      prop.update({'value': value})
