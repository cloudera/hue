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
import re

from itertools import imap
from operator import itemgetter

from django.utils.translation import ugettext as _

from desktop.lib import thrift_util
from desktop.conf import LDAP_PASSWORD, LDAP_USERNAME
from desktop.conf import DEFAULT_USER
from hadoop import cluster

from TCLIService import TCLIService
from TCLIService.ttypes import TOpenSessionReq, TGetTablesReq, TFetchResultsReq,\
  TStatusCode, TGetResultSetMetadataReq, TGetColumnsReq, TTypeId,\
  TExecuteStatementReq, TGetOperationStatusReq, TFetchOrientation,\
  TCloseSessionReq, TGetSchemasReq, TGetLogReq, TCancelOperationReq,\
  TCloseOperationReq, TFetchResultsResp, TRowSet, TProtocolVersion

from beeswax import conf as beeswax_conf
from beeswax import hive_site
from beeswax.models import Session, HiveServerQueryHandle, HiveServerQueryHistory
from beeswax.server.dbms import Table, NoSuchObjectException, DataTable,\
                                QueryServerException

LOG = logging.getLogger(__name__)

IMPALA_RESULTSET_CACHE_SIZE = 'impala.resultset.cache.size'
DEFAULT_USER = DEFAULT_USER.get()


class HiveServerTable(Table):
  """
  We are parsing DESCRIBE EXTENDED text as the metastore API like GetColumns() misses most of the information.
  Impala only supports a simple DESCRIBE.
  """
  def __init__(self, table_results, table_schema, desc_results, desc_schema):
    if beeswax_conf.THRIFT_VERSION.get() >= 7:
      if not table_results.columns:
        raise NoSuchObjectException()
      self.table = table_results.columns or ''
    else: # Deprecated. To remove in Hue 4.
      if not table_results.rows:
        raise NoSuchObjectException()
      self.table = table_results.rows and table_results.rows[0] or ''

    self.table_schema = table_schema
    self.desc_results = desc_results
    self.desc_schema = desc_schema

  @property
  def name(self):
    return HiveServerTRow(self.table, self.table_schema).col('TABLE_NAME')

  @property
  def is_view(self):
    return HiveServerTRow(self.table, self.table_schema).col('TABLE_TYPE') == 'VIEW' # Used to be VIRTUAL_VIEW

  @property
  def partition_keys(self):
    describe = self.extended_describe
    # Parses a list of: partitionKeys:[FieldSchema(name:baz, type:string, comment:null), FieldSchema(name:boom, type:string, comment:null)]
    match = re.search('partitionKeys:\[([^\]]+)\]', describe)
    if match is not None:
      match = match.group(1)
      return [PartitionKeyCompatible(*partition)
          for partition in re.findall('FieldSchema\(name:(.+?), type:(.+?), comment:(.+?)\)', match)]
    else:
      return []

  @property
  def path_location(self):
    try:
      describe = self.extended_describe
      match = re.search('location:([^,]+)', describe)
      if match is not None:
        match = match.group(1)
      return match
    except:
      # Impala does not have extended_describe
      return None

  @property
  def parameters(self):
    # Parses a list of: parameters:{serialization.format=1}),... parameters:{numPartitions=2, EXTERNAL=TRUE}
    describe = self.extended_describe
    params = re.findall('parameters:\{([^\}]+?)\}', describe)
    if params:
      params_list = ', '.join(params).split(', ')
      return dict([param.split('=')for param in params_list])
    else:
      return {}

  @property
  def cols(self):
    cols = HiveServerTTableSchema(self.desc_results, self.desc_schema).cols()
    try:
      end_cols_index = map(itemgetter('col_name'), cols).index('') # Truncate below extended describe
      return cols[0:end_cols_index]
    except:
      try:
        # Spark SQL: does not have an empty line in extended describe
        try:
          end_cols_index = map(itemgetter('col_name'), cols).index('# Partition Information')
        except:
          end_cols_index = map(itemgetter('col_name'), cols).index('Detailed Table Information')
        return cols[0:end_cols_index]
      except:
        # Impala: uses non extended describe and 'col' instead of 'col_name'
        return cols

  @property
  def comment(self):
    return HiveServerTRow(self.table, self.table_schema).col('REMARKS')

  @property
  def extended_describe(self):
    # Just keep rows after 'Detailed Table Information'
    rows = HiveServerTTableSchema(self.desc_results, self.desc_schema).cols()
    detailed_row_index = map(itemgetter('col_name'), rows).index('Detailed Table Information')
    # Hack because of bad delimiter escaping in LazySimpleSerDe in HS2: parameters:{serialization.format=})
    describe_text = rows[detailed_row_index]['data_type']
    try:
      # LazySimpleSerDe case, also add full next row
      return describe_text + rows[detailed_row_index + 1]['col_name'] + rows[detailed_row_index + 1]['data_type']
    except:
      return describe_text

  @property
  def properties(self):
    # Ugly but would need a recursive parsing to be clean
    no_table = re.sub('\)$', '', re.sub('^Table\(', '', self.extended_describe))
    properties = re.sub(', sd:StorageDescriptor\(cols.+?\]', '', no_table).split(', ')
    props = []

    for prop in properties:
      key_val = prop.rsplit(':', 1)
      if len(key_val) == 1:
        key_val = key_val[0].rsplit('=', 1)
      if len(key_val) == 2:
        props.append(key_val)

    return props


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
      cols_rows.append(dict(zip(col_names, cols_row)))

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
    if bytestring == '' or bytestring == '\x00':
      return values
    else:
      return [None if is_null else value for value, is_null in zip(values, cls.mark_nulls(values, bytestring))]


class HiveServerDataTable(DataTable):
  def __init__(self, results, schema, operation_handle, query_server):
    self.schema = schema and schema.schema
    self.row_set = HiveServerTRowSet(results.results, schema)
    self.operation_handle = operation_handle
    if query_server['server_name'] == 'impala':
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
    except Exception:
      # Impala API is different
      cols = HiveServerTRowSet(self.columns, self.schema).cols(('name', 'type', 'comment'))
      for col in cols:
        col['col_name'] = col.pop('name')
        col['col_type'] = col.pop('type')
      return cols

  def col(self, colName):
    pos = self._get_col_position(colName)
    return HiveServerTColumnDesc(self.columns[pos]).val

  def _get_col_position(self, column_name):
    return filter(lambda (i, col): col.columnName == column_name, enumerate(self.schema.columns))[0][0]


if beeswax_conf.THRIFT_VERSION.get() >= 7:
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
  HS2_MECHANISMS = {'KERBEROS': 'GSSAPI', 'NONE': 'PLAIN', 'NOSASL': 'NOSASL', 'LDAP': 'PLAIN'}

  def __init__(self, query_server, user):
    self.query_server = query_server
    self.user = user

    use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled, ldap_username, ldap_password = self.get_security()
    LOG.info('use_sasl=%s, mechanism=%s, kerberos_principal_short_name=%s, impersonation_enabled=%s' % (
             use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled))

    self.use_sasl = use_sasl
    self.kerberos_principal_short_name = kerberos_principal_short_name
    self.impersonation_enabled = impersonation_enabled

    if self.query_server['server_name'] == 'impala':
      from impala import conf as impala_conf

      ssl_enabled = impala_conf.SSL.ENABLED.get()
      ca_certs = impala_conf.SSL.CACERTS.get()
      keyfile = impala_conf.SSL.KEY.get()
      certfile = impala_conf.SSL.CERT.get()
      validate = impala_conf.SSL.VALIDATE.get()
      timeout = impala_conf.SERVER_CONN_TIMEOUT.get()
    else:
      ssl_enabled = beeswax_conf.SSL.ENABLED.get()
      ca_certs = beeswax_conf.SSL.CACERTS.get()
      keyfile = beeswax_conf.SSL.KEY.get()
      certfile = beeswax_conf.SSL.CERT.get()
      validate = beeswax_conf.SSL.VALIDATE.get()
      timeout = beeswax_conf.SERVER_CONN_TIMEOUT.get()

    if ldap_username:
      username = ldap_username
      password = ldap_password
    else:
      username = user.username
      password = None

    self._client = thrift_util.get_client(TCLIService.Client,
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
                                          validate=validate)


  def get_security(self):
    principal = self.query_server['principal']
    impersonation_enabled = False
    ldap_username = None
    ldap_password = None

    if principal:
      kerberos_principal_short_name = principal.split('/', 1)[0]
    else:
      kerberos_principal_short_name = None

    if self.query_server['server_name'] == 'impala':
      if LDAP_PASSWORD.get(): # Force LDAP auth if ldap_password is provided
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
        raise Exception(_('%s server authentication not supported. Valid are %s.' % (hive_mechanism, HiveServerClient.HS2_MECHANISMS.keys())))
      use_sasl = hive_mechanism in ('KERBEROS', 'NONE', 'LDAP')
      mechanism = HiveServerClient.HS2_MECHANISMS[hive_mechanism]
      impersonation_enabled = hive_site.hiveserver2_impersonation_enabled()

    if LDAP_PASSWORD.get(): # Pass-through LDAP authentication
      ldap_username = LDAP_USERNAME.get()
      ldap_password = LDAP_PASSWORD.get()

    return use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled, ldap_username, ldap_password


  def open_session(self, user):
    kwargs = {
        'client_protocol': beeswax_conf.THRIFT_VERSION.get() - 1,
        'username': user.username, # If SASL or LDAP, it gets the username from the authentication mechanism" since it dependents on it.
        'configuration': {},
    }

    if self.impersonation_enabled:
      kwargs.update({'username': DEFAULT_USER})

      if self.query_server['server_name'] == 'impala': # Only when Impala accepts it
        kwargs['configuration'].update({'impala.doas.user': user.username})

    if self.query_server['server_name'] == 'beeswax': # All the time
      kwargs['configuration'].update({'hive.server2.proxy.user': user.username})

    req = TOpenSessionReq(**kwargs)
    res = self._client.OpenSession(req)

    if res.status is not None and res.status.statusCode not in (TStatusCode.SUCCESS_STATUS,):
      if hasattr(res.status, 'errorMessage') and res.status.errorMessage:
        message = res.status.errorMessage
      else:
        message = ''
      raise QueryServerException(Exception('Bad status for request %s:\n%s' % (req, res)), message=message)

    sessionId = res.sessionHandle.sessionId
    LOG.info('Opening session %s' % sessionId)

    encoded_status, encoded_guid = HiveServerQueryHandle(secret=sessionId.secret, guid=sessionId.guid).get()

    return Session.objects.create(owner=user,
                                  application=self.query_server['server_name'],
                                  status_code=res.status.statusCode,
                                  secret=encoded_status,
                                  guid=encoded_guid,
                                  server_protocol_version=res.serverProtocolVersion)


  def call(self, fn, req, status=TStatusCode.SUCCESS_STATUS):
    session = Session.objects.get_session(self.user, self.query_server['server_name'])

    if session is None:
      session = self.open_session(self.user)

    if hasattr(req, 'sessionHandle') and req.sessionHandle is None:
      req.sessionHandle = session.get_handle()

    res = fn(req)

    # Not supported currently in HS2 and Impala: TStatusCode.INVALID_HANDLE_STATUS
    if res.status.statusCode == TStatusCode.ERROR_STATUS and \
        re.search('Invalid SessionHandle|Invalid session|Client session expired', res.status.errorMessage or '', re.I):
      LOG.info('Retrying with a new session because for %s of %s' % (self.user, res))

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
      return res


  def close_session(self, sessionHandle):
    req = TCloseSessionReq(sessionHandle=sessionHandle)
    return self._client.CloseSession(req)


  def get_databases(self):
    # GetCatalogs() is not implemented in HS2
    req = TGetSchemasReq()
    res = self.call(self._client.GetSchemas, req)

    results, schema = self.fetch_result(res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT)
    self.close_operation(res.operationHandle)

    col = 'TABLE_SCHEM'
    return HiveServerTRowSet(results.results, schema.schema).cols((col,))


  def get_tables(self, database, table_names):
    req = TGetTablesReq(schemaName=database, tableName=table_names)
    res = self.call(self._client.GetTables, req)

    results, schema = self.fetch_result(res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=5000)
    self.close_operation(res.operationHandle)

    return HiveServerTRowSet(results.results, schema.schema).cols(('TABLE_NAME',))


  def get_table(self, database, table_name):
    req = TGetTablesReq(schemaName=database, tableName=table_name)
    res = self.call(self._client.GetTables, req)

    table_results, table_schema = self.fetch_result(res.operationHandle, orientation=TFetchOrientation.FETCH_NEXT)
    self.close_operation(res.operationHandle)

    if self.query_server['server_name'] == 'impala':
      # Impala does not supported extended
      query = 'DESCRIBE %s' % table_name
    else:
      query = 'DESCRIBE EXTENDED %s' % table_name
    (desc_results, desc_schema), operation_handle = self.execute_statement(query, max_rows=5000)
    self.close_operation(operation_handle)

    return HiveServerTable(table_results.results, table_schema.schema, desc_results.results, desc_schema.schema)


  def execute_query(self, query, max_rows=1000):
    configuration = self._get_query_configuration(query)
    return self.execute_query_statement(statement=query.query['query'], max_rows=max_rows, configuration=configuration)


  def execute_query_statement(self, statement, max_rows=1000, configuration={}):
    (results, schema), operation_handle = self.execute_statement(statement=statement, max_rows=max_rows, configuration=configuration)
    return HiveServerDataTable(results, schema, operation_handle, self.query_server)


  def execute_async_query(self, query, statement=0):
    if statement == 0:
      # Impala just has settings currently
      if self.query_server['server_name'] == 'beeswax':
        for resource in query.get_configuration_statements():
          self.execute_statement(resource.strip())

    configuration = {}

    if self.query_server['server_name'] == 'impala' and self.query_server['querycache_rows'] > 0:
      configuration[IMPALA_RESULTSET_CACHE_SIZE] = str(self.query_server['querycache_rows'])

    # The query can override the default configuration
    configuration.update(self._get_query_configuration(query))
    query_statement = query.get_query_statement(statement)

    return self.execute_async_statement(statement=query_statement, confOverlay=configuration)


  def execute_statement(self, statement, max_rows=1000, configuration={}):
    if self.query_server['server_name'] == 'impala' and self.query_server['QUERY_TIMEOUT_S'] > 0:
      configuration['QUERY_TIMEOUT_S'] = str(self.query_server['QUERY_TIMEOUT_S'])

    req = TExecuteStatementReq(statement=statement.encode('utf-8'), confOverlay=configuration)
    res = self.call(self._client.ExecuteStatement, req)

    return self.fetch_result(res.operationHandle, max_rows=max_rows), res.operationHandle


  def execute_async_statement(self, statement, confOverlay):
    if self.query_server['server_name'] == 'impala' and self.query_server['QUERY_TIMEOUT_S'] > 0:
      confOverlay['QUERY_TIMEOUT_S'] = str(self.query_server['QUERY_TIMEOUT_S'])

    req = TExecuteStatementReq(statement=statement.encode('utf-8'), confOverlay=confOverlay, runAsync=True)
    res = self.call(self._client.ExecuteStatement, req)

    return HiveServerQueryHandle(secret=res.operationHandle.operationId.secret,
                                 guid=res.operationHandle.operationId.guid,
                                 operation_type=res.operationHandle.operationType,
                                 has_result_set=res.operationHandle.hasResultSet,
                                 modified_row_count=res.operationHandle.modifiedRowCount)


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
    return self.execute_query_statement(statement='EXPLAIN %s' % query_statement, configuration=configuration)


  def get_log(self, operation_handle):
    try:
      req = TGetLogReq(operationHandle=operation_handle)
      res = self.call(self._client.GetLog, req)
      return res.log
    except:
      return 'Server does not support GetLog()'


  def get_partitions(self, database, table_name, max_parts):
    table = self.get_table(database, table_name)

    if max_parts is None or max_parts <= 0:
      max_rows = 10000
    else:
      max_rows = 1000 if max_parts <= 250 else max_parts

    partitionTable = self.execute_query_statement('SHOW PARTITIONS %s' % table_name, max_rows=max_rows) # DB prefix supported since Hive 0.13
    return [PartitionValueCompatible(partition, table) for partition in partitionTable.rows()][-max_parts:]


  def _get_query_configuration(self, query):
    return dict([(setting['key'], setting['value']) for setting in query.settings])


class HiveServerTableCompatible(HiveServerTable):
  """Same API as Beeswax"""

  def __init__(self, hive_table):
    self.table = hive_table.table
    self.table_schema = hive_table.table_schema
    self.desc_results = hive_table.desc_results
    self.desc_schema = hive_table.desc_schema

  @property
  def cols(self):
    return [type('Col', (object,), {'name': col.get('col_name', '').strip(),
                                    'type': col.get('data_type', col.get('col_type', '')).strip(), # Impala is col_type
                                    'comment': col.get('comment', '').strip() if col.get('comment') else '', }) for col in HiveServerTable.cols.fget(self)]


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

  def __init__(self, partition, table):
    # Parses: ['datehour=2013022516'] or ['month=2011-07/dt=2011-07-01/hr=12']
    self.values = [val.split('=')[1] for part in partition for val in part.split('/')]
    self.sd = type('Sd', (object,), {'location': '%s/%s' % (table.path_location, ','.join(partition)),})


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


  def query(self, query, statement=0):
    return self._client.execute_async_query(query, statement)


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

    if start_over and not (self.query_server['server_name'] == 'impala' and self.query_server['querycache_rows'] == 0): # Backward compatibility for impala
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

    if beeswax_conf.USE_GET_LOG_API.get() or self.query_server['server_name'] == 'impala':
      return self._client.get_log(operationHandle)
    else:
      if start_over:
        orientation = TFetchOrientation.FETCH_FIRST
      else:
        orientation = TFetchOrientation.FETCH_NEXT

      return self._client.fetch_log(operationHandle, orientation=orientation, max_rows=-1)


  def get_databases(self):
    col = 'TABLE_SCHEM'
    return [table[col] for table in self._client.get_databases()]


  def get_tables(self, database, table_names):
    tables = [table['TABLE_NAME'] for table in self._client.get_tables(database, table_names)]
    tables.sort()
    return tables


  def get_table(self, database, table_name):
    table = self._client.get_table(database, table_name)
    return HiveServerTableCompatible(table)


  def get_columns(self, database, table):
    return self._client.get_columns(database, table)


  def get_default_configuration(self, *args, **kwargs):
    return {}


  def get_results_metadata(self, handle):
    # We just need to mock
    return ResultMetaCompatible()


  def create_database(self, name, description): raise NotImplementedError()


  def get_database(self, *args, **kwargs): raise NotImplementedError()


  def alter_table(self, dbname, tbl_name, new_tbl): raise NotImplementedError()


  def open_session(self, user):
    return self._client.open_session(user)


  def add_partition(self, new_part): raise NotImplementedError()


  def get_partition(self, *args, **kwargs): raise NotImplementedError()


  def get_partitions(self, database, table_name, max_parts):
    return self._client.get_partitions(database, table_name, max_parts)


  def alter_partition(self, db_name, tbl_name, new_part): raise NotImplementedError()
