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
import StringIO

from urlparse import urlparse

from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from simple_salesforce.api import Salesforce
from simple_salesforce.exceptions import SalesforceRefusedRequest

from desktop.lib import django_mako
from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode
from desktop.models import Document2
from kafka.kafka_api import get_topics
from metadata.manager_client import ManagerApi
from notebook.connectors.base import get_api, Notebook
from notebook.decorators import api_error_handler
from notebook.models import make_notebook, MockedDjangoRequest, escape_rows

from indexer.controller import CollectionManagerController
from indexer.file_format import HiveFormat
from indexer.fields import Field
from indexer.indexers.envelope import EnvelopeIndexer
from indexer.models import _save_pipeline
from indexer.indexers.morphline import MorphlineIndexer
from indexer.indexers.rdbms import run_sqoop, _get_api
from indexer.indexers.sql import SQLIndexer
from indexer.solr_client import SolrClient, MAX_UPLOAD_SIZE
from indexer.indexers.flume import FlumeIndexer


LOG = logging.getLogger(__name__)


try:
  from beeswax.server import dbms
except ImportError, e:
  LOG.warn('Hive and HiveServer2 interfaces are not enabled')

try:
  from filebrowser.views import detect_parquet
except ImportError, e:
  LOG.warn('File Browser interface is not enabled')

try:
  from search.conf import SOLR_URL
except ImportError, e:
  LOG.warn('Solr Search interface is not enabled')


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
    format_ = {"type": "csv"}
  elif file_format['inputFormat'] == 'stream':
    if file_format['streamSelection'] == 'kafka':
      format_ = {"type": "csv", "fieldSeparator": ",", "hasHeader": True, "quoteChar": "\"", "recordSeparator": "\\n", 'topics': get_topics()}
    elif file_format['streamSelection'] == 'flume':
      format_ = {"type": "csv", "fieldSeparator": ",", "hasHeader": True, "quoteChar": "\"", "recordSeparator": "\\n"}
  elif file_format['inputFormat'] == 'connector':
    if file_format['connectorSelection'] == 'sfdc':
      sf = Salesforce(
          username=file_format['streamUsername'],
          password=file_format['streamPassword'],
          security_token=file_format['streamToken']
      )
      format_ = {"type": "csv", "fieldSeparator": ",", "hasHeader": True, "quoteChar": "\"", "recordSeparator": "\\n", 'objects': [sobject['name'] for sobject in sf.restful('sobjects/')['sobjects'] if sobject['queryable']]}
    else:
      raise PopupException(_('Input format %(inputFormat)s connector not recognized: $(connectorSelection)s') % file_format)
  else:
    raise PopupException(_('Input format not recognized: %(inputFormat)s') % file_format)

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
    if 'sample' in format_ and format_['sample']:
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
    api = _get_api(request)
    sample = api.get_sample_data(None, database=file_format['rdbmsDatabaseName'], table=file_format['tableName'])

    format_ = {
      "sample": list(sample['rows'])[:4],
      "columns": [
          Field(col['name'], col['type']).to_dict()
          for col in sample['full_headers']
      ]
    }
  elif file_format['inputFormat'] == 'stream':
    if file_format['streamSelection'] == 'kafka':
      if file_format.get('kafkaSelectedTopics') == 'NavigatorAuditEvents':
        kafkaFieldNames = [
          'id',
          'additionalInfo', 'allowed', 'collectionName', 'databaseName', 'db',
          'DELEGATION_TOKEN_ID', 'dst', 'entityId', 'family', 'impersonator',
          'ip', 'name', 'objectType', 'objType', 'objUsageType',
          'operationParams', 'operationText', 'op', 'opText', 'path',
          'perms', 'privilege', 'qualifier', 'QUERY_ID', 'resourcePath',
          'service', 'SESSION_ID', 'solrVersion', 'src', 'status',
          'subOperation', 'tableName', 'table', 'time', 'type',
          'url', 'user'
        ]
        kafkaFieldTypes = [
          'string'
        ] * len(kafkaFieldNames)
        kafkaFieldNames.append('timeDate')
        kafkaFieldTypes.append('date')
      else:
        # Note: mocked here, should come from SFDC or Kafka API or sampling job
        kafkaFieldNames = file_format.get('kafkaFieldNames', '').split(',')
        kafkaFieldTypes = file_format.get('kafkaFieldTypes', '').split(',')

      data = """%(kafkaFieldNames)s
%(data)s""" % {
        'kafkaFieldNames': ','.join(kafkaFieldNames),
        'data': '\n'.join([','.join(['...'] * len(kafkaFieldTypes))] * 5)
      }
      stream = StringIO.StringIO()
      stream.write(data)

      _convert_format(file_format["format"], inverse=True)

      indexer = MorphlineIndexer(request.user, request.fs)
      format_ = indexer.guess_field_types({
        "file": {
            "stream": stream,
            "name": file_format['path']
        },
        "format": file_format['format']
      })
      type_mapping = dict(zip(kafkaFieldNames, kafkaFieldTypes))

      for col in format_['columns']:
        col['keyType'] = type_mapping[col['name']]
        col['type'] = type_mapping[col['name']]
    elif file_format['streamSelection'] == 'flume':
      if 'hue-httpd/access_log' in file_format['channelSourcePath']:
        columns = [
          {'name': 'id', 'type': 'string', 'unique': True},
          {'name': 'client_ip', 'type': 'string'},
          {'name': 'time', 'type': 'date'},
          {'name': 'request', 'type': 'string'},
          {'name': 'code', 'type': 'plong'},
          {'name': 'bytes', 'type': 'plong'},
          {'name': 'method', 'type': 'string'},
          {'name': 'url', 'type': 'string'},
          {'name': 'protocol', 'type': 'string'},
          {'name': 'app', 'type': 'string'},
          {'name': 'subapp', 'type': 'string'}
        ]
      else:
        columns = [{'name': 'message', 'type': 'string'}]

      format_ = {
          "sample": [['...'] * len(columns)] * 4,
          "columns": [
              Field(col['name'], HiveFormat.FIELD_TYPE_TRANSLATE.get(col['type'], 'string'), unique=col.get('unique')).to_dict()
              for col in columns
          ]
      }
  elif file_format['inputFormat'] == 'connector':
    if file_format['connectorSelection'] == 'sfdc':
      sf = Salesforce(
          username=file_format['streamUsername'],
          password=file_format['streamPassword'],
          security_token=file_format['streamToken']
      )
      table_metadata = [{
          'name': column['name'],
          'type': column['type']
        } for column in sf.restful('sobjects/%(streamObject)s/describe/' % file_format)['fields']
      ]
      query = 'SELECT %s FROM %s LIMIT 4' % (', '.join([col['name'] for col in table_metadata]), file_format['streamObject'])
      print query

      try:
        records = sf.query_all(query)
      except SalesforceRefusedRequest, e:
        raise PopupException(message=str(e))

      format_ = {
        "sample": [row.values()[1:] for row in records['records']],
        "columns": [
            Field(col['name'], HiveFormat.FIELD_TYPE_TRANSLATE.get(col['type'], 'string')).to_dict()
            for col in table_metadata
        ]
      }
    else:
      raise PopupException(_('Connector format not recognized: %(connectorSelection)s') % file_format)
  else:
      raise PopupException(_('Input format not recognized: %(inputFormat)s') % file_format)

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
      parent_path = request.fs.parent_path(path)
      stats = request.fs.stats(parent_path)
      split = urlparse(path)
      # Only for HDFS, import data and non-external table
      if split.scheme in ('', 'hdfs') and destination['importData'] and destination['useDefaultLocation'] and oct(stats["mode"])[-1] != '7' and not request.POST.get('show_command'):
        user_scratch_dir = request.fs.get_home_dir() + '/.scratchdir'
        request.fs.do_as_user(request.user, request.fs.mkdir, user_scratch_dir, 00777)
        request.fs.do_as_user(request.user, request.fs.rename, source['path'], user_scratch_dir)
        source['path'] = user_scratch_dir + '/' + source['path'].split('/')[-1]

  if destination['ouputFormat'] in ('database', 'table'):
    destination['nonDefaultLocation'] = request.fs.netnormpath(destination['nonDefaultLocation']) if destination['nonDefaultLocation'] else destination['nonDefaultLocation']

  if destination['ouputFormat'] == 'index':
    source['columns'] = destination['columns']
    index_name = destination["name"]

    if destination['indexerRunJob'] or source['inputFormat'] == 'stream':
      _convert_format(source["format"], inverse=True)
      job_handle = _large_indexing(request, source, index_name, start_time=start_time, lib_path=destination['indexerJobLibPath'], destination=destination)
    else:
      client = SolrClient(request.user)
      job_handle = _small_indexing(request.user, request.fs, client, source, destination, index_name)
  elif source['inputFormat'] in ('stream', 'connector') or destination['ouputFormat'] == 'stream':
    job_handle = _envelope_job(request, source, destination, start_time=start_time, lib_path=destination['indexerJobLibPath'])
  elif source['inputFormat'] == 'altus':
    # BDR copy or DistCP + DDL + Sentry DDL copy
    pass
  elif source['inputFormat'] == 'rdbms':
    if destination['outputFormat'] in ('database', 'file', 'table', 'hbase'):
      job_handle = run_sqoop(request, source, destination, start_time)
  elif destination['ouputFormat'] == 'database':
    job_handle = _create_database(request, source, destination, start_time)
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
  kwargs = {}
  errors = []

  if source['inputFormat'] not in ('manual', 'table', 'query_handle'):
    path = urllib.unquote(source["path"])
    stats = fs.stats(path)
    if stats.size > MAX_UPLOAD_SIZE:
      raise PopupException(_('File size is too large to handle!'))

  indexer = MorphlineIndexer(user, fs)

  fields = indexer.get_field_list(destination['columns'])
  _create_solr_collection(user, fs, client, destination, index_name, kwargs)

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
    elif source['inputFormat'] == 'manual':
      pass # No need to do anything
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
  on_success_url = reverse('metastore:show_tables', kwargs={'database': database}) + "?source_type=" + source.get('sourceType', 'hive')

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

  if request.POST.get('show_command'):
    return {'status': 0, 'commands': notebook.get_str()}
  else:
    return notebook.execute(request, batch=False)


def _large_indexing(request, file_format, collection_name, query=None, start_time=None, lib_path=None, destination=None):
  indexer = MorphlineIndexer(request.user, request.fs)

  unique_field = indexer.get_unique_field(file_format)
  is_unique_generated = indexer.is_unique_generated(file_format)

  schema_fields = indexer.get_kept_field_list(file_format['columns'])
  if is_unique_generated:
    schema_fields += [{"name": unique_field, "type": "string"}]

  client = SolrClient(user=request.user)

  if not client.exists(collection_name) and not request.POST.get('show_command'): # if destination['isTargetExisting']:
    client.create_index(
      name=collection_name,
      fields=request.POST.get('fields', schema_fields),
      unique_key_field=unique_field
      # No df currently
    )
  else:
    # TODO: check if format matches
    pass

  if file_format['inputFormat'] == 'table':
    db = dbms.get(request.user)
    table_metadata = db.get_table(database=file_format['databaseName'], table_name=file_format['tableName'])
    input_path = table_metadata.path_location
  elif file_format['inputFormat'] == 'stream' and file_format['streamSelection'] == 'flume':
    indexer = FlumeIndexer(user=request.user)
    if request.POST.get('show_command'):
      configs = indexer.generate_config(file_format, destination)
      return {'status': 0, 'commands': configs[-1]}
    else:
      return indexer.start(collection_name, file_format, destination)
  elif file_format['inputFormat'] == 'stream':
    return _envelope_job(request, file_format, destination, start_time=start_time, lib_path=lib_path)
  elif file_format['inputFormat'] == 'file':
    input_path = '${nameNode}%s' % urllib.unquote(file_format["path"])
  else:
    input_path = None

  morphline = indexer.generate_morphline_config(collection_name, file_format, unique_field, lib_path=lib_path)

  return indexer.run_morphline(request, collection_name, morphline, input_path, query, start_time=start_time, lib_path=lib_path)


def _envelope_job(request, file_format, destination, start_time=None, lib_path=None):
  collection_name = destination['name']
  indexer = EnvelopeIndexer(request.user, request.fs)

  lib_path = None # Todo optional input field
  input_path = None

  if file_format['inputFormat'] == 'table':
    db = dbms.get(request.user)
    table_metadata = db.get_table(database=file_format['databaseName'], table_name=file_format['tableName'])
    input_path = table_metadata.path_location
  elif file_format['inputFormat'] == 'file':
    input_path = file_format["path"]
    properties = {
      'input_path': input_path,
      'format': 'csv'
    }
  elif file_format['inputFormat'] == 'stream' and file_format['streamSelection'] == 'flume':
    pass
  elif file_format['inputFormat'] == 'stream':
    if file_format['streamSelection'] == 'kafka':
      manager = ManagerApi()
      properties = {
        "brokers": manager.get_kafka_brokers(),
        "topics": file_format['kafkaSelectedTopics'],
        "kafkaFieldType": file_format['kafkaFieldType'],
        "kafkaFieldDelimiter": file_format['kafkaFieldDelimiter'],
      }

      if file_format.get('kafkaSelectedTopics') == 'NavigatorAuditEvents':
        schema_fields = MorphlineIndexer.get_kept_field_list(file_format['sampleCols'])
        properties.update({
          "kafkaFieldNames": ', '.join([_field['name'] for _field in schema_fields]),
          "kafkaFieldTypes": ', '.join([_field['type'] for _field in schema_fields])
        })
      else:
        properties.update({
          "kafkaFieldNames": file_format['kafkaFieldNames'],
          "kafkaFieldTypes": file_format['kafkaFieldTypes']
        })

      if True:
        properties['window'] = ''
      else: # For "KafkaSQL"
        properties['window'] = '''
            window {
                enabled = true
                milliseconds = 60000
            }'''
  elif file_format['inputFormat'] == 'connector':
    if file_format['streamSelection'] == 'flume':
      properties = {
        'streamSelection': file_format['streamSelection'],
        'channelSourceHosts': file_format['channelSourceHosts'],
        'channelSourceSelectedHosts': file_format['channelSourceSelectedHosts'],
        'channelSourcePath': file_format['channelSourcePath'],
      }
    else:
      # sfdc
      properties = {
        'streamSelection': file_format['streamSelection'],
        'streamUsername': file_format['streamUsername'],
        'streamPassword': file_format['streamPassword'],
        'streamToken': file_format['streamToken'],
        'streamEndpointUrl': file_format['streamEndpointUrl'],
        'streamObject': file_format['streamObject'],
      }

  if destination['outputFormat'] == 'table':
    if destination['isTargetExisting']: # Todo: check if format matches
      pass
    else:
      destination['importData'] = False # Avoid LOAD DATA
      if destination['tableFormat'] == 'kudu':
        properties['kafkaFieldNames'] = properties['kafkaFieldNames'].lower() # Kudu names should be all lowercase
      # Create table
      if not request.POST.get('show_command'):
        SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(file_format, destination).execute(request)

    if destination['tableFormat'] == 'kudu':
      manager = ManagerApi()
      properties["output_table"] = "impala::%s" % collection_name
      properties["kudu_master"] = manager.get_kudu_master()
    else:
      properties['output_table'] = collection_name
  elif destination['outputFormat'] == 'stream':
    manager = ManagerApi()
    properties['brokers'] = manager.get_kafka_brokers()
    properties['topics'] = file_format['kafkaSelectedTopics']
    properties['kafkaFieldDelimiter'] = file_format['kafkaFieldDelimiter']
  elif destination['outputFormat'] == 'file':
    properties['path'] = file_format["path"]
    if file_format['inputFormat'] == 'stream':
      properties['format'] = 'csv'
    else:
      properties['format'] = file_format['tableFormat'] # or csv
  elif destination['outputFormat'] == 'index':
    properties['collectionName'] = collection_name
    properties['connection'] = SOLR_URL.get()


  properties["app_name"] = 'Data Ingest'
  properties["inputFormat"] = file_format['inputFormat']
  properties["ouputFormat"] = destination['ouputFormat']
  properties["streamSelection"] = file_format["streamSelection"]

  configs = indexer.generate_config(properties)

  if request.POST.get('show_command'):
    return {'status': 0, 'commands': configs['envelope.conf']}
  else:
    return indexer.run(request, collection_name, configs, input_path, start_time=start_time, lib_path=lib_path)


def _create_solr_collection(user, fs, client, destination, index_name, kwargs):
  unique_key_field = destination['indexerPrimaryKey'] and destination['indexerPrimaryKey'][0] or None
  df = destination['indexerDefaultField'] and destination['indexerDefaultField'][0] or None

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

@api_error_handler
@require_POST
# @check_document_modify_permission()
def save_pipeline(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))

  notebook_doc, save_as = _save_pipeline(notebook, request.user)

  response['status'] = 0
  response['save_as'] = save_as
  response.update(notebook_doc.to_dict())
  response['message'] = request.POST.get('editorMode') == 'true' and _('Query saved successfully') or _('Notebook saved successfully')

  return JsonResponse(response)
