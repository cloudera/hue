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
import csv

from django.utils.translation import ugettext as _
from django.utils.encoding import smart_str

from desktop.lib import thrift_util
from desktop.lib.exceptions_renderable import PopupException

from hbase import conf
from hbase.hbase_site import get_server_principal, get_server_authentication, is_using_thrift_ssl, is_using_thrift_http, get_thrift_transport
from hbase.server.hbase_lib import get_thrift_type, get_client_type


LOG = logging.getLogger(__name__)


# Format methods similar to Thrift API, for similarity with catch-all
class HbaseApi(object):

  def __init__(self, user):
    self.user = user

  def query(self, action, *args):
    try:
      if hasattr(self, action):
        return getattr(self, action)(*args)
      cluster = args[0]
      return self.queryCluster(action, cluster, *args[1:])
    except Exception, e:
      if 'Could not connect to' in e.message:
        raise PopupException(_("HBase Thrift 1 server cannot be contacted: %s") % e.message)
      else:
        error_msg = e.message.split('\n', 1)[0]
        raise PopupException(_("Api Error: %s") % error_msg)

  def queryCluster(self, action, cluster, *args):
    client = self.connectCluster(cluster)
    method = getattr(client, action)
    return method(*args, doas=self.user.username)

  def getClusters(self):
    clusters = []
    try:
      full_config = json.loads(conf.HBASE_CLUSTERS.get().replace("'", "\""))
    except:
      LOG.debug('Failed to read HBase cluster configuration as JSON, falling back to raw configuration.')
      full_config = [conf.HBASE_CLUSTERS.get()] #hack cause get() is weird

    for config in full_config:
      match = re.match('\((?P<name>[^\(\)\|]+)\|(?P<host>.+):(?P<port>[0-9]+)\)', config)
      if match:
        clusters += [{
          'name': match.group('name'),
          'host': match.group('host'),
          'port': int(match.group('port'))
        }]
      else:
        raise Exception(_("Cluster configuration %s isn't formatted correctly.") % config)
    return clusters

  def getCluster(self, name):
    try:
      clusters = self.getClusters()
      for cluster in clusters:
        if cluster["name"] == name:
          return cluster
    except:
      LOG.exception('failed to get the cluster %s' % name)
    raise PopupException(_("Cluster by the name of %s does not exist in configuration.") % name)

  def connectCluster(self, name):
    _security = self._get_security()
    target = self.getCluster(name)
    client = thrift_util.get_client(
        get_client_type(),
        target['host'],
        target['port'],
        service_name="Hue HBase Thrift Client for %s" % name,
        kerberos_principal=_security['kerberos_principal_short_name'],
        use_sasl=_security['use_sasl'],
        timeout_seconds=30,
        transport=get_thrift_transport(),
        transport_mode='http' if is_using_thrift_http() else 'socket',
        http_url=('https://' if is_using_thrift_ssl() else 'http://') + target['host'] + ':' + str(target['port']),
        validate=conf.SSL_CERT_CA_VERIFY.get()
    )

    return client

  @classmethod
  def _get_security(cls):
    principal = get_server_principal()
    if principal:
      kerberos_principal_short_name = principal.split('/', 1)[0]
    else:
      kerberos_principal_short_name = None
    use_sasl = get_server_authentication() == 'KERBEROS'

    if use_sasl and kerberos_principal_short_name is None:
      raise PopupException(_("The kerberos principal name is missing from the hbase-site.xml configuration file."))

    return {
        'kerberos_principal_short_name': kerberos_principal_short_name,
        'use_sasl': use_sasl,
    }

  def get(self, cluster, tableName, row, column, attributes):
    client = self.connectCluster(cluster)
    return client.get(tableName, smart_str(row), smart_str(column), attributes, doas=self.user.username)

  def getVerTs(self, cluster, tableName, row, column, timestamp, numVersions, attributesargs):
    client = self.connectCluster(cluster)
    return client.getVerTs(tableName, smart_str(row), smart_str(column), timestamp, numVersions, attributesargs, doas=self.user.username)

  def createTable(self, cluster, tableName, columns):
    client = self.connectCluster(cluster)
    client.createTable(tableName, [get_thrift_type('ColumnDescriptor')(**column['properties']) for column in columns], doas=self.user.username)
    return "%s successfully created" % tableName

  def getTableList(self, cluster):
    client = self.connectCluster(cluster)
    return [{'name': name, 'enabled': client.isTableEnabled(name, doas=self.user.username)} for name in client.getTableNames(doas=self.user.username)]

  def getRows(self, cluster, tableName, columns, startRowKey, numRows, prefix=False):
    client = self.connectCluster(cluster)
    if prefix == False:
      scanner = client.scannerOpen(tableName, smart_str(startRowKey), columns, None, doas=self.user.username)
    else:
      scanner = client.scannerOpenWithPrefix(tableName, smart_str(startRowKey), columns, None, doas=self.user.username)
    data = client.scannerGetList(scanner, numRows, doas=self.user.username)
    client.scannerClose(scanner, doas=self.user.username)
    return data

  def getAutocompleteRows(self, cluster, tableName, numRows, query):
    query = smart_str(query)
    try:
      client = self.connectCluster(cluster)
      scan = get_thrift_type('TScan')(startRow=query, stopRow=None, timestamp=None, columns=[], caching=None, filterString="PrefixFilter('" + query + "') AND ColumnPaginationFilter(1,0)", batchSize=None)
      scanner = client.scannerOpenWithScan(tableName, scan, None, doas=self.user.username)
      return [result.row for result in client.scannerGetList(scanner, numRows, doas=self.user.username)]
    except Exception, e:
      LOG.error('Autocomplete error: %s' % smart_str(e))
      return []

  def getRow(self, cluster, tableName, columns, startRowKey):
    row = self.getRows(cluster, tableName, columns, smart_str(startRowKey), 1)
    if len(row) > 0:
      return row[0]
    return None

  def getRowsFull(self, cluster, tableName, startRowKey, numRows):
    client = self.connectCluster(cluster)
    return self.getRows(cluster, tableName, [smart_str(column) for column in client.getColumnDescriptors(tableName, doas=self.user.username)], smart_str(startRowKey), numRows)

  def getRowFull(self, cluster, tableName, startRowKey, numRows):
    row = self.getRowsFull(cluster, tableName, smart_str(startRowKey), 1)
    if len(row) > 0:
      return row[0]
    return None

  def getRowPartial(self, cluster, tableName, rowKey, offset, number):
    client = self.connectCluster(cluster)
    scan = get_thrift_type('TScan')(startRow=rowKey, stopRow=None, timestamp=None, columns=[], caching=None, filterString="ColumnPaginationFilter(%i, %i)" % (number, offset), batchSize=None)
    scanner = client.scannerOpenWithScan(tableName, scan, None, doas=self.user.username)
    return client.scannerGetList(scanner, 1, doas=self.user.username)

  def deleteColumns(self, cluster, tableName, row, columns):
    client = self.connectCluster(cluster)
    Mutation = get_thrift_type('Mutation')
    mutations = [Mutation(isDelete = True, column=smart_str(column)) for column in columns]
    return client.mutateRow(tableName, smart_str(row), mutations, None, doas=self.user.username)

  def deleteColumn(self, cluster, tableName, row, column):
    return self.deleteColumns(cluster, tableName, smart_str(row), [smart_str(column)])

  def deleteAllRow(self, cluster, tableName, row, attributes):
    client = self.connectCluster(cluster)
    return client.deleteAllRow(tableName, smart_str(row), attributes, doas=self.user.username)

  def putRow(self, cluster, tableName, row, data):
    client = self.connectCluster(cluster)
    mutations = []
    Mutation = get_thrift_type('Mutation')
    for column in data.keys():
      value = smart_str(data[column]) if data[column] is not None else None
      mutations.append(Mutation(column=smart_str(column), value=value)) # must use str for API, does thrift coerce by itself?
    return client.mutateRow(tableName, smart_str(row), mutations, None, doas=self.user.username)

  def putColumn(self, cluster, tableName, row, column, value=None):
    return self.putRow(cluster, tableName, smart_str(row), {column: value})

  def putUpload(self, cluster, tableName, row, column, value):
    client = self.connectCluster(cluster)
    Mutation = get_thrift_type('Mutation')
    return client.mutateRow(tableName, smart_str(row), [Mutation(column=smart_str(column), value=value.file.read(value.size))], None, doas=self.user.username)

  def getRowQuerySet(self, cluster, tableName, columns, queries):
    client = self.connectCluster(cluster)
    aggregate_data = []
    limit = conf.TRUNCATE_LIMIT.get()
    queries = sorted(queries, key=lambda query: query['scan_length']) #sort by scan length
    for query in queries:
      scan_length = int(query['scan_length'])
      if query['row_key'] == "null":
        query['row_key'] = ""
      fs = query.get('filter', None)
      if fs:
        fs = " AND (" + fs.strip() + ")"
      filterstring = "(ColumnPaginationFilter(%i,0) AND PageFilter(%i))" % (limit, limit) + (fs or "")
      scan_columns = [smart_str(column.strip(':')) for column in query['columns']] or [smart_str(column.strip(':')) for column in columns]
      scan = get_thrift_type('TScan')(startRow=smart_str(query['row_key']), stopRow=None, timestamp=None, columns=scan_columns, caching=None, filterString=filterstring, batchSize=None)
      scanner = client.scannerOpenWithScan(tableName, scan, None, doas=self.user.username)
      aggregate_data += client.scannerGetList(scanner, query['scan_length'], doas=self.user.username)
    return aggregate_data

  def bulkUpload(self, cluster, tableName, data):
    client = self.connectCluster(cluster)
    BatchMutation = get_thrift_type('BatchMutation')
    Mutation = get_thrift_type('Mutation')
    columns = []
    data = data.read()
    dialect = csv.Sniffer().sniff(data)
    reader = csv.reader(data.splitlines(), delimiter=dialect.delimiter)
    columns = reader.next()
    batches = []
    for row in reader:
      row_key = row[0]
      row_data = {}
      mutations = []
      for column_index in range(1, len(row)):
        if str(row[column_index]) != "":
          mutations.append(Mutation(column=smart_str(columns[column_index]), value=smart_str(row[column_index])))
      batches += [BatchMutation(row=row_key, mutations=mutations)]
    client.mutateRows(tableName, batches, None, doas=self.user.username)
    return True
