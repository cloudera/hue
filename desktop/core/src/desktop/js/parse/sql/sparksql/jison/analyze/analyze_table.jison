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

Auxiliary
 : AnalyzeTable
 ;

Auxiliary_EDIT
 : AnalyzeTable_EDIT
 ;

AnalyzeTable
 : 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'STATISTICS' OptionalAnalyzeTableComputeOptions
   {
     parser.addTablePrimary($3);
   }
 ;

AnalyzeTable_EDIT
 : 'ANALYZE' 'TABLE' 'CURSOR'
   {
     parser.suggestDatabases({ appendDot: true });
     parser.suggestTables();
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier_EDIT
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords([{ value: 'PARTITION', weight: 2 }, { value: 'COMPUTE STATISTICS', weight: 1 }]);
     } else {
       parser.suggestKeywords(['COMPUTE STATISTICS']);
     }
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier PartitionSpec_EDIT
   {
     parser.addTablePrimary($3);
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'CURSOR'
   {
     parser.suggestKeywords(['STATISTICS']);
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'STATISTICS' OptionalAnalyzeTableComputeOptions 'CURSOR'
   {
     if (!$7) {
       parser.suggestKeywords(['FOR ALL COLUMNS', 'FOR COLUMNS', 'NOSCAN']);
     }
   }
 | 'ANALYZE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'COMPUTE' 'STATISTICS' AnalyzeTableComputeOptions_EDIT
   {
     parser.addTablePrimary($3);
   }
 ;

OptionalAnalyzeTableComputeOptions
 :
 | AnalyzeTableComputeOptions
 ;

AnalyzeTableComputeOptions
 : 'FOR' 'ALL' 'COLUMNS'
 | 'FOR' 'COLUMNS' ColumnList
 | 'NOSCAN'
 ;

AnalyzeTableComputeOptions_EDIT
 : 'FOR' 'CURSOR'
   {
     parser.suggestKeywords(['ALL COLUMNS', 'COLUMNS']);
   }
 | 'FOR' 'ALL' 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS']);
   }
 | 'FOR' 'COLUMNS' 'CURSOR'
   {
     parser.suggestColumns();
   }
 | 'FOR' 'COLUMNS' ColumnList_EDIT
 ;
