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

import logging
import itertools
import json
import re

from itertools import imap, izip
from operator import itemgetter

from django.utils.translation import ugettext as _

from desktop.lib import thrift_util
from desktop.conf import DEFAULT_USER
from desktop.models import Document2
from beeswax import conf
from hadoop import cluster

from TCLIService import TCLIService
from TCLIService.ttypes import TOpenSessionReq, TGetTablesReq, TFetchResultsReq,\
  TStatusCode, TGetResultSetMetadataReq, TGetColumnsReq, TTypeId,\
  TExecuteStatementReq, TGetOperationStatusReq, TFetchOrientation,\
  TCloseSessionReq, TGetSchemasReq, TGetLogReq, TCancelOperationReq,\
  TCloseOperationReq, TFetchResultsResp, TRowSet

from beeswax import conf as beeswax_conf
from beeswax import hive_site
from beeswax.hive_site import hiveserver2_use_ssl
from beeswax.conf import CONFIG_WHITELIST, LIST_PARTITIONS_LIMIT
from beeswax.models import Session, HiveServerQueryHandle, HiveServerQueryHistory, QueryHistory
from beeswax.server.dbms import Table, DataTable, QueryServerException


LOG = logging.getLogger(__name__)

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
    else: # Deprecated. To remove in Hue 4.
      if not table_results.rows:
        raise QueryServerException('No table rows')
      self.table = table_results.rows and table_results.rows[0] or ''

    self.table_schema = table_schema
    self.desc_results = desc_results
    self.desc_schema = desc_schema
    self.is_impala_only = False # Aka Kudu

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
      return [PartitionKeyCompatible(row['col_name'], row['data_type'], row['comment']) for row in self._get_partition_column()]
    except:
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
    except:
      LOG.exception('failed to get path location')
      return None

  @property
  def cols(self):
    rows = self.describe
    col_row_index = 1
    try:
      cols = map(itemgetter('col_name'), rows[col_row_index:])
      if cols.index('') == 0: # TEZ starts at 1 vs Hive, Impala starts at 2
        col_row_index = col_row_index + 1
        cols.pop(0)
      end_cols_index = cols.index('')
      return rows[col_row_index:][:end_cols_index] + self._get_partition_column()
    except ValueError:  # DESCRIBE on columns and nested columns does not always contain additional rows beyond cols
      return rows[col_row_index:]
    except:
      # Impala does not have it
      return rows

  def _get_partition_column(self):
    rows = self.describe
    try:
      col_row_index = map(itemgetter('col_name'), rows).index('# Partition Information') + 3
      end_cols_index = map(itemgetter('col_name'), rows[col_row_index:]).index('')
      return rows[col_row_index:][:end_cols_index]
    except:
      # Impala does not have it
      return []

  @property
  def comment(self):
    return HiveServerTRow(self.table, self.table_schema).col('REMARKS')

  @property
  def properties(self):
    rows = self.describe
    col_row_index = 2
    try:
      end_cols_index = map(itemgetter('col_name'), rows[col_row_index:]).index('')
    except ValueError as e:
      end_cols_index = 5000
      LOG.warn('Could not guess end column index, so defaulting to %s: %s' (end_cols_index, e))
    return [{
          'col_name': prop['col_name'].strip() if prop['col_name'] else prop['col_name'],
          'data_type': prop['data_type'].strip() if prop['data_type'] else prop['data_type'],
          'comment': prop['comment'].strip() if prop['comment'] else prop['comment']
        } for prop in rows[col_row_index + end_cols_index + 1:]
    ]

  @property
  def stats(self):
    try:
      rows = self.properties
      col_row_index = map(itemgetter('col_name'), rows).index('Table Parameters:') + 1
      end_cols_index = map(itemgetter('data_type'), rows[col_row_index:]).index(None)
      return rows[col_row_index:][:end_cols_index]
    except:
      LOG.exception('Table stats could not be retrieved')
      return []

  @property
  def storage_details(self):
    rows = self.properties
    col_row_index = map(itemgetter('col_name'), rows).index('Storage Desc Params:') + 1
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

      self._details = {
          'stats': dict([(stat['data_type'], stat['comment']) for stat in self.stats]),
          'properties': {
            'owner': props.get('Owner:'),
            'create_time': props.get('CreateTime:'),
            'table_type': props.get('Table Type:', 'MANAGED_TABLE'),
            'format': 'parquet' if 'ParquetHiveSerDe' in serde else ('text' if 'LazySimpleSerDe' in serde else ('kudu' if self.is_impala_only else serde.rsplit('.', 1)[-1])),
        }
      }

    return self._details


class HiveServerTRowSet2:
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

    for cols_row in itertools.izip(*cols):
      cols_rows.append(dict(itertools.izip(col_names, cols_row)))

    return cols_rows

  def __iter__(self):
    return self

  def next(self):
    if self.row_set.columns:
      return HiveServerTRow2(self.row_set.columns, self.schema)
    else:
      raise StopIteration


class HiveServerTRow2:
  def __init__(self, cols, schema):
    self.cols = cols
    self.schema = schema

  def col(self, colName):
    pos = self._get_col_position(colName)
    return HiveServerTColumnValue2(self.cols[pos]).val[0] # Return only first element

  def full_col(self, colName):
    pos = self._get_col_position(colName)
    return HiveServerTColumnValue2(self.cols[pos]).val # Return the full column and its values

  def _get_col_position(self, column_name):
    return filter(lambda (i, col): col.columnName == column_name, enumerate(self.schema.columns))[0][0]

  def fields(self):
    try:
      return [HiveServerTColumnValue2(field).val.pop(0) for field in self.cols]
    except IndexError:
      raise StopIteration


class HiveServerTColumnValue2:
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
    column.nulls = '' # Clear the null values for not re-marking again the column with nulls at the next call
    return column.values

  @classmethod
  def mark_nulls(cls, values, bytestring):
    mask = bytearray(bytestring)

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
  def set_nulls(cls, values, bytestring):
    if bytestring == '' or re.match('^(\x00)+$', bytestring): # HS2 has just \x00 or '', Impala can have \x00\x00...
      return values
    else:
      _values = [None if is_null else value for value, is_null in itertools.izip(values, cls.mark_nulls(values, bytestring))]
      if len(values) != len(_values): # HS2 can have just \x00\x01 instead of \x00\x01\x00...
        _values.extend(values[len(_values):])
      return _values


class HiveServerDataTable(DataTable):
  def __init__(self, results, schema, operation_handle, query_server):
    self.schema = schema and schema.schema
    self.row_set = HiveServerTRowSet(results.results, schema)
    self.operation_handle = operation_handle
    if query_server['server_name'].startswith('impala'):
      self.has_more = results.hasMoreRows
    else:
      self.has_more = not self.row_set.is_empty()    # Should be results.hasMoreRows but always True in HS2
    self.startRowOffset = self.row_set.startRowOffset    # Always 0 in HS2

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
      yield row.fields()



class HiveServerTTableSchema:
  def __init__(self, columns, schema):
    self.columns = columns
    self.schema = schema

  def cols(self):
    try:
      return HiveServerTRowSet(self.columns, self.schema).cols(('col_name', 'data_type', 'comment'))
    except:
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
    return filter(lambda (i, col): col.columnName == column_name, enumerate(self.schema.columns))[0][0]


if hasattr(beeswax_conf.THRIFT_VERSION, 'get') and beeswax_conf.THRIFT_VERSION.get() >= 7:
  HiveServerTRow = HiveServerTRow2
  HiveServerTRowSet = HiveServerTRowSet2
else:
  # Deprecated. To remove in Hue 4.
  class HiveServerTRow:
    def __init__(self, row, schema):
      self.row = row
      self.schema = schema

    def col(self, colName):
      pos = self._get_col_position(colName)
      return HiveServerTColumnValue(self.row.colVals[pos]).val

    def _get_col_position(self, column_name):
      return filter(lambda (i, col): col.columnName == column_name, enumerate(self.schema.columns))[0][0]

    def fields(self):
      return [HiveServerTColumnValue(field).val for field in self.row.colVals]

  class HiveServerTRowSet:
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

    def next(self):
      if self.rows:
        return HiveServerTRow(self.rows.pop(0), self.schema)
      else:
        raise StopIteration


class HiveServerTColumnValue:
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


class HiveServerTColumnDesc:
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


class HiveServerClient:
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
  ]

  def __init__(self, query_server, user):
    self.query_server = query_server
    self.user = user
    self.coordinator_host = ''

    use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled, auth_username, auth_password = self.get_security()
    LOG.info(
        '%s: server_host=%s, use_sasl=%s, mechanism=%s, kerberos_principal_short_name=%s, impersonation_enabled=%s, auth_username=%s' % (
        self.query_server['server_name'], self.query_server['server_host'], use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled, auth_username)
    )

    self.use_sasl = use_sasl
    self.kerberos_principal_short_name = kerberos_principal_short_name
    self.impersonation_enabled = impersonation_enabled

    if self.query_server['server_name'].startswith('impala'):
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

    if auth_username:
      username = auth_username
      password = auth_password
    else:
      username = user.username
      password = None

    thrift_class = TCLIService
    if self.query_server['server_name'].startswith('impala'):
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
    auth_username = self.query_server['auth_username'] # Pass-through LDAP/PAM authentication
    auth_password = self.query_server['auth_password']

    if principal:
      kerberos_principal_short_name = principal.split('/', 1)[0]
    else:
      kerberos_principal_short_name = None

    if self.query_server['server_name'].startswith('impala'):
      if auth_password: # Force LDAP/PAM.. auth if auth_password is provided
        use_sasl = True
        mechanism = HiveServerClient.HS2_MECHANISMS['NONE']
      else:
        cluster_conf = cluster.get_cluster_conf_for_job_submission()
        use_sasl = cluster_conf is not None and cluster_conf.SECURITY_ENABLED.get()
        mechanism = HiveServerClient.HS2_MECHANISMS['KERBEROS']
      impersonation_enabled = self.query_server['impersonation_enabled']
    else:
      hive_mechanism = hive_site.get_hiveserver2_authentication()
      if hive_mechanism not in HiveServerClient.HS2_MECHANISMS:
        raise Exception(_('%s server authentication not supported. Valid are %s.') % (hive_mechanism, HiveServerClient.HS2_MECHANISMS.keys()))
      use_sasl = hive_mechanism in ('KERBEROS', 'NONE', 'LDAP', 'PAM')
      mechanism = HiveServerClient.HS2_MECHANISMS[hive_mechanism]
      impersonation_enabled = hive_site.hiveserver2_impersonation_enabled()

    return use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled, auth_username, auth_password


  def open_session(self, user):

    self.user = user
    kwargs = {
        'client_protocol': beeswax_conf.THRIFT_VERSION.get() - 1,
        'username': user.username, # If SASL or LDAP, it gets the username from the authentication mechanism" since it dependents on it.
        'configuration': {},
    }

    if self.impersonation_enabled:
      kwargs.update({'username': DEFAULT_USER})

      if self.query_server['server_name'].startswith('impala'): # Only when Impala accepts it
        kwargs['configuration'].update({'impala.doas.user': user.username})

    if self.query_server['server_name'] == 'beeswax': # All the time
      kwargs['configuration'].update({'hive.server2.proxy.user': user.username})
      
    if self.query_server['server_name'] == 'llap': # All the time
      kwargs['configuration'].update({'hive.server2.proxy.user': user.username})
    
    if self.query_server['server_name'] == 'sparksql': # All the time
      kwargs['configuration'].update({'hive.server2.proxy.user': user.username})

    if self.query_server['server_name'].startswith('impala') and self.query_server['SESSION_TIMEOUT_S'] > 0:
      kwargs['configuration'].update({'idle_session_timeout': str(self.query_server['SESSION_TIMEOUT_S'])})

    LOG.info('Opening %s thrift session for user %s' % (self.query_server['server_name'], user.username))

    req = TOpenSessionReq(**kwargs)
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
    properties = session.get_properties()
    if not properties or self.query_server['server_name'] == 'beeswax':
      configuration = self.get_configuration()
      properties.update(configuration)
      session.properties = json.dumps(properties)
      session.save()

    return session


  def call(self, fn, req, status=TStatusCode.SUCCESS_STATUS, with_multiple_session=False):
    (res, session) = self.call_return_result_and_session(fn, req, status, with_multiple_session)
    return res


  def call_return_result_and_session(self, fn, req, status=TStatusCode.SUCCESS_STATUS, with_multiple_session=False):
    n_sessions = conf.MAX_NUMBER_OF_SESSIONS.get()

    # When a single session is allowed, avoid multiple session logic
    with_multiple_session = n_sessions > 1

    session = None

    if not with_multiple_session:
      # Default behaviour: get one session
      session = Session.objects.get_session(self.user, self.query_server['server_name'])
    else:
      session = self._get_tez_session(n_sessions)

    if session is None:
      session = self.open_session(self.user)

    if hasattr(req, 'sessionHandle') and req.sessionHandle is None:
      req.sessionHandle = session.get_handle()

    res = fn(req)

    # Not supported currently in HS2 and Impala: TStatusCode.INVALID_HANDLE_STATUS
    if res.status.statusCode == TStatusCode.ERROR_STATUS and \
        re.search('Invalid SessionHandle|Invalid session|Client session expired', res.status.errorMessage or '', re.I):
      LOG.info('Retrying with a new session because for %s of %s' % (self.user, res))
      session.status_code = TStatusCode.INVALID_HANDLE_STATUS
      session.save()

      session = self.open_session(self.user)

      req.sessionHandle = session.get_handle()

      # Get back the name of the function to call
      res = getattr(self._client, fn.attr)(req)

    if status is not None and res.status.statusCode not in (
        TStatusCode.SUCCESS_STATUS, TStatusCode.SUCCESS_WITH_INFO_STATUS, TStatusCode.STILL_EXECUTING_STATUS):
      if hasattr(res.status, 'errorMessage') and res.status.errorMessage:
        message = res.status.errorMessage
      else:
        message = ''
      raise QueryServerException(Exception('Bad status for request %s:\n%s' % (req, res)), message=message)
    else:
      return (res, session)


  def _get_tez_session(self, n_sessions):
    # Get 2 + n_sessions sessions and filter out the busy ones
    sessions = Session.objects.get_n_sessions(self.user, n=2 + n_sessions, application=self.query_server['server_name'])
    LOG.debug('%s sessions found' % len(sessions))
    if sessions:
      # Include trashed documents to keep the query lazy
      # and avoid retrieving all documents
      docs = Document2.objects.get_history(doc_type='query-hive', user=self.user, include_trashed=True)
      busy_sessions = set()

      # Only check last 40 documents for performance
      for doc in docs[:40]:
        try:
          snippet_data = json.loads(doc.data)['snippets'][0]
        except (KeyError, IndexError):
          # data might not contain a 'snippets' field or it might be empty
          LOG.warn('No snippets in Document2 object of type query-hive')
          continue
        session_guid = snippet_data.get('result', {}).get('handle', {}).get('session_guid')
        status = snippet_data.get('status')

        if status in [str(QueryHistory.STATE.submitted), str(QueryHistory.STATE.running)]:
          if session_guid is not None and session_guid not in busy_sessions:
            busy_sessions.add(session_guid)

      n_busy_sessions = 0
      available_sessions = []
      for session in sessions:
        if session.guid not in busy_sessions:
          available_sessions.append(session)
        else:
          n_busy_sessions += 1

      if n_busy_sessions == n_sessions:
        raise Exception('Too many open sessions. Stop a running query before starting a new one')

      if available_sessions:
        session = available_sessions[0]
      else:
        session = None # No available session found

      return session


  def close_session(self, sessionHandle):
    req = TCloseSessionReq(sessionHandle=sessionHandle)
    return self._client.CloseSession(req)


  def get_databases(self, schemaName=None):
    # GetCatalogs() is not implemented in HS2
    req = TGetSchemasReq()
    if schemaName is not None:
      req.schemaName = schemaName
    if self.query_server['server_name'].startswith('impala'):
      req.schemaName = None

    res = self.call(self._client.GetSchemas, req)

    results, schema = self.fetch_result(res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=5000)
    self.close_operation(res.operationHandle)

    col = 'TABLE_SCHEM'
    return HiveServerTRowSet(results.results, schema.schema).cols((col,))


  def get_database(self, database):
    query = 'DESCRIBE DATABASE EXTENDED `%s`' % (database)

    (desc_results, desc_schema), operation_handle = self.execute_statement(query, max_rows=5000, orientation=TFetchOrientation.FETCH_NEXT)
    self.close_operation(operation_handle)

    if self.query_server['server_name'].startswith('impala'):
      cols = ('name', 'location', 'comment') # Skip owner as on a new line
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
    res = self.call(self._client.GetTables, req)

    results, schema = self.fetch_result(res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=5000)
    self.close_operation(res.operationHandle)

    cols = ('TABLE_NAME', 'TABLE_TYPE', 'REMARKS')
    return HiveServerTRowSet(results.results, schema.schema).cols(cols)


  def get_tables(self, database, table_names, table_types=None):
    if not table_types:
      table_types = self.DEFAULT_TABLE_TYPES
    req = TGetTablesReq(schemaName=database, tableName=table_names, tableTypes=table_types)
    res = self.call(self._client.GetTables, req)

    results, schema = self.fetch_result(res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=5000)
    self.close_operation(res.operationHandle)

    return HiveServerTRowSet(results.results, schema.schema).cols(('TABLE_NAME',))


  def get_table(self, database, table_name, partition_spec=None):
    req = TGetTablesReq(schemaName=database.lower(), tableName=table_name.lower()) # Impala returns empty if not lower case
    res = self.call(self._client.GetTables, req)

    table_results, table_schema = self.fetch_result(res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT)
    self.close_operation(res.operationHandle)

    if partition_spec:
      query = 'DESCRIBE FORMATTED `%s`.`%s` PARTITION(%s)' % (database, table_name, partition_spec)
    else:
      query = 'DESCRIBE FORMATTED `%s`.`%s`' % (database, table_name)

    try:
      (desc_results, desc_schema), operation_handle = self.execute_statement(query, max_rows=10000, orientation=TFetchOrientation.FETCH_NEXT)
      self.close_operation(operation_handle)
    except Exception, e:
      ex_string = str(e)
      if 'cannot find field' in ex_string: # Workaround until Hive 2.0 and HUE-3751
        (desc_results, desc_schema), operation_handle = self.execute_statement('USE `%s`' % database)
        self.close_operation(operation_handle)
        if partition_spec:
          query = 'DESCRIBE FORMATTED `%s` PARTITION(%s)' % (table_name, partition_spec)
        else:
          query = 'DESCRIBE FORMATTED `%s`' % table_name
        (desc_results, desc_schema), operation_handle = self.execute_statement(query, max_rows=10000, orientation=TFetchOrientation.FETCH_NEXT)
        self.close_operation(operation_handle)
      elif 'not have privileges for DESCTABLE' in ex_string or 'AuthorizationException' in ex_string: # HUE-5608: No table permission but some column permissions
        query = 'DESCRIBE `%s`.`%s`' % (database, table_name)
        (desc_results, desc_schema), operation_handle = self.execute_statement(query, max_rows=10000, orientation=TFetchOrientation.FETCH_NEXT)
        self.close_operation(operation_handle)

        desc_results.results.columns[0].stringVal.values.insert(0, '# col_name')
        desc_results.results.columns[0].stringVal.values.insert(1, '')
        desc_results.results.columns[1].stringVal.values.insert(0, 'data_type')
        desc_results.results.columns[1].stringVal.values.insert(1, None)
        desc_results.results.columns[2].stringVal.values.insert(0, 'comment')
        desc_results.results.columns[2].stringVal.values.insert(1, None)
        try:
          part_index = desc_results.results.columns[0].stringVal.values.index('# Partition Information')
          desc_results.results.columns[0].stringVal.values = desc_results.results.columns[0].stringVal.values[:part_index] # Strip duplicate columns of partitioned tables
          desc_results.results.columns[1].stringVal.values = desc_results.results.columns[1].stringVal.values[:part_index]
          desc_results.results.columns[2].stringVal.values = desc_results.results.columns[2].stringVal.values[:part_index]

          desc_results.results.columns[1].stringVal.nulls = '' # Important to not clear the last two types

          desc_results.results.columns[1].stringVal.values[-1] = None
          desc_results.results.columns[2].stringVal.values[-1] = None
        except ValueError:
          desc_results.results.columns[0].stringVal.values.append('')
          desc_results.results.columns[1].stringVal.values.append(None)
          desc_results.results.columns[2].stringVal.values.append(None)
      else:
        raise e

    return HiveServerTable(table_results.results, table_schema.schema, desc_results.results, desc_schema.schema)


  def execute_query(self, query, max_rows=1000):
    configuration = self._get_query_configuration(query)
    return self.execute_query_statement(statement=query.query['query'], max_rows=max_rows, configuration=configuration)


  def execute_query_statement(self, statement, max_rows=1000, configuration={}, orientation=TFetchOrientation.FETCH_FIRST,
                              close_operation=False):
    (results, schema), operation_handle = self.execute_statement(statement=statement, max_rows=max_rows, configuration=configuration, orientation=orientation)

    if close_operation:
      self.close_operation(operation_handle)

    return HiveServerDataTable(results, schema, operation_handle, self.query_server)


  def execute_async_query(self, query, statement=0, with_multiple_session=False):
    if statement == 0:
      # Impala just has settings currently
      if self.query_server['server_name'] == 'beeswax':
        for resource in query.get_configuration_statements():
          self.execute_statement(resource.strip())

    configuration = {}

    if self.query_server['server_name'].startswith('impala') and self.query_server['querycache_rows'] > 0:
      configuration[IMPALA_RESULTSET_CACHE_SIZE] = str(self.query_server['querycache_rows'])

    # The query can override the default configuration
    configuration.update(self._get_query_configuration(query))
    query_statement = query.get_query_statement(statement)

    return self.execute_async_statement(statement=query_statement, confOverlay=configuration, with_multiple_session=with_multiple_session)


  def execute_statement(self, statement, max_rows=1000, configuration={}, orientation=TFetchOrientation.FETCH_NEXT):
    if self.query_server['server_name'].startswith('impala') and self.query_server['QUERY_TIMEOUT_S'] > 0:
      configuration['QUERY_TIMEOUT_S'] = str(self.query_server['QUERY_TIMEOUT_S'])

    req = TExecuteStatementReq(statement=statement.encode('utf-8'), confOverlay=configuration)
    res = self.call(self._client.ExecuteStatement, req)

    return self.fetch_result(res.operationHandle, max_rows=max_rows, orientation=orientation), res.operationHandle


  def execute_async_statement(self, statement, confOverlay, with_multiple_session=False):
    if self.query_server['server_name'].startswith('impala') and self.query_server['QUERY_TIMEOUT_S'] > 0:
      confOverlay['QUERY_TIMEOUT_S'] = str(self.query_server['QUERY_TIMEOUT_S'])

    req = TExecuteStatementReq(statement=statement.encode('utf-8'), confOverlay=confOverlay, runAsync=True)
    (res, session) = self.call_return_result_and_session(self._client.ExecuteStatement, req, with_multiple_session=with_multiple_session)

    return HiveServerQueryHandle(
        secret=res.operationHandle.operationId.secret,
        guid=res.operationHandle.operationId.guid,
        operation_type=res.operationHandle.operationType,
        has_result_set=res.operationHandle.hasResultSet,
        modified_row_count=res.operationHandle.modifiedRowCount,
        session_guid=session.guid
    )


  def fetch_data(self, operation_handle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=1000):
    # Fetch until the result is empty dues to a HS2 bug instead of looking at hasMoreRows
    results, schema = self.fetch_result(operation_handle, orientation, max_rows)
    return HiveServerDataTable(results, schema, operation_handle, self.query_server)


  def cancel_operation(self, operation_handle):
    req = TCancelOperationReq(operationHandle=operation_handle)
    return self.call(self._client.CancelOperation, req)


  def close_operation(self, operation_handle):
    req = TCloseOperationReq(operationHandle=operation_handle)
    return self.call(self._client.CloseOperation, req)


  def get_columns(self, database, table):
    req = TGetColumnsReq(schemaName=database, tableName=table)
    res = self.call(self._client.GetColumns, req)

    res, schema = self.fetch_result(res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT)
    self.close_operation(res.operationHandle)

    return res, schema


  def fetch_result(self, operation_handle, orientation=TFetchOrientation.FETCH_FIRST, max_rows=1000):
    if operation_handle.hasResultSet:
      fetch_req = TFetchResultsReq(operationHandle=operation_handle, orientation=orientation, maxRows=max_rows)
      res = self.call(self._client.FetchResults, fetch_req)
    else:
      res = TFetchResultsResp(results=TRowSet(startRowOffset=0, rows=[], columns=[]))

    if operation_handle.hasResultSet and TFetchOrientation.FETCH_FIRST: # Only fetch for the first call that should be with start_over
      meta_req = TGetResultSetMetadataReq(operationHandle=operation_handle)
      schema = self.call(self._client.GetResultSetMetadata, meta_req)
    else:
      schema = None

    return res, schema


  def fetch_log(self, operation_handle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=1000):
    req = TFetchResultsReq(operationHandle=operation_handle, orientation=orientation, maxRows=max_rows, fetchType=1)
    res = self.call(self._client.FetchResults, req)

    if beeswax_conf.THRIFT_VERSION.get() >= 7:
      lines = res.results.columns[0].stringVal.values
    else:
      lines = imap(lambda r: r.colVals[0].stringVal.value, res.results.rows)

    return '\n'.join(lines)


  def get_operation_status(self, operation_handle):
    req = TGetOperationStatusReq(operationHandle=operation_handle)
    return self.call(self._client.GetOperationStatus, req)

  def explain(self, query):
    query_statement = query.get_query_statement(0)
    configuration = self._get_query_configuration(query)
    return self.execute_query_statement(statement='EXPLAIN %s' % query_statement, configuration=configuration, orientation=TFetchOrientation.FETCH_NEXT)


  def get_log(self, operation_handle):
    try:
      req = TGetLogReq(operationHandle=operation_handle)
      res = self.call(self._client.GetLog, req)
      return res.log
    except Exception, e:
      if 'Invalid query handle' in str(e):
        message = 'Invalid query handle'
        LOG.error('%s: %s' % (message, e))
      else:
        message = 'Error when fetching the logs of the operation.'
        LOG.exception(message)

      return message


  def get_partitions(self, database, table_name, partition_spec=None, max_parts=None, reverse_sort=True):
    table = self.get_table(database, table_name)

    query = 'SHOW PARTITIONS `%s`.`%s`' % (database, table_name)
    if self.query_server['server_name'] == 'beeswax' and partition_spec:
      query += ' PARTITION(%s)' % partition_spec

    # We fetch N partitions then reverse the order later and get the max_parts. Use partition_spec to refine more the initial list.
    # Need to fetch more like this until SHOW PARTITIONS offers a LIMIT and ORDER BY
    partition_table = self.execute_query_statement(query, max_rows=10000, orientation=TFetchOrientation.FETCH_NEXT, close_operation=True)

    if self.query_server['server_name'].startswith('impala'):
      try:
        # Fetch all partition key names, which are listed before the #Rows column
        cols = [col.name for col in partition_table.cols()]
        stop = cols.index('#Rows')
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
          zipped_parts = izip(partition_keys, values)
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


  def get_configuration(self):
    configuration = {}

    if self.query_server['server_name'].startswith('impala'):  # Return all configuration settings
      query = 'SET'
      results = self.execute_query_statement(query, orientation=TFetchOrientation.FETCH_NEXT, close_operation=True)
      configuration = dict((row[0], row[1]) for row in results.rows())
    else:  # For Hive, only return white-listed configurations
      query = 'SET -v'
      results = self.execute_query_statement(query, orientation=TFetchOrientation.FETCH_FIRST, max_rows=-1, close_operation=True)
      config_whitelist = [config.lower() for config in CONFIG_WHITELIST.get()]
      properties = [(row[0].split('=')[0], row[0].split('=')[1]) for row in results.rows() if '=' in row[0]]
      configuration = dict((prop, value) for prop, value in properties if prop.lower() in config_whitelist)

    return configuration


  def _get_query_configuration(self, query):
    return dict([(setting['key'], setting['value']) for setting in query.settings])


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
      self.is_impala_only = 'org.apache.kudu.mapreduce.KuduTableOutputFormat' in str(hive_table.properties)
    except Exception as e:
      LOG.warn('Autocomplete data fetching error: %s' % e)
      self.is_impala_only = False

  @property
  def cols(self):
    return [
        type('Col', (object,), {
          'name': col.get('col_name', '').strip() if col.get('col_name') else '',
          'type': col.get('data_type', '').strip() if col.get('data_type') else '',
          'comment': col.get('comment', '').strip() if col.get('comment') else ''
        }) for col in HiveServerTable.cols.fget(self)
  ]


class ResultCompatible:

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


class PartitionKeyCompatible:

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


class PartitionValueCompatible:

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


class ExplainCompatible:

  def __init__(self, data_table):
    self.textual = '\n'.join([line[0] for line in data_table.rows()])


class ResultMetaCompatible:

  def __init__(self):
    self.in_tablename = True


class HiveServerClientCompatible(object):
  """Same API as Beeswax"""

  def __init__(self, client):
    self._client = client
    self.user = client.user
    self.query_server = client.query_server


  def query(self, query, statement=0, with_multiple_session=False):
    return self._client.execute_async_query(query, statement, with_multiple_session=with_multiple_session)


  def get_state(self, handle):
    operationHandle = handle.get_rpc_handle()
    res = self._client.get_operation_status(operationHandle)
    return HiveServerQueryHistory.STATE_MAP[res.operationState]


  def get_operation_status(self, handle):
    operationHandle = handle.get_rpc_handle()
    return self._client.get_operation_status(operationHandle)


  def use(self, query):
    data = self._client.execute_query(query)
    self._client.close_operation(data.operation_handle)
    return data


  def explain(self, query):
    data_table = self._client.explain(query)
    data = ExplainCompatible(data_table)
    self._client.close_operation(data_table.operation_handle)
    return data


  def fetch(self, handle, start_over=False, max_rows=None):
    operationHandle = handle.get_rpc_handle()
    if max_rows is None:
      max_rows = 1000

    if start_over and not (self.query_server['server_name'].startswith('impala') and self.query_server['querycache_rows'] == 0): # Backward compatibility for impala
      orientation = TFetchOrientation.FETCH_FIRST
    else:
      orientation = TFetchOrientation.FETCH_NEXT

    data_table = self._client.fetch_data(operationHandle, orientation=orientation, max_rows=max_rows)

    return ResultCompatible(data_table)


  def cancel_operation(self, handle):
    operationHandle = handle.get_rpc_handle()
    return self._client.cancel_operation(operationHandle)


  def close(self, handle):
    return self.close_operation(handle)


  def close_operation(self, handle):
    operationHandle = handle.get_rpc_handle()
    return self._client.close_operation(operationHandle)


  def close_session(self, session):
    operationHandle = session.get_handle()
    return self._client.close_session(operationHandle)


  def dump_config(self):
    return 'Does not exist in HS2'


  def get_log(self, handle, start_over=True):
    operationHandle = handle.get_rpc_handle()

    if beeswax_conf.USE_GET_LOG_API.get() or self.query_server['server_name'].startswith('impala'):
      return self._client.get_log(operationHandle)
    else:
      if start_over:
        orientation = TFetchOrientation.FETCH_FIRST
      else:
        orientation = TFetchOrientation.FETCH_NEXT

      return self._client.fetch_log(operationHandle, orientation=orientation, max_rows=-1)


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
        'type': table['TABLE_TYPE'].capitalize()}
      )
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
