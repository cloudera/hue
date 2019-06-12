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
 ;

DataDefinition_EDIT
 : AnalyzeStatement_EDIT
 ;

AnalyzeStatement
 : 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'STATISTICS' OptionalForColumns OptionalCacheMetadata OptionalNoscan
   {
     parser.addTablePrimary($3);
   }
 ;

AnalyzeStatement_EDIT
 : 'ANALYZE' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'ANALYZE' 'TABLE' 'CURSOR'
   {
     parser.suggestTables({ onlyTables: true });
     parser.suggestDatabases({ appendDot: true });
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyTables = true;
     }
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT
   {
     parser.addTablePrimary($3);
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($3);
     if (!$4) {
       parser.suggestKeywords([{ value: 'PARTITION', weight: 2 }, { value: 'COMPUTE STATISTICS', weight: 1 }]);
     } else {
       parser.suggestKeywords(['COMPUTE STATISTICS']);
     }
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'CURSOR'
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['STATISTICS']);
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'STATISTICS' 'CURSOR' OptionalForColumns OptionalCacheMetadata OptionalNoscan
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(parser.getKeywordsForOptionalsLR([$8, $9, $10], [{ value: 'FOR COLUMNS', weight: 3 }, { value: 'CACHE METADATA', weight: 2 }, { value: 'NOSCAN', weight: 1 }]));
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'STATISTICS' ForColumns 'CURSOR' OptionalCacheMetadata OptionalNoscan
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(parser.getKeywordsForOptionalsLR([$9, $10], [{ value: 'CACHE METADATA', weight: 2 }, { value: 'NOSCAN', weight: 1 }]));
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'STATISTICS' OptionalForColumns CacheMetadata 'CURSOR' OptionalNoscan
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(parser.getKeywordsForOptionalsLR([$10], [{ value: 'NOSCAN', weight: 1 }]));
   }
 | 'ANALYZE' 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.suggestKeywords(['TABLE']);
     parser.addTablePrimary($3);
   }
 | 'ANALYZE' 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'STATISTICS' OptionalForColumns OptionalCacheMetadata OptionalNoscan
   {
     parser.suggestKeywords(['TABLE']);
     parser.addTablePrimary($3);
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec 'COMPUTE' 'STATISTICS' OptionalForColumns OptionalCacheMetadata OptionalNoscan
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT 'COMPUTE' 'STATISTICS' OptionalForColumns OptionalCacheMetadata OptionalNoscan
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'STATISTICS' ForColumns_EDIT OptionalCacheMetadata OptionalNoscan
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'STATISTICS' OptionalForColumns CacheMetadata_EDIT OptionalNoscan
 ;

OptionalForColumns
 :
 | ForColumns
 ;

ForColumns
 : 'FOR' 'COLUMNS'
 ;

ForColumns_EDIT
 : 'FOR' 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS']);
   }
 ;

OptionalCacheMetadata
 :
 | CacheMetadata
 ;

CacheMetadata
 : 'CACHE' 'METADATA'
 ;

CacheMetadata_EDIT
 : 'CACHE' 'CURSOR'
   {
     parser.suggestKeywords(['METADATA']);
   }
 ;

OptionalNoscan
 :
 | 'NOSCAN'
 ;
