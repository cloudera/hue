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

from django.urls import reverse

from notebook.models import make_notebook

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class FlinkIndexer():

  def __init__(self, user, fs):
    self.fs = fs
    self.user = user

  def create_table_from_kafka(self, source, destination, start_time=-1, dry_run=False):
    if '.' in destination['name']:
      database, table_name = destination['name'].split('.', 1)
    else:
      database = 'default'
      table_name = destination['name']
    final_table_name = table_name

    source_type = source['sourceType']

    from desktop.api_public import _get_interpreter_from_dialect   # due to a circular import
    interpreter = _get_interpreter_from_dialect('flink', self.user)
    editor_type = interpreter['type']  # destination['sourceType']

    columns = destination['columns']

    sql = '''CREATE TABLE %(table_name)s (
%(columns)s
) WITH (
  'connector' = 'kafka',
  'topic' = '%(topic)s',
  'scan.startup.mode' = 'earliest-offset',
  'properties.bootstrap.servers' = 'kafka:9094',
  'format' = 'json'
);''' % {
          'database': database,
          'table_name': table_name,
          'columns': ',\n'.join(['  %(name)s %(type)s' % col for col in columns]),
          'topic': source.get('kafkaSelectedTopics')
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
