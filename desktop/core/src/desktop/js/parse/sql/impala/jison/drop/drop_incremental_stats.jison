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
 : DropIncrementalStatsStatement
 ;

DataDefinition_EDIT
 : DropIncrementalStatsStatement_EDIT
 ;

DropIncrementalStatsStatement
 : 'DROP' 'INCREMENTAL' 'STATS' SchemaQualifiedTableIdentifier PartitionSpec
   {
     parser.addTablePrimary($4);
   }
 ;

DropIncrementalStatsStatement_EDIT
 : 'DROP' 'CURSOR' 'STATS' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['INCREMENTAL']);
   }
 | 'DROP' 'CURSOR' 'STATS' SchemaQualifiedTableIdentifier PartitionSpec
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['INCREMENTAL']);
   }
 | 'DROP' 'INCREMENTAL' 'CURSOR'
   {
     parser.suggestKeywords(['STATS']);
   }
 | 'DROP' 'INCREMENTAL' 'STATS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' 'INCREMENTAL' 'STATS' SchemaQualifiedTableIdentifier_EDIT
 | 'DROP' 'INCREMENTAL' 'STATS' SchemaQualifiedTableIdentifier_EDIT PartitionSpec
 | 'DROP' 'INCREMENTAL' 'STATS' SchemaQualifiedTableIdentifier 'CURSOR'
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['PARTITION']);
   }
 | 'DROP' 'INCREMENTAL' 'STATS' SchemaQualifiedTableIdentifier PartitionSpec_EDIT
   {
     parser.addTablePrimary($4);
   }
 ;
