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
import uuid

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import smart_str
from librdbms.conf import DATABASES, get_database_password, get_server_choices, get_connector_name
from librdbms.jdbc import Jdbc
from librdbms.server import dbms as rdbms
from notebook.conf import get_ordered_interpreters
from notebook.connectors.base import get_api
from notebook.models import make_notebook


LOG = logging.getLogger(__name__)


def get_db_component(request):
  format_ = {'data': [], 'status': 1, 'message': ''}
  try:
    source = json.loads(request.POST.get('source', '{}'))

    api = _get_api(request)

    if not source['rdbmsDatabaseName'] or (source['rdbmsMode'] == "customRdbms" and not source['rdbmsDbIsValid']):
      autocomplete = api.autocomplete(None)
      data = autocomplete['databases']
    elif source['rdbmsDatabaseName']:
      autocomplete = api.autocomplete(None, source['rdbmsDatabaseName'])
      data = [table['name'] for table in autocomplete['tables_meta']]

    format_['data'] = [{'name': element, 'value': element} for element in data]
    format_['status'] = 0
  except Exception, e:
    message = _('Error accessing the database: %s') % e
    LOG.warn(message)
    format_['message'] = message

  return JsonResponse(format_)

def _get_api(request):
  file_format = json.loads(request.POST.get('source', request.POST.get('fileFormat', '{}')))
  options = None
  query_server = None
  if file_format['rdbmsMode'] == 'customRdbms':
    type = 'custom'
    if file_format['rdbmsType'] == 'jdbc':
      name = file_format['rdbmsHostname'] # We make sure it's unique as name is the cache key
      interface = file_format['rdbmsType']
      options = {'driver': file_format['rdbmsJdbcDriver'],
                 'url': file_format['rdbmsHostname'],
                 'user': file_format['rdbmsUsername'],
                 'password': file_format['rdbmsPassword']
                }
    else:
      interface = 'rdbms'
      query_server = {
        'server_name': file_format['rdbmsType'],
        'server_host': file_format['rdbmsHostname'],
        'server_port': int(file_format['rdbmsPort'] or '3306'),
        'username': file_format['rdbmsUsername'],
        'password': file_format['rdbmsPassword'],
        'options': {},
        'alias': file_format['rdbmsType']
      }
      name = 'rdbms:%(server_name)s://%(server_host)s:%(server_port)s' % query_server # We make sure it's unique as name is the cache key
  else:
    if file_format['rdbmsType'] == 'jdbc':
      type = file_format['rdbmsJdbcDriverName'] and file_format['rdbmsJdbcDriverName'].lower()
    else:
      type = file_format['rdbmsType']
      query_server = rdbms.get_query_server_config(server=file_format['rdbmsType'])
    name = type
    interface = file_format['inputFormat']

  return get_api(request, { 'type': type, 'interface': interface, 'options': options, 'query_server': query_server, 'name': name})

def jdbc_db_list(request):
  format_ = {'data': [], 'status': 1}
  interpreters = get_ordered_interpreters(request.user)
  format_['data'] = [{'value': key['name'], 'name': key['name']} for key in interpreters if key['interface'] == 'jdbc']
  format_['status'] = 0

  return JsonResponse(format_)

def get_drivers(request):
  format_ = {'data': [], 'status': 1}
  servers_dict = dict(get_server_choices())
  format_['data'] = [{'value': key, 'name': servers_dict[key]} for key in servers_dict.keys()]
  format_['data'].append({'value': 'jdbc', 'name': 'JDBC'})
#   format_['data'].append({'value': 'sqlalchemy', 'name': 'SQL Alchemy'})
  format_['status'] = 0

  return JsonResponse(format_)

def run_sqoop(request, source, destination, start_time):
  rdbms_mode = source['rdbmsMode']
  rdbms_name = source['rdbmsJdbcDriverName'] if source['rdbmsType'] == 'jdbc' else source['rdbmsType']
  rdbms_database_name = source['rdbmsDatabaseName']
  rdbms_all_tables_selected = source['rdbmsAllTablesSelected']
  rdbms_exclude = source['rdbmsTablesExclude']
  destination_type = destination['outputFormat']
  destination_name = destination['name']
  destination_table_name = destination['tableName']
  destination_database_name = destination['databaseName']
  destination_mappers_num = destination['numMappers']
  destination_file_output_format = destination['rdbmsFileOutputFormat']
  destination_custom_fields_delimiter = destination['customFieldsDelimiter']
  destination_custom_line_delimiter = destination['customLineDelimiter']
  destination_custom_enclosed_by_delimiter = destination['customEnclosedByDelimiter']
  destination_splitby_column = destination['rdbmsSplitByColumn']

  if not rdbms_all_tables_selected:
    rdbms_table_name = source['tableName']
  else:
    rdbms_table_name = None

  if rdbms_mode == 'configRdbms' and rdbms_name == 'jdbc':
    username = ''
    password = ''
    url = ''
    interpreters = get_ordered_interpreters(request.user)
    key = [key for key in interpreters if key['name'] == source['rdbmsJdbcDriverName']]

    if key:
      options = key[0]['options']
      url = options['url']
      password = options['password']
      username = options['user']
    statement = '--connect %(url)s --username %(username)s --password %(password)s' % {
      'url': url,
      'username': username,
      'password': password
    }
  else:
    if rdbms_mode == 'configRdbms':
      rdbms_host = DATABASES[rdbms_name].HOST.get()
      rdbms_port = DATABASES[rdbms_name].PORT.get()
      rdbms_user_name = DATABASES[rdbms_name].USER.get()
      rdbms_password = get_database_password(rdbms_name)
      url = "jdbc:%(rdbmsType)s://%(rdbmsHost)s:%(rdbmsPort)s" % {
        'rdbmsType': rdbms_name,
        'rdbmsHost': rdbms_host,
        'rdbmsPort': rdbms_port
      }
    else:
      rdbms_host = source['rdbmsHostname']
      rdbms_port = source['rdbmsPort']
      rdbms_user_name = source['rdbmsUsername']
      rdbms_password = source['rdbmsPassword']
      url = rdbms_host

    password_file_path = request.fs.join(request.fs.get_home_dir() + '/sqoop/', uuid.uuid4().hex + '.password')
    request.fs.do_as_user(request.user, request.fs.create, password_file_path, overwrite=True, permission=0700, data=smart_str(rdbms_password))

    lib_files = []
    if destination['sqoopJobLibPaths']:
      lib_files = [{'path': f['path'], 'type': 'jar'} for f in destination['sqoopJobLibPaths'] if f['path']]

    statement = '--connect %(url)s/%(rdbmsDatabaseName)s --username %(rdbmsUserName)s --password-file %(passwordFilePath)s' % {
      'url': url,
      'rdbmsDatabaseName': rdbms_database_name,
      'rdbmsUserName': rdbms_user_name,
      'passwordFilePath': password_file_path
    }
  if rdbms_exclude:
    exclude = '--exclude-tables %s' % ','.join(rdbms_exclude)
  else:
    exclude = ''
  if destination_type == 'file':
    success_url = '/filebrowser/view/' + destination_name
    targetDir = request.fs.fs_defaultfs + destination_name
    if rdbms_all_tables_selected:
      statement = 'import-all-tables %(statement)s --warehouse-dir %(targetDir)s %(exclude)s' % {
        'statement': statement,
        'targetDir': targetDir,
        'exclude': exclude
      }
    else:
      statement = 'import %(statement)s --table %(rdbmsTableName)s --delete-target-dir --target-dir %(targetDir)s' % {
        'statement': statement,
        'rdbmsTableName': rdbms_table_name,
        'targetDir': targetDir
      }
      if destination_file_output_format == 'text':
        statement = '%(statement)s --as-textfile --fields-terminated-by %(customFieldsDelimiter)s --lines-terminated-by %(customLineDelimiter)s --enclosed-by %(customEnclosedByDelimiter)s' % {
          'statement': statement,
          'customFieldsDelimiter': destination_custom_fields_delimiter,
          'customLineDelimiter': destination_custom_line_delimiter,
          'customEnclosedByDelimiter': destination_custom_enclosed_by_delimiter
        }
      elif destination_file_output_format == 'sequence':
        statement = '%(statement)s --as-sequencefile' % {
          'statement': statement
        }
      elif destination_file_output_format == 'avro':
        statement = '%(statement)s --as-avrodatafile' % {
          'statement': statement
        }
      statement = _splitby_column_check(statement, destination_splitby_column)
  elif destination_type == 'table' or destination_type == 'database':
    success_url = reverse('metastore:describe_table', kwargs={'database': destination_database_name, 'table': destination_table_name})
    if rdbms_all_tables_selected:
      statement = 'import-all-tables %(statement)s --hive-import --hive-database %(hive_database_name)s %(exclude)s' % {
        'statement': statement,
        'hive_database_name': destination_database_name,
        'exclude': exclude
      }
    else:
      statement = 'import %(statement)s --table %(rdbmsTableName)s --hive-import --delete-target-dir --hive-database %(hive_database_name)s --hive-table %(hive_table_name)s' % {
        'statement': statement,
        'rdbmsTableName': rdbms_table_name,
        'hive_database_name': destination_database_name,
        'hive_table_name': destination_table_name
      }
      statement = _splitby_column_check(statement, destination_splitby_column)
  elif destination_type == 'hbase':
    success_url = '/hbase/#HBase/' + destination_table_name

    # Todo
  statement = '%(statement)s --num-mappers %(numMappers)s --verbose' % {
    'statement': statement,
    'numMappers': destination_mappers_num
  }

  task = make_notebook(
    name=_('Indexer job for %(rdbmsDatabaseName)s.%(rdbmsTableName)s to %(path)s') % {
      'rdbmsDatabaseName': rdbms_database_name,
      'rdbmsTableName': '*' if rdbms_all_tables_selected else rdbms_table_name,
      'path': destination_name
    },
    editor_type='sqoop1',
    statement=statement,
    files=lib_files,
    status='ready',
    on_success_url=success_url,
    last_executed=start_time,
    is_task=True
  )

  if request.POST.get('show_command'):
    return {'status': 0, 'commands': task.get_str()}
  else:
    return task.execute(request, batch=False)


def _splitby_column_check(statement, destination_splitby_column):
  if destination_splitby_column:
    statement = '%(statement)s --split-by %(destinationSplitbyColumn)s' % {
      'statement': statement,
      'destinationSplitbyColumn': destination_splitby_column
    }
  return statement