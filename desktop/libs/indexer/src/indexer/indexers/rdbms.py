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
import os.path
import uuid

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import smart_str
from librdbms.conf import DATABASES, get_database_password, get_server_choices
from librdbms.jdbc import Jdbc
from librdbms.server import dbms as rdbms
from notebook.conf import get_ordered_interpreters
from notebook.connectors.jdbc import Assist as JdbcAssist
from notebook.connectors.rdbms import Assist
from notebook.models import make_notebook

import beeswax.conf


LOG = logging.getLogger(__name__)


def get_db_component(request):
  format_ = {'data': [], 'status': 1, 'message': ''}
  db = None

  try:
    source = json.loads(request.POST.get('source', '{}'))
    user = User.objects.get(username=request.user)
    name = source['rdbmsType']

    if source['rdbmsMode'] == 'configRdbms':
      if name != 'jdbc':
        query_server = rdbms.get_query_server_config(server=name)
        db = rdbms.get(user, query_server=query_server)
      else:
        interpreters = get_ordered_interpreters(request.user)
        key = [key for key in interpreters if key['name'] == source['rdbmsJdbcDriverName']]
        if key:
          options = key[0]['options']
          source['rdbmsHostname'] = options['url']
          db = Jdbc(driver_name=options['driver'], url=options['url'], username=options['user'], password=options['password'])
    else:
      if name != 'jdbc':
        query_server = {
          'server_name': name,
          'server_host': source['rdbmsHostname'].split('/',1)[0],
          'server_port': int(source['rdbmsPort']),
          'username': source['rdbmsUsername'],
          'password': source['rdbmsPassword'],
          'options': {},
          'alias': name
        }
        if '/' in source['rdbmsHostname'] and source['rdbmsHostname'].split('/',1)[1]:
          query_server['name'] = source['rdbmsHostname'].split('/',1)[1]
        db = rdbms.get(user, query_server=query_server)
      else:
        db = Jdbc(driver_name=source['rdbmsJdbcDriver'], url=source['rdbmsHostname'], username=source['rdbmsUsername'], password=source['rdbmsPassword'])

    if name != 'jdbc':
      assist = Assist(db)
      if not source['rdbmsDatabaseName']:
        data = assist.get_databases()
      elif source['rdbmsDatabaseName']:
        data = assist.get_tables(source['rdbmsDatabaseName'])
    else:
      assist = JdbcAssist(db)
      if not source['rdbmsDatabaseName']:
        data = assist.get_databases(source['rdbmsHostname'].split(':',2)[1])
      elif source['rdbmsDatabaseName']:
        data = assist.get_tables(source['rdbmsDatabaseName'], None, source['rdbmsHostname'].split(':',2)[1])
    if data:
      format_['data'] = [{'name': element, 'value': element} for element in data]
      format_['status'] = 0
  except Exception, e:
    message = _('Error accessing the database %s: %s') % (name, e)
    LOG.warn(message)

  return JsonResponse(format_)

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
  format_['status'] = 0

  return JsonResponse(format_)

def run_sqoop(request, source, destination, start_time):
  rdbms_mode = source['rdbmsMode']
  name = source['rdbmsType']
  rdbms_name = source['rdbmsJdbcDriverName'] if name == 'jdbc' else name
  rdbms_database_name = source['rdbmsDatabaseName']

  rdbms_all_tables_selected = source['rdbmsAllTablesSelected']
  columns = destination['columns']
  destination_type = destination['outputFormat']
  destination_name = destination['name']
  destination_table_name = destination['tableName']
  destination_database_name = destination['databaseName']
  destination_mappers_num = destination['numMappers']
  destination_file_output_format = destination['rdbmsFileOutputFormat']
  destination_custom_fields_delimiter = destination['customFieldsDelimiter']
  destination_custom_line_delimiter = destination['customLineDelimiter']
  destination_custom_enclosed_by_delimiter = destination['customEnclosedByDelimiter']
  destination_compress_mode = destination['compressMode']
  destination_verbose_mode = destination['verboseMode']
  destination_splitby_column = destination['rdbmsSplitByColumn']

  if not rdbms_all_tables_selected:
    rdbms_table_name = source['rdbmsTableName']

  if rdbms_mode == 'configRdbms':
    if name != 'jdbc':
      rdbms_host = DATABASES[rdbms_name].HOST.get().split('/', 1)[0]
      rdbms_port = DATABASES[rdbms_name].PORT.get()
      rdbms_user_name = DATABASES[rdbms_name].USER.get()
      rdbms_password = get_database_password(rdbms_name)
    else:
      interpreters = get_ordered_interpreters(request.user)
      key = [key for key in interpreters if key['name'] == source['rdbmsJdbcDriverName']]
      if key:
        options = key[0]['options']
        rdbms_url = options['url']
        rdbms_driver = options['driver']
        rdbms_user_name = options['user']
        rdbms_password = options['password']
  else:
    if name != 'jdbc':
      rdbms_host = source['rdbmsHostname'].split('/', 1)[0]
      rdbms_port = source['rdbmsPort']
      rdbms_user_name = source['rdbmsUsername']
      rdbms_password = source['rdbmsPassword']
    else:
      rdbms_url = source['rdbmsHostname']
      rdbms_driver = source['rdbmsJdbcDriver']
      rdbms_user_name = source['rdbmsUsername']
      rdbms_password = source['rdbmsPassword']

  if name != 'jdbc':
    connect_value = 'jdbc:%(rdbmsName)s:%(thin)s//%(rdbmsHost)s:%(rdbmsPort)s/%(rdbmsDatabaseName)s' % {
      'rdbmsName': rdbms_name,
      'thin': 'thin:@' if name == 'oracle' else '',
      'rdbmsHost': rdbms_host,
      'rdbmsPort': rdbms_port,
      'rdbmsDatabaseName': rdbms_database_name
    }
  else:
    connect_value = rdbms_url.rsplit('/', 1)[0] + '/' + rdbms_database_name

  password_file_path = request.fs.join(request.fs.get_home_dir() + '/sqoop/', uuid.uuid4().hex + '.password')
  request.fs.do_as_user(request.user, request.fs.create, password_file_path, overwrite=True, permission=0700, data=smart_str(rdbms_password))

  lib_files = []
  if destination['sqoopJobLibPaths']:
    lib_files = [{'path': f['path'], 'type': 'jar'} for f in destination['sqoopJobLibPaths']]

  statement = '--connect %(connectValue)s --username %(rdbmsUserName)s --password-file %(passwordFilePath)s' % {
    'connectValue': connect_value,
    'driver': 'com.teradata.jdbc.TeraDriver',
    'rdbmsUserName': rdbms_user_name,
    'passwordFilePath': password_file_path
  }
  if name == 'jdbc':
    statement = '%(statement)s --driver %(driver)s' % {
      'statement': statement,
      'driver': rdbms_driver,
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
      query = ''
      for element in columns:
        if element['keep']:
          query += element['name']+','
      query = '\'SELECT %(query)s from %(rdbmsTableName)s WHERE $CONDITIONS\'' % {
        'query': query.rstrip(','),
        'rdbmsTableName': rdbms_table_name
      }
      statement = 'import %(statement)s --query %(query)s --delete-target-dir --target-dir %(targetDir)s' % {
        'statement': statement,
        'query': query,
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
    '''
    _HIVE_SITE_PATH = os.path.join(beeswax.conf.HIVE_CONF_DIR.get(), 'hive-site.xml')
    hive_file_path = request.fs.join(request.fs.get_home_dir() + '/sqoop/', 'hive-site.xml')
    request.fs.do_as_user(request.user, request.fs.create, hive_file_path, overwrite=True, permission=0700, data=smart_str(file(_HIVE_SITE_PATH, 'r').read()))
    lib_files.append({'path': hive_file_path, 'type': 'xml'})
    '''
    lib_files.append({'path': '/user/admin/sqoop/hive-site.xml', 'type': 'jar'})
    if rdbms_all_tables_selected:
      targetDir = request.fs.fs_defaultfs + destination_name
      success_url = '/filebrowser/view/' + destination_name
      statement = 'import-all-tables %(statement)s --hive-import --warehouse-dir %(targetDir)s' % {
        'statement': statement,
        'targetDir': targetDir
      }
    else:
      success_url = reverse('metastore:describe_table', kwargs={'database': destination_database_name, 'table': destination_table_name})
      folder_path = request.fs.join(request.fs.get_home_dir() + '/' + destination['name'])
      request.fs.do_as_user(request.user, request.fs.mkdir, folder_path)
      folder_path = request.fs.fs_defaultfs + folder_path
      query = ''
      for element in columns:
        if element['keep']:
          query += element['name'] + ' AS ' + element['newName'] + ','
      query = '\'SELECT %(query)s from %(rdbmsTableName)s WHERE $CONDITIONS\'' % {
        'query': query.rstrip(','),
        'rdbmsTableName': rdbms_table_name
      }
      statement = 'import %(statement)s --query %(query)s --hive-import --delete-target-dir --target-dir %(targetDir)s --hive-table %(destinationName)s' % {
        'statement': statement,
        'query': query,
        'targetDir': folder_path,
        'destinationName': destination_name
      }
      statement = _splitby_column_check(statement, destination_splitby_column)
  elif destination_type == 'hbase':
    success_url = '/hbase/#HBase/' + destination_table_name
    # Todo
  statement = '%(statement)s --num-mappers %(numMappers)s' % {
    'statement': statement,
    'numMappers': destination_mappers_num
  }
  if destination_compress_mode:
    statement = '%(statement)s --compress' % {
      'statement': statement
    }
  if destination_verbose_mode:
    statement = '%(statement)s --verbose' % {
      'statement': statement
    }
  task = make_notebook(
    name=_('Indexer job for %(rdbmsDatabaseName)s.%(rdbmsTableName)s to %(path)s') % {
      'rdbmsDatabaseName': destination_database_name,
      'rdbmsTableName': destination_table_name,
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

  def __init__(self, user, db_conf_name):
    self.user = user
    self.db_conf_name = db_conf_name

  def guess_format(self):
    return {"type": "csv"}

  def get_sample_data(self, source=None):
    format_ = {'rows': [], 'status': 1, 'headers': [], 'message': ''}
    db = None
    name = source['rdbmsType']

    try:
      if source['rdbmsMode'] == 'configRdbms':
        if name != 'jdbc':
          query_server = rdbms.get_query_server_config(server=name)
          db = rdbms.get(self.user, query_server=query_server)
        else:
          interpreters = get_ordered_interpreters(self.user)
          key = [key for key in interpreters if key['name'] == source['rdbmsJdbcDriverName']]
          if key:
            options = key[0]['options']
            source['rdbmsHostname'] = options['url']
            db = Jdbc(driver_name=options['driver'], url=options['url'], username=options['user'], password=options['password'])
      else:
        if name != 'jdbc':
          query_server = {
            'server_name': name,
            'server_host': source['rdbmsHostname'].split('/', 1)[0],
            'server_port': int(source['rdbmsPort']),
            'username': source['rdbmsUsername'],
            'password': source['rdbmsPassword'],
            'options': {},
            'alias': name
          }
          if '/' in source['rdbmsHostname'] and source['rdbmsHostname'].split('/', 1)[1]:
            query_server['name'] = source['rdbmsHostname'].split('/', 1)[1]
          db = rdbms.get(self.user, query_server=query_server)
        else:
          db = Jdbc(driver_name=source['rdbmsJdbcDriver'], url=source['rdbmsHostname'], username=source['rdbmsUsername'], password=source['rdbmsPassword'])

      if name != 'jdbc':
        assist = Assist(db)
        data = assist.get_sample_data(source['rdbmsDatabaseName'], source['rdbmsTableName'])
        if data:
          format_['status'] = 0
          format_['headers'] = data.columns
          format_['rows'] = list(data.rows())
      else:
        assist = JdbcAssist(db)
        data, meta = assist.get_sample_data(source['rdbmsDatabaseName'], source['rdbmsTableName'], None, source['rdbmsHostname'].split(':',2)[1], 4)
        meta = [row[0] for row in meta]
        if data:
          format_['status'] = 0
          format_['headers'] = meta
          format_['rows'] = data
    except Exception, e:
      message = _('Error accessing the database %s: %s') % (name, e)
      LOG.warn(message)

    return format_

  def get_columns(self, source=None):
    format_ = {'data': [], 'status': 1, 'message': ''}
    db = None
    name = source['rdbmsType']

    try:
      if source['rdbmsMode'] == 'configRdbms':
        if name != 'jdbc':
          query_server = rdbms.get_query_server_config(server=name)
          db = rdbms.get(self.user, query_server=query_server)
        else:
          interpreters = get_ordered_interpreters(self.user)
          key = [key for key in interpreters if key['name'] == source['rdbmsJdbcDriverName']]
          if key:
            options = key[0]['options']
            source['rdbmsHostname'] = options['url']
            db = Jdbc(driver_name=options['driver'], url=options['url'], username=options['user'], password=options['password'])
      else:
        if name != 'jdbc':
          query_server = {
            'server_name': name,
            'server_host': source['rdbmsHostname'].split('/', 1)[0],
            'server_port': int(source['rdbmsPort']),
            'username': source['rdbmsUsername'],
            'password': source['rdbmsPassword'],
            'options': {},
            'alias': name
          }
          if '/' in source['rdbmsHostname'] and source['rdbmsHostname'].split('/', 1)[1]:
            query_server['name'] = source['rdbmsHostname'].split('/', 1)[1]
          db = rdbms.get(self.user, query_server=query_server)
        else:
          db = Jdbc(driver_name=source['rdbmsJdbcDriver'], url=source['rdbmsHostname'], username=source['rdbmsUsername'], password=source['rdbmsPassword'])

      if name != 'jdbc':
        assist = Assist(db)
        data = assist.get_columns(source['rdbmsDatabaseName'], source['rdbmsTableName'])
      else:
        assist = JdbcAssist(db)
        data = assist.get_columns(source['rdbmsDatabaseName'], source['rdbmsTableName'], source['rdbmsHostname'].split(':',2)[1])
      if data:
        format_['status'] = 0
        format_['data'] = data
    except Exception, e:
      message = _('Error accessing the database %s: %s') % (name, e)
      LOG.warn(message)

    return format_