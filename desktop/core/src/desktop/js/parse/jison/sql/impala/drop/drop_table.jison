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
 : DropTableStatement
 ;

DataDefinition_EDIT
 : DropTableStatement_EDIT
 ;

DropTableStatement
 : 'DROP' 'TABLE' OptionalIfExists SchemaQualifiedTableIdentifier OptionalPurge
   {
     parser.addTablePrimary($4);
   }
 ;

DropTableStatement_EDIT
 : 'DROP' 'TABLE' OptionalIfExists_EDIT
 | 'DROP' 'TABLE' OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestTables({ onlyTables: true });
     parser.suggestDatabases({
       appendDot: true
     });
   }
 | 'DROP' 'TABLE' OptionalIfExists SchemaQualifiedTableIdentifier_EDIT OptionalPurge
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyTables = true;
     }
   }
 | 'DROP' 'TABLE' OptionalIfExists_EDIT SchemaQualifiedTableIdentifier OptionalPurge
 | 'DROP' 'TABLE' OptionalIfExists SchemaQualifiedTableIdentifier OptionalPurge 'CURSOR'
   {
     parser.addTablePrimary($4);
     if (!$5) {
       parser.suggestKeywords(['PURGE']);
     }
   }
 ;

OptionalPurge
 :
 | 'PURGE'
 ;
