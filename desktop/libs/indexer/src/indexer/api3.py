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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib import django_mako
from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document2
from notebook.connectors.base import get_api, Notebook

from indexer.controller import CollectionManagerController
from indexer.file_format import HiveFormat
from indexer.fields import Field
from indexer.smart_indexer import Indexer
from notebook.models import make_notebook


LOG = logging.getLogger(__name__)

try:
  from beeswax.server import dbms
except ImportError, e:
  LOG.warn('Hive and HiveServer2 interfaces are not enabled')


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
      "file": {
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


def importer_submit(request):
  source = json.loads(request.POST.get('source', '{}'))
  destination = json.loads(request.POST.get('destination', '{}'))

  if destination['ouputFormat'] == 'index':
    _convert_format(source["format"], inverse=True)
    collection_name = source["name"]
    source['columns'] = destination['columns']
    job_handle = _index(request, source, collection_name)
  else:
    job_handle = _create_table(request, source, destination)

  return JsonResponse(job_handle)


def _create_table(request, source, destination):
  # Create table from File  
  delim = ','
  table_name = final_table_name = destination['name']
  comment = 'comment'
  external = True
  load_data = True
  skip_header = True
  database = 'default'
  path = source['path']
  table_format = 'parquet' #'text'

  file_format = 'TextFile'
  sql = ''
  
  # if external and non text and load_data, both bath !=
  
  
  if table_format == 'parquet':
    table_name, final_table_name = 'hue__tmp_%s' % table_name, table_name # Or tmp table?
    
  if external and not request.fs.isdir(path):
    path = request.fs.split(path)[0]
    # If dir not empty, create data dir %(filename)_table and move file there...
    
    # Guess should accept a directory too

  sql += django_mako.render_to_string("gen/create_table_statement.mako", {
      'table': {
          'name': table_name,
          'comment': comment,
          'row_format': 'Delimited',
          'field_terminator': delim,
          'file_format': file_format,
          'external': external,
          'path': path, 
          'skip_header': skip_header
       },
      'columns': destination['columns'],
      'partition_columns': [],
      'database': database
    }
  )

  if not external and load_data:
    sql += "\n\nLOAD DATA INPATH '%s' INTO TABLE `%s`.`%s`;" % (path, database, table_name)

  if table_format == 'parquet':
    sql += '\n\nCREATE TABLE `%(database)s`.`%(final_table_name)s` STORED AS %(file_format)s AS SELECT * FROM `%(database)s`.`%(table_name)s`;' % {
        'database': database,
        'final_table_name': final_table_name,
        'table_name': table_name,
        'file_format': table_format
    }
    sql += '\n\nDROP TABLE IF EXISTS `%(database)s`.`%(table_name)s`;' % {'database': database, 'table_name': table_name}

  try:
    editor_type = 'hive'
    # on_success_url = reverse('metastore:describe_table', kwargs={'database': database, 'table': table_name})
    notebook = make_notebook(name='Execute and watch', editor_type=editor_type, statement=sql, status='ready', database=database)

    return notebook.execute(request, batch=False)
  except Exception, e:
    raise PopupException(_('The table could not be created.'), detail=e.message)


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
