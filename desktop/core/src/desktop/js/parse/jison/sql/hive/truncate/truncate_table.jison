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
 : TruncateTableStatement
 ;

DataDefinition_EDIT
 : TruncateTableStatement_EDIT
 ;

TruncateTableStatement
 : 'TRUNCATE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($3);
   }
 ;

TruncateTableStatement_EDIT
 : 'TRUNCATE' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'TRUNCATE' 'TABLE' 'CURSOR' OptionalPartitionSpec
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'TRUNCATE' 'TABLE' SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | 'TRUNCATE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($3);
     if (!$4) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'TRUNCATE' 'TABLE' SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT
   {
     parser.addTablePrimary($3);
   }
 | 'TRUNCATE' 'TABLE' 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
   }
 ;
