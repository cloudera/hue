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
import re
import thrift

from operator import itemgetter

from desktop.conf import KERBEROS
from desktop.lib import thrift_util
from hadoop import cluster

from TCLIService import TCLIService
from TCLIService.ttypes import TOpenSessionReq, TGetTablesReq, TFetchResultsReq,\
  TStatusCode, TGetResultSetMetadataReq, TGetColumnsReq, TType,\
  TExecuteStatementReq, TGetOperationStatusReq, TFetchOrientation,\
  TCloseSessionReq, TGetSchemasReq, TGetLogReq, TCancelOperationReq,\
  TCloseOperationReq

from beeswax import conf
from beeswax import hive_site
from beeswax.models import Session, HiveServerQueryHandle, HiveServerQueryHistory
from beeswax.server.dbms import Table, NoSuchObjectException, DataTable,\
  QueryServerException


LOG = logging.getLogger(__name__)


class HiveServerTable(Table):
  """
  We are parsing DESCRIBE EXTENDED text sometimes and might need to implement the metastore API instead at some point.
  """
  def __init__(self, table_results, table_schema, desc_results, desc_schema):
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
    return HiveServerTRow(self.table, self.table_schema).col('TABLE_TYPE') == 'VIRTUAL_VIEW'

  @property
  def partition_keys(self):
    describe = self.extended_describe
    #  partitionKeys:[FieldSchema(name:datehour, type:int, comment:null)],
    match = re.search('partitionKeys:\[([^\]]+)\]', describe)
    if match is not None:
      match = match.group(1)
      return [PartitionKeyCompatible(partition)
              for partition in re.findall('FieldSchema\((.+?)\)', match)]
    else:
      return []

  @property
  def path_location(self):
    describe = self.extended_describe
    match = re.search('location:([^,]+)', describe)
    if match is not None:
      match = match.group(1)
    return match

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
      # Impala use non extended describe and 'col' instead of 'col_name'
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
      # LazySimpleSerDe case
      return describe_text + rows[detailed_row_index + 1]['col_name']
    except:
      return describe_text


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



class HiveServerDataTable(DataTable):
  def __init__(self, results, schema, operation_handle):
    self.schema = schema and schema.schema
    self.row_set = HiveServerTRowSet(results.results, schema)
    self.operation_handle = operation_handle
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
        col['col_type'] = col.pop('type')
      return cols

  def col(self, colName):
    pos = self._get_col_position(colName)
    return HiveServerTColumnDesc(self.columns[pos]).val

  def _get_col_position(self, column_name):
    return filter(lambda (i, col): col.columnName == column_name, enumerate(self.schema.columns))[0][0]


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


class HiveServerTColumnValue:
  def __init__(self, tcolumn_value):
    self.column_value = tcolumn_value

  @property
  def val(self):
    # TODO get index from schema
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
        return TType._VALUES_TO_NAMES[ttype.primitiveEntry.type]
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
  HS2_MECHANISMS = {'KERBEROS': 'GSSAPI', 'NONE': 'PLAIN', 'NOSASL': 'NOSASL'}

  def __init__(self, query_server, user):
    self.query_server = query_server
    self.user = user

    use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled = HiveServerClient.get_security(query_server)
    LOG.info('use_sasl=%s, mechanism=%s, kerberos_principal_short_name=%s, impersonation_enabled=%s' % (
             use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled))

    self.use_sasl = use_sasl
    self.impersonation_enabled = impersonation_enabled
    self._client = thrift_util.get_client(TCLIService.Client,
                                          query_server['server_host'],
                                          query_server['server_port'],
                                          service_name=query_server['server_name'],
                                          kerberos_principal=kerberos_principal_short_name,
                                          use_sasl=use_sasl,
                                          mechanism=mechanism,
                                          username=user.username,
                                          timeout_seconds=conf.BEESWAX_SERVER_CONN_TIMEOUT.get())


  @classmethod
  def get_security(cls, query_server):
    principal = query_server['principal']
    impersonation_enabled = False

    if query_server['server_name'] == 'impala':
      cluster_conf = cluster.get_cluster_conf_for_job_submission()
      use_sasl = cluster_conf is not None and cluster_conf.SECURITY_ENABLED.get()
      mechanism = HiveServerClient.HS2_MECHANISMS['KERBEROS']
      impersonation_enabled = query_server['impersonation_enabled']
    else:
      hive_mechanism = hive_site.get_hiveserver2_authentication()
      if hive_mechanism not in HiveServerClient.HS2_MECHANISMS:
        raise Exception(_('%s server authentication not supported. Valid are %s.' % (hive_mechanism, HiveServerClient.HS2_MECHANISMS.keys())))
      use_sasl = hive_mechanism in ('KERBEROS', 'NONE')
      mechanism = 'NOSASL'
      if use_sasl:
        mechanism = HiveServerClient.HS2_MECHANISMS[hive_mechanism]
      impersonation_enabled = hive_site.hiveserver2_impersonation_enabled()

    if principal:
      kerberos_principal_short_name = principal.split('/', 1)[0]
    else:
      kerberos_principal_short_name = None

    return use_sasl, mechanism, kerberos_principal_short_name, impersonation_enabled


  def open_session(self, user):
    kwargs = {'username': user.username, 'configuration': {}}

    if self.use_sasl:
      kerberos_principal_short_name = KERBEROS.HUE_PRINCIPAL.get().split('/', 1)[0]
      kwargs.update({'username': kerberos_principal_short_name})

    if self.impersonation_enabled:
      kwargs.update({'username': 'hue'})

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
        re.search('Invalid SessionHandle|Invalid session', res.status.errorMessage or '', re.I):
      LOG.info('Retrying with a new session because of %s' % res)

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


  def close_session(self):
    session = Session.objects.get_session(self.user, self.query_server['server_name']).get_handle()

    req = TCloseSessionReq(sessionHandle=session)
    return self._client.CloseSession(req)


  def get_databases(self):
    # GetCatalogs() is not implemented in HS2
    req = TGetSchemasReq()
    res = self.call(self._client.GetSchemas, req)

    results, schema = self.fetch_result(res.operationHandle)
    self.close_operation(res.operationHandle)

    col = 'TABLE_SCHEM'
    return HiveServerTRowSet(results.results, schema.schema).cols((col,))


  def get_tables(self, database, table_names):
    req = TGetTablesReq(schemaName=database, tableName=table_names)
    res = self.call(self._client.GetTables, req)

    results, schema = self.fetch_result(res.operationHandle)
    self.close_operation(res.operationHandle)

    return HiveServerTRowSet(results.results, schema.schema).cols(('TABLE_NAME',))


  def get_table(self, database, table_name):
    req = TGetTablesReq(schemaName=database, tableName=table_name)
    res = self.call(self._client.GetTables, req)

    table_results, table_schema = self.fetch_result(res.operationHandle)
    self.close_operation(res.operationHandle)

    if self.query_server['server_name'] == 'impala':
      # Impala does not supported extended
      query = 'DESCRIBE %s' % table_name
    else:
      query = 'DESCRIBE EXTENDED %s' % table_name
    (desc_results, desc_schema), operation_handle = self.execute_statement(query)
    self.close_operation(operation_handle)

    # Using 'SELECT * from table' does not show column comments in the metadata
    if self.query_server['server_name'] == 'beeswax':
      self.execute_statement(statement='SET hive.server2.blocking.query=true')

    return HiveServerTable(table_results.results, table_schema.schema, desc_results.results, desc_schema.schema)


  def execute_query(self, query, max_rows=5000):
    configuration = self._get_query_configuration(query)
    return self.execute_query_statement(statement=query.query['query'], max_rows=max_rows, configuration=configuration)


  def execute_query_statement(self, statement, max_rows=5000, configuration={}):
    # Only execute_async_query() supports configuration
    if self.query_server['server_name'] == 'beeswax':
      self.execute_statement(statement='SET hive.server2.blocking.query=true')

    (results, schema), operation_handle = self.execute_statement(statement=statement, max_rows=max_rows, configuration=configuration)
    return HiveServerDataTable(results, schema, operation_handle)


  def execute_async_query(self, query, statement=0):
    # Set configuration manually until Hive Server 2 supports confOverlay
    # This will leak the config in the session
    if statement == 0:
      if self.query_server['server_name'] == 'beeswax':
        self.execute_statement(statement='SET hive.server2.blocking.query=true')
        for resource in query.get_configuration():
          self.execute_statement(resource.strip())

    if self.query_server['server_name'] == 'beeswax':
      self.execute_statement(statement='SET hive.server2.blocking.query=false')

    configuration = self._get_query_configuration(query)

    query_statement =  query.get_query_statement(statement)
    return self.execute_async_statement(statement=query_statement, confOverlay=configuration)


  def execute_statement(self, statement, max_rows=5000, configuration={}):
    req = TExecuteStatementReq(statement=statement.encode('utf-8'), confOverlay=configuration)
    res = self.call(self._client.ExecuteStatement, req)

    return self.fetch_result(res.operationHandle, max_rows=max_rows), res.operationHandle


  def execute_async_statement(self, statement, confOverlay):
    req = TExecuteStatementReq(statement=statement.encode('utf-8'), confOverlay=confOverlay)
    res = self.call(self._client.ExecuteStatement, req)

    return HiveServerQueryHandle(secret=res.operationHandle.operationId.secret,
                                 guid=res.operationHandle.operationId.guid,
                                 operation_type=res.operationHandle.operationType,
                                 has_result_set=res.operationHandle.hasResultSet,
                                 modified_row_count=res.operationHandle.modifiedRowCount)



  def fetch_data(self, operation_handle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=5000):
    # The client should check for hasMoreRows and fetch until the result is empty dues to a HS2 bug
    results, schema = self.fetch_result(operation_handle, orientation, max_rows)
    return HiveServerDataTable(results, schema, operation_handle)


  def cancel_operation(self, operation_handle):
    req = TCancelOperationReq(operationHandle=operation_handle)
    return self.call(self._client.CancelOperation, req)


  def close_operation(self, operation_handle):
    req = TCloseOperationReq(operationHandle=operation_handle)
    return self.call(self._client.CloseOperation, req)


  def get_columns(self, database, table):
    req = TGetColumnsReq(schemaName=database, tableName=table)
    res = self.call(self._client.GetColumns, req)

    res, schema = self.fetch_result(res.operationHandle)
    self.close_operation(res.operationHandle)

    return res, schema



  def fetch_result(self, operation_handle, orientation=TFetchOrientation.FETCH_NEXT, max_rows=5000):
    fetch_req = TFetchResultsReq(operationHandle=operation_handle, orientation=orientation, maxRows=max_rows)
    res = self.call(self._client.FetchResults, fetch_req)

    if operation_handle.hasResultSet:
      meta_req = TGetResultSetMetadataReq(operationHandle=operation_handle)
      schema = self.call(self._client.GetResultSetMetadata, meta_req)
    else:
      schema = None

    return res, schema


  def get_operation_status(self, operation_handle):
    req = TGetOperationStatusReq(operationHandle=operation_handle)
    return self.call(self._client.GetOperationStatus, req)


  def explain(self, query):
    return self.execute_query_statement('EXPLAIN %s' % query.query['query'])


  def get_log(self, operation_handle):
    try:
      req = TGetLogReq(operationHandle=operation_handle)
      res = self.call(self._client.GetLog, req)
      return res.log
    except:
      return 'Server does not support GetLog()'


  def get_partitions(self, database, table_name, max_parts):
    table = self.get_table(database, table_name)
    if self.query_server['server_name'] == 'beeswax':
      self.execute_statement(statement='SET hive.server2.blocking.query=true')

    partitionTable = self.execute_query_statement('SHOW PARTITIONS %s' % table_name) # DB prefix not supported
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
                                    'type': col.get('data_type', ''),
                                    'comment': col.get('comment', '').strip(), }) for col in HiveServerTable.cols.fget(self)]

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

  def __init__(self, partition):
    # Parses: ['name:datehour, type:int, comment:null']
    name, type, comment = partition.split(', ')
    self.name = name.split(':')[1]
    self.type = type.split(':')[1]
    self.comment = comment.split(':')[1]


class PartitionValueCompatible:

  def __init__(self, partition, table):
    # Parses: ['datehour=2013022516']
    self.values = [part.split('=')[1] for part in partition]
    self.sd = type('Sd', (object,), {'location': '%s/%s' % (table.path_location, ','.join(partition)),})


class ExplainCompatible:

  def __init__(self, data_table):
    self.textual = '\n'.join([line[0] for line in data_table.rows()])


class ResultMetaCompatible:

  def __init__(self):
    self.in_tablename = True


class HiveServerClientCompatible:
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
      max_rows = 5000

    # Impala does not support FETCH_FIRST
    if self.query_server['server_name'] == 'impala':
      start_over = False

    if start_over:
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


  def dump_config(self):
    return 'Does not exist in HS2'


  def echo(self, msg):
    return 'Does not exist in HS2'


  def get_log(self, handle):
    operationHandle = handle.get_rpc_handle()
    return self._client.get_log(operationHandle)


  def get_databases(self):
    col = 'TABLE_SCHEM'
    return [table[col] for table in self._client.get_databases()]


  def get_tables(self, database, table_names):
    return [table['TABLE_NAME'] for table in self._client.get_tables(database, table_names)]


  def get_table(self, database, table_name):
    table = self._client.get_table(database, table_name)
    return HiveServerTableCompatible(table)


  def get_default_configuration(self, *args, **kwargs):
    return {}


  def get_results_metadata(self, handle):
    # We just need to mock
    return ResultMetaCompatible()


  def create_database(self, name, description): raise NotImplementedError()


  def get_database(self, *args, **kwargs): raise NotImplementedError()


  def alter_table(self, dbname, tbl_name, new_tbl): raise NotImplementedError()


  def add_partition(self, new_part): raise NotImplementedError()


  def get_partition(self, *args, **kwargs): raise NotImplementedError()


  def get_partitions(self, database, table_name, max_parts):
    return self._client.get_partitions(database, table_name, max_parts)


  def alter_partition(self, db_name, tbl_name, new_part): raise NotImplementedError()
