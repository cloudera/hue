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
from notebook.connectors.jdbc import Assist as JdbcAssist
from notebook.connectors.rdbms import Assist
from notebook.models import make_notebook


LOG = logging.getLogger(__name__)


def get_db_component(request):
  format_ = {'data': [], 'status': 1, 'message': ''}
  db = None

  try:
    source = json.loads(request.POST.get('source', '{}'))

    db = _get_db(request)

    if source['rdbmsType'] != 'jdbc':
      assist = Assist(db)
    else:
      assist = JdbcAssist(db)

    if not source['rdbmsDatabaseName'] or (source['rdbmsMode'] == "customRdbms" and not source['rdbmsDbIsValid']):
      data = assist.get_databases()
    elif source['rdbmsDatabaseName']:
      data = assist.get_tables(source['rdbmsDatabaseName'])

    format_['data'] = [{'name': element, 'value': element} for element in data]
    format_['status'] = 0
  except Exception, e:
    message = _('Error accessing the database: %s') % e
    LOG.warn(message)
    format_['message'] = message

  return JsonResponse(format_)

def _get_db(request):
  source = json.loads(request.POST.get('source', request.POST.get('fileFormat', '{}')))
  user = User.objects.get(username=request.user)
  name = None

  if source['rdbmsMode'] == 'configRdbms':
    if source['rdbmsType'] != 'jdbc':
      query_server = rdbms.get_query_server_config(server=source['rdbmsType'])
      db = rdbms.get(user, query_server=query_server)
    else:
      interpreters = get_ordered_interpreters(request.user)
      options = {}
      key = [key for key in interpreters if key['name'] == source['rdbmsJdbcDriverName']]
      if key:
        options = key[0]['options']

        db = Jdbc(driver_name=options['driver'], url=options['url'], username=options['user'], password=options['password'])
  else:
    name = source['rdbmsType']
    if name != 'jdbc':
      query_server = {
        'server_name': name,
        'server_host': source['rdbmsHostname'],
        'server_port': int(source['rdbmsPort'] or 3306),
        'username': source['rdbmsUsername'],
        'password': source['rdbmsPassword'],
        'options': {},
        'alias': name
      }
      db = rdbms.get(user, query_server=query_server)
    else:
      db = Jdbc(driver_name=source['rdbmsJdbcDriver'], url=source['rdbmsHostname'], username=source['rdbmsUsername'], password=source['rdbmsPassword'])

  return db

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
    rdbms_table_name = source['rdbmsTableName']
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
    else:
      rdbms_host = source['rdbmsHostname']
      rdbms_port = source['rdbmsPort']
      rdbms_user_name = source['rdbmsUsername']
      rdbms_password = source['rdbmsPassword']

    password_file_path = request.fs.join(request.fs.get_home_dir() + '/sqoop/', uuid.uuid4().hex + '.password')
    request.fs.do_as_user(request.user, request.fs.create, password_file_path, overwrite=True, permission=0700, data=smart_str(rdbms_password))

    lib_files = []
    if destination['sqoopJobLibPaths']:
      lib_files = [{'path': f['path'], 'type': 'jar'} for f in destination['sqoopJobLibPaths'] if f['path']]

    statement = '--connect jdbc:%(rdbmsType)s://%(rdbmsHost)s:%(rdbmsPort)s/%(rdbmsDatabaseName)s --username %(rdbmsUserName)s --password-file %(passwordFilePath)s' % {
      'rdbmsType': get_connector_name(rdbms_name),
      'rdbmsHost': rdbms_host,
      'rdbmsPort': rdbms_port,
      'rdbmsDatabaseName': rdbms_database_name,
      'rdbmsUserName': rdbms_user_name,
      'passwordFilePath': password_file_path
    }

  if destination_type == 'file':
    success_url = '/filebrowser/view/' + destination_name
    targetDir = request.fs.fs_defaultfs + destination_name
    if rdbms_all_tables_selected:
      statement = 'import-all-tables %(statement)s --warehouse-dir %(targetDir)s' % {
        'statement': statement,
        'targetDir': targetDir
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
  elif destination_type == 'table':
    success_url = reverse('metastore:describe_table', kwargs={'database': destination_database_name, 'table': destination_table_name})
    if rdbms_all_tables_selected:
      statement = 'import-all-tables %(statement)s --hive-import --delete-target-dir --hive-database %(hive_database_name)s' % {
        'statement': statement,
        'hive_database_name': destination_database_name
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
  statement = '%(statement)s --num-mappers %(numMappers)s' % {
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

  return task.execute(request, batch=False)

def _splitby_column_check(statement, destination_splitby_column):
  if destination_splitby_column:
    statement = '%(statement)s --split-by %(destinationSplitbyColumn)s' % {
      'statement': statement,
      'destinationSplitbyColumn': destination_splitby_column
    }
  return statement


class RdbmsIndexer():

  def __init__(self, user, db_conf_name, db=None):
    self.user = user
    self.db_conf_name = db_conf_name
    self.db = db

  def guess_format(self):
    return {"type": "csv"}

  def get_sample_data(self, mode=None, database=None, table=None, column=None):
    if self.db:
      db = self.db
    else:
      query_server = rdbms.get_query_server_config(server=self.db_conf_name)
      db = rdbms.get(self.user, query_server=query_server)

    if mode == 'configRdbms' or self.db_conf_name != 'jdbc':
      assist = Assist(db)
    else:
      assist = JdbcAssist(db)

    response = {'status': -1}
    sample_data = assist.get_sample_data(database, table, column)

    if sample_data:
      response['status'] = 0
      response['headers'] = sample_data.columns
      response['rows'] = list(sample_data.rows())
    else:
      response['message'] = _('Failed to get sample data.')

    return response
