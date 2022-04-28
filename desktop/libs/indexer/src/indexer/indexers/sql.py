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

from future import standard_library
standard_library.install_aliases()
from builtins import object
import csv
import logging
import sys
import urllib.request, urllib.error
import uuid

from collections import OrderedDict

from django.urls import reverse

from azure.abfs.__init__ import abfspath
from hadoop.fs.hadoopfs import Hdfs
from notebook.connectors.base import get_interpreter
from notebook.models import make_notebook
from useradmin.models import User
from impala.conf import USER_SCRATCH_DIR_PERMISSION

from desktop.lib import django_mako
from desktop.lib.exceptions_renderable import PopupException
from desktop.settings import BASE_DIR

if sys.version_info[0] > 2:
  from urllib.parse import urlparse, unquote as urllib_unquote
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
  from urllib import unquote as urllib_unquote
  from urlparse import urlparse


LOG = logging.getLogger(__name__)


try:
  from beeswax.server import dbms
except ImportError as e:
  LOG.warning('Hive and HiveServer2 interfaces are not enabled')


class SQLIndexer(object):

  def __init__(self, user, fs):
    self.fs = fs
    self.user = user

  def create_table_from_a_file(self, source, destination, start_time=-1, file_encoding=None):
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

    source_path = urllib_unquote(source['path'])
    load_data = destination['importData']
    external = not destination['useDefaultLocation']
    external_path = urllib_unquote(destination['nonDefaultLocation'])

    editor_type = destination['sourceType']
    is_transactional = destination['isTransactional']
    default_transactional_type = 'insert_only' if destination['isInsertOnly'] else 'default'

    skip_header = destination.get('hasHeader')

    primary_keys = destination['primaryKeys']

    if destination['useCustomDelimiters']:
      field_delimiter = destination['customFieldDelimiter']
      collection_delimiter = destination['customCollectionDelimiter'] or None
      map_delimiter = destination['customMapDelimiter'] or None
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

    use_temp_table = table_format in ('parquet', 'orc', 'kudu') or is_transactional
    if use_temp_table: # We'll be using a temp table to load data
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

    if external or (load_data and table_format in ('parquet', 'orc', 'kudu')): # We'll use location to load data
      if not self.fs.isdir(external_path): # File selected
        external_path, external_file_name = Hdfs.split(external_path)

        if len(self.fs.listdir(external_path)) > 1:
          # If dir not just the file, create data dir and move file there. Make sure it's unique.
          external_path = external_path + '/%s%s_table' % (external_file_name, str(uuid.uuid4()))
          self.fs.mkdir(external_path)
          self.fs.rename(source_path, external_path)
    elif load_data: # We'll use load data command
      parent_path = self.fs.parent_path(source_path)
      stats = self.fs.stats(parent_path)
      split = urlparse(source_path)
      # Only for HDFS, import data and non-external table
      if split.scheme in ('', 'hdfs') and oct(stats["mode"])[-1] != '7':
        user_scratch_dir = self.fs.get_home_dir() + '/.scratchdir/%s' % str(uuid.uuid4()) # Make sure it's unique.
        self.fs.do_as_user(self.user, self.fs.mkdir, user_scratch_dir, 0o0777)
        self.fs.do_as_user(self.user, self.fs.rename, source['path'], user_scratch_dir)
        if USER_SCRATCH_DIR_PERMISSION.get():
          self.fs.do_as_user(self.user, self.fs.chmod, user_scratch_dir, 0o0777, True)
        source_path = user_scratch_dir + '/' + source['path'].split('/')[-1]

    if external_path.lower().startswith("abfs"): #this is to check if its using an ABFS path
      external_path = abfspath(external_path)

    tbl_properties = OrderedDict()
    if skip_header:
      tbl_properties['skip.header.line.count'] = '1'
    # The temp table is not transactional, but final table can be if is_transactional.
    # tbl_properties that don't exist in previous versions can safely be added without error.
    tbl_properties['transactional'] = 'false'

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
            'external': external or load_data and table_format in ('parquet', 'orc', 'kudu'),
            'path': external_path,
            'primary_keys': primary_keys if table_format == 'kudu' and not load_data else [],
            'tbl_properties': tbl_properties
         },
        'columns': columns,
        'partition_columns': partition_columns,
        'kudu_partition_columns': kudu_partition_columns,
        'database': database
      }
    )
    if file_encoding and file_encoding != 'ASCII' and file_encoding != 'utf-8' and not use_temp_table:
      sql += '\n\nALTER TABLE `%(database)s`.`%(final_table_name)s` ' \
             'SET serdeproperties ("serialization.encoding"="%(file_encoding)s");' % {
                 'database': database,
                 'final_table_name': final_table_name,
                 'file_encoding': file_encoding
             }

    if table_format in ('text', 'json', 'csv', 'regexp') and not external and load_data:
      form_data = {
        'path': source_path,
        'overwrite': False,
        'partition_columns': [(partition['name'], partition['partitionValue']) for partition in partition_columns],
      }
      query_server_config = dbms.get_query_server_config(name=source_type)
      db = dbms.get(self.user, query_server=query_server_config)
      sql += "\n\n%s;" % db.load_data(database, table_name, form_data, None, generate_ddl_only=True)

    if load_data and use_temp_table:
      file_format = 'TextFile' if table_format == 'text' else table_format
      if table_format == 'kudu':
        columns_list = [
            '`%s`' % col for col in primary_keys
            +
            [col['name'] for col in destination['columns'] if col['name'] not in primary_keys and col['keep']]
        ]
        extra_create_properties = """PRIMARY KEY (%(primary_keys)s)
        PARTITION BY HASH PARTITIONS 16
        STORED AS %(file_format)s
        TBLPROPERTIES(
        'kudu.num_tablet_replicas'='1'
        )""" % {
          'file_format': file_format,
          'primary_keys': ', '.join(primary_keys)
        }
      else:
        columns_list = ['*']
        extra_create_properties = 'STORED AS %(file_format)s' % {'file_format': file_format}
        if is_transactional:
          extra_create_properties += "\nTBLPROPERTIES('transactional'='true', 'transactional_properties'='%s')" % \
              default_transactional_type

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
      if file_encoding and file_encoding != 'ASCII' and file_encoding != 'utf-8':
        sql += '\n\nALTER TABLE `%(database)s`.`%(final_table_name)s` ' \
               'SET serdeproperties ("serialization.encoding"="%(file_encoding)s");' % {
            'database': database,
            'final_table_name': final_table_name,
            'file_encoding': file_encoding
        }

    on_success_url = reverse(
        'metastore:describe_table', kwargs={'database': database, 'table': final_table_name}
    ) + '?source_type=' + source_type

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

  def nomalize_booleans(self, row, columns):
    for cnt, col in enumerate(columns):
      if col['type'] == 'boolean':
        if row[cnt] in ('T', 't', 'true', 'True', 'TRUE', '1'):
          row[cnt] = '1'
        elif row[cnt] in ('F', 'f', 'false', 'False', 'FALSE', '0'):
          row[cnt] = '0'
        else:
          row[cnt] = 'NULL'
    return row

  def create_table_from_local_file(self, source, destination, start_time=-1):
    if '.' in destination['name']:
      database, table_name = destination['name'].split('.', 1)
    else:
      database = 'default'
      table_name = destination['name']
    final_table_name = table_name

    source_type = source['sourceType']
    editor_type = destination['sourceType']

    cols_to_remove = sorted(
      [col_index for col_index, col in enumerate(destination['columns']) if not col['keep']],
      reverse=True
    )
    columns = [col for col_index, col in enumerate(destination['columns']) if col_index not in cols_to_remove]

    dialect = get_interpreter(source_type, self.user)['dialect']
    tmp_table_name = table_name

    if dialect in ('hive', 'mysql'):

      if dialect == 'mysql':
        for col in columns:
          if col['type'] == 'string':
            col['type'] = 'VARCHAR(255)'

      sql = '''CREATE TABLE IF NOT EXISTS %(database)s.%(table_name)s (
%(columns)s);\n''' % {
        'database': database,
        'table_name': table_name,
        'columns': ',\n'.join(['  `%(name)s` %(type)s' % col for col in columns]),
      }

    elif dialect == 'impala':
      tmp_table_name = tmp_table_name + '_tmp'
      sql = '''CREATE TABLE IF NOT EXISTS %(database)s.%(table_name)s (
%(columns)s);\n''' % {
          'database': database,
          'table_name': tmp_table_name,
          'columns': ',\n'.join(['  `%(name)s` string' % col for col in columns]),
      }                                                 # Impala does not implicitly cast between string and numeric or Boolean types.

    path = urllib_unquote(source['path'])

    if path:                                                  # data insertion
      with open(path, 'r') as local_file:
        reader = csv.reader(local_file)
        _csv_rows = []

        for count, row in enumerate(reader):
          if (source['format']['hasHeader'] and count == 0) or not row:
            continue
          for col_index in cols_to_remove:
            del row[col_index]
          if dialect == 'impala':                         # for the boolean col updating csv_val to (1,0)
            row = self.nomalize_booleans(row, columns)
          _csv_rows.append(tuple(row))

        if _csv_rows:

          insert_sql = ""
          for count in range(1 + len(_csv_rows)//5000):      # Inserting 5000 (decided through testing on some files) rows through one sql
            temp_list = _csv_rows[count*5000:(count+1)*5000] # statement as we can get memory issue if we insert all rows in one statement.
            if len(temp_list) == 0:
              break
            csv_rows = str(temp_list)[1:-1]
            insert_sql += '''\nINSERT INTO %(database)s.%(table_name)s VALUES %(csv_rows)s;\n'''% {
              'database': database,
              'table_name': tmp_table_name,
              'csv_rows': csv_rows
            }

          if dialect in ('hive', 'mysql'):
            sql += insert_sql

          elif dialect == 'impala':
             # casting from string to boolean is not allowed in impala so string -> int -> bool
            sql_ = ',\n'.join([
              '  CAST ( `%(name)s` AS %(type)s ) `%(name)s`' % col if col['type'] != 'boolean' \
              else '  CAST ( CAST ( `%(name)s` AS TINYINT ) AS boolean ) `%(name)s`' % col for col in columns
            ])
            sql += insert_sql
            sql += '''\nCREATE TABLE IF NOT EXISTS %(database)s.%(table_name)s
AS SELECT\n%(sql_)s\nFROM  %(database)s.%(table_name)s_tmp;\n\nDROP TABLE IF EXISTS %(database)s.%(table_name)s_tmp;'''% {
              'database': database,
              'table_name': table_name,
              'csv_rows': csv_rows,
              'sql_': sql_
            }

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
  on_success_url = reverse(
      'metastore:show_tables',
      kwargs={'database': database}) + "?source_type=" + source.get('sourceType', 'hive'
  )

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


def _create_table(request, source, destination, start_time=-1, file_encoding=None):
  notebook = SQLIndexer(user=request.user, fs=request.fs).create_table_from_a_file(source, destination, start_time, file_encoding)

  if request.POST.get('show_command'):
    return {'status': 0, 'commands': notebook.get_str()}
  else:
    return notebook.execute(request, batch=False)

def _create_table_from_local(request, source, destination, start_time=-1):
  notebook = SQLIndexer(user=request.user, fs=request.fs).create_table_from_local_file(source, destination, start_time)

  if request.POST.get('show_command'):
    return {'status': 0, 'commands': notebook.get_str()}
  else:
    return notebook.execute(request, batch=False)
