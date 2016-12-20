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
    collection_name = destination["name"]
    source['columns'] = destination['columns']
    job_handle = _index(request, source, collection_name)
  else:
    job_handle = _create_table(request, source, destination)

  return JsonResponse(job_handle)


def _create_table(request, source, destination):
  return _create_table_from_a_file(request, source, destination)


def _create_table_from_a_file(request, source, destination):
  table_name = final_table_name = destination['name']
  table_format = destination['tableFormat']

  database = destination['database']
  columns = destination['columns']
  partition_columns = destination['partitionColumns']

  comment = destination['description']

  source_path = source['path']
  external = not destination['useDefaultLocation']
  external_path = not destination['nonDefaultLocation']

  load_data = destination['importData']
  skip_header = destination['hasHeader']

  primary_keys = destination['primaryKeys']

  if destination['useCustomDelimiters']:
    field_delimiter = destination['customFieldDelimiter']
    collection_delimiter = destination['customCollectionDelimiter']
    map_delimiter = destination['customMapDelimiter']
    regexp_delimiter = destination['customRegexp']
  else:
    field_delimiter = ','
    collection_delimiter = r'\\002'
    map_delimiter = r'\\003'
    regexp_delimiter = '.*'


  file_format = 'TextFile'
  extra_create_properties = ''
  sql = ''

  if load_data:
    if table_format in ('parquet', 'kudu'):
      table_name, final_table_name = 'hue__tmp_%s' % table_name, table_name

  if external or load_data and table_format in ('parquet', 'kudu'):
    if not request.fs.isdir(external_path): # File selected
      external_path = request.fs.split(external_path)[0]
      if len(request.fs.listdir(external_path)) != 1:
        external_path = external_path + '_table' # If dir not just the file, create data dir and move file there.
        request.fs.mkdir(source_path + '_table')
        request.fs.rename(source_path, external_path)

  
  sql += '\n\nDROP TABLE IF EXISTS `%(database)s`.`%(table_name)s`;\n' % {
      'database': database,
      'table_name': table_name
  }

  sql += django_mako.render_to_string("gen/create_table_statement.mako", {
      'table': {
          'name': table_name,
          'comment': comment,
          'row_format': 'Delimited',
          'field_terminator': field_delimiter,
          'file_format': file_format,
          'external': external or load_data and table_format in ('parquet', 'kudu'),
          'path': external_path,
          'skip_header': skip_header,
          'primary_keys': primary_keys if table_format == 'kudu' and not load_data else []
       },
      'columns': columns,
      'partition_columns': [],
      'database': database
    }
  )

  if table_format == 'text' and not external and load_data:
    sql += "\n\nLOAD DATA INPATH '%s' INTO TABLE `%s`.`%s`;" % (source_path, database, table_name)

  if table_format in ('parquet', 'kudu'):
    file_format = table_format
    if table_format == 'kudu':
      columns_list = ['`%s`' % col for col in primary_keys + [col['name'] for col in destination['columns'] if col['name'] not in primary_keys]]
      extra_create_properties = """PRIMARY KEY (%(primary_keys)s)
      DISTRIBUTE BY HASH INTO 16 BUCKETS
      STORED AS %(file_format)s
      TBLPROPERTIES(
      'kudu.num_tablet_replicas' = '1'
      )""" % {
        'file_format': file_format,
        'primary_keys': ', '.join(primary_keys)
      }
    else:
      columns_list = ['*']
    sql += '''\n\nCREATE TABLE `%(database)s`.`%(final_table_name)s`
      %(extra_create_properties)s
      AS SELECT %(columns_list)s
      FROM `%(database)s`.`%(table_name)s`;''' % {
        'database': database,
        'final_table_name': final_table_name,
        'table_name': table_name,
        'extra_create_properties': extra_create_properties,
        'columns_list': ', '.join(columns_list),
    }
    sql += '\n\nDROP TABLE IF EXISTS `%(database)s`.`%(table_name)s`;\n' % {
        'database': database,
        'table_name': table_name
    }

  try:
    editor_type = 'impala' if table_format == 'kudu' else 'hive'
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
