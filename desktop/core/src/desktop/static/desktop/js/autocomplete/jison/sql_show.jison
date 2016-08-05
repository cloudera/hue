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
 | ShowColumnsStatement
 | ShowCompactionsStatement
 | ShowConfStatement
 | ShowCreateTableStatement
 | ShowCurrentRolesStatement
 | ShowDatabasesStatement
 | ShowFunctionsStatement
 | ShowGrantStatement
 | ShowIndexStatement
 | ShowLocksStatement
 | ShowPartitionsStatement
 | ShowRoleStatement
 | ShowRolesStatement
 | ShowTableStatement
 | ShowTablesStatement
 | ShowTblPropertiesStatement
 | ShowTransactionsStatement
 ;

AnyShow
 : 'SHOW'
 | '<hive>SHOW'
 ;

ShowStatement_EDIT
 : AnyShow 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['COLUMNS', 'COMPACTIONS', 'CONF', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FORMATTED', 'FUNCTIONS', 'GRANT', 'INDEX', 'INDEXES', 'LOCKS', 'PARTITIONS', 'PRINCIPALS', 'ROLE GRANT', 'ROLES', 'SCHEMAS', 'TABLE EXTENDED', 'TABLES', 'TBLPROPERTIES', 'TRANSACTIONS']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'COLUMN STATS', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FUNCTIONS', 'GRANT ROLE', 'PARTITIONS', 'ROLE GRANT GROUP', 'ROLES', 'SCHEMAS', 'TABLE STATS', 'TABLES']);
     } else {
       suggestKeywords(['COLUMNS', 'DATABASES', 'TABLES']);
     }
   }
 | AnyShow 'CURSOR' RegularOrBackTickedSchemaQualifiedName
   {
     // ROLES is considered a non-reserved keywords so we can't match it in ShowCurrentRolesStatement_EDIT
     if ($3.identifierChain && $3.identifierChain.length === 1 && $3.identifierChain[0].name.toLowerCase() === 'roles') {
       suggestKeywords(['CURRENT']);
     } else {
       addTablePrimary($3);
       if (isImpala()) {
         suggestKeywords(['COLUMN STATS', 'CREATE TABLE', 'PARTITIONS', 'TABLE STATS']);
       }
     }
   }
 | AnyShow 'CURSOR' LIKE SingleQuotedValue
   {
     if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'DATABASES', 'FUNCTIONS', 'SCHEMAS', 'TABLES']);
     } else if (isHive()) {
       suggestKeywords(['DATABASES', 'SCHEMAS', 'TABLE EXTENDED']);
     }
   }
 | ShowColumnStatsStatement_EDIT
 | ShowColumnsStatement_EDIT
 | ShowCreateTableStatement_EDIT
 | ShowCurrentRolesStatement_EDIT
 | ShowDatabasesStatement_EDIT
 | ShowFunctionsStatement_EDIT
 | ShowGrantStatement_EDIT
 | ShowIndexStatement_EDIT
 | ShowLocksStatement_EDIT
 | ShowPartitionsStatement_EDIT
 | ShowRoleStatement_EDIT
 | ShowTableStatement_EDIT
 | ShowTablesStatement_EDIT
 | ShowTblPropertiesStatement_EDIT
 ;

ShowColumnStatsStatement
 : AnyShow '<impala>COLUMN' '<impala>STATS' RegularOrBackTickedSchemaQualifiedName
   {
     addTablePrimary($4);
   }
 ;

ShowColumnStatsStatement_EDIT
 : AnyShow '<impala>COLUMN' 'CURSOR'
   {
     suggestKeywords(['STATS']);
   }
 | AnyShow '<impala>COLUMN' '<impala>STATS' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | AnyShow '<impala>COLUMN' '<impala>STATS' RegularOrBackTickedSchemaQualifiedName_EDIT
 ;

ShowColumnsStatement
 : AnyShow '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier
 | AnyShow '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 ;

ShowColumnsStatement_EDIT
 : AnyShow '<hive>COLUMNS' 'CURSOR'
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | AnyShow '<hive>COLUMNS' 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | AnyShow '<hive>COLUMNS' AnyFromOrIn 'CURSOR'
   {
     suggestTables();
   }
 | AnyShow '<hive>COLUMNS' AnyFromOrIn 'CURSOR' AnyFromOrIn
   {
     suggestTables();
   }
 | AnyShow '<hive>COLUMNS' AnyFromOrIn 'CURSOR' AnyFromOrIn RegularOrBacktickedIdentifier
   {
     suggestTables();
   }
 | AnyShow '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier 'CURSOR'
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | AnyShow '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | AnyShow '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier AnyFromOrIn 'CURSOR'
   {
     suggestDatabases();
   }
 ;

ShowCompactionsStatement
 : AnyShow '<hive>COMPACTIONS'
 ;

ShowConfStatement
 : AnyShow '<hive>CONF' ConfigurationName
 ;

ShowCreateTableStatement
 : AnyShow HiveOrImpalaCreate AnyTable RegularOrBackTickedSchemaQualifiedName
   {
     addTablePrimary($4);
   }
 ;

ShowCreateTableStatement_EDIT
 : AnyShow HiveOrImpalaCreate 'CURSOR'
   {
     suggestKeywords(['TABLE']);
   }
 | AnyShow HiveOrImpalaCreate AnyTable 'CURSOR'
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | AnyShow HiveOrImpalaCreate AnyTable RegularOrBackTickedSchemaQualifiedName_EDIT
 | AnyShow HiveOrImpalaCreate 'CURSOR' RegularOrBackTickedSchemaQualifiedName
   {
     addTablePrimary($4);
     suggestKeywords(['TABLE']);
   }
 ;

ShowCurrentRolesStatement
 : AnyShow '<hive>CURRENT' '<hive>ROLES'
 | AnyShow '<impala>CURRENT' '<impala>ROLES'
 ;

ShowCurrentRolesStatement_EDIT
 : AnyShow '<hive>CURRENT' 'CURSOR'
   {
     suggestKeywords([ 'ROLES' ]);
   }
 | AnyShow '<impala>CURRENT' 'CURSOR'
   {
     suggestKeywords([ 'ROLES' ]);
   }
 ;

ShowDatabasesStatement
 : AnyShow HiveOrImpalaDatabasesOrSchemas 'LIKE' SingleQuotedValue
 | AnyShow '<impala>DATABASES' SingleQuotedValue
 ;

ShowDatabasesStatement_EDIT
 : AnyShow HiveOrImpalaDatabasesOrSchemas 'CURSOR'
   {
     suggestKeywords(['LIKE']);
   }
 ;

ShowFunctionsStatement
 : AnyShow '<hive>FUNCTIONS'
 | AnyShow '<hive>FUNCTIONS' DoubleQuotedValue
 | AnyShow OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase
 | AnyShow OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase 'LIKE' SingleQuoteValue
 ;

ShowFunctionsStatement_EDIT
 : AnyShow AggregateOrAnalytic 'CURSOR'
   {
     suggestKeywords(['FUNCTIONS']);
   }
 | AnyShow 'CURSOR' '<impala>FUNCTIONS' OptionalInDatabase
   {
     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   }
 | AnyShow OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase 'CURSOR'
   {
     if (!$4) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   }
 | AnyShow AggregateOrAnalytic 'CURSOR' OptionalInDatabase 'LIKE' SingleQuoteValue
   {
     suggestKeywords(['FUNCTIONS']);
   }
 | AnyShow 'CURSOR' '<impala>FUNCTIONS' OptionalInDatabase 'LIKE' SingleQuoteValue
   {
     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   }
 | AnyShow OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase 'CURSOR' SingleQuoteValue
   {
     if (!$4) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   }
 ;

ShowGrantStatement
 : AnyShow '<hive>GRANT' OptionalPrincipalName
 | AnyShow '<hive>GRANT' OptionalPrincipalName 'ON' '<hive>ALL'
 | AnyShow '<hive>GRANT' OptionalPrincipalName 'ON' RegularOrBacktickedIdentifier
 | AnyShow '<hive>GRANT' OptionalPrincipalName 'ON' AnyTable RegularOrBacktickedIdentifier
 ;

ShowGrantStatement_EDIT
 : AnyShow '<hive>GRANT' OptionalPrincipalName_EDIT
   {
     suggestKeywords(['ON']);
   }
 | AnyShow '<hive>GRANT' OptionalPrincipalName_EDIT 'ON' '<hive>ALL'
 | AnyShow '<hive>GRANT' OptionalPrincipalName 'ON' 'CURSOR'
   {
     suggestKeywords(['ALL', 'TABLE']);
     suggestTables();
   }
 | AnyShow  '<hive>GRANT' OptionalPrincipalName 'ON' AnyTable 'CURSOR'
   {
     suggestTables();
   }
 | AnyShow '<hive>GRANT' OptionalPrincipalName 'ON' 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['TABLE']);
   }
 | AnyShow '<impala>GRANT' 'CURSOR'
   {
     suggestKeywords(['ROLE']);
   }
 ;

OptionalPrincipalName
 :
 | RegularIdentifier
 ;

OptionalPrincipalName_EDIT
 : 'CURSOR'
 | RegularIdentifier 'CURSOR'
 ;

ShowIndexStatement
 : AnyShow OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier
 | AnyShow OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 ;

ShowIndexStatement_EDIT
 : AnyShow OptionallyFormattedIndex
 | AnyShow OptionallyFormattedIndex_EDIT
 | AnyShow OptionallyFormattedIndex_EDIT 'ON' RegularOrBacktickedIdentifier
 | AnyShow OptionallyFormattedIndex_EDIT 'ON' RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 | AnyShow OptionallyFormattedIndex 'CURSOR'
   {
     suggestKeywords(['ON']);
   }
 | AnyShow OptionallyFormattedIndex 'ON' 'CURSOR'
   {
     suggestTables();
   }
 | AnyShow OptionallyFormattedIndex 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['ON']);
   }
 | AnyShow OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier 'CURSOR'
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | AnyShow OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | AnyShow OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier AnyFromOrIn 'CURSOR'
   {
     suggestDatabases();
   }
 | AnyShow OptionallyFormattedIndex 'ON' 'CURSOR' AnyFromOrIn RegularOrBacktickedIdentifier
   {
     suggestTablesOrColumns($6);
   }
 ;

ShowLocksStatement
 : AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName
   {
     addTablePrimary($3);
   }
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName '<hive>EXTENDED'
   {
     addTablePrimary($3);
   }
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName PartitionSpec
   {
     addTablePrimary($3);
   }
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName PartitionSpec '<hive>EXTENDED'
   {
     addTablePrimary($3);
   }
 | AnyShow '<hive>LOCKS' DatabaseOrSchema RegularOrBacktickedIdentifier
 ;

ShowLocksStatement_EDIT
 : AnyShow '<hive>LOCKS' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
     suggestKeywords(['DATABASE', 'SCHEMA']);
   }
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName 'CURSOR'
    {
      addTablePrimary($3);
      suggestKeywords(['EXTENDED', 'PARTITION']);
    }
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT '<hive>EXTENDED'
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT PartitionSpec
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName PartitionSpec 'CURSOR'
   {
     addTablePrimary($3);
     suggestKeywords(['EXTENDED']);
   }
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT PartitionSpec '<hive>EXTENDED'
 | AnyShow '<hive>LOCKS' DatabaseOrSchema 'CURSOR'
   {
     suggestDatabases();
   }
 ;

ShowPartitionsStatement
 : AnyShow '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName
   {
     addTablePrimary($3);
   }
 | AnyShow '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName PartitionSpec
   {
     addTablePrimary($3);
   }
 | AnyShow '<impala>PARTITIONS' RegularOrBackTickedSchemaQualifiedName
   {
     addTablePrimary($3);
   }
 ;

ShowPartitionsStatement_EDIT
 : AnyShow '<hive>PARTITIONS' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | AnyShow '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName_EDIT
 | AnyShow '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName 'CURSOR'
   {
     addTablePrimary($3);
     suggestKeywords(['PARTITION']);
   }
 | AnyShow '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName_EDIT PartitionSpec
 | AnyShow '<impala>PARTITIONS' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | AnyShow '<impala>PARTITIONS' RegularOrBackTickedSchemaQualifiedName_EDIT
 ;

ShowRoleStatement
 : AnyShow '<hive>ROLE' '<hive>GRANT' HiveRoleOrUser RegularIdentifier
 | AnyShow '<impala>ROLE' '<impala>GRANT' '<impala>GROUP' RegularIdentifier
 ;

ShowRoleStatement_EDIT
 : AnyShow '<hive>ROLE' 'CURSOR'
   {
     suggestKeywords(['GRANT']);
   }
 | AnyShow '<impala>ROLE' 'CURSOR'
   {
     suggestKeywords(['GRANT']);
   }
 | AnyShow '<hive>ROLE' 'CURSOR' HiveRoleOrUser RegularIdentifier
   {
     suggestKeywords(['GRANT']);
   }
 | AnyShow '<hive>ROLE' '<hive>GRANT' 'CURSOR'
   {
     suggestKeywords(['ROLE', 'USER']);
   }
 | AnyShow '<hive>ROLE' '<hive>GRANT' 'CURSOR' RegularIdentifier
   {
     suggestKeywords(['ROLE', 'USER']);
   }
 | AnyShow '<impala>ROLE' '<impala>GRANT' 'CURSOR'
   {
     suggestKeywords(['GROUP']);
   }
 | AnyShow '<impala>ROLE' '<impala>GRANT' 'CURSOR' RegularIdentifier
   {
     suggestKeywords(['GROUP']);
   }
 ;

ShowRolesStatement
 : AnyShow '<impala>ROLES'
 | AnyShow '<hive>ROLES'
 ;

ShowTableStatement
 : AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue PartitionSpec
 ;

ShowTableStatement_EDIT
 : AnyShow '<hive>TABLE' 'CURSOR'
   {
     suggestKeywords(['EXTENDED']);
   }
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_EDIT
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'CURSOR'
    {
      if ($4) {
        suggestKeywords(['LIKE']);
      } else {
        suggestKeywords(['FROM', 'IN', 'LIKE']);
      }
    }
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_EDIT 'LIKE' SingleQuotedValue
 | AnyShow '<hive>TABLE' 'CURSOR' OptionalFromDatabase 'LIKE' SingleQuotedValue
    {
      if (isHive()) {
        suggestKeywords(['EXTENDED']);
      }
    }
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'CURSOR' SingleQuotedValue
    {
      suggestKeywords(['LIKE']);
    }
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue 'CURSOR'
    {
      suggestKeywords(['PARTITION']);
    }
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_EDIT 'LIKE' SingleQuotedValue PartitionSpec
 | AnyShow '<hive>TABLE' 'CURSOR' OptionalFromDatabase 'LIKE' SingleQuotedValue PartitionSpec
   {
     suggestKeywords(['EXTENDED']);
   }
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'CURSOR' SingleQuotedValue PartitionSpec
   {
     suggestKeywords(['LIKE']);
   }
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue 'CURSOR' PartitionSpecList
   {
     suggestKeywords(['PARTITION']);
   }
 | AnyShow '<impala>TABLE' 'CURSOR'
   {
     suggestKeywords(['STATS']);
   }
 | AnyShow '<impala>TABLE' '<impala>STATS' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | AnyShow '<impala>TABLE' '<impala>STATS' RegularOrBackTickedSchemaQualifiedName
    {
      addTablePrimary($4);
    }
 | AnyShow '<impala>TABLE' '<impala>STATS' RegularOrBackTickedSchemaQualifiedName_EDIT
 ;

ShowTablesStatement
 : AnyShow HiveOrImpalaTables OptionalInDatabase
 | AnyShow HiveOrImpalaTables OptionalInDatabase SingleQuotedValue
 | AnyShow HiveOrImpalaTables OptionalInDatabase 'LIKE' SingleQuotedValue
 ;

ShowTablesStatement_EDIT
 : AnyShow HiveOrImpalaTables OptionalInDatabase 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   }
 ;

ShowTblPropertiesStatement
 : AnyShow '<hive>TBLPROPERTIES' RegularOrBackTickedSchemaQualifiedName
   {
     addTablePrimary($3);
   }
 ;

ShowTblPropertiesStatement_EDIT
 : AnyShow '<hive>TBLPROPERTIES' RegularOrBackTickedSchemaQualifiedName_EDIT
 | AnyShow '<hive>TBLPROPERTIES' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({ prependDot: true });
   }
 ;

ShowTransactionsStatement
 : AnyShow '<hive>TRANSACTIONS'
 ;