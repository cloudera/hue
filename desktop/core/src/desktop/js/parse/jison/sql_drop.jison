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
 | HiveAbortStatement
 ;

DataDefinition_EDIT
 : DropStatement_EDIT
 | HiveAbortStatement_EDIT
 ;

DataManipulation
 : HiveDeleteStatement
 | ImpalaDeleteStatement
 ;

DataManipulation_EDIT
 : HiveDeleteStatement_EDIT
 | ImpalaDeleteStatement_EDIT
 ;

DropStatement
 : DropDatabaseStatement
 | DropFunctionStatement
 | DropRoleStatement
 | DropStatsStatement
 | DropTableStatement
 | DropIndexStatement
 | DropMacroStatement
 | DropViewStatement
 | TruncateTableStatement
 ;

DropStatement_EDIT
 : DropDatabaseStatement_EDIT
 | DropFunctionStatement_EDIT
 | DropStatsStatement_EDIT
 | DropTableStatement_EDIT
 | DropIndexStatement_EDIT
 | DropMacroStatement_EDIT
 | DropViewStatement_EDIT
 | TruncateTableStatement_EDIT
 | 'DROP' 'CURSOR'
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['DATABASE', 'FUNCTION', 'INDEX', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']);
     } else {
       parser.suggestKeywords(['ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
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
     if (parser.isHive() || parser.isImpala()) {
       parser.suggestKeywords(['CASCADE', 'RESTRICT']);
     }
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
 : DropImpalaFunction
 | DropHiveFunction
 ;

DropFunctionStatement_EDIT
 : DropImpalaFunction_EDIT
 | DropHiveFunction_EDIT
 ;

// OptionalAggregate is no go for look ahead reasons
DropImpalaFunction
 : 'DROP' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList
 ;

DropImpalaFunction_EDIT
 : 'DROP' '<impala>FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' '<impala>FUNCTION' OptionalIfExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<impala>FUNCTION' OptionalIfExists_EDIT
 | 'DROP' 'CURSOR' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList
   {
     parser.suggestKeywords(['AGGREGATE']);
   }
 | 'DROP' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList_EDIT
 | 'DROP' '<impala>AGGREGATE' 'CURSOR'
   {
     parser.suggestKeywords(['FUNCTION']);
   }
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists 'CURSOR' SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList
   {
     if (!$4) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists_EDIT
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedIdentifier ParenthesizedImpalaArgumentList_EDIT
 | 'DROP' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedIdentifier_EDIT ParenthesizedImpalaArgumentList
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedIdentifier_EDIT ParenthesizedImpalaArgumentList
 ;

DropHiveFunction
 : 'DROP' '<hive>FUNCTION' OptionalIfExists SchemaQualifiedIdentifier
 | 'DROP' '<hive>TEMPORARY' '<hive>FUNCTION' OptionalIfExists RegularIdentifier
 ;

DropHiveFunction_EDIT
 : 'DROP' '<hive>FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<hive>FUNCTION' OptionalIfExists 'CURSOR' SchemaQualifiedIdentifier
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<hive>FUNCTION' OptionalIfExists_EDIT
 | 'DROP' '<hive>FUNCTION' OptionalIfExists_EDIT SchemaQualifiedIdentifier
 | 'DROP' '<hive>FUNCTION' OptionalIfExists SchemaQualifiedIdentifier_EDIT
 | 'DROP' '<hive>TEMPORARY' '<hive>FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<hive>TEMPORARY' '<hive>FUNCTION' OptionalIfExists_EDIT
 ;

DropRoleStatement
 : 'DROP' AnyRole RegularIdentifier
 ;

DropStatsStatement
 : 'DROP' '<impala>STATS' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($3);
   }
 | 'DROP' '<impala>INCREMENTAL' '<impala>STATS' SchemaQualifiedTableIdentifier PartitionSpec
   {
     parser.addTablePrimary($4);
   }
 ;

DropStatsStatement_EDIT
 : 'DROP' '<impala>STATS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' '<impala>STATS' SchemaQualifiedTableIdentifier_EDIT
 | 'DROP' 'CURSOR' '<impala>STATS' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['INCREMENTAL']);
   }
 | 'DROP' 'CURSOR' '<impala>STATS' SchemaQualifiedTableIdentifier PartitionSpec
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['INCREMENTAL']);
   }
 | 'DROP' '<impala>INCREMENTAL' 'CURSOR'
   {
     parser.suggestKeywords(['STATS']);
   }
 | 'DROP' '<impala>INCREMENTAL' '<impala>STATS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' '<impala>INCREMENTAL' '<impala>STATS' SchemaQualifiedTableIdentifier_EDIT
 | 'DROP' '<impala>INCREMENTAL' '<impala>STATS' SchemaQualifiedTableIdentifier_EDIT PartitionSpec
 | 'DROP' '<impala>INCREMENTAL' '<impala>STATS' SchemaQualifiedTableIdentifier 'CURSOR'
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['PARTITION']);
   }
 | 'DROP' '<impala>INCREMENTAL' '<impala>STATS' SchemaQualifiedTableIdentifier PartitionSpec_EDIT
   {
     parser.addTablePrimary($4);
   }
 ;

DropTableStatement
 : 'DROP' AnyTable OptionalIfExists SchemaQualifiedTableIdentifier OptionalPurge
   {
     parser.addTablePrimary($4);
   }
 ;

DropTableStatement_EDIT
 : 'DROP' AnyTable OptionalIfExists_EDIT
 | 'DROP' AnyTable OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestTables({ onlyTables: true });
     parser.suggestDatabases({
       appendDot: true
     });
   }
 | 'DROP' AnyTable OptionalIfExists SchemaQualifiedTableIdentifier_EDIT OptionalPurge
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyTables = true;
     }
   }
 | 'DROP' AnyTable OptionalIfExists_EDIT SchemaQualifiedTableIdentifier OptionalPurge
 | 'DROP' AnyTable OptionalIfExists SchemaQualifiedTableIdentifier OptionalPurge 'CURSOR'
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
 | '<hive>PURGE'
 ;


DropIndexStatement
 : 'DROP' '<hive>INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($6);
   }
 ;

DropIndexStatement_EDIT
 : 'DROP' '<hive>INDEX' OptionalIfExists 'CURSOR'
   {
     parser.suggestKeywords(['IF EXISTS']);
   }
 | 'DROP' '<hive>INDEX' OptionalIfExists_EDIT
 | 'DROP' '<hive>INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | 'DROP' '<hive>INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' '<hive>INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier_EDIT
 ;

DropMacroStatement
 : 'DROP' '<hive>TEMPORARY' '<hive>MACRO' OptionalIfExists RegularIdentifier
 ;

DropMacroStatement_EDIT
 : 'DROP' '<hive>TEMPORARY' 'CURSOR'
   {
     parser.suggestKeywords(['FUNCTION', 'MACRO']);
   }
 | 'DROP' '<hive>TEMPORARY' '<hive>MACRO' OptionalIfExists 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<hive>TEMPORARY' '<hive>MACRO' OptionalIfExists_EDIT
 ;

DropViewStatement
 : 'DROP' AnyView OptionalIfExists SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
   }
 ;

DropViewStatement_EDIT
 : 'DROP' AnyView OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
     parser.suggestTables({ onlyViews: true });
     parser.suggestDatabases({ appendDot: true });
   }
 | 'DROP' AnyView OptionalIfExists 'CURSOR' SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($5);
     if (!$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' AnyView OptionalIfExists_EDIT
 | 'DROP' AnyView OptionalIfExists_EDIT SchemaQualifiedTableIdentifier
   {
     parser.addTablePrimary($4);
   }
 | 'DROP' AnyView OptionalIfExists SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 ;

TruncateTableStatement
 : 'TRUNCATE' AnyTable OptionalIfExists SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
   }
 ;

TruncateTableStatement_EDIT
 : 'TRUNCATE' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'TRUNCATE' AnyTable OptionalIfExists 'CURSOR' OptionalPartitionSpec
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
     if (parser.isImpala() && !$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'TRUNCATE' AnyTable OptionalIfExists_EDIT OptionalPartitionSpec
 | 'TRUNCATE' AnyTable OptionalIfExists SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | 'TRUNCATE' AnyTable OptionalIfExists SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($4);
     if (parser.isHive() && !$5) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'TRUNCATE' AnyTable OptionalIfExists SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT
   {
     parser.addTablePrimary($4);
   }
 | 'TRUNCATE' AnyTable OptionalIfExists 'CURSOR' SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
     if (parser.isImpala() && !$3) {
       parser.suggestKeywords(['IF EXISTS']);
     }
   }
 | 'TRUNCATE' AnyTable OptionalIfExists_EDIT SchemaQualifiedTableIdentifier OptionalPartitionSpec
 ;

HiveDeleteStatement
 : '<hive>DELETE' 'FROM' SchemaQualifiedTableIdentifier OptionalWhereClause
   {
     parser.addTablePrimary($3);
   }
 ;

HiveDeleteStatement_EDIT
 : '<hive>DELETE' 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
   }
 | '<hive>DELETE' 'FROM' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | '<hive>DELETE' 'FROM' SchemaQualifiedTableIdentifier 'CURSOR' OptionalWhereClause
   {
     parser.addTablePrimary($3);
     if (!$5) {
       parser.suggestKeywords(['WHERE']);
     }
   }
 | '<hive>DELETE' 'FROM' SchemaQualifiedTableIdentifier_EDIT OptionalWhereClause
 | '<hive>DELETE' 'FROM' SchemaQualifiedTableIdentifier WhereClause_EDIT
   {
     parser.addTablePrimary($3);
   }
 ;

ImpalaDeleteStatement
 : '<impala>DELETE' OptionalImpalaDeleteTableRef 'FROM' TableReference OptionalWhereClause
 ;

ImpalaDeleteStatement_EDIT
 : '<impala>DELETE' OptionalImpalaDeleteTableRef 'CURSOR'
   {
     parser.suggestKeywords(['FROM']);
     if (parser.isImpala() && !$2) {
       parser.suggestTables();
       parser.suggestDatabases({ appendDot: true });
     }
   }
 | '<impala>DELETE' ImpalaDeleteTableRef_EDIT
 | '<impala>DELETE' OptionalImpalaDeleteTableRef 'FROM' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ appendDot: true });
   }
 | '<impala>DELETE' OptionalImpalaDeleteTableRef 'FROM' TableReference 'CURSOR' OptionalWhereClause
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
 | '<impala>DELETE' ImpalaDeleteTableRef_EDIT 'FROM'
 | '<impala>DELETE' ImpalaDeleteTableRef_EDIT 'FROM' TableReference OptionalWhereClause
 | '<impala>DELETE' OptionalImpalaDeleteTableRef 'FROM' TableReference_EDIT OptionalWhereClause
 | '<impala>DELETE' OptionalImpalaDeleteTableRef 'FROM' TableReference WhereClause_EDIT
 ;

OptionalImpalaDeleteTableRef
 :
 | TableReference
 ;

ImpalaDeleteTableRef_EDIT
 : TableReference_EDIT
 ;

HiveAbortStatement
 : '<hive>ABORT' '<hive>TRANSACTIONS' TransactionIdList
 ;

HiveAbortStatement_EDIT
 : '<hive>ABORT' 'CURSOR'
   {
     parser.suggestKeywords(['TRANSACTIONS']);
   }
 ;

TransactionIdList
 : UnsignedNumericLiteral
 | TransactionIdList ',' UnsignedNumericLiteral
 ;