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

import chardet
import json
import logging
import urllib

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib import django_mako
from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode
from desktop.models import Document2
from librdbms.server import dbms as rdbms
from notebook.connectors.base import get_api, Notebook
from notebook.decorators import api_error_handler
from notebook.models import make_notebook, MockedDjangoRequest, escape_rows

from indexer.controller import CollectionManagerController
from indexer.file_format import HiveFormat
from indexer.fields import Field
from indexer.indexers.envelope import EnvelopeIndexer
from indexer.indexers.morphline import MorphlineIndexer
from indexer.indexers.rdbms import RdbmsIndexer, run_sqoop
from indexer.indexers.sql import SQLIndexer
from indexer.solr_client import SolrClient, MAX_UPLOAD_SIZE


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


@api_error_handler
def guess_format(request):
  file_format = json.loads(request.POST.get('fileFormat', '{}'))

  if file_format['inputFormat'] == 'file':
    path = urllib.unquote(file_format["path"])
    indexer = MorphlineIndexer(request.user, request.fs)
    if not request.fs.isfile(path):
      raise PopupException(_('Path %(path)s is not a file') % file_format)

    stream = request.fs.open(path)
    format_ = indexer.guess_format({
      "file": {
        "stream": stream,
        "name": path
      }
    })
    _convert_format(format_)
  elif file_format['inputFormat'] == 'table':
    db = dbms.get(request.user)
    try:
      table_metadata = db.get_table(database=file_format['databaseName'], table_name=file_format['tableName'])
    except Exception, e:
      raise PopupException(e.message if hasattr(e, 'message') and e.message else e)
    storage = {}
    for delim in table_metadata.storage_details:
      if delim['data_type']:
        if '=' in delim['data_type']:
          key, val = delim['data_type'].split('=', 1)
          storage[key] = val
        else:
          storage[delim['data_type']] = delim['comment']
    if table_metadata.details['properties']['format'] == 'text':
      format_ = {"quoteChar": "\"", "recordSeparator": '\\n', "type": "csv", "hasHeader": False, "fieldSeparator": storage.get('field.delim', ',')}
    elif table_metadata.details['properties']['format'] == 'parquet':
      format_ = {"type": "parquet", "hasHeader": False,}
    else:
      raise PopupException('Hive table format %s is not supported.' % table_metadata.details['properties']['format'])
  elif file_format['inputFormat'] == 'query':
    format_ = {"quoteChar": "\"", "recordSeparator": "\\n", "type": "csv", "hasHeader": False, "fieldSeparator": "\u0001"}
  elif file_format['inputFormat'] == 'rdbms':
    format_ = RdbmsIndexer(request.user, file_format['rdbmsType']).guess_format()

  format_['status'] = 0
  return JsonResponse(format_)


def guess_field_types(request):
  file_format = json.loads(request.POST.get('fileFormat', '{}'))

  if file_format['inputFormat'] == 'file':
    indexer = MorphlineIndexer(request.user, request.fs)
    path = urllib.unquote(file_format["path"])
    stream = request.fs.open(path)
    encoding = chardet.detect(stream.read(10000)).get('encoding')
    stream.seek(0)
    _convert_format(file_format["format"], inverse=True)

    format_ = indexer.guess_field_types({
      "file": {
          "stream": stream,
          "name": path
        },
      "format": file_format['format']
    })

    # Note: Would also need to set charset to table (only supported in Hive)
    if 'sample' in format_:
      format_['sample'] = escape_rows(format_['sample'], nulls_only=True, encoding=encoding)
    for col in format_['columns']:
      col['name'] = smart_unicode(col['name'], errors='replace', encoding=encoding)

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
  elif file_format['inputFormat'] == 'query':
    query_id = file_format['query']['id'] if file_format['query'].get('id') else file_format['query']

    notebook = Notebook(document=Document2.objects.document(user=request.user, doc_id=query_id)).get_data()
    snippet = notebook['snippets'][0]
    db = get_api(request, snippet)

    if file_format.get('sampleCols'):
      columns = file_format.get('sampleCols')
      sample = file_format.get('sample')
    else:
      snippet['query'] = snippet['statement']
      try:
        sample = db.fetch_result(notebook, snippet, 4, start_over=True)['rows'][:4]
      except Exception, e:
        LOG.warn('Skipping sample data as query handle might be expired: %s' % e)
        sample = [[], [], [], [], []]
      columns = db.autocomplete(snippet=snippet, database='', table='')
      columns = [
          Field(col['name'], HiveFormat.FIELD_TYPE_TRANSLATE.get(col['type'], 'string')).to_dict()
          for col in columns['extended_columns']
      ]
    format_ = {
        "sample": sample,
        "columns": columns,
    }
  elif file_format['inputFormat'] == 'rdbms':
    query_server = rdbms.get_query_server_config(server=file_format['rdbmsType'])
    db = rdbms.get(request.user, query_server=query_server)
    sample = RdbmsIndexer(request.user, file_format['rdbmsType']).get_sample_data(mode=file_format['rdbmsMode'], database=file_format['rdbmsDatabaseName'], table=file_format['rdbmsTableName'])
    table_metadata = db.get_columns(file_format['rdbmsDatabaseName'], file_format['rdbmsTableName'], names_only=False)

    format_ = {
        "sample": list(sample['rows'])[:4],
        "columns": [
            Field(col['name'], HiveFormat.FIELD_TYPE_TRANSLATE.get(col['type'], 'string')).to_dict()
            for col in table_metadata
        ]
    }
  elif file_format['inputFormat'] == 'kafka':
    # Mocked currently
    format_ = {"sample": [["0", "US", "This tremendous 100% varietal wine hails from Oakville and was aged over three years in oak. Juicy red-cherry fruit and a compelling hint of caramel greet the palate, framed by elegant, fine tannins and a subtle minty tone in the background. Balanced and rewarding from start to finish, it has years ahead of it to develop further nuance. Enjoy 2022\u20132030.", "Martha's Vineyard", "96", "235.0", "California", "Napa Valley", "Napa", "Cabernet Sauvignon", "Heitz"], ["1", "Spain", "Ripe aromas of fig, blackberry and cassis are softened and sweetened by a slathering of oaky chocolate and vanilla. This is full, layered, intense and cushioned on the palate, with rich flavors of chocolaty black fruits and baking spices. A toasty, everlasting finish is heady but ideally balanced. Drink through 2023.", "Carodorum Selecci\u00f3n Especial Reserva", "96", "110.0", "Northern Spain", "Toro", "", "Tinta de Toro", "Bodega Carmen Rodr\u00edguez"], ["2", "US", "Mac Watson honors the memory of a wine once made by his mother in this tremendously delicious, balanced and complex botrytised white. Dark gold in color, it layers toasted hazelnut, pear compote and orange peel flavors, reveling in the succulence of its 122 g/L of residual sugar.", "Special Selected Late Harvest", "96", "90.0", "California", "Knights Valley", "Sonoma", "Sauvignon Blanc", "Macauley"], ["3", "US", "This spent 20 months in 30% new French oak, and incorporates fruit from Ponzi's Aurora, Abetina and Madrona vineyards, among others. Aromatic, dense and toasty, it deftly blends aromas and flavors of toast, cigar box, blackberry, black cherry, coffee and graphite. Tannins are polished to a fine sheen, and frame a finish loaded with dark chocolate and espresso. Drink now through 2032.", "Reserve", "96", "65.0", "Oregon", "Willamette Valley", "Willamette Valley", "Pinot Noir", "Ponzi"], ["4", "France", "This is the top wine from La B\u00e9gude, named after the highest point in the vineyard at 1200 feet. It has structure, density and considerable acidity that is still calming down. With 18 months in wood, the wine has developing an extra richness and concentration. Produced by the Tari family, formerly of Ch\u00e2teau Giscours in Margaux, it is a wine made for aging. Drink from 2020.", "La Br\u00fblade", "95", "66.0", "Provence", "Bandol", "", "Provence red blend", "Domaine de la B\u00e9gude"]], "columns": [{"operations": [], "comment": "", "nested": [], "name": "id", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "long", "showProperties": False, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "country", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "string", "showProperties": False, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "description", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "text_general", "showProperties": False, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "designation", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "string", "showProperties": False, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "points", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "long", "showProperties": False, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "price", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "double", "showProperties": False, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "province", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "string", "showProperties": False, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "region_1", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "string", "showProperties": False, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "region_2", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "string", "showProperties": False, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "variety", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "string", "showProperties": False, "scale": 0}, {"operations": [], "comment": "", "nested": [], "name": "winery", "level": 0, "keyType": "string", "required": False, "precision": 10, "keep": True, "isPartition": False, "length": 100, "partitionValue": "", "multiValued": False, "unique": False, "type": "string", "showProperties": False, "scale": 0}]}

  return JsonResponse(format_)


@api_error_handler
def importer_submit(request):
  source = json.loads(request.POST.get('source', '{}'))
  outputFormat = json.loads(request.POST.get('destination', '{}'))['outputFormat']
  destination = json.loads(request.POST.get('destination', '{}'))
  destination['ouputFormat'] = outputFormat # Workaround a very weird bug
  start_time = json.loads(request.POST.get('start_time', '-1'))

  if source['inputFormat'] == 'file':
    if source['path']:
      path = urllib.unquote(source['path'])
      source['path'] = request.fs.netnormpath(path)
  if destination['ouputFormat'] in ('database', 'table'):
    destination['nonDefaultLocation'] = request.fs.netnormpath(destination['nonDefaultLocation']) if destination['nonDefaultLocation'] else destination['nonDefaultLocation']

  if destination['ouputFormat'] == 'index':
    source['columns'] = destination['columns']
    index_name = destination["name"]

    if destination['indexerRunJob']:
      _convert_format(source["format"], inverse=True)
      job_handle = _large_indexing(request, source, index_name, start_time=start_time, lib_path=destination['indexerJobLibPath'])
    else:
      client = SolrClient(request.user)
      job_handle = _small_indexing(request.user, request.fs, client, source, destination, index_name)
  elif destination['ouputFormat'] == 'database':
    job_handle = _create_database(request, source, destination, start_time)
  elif source['inputFormat'] == 'rdbms':
    if destination['outputFormat'] in ('file', 'table', 'hbase'):
      job_handle = run_sqoop(request, source, destination, start_time)
  elif source['inputFormat'] == 'kafka':
    job_handle = _envelope_job(request, source, destination['name'], start_time=start_time, lib_path=destination['indexerJobLibPath'])
  else:
    job_handle = _create_table(request, source, destination, start_time)

  request.audit = {
    'operation': 'EXPORT',
    'operationText': 'User %(username)s exported %(inputFormat)s to %(ouputFormat)s: %(name)s' % {
        'username': request.user.username,
        'inputFormat': source['inputFormat'],
        'ouputFormat': destination['ouputFormat'],
        'name': destination['name'],
    },
    'allowed': True
  }

  return JsonResponse(job_handle)


def _small_indexing(user, fs, client, source, destination, index_name):
  unique_key_field = destination['indexerPrimaryKey'] and destination['indexerPrimaryKey'][0] or None
  df = destination['indexerDefaultField'] and destination['indexerDefaultField'][0] or None
  kwargs = {}
  errors = []

  if source['inputFormat'] not in ('manual', 'table', 'query_handle'):
    path = urllib.unquote(source["path"])
    stats = fs.stats(path)
    if stats.size > MAX_UPLOAD_SIZE:
      raise PopupException(_('File size is too large to handle!'))

  indexer = MorphlineIndexer(user, fs)
  fields = indexer.get_field_list(destination['columns'])
  skip_fields = [field['name'] for field in fields if not field['keep']]

  kwargs['fieldnames'] = ','.join([field['name'] for field in fields])
  for field in fields:
    for operation in field['operations']:
      if operation['type'] == 'split':
        field['multiValued'] = True # Solr requires multiValued to be set when splitting
        kwargs['f.%(name)s.split' % field] = 'true'
        kwargs['f.%(name)s.separator' % field] = operation['settings']['splitChar'] or ','

  if skip_fields:
    kwargs['skip'] = ','.join(skip_fields)
    fields = [field for field in fields if field['name'] not in skip_fields]

  if not unique_key_field:
    unique_key_field = 'hue_id'
    fields += [{"name": unique_key_field, "type": "string"}]
    kwargs['rowid'] = unique_key_field

  if not destination['hasHeader']:
    kwargs['header'] = 'false'
  else:
    kwargs['skipLines'] = 1

  if not client.exists(index_name):
    client.create_index(
        name=index_name,
        config_name=destination.get('indexerConfigSet'),
        fields=fields,
        unique_key_field=unique_key_field,
        df=df,
        shards=destination['indexerNumShards'],
        replication=destination['indexerReplicationFactor']
    )

  if source['inputFormat'] == 'file':
    path = urllib.unquote(source["path"])
    data = fs.read(path, 0, MAX_UPLOAD_SIZE)

  if client.is_solr_six_or_more():
    kwargs['processor'] = 'tolerant'
    kwargs['map'] = 'NULL:'

  try:
    if source['inputFormat'] == 'query':
      query_id = source['query']['id'] if source['query'].get('id') else source['query']

      notebook = Notebook(document=Document2.objects.document(user=user, doc_id=query_id)).get_data()
      request = MockedDjangoRequest(user=user)
      snippet = notebook['snippets'][0]

      searcher = CollectionManagerController(user)
      columns = [field['name'] for field in fields if field['name'] != 'hue_id']
      fetch_handle = lambda rows, start_over: get_api(request, snippet).fetch_result(notebook, snippet, rows=rows, start_over=start_over) # Assumes handle still live
      rows = searcher.update_data_from_hive(index_name, columns, fetch_handle=fetch_handle, indexing_options=kwargs)
      # TODO if rows == MAX_ROWS truncation warning
    else:
      response = client.index(name=index_name, data=data, **kwargs)
      errors = [error.get('message', '') for error in response['responseHeader'].get('errors', [])]
  except Exception, e:
    try:
      client.delete_index(index_name, keep_config=False)
    except Exception, e2:
      LOG.warn('Error while cleaning-up config of failed collection creation %s: %s' % (index_name, e2))
    raise e

  return {'status': 0, 'on_success_url': reverse('indexer:indexes', kwargs={'index': index_name}), 'pub_sub_url': 'assist.collections.refresh', 'errors': errors}


def _create_database(request, source, destination, start_time):
  database = destination['name']
  comment = destination['description']

  use_default_location = destination['useDefaultLocation']
  external_path = destination['nonDefaultLocation']

  sql = django_mako.render_to_string("gen/create_database_statement.mako", {
      'database': {
          'name': database,
          'comment': comment,
          'use_default_location': use_default_location,
          'external_location': external_path,
          'properties': [],
      }
    }
  )

  editor_type = destination['apiHelperType']
  on_success_url = reverse('metastore:show_tables', kwargs={'database': database})

  notebook = make_notebook(
      name=_('Creating database %(name)s') % destination,
      editor_type=editor_type,
      statement=sql,
      status='ready',
      on_success_url=on_success_url,
      last_executed=start_time,
      is_task=True
  )
  return notebook.execute(request, batch=False)


def _create_table(request, source, destination, start_time=-1):
  notebook = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination, start_time)
  return notebook.execute(request, batch=False)


def _large_indexing(request, file_format, collection_name, query=None, start_time=None, lib_path=None):
  indexer = MorphlineIndexer(request.user, request.fs)

  unique_field = indexer.get_unique_field(file_format)
  is_unique_generated = indexer.is_unique_generated(file_format)

  schema_fields = indexer.get_kept_field_list(file_format['columns'])
  if is_unique_generated:
    schema_fields += [{"name": unique_field, "type": "string"}]

  client = SolrClient(user=request.user)

  if not client.exists(collection_name):
    client.create_index(
      name=collection_name,
      fields=request.POST.get('fields', schema_fields),
      unique_key_field=unique_field
      # No df currently
    )

  if file_format['inputFormat'] == 'table':
    db = dbms.get(request.user)
    table_metadata = db.get_table(database=file_format['databaseName'], table_name=file_format['tableName'])
    input_path = table_metadata.path_location
  elif file_format['inputFormat'] == 'file':
    input_path = '${nameNode}%s' % urllib.unquote(file_format["path"])
  else:
    input_path = None

  morphline = indexer.generate_morphline_config(collection_name, file_format, unique_field, lib_path=lib_path)

  return indexer.run_morphline(request, collection_name, morphline, input_path, query, start_time=start_time, lib_path=lib_path)


def _envelope_job(request, file_format, collection_name, start_time=None, lib_path=None):
  indexer = EnvelopeIndexer(request.user, request.fs)

  lib_path = '/tmp/envelope-0.5.0.jar'

  if file_format['inputFormat'] == 'table':
    db = dbms.get(request.user)
    table_metadata = db.get_table(database=file_format['databaseName'], table_name=file_format['tableName'])
    input_path = table_metadata.path_location
  elif file_format['inputFormat'] == 'file':
    input_path = '${nameNode}%s' % file_format["path"]
  else:
    input_path = None

  morphline = indexer.generate_config()

  return indexer.run(request, collection_name, morphline, input_path, start_time=start_time, lib_path=lib_path)

