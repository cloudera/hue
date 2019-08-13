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
 | DropStatsStatement
 | DropTableStatement
 | DropViewStatement
 | TruncateTableStatement
 ;

DropStatement_EDIT
 : DropDatabaseStatement_EDIT
 | DropFunctionStatement_EDIT
 | DropStatsStatement_EDIT
 | DropTableStatement_EDIT
 | DropViewStatement_EDIT
 | TruncateTableStatement_EDIT
 | 'DROP' 'CURSOR'
   {
     parser.suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']);
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

// OptionalAggregate is no go for look ahead reasons
DropFunctionStatement
 : 'DROP' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedArgumentList
 | 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedArgumentList
 ;

DropFunctionStatement_EDIT
 : 'DROP' 'FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' 'FUNCTION' OptionalIfExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedArgumentList
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' 'FUNCTION' OptionalIfExists_EDIT
 | 'DROP' 'CURSOR' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedArgumentList
   {
     parser.suggestKeywords(['AGGREGATE']);
   }
 | 'DROP' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT
 | 'DROP' 'AGGREGATE' 'CURSOR'
   {
     parser.suggestKeywords(['FUNCTION']);
   }
 | 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedArgumentList
   {
     if (!$4) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists_EDIT
 | 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedArgumentList_EDIT
 | 'DROP' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier_EDIT ParenthesizedArgumentList
 | 'DROP' 'AGGREGATE' 'FUNCTION' OptionalIfExists SchemaQualifiedIdentifier_EDIT ParenthesizedArgumentList
 ;

DropRoleStatement
 : 'DROP' 'ROLE' RegularIdentifier
 ;

DropStatsStatement
 : 'DROP' 'STATS' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 | 'DROP' 'INCREMENTAL' 'STATS' SchemaQualifiedTableIdentifier PartitionSpec
   {
     parser.addTablePrimary($4);
   }
 ;

DropStatsStatement_EDIT
 : 'DROP' 'STATS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' 'STATS' SchemaQualifiedTableIdentifier_EDIT
 | 'DROP' 'CURSOR' 'STATS' SchemaQualifiedTableIdentifier
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
 | 'TRUNCATE' 'TABLE' OptionalIfExists_EDIT SchemaQualifiedTableIdentifier
 ;

DeleteStatement
 : 'DELETE' OptionalDeleteTableRef 'FROM' TableReference OptionalWhereClause
 ;

DeleteStatement_EDIT
 : 'DELETE' OptionalDeleteTableRef 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
     if (!$2) {
       parser.suggestTables();
       parser.suggestDatabases({ appendDot: true });
     }
   }
 | 'DELETE' DeleteTableRef_EDIT
 | 'DELETE' OptionalDeleteTableRef 'FROM' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DELETE' OptionalDeleteTableRef 'FROM' TableReference 'CURSOR' OptionalWhereClause
   {
     var keywords = [{ value: 'FULL JOIN', weight: 1 }, { value: 'FULL OUTER JOIN', weight: 1 }, { value: 'JOIN', weight: 1 }, { value: 'LEFT JOIN', weight: 1 }, { value: 'LEFT OUTER JOIN', weight: 1 }, { value: 'RIGHT JOIN', weight: 1 }, { value: 'RIGHT OUTER JOIN', weight: 1 }, { value: 'INNER JOIN', weight: 1 },  { value: 'LEFT ANTI JOIN', weight: 1 }, { value: 'LEFT SEMI JOIN', weight: 1 }, { value: 'RIGHT ANTI JOIN', weight: 1 }, { value: 'RIGHT SEMI JOIN', weight: 1 }];
     if (!$6) {
       keywords.push({ value: 'WHERE', weight: 3 });
     }
     if ($4.suggestJoinConditions) {
       parser.suggestJoinConditions($4.suggestJoinConditions);
     }
     if ($4.suggestJoins) {
       parser.suggestJoins($4.suggestJoins);
     }
     if ($4.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($4.suggestKeywords, 2));
     }
     if (keywords.length > 0) {
       parser.suggestKeywords(keywords);
     }
   }
 | 'DELETE' DeleteTableRef_EDIT 'FROM'
 | 'DELETE' DeleteTableRef_EDIT 'FROM' TableReference OptionalWhereClause
 | 'DELETE' OptionalDeleteTableRef 'FROM' TableReference_EDIT OptionalWhereClause
 | 'DELETE' OptionalDeleteTableRef 'FROM' TableReference WhereClause_EDIT
 ;

OptionalDeleteTableRef
 :
 | TableReference
 ;

DeleteTableRef_EDIT
 : TableReference_EDIT
 ;

TransactionIdList
 : UnsignedNumericLiteral
 | TransactionIdList ',' UnsignedNumericLiteral
 ;
