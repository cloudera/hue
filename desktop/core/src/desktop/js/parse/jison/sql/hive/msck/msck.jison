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
 : Msck
 ;

DataDefinition_EDIT
 : Msck_EDIT
 ;

Msck
 : 'MSCK' OptionalRepair 'TABLE' SchemaQualifiedTableIdentifier OptionalAddDropSyncPartitions
   {
     parser.addTablePrimary($4);
   }
 ;

Msck_EDIT
 : 'MSCK' OptionalRepair 'CURSOR'
   {
     if (!$2) {
       parser.suggestKeywords(['TABLE', 'REPAIR TABLE']);
     } else {
       parser.suggestKeywords(['TABLE']);
     }
   }
 | 'MSCK' OptionalRepair 'TABLE' 'CURSOR'
   {
     parser.suggestTables({ onlyTables: true });
     parser.suggestDatabases({ appendDot: true });
   }
 | 'MSCK' OptionalRepair 'TABLE' SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 | 'MSCK' OptionalRepair 'TABLE' SchemaQualifiedTableIdentifier AddDropSyncPartitions_EDIT
   {
     parser.addTablePrimary($4);
   }
 | 'MSCK' OptionalRepair 'TABLE' SchemaQualifiedTableIdentifier OptionalAddDropSyncPartitions 'CURSOR'
   {
     parser.addTablePrimary($4);
     if (!$5) {
       parser.suggestKeywords(['ADD PARTITIONS', 'DROP PARTITIONS', 'SYNC PARTITIONS']);
     }
   }
 ;

OptionalRepair
 :
 | 'REPAIR'
 ;

OptionalAddDropSyncPartitions
 :
 | AddDropOrSync 'PARTITIONS'
 ;

AddDropSyncPartitions_EDIT
 : AddDropOrSync 'CURSOR'
   {
     parser.suggestKeywords(['PARTITIONS']);
   }
 ;

AddDropOrSync
 : 'ADD'
 | 'DROP'
 | 'SYNC'
 ;
