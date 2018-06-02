#!/usr/bin/env python
# -- coding: utf-8 --
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

from django.utils.translation import ugettext as _

from metadata.catalog.base import Api


LOG = logging.getLogger(__name__)


class DummyApi(Api):

  def __init__(self, user=None):
    self.user = user


  def search_entities_interactive(self, query_s=None, limit=100, **filters):
    return {u'highlighting': {u'27': {u'sourceType': [u'<em>HIVE</em>'], u'originalName': [u'<em>sample_08</em>'], u'owner': [u'<em>admin</em>'], u'type': [u'<em>TABLE</em>'], u'fileSystemPath': [u'<em>hdfs://self-service-analytics-1.gce.cloudera.com:8020/user/hive/warehouse/sample_08</em>'], u'internalType': [u'<em>hv_table</em>']}, u'1144700': {u'sourceType': [u'<em>HIVE</em>'], u'originalName': [u'<em>sample_07_parquet</em>'], u'owner': [u'<em>admin</em>'], u'type': [u'<em>TABLE</em>'], u'fileSystemPath': [u'<em>hdfs://self-service-analytics-1.gce.cloudera.com:8020/user/hive/warehouse/sample_07_parquet</em>'], u'internalType': [u'<em>hv_table</em>']}, u'22': {u'sourceType': [u'<em>HIVE</em>'], u'description': [u'<em>Job</em> <em>data</em>'], u'originalName': [u'<em>sample_07</em>'], u'owner': [u'<em>admin</em>'], u'type': [u'<em>TABLE</em>'], u'fileSystemPath': [u'<em>hdfs://self-service-analytics-1.gce.cloudera.com:8020/user/hive/warehouse/sample_07</em>'], u'internalType': [u'<em>hv_table</em>']}}, u'facets': {}, u'qtime': 1339, u'facetRanges': [], u'results': [{u'clusteredByColNames': None, u'customProperties': {}, u'owner': u'admin', u'serdeName': None, u'deleteTime': None, u'fileSystemPath': u'hdfs://self-service-analytics-1.gce.cloudera.com:8020/user/hive/warehouse/sample_08', u'sourceType': u'HIVE', u'serdeLibName': u'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe', u'lastModifiedBy': None, u'sortByColNames': None, u'partColNames': None, u'type': u'TABLE', u'internalType': u'hv_table', u'description': None, u'inputFormat': u'org.apache.hadoop.mapred.TextInputFormat', u'tags': None, u'deleted': False, u'technicalProperties': None, u'userEntity': False, u'serdeProps': None, u'originalDescription': None, u'compressed': False, u'metaClassName': u'hv_table', u'properties': {u'__cloudera_internal__hueLink': u'http://self-service-analytics-1.gce.cloudera.com:8889/metastore/table/default/sample_08', u'dd': u'xx'}, u'identity': u'27', u'outputFormat': u'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat', u'firstClassParentId': None, u'name': None, u'extractorRunId': u'8##503', u'created': u'2018-03-30T17:14:44.000Z', u'sourceId': u'8', u'lastModified': None, u'packageName': u'nav', u'parentPath': u'/default', u'originalName': u'sample_08', u'lastAccessed': u'1970-01-01T00:00:00.000Z'}, {u'clusteredByColNames': None, u'customProperties': {}, u'owner': u'admin', u'serdeName': None, u'deleteTime': None, u'fileSystemPath': u'hdfs://self-service-analytics-1.gce.cloudera.com:8020/user/hive/warehouse/sample_07_parquet', u'sourceType': u'HIVE', u'serdeLibName': u'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe', u'lastModifiedBy': None, u'sortByColNames': None, u'partColNames': None, u'type': u'TABLE', u'internalType': u'hv_table', u'description': None, u'inputFormat': u'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat', u'tags': None, u'deleted': False, u'technicalProperties': None, u'userEntity': False, u'serdeProps': None, u'originalDescription': None, u'compressed': False, u'metaClassName': u'hv_table', u'properties': {u'__cloudera_internal__hueLink': u'http://self-service-analytics-1.gce.cloudera.com:8889/metastore/table/default/sample_07_parquet'}, u'identity': u'1144700', u'outputFormat': u'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat', u'firstClassParentId': None, u'name': None, u'extractorRunId': u'8##718', u'created': u'2018-04-17T06:16:17.000Z', u'sourceId': u'8', u'lastModified': None, u'packageName': u'nav', u'parentPath': u'/default', u'originalName': u'sample_07_parquet', u'lastAccessed': u'1970-01-01T00:00:00.000Z'}, {u'clusteredByColNames': None, u'customProperties': {}, u'owner': u'admin', u'serdeName': None, u'deleteTime': None, u'fileSystemPath': u'hdfs://self-service-analytics-1.gce.cloudera.com:8020/user/hive/warehouse/sample_07', u'sourceType': u'HIVE', u'serdeLibName': u'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe', u'lastModifiedBy': None, u'sortByColNames': None, u'partColNames': None, u'type': u'TABLE', u'internalType': u'hv_table', u'description': u'Job data', u'inputFormat': u'org.apache.hadoop.mapred.TextInputFormat', u'tags': None, u'deleted': False, u'technicalProperties': None, u'userEntity': False, u'serdeProps': None, u'originalDescription': None, u'compressed': False, u'metaClassName': u'hv_table', u'properties': {u'__cloudera_internal__hueLink': u'http://self-service-analytics-1.gce.cloudera.com:8889/metastore/table/default/sample_07'}, u'identity': u'22', u'outputFormat': u'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat', u'firstClassParentId': None, u'name': None, u'extractorRunId': u'8##503', u'created': u'2018-03-30T17:14:42.000Z', u'sourceId': u'8', u'lastModified': None, u'packageName': u'nav', u'parentPath': u'/default', u'originalName': u'sample_07', u'lastAccessed': u'1970-01-01T00:00:00.000Z'}], u'totalMatched': 3, u'limit': 45, u'offset': 0}


  def find_entity(self, source_type, type, name, **filters):
    return [{u'clusteredByColNames': None, u'customProperties': {}, u'owner': u'admin', u'serdeName': None, u'deleteTime': None, u'fileSystemPath': u'hdfs://self-service-analytics-1.gce.cloudera.com:8020/user/hive/warehouse/sample_07', u'sourceType': u'HIVE', u'serdeLibName': u'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe', u'lastModifiedBy': None, u'sortByColNames': None, u'partColNames': None, u'type': u'TABLE', u'internalType': u'hv_table', u'description': u'Job data', u'inputFormat': u'org.apache.hadoop.mapred.TextInputFormat', u'tags': None, u'deleted': False, u'technicalProperties': None, u'userEntity': False, u'serdeProps': None, u'originalDescription': None, u'compressed': False, u'metaClassName': u'hv_table', u'properties': {u'__cloudera_internal__hueLink': u'http://self-service-analytics-1.gce.cloudera.com:8889/metastore/table/default/sample_07'}, u'identity': u'22', u'outputFormat': u'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat', u'firstClassParentId': None, u'name': None, u'extractorRunId': u'8##503', u'created': u'2018-03-30T17:14:42.000Z', u'sourceId': u'8', u'lastModified': None, u'packageName': u'nav', u'parentPath': u'/default', u'originalName': u'sample_07', u'lastAccessed': u'1970-01-01T00:00:00.000Z'}]


  def get_entity(self, entity_id):
    return {u'customProperties': None, u'deleteTime': None, u'description': None, u'dataType': u'int', u'type': u'FIELD', u'internalType': u'hv_column', u'sourceType': u'HIVE', u'tags': None, u'deleted': False, u'technicalProperties': None, u'userEntity': False, u'originalDescription': None, u'metaClassName': u'hv_column', u'properties': {u'__cloudera_internal__hueLink': u'http://self-service-analytics-1.gce.cloudera.com:8889/metastore/table/default/sample_07'}, u'identity': u'26', u'firstClassParentId': u'22', u'name': None, u'extractorRunId': u'8##1', u'sourceId': u'8', u'packageName': u'nav', u'parentPath': u'/default/sample_07', u'originalName': u'total_emp'}


  def update_entity(self, entity, **metadata):
    return {}


  def add_tags(self, entity_id, tags):
    # Return entity but not used currently
    return {u'clusteredByColNames': None, u'customProperties': {}, u'owner': u'admin', u'serdeName': None, u'deleteTime': None, u'fileSystemPath': u'hdfs://self-service-analytics-1.gce.cloudera.com:8020/user/hive/warehouse/sample_07', u'sourceType': u'HIVE', u'serdeLibName': u'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe', u'lastModifiedBy': None, u'sortByColNames': None, u'partColNames': None, u'type': u'TABLE', u'internalType': u'hv_table', u'description': u'Job data', u'inputFormat': u'org.apache.hadoop.mapred.TextInputFormat', u'tags': [u'usage'], u'deleted': False, u'technicalProperties': None, u'userEntity': False, u'serdeProps': None, u'originalDescription': None, u'compressed': False, u'metaClassName': u'hv_table', u'properties': {u'__cloudera_internal__hueLink': u'http://self-service-analytics-1.gce.cloudera.com:8889/metastore/table/default/sample_07'}, u'identity': u'22', u'outputFormat': u'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat', u'firstClassParentId': None, u'name': None, u'extractorRunId': u'8##503', u'created': u'2018-03-30T17:14:42.000Z', u'sourceId': u'8', u'lastModified': None, u'packageName': u'nav', u'parentPath': u'/default', u'originalName': u'sample_07', u'lastAccessed': u'1970-01-01T00:00:00.000Z'}


  def delete_tags(self, entity_id, tags):
    return {}


  def update_properties(self, entity_id, properties, modified_custom_metadata=None, deleted_custom_metadata_keys=None):
    # For updating comments of table or columns
    # Returning the entity but not used currently
    return {u'clusteredByColNames': None, u'customProperties': {}, u'owner': u'admin', u'serdeName': None, u'deleteTime': None, u'fileSystemPath': u'hdfs://self-service-analytics-1.gce.cloudera.com:8020/user/hive/warehouse/sample_07', u'sourceType': u'HIVE', u'serdeLibName': u'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe', u'lastModifiedBy': None, u'sortByColNames': None, u'partColNames': None, u'type': u'TABLE', u'internalType': u'hv_table', u'description': u'Adding an description', u'inputFormat': u'org.apache.hadoop.mapred.TextInputFormat', u'tags': [u'usage'], u'deleted': False, u'technicalProperties': None, u'userEntity': False, u'serdeProps': None, u'originalDescription': None, u'compressed': False, u'metaClassName': u'hv_table', u'properties': {u'__cloudera_internal__hueLink': u'http://self-service-analytics-1.gce.cloudera.com:8889/metastore/table/default/sample_07'}, u'identity': u'22', u'outputFormat': u'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat', u'firstClassParentId': None, u'name': None, u'extractorRunId': u'8##503', u'created': u'2018-03-30T17:14:42.000Z', u'sourceId': u'8', u'lastModified': None, u'packageName': u'nav', u'parentPath': u'/default', u'originalName': u'sample_07', u'lastAccessed': u'1970-01-01T00:00:00.000Z'}

