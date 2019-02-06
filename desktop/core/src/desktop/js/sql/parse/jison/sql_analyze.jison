// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

DataDefinition
 : AnalyzeStatement
 | RefreshStatement
 | InvalidateStatement
 | ComputeStatsStatement
 ;

DataDefinition_EDIT
 : AnalyzeStatement_EDIT
 | RefreshStatement_EDIT
 | InvalidateStatement_EDIT
 | ComputeStatsStatement_EDIT
 ;

AnalyzeStatement
 : '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec '<hive>COMPUTE' '<hive>STATISTICS' OptionalForColumns OptionalCacheMetadata OptionalNoscan
   {
     parser.addTablePrimary($3);
   }
 ;

AnalyzeStatement_EDIT
 : '<hive>ANALYZE' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | '<hive>ANALYZE' '<hive>TABLE' 'CURSOR'
   {
     parser.suggestTables({ onlyTables: true });
     parser.suggestDatabases({ appendDot: true });
   }
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyTables = true;
     }
   }
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT
   {
     parser.addTablePrimary($3);
   }
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($3);
     if (!$4) {
       parser.suggestKeywords([{ value: 'PARTITION', weight: 2 }, { value: 'COMPUTE STATISTICS', weight: 1 }]);
     } else {
       parser.suggestKeywords(['COMPUTE STATISTICS']);
     }
   }
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec '<hive>COMPUTE' 'CURSOR'
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['STATISTICS']);
   }
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec '<hive>COMPUTE' '<hive>STATISTICS' 'CURSOR' OptionalForColumns OptionalCacheMetadata OptionalNoscan
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(parser.getKeywordsForOptionalsLR([$8, $9, $10], [{ value: 'FOR COLUMNS', weight: 3 }, { value: 'CACHE METADATA', weight: 2 }, { value: 'NOSCAN', weight: 1 }]));
   }
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec '<hive>COMPUTE' '<hive>STATISTICS' ForColumns 'CURSOR' OptionalCacheMetadata OptionalNoscan
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(parser.getKeywordsForOptionalsLR([$9, $10], [{ value: 'CACHE METADATA', weight: 2 }, { value: 'NOSCAN', weight: 1 }]));
   }
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec '<hive>COMPUTE' '<hive>STATISTICS' OptionalForColumns CacheMetadata 'CURSOR' OptionalNoscan
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(parser.getKeywordsForOptionalsLR([$10], [{ value: 'NOSCAN', weight: 1 }]));
   }
 | '<hive>ANALYZE' 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.suggestKeywords(['TABLE']);
     parser.addTablePrimary($3);
   }
 | '<hive>ANALYZE' 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec '<hive>COMPUTE' '<hive>STATISTICS' OptionalForColumns OptionalCacheMetadata OptionalNoscan
   {
     parser.suggestKeywords(['TABLE']);
     parser.addTablePrimary($3);
   }
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec '<hive>COMPUTE' '<hive>STATISTICS' OptionalForColumns OptionalCacheMetadata OptionalNoscan
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT '<hive>COMPUTE' '<hive>STATISTICS' OptionalForColumns OptionalCacheMetadata OptionalNoscan
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec '<hive>COMPUTE' '<hive>STATISTICS' ForColumns_EDIT OptionalCacheMetadata OptionalNoscan
 | '<hive>ANALYZE' '<hive>TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec '<hive>COMPUTE' '<hive>STATISTICS' OptionalForColumns CacheMetadata_EDIT OptionalNoscan
 ;

OptionalForColumns
 :
 | ForColumns
 ;

ForColumns
 : '<hive>FOR' '<hive>COLUMNS'
 ;

ForColumns_EDIT
 : '<hive>FOR' 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS']);
   }
 ;

OptionalCacheMetadata
 :
 | CacheMetadata
 ;

CacheMetadata
 : '<hive>CACHE' '<hive>METADATA'
 ;

CacheMetadata_EDIT
 : '<hive>CACHE' 'CURSOR'
   {
     parser.suggestKeywords(['METADATA']);
   }
 ;

OptionalNoscan
 :
 | '<hive>NOSCAN'
 ;

RefreshStatement
 : '<impala>REFRESH' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($2);
   }
 | '<impala>REFRESH' '<impala>FUNCTIONS' DatabaseIdentifier
   {
     parser.addDatabaseLocation(@3, [{ name: $3 }]);
   }
 | '<impala>REFRESH' '<impala>AUTHORIZATION'
 ;

RefreshStatement_EDIT
 : '<impala>REFRESH' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
     parser.suggestKeywords(['AUTHORIZATION', 'FUNCTIONS']);
   }
 | '<impala>REFRESH' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | '<impala>REFRESH' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($2);
     if (!$3) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | '<impala>REFRESH' SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT
 | '<impala>REFRESH' '<impala>FUNCTIONS' 'CURSOR'
   {
     parser.suggestDatabases();
   }
 ;

InvalidateStatement
 : '<impala>INVALIDATE' '<impala>METADATA'
 | '<impala>INVALIDATE' '<impala>METADATA' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 ;

InvalidateStatement_EDIT
 : '<impala>INVALIDATE' 'CURSOR'
   {
     parser.suggestKeywords(['METADATA']);
   }
 | '<impala>INVALIDATE' '<impala>METADATA' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | '<impala>INVALIDATE' '<impala>METADATA' SchemaQualifiedTableIdentifier_EDIT
 | '<impala>INVALIDATE' 'CURSOR' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['METADATA']);
   }
 ;

ComputeStatsStatement
 : '<impala>COMPUTE' '<impala>STATS' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalImpalaTableSample
   {
     parser.addTablePrimary($3);
   }
 | '<impala>COMPUTE' '<impala>INCREMENTAL' '<impala>STATS' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
   }
 ;

ComputeStatsStatement_EDIT
 : '<impala>COMPUTE' 'CURSOR'
   {
     parser.suggestKeywords(['STATS', 'INCREMENTAL STATS']);
   }
 | '<impala>COMPUTE' '<impala>STATS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | '<impala>COMPUTE' '<impala>STATS' SchemaQualifiedTableIdentifier_EDIT
 | '<impala>COMPUTE' 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['STATS', 'INCREMENTAL STATS']);
   }
 | '<impala>COMPUTE' '<impala>STATS' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalImpalaTableSample 'CURSOR'
   {
     parser.addTablePrimary($3);
     if (!$5) {
       parser.suggestKeywords(['TABLESAMPLE']);
     } else if ($5.suggestKeywords) {
       parser.suggestKeywords($5.suggestKeywords);
     }
   }
 | '<impala>COMPUTE' '<impala>STATS' SchemaQualifiedTableIdentifier ParenthesizedColumnList_EDIT OptionalImpalaTableSample
   {
     parser.addTablePrimary($3);
   }
 | '<impala>COMPUTE' '<impala>STATS' SchemaQualifiedTableIdentifier OptionalParenthesizedColumnList OptionalImpalaTableSample_EDIT
   {
     parser.addTablePrimary($3);
   }
 | '<impala>COMPUTE' 'CURSOR' '<impala>STATS' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['INCREMENTAL']);
   }
 | '<impala>COMPUTE' '<impala>INCREMENTAL' 'CURSOR'
   {
     parser.suggestKeywords(['STATS']);
   }
 | '<impala>COMPUTE' '<impala>INCREMENTAL' 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['STATS']);
   }
 | '<impala>COMPUTE' '<impala>INCREMENTAL' '<impala>STATS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | '<impala>COMPUTE' '<impala>INCREMENTAL' '<impala>STATS' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | '<impala>COMPUTE' '<impala>INCREMENTAL' '<impala>STATS' SchemaQualifiedTableIdentifier 'CURSOR' OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
     if (!$6) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | '<impala>COMPUTE' '<impala>INCREMENTAL' '<impala>STATS' SchemaQualifiedTableIdentifier PartitionSpec_EDIT
   {
     parser.addTablePrimary($4);
   }
 ;