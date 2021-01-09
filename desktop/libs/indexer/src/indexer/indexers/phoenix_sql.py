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
# limitations under the License.import logging

import logging
import sys
import uuid

from django.urls import reverse
from django.utils.translation import ugettext as _

from notebook.models import make_notebook

if sys.version_info[0] > 2:
  from urllib.parse import urlparse, unquote as urllib_unquote
else:
  from urllib import unquote as urllib_unquote
  from urlparse import urlparse


LOG = logging.getLogger(__name__)


class PhoenixIndexer():

  def __init__(self, user, fs):
    self.fs = fs
    self.user = user

  def create_table_from_file(self, source, destination, start_time=-1, dry_run=False):
    if '.' in destination['name']:
      database, table_name = destination['name'].split('.', 1)
    else:
      database = 'default'
      table_name = destination['name']
    final_table_name = table_name

    source_type = source['sourceType']
    editor_type = '50'  # destination['sourceType']

    columns = destination['columns']

    # Until we have proper type convertion
    for col in columns:
      if col['type'] == 'string':
        col['type'] = 'VARCHAR'

    sql = '''CREATE TABLE IF NOT EXISTS %(table_name)s (
%(columns)s
CONSTRAINT my_pk PRIMARY KEY (%(primary_keys)s)
);
''' % {
          'database': database,
          'table_name': table_name,
          'columns': ',\n'.join(['  %(name)s %(type)s' % col for col in columns]),
          'primary_keys': ', '.join(destination.get('indexerPrimaryKey'))
      }

    if destination['indexerRunJob']:
      sql += '''
  UPSERT INTO %(table_name)s VALUES ('NY','New York',8143197);
  UPSERT INTO %(table_name)s VALUES ('CA','Los Angeles',3844829);
  UPSERT INTO %(table_name)s VALUES ('IL','Chicago',2842518);
  UPSERT INTO %(table_name)s VALUES ('TX','Houston',2016582);
  UPSERT INTO %(table_name)s VALUES ('PA','Philadelphia',1463281);
  UPSERT INTO %(table_name)s VALUES ('AZ','Phoenix',1461575);
  UPSERT INTO %(table_name)s VALUES ('TX','San Antonio',1256509);
  UPSERT INTO %(table_name)s VALUES ('CA','San Diego',1255540);
  UPSERT INTO %(table_name)s VALUES ('TX','Dallas',1213825);
  UPSERT INTO %(table_name)s VALUES ('CA','San Jose',91233);
  ''' % {
          'table_name': table_name,
        }

    if dry_run:
      return sql
    else:
      on_success_url = reverse('metastore:describe_table', kwargs={'database': database, 'table': final_table_name}) + \
          '?source_type=' + source_type

      return make_notebook(
          name=_('Creating table %(database)s.%(table)s') % {'database': database, 'table': final_table_name},
          editor_type=editor_type,
          statement=sql.strip(),
          status='ready',
          database=database,
          on_success_url=on_success_url,
          last_executed=start_time,
          is_task=True
      )
