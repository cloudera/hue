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
 | AbortStatement
 ;

DataDefinition_EDIT
 : DropStatement_EDIT
 | AbortStatement_EDIT
 ;

DataManipulation
 : DeleteStatement
 ;

DataManipulation_EDIT
 : DeleteStatement_EDIT
 ;

DropStatement
 : DropDatabaseStatement
 | DropFunctionStatement
 | DropRoleStatement
 | DropTableStatement
 | DropIndexStatement
 | DropMacroStatement
 | DropMaterializedViewStatement
 | DropViewStatement
 | TruncateTableStatement
 ;

DropStatement_EDIT
 : DropDatabaseStatement_EDIT
 | DropFunctionStatement_EDIT
 | DropTableStatement_EDIT
 | DropIndexStatement_EDIT
 | DropMacroStatement_EDIT
 | DropMaterializedViewStatement_EDIT
 | DropViewStatement_EDIT
 | TruncateTableStatement_EDIT
 | 'DROP' 'CURSOR'
   {
     parser.suggestKeywords(['DATABASE', 'FUNCTION', 'INDEX', 'MATERIALIZED VIEW', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']);
   }
 ;

DropDatabaseStatement
 : 'DROP' DatabaseOrSchema OptionalIfExists RegularOrBacktickedIdentifier OptionalCascadeOrRestrict
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
     parser.suggestKeywords(['CASCADE', 'RESTRICT']);
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists_EDIT RegularOrBacktickedIdentifier OptionalCascadeOrRestrict
 | 'DROP' DatabaseOrSchema OptionalIfExists 'CURSOR' RegularOrBacktickedIdentifier OptionalCascadeOrRestrict
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 ;

DropFunctionStatement
 : 'DROP' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier
 | 'DROP' 'TEMPORARY' 'FUNCTION' OptionalIfExists RegularIdentifier
 ;

DropFunctionStatement_EDIT
 : 'DROP' 'FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' 'FUNCTION' OptionalIfExists 'CURSOR' SchemaQualifiedIdentifier
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' 'FUNCTION' OptionalIfExists_EDIT
 | 'DROP' 'FUNCTION' OptionalIfExists_EDIT SchemaQualifiedIdentifier
 | 'DROP' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier_EDIT
 | 'DROP' 'TEMPORARY' 'FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' 'TEMPORARY' 'FUNCTION' OptionalIfExists_EDIT
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

DropIndexStatement
 : 'DROP' 'INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($6);
   }
 ;

DropIndexStatement_EDIT
 : 'DROP' 'INDEX' OptionalIfExists 'CURSOR'
   {
     parser.suggestKeywords(['IF EXISTS']);
   }
 | 'DROP' 'INDEX' OptionalIfExists_EDIT
 | 'DROP' 'INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | 'DROP' 'INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' 'INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier_EDIT
 ;

DropMacroStatement
 : 'DROP' 'TEMPORARY' 'MACRO' OptionalIfExists RegularIdentifier
 ;

DropMacroStatement_EDIT
 : 'DROP' 'TEMPORARY' 'CURSOR'
   {
     parser.suggestKeywords(['FUNCTION', 'MACRO']);
   }
 | 'DROP' 'TEMPORARY' 'MACRO' OptionalIfExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' 'TEMPORARY' 'MACRO' OptionalIfExists_EDIT
 ;


DropMaterializedViewStatement
 : 'DROP' 'MATERIALIZED' 'VIEW' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
   }
 ;

DropMaterializedViewStatement_EDIT
 : 'DROP' 'MATERIALIZED' 'CURSOR'
   {
     parser.suggestKeywords(['VIEW']);
   }
 | 'DROP' 'MATERIALIZED' 'VIEW' 'CURSOR'
   {
     parser.suggestTables({ onlyViews: true });
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' 'MATERIALIZED' VIEW SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
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

DeleteStatement
 : 'DELETE' 'FROM' SchemaQualifiedTableIdentifier OptionalWhereClause
   {
     parser.addTablePrimary($3);
   }
 ;

DeleteStatement_EDIT
 : 'DELETE' 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 | 'DELETE' 'FROM' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DELETE' 'FROM' SchemaQualifiedTableIdentifier 'CURSOR' OptionalWhereClause
   {
     parser.addTablePrimary($3);
     if (!$5) {
       parser.suggestKeywords(['WHERE']);
     }
   }
 | 'DELETE' 'FROM' SchemaQualifiedTableIdentifier_EDIT OptionalWhereClause
 | 'DELETE' 'FROM' SchemaQualifiedTableIdentifier WhereClause_EDIT
   {
     parser.addTablePrimary($3);
   }
 ;

AbortStatement
 : 'ABORT' 'TRANSACTIONS' TransactionIdList
 ;

AbortStatement_EDIT
 : 'ABORT' 'CURSOR'
   {
     parser.suggestKeywords(['TRANSACTIONS']);
   }
 ;

TransactionIdList
 : UnsignedNumericLiteral
 | TransactionIdList ',' UnsignedNumericLiteral
 ;
