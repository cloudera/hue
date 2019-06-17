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
 : ShowColumnsStatement
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
 | ShowRolesStatement
 | ShowRoleStatement
 | ShowTablesStatement
 | ShowTableStatement
 | ShowTblPropertiesStatement
 | ShowTransactionsStatement
 | ShowViewsStatement
 ;

ShowStatement_EDIT
 : 'SHOW' 'CURSOR'
   {
     parser.suggestKeywords(['COLUMNS', 'COMPACTIONS', 'CONF', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FORMATTED', 'FUNCTIONS', 'GRANT', 'INDEX', 'INDEXES', 'LOCKS', 'PARTITIONS', 'PRINCIPALS', 'ROLE GRANT', 'ROLES', 'SCHEMAS', 'TABLE EXTENDED', 'TABLES', 'TBLPROPERTIES', 'TRANSACTIONS', 'VIEWS']);
   }
 | 'SHOW' 'CURSOR' RegularOrBackTickedSchemaQualifiedName
   {
     // ROLES is considered a non-reserved keywords so we can't match it in ShowCurrentRolesStatement_EDIT
     if ($3.identifierChain && $3.identifierChain.length === 1 && $3.identifierChain[0].name.toLowerCase() === 'roles') {
       parser.suggestKeywords(['CURRENT']);
       parser.yy.locations.pop();
     } else {
       parser.addTablePrimary($3);
     }
   }
 | 'SHOW' 'CURSOR' LIKE SingleQuotedValue
   {
     parser.suggestKeywords(['DATABASES', 'SCHEMAS', 'TABLE EXTENDED']);
   }
 | ShowColumnsStatement_EDIT
 | ShowCreateTableStatement_EDIT
 | ShowCurrentRolesStatement_EDIT
 | ShowDatabasesStatement_EDIT
 | ShowGrantStatement_EDIT
 | ShowIndexStatement_EDIT
 | ShowLocksStatement_EDIT
 | ShowPartitionsStatement_EDIT
 | ShowRoleStatement_EDIT
 | ShowTablesStatement_EDIT
 | ShowTableStatement_EDIT
 | ShowTblPropertiesStatement_EDIT
 | ShowViewsStatement_EDIT
 ;

ShowColumnsStatement
 : 'SHOW' 'COLUMNS' FromOrIn RegularOrBacktickedIdentifier
 | 'SHOW' 'COLUMNS' FromOrIn RegularOrBacktickedIdentifier FromOrIn RegularOrBacktickedIdentifier
 ;

ShowColumnsStatement_EDIT
 : 'SHOW' 'COLUMNS' 'CURSOR'
   {
     parser.suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' 'COLUMNS' 'CURSOR' RegularOrBacktickedIdentifier
   {
     parser.suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' 'COLUMNS' FromOrIn 'CURSOR'
   {
     parser.suggestTables();
   }
 | 'SHOW' 'COLUMNS' FromOrIn 'CURSOR' FromOrIn
   {
     parser.suggestTables();
   }
 | 'SHOW' 'COLUMNS' FromOrIn 'CURSOR' FromOrIn RegularOrBacktickedIdentifier
   {
     parser.suggestTables();
   }
 | 'SHOW' 'COLUMNS' FromOrIn RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' 'COLUMNS' FromOrIn RegularOrBacktickedIdentifier 'CURSOR' RegularOrBacktickedIdentifier
   {
     parser.suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' 'COLUMNS' FromOrIn RegularOrBacktickedIdentifier FromOrIn 'CURSOR'
   {
     parser.suggestDatabases();
   }
 ;

ShowCompactionsStatement
 : 'SHOW' 'COMPACTIONS'
 ;

ShowConfStatement
 : 'SHOW' 'CONF' ConfigurationName
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
     parser.suggestKeywords(['TABLE']);
   }
 | 'SHOW' 'CREATE' TableOrView 'CURSOR'
   {
     parser.suggestTables();
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
     parser.suggestKeywords(['TABLE']);
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
 ;

ShowDatabasesStatement
 : 'SHOW' DatabasesOrSchemas 'LIKE' SingleQuotedValue
 ;

ShowDatabasesStatement_EDIT
 : 'SHOW' DatabasesOrSchemas 'CURSOR'
   {
     parser.suggestKeywords(['LIKE']);
   }
 ;

ShowFunctionsStatement
 : 'SHOW' 'FUNCTIONS'
 | 'SHOW' 'FUNCTIONS' DoubleQuotedValue
 ;

ShowGrantStatement
 : 'SHOW' 'GRANT' OptionalPrincipalName
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' 'ALL'
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' SchemaQualifiedTableIdentifier
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' 'TABLE' SchemaQualifiedTableIdentifier
 ;

ShowGrantStatement_EDIT
 : 'SHOW' 'GRANT' OptionalPrincipalName_EDIT
   {
     parser.suggestKeywords(['ON']);
   }
 | 'SHOW' 'GRANT' OptionalPrincipalName_EDIT 'ON' 'ALL'
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' 'CURSOR'
   {
     parser.suggestKeywords(['ALL', 'TABLE']);
     parser.suggestTables();
   }
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' SchemaQualifiedTableIdentifier_EDIT
 | 'SHOW'  'GRANT' OptionalPrincipalName 'ON' 'TABLE' 'CURSOR'
   {
     parser.suggestTables();
   }
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' 'CURSOR' SchemaQualifiedTableIdentifier
   {
     parser.suggestKeywords(['TABLE']);
   }
 | 'SHOW' 'GRANT' OptionalPrincipalName 'ON' 'CURSOR' SchemaQualifiedTableIdentifier_EDIT
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
 : 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier FromOrIn RegularOrBacktickedIdentifier
 ;

ShowIndexStatement_EDIT
 : 'SHOW' OptionallyFormattedIndex
 | 'SHOW' OptionallyFormattedIndex_EDIT
 | 'SHOW' OptionallyFormattedIndex_EDIT 'ON' RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex_EDIT 'ON' RegularOrBacktickedIdentifier FromOrIn RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex 'CURSOR'
   {
     parser.suggestKeywords(['ON']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' 'CURSOR'
   {
     parser.suggestTables();
   }
 | 'SHOW' OptionallyFormattedIndex 'CURSOR' RegularOrBacktickedIdentifier
   {
     parser.suggestKeywords(['ON']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier 'CURSOR' RegularOrBacktickedIdentifier
   {
     parser.suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier FromOrIn 'CURSOR'
   {
     parser.suggestDatabases();
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' 'CURSOR' FromOrIn RegularOrBacktickedIdentifier
   {
     parser.suggestTables({identifierChain: [{name: $6}]});
   }
 ;

ShowLocksStatement
 : 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName 'EXTENDED'
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName PartitionSpec
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName PartitionSpec 'EXTENDED'
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'LOCKS' DatabaseOrSchema RegularOrBacktickedIdentifier
 ;

ShowLocksStatement_EDIT
 : 'SHOW' 'LOCKS' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({
       appendDot: true
     });
     parser.suggestKeywords(['DATABASE', 'SCHEMA']);
   }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName 'CURSOR'
    {
      parser.addTablePrimary($3);
      parser.suggestKeywords(['EXTENDED', 'PARTITION']);
    }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT 'EXTENDED'
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT PartitionSpec
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName PartitionSpec 'CURSOR'
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' 'LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT PartitionSpec 'EXTENDED'
 | 'SHOW' 'LOCKS' DatabaseOrSchema 'CURSOR'
   {
     parser.suggestDatabases();
   }
 ;

ShowPartitionsStatement
 : 'SHOW' 'PARTITIONS' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'PARTITIONS' RegularOrBackTickedSchemaQualifiedName PartitionSpec
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
 | 'SHOW' 'PARTITIONS' RegularOrBackTickedSchemaQualifiedName 'CURSOR'
   {
     parser.addTablePrimary($3);
     parser.suggestKeywords(['PARTITION']);
   }
 | 'SHOW' 'PARTITIONS' RegularOrBackTickedSchemaQualifiedName_EDIT PartitionSpec
 ;

ShowRoleStatement
 : 'SHOW' 'ROLE' 'GRANT' RoleOrUser RegularIdentifier
 ;

ShowRoleStatement_EDIT
 : 'SHOW' 'ROLE' 'CURSOR'
   {
     parser.suggestKeywords(['GRANT']);
   }
 | 'SHOW' 'ROLE' 'CURSOR' RoleOrUser RegularIdentifier
   {
     parser.suggestKeywords(['GRANT']);
   }
 | 'SHOW' 'ROLE' 'GRANT' 'CURSOR'
   {
     parser.suggestKeywords(['ROLE', 'USER']);
   }
 | 'SHOW' 'ROLE' 'GRANT' 'CURSOR' RegularIdentifier
   {
     parser.suggestKeywords(['ROLE', 'USER']);
   }
 ;

ShowRolesStatement
 : 'SHOW' 'ROLES'
 ;

ShowTableStatement
 : 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue PartitionSpec
 ;

ShowTableStatement_EDIT
 : 'SHOW' 'TABLE' 'CURSOR'
   {
     parser.suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase_EDIT
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase 'CURSOR'
    {
      if ($4) {
        parser.suggestKeywords(['LIKE']);
      } else {
        parser.suggestKeywords(['FROM', 'IN', 'LIKE']);
      }
    }
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase_EDIT 'LIKE' SingleQuotedValue
 | 'SHOW' 'TABLE' 'CURSOR' OptionalFromDatabase 'LIKE' SingleQuotedValue
    {
      parser.suggestKeywords(['EXTENDED']);
    }
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase 'CURSOR' SingleQuotedValue
    {
      parser.suggestKeywords(['LIKE']);
    }
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue 'CURSOR'
    {
      parser.suggestKeywords(['PARTITION']);
    }
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase_EDIT 'LIKE' SingleQuotedValue PartitionSpec
 | 'SHOW' 'TABLE' 'CURSOR' OptionalFromDatabase 'LIKE' SingleQuotedValue PartitionSpec
   {
     parser.suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase 'CURSOR' SingleQuotedValue PartitionSpec
   {
     parser.suggestKeywords(['LIKE']);
   }
 | 'SHOW' 'TABLE' 'EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue 'CURSOR' PartitionSpecList
   {
     parser.suggestKeywords(['PARTITION']);
   }
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

ShowTblPropertiesStatement
 : 'SHOW' 'TBLPROPERTIES' RegularOrBackTickedSchemaQualifiedName
   {
     parser.addTablePrimary($3);
   }
 | 'SHOW' 'TBLPROPERTIES' RegularOrBackTickedSchemaQualifiedName '(' QuotedValue ')'
   {
     parser.addTablePrimary($3);
   }
 ;

ShowTblPropertiesStatement_EDIT
 : 'SHOW' 'TBLPROPERTIES' RegularOrBackTickedSchemaQualifiedName_EDIT
 | 'SHOW' 'TBLPROPERTIES' 'CURSOR'
   {
     parser.suggestTables();
     parser.suggestDatabases({ prependDot: true });
   }
 ;

ShowTransactionsStatement
 : 'SHOW' 'TRANSACTIONS'
 ;

ShowViewsStatement
 : 'SHOW' 'VIEWS' OptionalInOrFromDatabase OptionalLike
 ;

ShowViewsStatement_EDIT
 : 'SHOW' 'VIEWS' OptionalInOrFromDatabase OptionalLike 'CURSOR'
   {
     if (!$4 && !$3) {
       parser.suggestKeywords([{ value: 'IN', weight: 2 }, { value: 'FROM', weight: 2 }, { value: 'LIKE', weight: 1 }]);
     } else if (!$4) {
       parser.suggestKeywords(['LIKE']);
     }
   }
 | 'SHOW' 'VIEWS' InOrFromDatabase_EDIT OptionalLike
 | 'SHOW' 'VIEWS' OptionalInOrFromDatabase Like_EDIT
 ;

OptionalInOrFromDatabase
 :
 | 'IN' RegularOrBacktickedIdentifier
   {
     parser.addDatabaseLocation(@2, [ { name: $2 } ]);
   }
 | 'FROM' RegularOrBacktickedIdentifier
   {
     parser.addDatabaseLocation(@2, [ { name: $2 } ]);
   }
 ;

InOrFromDatabase_EDIT
 : 'IN' 'CURSOR'
   {
     parser.suggestDatabases();
   }
 | 'FROM' 'CURSOR'
   {
     parser.suggestDatabases();
   }
 ;

OptionalLike
 :
 | 'LIKE' SingleQuotedValue
 ;

Like_EDIT
 : 'LIKE' 'CURSOR'
 ;
