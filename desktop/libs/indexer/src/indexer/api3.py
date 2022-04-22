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

from future import standard_library
standard_library.install_aliases()

from builtins import zip
from past.builtins import basestring
import csv
import json
import logging
import urllib.error
import openpyxl
import re
import sys
import tempfile
import uuid

from django.urls import reverse
from django.views.decorators.http import require_POST

LOG = logging.getLogger(__name__)

try:
  from simple_salesforce.api import Salesforce
  from simple_salesforce.exceptions import SalesforceRefusedRequest
except ImportError:
  LOG.warning('simple_salesforce module not found')

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode
from desktop.lib.python_util import check_encoding
from desktop.models import Document2
from filebrowser.forms import UploadLocalFileForm
from kafka.kafka_api import get_topics, get_topic_data
from notebook.connectors.base import get_api, Notebook
from notebook.decorators import api_error_handler
from notebook.models import MockedDjangoRequest, escape_rows

from indexer.controller import CollectionManagerController
from indexer.file_format import HiveFormat
from indexer.fields import Field, guess_field_type_from_samples
from indexer.indexers.envelope import _envelope_job
from indexer.indexers.base import get_api
from indexer.indexers.flink_sql import FlinkIndexer
from indexer.indexers.morphline import MorphlineIndexer, _create_solr_collection
from indexer.indexers.phoenix_sql import PhoenixIndexer
from indexer.indexers.rdbms import run_sqoop, _get_api
from indexer.indexers.sql import _create_database, _create_table, _create_table_from_local
from indexer.models import _save_pipeline
from indexer.solr_client import SolrClient, MAX_UPLOAD_SIZE
from indexer.indexers.flume import FlumeIndexer


if sys.version_info[0] > 2:
  from io import StringIO as string_io
  from urllib.parse import urlparse, unquote as urllib_unquote
  from django.utils.translation import gettext as _
  import pandas as pd
else:
  from StringIO import StringIO as string_io
  from urllib import unquote as urllib_unquote
  from urlparse import urlparse
  from django.utils.translation import ugettext as _

try:
  from beeswax.server import dbms
except ImportError as e:
  LOG.warning('Hive and HiveServer2 interfaces are not enabled')

try:
  from filebrowser.views import detect_parquet
except ImportError as e:
  LOG.warning('File Browser interface is not enabled')

try:
  from search.conf import SOLR_URL
except ImportError as e:
  LOG.warning('Solr Search interface is not enabled')


def _escape_white_space_characters(s, inverse=False):
  MAPPINGS = {
    "\n": "\\n",
    "\t": "\\t",
    "\r": "\\r",
    " ": "\\s"
  }

  to = 1 if inverse else 0
  from_ = 0 if inverse else 1

  for pair in MAPPINGS.items():
    if sys.version_info[0] > 2:
      s = s.replace(pair[to], pair[from_])
    else:
      s = s.replace(pair[to], pair[from_]).encode('utf-8')

  return s


def _convert_format(format_dict, inverse=False):
  for field in format_dict:
    if isinstance(format_dict[field], basestring):
      format_dict[field] = _escape_white_space_characters(format_dict[field], inverse)


@api_error_handler
def guess_format(request):
  file_format = json.loads(request.POST.get('fileFormat', '{}'))
  file_type = file_format['file_type']
  path = urllib_unquote(file_format["path"])
  
  if sys.version_info[0] < 3 and (file_type == 'excel' or path[-3:] == 'xls' or path[-4:] == 'xlsx'):
    return JsonResponse({'status': -1, 'message': 'Python2 based Hue does not support Excel file importer'})

  if file_format['inputFormat'] == 'localfile':
    if file_type == 'excel':
      format_ = {
        "type": "excel",
        "hasHeader": True
      }
    else:
      format_ = {
        "quoteChar": "\"",
        "recordSeparator": '\\n',
        "type": "csv",
        "hasHeader": True,
        "fieldSeparator": ","
      }

  elif file_format['inputFormat'] == 'file':
    if path[-3:] == 'xls' or path[-4:] == 'xlsx':
      file_obj = request.fs.open(path)
      if path[-3:] == 'xls':
        df = pd.read_excel(file_obj.read(1024 * 1024 * 1024), engine='xlrd')
      else:
        df = pd.read_excel(file_obj.read(1024 * 1024 * 1024), engine='openpyxl')
      _csv_data = df.to_csv(index=False)

      path = excel_to_csv_file_name_change(path)
      request.fs.create(path, overwrite=True, data=_csv_data)

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

    if file_format["path"][-3:] == 'xls' or file_format["path"][-4:] == 'xlsx': 
      format_ = {
          "quoteChar": "\"",
          "recordSeparator": '\\n',
          "type": "excel",
          "hasHeader": True,
          "fieldSeparator": ","
        }

  elif file_format['inputFormat'] == 'table':
    db = dbms.get(request.user)
    try:
      table_metadata = db.get_table(database=file_format['databaseName'], table_name=file_format['tableName'])
    except Exception as e:
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
      format_ = {
        "quoteChar": "\"",
        "recordSeparator": '\\n',
        "type": "csv",
        "hasHeader": False,
        "fieldSeparator": storage.get('field.delim', ',')
      }
    elif table_metadata.details['properties']['format'] == 'parquet':
      format_ = {"type": "parquet", "hasHeader": False,}
    else:
      raise PopupException('Hive table format %s is not supported.' % table_metadata.details['properties']['format'])
  elif file_format['inputFormat'] == 'query':
    format_ = {
      "quoteChar": "\"",
      "recordSeparator": "\\n",
      "type": "csv",
      "hasHeader": False,
      "fieldSeparator": "\u0001"
    }
  elif file_format['inputFormat'] == 'rdbms':
    format_ = {"type": "csv"}
  elif file_format['inputFormat'] == 'stream':
    if file_format['streamSelection'] == 'kafka':
      format_ = {
        "type": "json",
        # "fieldSeparator": ",",
        # "hasHeader": True,
        # "quoteChar": "\"",
        # "recordSeparator": "\\n",
        'topics': get_topics(request.user)
      }
    elif file_format['streamSelection'] == 'flume':
      format_ = {
        "type": "csv",
        "fieldSeparator": ",",
        "hasHeader": True,
        "quoteChar": "\"",
        "recordSeparator": "\\n"
      }
  elif file_format['inputFormat'] == 'connector':
    if file_format['connectorSelection'] == 'sfdc':
      sf = Salesforce(
          username=file_format['streamUsername'],
          password=file_format['streamPassword'],
          security_token=file_format['streamToken']
      )
      format_ = {
        "type": "csv",
        "fieldSeparator": ",",
        "hasHeader": True,
        "quoteChar": "\"",
        "recordSeparator": "\\n",
        'objects': [sobject['name'] for sobject in sf.restful('sobjects/')['sobjects'] if sobject['queryable']]
      }
    else:
      raise PopupException(_('Input format %(inputFormat)s connector not recognized: $(connectorSelection)s') % file_format)
  else:
    raise PopupException(_('Input format not recognized: %(inputFormat)s') % file_format)

  format_['status'] = 0
  return JsonResponse(format_)

def decode_utf8(input_iterator):
  for l in input_iterator:
    yield l.decode('utf-8')

def guess_field_types(request):
  file_format = json.loads(request.POST.get('fileFormat', '{}'))

  if file_format['inputFormat'] == 'localfile':
    path = urllib_unquote(file_format['path'])

    with open(path, 'r') as local_file:

      reader = csv.reader(local_file)
      csv_data = list(reader)

      if file_format['format']['hasHeader']:
        sample = csv_data[1:5]
        column_row = [re.sub('[^0-9a-zA-Z]+', '_', col) for col in csv_data[0]]
      else:
        sample = csv_data[:4]
        column_row = ['field_' + str(count+1) for count, col in enumerate(sample[0])]

      field_type_guesses = []
      for count, col in enumerate(column_row):
        column_samples = [sample_row[count] for sample_row in sample if len(sample_row) > count]
        field_type_guess = guess_field_type_from_samples(column_samples)
        field_type_guesses.append(field_type_guess)

      columns = [
        Field(column_row[count], field_type_guesses[count]).to_dict()
        for count, col in enumerate(column_row)
      ]

      format_ = {
        'columns': columns,
        'sample': sample
      }

  elif file_format['inputFormat'] == 'file':
    indexer = MorphlineIndexer(request.user, request.fs)
    path = urllib_unquote(file_format["path"])
    if path[-3:] == 'xls' or path[-4:] == 'xlsx':
      path = excel_to_csv_file_name_change(path)
    stream = request.fs.open(path)
    encoding = check_encoding(stream.read(10000))
    LOG.debug('File %s encoding is %s' % (path, encoding))
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
    sample = get_api(
      request, {'type': 'hive'}).get_sample_data({'type': 'hive'}, database=file_format['databaseName'], table=file_format['tableName']
    )
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
      except Exception as e:
        LOG.warning('Skipping sample data as query handle might be expired: %s' % e)
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
      data = get_topic_data(
        request.user,
        file_format.get('kafkaSelectedTopics')
      )

      kafkaFieldNames = [col['name'] for col in data['full_headers']]
      kafkaFieldTypes = [col['type'] for col in data['full_headers']]
      topics_data = data['rows']

      format_ = {
          "sample": topics_data,
          "columns": [
              Field(col, 'string', unique=False).to_dict()
              for col in kafkaFieldNames
          ]
      }
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
      print(query)

      try:
        records = sf.query_all(query)
      except SalesforceRefusedRequest as e:
        raise PopupException(message=str(e))

      format_ = {
        "sample": [list(row.values())[1:] for row in records['records']],
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
  destination['ouputFormat'] = outputFormat  # Workaround a very weird bug
  start_time = json.loads(request.POST.get('start_time', '-1'))

  file_encoding = None
  if source['inputFormat'] == 'file':
    if source['path']:
      path = urllib_unquote(source['path'])
      if path[-3:] == 'xls' or path[-4:] == 'xlsx':
        path = excel_to_csv_file_name_change(path)
      source['path'] = request.fs.netnormpath(path)
      stream = request.fs.open(path)
      file_encoding = check_encoding(stream.read(10000))

  if destination['ouputFormat'] in ('database', 'table') and request.fs is not None:
    destination['nonDefaultLocation'] = request.fs.netnormpath(destination['nonDefaultLocation']) \
        if destination['nonDefaultLocation'] else destination['nonDefaultLocation']

  if destination['ouputFormat'] == 'index':
    source['columns'] = destination['columns']
    index_name = destination["name"]

    if destination['indexerRunJob'] or source['inputFormat'] == 'stream':
      _convert_format(source["format"], inverse=True)
      job_handle = _large_indexing(
          request,
          source,
          index_name,
          start_time=start_time,
          lib_path=destination['indexerJobLibPath'],
          destination=destination
      )
    else:
      client = SolrClient(request.user)
      job_handle = _small_indexing(
          request.user,
          request.fs,
          client,
          source,
          destination, index_name
      )
  elif destination['ouputFormat'] == 'stream-table':
    args = {
      'source': source,
      'destination': destination,
      'start_time': start_time,
      'dry_run': request.POST.get('show_command')
    }
    api = FlinkIndexer(
      request.user,
      request.fs
    )

    job_nb = api.create_table_from_kafka(**args)

    if request.POST.get('show_command'):
      job_handle = {
        'status': 0,
        'commands': job_nb
      }
    else:
      job_handle = job_nb.execute(request, batch=False)
  elif source['inputFormat'] == 'altus':
    # BDR copy or DistCP + DDL + Sentry DDL copy
    pass
  elif source['inputFormat'] == 'rdbms':
    if destination['outputFormat'] in ('database', 'file', 'table', 'hbase'):
      job_handle = run_sqoop(
        request,
        source,
        destination,
        start_time
      )
  elif destination['ouputFormat'] == 'database':
    job_handle = _create_database(
      request,
      source,
      destination,
      start_time
    )
  elif destination['ouputFormat'] == 'big-table':
    args = {
      'request': request,
      'source': source,
      'destination': destination,
      'start_time': start_time,
      'dry_run': request.POST.get('show_command')
    }
    api = PhoenixIndexer(
      request.user,
      request.fs
    )

    job_nb = api.create_table_from_file(**args)

    if request.POST.get('show_command'):
      job_handle = {
        'status': 0,
        'commands': job_nb
      }
    else:
      job_handle = job_nb.execute(request, batch=False)
  else:
    if source['inputFormat'] == 'localfile':
      job_handle = _create_table_from_local(
        request,
        source,
        destination,
        start_time
      )
    else:
      # TODO: if inputFormat is 'stream' and tableFormat is 'kudu' --> create Table only
      job_handle = _create_table(
        request,
        source,
        destination,
        start_time,
        file_encoding
      )

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


@require_POST
@api_error_handler
def index(request):
  '''
  Input: pasted data, CSV/json files, Kafka topic
  Output: tables
  '''
  source = json.loads(request.POST.get('source', '{}'))
  destination = json.loads(request.POST.get('destination', '{}'))
  options = json.loads(request.POST.get('options', '{}'))
  connector_id = request.POST.get('connector')

  api = get_api(request.user, connector_id)

  if request.FILES.get('data'):
    source['file'] = request.FILES['data']

  result = api.index(source, destination, options)

  return JsonResponse({'result': result})


def _small_indexing(user, fs, client, source, destination, index_name):
  kwargs = {}
  errors = []

  if source['inputFormat'] not in ('manual', 'table', 'query_handle'):
    path = urllib_unquote(source["path"])
    stats = fs.stats(path)
    if stats.size > MAX_UPLOAD_SIZE:
      raise PopupException(_('File size is too large to handle!'))

  indexer = MorphlineIndexer(user, fs)

  fields = indexer.get_field_list(destination['columns'])
  _create_solr_collection(user, fs, client, destination, index_name, kwargs)

  if source['inputFormat'] == 'file':
    kwargs['separator'] = source['format']['fieldSeparator']
    path = urllib_unquote(source["path"])
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
      # Assumes handle still live
      fetch_handle = lambda rows, start_over: get_api(
          request, snippet
      ).fetch_result(
          notebook,
          snippet,
          rows=rows,
          start_over=start_over
      )
      rows = searcher.update_data_from_hive(
          index_name,
          columns,
          fetch_handle=fetch_handle,
          indexing_options=kwargs
      )
      # TODO if rows == MAX_ROWS truncation warning
    elif source['inputFormat'] == 'manual':
      pass # No need to do anything
    else:
      response = client.index(name=index_name, data=data, **kwargs)
      errors = [error.get('message', '') for error in response['responseHeader'].get('errors', [])]
  except Exception as e:
    try:
      client.delete_index(index_name, keep_config=False)
    except Exception as e2:
      LOG.warning('Error while cleaning-up config of failed collection creation %s: %s' % (index_name, e2))
    raise e

  return {
    'status': 0,
    'on_success_url': reverse('indexer:indexes',
    kwargs={'index': index_name}),
    'pub_sub_url': 'assist.collections.refresh',
    'errors': errors
  }


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
    input_path = '${nameNode}%s' % urllib_unquote(file_format["path"])
  else:
    input_path = None

  morphline = indexer.generate_morphline_config(collection_name, file_format, unique_field, lib_path=lib_path)

  return indexer.run_morphline(
      request,
      collection_name,
      morphline,
      input_path,
      query,
      start_time=start_time,
      lib_path=lib_path
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


def excel_to_csv_file_name_change(path):
  if path[-4:] == 'xlsx':
    path = path[:-4] + 'csv'
  elif path[-3:] == 'xls':
    path = path[:-3] + 'csv'
  return path


def upload_local_file_drag_and_drop(request):
  response = {'status': -1, 'data': ''}
  form = UploadLocalFileForm(request.POST, request.FILES)

  if form.is_valid():
    resp = upload_local_file(request)
    json_data = json.loads(resp.content)
    response['status'] = 0
    response.update({
      'path': json_data['local_file_url'],
    })

  return JsonResponse(response)


def upload_local_file(request):
  upload_file = request.FILES['file']
  username = request.user.username
  filename = "%s_%s:%s;" % (username, uuid.uuid4(), re.sub('[^0-9a-zA-Z]+', '_', upload_file.name))
  file_format = upload_file.name.split(".")[-1]
  file_type = 'csv'

  if file_format in ("xlsx", "xls"):
    if file_format == "xlsx":
      read_file = pd.read_excel(upload_file)
    else:
      read_file = pd.read_excel(upload_file, engine='xlrd')
  
    temp_file = tempfile.NamedTemporaryFile(mode='w', prefix=filename, suffix='.csv', delete=False)
    read_file.to_csv(temp_file, index=False)
    file_type = 'excel'

  else: 
    temp_file = tempfile.NamedTemporaryFile(prefix=filename, suffix='.csv', delete=False)
    temp_file.write(upload_file.read())

  local_file_url = temp_file.name
  temp_file.close()

  return JsonResponse({'local_file_url': local_file_url, 'file_type': file_type})
