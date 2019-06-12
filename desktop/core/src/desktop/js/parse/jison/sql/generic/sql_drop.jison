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
 : DropStatement
 ;

DataDefinition_EDIT
 : DropStatement_EDIT
 ;

DropStatement
 : DropDatabaseStatement
 | DropRoleStatement
 | DropTableStatement
 | DropViewStatement
 | TruncateTableStatement
 ;

DropStatement_EDIT
 : DropDatabaseStatement_EDIT
 | DropTableStatement_EDIT
 | DropViewStatement_EDIT
 | TruncateTableStatement_EDIT
 | 'DROP' 'CURSOR'
   {
     parser.suggestKeywords(['DATABASE', 'ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
   }
 ;

DropDatabaseStatement
 : 'DROP' DatabaseOrSchema OptionalIfExists RegularOrBacktickedIdentifier OptionalCascade
 ;

DropDatabaseStatement_EDIT
 : 'DROP' DatabaseOrSchema OptionalIfExists
 | 'DROP' DatabaseOrSchema OptionalIfExists_EDIT
 | 'DROP' DatabaseOrSchema OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestDatabases();
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['CASCADE']);
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists_EDIT RegularOrBacktickedIdentifier OptionalCascade
 | 'DROP' DatabaseOrSchema OptionalIfExists 'CURSOR' RegularOrBacktickedIdentifier OptionalCascade
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 ;
DropRoleStatement
 : 'DROP' 'ROLE' RegularIdentifier
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

DropViewStatement
 : 'DROP' 'VIEW' OptionalIfExists SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
   }
 ;

DropViewStatement_EDIT
 : 'DROP' 'VIEW' OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestTables({ onlyViews: true });
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' 'VIEW' OptionalIfExists 'CURSOR' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($5);
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' 'VIEW' OptionalIfExists_EDIT
 | 'DROP' 'VIEW' OptionalIfExists_EDIT SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
   }
 | 'DROP' 'VIEW' OptionalIfExists SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 ;

TruncateTableStatement
 : 'TRUNCATE' 'TABLE' OptionalIfExists SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
   }
 ;

TruncateTableStatement_EDIT
 : 'TRUNCATE' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'TRUNCATE' 'TABLE' OptionalIfExists 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'TRUNCATE' 'TABLE' OptionalIfExists_EDIT
 | 'TRUNCATE' 'TABLE' OptionalIfExists SchemaQualifiedTableIdentifier_EDIT
 | 'TRUNCATE' 'TABLE' OptionalIfExists SchemaQualifiedTableIdentifier 'CURSOR'
   {
     parser.addTablePrimary($4);
   }
 | 'TRUNCATE' 'TABLE' OptionalIfExists 'CURSOR' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'TRUNCATE' 'TABLE' OptionalIfExists_EDIT SchemaQualifiedTableIdentifier OptionalPartitionSpec
 ;
