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
 : AlterStatement
 ;

DataDefinition_EDIT
 : AlterStatement_EDIT
 ;

AlterStatement
 : AlterDatabase
 | AlterTable
 | AlterView
 ;

AlterStatement_EDIT
 : AlterDatabase_EDIT
 | AlterTable_EDIT
 | AlterView_EDIT
 | 'ALTER' 'CURSOR'
   {
     parser.suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE', 'VIEW']);
   }
 ;

AlterDatabase
 ;

AlterDatabase_EDIT
 ;

AlterTable
 : AlterTableLeftSide OptionalPartitionOperations
 | AlterTableLeftSide PartitionSpec OptionalPartitionOperations
 ;

AlterTable_EDIT
 : AlterTableLeftSide_EDIT
 | AlterTableLeftSide_EDIT OptionalPartitionOperations
 | AlterTableLeftSide_EDIT PartitionSpec OptionalPartitionOperations
 | AlterTableLeftSide OptionalPartitionOperations_EDIT
 | AlterTableLeftSide 'CURSOR'
 | AlterTableLeftSide PartitionSpec 'CURSOR'
 | AlterTableLeftSide PartitionSpec 'SET' 'CURSOR'
 | AlterTableLeftSide 'SET' 'CURSOR'
 | AlterTableLeftSide PartitionSpec OptionalPartitionOperations_EDIT
 ;

AlterTableLeftSide
 : 'ALTER' 'TABLE' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 ;

AlterTableLeftSide_EDIT
 : 'ALTER' 'TABLE' SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyTables = true;
     }
   }
 | 'ALTER' 'TABLE' 'CURSOR'
   {
     parser.suggestTables({ onlyTables: true });
     parser.suggestDatabases({ appendDot: true });
   }
 ;

AlterView
 | AlterViewLeftSide 'AS' QuerySpecification
 ;

AlterView_EDIT
 : AlterViewLeftSide_EDIT
 | AlterViewLeftSide 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | AlterViewLeftSide 'SET' 'CURSOR'
 | AlterViewLeftSide 'AS' 'CURSOR'
   {
     parser.suggestKeywords(['SELECT']);
   }
 | AlterViewLeftSide 'AS' QuerySpecification_EDIT
 ;


AlterViewLeftSide
 : 'ALTER' 'VIEW' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 ;

AlterViewLeftSide_EDIT
 : 'ALTER' 'VIEW' SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 | 'ALTER' 'VIEW' 'CURSOR'
   {
     parser.suggestTables({ onlyViews: true });
     parser.suggestDatabases({ appendDot: true });
   }
 ;
