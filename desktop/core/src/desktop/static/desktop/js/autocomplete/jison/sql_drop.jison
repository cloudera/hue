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
 | DropFunctionStatement
 | DropRoleStatement
 | DropTableStatement
 | DropIndexStatement
 | DropMacroStatement
 | DropViewStatement
 | TruncateTableStatement
 ;

DropStatement_EDIT
 : DropDatabaseStatement_EDIT
 | DropFunctionStatement_EDIT
 | DropTableStatement_EDIT
 | DropIndexStatement_EDIT
 | DropMacroStatement_EDIT
 | DropViewStatement_EDIT
 | TruncateTableStatement_EDIT
 | 'DROP' 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['DATABASE', 'FUNCTION', 'INDEX', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']);
     } else {
       suggestKeywords(['ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   }
 ;

DropDatabaseStatement
 : 'DROP' DatabaseOrSchema OptionalIfExists RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict
 ;

DropDatabaseStatement_EDIT
 : 'DROP' DatabaseOrSchema OptionalIfExists
 | 'DROP' DatabaseOrSchema OptionalIfExists_EDIT
 | 'DROP' DatabaseOrSchema OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases();
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists RegularOrBacktickedIdentifier 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists_EDIT RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict
 | 'DROP' DatabaseOrSchema OptionalIfExists 'CURSOR' RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
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
 : 'DROP' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList
 ;

DropImpalaFunction_EDIT
 : 'DROP' '<impala>FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases({ appendDot: true });
   }
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$4) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases({ appendDot: true });
   }
 | 'DROP' '<impala>FUNCTION' OptionalIfExists 'CURSOR' SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<impala>FUNCTION' OptionalIfExists_EDIT
 | 'DROP' 'CURSOR' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList
   {
     suggestKeywords(['AGGREGATE']);
   }
 | 'DROP' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList_EDIT
 | 'DROP' '<impala>AGGREGATE' 'CURSOR'
   {
     suggestKeywords(['FUNCTION']);
   }
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists 'CURSOR' SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList
   {
     if (!$4) {
       suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists_EDIT
 | 'DROP' '<impala>AGGREGATE' '<impala>FUNCTION' OptionalIfExists SchemaQualifiedTableIdentifier ParenthesizedImpalaArgumentList_EDIT
 ;

DropHiveFunction
 : 'DROP' '<hive>FUNCTION' OptionalIfExists SchemaQualifiedTableIdentifier
 ;

DropHiveFunction_EDIT
 : 'DROP' '<hive>FUNCTION' OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<hive>FUNCTION' OptionalIfExists 'CURSOR' SchemaQualifiedTableIdentifier
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<hive>FUNCTION' OptionalIfExists_EDIT
 | 'DROP' '<hive>FUNCTION' OptionalIfExists_EDIT SchemaQualifiedTableIdentifier
 ;

DropRoleStatement
 : 'DROP' AnyRole RegularIdentifier
 ;

DropTableStatement
 : 'DROP' AnyTable OptionalIfExists SchemaQualifiedTableIdentifier
   {
     addTablePrimary($4);
   }
 ;

DropTableStatement_EDIT
 : 'DROP' AnyTable OptionalIfExists_EDIT
 | 'DROP' AnyTable OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestTables({ onlyTables: true });
     suggestDatabases({
       appendDot: true
     });
   }
 | 'DROP' AnyTable OptionalIfExists SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyTables = true;
     }
   }
 | 'DROP' AnyTable OptionalIfExists_EDIT SchemaQualifiedTableIdentifier
 | 'DROP' AnyTable OptionalIfExists SchemaQualifiedTableIdentifier 'CURSOR'
   {
     addTablePrimary($4);
     if (isHive()) {
       suggestKeywords(['PURGE']);
     }
   }
 ;

DropIndexStatement
 : 'DROP' '<hive>INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier
   {
     addTablePrimary($6);
   }
 ;

DropIndexStatement_EDIT
 : 'DROP' '<hive>INDEX' OptionalIfExists 'CURSOR'
   {
     suggestKeywords(['IF EXISTS']);
   }
 | 'DROP' '<hive>INDEX' OptionalIfExists_EDIT
 | 'DROP' '<hive>INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'CURSOR'
   {
     suggestKeywords(['ON']);
   }
 | 'DROP' '<hive>INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | 'DROP' '<hive>INDEX' OptionalIfExists RegularOrBacktickedIdentifier 'ON' SchemaQualifiedTableIdentifier_EDIT
 ;

DropMacroStatement
 : 'DROP' '<hive>TEMPORARY' '<hive>MACRO' OptionalIfExists RegularIdentifier
 ;

DropMacroStatement_EDIT
 : 'DROP' '<hive>TEMPORARY' 'CURSOR'
   {
     suggestKeywords(['MACRO']);
   }
 | 'DROP' '<hive>TEMPORARY' '<hive>MACRO' OptionalIfExists 'CURSOR'
   {
     if (!$4) {
       suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' '<hive>TEMPORARY' '<hive>MACRO' OptionalIfExists_EDIT
 ;

DropViewStatement
 : 'DROP' AnyView OptionalIfExists SchemaQualifiedTableIdentifier
   {
     addTablePrimary($4);
   }
 ;

DropViewStatement_EDIT
 : 'DROP' AnyView OptionalIfExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestTables({ onlyViews: true });
     suggestDatabases({ appendDot: true });
   }
 | 'DROP' AnyView OptionalIfExists 'CURSOR' SchemaQualifiedTableIdentifier
   {
     addTablePrimary($5);
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
   }
 | 'DROP' AnyView OptionalIfExists_EDIT
 | 'DROP' AnyView OptionalIfExists_EDIT SchemaQualifiedTableIdentifier
   {
     addTablePrimary($4);
   }
 | 'DROP' AnyView OptionalIfExists SchemaQualifiedTableIdentifier_EDIT
   {
     if (parser.yy.result.suggestTables) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 ;

TruncateTableStatement
 : 'TRUNCATE' AnyTable SchemaQualifiedTableIdentifier OptionalPartitionSpec
   {
     addTablePrimary($3);
   }
 ;

TruncateTableStatement_EDIT
 : 'TRUNCATE' 'CURSOR'
   {
     suggestKeywords(['TABLE']);
   }
 | 'TRUNCATE' AnyTable 'CURSOR' OptionalPartitionSpec
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | 'TRUNCATE' AnyTable SchemaQualifiedTableIdentifier_EDIT OptionalPartitionSpec
 | 'TRUNCATE' AnyTable SchemaQualifiedTableIdentifier OptionalPartitionSpec 'CURSOR'
   {
     addTablePrimary($3);
     if (isHive() && !$4) {
       suggestKeywords(['PARTITION']);
     }
   }
 | 'TRUNCATE' AnyTable SchemaQualifiedTableIdentifier OptionalPartitionSpec_EDIT
   {
     addTablePrimary($3);
   }
 ;