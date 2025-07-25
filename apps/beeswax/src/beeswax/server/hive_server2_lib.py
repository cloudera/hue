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
import re
from operator import itemgetter

from django.utils.translation import gettext as _
from TCLIService import TCLIService
from TCLIService.ttypes import (
  TCancelOperationReq,
  TCloseOperationReq,
  TCloseSessionReq,
  TExecuteStatementReq,
  TFetchOrientation,
  TFetchResultsReq,
  TFetchResultsResp,
  TGetColumnsReq,
  TGetCrossReferenceReq,
  TGetFunctionsReq,
  TGetLogReq,
  TGetOperationStatusReq,
  TGetPrimaryKeysReq,
  TGetResultSetMetadataReq,
  TGetSchemasReq,
  TGetTablesReq,
  TOpenSessionReq,
  TRowSet,
  TStatusCode,
  TTypeId,
)

from beeswax import conf as beeswax_conf, hive_site
from beeswax.conf import CONFIG_WHITELIST, LIST_PARTITIONS_LIMIT, MAX_CATALOG_SQL_ENTRIES
from beeswax.hive_site import hiveserver2_use_ssl
from beeswax.models import HiveServerQueryHandle, HiveServerQueryHistory, Session
from beeswax.server.dbms import DataTable, InvalidSessionQueryServerException, QueryServerException, reset_ha, Table
from desktop.conf import DEFAULT_USER, ENABLE_X_CSRF_TOKEN_FOR_HIVE_IMPALA, ENABLE_XFF_FOR_HIVE_IMPALA, USE_THRIFT_HTTP_JWT
from desktop.lib import python_util, thrift_util
from notebook.connectors.base import get_interpreter

LOG = logging.getLogger()
IMPALA_RESULTSET_CACHE_SIZE = 'impala.resultset.cache.size'
DEFAULT_USER = DEFAULT_USER.get()


class HiveServerTable(Table):
  """
  We get the table details from a DESCRIBE FORMATTED.
  """

  def __init__(self, table_results, table_schema, desc_results, desc_schema):
    if beeswax_conf.THRIFT_VERSION.get() >= 7:
      if not table_results.columns:
        raise QueryServerException('No table columns')
      self.table = table_results.columns
    else:  # Deprecated. To remove in Hue 4.
      if not table_results.rows:
        raise QueryServerException('No table rows')
      self.table = table_results.rows and table_results.rows[0] or ''

    self.table_schema = table_schema
    self.desc_results = desc_results
    self.desc_schema = desc_schema
    self.is_impala_only = False  # Aka Kudu

    self.describe = HiveServerTTableSchema(self.desc_results, self.desc_schema).cols()
    self._details = None

  @property
  def name(self):
    return HiveServerTRow(self.table, self.table_schema).col('TABLE_NAME')

  @property
  def is_view(self):
    return HiveServerTRow(self.table, self.table_schema).col('TABLE_TYPE') == 'VIEW'

  @property
  def partition_keys(self):
    try:
      return [PartitionKeyCompatible(row['col_name'], row['data_type'], row['comment']) for row in self._get_partition_columns()]
    except Exception:
      LOG.exception('failed to get partition keys')
      return []

  @property
  def path_location(self):
    if self.is_impala_only:
      return None

    try:
      rows = self.describe
      rows = [row for row in rows if row['col_name'].startswith('Location:')]
      if rows:
        return rows[0]['data_type']
    except Exception:
      LOG.exception('failed to get path location')
      return None

  @property
  def cols(self):
    rows = self.describe
    col_row_index = 0
    try:
      cols = [col.strip() for col in map(itemgetter('col_name'), rows[col_row_index:])]
      # Hive MR/Impala have headers and one blank line, Hive Tez has nothing, Hive LLAP upstream has headers and no blank line
      if cols[0] == '# col_name':
        col_row_index = 1
        if not cols[1]:
          col_row_index += 1
        cols = cols[col_row_index:]
      end_cols_index = cols.index('')
      return rows[col_row_index:][:end_cols_index] + self._get_partition_columns()
    except ValueError:  # DESCRIBE on nested columns does not always contain additional rows beyond cols
      return rows[col_row_index:]
    except Exception:
      return rows

  def _get_partition_columns(self):
    rows = self.describe
    try:
      col_row_index = list(map(itemgetter('col_name'), rows)).index('# Partition Information') + 2
      if rows[col_row_index]['col_name'] == '':  # Impala has a blank line
        col_row_index += 1
      end_cols_index = list(map(itemgetter('col_name'), rows[col_row_index:])).index('')
      return rows[col_row_index:][:end_cols_index]
    except Exception:
      # Not partitioned
      return []

  def _parse_keys(self, key_name):
    rows = self.describe

    try:
      col_row_index = list(map(itemgetter('col_name'), rows)).index(key_name) + 3
      try:
        end_cols_index = list(map(itemgetter('col_name'), rows[col_row_index:])).index('')
        keys = rows[col_row_index:][:end_cols_index]
      except ValueError:
        keys = rows[col_row_index:]  # There was no other constraints afterwards
    except Exception:
      # No info (e.g. IMPALA-8291)
      keys = []

    return keys

  @property
  def primary_keys(self):
    # Note: Thrift has GetPrimaryKeys() API
    return [
      PartitionKeyCompatible(row['data_type'].strip(), 'NULL', row['comment']) for row in self._parse_keys(key_name='# Primary Key')
    ]

  @property
  def foreign_keys(self):
    # Note: Thrift has GetCrossReference() API
    return [
      PartitionKeyCompatible(
        row['data_type'].strip().split(':', 1)[1],  # from: Column Name:head
        row['col_name'].strip().split(':', 1)[1],  # to: Parent Column Name:default.persons.id
        row['comment']
      )
      for row in self._parse_keys(key_name='# Foreign Keys')
    ]

  @property
  def comment(self):
    return HiveServerTRow(self.table, self.table_schema).col('REMARKS')

  @property
  def properties(self):
    rows = self.describe
    col_row_index = 2
    try:
      end_cols_index = list(map(itemgetter('col_name'), rows[col_row_index:])).index('')
    except ValueError as e:
      end_cols_index = MAX_CATALOG_SQL_ENTRIES.get()
      LOG.warning('Could not guess end column index, so defaulting to %s: %s' % (end_cols_index, e))
    return [{
          'col_name': prop['col_name'].strip() if prop['col_name'] else prop['col_name'],
          'data_type': prop['data_type'].strip() if prop['data_type'] else prop['data_type'],
          'comment': prop['comment'].strip() if prop['comment'] else prop['comment']
        }
        for prop in rows[col_row_index + end_cols_index + 1:
      ]
    ]

  @property
  def stats(self):
    try:
      rows = self.properties
      col_row_index = list(map(itemgetter('col_name'), rows)).index('Table Parameters:') + 1
      end_cols_index = list(map(itemgetter('data_type'), rows[col_row_index:])).index(None)
      return rows[col_row_index:][:end_cols_index]
    except Exception:
      LOG.exception('Table stats could not be retrieved')
      return []

  @property
  def storage_details(self):
    rows = self.properties
    col_row_index = list(map(itemgetter('col_name'), rows)).index('Storage Desc Params:') + 1
    return rows[col_row_index:][:col_row_index + 2]

  @property
  def has_complex(self):
    has_complex = False
    complex_types = ["struct", "array", "map", "uniontype"]
    patterns = [re.compile(typ) for typ in complex_types]

    for column in self.cols:
      if isinstance(column, dict) and 'data_type' in column:
        column_type = column['data_type']
      else:  # Col object
        column_type = column.type
      if column_type and any(p.match(column_type.lower()) for p in patterns):
        has_complex = True
        break

    return has_complex

  @property
  def details(self):
    if self._details is None:
      props = dict([(stat['col_name'], stat['data_type']) for stat in self.properties if stat['col_name'] != 'Table Parameters:'])
      serde = props.get('SerDe Library:', '')
      if 'ParquetHiveSerDe' in serde:
        details_format = 'parquet'
      elif 'LazySimpleSerDe' in serde:
        details_format = 'text'
      elif self.is_impala_only:
        details_format = 'kudu'
      else:
        details_format = serde.rsplit('.', 1)[-1]

      self._details = {
          'stats': dict([(stat['data_type'], stat['comment']) for stat in self.stats]),
          'properties': {
            'owner': props.get('Owner:'),
            'create_time': props.get('CreateTime:'),
            'table_type': props.get('Table Type:', 'MANAGED_TABLE'),
            'format': details_format,
        }
      }

    return self._details


class HiveServerTRowSet2(object):
  def __init__(self, row_set, schema):
    self.row_set = row_set
    self.rows = row_set.rows
    self.schema = schema
    self.startRowOffset = row_set.startRowOffset

  def is_empty(self):
    return not self.row_set.columns or not HiveServerTColumnValue2(self.row_set.columns[0]).val

  def cols(self, col_names):
    cols_rows = []

    rs = HiveServerTRow2(self.row_set.columns, self.schema)
    cols = [rs.full_col(name) for name in col_names]

    for cols_row in zip(*cols):
      cols_rows.append(dict(zip(col_names, cols_row)))

    return cols_rows

  def __iter__(self):
    return self

  def __next__(self):
    if self.row_set.columns:
      return HiveServerTRow2(self.row_set.columns, self.schema)
    else:
      raise StopIteration


class HiveServerTRow2(object):
  def __init__(self, cols, schema):
    self.cols = cols
    self.schema = schema

  def col(self, colName):
    pos = self._get_col_position(colName)
    try:
      return HiveServerTColumnValue2(self.cols[pos]).val[0]  # Return only first element
    except Exception:
      # Bug with SparkSql
      return ''

  def full_col(self, colName):
    pos = self._get_col_position(colName)
    return HiveServerTColumnValue2(self.cols[pos]).val  # Return the full column and its values

  def _get_col_position(self, column_name):
    return list(filter(lambda i_col1: i_col1[1].columnName == column_name, enumerate(self.schema.columns)))[0][0]

  def fields(self):
    try:
      return [HiveServerTColumnValue2(field).val.pop(0) for field in self.cols]
    except IndexError:
      raise StopIteration


class HiveServerTColumnValue2(object):
  def __init__(self, tcolumn_value):
    self.column_value = tcolumn_value

  @property
  def val(self):
    # Could directly get index from schema but would need to cache the schema
    if self.column_value.stringVal:
      return self._get_val(self.column_value.stringVal)
    elif self.column_value.i16Val is not None:
      return self._get_val(self.column_value.i16Val)
    elif self.column_value.i32Val is not None:
      return self._get_val(self.column_value.i32Val)
    elif self.column_value.i64Val is not None:
      return self._get_val(self.column_value.i64Val)
    elif self.column_value.doubleVal is not None:
      return self._get_val(self.column_value.doubleVal)
    elif self.column_value.boolVal is not None:
      return self._get_val(self.column_value.boolVal)
    elif self.column_value.byteVal is not None:
      return self._get_val(self.column_value.byteVal)
    elif self.column_value.binaryVal is not None:
      return self._get_val(self.column_value.binaryVal)

  @classmethod
  def _get_val(cls, column):
    column.values = cls.set_nulls(column.values, column.nulls)
    column.nulls = ''  # Clear the null values for not re-marking again the column with nulls at the next call
    return column.values

  @classmethod
  def mark_nulls(cls, values, bytestring):
    if isinstance(bytestring, bytes):
      mask = bytearray(bytestring)
    else:
      bitstring = python_util.from_string_to_bits(bytestring)
      mask = python_util.get_bytes_from_bits(bitstring)

    for n in mask:
      yield n & 0x01
      yield n & 0x02
      yield n & 0x04
      yield n & 0x08

      yield n & 0x10
      yield n & 0x20
      yield n & 0x40
      yield n & 0x80

  @classmethod
  def set_nulls(cls, values, nulls):
    can_decode = True
    bytestring = nulls
    if isinstance(bytestring, bytes):
      try:
        bytestring = bytestring.decode('utf-8')
      except Exception:
        can_decode = False

    if bytestring == '' or (can_decode and re.match('^(\x00)+$', bytestring)):  # HS2 has just \x00 or '', Impala can have \x00\x00...
      return values
    else:
      _values = [None if is_null else value for value, is_null in zip(values, cls.mark_nulls(values, nulls))]
      if len(values) != len(_values):  # HS2 can have just \x00\x01 instead of \x00\x01\x00...
        _values.extend(values[len(_values):])
      return _values


class HiveServerDataTable(DataTable):
  def __init__(self, results, schema, operation_handle, query_server, session=None):
    self.schema = schema and schema.schema
    self.row_set = HiveServerTRowSet(results.results, schema)
    self.operation_handle = operation_handle
    if query_server.get('dialect') == 'impala':
      self.has_more = results.hasMoreRows
    else:
      self.has_more = not self.row_set.is_empty()    # Should be results.hasMoreRows but always True in HS2
    self.startRowOffset = self.row_set.startRowOffset    # Always 0 in HS2
    self.session = session

  @property
  def ready(self):
    return True

  def cols(self):
    if self.schema:
      return [HiveServerTColumnDesc(col) for col in self.schema.columns]
    else:
      return []

  def rows(self):
    for row in self.row_set:
      try:
        yield row.fields()
      except StopIteration:
        return  # pep-0479: expected Py3.8 generator raised StopIteration


class HiveServerTTableSchema(object):
  def __init__(self, columns, schema):
    self.columns = columns
    self.schema = schema

  def cols(self):
    try:
      return HiveServerTRowSet(self.columns, self.schema).cols(('col_name', 'data_type', 'comment'))
    except Exception:
      # Impala API is different
      cols = HiveServerTRowSet(self.columns, self.schema).cols(('name', 'type', 'comment'))
      for col in cols:
        col['col_name'] = col.pop('name')
        col['data_type'] = col.pop('type')
      return cols

  def col(self, colName):
    pos = self._get_col_position(colName)
    return HiveServerTColumnDesc(self.columns[pos]).val

  def _get_col_position(self, column_name):
    return list(filter(lambda i_col2: i_col2[1].columnName == column_name, enumerate(self.schema.columns)))[0][0]


if hasattr(beeswax_conf.THRIFT_VERSION, 'get') and beeswax_conf.THRIFT_VERSION.get() >= 7:
  HiveServerTRow = HiveServerTRow2
  HiveServerTRowSet = HiveServerTRowSet2
else:
  # Deprecated. To remove in Hue 4.
  class HiveServerTRow(object):
    def __init__(self, row, schema):
      self.row = row
      self.schema = schema

    def col(self, colName):
      pos = self._get_col_position(colName)
      return HiveServerTColumnValue(self.row.colVals[pos]).val

    def _get_col_position(self, column_name):
      return list(filter(lambda i_col: i_col[1].columnName == column_name, enumerate(self.schema.columns)))[0][0]

    def fields(self):
      return [HiveServerTColumnValue(field).val for field in self.row.colVals]

  class HiveServerTRowSet(object):
    def __init__(self, row_set, schema):
      self.row_set = row_set
      self.rows = row_set.rows
      self.schema = schema
      self.startRowOffset = row_set.startRowOffset

    def is_empty(self):
      return len(self.rows) == 0

    def cols(self, col_names):
      cols_rows = []
      for row in self.rows:
        row = HiveServerTRow(row, self.schema)
        cols = {}
        for col_name in col_names:
          cols[col_name] = row.col(col_name)
        cols_rows.append(cols)
      return cols_rows

    def __iter__(self):
      return self

    def __next__(self):
      if self.rows:
        return HiveServerTRow(self.rows.pop(0), self.schema)
      else:
        raise StopIteration


class HiveServerTColumnValue(object):
  def __init__(self, tcolumn_value):
    self.column_value = tcolumn_value

  @property
  def val(self):
    if self.column_value.boolVal is not None:
      return self.column_value.boolVal.value
    elif self.column_value.byteVal is not None:
      return self.column_value.byteVal.value
    elif self.column_value.i16Val is not None:
      return self.column_value.i16Val.value
    elif self.column_value.i32Val is not None:
      return self.column_value.i32Val.value
    elif self.column_value.i64Val is not None:
      return self.column_value.i64Val.value
    elif self.column_value.doubleVal is not None:
      return self.column_value.doubleVal.value
    elif self.column_value.stringVal is not None:
      return self.column_value.stringVal.value


class HiveServerTColumnDesc(object):
  def __init__(self, column):
    self.column = column

  @property
  def name(self):
    return self.column.columnName

  @property
  def comment(self):
    return self.column.comment

  @property
  def type(self):
    return self.get_type(self.column.typeDesc)

  @classmethod
  def get_type(self, typeDesc):
    for ttype in typeDesc.types:
      if ttype.primitiveEntry is not None:
        return TTypeId._VALUES_TO_NAMES[ttype.primitiveEntry.type]
      elif ttype.mapEntry is not None:
        return ttype.mapEntry
      elif ttype.unionEntry is not None:
        return ttype.unionEntry
      elif ttype.arrayEntry is not None:
        return ttype.arrayEntry
      elif ttype.structEntry is not None:
        return ttype.structEntry
      elif ttype.userDefinedTypeEntry is not None:
        return ttype.userDefinedTypeEntry


def extract_cookies(connection):
  if hasattr(connection, 'conf') and hasattr(connection.conf, 'transport_mode') and connection.conf.transport_mode == 'http':
    http_transport = connection.transport
    from thrift.transport.TTransport import TBufferedTransport
    if isinstance(http_transport, TBufferedTransport):
      http_transport = http_transport._TBufferedTransport__trans
    if hasattr(http_transport, '_client') and hasattr(http_transport._client, '_cookies'):
      cookies = http_transport._client._cookies
      from requests.utils import dict_from_cookiejar
      return dict_from_cookiejar(cookies) if cookies else {}


def set_cookies(connection, cookies):
  if hasattr(connection, 'conf') and hasattr(connection.conf, 'transport_mode') and connection.conf.transport_mode == 'http':
    http_transport = connection.transport
    from thrift.transport.TTransport import TBufferedTransport

    if isinstance(http_transport, TBufferedTransport):
      http_transport = http_transport._TBufferedTransport__trans
    if hasattr(http_transport, '_client') and hasattr(http_transport._client, '_cookies'):
      from requests.utils import cookiejar_from_dict
      http_transport._client._cookies = cookiejar_from_dict(cookies or {})


class HiveServerClient(object):
  HS2_MECHANISMS = {
      'KERBEROS': 'GSSAPI',
      'NONE': 'PLAIN',
      'NOSASL': 'NOSASL',
      'LDAP': 'PLAIN',
      'PAM': 'PLAIN',
      'CUSTOM': 'PLAIN',
  }

  DEFAULT_TABLE_TYPES = [
    'TABLE',
    'VIEW',
    'EXTERNAL_TABLE',
    'MATERIALIZED_VIEW',
  ]

  def __init__(self, query_server, user):
    self.query_server = query_server
    self.user = user
    self.coordinator_host = ''
    self.has_close_sessions = query_server.get('close_sessions', False)
    self.has_session_pool = query_server.get('has_session_pool', False)
    self.max_number_of_sessions = query_server.get('max_number_of_sessions', 1)

    use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled, auth_username, auth_password = self.get_security()
    LOG.info(
        '%s: server_host=%s, use_sasl=%s, mechanism=%s, kerberos_principal_short_name=%s, impersonation_enabled=%s, auth_username=%s' % (
        self.query_server['server_name'], self.query_server['server_host'], use_sasl, mechanism, kerberos_principal_short_name,
        impersonation_enabled, auth_username)
    )

    self.use_sasl = use_sasl
    self.kerberos_principal_short_name = kerberos_principal_short_name
    self.impersonation_enabled = impersonation_enabled

    if self.query_server.get('dialect') == 'impala':
      from impala import conf as impala_conf

      ssl_enabled = impala_conf.SSL.ENABLED.get()
      ca_certs = impala_conf.SSL.CACERTS.get()
      keyfile = impala_conf.SSL.KEY.get()
      certfile = impala_conf.SSL.CERT.get()
      validate = impala_conf.SSL.VALIDATE.get()
      timeout = impala_conf.SERVER_CONN_TIMEOUT.get()
    else:
      ssl_enabled = hiveserver2_use_ssl()
      ca_certs = beeswax_conf.SSL.CACERTS.get()
      keyfile = beeswax_conf.SSL.KEY.get()
      certfile = beeswax_conf.SSL.CERT.get()
      validate = beeswax_conf.SSL.VALIDATE.get()
      timeout = beeswax_conf.SERVER_CONN_TIMEOUT.get()

    if auth_username and not USE_THRIFT_HTTP_JWT.get():
      username = auth_username
      password = auth_password
    else:
      username = user.username
      password = None

    thrift_class = TCLIService
    if self.query_server.get('dialect') == 'impala':
      from ImpalaService import ImpalaHiveServer2Service
      thrift_class = ImpalaHiveServer2Service

    LOG.debug('Using %s for host_name %s' % (thrift_class, query_server['server_host']))

    self._client = thrift_util.get_client(
        thrift_class.Client,
        query_server['server_host'],
        query_server['server_port'],
        service_name=query_server['server_name'],
        kerberos_principal=kerberos_principal_short_name,
        use_sasl=use_sasl,
        mechanism=mechanism,
        username=username,
        password=password,
        timeout_seconds=timeout,
        use_ssl=ssl_enabled,
        ca_certs=ca_certs,
        keyfile=keyfile,
        certfile=certfile,
        validate=validate,
        transport_mode=query_server.get('transport_mode', 'socket'),
        http_url=query_server.get('http_url', ''),
        coordinator_host=self.coordinator_host
    )

  def get_security(self):
    principal = self.query_server['principal']
    impersonation_enabled = False
    auth_username = self.query_server['auth_username']  # Pass-through LDAP/PAM authentication
    auth_password = self.query_server['auth_password']

    if principal:
      kerberos_principal_short_name = principal.split('/', 1)[0]
    else:
      kerberos_principal_short_name = None

    use_sasl = self.query_server['use_sasl']  # Coming from dialect conf.USE_SASL
    if self.query_server.get('dialect') == 'impala':
      if auth_password:  # Force LDAP/PAM.. auth if auth_password is provided
        mechanism = HiveServerClient.HS2_MECHANISMS['NONE']
      else:
        mechanism = HiveServerClient.HS2_MECHANISMS['KERBEROS']
      impersonation_enabled = self.query_server['impersonation_enabled']
    else:
      hive_mechanism = hive_site.get_hiveserver2_authentication()
      if hive_mechanism not in HiveServerClient.HS2_MECHANISMS:
        raise Exception(
          _('%s server authentication not supported. Valid are %s.') % (hive_mechanism, list(HiveServerClient.HS2_MECHANISMS.keys()))
        )
      mechanism = HiveServerClient.HS2_MECHANISMS[hive_mechanism]
      impersonation_enabled = hive_site.hiveserver2_impersonation_enabled()

    return use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled, auth_username, auth_password

  def open_session(self, user):
    self.user = user
    kwargs = {
        'client_protocol': beeswax_conf.THRIFT_VERSION.get() - 1,
        'username': user.username,  # If SASL or LDAP, it gets the username from the authentication mechanism since it dependents on it.
        'configuration': {},
    }
    connector_type = 'hive' if self.query_server['server_name'] == 'beeswax' else self.query_server['server_name']
    interpreter_dialect = self.query_server['dialect']
    if not interpreter_dialect:
      interpreter = get_interpreter(connector_type=connector_type, user=self.user)
      interpreter_dialect = interpreter.get('dialect')

    if self.impersonation_enabled:
      kwargs.update({'username': DEFAULT_USER})

      if self.query_server.get('dialect') == 'impala':  # Only when Impala accepts it
        kwargs['configuration'].update({'impala.doas.user': user.username})

    if self.query_server['server_name'] == 'beeswax' or \
        (self.query_server.get('is_compute') and self.query_server.get('dialect') == 'hive'):
      kwargs['configuration'].update({'hive.server2.proxy.user': user.username})
      xff_header = json.loads(user.userprofile.json_data).get('X-Forwarded-For', None)
      if xff_header and ENABLE_XFF_FOR_HIVE_IMPALA.get():
        kwargs['configuration'].update({'X-Forwarded-For': xff_header})
      csrf_header = json.loads(user.userprofile.json_data).get('X-CSRF-TOKEN')
      if csrf_header and ENABLE_X_CSRF_TOKEN_FOR_HIVE_IMPALA.get():
        kwargs['configuration'].update({'X-CSRF-TOKEN': csrf_header})

    if self.query_server['server_name'] == 'hplsql' or interpreter_dialect == 'hplsql':  # All the time
      kwargs['configuration'].update({'hive.server2.proxy.user': user.username, 'set:hivevar:mode': 'HPLSQL'})

    if self.query_server['server_name'] == 'llap':  # All the time
      kwargs['configuration'].update({'hive.server2.proxy.user': user.username})

    if self.query_server['server_name'] == 'sparksql':  # All the time
      kwargs['configuration'].update({'hive.server2.proxy.user': user.username})

    if self.query_server.get('dialect') == 'impala' and self.query_server['SESSION_TIMEOUT_S'] > 0:
      kwargs['configuration'].update({'idle_session_timeout': str(self.query_server['SESSION_TIMEOUT_S'])})
      xff_header = json.loads(user.userprofile.json_data).get('X-Forwarded-For', None)
      if xff_header and ENABLE_XFF_FOR_HIVE_IMPALA.get():
        kwargs['configuration'].update({'X-Forwarded-For': xff_header})
      csrf_header = json.loads(user.userprofile.json_data).get('X-CSRF-TOKEN', None)
      if csrf_header and ENABLE_X_CSRF_TOKEN_FOR_HIVE_IMPALA.get():
        kwargs['configuration'].update({'X-CSRF-TOKEN': csrf_header})

    LOG.info('Opening %s thrift session for user %s' % (self.query_server['server_name'], user.username))

    try:
      req = TOpenSessionReq(**kwargs)
    except Exception as e:
      if 'Connection refused' in str(e):
        reset_ha()
    res = self._client.OpenSession(req)
    self.coordinator_host = self._client.get_coordinator_host()
    if self.coordinator_host:
      res.configuration['coordinator_host'] = self.coordinator_host

    if res.status is not None and res.status.statusCode not in (TStatusCode.SUCCESS_STATUS,):
      if hasattr(res.status, 'errorMessage') and res.status.errorMessage:
        message = res.status.errorMessage
      else:
        message = ''

      raise QueryServerException(Exception('Bad status for request %s:\n%s' % (req, res)), message=message)

    sessionId = res.sessionHandle.sessionId
    LOG.info('Session %s opened' % repr(sessionId.guid))

    cookies = extract_cookies(self._client) or {}  # Extract cookies from the response
    res.configuration['cookies'] = cookies

    encoded_status, encoded_guid = HiveServerQueryHandle(secret=sessionId.secret, guid=sessionId.guid).get()
    properties = json.dumps(res.configuration)

    session = Session.objects.create(
        owner=user,
        application=self.query_server['server_name'],
        status_code=res.status.statusCode,
        secret=encoded_status,
        guid=encoded_guid,
        server_protocol_version=res.serverProtocolVersion,
        properties=properties
    )

    # HS2 does not return properties in TOpenSessionResp
    # TEZ returns properties, but we need the configuration to detect engine
    properties = session.get_properties() or {}
    if not properties or self.query_server['server_name'] == 'beeswax':
      configuration = self.get_configuration(session=session)
      properties.update(configuration)
      session.properties = json.dumps(properties)
      session.save()

    return session

  def call(self, fn, req, status=TStatusCode.SUCCESS_STATUS, session=None):
    return self.call_return_result_and_session(fn, req, status, session=session)

  def call_return_result_and_session(self, fn, req, status=TStatusCode.SUCCESS_STATUS, session=None):
    if not hasattr(req, 'sessionHandle'):
      return self._call_return_result_and_session(fn, req, status=TStatusCode.SUCCESS_STATUS, session=session)

    if session:
      if session.status_code not in (
        TStatusCode.SUCCESS_STATUS, TStatusCode.SUCCESS_WITH_INFO_STATUS, TStatusCode.STILL_EXECUTING_STATUS):
        LOG.info('Retrying with a new session for %s because status is %s' % (self.user, str(session.status_code)))
        session = None
      else:
        try:
          return self._call_return_result_and_session(fn, req, status=status, session=session)
        except InvalidSessionQueryServerException as e:
          LOG.info('Retrying with a new session because for %s of %s' % (self.user, str(e)))

    if self.has_session_pool:
      session = Session.objects.get_tez_session(self.user, self.query_server['server_name'], self.max_number_of_sessions)
    elif self.max_number_of_sessions == 1:  # Default behaviour: reuse opened session
      session = Session.objects.get_session(self.user, self.query_server['server_name'])

    if session:
      try:
        return self._call_return_result_and_session(fn, req, status=status, session=session)
      except InvalidSessionQueryServerException as e:
        LOG.info('Retrying with a new session because for %s of %s' % (self.user, str(e)))

    if self.has_close_sessions and self.max_number_of_sessions > 1 and \
        Session.objects.get_n_sessions(
            self.user,
            n=self.max_number_of_sessions,
            application=self.query_server['server_name']
        ).count() >= self.max_number_of_sessions:
      raise Exception('Too many open sessions. Stop a running query before starting a new one')

    session = self.open_session(self.user)

    return self._call_return_result_and_session(fn, req, status=status, session=session)

  def _call_return_result_and_session(self, fn, req, status=TStatusCode.SUCCESS_STATUS, session=None):
    if hasattr(req, 'sessionHandle') and session and not isinstance(req, TCloseOperationReq):
      req.sessionHandle = session.get_handle()
    cookies = session.get_cookies() if session else {}
    set_cookies(self._client, cookies)
    LOG.debug('setting cookies for call req: %s, session: %s, cookies: %s' % (req, session, cookies))

    res = fn(req)

    cookies = extract_cookies(self._client) or {}  # Extract cookies from the response
    LOG.debug('storing cookies received from server cookies: %s' % cookies)
    if hasattr(res, 'configuration') and isinstance(res.configuration, dict):
      res.configuration['cookies'] = cookies
    if session:
      session.set_cookies(cookies)
      session.save()

    # Not supported currently in HS2 and Impala: TStatusCode.INVALID_HANDLE_STATUS
    if res.status.statusCode == TStatusCode.ERROR_STATUS and \
      re.search('Invalid SessionHandle|Invalid session|Client session expired|Could not connect', res.status.errorMessage or '', re.I):
      if session:
        session.status_code = TStatusCode.INVALID_HANDLE_STATUS
        session.save()
      raise InvalidSessionQueryServerException(Exception('Invalid Session %s:\n%s' % (req, res)))

    if status is not None and res.status.statusCode not in (
      TStatusCode.SUCCESS_STATUS, TStatusCode.SUCCESS_WITH_INFO_STATUS, TStatusCode.STILL_EXECUTING_STATUS):
      if hasattr(res.status, 'errorMessage') and res.status.errorMessage:
        message = res.status.errorMessage
      else:
        message = 'Bad status for request %s:\n%s' % (req, res)
      raise QueryServerException(Exception(message), message=message)
    else:
      return (res, session)

  def close_session(self, session):
    req = TCloseSessionReq(sessionHandle=session.get_handle())
    try:
      res = self._client.CloseSession(req)
      session.status_code = TStatusCode.INVALID_HANDLE_STATUS
      session.save()
      return res
    except Exception as e:
      session.status_code = TStatusCode.ERROR_STATUS
      session.save()
      raise e

  def get_databases(self, schemaName=None):
    # GetCatalogs() is not implemented in HS2
    req = TGetSchemasReq()
    if schemaName is not None:
      req.schemaName = schemaName
    if self.query_server.get('dialect') in ['impala', 'sparksql']:
      req.schemaName = None

    (res, session) = self.call(self._client.GetSchemas, req)

    results, schema = self.fetch_result(
      res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=MAX_CATALOG_SQL_ENTRIES.get(),
      session=session
    )
    self._close(res.operationHandle, session)

    col = 'TABLE_SCHEM'
    return HiveServerTRowSet(results.results, schema.schema).cols((col,))

  def get_database(self, database):
    query = 'DESCRIBE DATABASE EXTENDED `%s`' % (database)

    desc_results, desc_schema, operation_handle, session = self.execute_statement(
      query, max_rows=MAX_CATALOG_SQL_ENTRIES.get(), orientation=TFetchOrientation.FETCH_NEXT
    )
    self._close(operation_handle, session)

    if self.query_server.get('dialect') == 'impala':
      cols = ('name', 'location', 'comment')  # Skip owner as on a new line
    else:
      cols = ('db_name', 'comment', 'location', 'owner_name', 'owner_type', 'parameters')

#     try:
#       if len(HiveServerTRowSet(desc_results.results, desc_schema.schema).cols(cols)) != 1:
#         raise ValueError(_("%(query)s returned more than 1 row") % {'query': query})
#     except Exception, e:
#       print e
#       raise e

    return HiveServerTRowSet(desc_results.results, desc_schema.schema).cols(cols)[0]  # Should only contain one row

  def get_tables_meta(self, database, table_names, table_types=None):
    if not table_types:
      table_types = self.DEFAULT_TABLE_TYPES
    req = TGetTablesReq(schemaName=database, tableName=table_names, tableTypes=table_types)
    (res, session) = self.call(self._client.GetTables, req)

    table_metadata = []
    cols = ('TABLE_NAME', 'TABLE_TYPE', 'REMARKS')

    while True:
      results, schema = self.fetch_result(
        res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=MAX_CATALOG_SQL_ENTRIES.get(),
        session=session
      )
      fetched_tables = HiveServerTRowSet(results.results, schema.schema).cols(cols)
      table_metadata += fetched_tables

      if len(fetched_tables) == 0 or MAX_CATALOG_SQL_ENTRIES.get() == len(table_metadata):
        break

    self._close(res.operationHandle, session)
    return table_metadata

  def get_tables(self, database, table_names, table_types=None):
    if not table_types:
      table_types = self.DEFAULT_TABLE_TYPES
    req = TGetTablesReq(schemaName=database, tableName=table_names, tableTypes=table_types)
    (res, session) = self.call(self._client.GetTables, req)

    results, schema = self.fetch_result(
      res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=MAX_CATALOG_SQL_ENTRIES.get(),
      session=session
    )
    self._close(res.operationHandle, session)

    return HiveServerTRowSet(results.results, schema.schema).cols(('TABLE_NAME',))

  def get_table(self, database, table_name, partition_spec=None):
    req = TGetTablesReq(schemaName=database.lower(), tableName=table_name.lower())  # Impala returns empty if not lower case
    (res, session) = self.call(self._client.GetTables, req)

    table_results, table_schema = self.fetch_result(res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT, session=session)
    self.close_operation(res.operationHandle)

    if partition_spec:
      query = 'DESCRIBE FORMATTED `%s`.`%s` PARTITION(%s)' % (database, table_name, partition_spec)
    else:
      query = 'DESCRIBE FORMATTED `%s`.`%s`' % (database, table_name)

    try:
      desc_results, desc_schema, operation_handle, session = self.execute_statement(
          query,
          max_rows=10000,
          orientation=TFetchOrientation.FETCH_NEXT,
          session=session
      )
      self.close_operation(operation_handle)
    except Exception as e:
      ex_string = str(e)
      if 'cannot find field' in ex_string:  # Workaround until Hive 2.0 and HUE-3751
        desc_results, desc_schema, operation_handle, session = self.execute_statement('USE `%s`' % database, session=session)
        self.close_operation(operation_handle)
        if partition_spec:
          query = 'DESCRIBE FORMATTED `%s` PARTITION(%s)' % (table_name, partition_spec)
        else:
          query = 'DESCRIBE FORMATTED `%s`' % table_name
        desc_results, desc_schema, operation_handle, session = self.execute_statement(
            query,
            max_rows=10000,
            orientation=TFetchOrientation.FETCH_NEXT,
            session=session
        )
        self.close_operation(operation_handle)
      elif 'not have privileges for DESCTABLE' in ex_string \
          or 'AuthorizationException' in ex_string:  # HUE-5608: No table permission but some column permissions
        query = 'DESCRIBE `%s`.`%s`' % (database, table_name)
        desc_results, desc_schema, operation_handle, session = self.execute_statement(
            query,
            max_rows=10000,
            orientation=TFetchOrientation.FETCH_NEXT,
            session=session
        )
        self.close_operation(operation_handle)

        desc_results.results.columns[0].stringVal.values.insert(0, '# col_name')
        desc_results.results.columns[0].stringVal.values.insert(1, '')
        desc_results.results.columns[1].stringVal.values.insert(0, 'data_type')
        desc_results.results.columns[1].stringVal.values.insert(1, None)
        desc_results.results.columns[2].stringVal.values.insert(0, 'comment')
        desc_results.results.columns[2].stringVal.values.insert(1, None)
        try:
          part_index = desc_results.results.columns[0].stringVal.values.index('# Partition Information')
          # Strip duplicate columns of partitioned tables
          desc_results.results.columns[0].stringVal.values = desc_results.results.columns[0].stringVal.values[:part_index]
          desc_results.results.columns[1].stringVal.values = desc_results.results.columns[1].stringVal.values[:part_index]
          desc_results.results.columns[2].stringVal.values = desc_results.results.columns[2].stringVal.values[:part_index]

          desc_results.results.columns[1].stringVal.nulls = ''  # Important to not clear the last two types

          desc_results.results.columns[1].stringVal.values[-1] = None
          desc_results.results.columns[2].stringVal.values[-1] = None
        except ValueError:
          desc_results.results.columns[0].stringVal.values.append('')
          desc_results.results.columns[1].stringVal.values.append(None)
          desc_results.results.columns[2].stringVal.values.append(None)
      else:
        raise e
    finally:
      if self.has_close_sessions:
        self.close_session(session)

    return HiveServerTable(table_results.results, table_schema.schema, desc_results.results, desc_schema.schema)

  def execute_query(self, query, max_rows=1000, session=None):
    configuration = self._get_query_configuration(query)
    return self.execute_query_statement(statement=query.query['query'], max_rows=max_rows, configuration=configuration, session=session)

  def execute_query_statement(self, statement, max_rows=1000, configuration=None, orientation=TFetchOrientation.FETCH_FIRST,
      close_operation=False, session=None):
    if configuration is None:
      configuration = {}

    results, schema, operation_handle, session = self.execute_statement(
        statement=statement,
        max_rows=max_rows,
        configuration=configuration,
        orientation=orientation,
        session=session
    )

    if close_operation:
      self.close_operation(operation_handle, session=session)

    return HiveServerDataTable(results, schema, operation_handle, self.query_server, session=session)

  def execute_async_query(self, query, statement=0, session=None):
    if statement == 0:
      # Impala just has settings currently
      if self.query_server['server_name'] == 'beeswax':
        for resource in query.get_configuration_statements():
          self.execute_statement(resource.strip(), session=session)

    configuration = {}

    if self.query_server.get('dialect') == 'impala' and self.query_server['querycache_rows'] > 0:
      configuration[IMPALA_RESULTSET_CACHE_SIZE] = str(self.query_server['querycache_rows'])

    # The query can override the default configuration
    configuration.update(self._get_query_configuration(query))
    query_statement = query.get_query_statement(statement)

    return self.execute_async_statement(statement=query_statement, conf_overlay=configuration, session=session)

  def execute_statement(self, statement, max_rows=1000, configuration=None, orientation=TFetchOrientation.FETCH_NEXT, session=None):
    if configuration is None:
      configuration = {}
    if self.query_server.get('dialect') == 'impala' and self.query_server['QUERY_TIMEOUT_S'] > 0:
      configuration['QUERY_TIMEOUT_S'] = str(self.query_server['QUERY_TIMEOUT_S'])

    req = TExecuteStatementReq(statement=statement, confOverlay=configuration)
    (res, session) = self.call(self._client.ExecuteStatement, req, session=session)

    results, schema = self.fetch_result(res.operationHandle, max_rows=max_rows, orientation=orientation, session=session)
    return results, schema, res.operationHandle, session

  def execute_async_statement(self, statement=None, thrift_function=None, thrift_request=None, conf_overlay=None, session=None):
    if conf_overlay is None:
      conf_overlay = {}
    if thrift_function is None:
      thrift_function = self._client.ExecuteStatement
    if thrift_request is None:
      thrift_request = TExecuteStatementReq(statement=statement, confOverlay=conf_overlay, runAsync=True)

    if self.query_server.get('dialect') == 'impala' and self.query_server['QUERY_TIMEOUT_S'] > 0:
      conf_overlay['QUERY_TIMEOUT_S'] = str(self.query_server['QUERY_TIMEOUT_S'])

    (res, session) = self.call_return_result_and_session(thrift_function, thrift_request, session=session)

    return HiveServerQueryHandle(
        secret=res.operationHandle.operationId.secret,
        guid=res.operationHandle.operationId.guid,
        operation_type=res.operationHandle.operationType,
        has_result_set=res.operationHandle.hasResultSet,
        modified_row_count=res.operationHandle.modifiedRowCount,
        session_guid=thrift_util.unpack_guid(session.get_handle().sessionId.guid),
        session_id=session.id
    )

  # Note: An operation_handle is attached to a session. All operations that require operation_handle cannot recover if the session is
  # closed. Passing the session is not required
  def fetch_data(self, operation_handle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=1000, session=None):
    # Fetch until the result is empty dues to a HS2 bug instead of looking at hasMoreRows
    results, schema = self.fetch_result(operation_handle, orientation, max_rows, session=session)
    return HiveServerDataTable(results, schema, operation_handle, self.query_server)

  def cancel_operation(self, operation_handle, session=None):
    req = TCancelOperationReq(operationHandle=operation_handle)
    (res, session) = self.call(self._client.CancelOperation, req, session=session)
    return res

  def close_operation(self, operation_handle, session=None):
    req = TCloseOperationReq(operationHandle=operation_handle)
    (res, session) = self.call(self._client.CloseOperation, req, session=session)
    return res

  def fetch_result(self, operation_handle, orientation=TFetchOrientation.FETCH_FIRST, max_rows=1000, session=None):
    if operation_handle.hasResultSet:
      fetch_req = TFetchResultsReq(operationHandle=operation_handle, orientation=orientation, maxRows=max_rows)
      (res, session) = self.call(self._client.FetchResults, fetch_req, session=session)
    else:
      res = TFetchResultsResp(results=TRowSet(startRowOffset=0, rows=[], columns=[]))

    if operation_handle.hasResultSet and TFetchOrientation.FETCH_FIRST:  # Only fetch for the first call that should be with start_over
      meta_req = TGetResultSetMetadataReq(operationHandle=operation_handle)
      (schema, session) = self.call(self._client.GetResultSetMetadata, meta_req, session=session)
    else:
      schema = None

    return res, schema

  def fetch_log(self, operation_handle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=1000, session=None):
    req = TFetchResultsReq(operationHandle=operation_handle, orientation=orientation, maxRows=max_rows, fetchType=1)
    (res, session) = self.call(self._client.FetchResults, req, session=session)

    if beeswax_conf.THRIFT_VERSION.get() >= 7:
      lines = res.results.columns[0].stringVal.values
    else:
      lines = list(map(lambda r: r.colVals[0].stringVal.value, res.results.rows))

    return '\n'.join(lines)

  def get_operation_status(self, operation_handle, session=None):
    req = TGetOperationStatusReq(operationHandle=operation_handle)
    (res, session) = self.call(self._client.GetOperationStatus, req, session=session)
    return res

  def get_log(self, operation_handle, session=None):
    try:
      req = TGetLogReq(operationHandle=operation_handle)
      (res, session) = self.call(self._client.GetLog, req, session=session)
      return res.log
    except Exception as e:
      if 'Invalid query handle' in str(e) or 'Invalid or unknown query handle' in str(e):
        message = 'Invalid or unknown query handle'
        LOG.error('%s: %s' % (message, e))
      else:
        message = 'Error when fetching the logs of the operation.'
        LOG.exception(message)

      return message

  def _close(self, operation_handle, session):
    if self.has_close_sessions:  # Close session will close all associated operation_handle
      self.close_session(session)
    else:
      self.close_operation(operation_handle, session=session)

  def get_columns(self, database, table):
    req = TGetColumnsReq(schemaName=database, tableName=table)
    (res, session) = self.call(self._client.GetColumns, req)

    results, schema = self.fetch_result(res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT, session=session)
    self._close(res.operationHandle, session)

    return results, schema

  def explain(self, query):
    query_statement = query.get_query_statement(0)
    configuration = self._get_query_configuration(query)
    return self.execute_query_statement(statement='EXPLAIN %s' % query_statement, configuration=configuration,
                                        orientation=TFetchOrientation.FETCH_NEXT)

  # TODO execute both requests in same session
  def get_partitions(self, database, table_name, partition_spec=None, max_parts=None, reverse_sort=True):
    table = self.get_table(database, table_name)

    query = 'SHOW PARTITIONS `%s`.`%s`' % (database, table_name)
    if self.query_server['server_name'] == 'beeswax' and partition_spec:
      query += ' PARTITION(%s)' % partition_spec

    # We fetch N partitions then reverse the order later and get the max_parts. Use partition_spec to refine more the initial list.
    # Need to fetch more like this until SHOW PARTITIONS offers a LIMIT and ORDER BY
    partition_table = self.execute_query_statement(query, max_rows=10000, orientation=TFetchOrientation.FETCH_NEXT, close_operation=True)

    if self.has_close_sessions:
      self.close_session(partition_table.session)

    if self.query_server.get('dialect') == 'impala':
      try:
        # Fetch all partition key names, which are listed before the #Rows column
        cols = [col.name for col in partition_table.cols()]
        try:
          stop = cols.index('#Rows')
        except ValueError:
          stop = -1
        partition_keys = cols[:stop]
        num_parts = len(partition_keys)

        # Get all partition values
        rows = partition_table.rows()
        partition_values = [partition[:num_parts] for partition in rows]

        # Truncate last row which is the Total
        partition_values = partition_values[:-1]
        partitions_formatted = []

        # Format partition key and values into Hive format: [key1=val1/key2=value2]
        for values in partition_values:
          zipped_parts = zip(partition_keys, values)
          partitions_formatted.append(['/'.join(['%s=%s' % (str(part[0]), str(part[1])) for part in zipped_parts if all(part)])])

        partitions = [PartitionValueCompatible(partition, table) for partition in partitions_formatted]
      except Exception:
        raise ValueError(_('Failed to determine partition keys for Impala table: `%s`.`%s`') % (database, table_name))
    else:
      partitions = [PartitionValueCompatible(partition, table) for partition in partition_table.rows()]

    if reverse_sort:
      partitions.reverse()

    if max_parts is None or max_parts <= 0:
      max_parts = LIST_PARTITIONS_LIMIT.get()

    return partitions[:max_parts]

  def get_configuration(self, session=None):
    configuration = {}

    if self.query_server.get('dialect') == 'impala':  # Return all configuration settings
      query = 'SET'
      results = self.execute_query_statement(query, orientation=TFetchOrientation.FETCH_NEXT, close_operation=True, session=session)
      configuration = dict((row[0], row[1]) for row in results.rows())
    else:  # For Hive, only return white-listed configurations
      query = 'SET -v'
      results = self.execute_query_statement(
          query,
          orientation=TFetchOrientation.FETCH_FIRST,
          max_rows=-1,
          close_operation=True,
          session=session
      )
      config_whitelist = [config.lower() for config in CONFIG_WHITELIST.get()]
      properties = [(row[0].split('=')[0], row[0].split('=')[1]) for row in results.rows() if '=' in row[0]]
      configuration = dict((prop, value) for prop, value in properties if prop.lower() in config_whitelist)

    return configuration

  def _get_query_configuration(self, query):
    return dict([(setting['key'], setting['value']) for setting in query.settings])

  def get_functions(self):
    '''
    Could support parameters.

    Result data is pretty limited, e.g.
    [None, None, 'histogram_numeric', '', 1, 'org.apache.hadoop.hive.ql.exec.WindowFunctionInfo']

    GetAllFunctionsResponse get_all_functions() would also be nice as more detailed it seems, but this would be a call to HMS.
    '''
    req = TGetFunctionsReq(functionName='.*')
    thrift_function = self._client.GetFunctions

    return self.execute_async_statement(thrift_function=thrift_function, thrift_request=req)

  def get_primary_keys(self, database_name, table_name, catalog_name=None):
    '''
    Get the Primary Keys of a Table entity (seems like database name is required).

    e.g. Primary Keys of the sales.order table: schema_name='sales' table_name='orders'

    Example of result:
    [
      {
        'TABLE_CAT': None, 'TABLE_SCHEM': 'default', 'TABLE_NAME': 'business_unit', 'COLUMN_NAME': 'id',
        'KEQ_SEQ': 1, 'PK_NAME': 'pk_245553536_1595688608351_0'
      }
    ]
    '''
    req = TGetPrimaryKeysReq(
      catalogName=catalog_name,
      schemaName=database_name,
      tableName=table_name
    )

    (res, session) = self.call(self._client.GetPrimaryKeys, req)
    results, schema = self.fetch_result(res.operationHandle, max_rows=100)

    self._close(res.operationHandle, session)

    results = HiveServerTRowSet(results.results, schema.schema).cols(
      (
        'TABLE_CAT', 'TABLE_SCHEM', 'TABLE_NAME', 'COLUMN_NAME', 'KEQ_SEQ', 'PK_NAME'
      )
    )

    return results

  def get_foreign_keys(self, parent_catalog_name=None, parent_database_name=None, parent_table_name=None, foreign_catalog_name=None,
      foreign_database_name=None, foreign_table_name=None):
    '''
    Get the Foreign Keys between two entities (e.g. Catalog, DB, Tables).

    e.g. Foreign Keys between the two tables people.customers and sales.orders:
      parent_database_name='people', parent_table_name='customers'
      foreign_database_name='sales', foreign_table_name='orders'

    Table names are also optional.

    Example of result:
    [
      {
        'PKTABLE_CAT': None, 'PKTABLE_SCHEM': 'default', 'PKTABLE_NAME': 'person', 'PKCOLUMN_NAME': 'id',
        'FKTABLE_CAT': None, 'FKTABLE_SCHEM': 'default', 'FKTABLE_NAME': 'business_unit', 'FKCOLUMN_NAME': 'head',
        'KEQ_SEQ': 1, 'UPDATE_RULE': 0, 'DELETE_RULE': 0,
        'FK_NAME': 'fk',
        'PK_NAME': 'pk_146568770_1595688607640_0',
        'DEFERRABILITY': 0
      }
    ]
    '''
    req = TGetCrossReferenceReq(
      parentCatalogName=parent_catalog_name,
      parentSchemaName=parent_database_name,
      parentTableName=parent_table_name,
      foreignCatalogName=foreign_catalog_name,
      foreignSchemaName=foreign_database_name,
      foreignTableName=foreign_table_name
    )

    (res, session) = self.call(self._client.GetCrossReference, req)
    results, schema = self.fetch_result(res.operationHandle, max_rows=100)

    self._close(res.operationHandle, session)

    results = HiveServerTRowSet(results.results, schema.schema).cols(
      (
        'PKTABLE_CAT', 'PKTABLE_SCHEM', 'PKTABLE_NAME', 'PKCOLUMN_NAME',
        'FKTABLE_CAT', 'FKTABLE_SCHEM', 'FKTABLE_NAME', 'FKCOLUMN_NAME',
        'KEQ_SEQ', 'UPDATE_RULE', 'DELETE_RULE', 'FK_NAME', 'PK_NAME', 'DEFERRABILITY'
      )
    )

    return results


class HiveServerTableCompatible(HiveServerTable):
  """Same API as Beeswax"""

  def __init__(self, hive_table):
    self.table = hive_table.table
    self.table_schema = hive_table.table_schema
    self.desc_results = hive_table.desc_results
    self.desc_schema = hive_table.desc_schema

    self.describe = HiveServerTTableSchema(self.desc_results, self.desc_schema).cols()
    self._details = None
    try:
      self.is_impala_only = 'org.apache.hadoop.hive.kudu.KuduSerDe' in str(hive_table.properties) or \
        'org.apache.kudu.mapreduce.KuduTableOutputFormat' in str(hive_table.properties)  # Deprecated since CDP
    except Exception as e:
      LOG.warning('Autocomplete data fetching error: %s' % e)
      self.is_impala_only = False

  @property
  def cols(self):
    return [
        type('Col', (object,), {
          'name': col.get('col_name', '').strip() if col.get('col_name') else '',
          'type': col.get('data_type', '').strip() if col.get('data_type') else '',
          'comment': col.get('comment', '').strip() if col.get('comment') else ''
        })
        for col in HiveServerTable.cols.fget(self)
    ]


class ResultCompatible(object):

  def __init__(self, data_table):
    self.data_table = data_table
    self.rows = data_table.rows
    self.has_more = data_table.has_more
    self.start_row = data_table.startRowOffset
    self.ready = True

  @property
  def columns(self):
    return self.cols()

  def cols(self):
    return [col.name for col in self.data_table.cols()]

  def full_cols(self):
    return [{'name': col.name, 'type': col.type, 'comment': col.comment} for col in self.data_table.cols()]


class PartitionKeyCompatible(object):

  def __init__(self, name, type, comment):
    self.name = name
    self.type = type
    self.comment = comment

  def __eq__(self, other):
    return isinstance(other, PartitionKeyCompatible) and \
        self.name == other.name and \
        self.type == other.type and \
        self.comment == other.comment

  def __repr__(self):
    return 'PartitionKey(name:%s, type:%s, comment:%s)' % (self.name, self.type, self.comment)


class PartitionValueCompatible(object):

  def __init__(self, partition_row, table, properties=None):
    self.partition_keys = table.partition_keys
    if properties is None:
      properties = {}
    # Parses: ['datehour=2013022516'] or ['month=2011-07/dt=2011-07-01/hr=12']
    partition = partition_row[0]
    parts = partition.split('/')
    self.partition_spec = ','.join([self._get_partition_spec(pv[0], pv[1]) for pv in [part.split('=') for part in parts]])
    self.values = [pv[1] for pv in [part.split('=') for part in parts]]
    self.sd = type('Sd', (object,), properties,)

  def __repr__(self):
    return 'PartitionValueCompatible(spec:%s, values:%s, sd:%s)' % (self.partition_spec, self.values, self.sd)

  def _get_partition_spec(self, name, value):
    partition_spec = "`%s`='%s'" % (name, value)
    partition_key = next((key for key in self.partition_keys if key.name == name), None)
    if partition_key and partition_key.type.upper() not in ('STRING', 'CHAR', 'VARCHAR', 'TIMESTAMP', 'DATE'):
      partition_spec = "`%s`=%s" % (name, value)
    return partition_spec


class ExplainCompatible(object):

  def __init__(self, data_table):
    self.textual = '\n'.join([line[0] for line in data_table.rows()])


class ResultMetaCompatible(object):

  def __init__(self):
    self.in_tablename = True


class HiveServerClientCompatible(object):
  """Same API as Beeswax"""

  def __init__(self, client):
    self._client = client
    self.user = client.user
    self.query_server = client.query_server

  def query(self, query, statement=0, session=None):
    return self._client.execute_async_query(query, statement, session=session)

  def get_state(self, handle):
    operationHandle = handle.get_rpc_handle()
    session = handle.get_session()
    res = self._client.get_operation_status(operationHandle, session=session)
    return HiveServerQueryHistory.STATE_MAP[res.operationState]

  def get_operation_status(self, handle):
    operationHandle = handle.get_rpc_handle()
    session = handle.get_session()
    return self._client.get_operation_status(operationHandle, session=session)

  def use(self, query, session=None):
    data = self._client.execute_query(query, session=session)
    self._client.close_operation(data.operation_handle, session=session)
    return data

  def explain(self, query):
    data_table = self._client.explain(query)
    data = ExplainCompatible(data_table)
    self._client.close_operation(data_table.operation_handle)
    return data

  def fetch(self, handle, start_over=False, max_rows=None):
    operationHandle = handle.get_rpc_handle()
    session = handle.get_session()
    if max_rows is None:
      max_rows = 1000

    if start_over and not (self.query_server.get('dialect') == 'impala' and self.query_server['querycache_rows'] == 0):
      orientation = TFetchOrientation.FETCH_FIRST  # Backward compatibility for impala
    else:
      orientation = TFetchOrientation.FETCH_NEXT

    data_table = self._client.fetch_data(operationHandle, orientation=orientation, max_rows=max_rows, session=session)

    return ResultCompatible(data_table)

  def cancel_operation(self, handle):
    operationHandle = handle.get_rpc_handle()
    session = handle.get_session()
    return self._client.cancel_operation(operationHandle, session=session)

  def close(self, handle):
    return self.close_operation(handle)

  def close_operation(self, handle):
    operationHandle = handle.get_rpc_handle()
    session = handle.get_session()
    return self._client.close_operation(operationHandle, session=session)

  def close_session(self, session):
    return self._client.close_session(session)

  def dump_config(self):
    return 'Does not exist in HS2'

  def get_log(self, handle, start_over=True):
    operationHandle = handle.get_rpc_handle()
    session = handle.get_session()

    if beeswax_conf.USE_GET_LOG_API.get() or self.query_server.get('dialect') == 'impala':
      return self._client.get_log(operationHandle, session=session)
    else:
      if start_over:
        orientation = TFetchOrientation.FETCH_FIRST
      else:
        orientation = TFetchOrientation.FETCH_NEXT

      return self._client.fetch_log(operationHandle, orientation=orientation, max_rows=-1, session=session)

  def get_databases(self, schemaName=None):
    col = 'TABLE_SCHEM'
    return [table[col] for table in self._client.get_databases(schemaName)]

  def get_database(self, database):
    return self._client.get_database(database)

  def get_tables_meta(self, database, table_names, table_types=None):
    tables = self._client.get_tables_meta(database, table_names, table_types)
    massaged_tables = []
    for table in tables:
      massaged_tables.append({
          'name': table['TABLE_NAME'],
          'comment': table['REMARKS'],
          'type': table['TABLE_TYPE'].capitalize()
        }
      )
    massaged_tables = sorted(massaged_tables, key=lambda table_: table_['name'])
    return massaged_tables

  def get_tables(self, database, table_names, table_types=None):
    tables = [table['TABLE_NAME'] for table in self._client.get_tables(database, table_names, table_types)]
    tables.sort()
    return tables

  def get_table(self, database, table_name, partition_spec=None):
    table = self._client.get_table(database, table_name, partition_spec)
    return HiveServerTableCompatible(table)

  def get_columns(self, database, table):
    return self._client.get_columns(database, table)

  def get_default_configuration(self, *args, **kwargs):
    return []

  def get_results_metadata(self, handle):
    # We just need to mock
    return ResultMetaCompatible()

  def create_database(self, name, description): raise NotImplementedError()

  def alter_table(self, dbname, tbl_name, new_tbl): raise NotImplementedError()

  def open_session(self, user):
    return self._client.open_session(user)

  def add_partition(self, new_part): raise NotImplementedError()

  def get_partition(self, *args, **kwargs): raise NotImplementedError()

  def get_partitions(self, database, table_name, partition_spec, max_parts, reverse_sort=True):
    return self._client.get_partitions(database, table_name, partition_spec, max_parts, reverse_sort)

  def alter_partition(self, db_name, tbl_name, new_part): raise NotImplementedError()

  def get_configuration(self):
    return self._client.get_configuration()

  def get_functions(self):
    return self._client.get_functions()
