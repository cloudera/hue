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
 : ShowStatement
 ;

DataDefinition_EDIT
 : ShowStatement_EDIT
 ;

ShowStatement
 : ShowColumnStatsStatement
 | ShowCreateTableStatement
 | ShowCurrentRolesStatement
 | ShowDatabasesStatement
 | ShowFilesStatement
 | ShowFunctionsStatement
 | ShowGrantStatement
 | ShowPartitionsStatement
 | ShowRoleStatement
 | ShowRolesStatement
 | ShowTableStatsStatement
 | ShowTablesStatement
 ;

ShowStatement_EDIT
 : 'SHOW' 'CURSOR'
   {
     parser.suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'COLUMN STATS', 'CREATE TABLE', 'CURRENT ROLES', 'CREATE VIEW', 'DATABASES', 'FILES IN', 'FUNCTIONS', 'GRANT ROLE', 'GRANT USER', 'PARTITIONS', 'RANGE PARTITIONS', 'ROLE GRANT GROUP', 'ROLES', 'SCHEMAS', 'TABLE STATS', 'TABLES']);
   }
 | 'SHOW' 'CURSOR' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['COLUMN STATS', 'CREATE TABLE', 'CREATE VIEW', 'FILES IN', 'PARTITIONS', 'RANGE PARTITIONS', 'TABLE STATS']);
   }
 | 'SHOW' 'CURSOR' 'LIKE' SingleQuotedValue
   {
     parser.suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'DATABASES', 'FUNCTIONS', 'SCHEMAS', 'TABLES']);
   }
 | ShowColumnStatsStatement_EDIT
 | ShowCreateTableStatement_EDIT
 | ShowCurrentRolesStatement_EDIT
 | ShowDatabasesStatement_EDIT
 | ShowFilesStatement_EDIT
 | ShowFunctionsStatement_EDIT
 | ShowGrantStatement_EDIT
 | ShowPartitionsStatement_EDIT
 | ShowRoleStatement_EDIT
 | ShowTableStatsStatement_EDIT
 | ShowTablesStatement_EDIT
 ;

ShowColumnStatsStatement
 : 'SHOW' 'COLUMN' 'STATS' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($4);
   }
 ;

ShowColumnStatsStatement_EDIT
 : 'SHOW' 'COLUMN' 'CURSOR'
   {
     parser.suggestKeywords(['STATS']);
   }
 | 'SHOW' 'COLUMN' 'STATS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' 'COLUMN' 'STATS' RegularOrBackTickedSchemaQualifiedName_EDIT
 ;

ShowCreateTableStatement
 : 'SHOW' 'CREATE' TableOrView RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($4);
   }
 ;

ShowCreateTableStatement_EDIT
 : 'SHOW' 'CREATE' 'CURSOR'
   {
     parser.suggestKeywords(['TABLE', 'VIEW']);
   }
 | 'SHOW' 'CREATE' TableOrView 'CURSOR'
   {
     if ($3.isView) {
       parser.suggestTables({ onlyViews: true });
     } else {
       parser.suggestTables();
     }
     parser.suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' 'CREATE' TableOrView RegularOrBackTickedSchemaQualifiedName_EDIT
   {
     if (parser.yy.result.suggestTables && $3.isView) {
       parser.yy.result.suggestTables.onlyViews = true;
     }
   }
 | 'SHOW' 'CREATE' 'CURSOR' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['TABLE', 'VIEW']);
   }
 ;

TableOrView
 : 'TABLE'
 | 'VIEW'   -> { isView: true }
 ;

ShowCurrentRolesStatement
 : 'SHOW' 'CURRENT' 'ROLES'
 ;

ShowCurrentRolesStatement_EDIT
 : 'SHOW' 'CURRENT' 'CURSOR'
   {
     parser.suggestKeywords([ 'ROLES' ]);
   }
 | 'SHOW' 'CURSOR' 'ROLES'
   {
     parser.suggestKeywords([ 'CURRENT' ]);
   }
 ;

ShowDatabasesStatement
 : 'SHOW' DatabasesOrSchemas 'LIKE' SingleQuotedValue
 | 'SHOW' 'DATABASES' SingleQuotedValue
 ;

ShowDatabasesStatement_EDIT
 : 'SHOW' DatabasesOrSchemas 'CURSOR'
   {
     parser.suggestKeywords(['LIKE']);
   }
 ;

ShowFilesStatement
 : 'SHOW' 'FILES' 'IN' RegularOrBackTickedSchemaQualifiedName OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
   }
 ;

ShowFilesStatement_EDIT
 : 'SHOW' 'FILES' 'CURSOR'
   {
     parser.suggestKeywords(['IN']);
   }
 | 'SHOW' 'FILES' 'IN' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' 'FILES' 'IN' RegularOrBackTickedSchemaQualifiedName_EDIT OptionalPartitionSpec
 | 'SHOW' 'FILES' 'IN' RegularOrBackTickedSchemaQualifiedName OptionalPartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($4);
     if (!$5) {
       parser.suggestKeywords(['PARTITION']);
     }
   }
 | 'SHOW' 'FILES' 'IN' RegularOrBackTickedSchemaQualifiedName OptionalPartitionSpec_EDIT
 | 'SHOW' 'FILES' 'CURSOR' RegularOrBackTickedSchemaQualifiedName OptionalPartitionSpec
   {
     parser.addTablePrimary($4);
     parser.suggestKeywords(['IN']);
   }
 ;

ShowFunctionsStatement
 : 'SHOW' OptionalAggregateOrAnalytic 'FUNCTIONS' OptionalInDatabase
 | 'SHOW' OptionalAggregateOrAnalytic 'FUNCTIONS' OptionalInDatabase 'LIKE' QuotedValue
 ;

ShowFunctionsStatement_EDIT
 : 'SHOW' AggregateOrAnalytic 'CURSOR'
   {
     parser.suggestKeywords(['FUNCTIONS']);
   }
 | 'SHOW' 'CURSOR' 'FUNCTIONS' OptionalInDatabase
   {
     parser.suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   }
 | 'SHOW' OptionalAggregateOrAnalytic 'FUNCTIONS' OptionalInDatabase 'CURSOR'
   {
     if (!$4) {
       parser.suggestKeywords(['IN', 'LIKE']);
     } else {
       parser.suggestKeywords(['LIKE']);
     }
   }
 | 'SHOW' AggregateOrAnalytic 'CURSOR' OptionalInDatabase 'LIKE' QuotedValue
   {
     parser.suggestKeywords(['FUNCTIONS']);
   }
 | 'SHOW' 'CURSOR' 'FUNCTIONS' OptionalInDatabase 'LIKE' QuotedValue
   {
     parser.suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   }
 | 'SHOW' OptionalAggregateOrAnalytic 'FUNCTIONS' OptionalInDatabase 'CURSOR' QuotedValue
   {
     if (!$4) {
       parser.suggestKeywords([{ value: 'IN', weight: 2 }, { value: 'LIKE', weight: 1 }]);
     } else {
       parser.suggestKeywords(['LIKE']);
     }
   }
 ;

ShowGrantStatement
 : 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'DATABASE' RegularOrBacktickedIdentifier
   {
     parser.addDatabaseLocation(@7, [ { name: $7 } ]);
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'SERVER'
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'TABLE' SchemaQualifiedTableIdentifier
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'URI' RegularOrBacktickedIdentifier
 ;

ShowGrantStatement_EDIT
 : 'SHOW' 'GRANT' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP', 'ROLE', 'USER']);
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser 'CURSOR'
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['ON DATABASE', 'ON SERVER', 'ON TABLE', 'ON URI']);
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'CURSOR'
   {
     parser.suggestKeywords(['DATABASE', 'SERVER', 'TABLE', 'URI']);
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'DATABASE' 'CURSOR'
   {
     parser.suggestDatabases();
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'TABLE' 'CURSOR'
   {
     parser.suggestDatabases({
       appendDot: true
     });
     parser.suggestTables();
   }
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'TABLE' SchemaQualifiedTableIdentifier_EDIT
 | 'SHOW' 'GRANT' GroupRoleOrUser RegularOrBacktickedIdentifier 'ON' 'URI' 'CURSOR'
 ;

OptionalPrincipalName
 :
 | RegularIdentifier
 ;

OptionalPrincipalName_EDIT
 : 'CURSOR'
 | RegularIdentifier 'CURSOR'
 ;

ShowPartitionsStatement
 : 'SHOW' 'PARTITIONS' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'RANGE' 'PARTITIONS' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($3);
   }
 ;

ShowPartitionsStatement_EDIT
 : 'SHOW' 'PARTITIONS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' 'PARTITIONS' RegularOrBackTickedSchemaQualifiedName_EDIT
 | 'SHOW' 'RANGE' 'PARTITIONS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' 'RANGE' 'PARTITIONS' RegularOrBackTickedSchemaQualifiedName_EDIT
 ;

ShowRoleStatement
 : 'SHOW' 'ROLE' 'GRANT' 'GROUP' RegularIdentifier
 ;

ShowRoleStatement_EDIT
 : 'SHOW' 'ROLE' 'CURSOR'
   {
     parser.suggestKeywords(['GRANT']);
   }
 | 'SHOW' 'ROLE' 'GRANT' 'CURSOR'
   {
     parser.suggestKeywords(['GROUP']);
   }
 | 'SHOW' 'ROLE' 'GRANT' 'CURSOR' RegularIdentifier
   {
     parser.suggestKeywords(['GROUP']);
   }
 ;

ShowRolesStatement
 : 'SHOW' 'ROLES'
 ;

ShowTableStatsStatement
 : 'SHOW' 'TABLE' 'STATS' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($4);
   }
 ;

ShowTableStatsStatement_EDIT
 : 'SHOW' 'TABLE' 'CURSOR'
   {
     parser.suggestKeywords(['STATS']);
   }
 | 'SHOW' 'TABLE' 'STATS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' 'TABLE' 'STATS' RegularOrBackTickedSchemaQualifiedName_EDIT
 ;

ShowTablesStatement
 : 'SHOW' 'TABLES' OptionalInDatabase
 | 'SHOW' 'TABLES' OptionalInDatabase SingleQuotedValue
 | 'SHOW' 'TABLES' OptionalInDatabase 'LIKE' SingleQuotedValue
 ;

ShowTablesStatement_EDIT
 : 'SHOW' 'TABLES' OptionalInDatabase 'CURSOR'
   {
     if (!$3) {
       parser.suggestKeywords(['IN', 'LIKE']);
     } else {
       parser.suggestKeywords(['LIKE']);
     }
   }
 ;
