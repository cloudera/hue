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
import urllib

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import ugettext as _

from desktop.lib import django_mako
from notebook.models import make_notebook


LOG = logging.getLogger(__name__)


try:
  from beeswax.server import dbms
except ImportError, e:
  LOG.warn('Hive and HiveServer2 interfaces are not enabled')


class SQLIndexer(object):

  def __init__(self, user, fs):
    self.fs = fs
    self.user = user

  def create_table_from_a_file(self, source, destination, start_time=-1):
    if '.' in destination['name']:
      database, table_name = destination['name'].split('.', 1)
    else:
      database = 'default'
      table_name = destination['name']
    final_table_name = table_name

    table_format = destination['tableFormat']
    source_type = source['sourceType']

    columns = destination['columns']
    partition_columns = destination['partitionColumns']
    kudu_partition_columns = destination['kuduPartitionColumns']
    comment = destination['description']

    source_path = urllib.unquote(source['path'])
    external = not destination['useDefaultLocation']
    external_path = urllib.unquote(destination['nonDefaultLocation'])

    load_data = destination['importData']
    skip_header = destination['hasHeader']

    primary_keys = destination['primaryKeys']

    if destination['useCustomDelimiters']:
      field_delimiter = destination['customFieldDelimiter']
      collection_delimiter = destination['customCollectionDelimiter']
      map_delimiter = destination['customMapDelimiter']
    else:
      field_delimiter = ','
      collection_delimiter = r'\002'
      map_delimiter = r'\003'
    regexp_delimiter = destination['customRegexp']

    file_format = 'TextFile'
    row_format = 'Delimited'
    serde_name = ''
    serde_properties = ''
    extra_create_properties = ''
    sql = ''

    if source['inputFormat'] == 'manual':
      load_data = False
      source['format'] = {
        'quoteChar': '"',
        'fieldSeparator': ','
      }

    if table_format == 'json':
      row_format = 'serde'
      serde_name = 'org.apache.hive.hcatalog.data.JsonSerDe'
    elif table_format == 'regexp':
      row_format = 'serde'
      serde_name = 'org.apache.hadoop.hive.serde2.RegexSerDe'
      serde_properties = '"input.regex" = "%s"' % regexp_delimiter
    elif table_format == 'csv':
      if source['format']['quoteChar'] == '"':
        source['format']['quoteChar'] = '\\"'
      row_format = 'serde'
      serde_name = 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
      serde_properties = '''"separatorChar" = "%(fieldSeparator)s",
    "quoteChar"     = "%(quoteChar)s",
    "escapeChar"    = "\\\\"
    ''' % source['format']


    if table_format in ('parquet', 'kudu'):
      if load_data:
        table_name, final_table_name = 'hue__tmp_%s' % table_name, table_name

        sql += '\n\nDROP TABLE IF EXISTS `%(database)s`.`%(table_name)s`;\n' % {
            'database': database,
            'table_name': table_name
        }
      else: # Manual
        row_format = ''
        file_format = table_format
        skip_header = False
        if table_format == 'kudu':
          columns = [col for col in columns if col['name'] in primary_keys] + [col for col in columns if col['name'] not in primary_keys]

    if table_format == 'kudu':
      collection_delimiter = None
      map_delimiter = None

    if external or (load_data and table_format in ('parquet', 'kudu')):
      if not self.fs.isdir(external_path): # File selected
        external_path, external_file_name = self.fs.split(external_path)

        if len(self.fs.listdir(external_path)) > 1:
          external_path = external_path + '/%s_table' % external_file_name # If dir not just the file, create data dir and move file there.
          self.fs.mkdir(external_path)
          self.fs.rename(source_path, external_path)

    sql += django_mako.render_to_string("gen/create_table_statement.mako", {
        'table': {
            'name': table_name,
            'comment': comment,
            'row_format': row_format,
            'field_terminator': field_delimiter,
            'collection_terminator': collection_delimiter if source_type == 'hive' else None,
            'map_key_terminator': map_delimiter if source_type == 'hive' else None,
            'serde_name': serde_name,
            'serde_properties': serde_properties,
            'file_format': file_format,
            'external': external or load_data and table_format in ('parquet', 'kudu'),
            'path': external_path,
            'skip_header': skip_header,
            'primary_keys': primary_keys if table_format == 'kudu' and not load_data else [],
         },
        'columns': columns,
        'partition_columns': partition_columns,
        'kudu_partition_columns': kudu_partition_columns,
        'database': database
      }
    )

    if table_format in ('text', 'json', 'csv', 'regexp') and not external and load_data:
      form_data = {
        'path': source_path,
        'overwrite': False,
        'partition_columns': [(partition['name'], partition['partitionValue']) for partition in partition_columns],
      }
      db = dbms.get(self.user)
      sql += "\n\n%s;" % db.load_data(database, table_name, form_data, None, generate_ddl_only=True)

    if load_data and table_format in ('parquet', 'kudu'):
      file_format = table_format
      if table_format == 'kudu':
        columns_list = ['`%s`' % col for col in primary_keys + [col['name'] for col in destination['columns'] if col['name'] not in primary_keys and col['keep']]]
        extra_create_properties = """PRIMARY KEY (%(primary_keys)s)
        PARTITION BY HASH PARTITIONS 16
        STORED AS %(file_format)s
        TBLPROPERTIES(
        'kudu.num_tablet_replicas' = '1'
        )""" % {
          'file_format': file_format,
          'primary_keys': ', '.join(primary_keys)
        }
      else:
        columns_list = ['*']
        extra_create_properties = 'STORED AS %(file_format)s' % {'file_format': file_format}
      sql += '''\n\nCREATE TABLE `%(database)s`.`%(final_table_name)s`%(comment)s
        %(extra_create_properties)s
        AS SELECT %(columns_list)s
        FROM `%(database)s`.`%(table_name)s`;''' % {
          'database': database,
          'final_table_name': final_table_name,
          'table_name': table_name,
          'extra_create_properties': extra_create_properties,
          'columns_list': ', '.join(columns_list),
          'comment': ' COMMENT "%s"' % comment if comment else ''
      }
      sql += '\n\nDROP TABLE IF EXISTS `%(database)s`.`%(table_name)s`;\n' % {
          'database': database,
          'table_name': table_name
      }

    editor_type = 'impala' if table_format == 'kudu' else destination['sourceType']

    on_success_url = reverse('metastore:describe_table', kwargs={'database': database, 'table': final_table_name}) + '?source_type=' + source_type

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
