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

import csv
import logging
import sys
import uuid
from django.urls import reverse

from notebook.conf import get_ordered_interpreters
from notebook.models import make_notebook

if sys.version_info[0] > 2:
  from io import StringIO as string_io
  from urllib.parse import urlparse, unquote as urllib_unquote
  from django.utils.translation import gettext as _
else:
  from cStringIO import StringIO as string_io
  from django.utils.translation import ugettext as _
  from urllib import unquote as urllib_unquote
  from urlparse import urlparse


LOG = logging.getLogger()


class PhoenixIndexer():

  def __init__(self, user, fs):
    self.fs = fs
    self.user = user

  def create_table_from_file(self, request, source, destination, start_time=-1, dry_run=False):
    if '.' in destination['name']:
      database, table_name = destination['name'].split('.', 1)
    else:
      database = 'default'
      table_name = destination['name']
    final_table_name = table_name

    source_type = [interpreter['type'] for interpreter in get_ordered_interpreters(self.user) if interpreter['dialect'] == 'phoenix'][0]
    editor_type = source_type

    columns = destination['columns']

    # Until we have proper type convertion
    for col in columns:
      if col['type'] == 'string':
        col['type'] = 'varchar'

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

    source_path = urllib_unquote(source['path'])
    if source['inputFormat'] == 'file':
      file_obj = request.fs.open(source_path)
      content = file_obj.read().decode("utf-8")
      csvfile = string_io(content)
      reader = csv.reader(csvfile)
    else:
      local_file = open(source_path, 'r')
      reader = csv.reader(local_file)

    if destination['indexerRunJob']:
      for count, csv_row in enumerate(reader):
        if (source['format']['hasHeader'] and count == 0) or not csv_row:
            continue
        else:
          _sql = ', '.join([ "'{0}'".format(col_val) if columns[count]['type'] in ('varchar', 'timestamp') \
            else '{0}'.format(col_val) for count, col_val in enumerate(csv_row)])

          sql += '''\nUPSERT INTO %(table_name)s VALUES (%(csv_row)s);\n''' % {
            'database': database,
            'table_name': table_name,
            'csv_row': _sql
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
