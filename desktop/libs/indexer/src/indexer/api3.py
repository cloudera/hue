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

from beeswax.server import dbms
from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2
from notebook.connectors.base import get_api, Notebook

from indexer.controller import CollectionManagerController
from indexer.file_format import HiveFormat
from indexer.fields import Field
from indexer.smart_indexer import Indexer


LOG = logging.getLogger(__name__)


def _escape_white_space_characters(s, inverse = False):
  MAPPINGS = {
    "\n": "\\n",
    "\t": "\\t",
    "\r": "\\r",
    " ": "\\s"
  }

  to = 1 if inverse else 0
  from_ = 0 if inverse else 1

  for pair in MAPPINGS.iteritems():
    s = s.replace(pair[to], pair[from_]).encode('utf-8')

  return s


def _convert_format(format_dict, inverse=False):
  for field in format_dict:
    if isinstance(format_dict[field], basestring):
      format_dict[field] = _escape_white_space_characters(format_dict[field], inverse)


def guess_format(request):
  file_format = json.loads(request.POST.get('fileFormat', '{}'))

  if file_format['inputFormat'] == 'file':
    indexer = Indexer(request.user, request.fs)
    stream = request.fs.open(file_format["path"])
    format_ = indexer.guess_format({
      "file":{
        "stream": stream,
        "name": file_format['path']
        }
      })
    _convert_format(format_)
  elif file_format['inputFormat'] == 'table':
    db = dbms.get(request.user)
    table_metadata = db.get_table(database=file_format['databaseName'], table_name=file_format['tableName'])

    storage = dict([(delim['data_type'], delim['comment']) for delim in table_metadata.storage_details])
    if table_metadata.details['properties']['format'] == 'text':
      format_ = {"quoteChar": "\"", "recordSeparator": '\\n', "type": "csv", "hasHeader": False, "fieldSeparator": storage['serialization.format']}
    elif table_metadata.details['properties']['format'] == 'parquet':
      format_ = {"type": "parquet", "hasHeader": False,}
    else:
      raise PopupException('Hive table format %s is not supported.' % table_metadata.details['properties']['format'])
  elif file_format['inputFormat'] == 'query':
    format_ = {"quoteChar": "\"", "recordSeparator": "\\n", "type": "csv", "hasHeader": False, "fieldSeparator": "\u0001"}

  return JsonResponse(format_)


def guess_field_types(request):
  file_format = json.loads(request.POST.get('fileFormat', '{}'))

  if file_format['inputFormat'] == 'file':
    indexer = Indexer(request.user, request.fs)
    stream = request.fs.open(file_format["path"])
    _convert_format(file_format["format"], inverse=True)

    format_ = indexer.guess_field_types({
      "file": {
          "stream": stream,
          "name": file_format['path']
        },
      "format": file_format['format']
    })
  elif file_format['inputFormat'] == 'table':
    sample = get_api(request, {'type': 'hive'}).get_sample_data({'type': 'hive'}, database=file_format['databaseName'], table=file_format['tableName'])
    db = dbms.get(request.user)
    table_metadata = db.get_table(database=file_format['databaseName'], table_name=file_format['tableName'])

    format_ = {
        "sample": sample['rows'][:4],
        "columns": [
            Field(col.name, HiveFormat.FIELD_TYPE_TRANSLATE.get(col.type, 'string')).to_dict()
            for col in table_metadata.cols
        ]
    }
  elif file_format['inputFormat'] == 'query': # Only support open query history
    # TODO get schema from explain query, which is not possible
    notebook = Notebook(document=Document2.objects.get(id=file_format['query'])).get_data()
    snippet = notebook['snippets'][0]
    sample = get_api(request, snippet).fetch_result(notebook, snippet, 4, start_over=True)

    format_ = {
        "sample": sample['rows'][:4],
        "sample_cols": sample.meta,
        "columns": [
            Field(col['name'], HiveFormat.FIELD_TYPE_TRANSLATE.get(col['type'], 'string')).to_dict()
            for col in sample.meta
        ]
    }

  return JsonResponse(format_)


def index_file(request):
  file_format = json.loads(request.POST.get('fileFormat', '{}'))
  _convert_format(file_format["format"], inverse=True)
  collection_name = file_format["name"]

  job_handle = _index(request, file_format, collection_name)
  return JsonResponse(job_handle)


def _index(request, file_format, collection_name, query=None):
  indexer = Indexer(request.user, request.fs)

  unique_field = indexer.get_unique_field(file_format)
  is_unique_generated = indexer.is_unique_generated(file_format)

  schema_fields = indexer.get_kept_field_list(file_format['columns'])
  if is_unique_generated:
    schema_fields += [{"name": unique_field, "type": "string"}]

  morphline = indexer.generate_morphline_config(collection_name, file_format, unique_field)

  collection_manager = CollectionManagerController(request.user)
  if not collection_manager.collection_exists(collection_name):
    collection_manager.create_collection(collection_name, schema_fields, unique_key_field=unique_field)

  if file_format['inputFormat'] == 'table':
    db = dbms.get(request.user)
    table_metadata = db.get_table(database=file_format['databaseName'], table_name=file_format['tableName'])
    input_path = table_metadata.path_location
  elif file_format['inputFormat'] == 'file':
    input_path = '${nameNode}%s' % file_format["path"]
  else:
    input_path = None

  return indexer.run_morphline(request, collection_name, morphline, input_path, query)
