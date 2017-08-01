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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from librdbms.server import dbms as rdbms
from librdbms.conf import DATABASES, get_database_password
from notebook.connectors.rdbms import Assist
from notebook.models import make_notebook


LOG = logging.getLogger(__name__)


def get_db_component(request):
  format_ = {'data': [], 'status': 1, 'message': ''}
  name = None
  try:
    source = json.loads(request.POST.get('source', '{}'))
    user = User.objects.get(username=request.user)
    if source['rdbmsMode'] == 'configRdbms':
      query_server = rdbms.get_query_server_config(server=source['rdbmsType'])
    else:
      name = source['rdbmsType']
      if name:
        query_server = {
          'server_name': name,
          'server_host': source['rdbmsHostname'],
          'server_port': int(source['rdbmsPort']),
          'username': source['rdbmsUsername'],
          'password': source['rdbmsPassword'],
          'options': {},
          'alias': name
        }

    db = rdbms.get(user, query_server=query_server)
    assist = Assist(db)
    if not source['rdbmsDatabaseName']:
      data = assist.get_databases()
    else:
      data = assist.get_tables(source['rdbmsDatabaseName'])
    format_['data'] = [{'name': element, 'value': element} for element in data]
    format_['status'] = 0
  except Exception, e:
    message = 'Error accessing the database %s' % name
    LOG.warn(message, e)
    format['message'] = _(message)

  return JsonResponse(format_)


def run_sqoop(request, source, destination, start_time):
  rdbms_mode = source['rdbmsMode']
  rdbms_name = source['rdbmsType']
  rdbms_database_name = source['rdbmsDatabaseName']
  rdbms_all_tables_selected = source['rdbmsAllTablesSelected']
  destination_type = destination['outputFormat']
  destination_name = destination['name']
  destination_table_name = destination['tableName']
  destination_database_name = destination['databaseName']

  if not rdbms_all_tables_selected:
    rdbms_table_name = source['rdbmsTableName']

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

  statement = '--connect jdbc:%(rdbmsName)s://%(rdbmsHost)s:%(rdbmsPort)s/%(rdbmsDatabaseName)s --username %(rdbmsUserName)s --password %(rdbmsPassword)s' % {
    'rdbmsName': rdbms_name,
    'rdbmsHost': rdbms_host,
    'rdbmsPort': rdbms_port,
    'rdbmsDatabaseName': rdbms_database_name,
    'rdbmsUserName': rdbms_user_name,
    'rdbmsPassword': rdbms_password
  }
  if destination_type == 'file':
    success_url = '/filebrowser/view/' + destination_name
    targetDir = request.fs.fs_defaultfs + destination_name
    if rdbms_all_tables_selected:
      statement = 'import-all-tables %(statement)s --warehouse-dir %(targetDir)s -m 1' % {
        'statement': statement,
        'targetDir': targetDir
      }
    else:
      statement = 'import %(statement)s --table %(rdbmsTableName)s --delete-target-dir --target-dir %(targetDir)s -m 1' % {
        'statement': statement,
        'rdbmsTableName': rdbms_table_name,
        'targetDir': targetDir
      }
  elif destination_type == 'table':
    success_url = reverse('metastore:describe_table', kwargs={'database': destination_database_name, 'table': destination_table_name})
    if rdbms_all_tables_selected:
      statement = 'import-all-tables %(statement)s --hive-import' % {
        'statement': statement
      }
    else:
      statement = 'import %(statement)s --table %(rdbmsTableName)s --hive-import' % {
        'statement': statement,
        'rdbmsTableName': rdbms_table_name
      }
  elif destination_type == 'hbase':
    success_url = '/hbase/#HBase/' + destination_table_name
    # Todo

  lib_files = []
  if destination['sqoopJobLibPaths']:
    lib_files = [{'path': f['path'], 'type': 'jar'} for f in destination['sqoopJobLibPaths']]

  task = make_notebook(
    name=_('Indexer job for %(rdbmsDatabaseName)s.%(rdbmsDatabaseName)s to %(path)s') % {
      'rdbmsDatabaseName': rdbms_database_name,
      'rdbmsDatabaseName': rdbms_database_name,
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


class RdbmsIndexer():

  def __init__(self, user, db_conf_name):
    self.user = user
    self.db_conf_name = db_conf_name

  def guess_format(self):
    return {"type": "csv"}

  def get_sample_data(self, database=None, table=None, column=None):
    query_server = rdbms.get_query_server_config(server=self.db_conf_name)
    db = rdbms.get(self.user, query_server=query_server)

    assist = Assist(db)
    response = {'status': -1}
    sample_data = assist.get_sample_data(database, table, column)

    if sample_data:
      response['status'] = 0
      response['headers'] = sample_data.columns
      response['rows'] = list(sample_data.rows())
    else:
      response['message'] = _('Failed to get sample data.')

    return response