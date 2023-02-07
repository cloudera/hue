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
 : UncacheTable
 ;

Auxiliary_EDIT
 : UncacheTable_EDIT
 ;

UncacheTable
 : 'UNCACHE' 'TABLE' OptionalIfExists SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
   }
 ;

UncacheTable_EDIT
 : 'UNCACHE' 'TABLE' OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
     parser.suggestTables();
   }
 | 'UNCACHE' 'TABLE' IfExists_EDIT
 | 'UNCACHE' 'TABLE' OptionalIfExists SchemaQualifiedTableIdentifier_EDIT
 | 'UNCACHE' 'TABLE' IfExists_EDIT SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
   }
 ;