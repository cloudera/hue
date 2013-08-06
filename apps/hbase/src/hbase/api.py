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

try:
  import json
except ImportError:
  import simplejson as json
import logging
import re

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib import thrift_util
from desktop.lib.exceptions_renderable import PopupException

from hbase.server.hbase_lib import get_thrift_attributes, get_thrift_type, get_client_type
from hbase import conf

LOG = logging.getLogger(__name__)

#format methods similar to Thrift API, for similarity with catch-all
class HbaseApi(object):
  def query(self, action, *args):
    try:
      if hasattr(self,action):
        return getattr(self, action)(*args)
      cluster = args[0]
      return self.queryCluster(action, cluster, *args[1:])
    except Exception, e:
      raise PopupException(_("Api Error: %s") % e.message)

  def queryCluster(self, action, cluster, *args):
    client = self.connectCluster(cluster)
    method = getattr(client, action)
    return method(*args)

  def getClusters(self):
    clusters = []
    try:
      full_config = json.loads(conf.HBASE_CLUSTERS.get().replace("'","\""))
    except:
      full_config = [conf.HBASE_CLUSTERS.get()]
    for config in full_config: #hack cause get() is weird
      match = re.match('\((?P<name>[^\(\)\|]+)\|(?P<host>.+):(?P<port>[0-9]+)\)', config)
      clusters += [{
        'name': match.group('name'),
        'host': match.group('host'),
        'port': int(match.group('port'))
      }]
    return clusters

  def getCluster(self, name):
    try:
      clusters = self.getClusters()
      for cluster in clusters:
        if cluster["name"] == name:
          return cluster
    except Exception, e:
      pass
    raise PopupException(_("Cluster by the name of %s does not exist in configuration.") % name)

  def connectCluster(self, name):
    target = self.getCluster(name)
    return thrift_util.get_client(get_client_type(),
                                  target['host'],
                                  target['port'],
                                  service_name="Hue HBase Thrift Client for %s" % name,
                                  kerberos_principal=None,
                                  use_sasl=False,
                                  timeout_seconds=None)

  def createTable(self, cluster, tableName, *columns):
    client = self.connectCluster(cluster)
    client.createTable(tableName, [get_thrift_type('ColumnDescriptor')(name=column) for column in columns])
    return "%s successfully created" % tableName

  def getTableList(self, cluster):
    client = self.connectCluster(cluster)
    return [{'name': name,'enabled': client.isTableEnabled(name)} for name in client.getTableNames()]

  def getRows(self, cluster, tableName, columns, startRowKey, numRows, prefix = False):
    client = self.connectCluster(cluster)
    if prefix == False:
      scanner = client.scannerOpen(tableName, startRowKey, columns, None)
    else:
      scanner = client.scannerOpenWithPrefix(tableName, startRowKey, columns, None)
    data = client.scannerGetList(scanner, numRows)
    client.scannerClose(scanner)
    return data

  def getAutocompleteRows(self, cluster, tableName, numRows, query):
    try:
      client = self.connectCluster(cluster)
      scan = get_thrift_type('TScan')(startRow=query, stopRow=None, timestamp=None, columns=[], caching=None, filterString="PrefixFilter('" + query + "') AND ColumnPaginationFilter(1,0)", batchSize=None)
      scanner = client.scannerOpenWithScan(tableName, scan, None)
      return [result.row for result in client.scannerGetList(scanner, numRows)]
    except:
      return []

  def getRow(self, cluster, tableName, columns, startRowKey):
    row = self.getRows(cluster, tableName, columns, startRowKey, 1)
    if len(row) > 0:
      return row[0]
    return None

  def getRowsFull(self, cluster, tableName, startRowKey, numRows):
    client = self.connectCluster(cluster)
    return self.getRows(cluster, tableName, [column for column in client.getColumnDescriptors(tableName)], startRowKey, numRows)

  def getRowFull(self, cluster, tableName, startRowKey, numRows):
    row = self.getRowsFull(cluster, tableName, startRowKey, 1)
    if len(row) > 0:
      return row[0]
    return None

  def deleteColumns(self, cluster, tableName, row, columns):
    client = self.connectCluster(cluster)
    Mutation = get_thrift_type('Mutation')
    mutations = [Mutation(isDelete = True, column=column) for column in columns]
    return client.mutateRow(tableName, row, mutations, None)

  def deleteColumn(self, cluster, tableName, row, column):
    return self.deleteColumns(cluster, tableName, row, [column])

  def putRow(self, cluster, tableName, row, data):
    client = self.connectCluster(cluster)
    mutations = []
    Mutation = get_thrift_type('Mutation')
    for column in data.keys():
      mutations.append(Mutation(column=column, value=str(data[column]))) # must use str for API, does thrift coerce by itself?
    return client.mutateRow(tableName, row, mutations, None)

  def putColumn(self, cluster, tableName, row, column, value):
    return self.putRow(cluster, tableName, row, {column: value})

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
        fs = " AND (" + fs + ")"
      filterstring = "(ColumnPaginationFilter(" + str(limit) + ",0) AND PageFilter(" + str(limit) + "))" + (fs or "")
      scan = get_thrift_type('TScan')(startRow=query['row_key'], stopRow=None, timestamp=None, columns=query['columns'] or columns, caching=None, filterString=filterstring, batchSize=None)
      scanner = client.scannerOpenWithScan(tableName, scan, None)
      aggregate_data += client.scannerGetList(scanner, query['scan_length'])
    return aggregate_data
