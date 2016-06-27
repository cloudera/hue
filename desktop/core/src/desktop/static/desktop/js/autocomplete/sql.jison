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

%lex
%options case-insensitive
%s hive impala
%x hdfs doubleQuotedValue singleQuotedValue backtickedValue
%%

[ \t\n]                             { /* skip whitespace */ }
'--'.*                              { /* skip comments */ }
[/][*][^*]*[*]+([^/*][^*]*[*]+)*[/] { /* skip comments */ }

'\u2020'                            { parser.yy.cursorFound = true; return 'CURSOR'; }
'\u2021'                            { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }

<hive>'AS'                          { return '<hive>AS'; }
<hive>'ALL'                         { return '<hive>ALL'; }
<hive>'BINARY'                      { return '<hive>BINARY'; }
<hive>'COLUMNS'                     { return '<hive>COLUMNS'; }
<hive>'COMMENT'                     { return '<hive>COMMENT'; }
<hive>'COMPACTIONS'                 { return '<hive>COMPACTIONS'; }
<hive>'CONF'                        { return '<hive>CONF'; }
<hive>'CREATE'                      { determineCase(yytext); return '<hive>CREATE'; }
<hive>'CURRENT'                     { return '<hive>CURRENT'; }
<hive>'DATA'                        { return '<hive>DATA'; }
<hive>'DATABASES'                   { return '<hive>DATABASES'; }
<hive>'DATE'                        { return '<hive>DATE'; }
<hive>'EXTENDED'                    { return '<hive>EXTENDED'; }
<hive>'EXTERNAL'                    { return '<hive>EXTERNAL'; }
<hive>'FORMATTED'                   { return '<hive>FORMATTED'; }
<hive>'FUNCTION'                    { return '<hive>FUNCTION'; }
<hive>'FUNCTIONS'                   { return '<hive>FUNCTIONS'; }
<hive>'GRANT'                       { return '<hive>GRANT'; }
<hive>'IN'                          { return '<hive>IN'; }
<hive>'INDEX'                       { return '<hive>INDEX'; }
<hive>'INDEXES'                     { return '<hive>INDEXES'; }
<hive>'INPATH'                      { this.begin('hdfs'); return '<hive>INPATH'; }
<hive>'LATERAL'                     { return '<hive>LATERAL'; }
<hive>'LOAD'                        { return '<hive>LOAD'; }
<hive>'LOCATION'                    { this.begin('hdfs'); return '<hive>LOCATION'; }
<hive>'LOCKS'                       { return '<hive>LOCKS'; }
<hive>'MACRO'                       { return '<hive>MACRO'; }
<hive>'PARTITION'                   { return '<hive>PARTITION'; }
<hive>'PARTITIONS'                  { return '<hive>PARTITIONS'; }
<hive>'ROLE'                        { return '<hive>ROLE'; }
<hive>'ROLES'                       { return '<hive>ROLES'; }
<hive>'SCHEMAS'                     { return '<hive>SCHEMAS'; }
<hive>'TABLE'                       { return '<hive>TABLE'; }
<hive>'TABLES'                      { return '<hive>TABLES'; }
<hive>'TBLPROPERTIES'               { return '<hive>TBLPROPERTIES'; }
<hive>'TEMPORARY'                   { return '<hive>TEMPORARY'; }
<hive>'TRANSACTIONS'                { return '<hive>TRANSACTIONS'; }
<hive>'USER'                        { return '<hive>USER'; }

<hive>'explode'                     { return '<hive>explode'; }
<hive>'posexplode'                  { return '<hive>posexplode'; }

<hive>[.]                           { return '<hive>.'; }

<impala>'AGGREGATE'                 { return '<impala>AGGREGATE'; }
<impala>'ANALYTIC'                  { return '<impala>ANALYTIC'; }
<impala>'COLUMN'                    { return '<impala>COLUMN'; }
<impala>'COMMENT'                   { return '<impala>COMMENT'; }
<impala>'CREATE'                    { determineCase(yytext); return '<impala>CREATE'; }
<impala>'CURRENT'                   { return '<impala>CURRENT'; }
<impala>'DATA'                      { return '<impala>DATA'; }
<impala>'DATABASES'                 { return '<impala>DATABASES'; }
<impala>'FUNCTION'                  { return '<impala>FUNCTION'; }
<impala>'FUNCTIONS'                 { return '<impala>FUNCTIONS'; }
<impala>'GRANT'                     { return '<impala>GRANT'; }
<impala>'GROUP'                     { return '<impala>GROUP'; }
<impala>'EXTERNAL'                  { return '<impala>EXTERNAL'; }
<impala>'INCREMENTAL'               { return '<impala>INCREMENTAL'; }
<impala>'INPATH'                    { this.begin('hdfs'); return '<impala>INPATH'; }
<impala>'IN'                        { return '<impala>IN'; }
<impala>'LOAD'                      { return '<impala>LOAD'; }
<impala>'LOCATION'                  { this.begin('hdfs'); return '<impala>LOCATION'; }
<impala>'PARTITIONS'                { return '<impala>PARTITIONS'; }
<impala>'ROLE'                      { return '<impala>ROLE'; }
<impala>'ROLES'                     { return '<impala>ROLES'; }
<impala>'SCHEMAS'                   { return '<impala>SCHEMAS'; }
<impala>'STATS'                     { return '<impala>STATS'; }
<impala>'TABLE'                     { return '<impala>TABLE'; }
<impala>'TABLES'                    { return '<impala>TABLES'; }

<impala>[.]                         { return '<impala>.'; }

'AND'                               { return 'AND'; }
'BIGINT'                            { return 'BIGINT'; }
'BOOLEAN'                           { return 'BOOLEAN'; }
'BY'                                { return 'BY'; }
'CHAR'                              { return 'CHAR'; }
'CREATE'                            { determineCase(yytext); return 'CREATE'; }
'DATABASE'                          { return 'DATABASE'; }
'DECIMAL'                           { return 'DECIMAL'; }
'DOUBLE'                            { return 'DOUBLE'; }
'DROP'                              { determineCase(yytext); return 'DROP'; }
'EXISTS'                            { return 'EXISTS'; }
'FLOAT'                             { return 'FLOAT'; }
'FROM'                              { return 'FROM'; }
'GROUP'                             { return 'GROUP'; }
'IF'                                { return 'IF'; }
'INT'                               { return 'INT'; }
'INTO'                              { return 'INTO'; }
'IS'                                { return 'IS'; }
'JOIN'                              { return 'JOIN'; }
'LIKE'                              { return 'LIKE'; }
'NOT'                               { return 'NOT'; }
'ON'                                { return 'ON'; }
'OR'                                { return 'OR'; }
'ORDER'                             { return 'ORDER'; }
'ROLE'                              { return 'ROLE'; }
'SCHEMA'                            { return 'SCHEMA'; }
'SELECT'                            { determineCase(yytext); return 'SELECT'; }
'SET'                               { return 'SET'; }
'SHOW'                              { determineCase(yytext); return 'SHOW'; }
'SMALLINT'                          { return 'SMALLINT'; }
'STRING'                            { return 'STRING'; }
'TABLE'                             { return 'TABLE'; }
'TIMESTAMP'                         { return 'TIMESTAMP'; }
'TINYINT'                           { return 'TINYINT'; }
'UPDATE'                            { determineCase(yytext); return 'UPDATE'; }
'USE'                               { determineCase(yytext); return 'USE'; }
'VARCHAR'                           { return 'VARCHAR'; }
'VIEW'                              { return 'VIEW'; }
'WHERE'                             { return 'WHERE'; }

[0-9]+                              { return 'UNSIGNED_INTEGER'; }
[A-Za-z][A-Za-z0-9_]*               { return 'REGULAR_IDENTIFIER'; }

<hdfs>'\u2020'                      { parser.yy.cursorFound = true; return 'CURSOR'; }
<hdfs>'\u2021'                      { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }
<hdfs>\s+[']                        { return 'HDFS_START_QUOTE'; }
<hdfs>[^'\u2020\u2021]+             { return 'HDFS_PATH'; }
<hdfs>[']                           { this.popState(); return 'HDFS_END_QUOTE'; }
<hdfs><<EOF>>                       { return 'EOF'; }

[-+&~|^/%*(),.;!]                   { return yytext; }
[=<>]+                              { return yytext; }


\[                                  { return '['; }
\]                                  { return ']'; }

\`                                  { this.begin('backtickedValue'); return 'BACKTICK'; }
<backtickedValue>[^`]+              { if (yytext.indexOf('\u2020') !== -1 || yytext.indexOf('\u2021') !== -1) {
                                        this.popState();
                                        return 'PARTIAL_VALUE';
                                      }
                                      return 'VALUE';
                                    }
<backtickedValue>\`                 { this.popState(); return 'BACKTICK'; }

\'                                  { this.begin('singleQuotedValue'); return 'SINGLE_QUOTE'; }
<singleQuotedValue>[^']+            { return 'VALUE'; }
<singleQuotedValue>\'               { this.popState(); return 'SINGLE_QUOTE'; }

\"                                  { this.begin('doubleQuotedValue'); return 'DOUBLE_QUOTE'; }
<doubleQuotedValue>[^"]+            { return 'VALUE'; }
<doubleQuotedValue>\"               { this.popState(); return 'DOUBLE_QUOTE'; }

<<EOF>>                             { return 'EOF'; }

/lex

%start Sql

%%

AnyCursor
 : 'CURSOR'
 | 'PARTIAL_CURSOR'
 ;

PartialIdentifierOrCursor
 : 'REGULAR_IDENTIFIER' 'PARTIAL_CURSOR'
 | 'CURSOR'
 ;

PartialIdentifierOrPartialCursor
 : 'REGULAR_IDENTIFIER' 'PARTIAL_CURSOR'
 | 'PARTIAL_CURSOR'
 ;

InitResults
 : /* empty */
   {
     parser.yy.result = {};
     parser.yy.cursorFound = false;

     // TODO: Move these below before token or use $$ instead
     delete parser.yy.latestTablePrimaries;
     delete parser.yy.identifierChain;
     delete parser.yy.derivedColumnChain;
     delete parser.yy.currentViews;
     delete parser.yy.keepColumns;

     parser.parseError = function (message, error) {
       if (typeof parser.yy.result.suggestColumns !== 'undefined') {
         linkTablePrimaries();
       }
       prioritizeSuggestions();
       parser.yy.result.error = error;
       return message;
     }
   }
 ;

Sql
 : InitResults SqlStatements ';' EOF
   {
     prioritizeSuggestions();
     return parser.yy.result;
   }
 | InitResults SqlStatements EOF
   {
     prioritizeSuggestions();
     return parser.yy.result;
   }
 ;

SqlStatements
 : SqlStatement
 | SqlStatements ';' SqlStatement
 ;

SqlStatement
 : DataManipulation
 | DataDefinition
 | QueryExpression
 | 'REGULAR_IDENTIFIER' 'PARTIAL_CURSOR' 'REGULAR_IDENTIFIER'
 | 'REGULAR_IDENTIFIER' 'PARTIAL_CURSOR'
   {
     suggestDdlAndDmlKeywords();
   }
 | AnyCursor // Could be either ;| or ; |
   {
     suggestDdlAndDmlKeywords();
   }
 ;

DataManipulation
 : LoadStatement
 | UpdateStatement
 ;

LoadStatement
 : HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath 'INTO' AnyTable 'REGULAR_IDENTIFIER'
 | HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath 'INTO' PartialIdentifierOrCursor
   {
     suggestKeywords([ 'TABLE' ]);
   }
 | HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath PartialIdentifierOrCursor
   {
     suggestKeywords([ 'INTO' ]);
   }
 | HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath
 | HiveOrImpalaLoad HiveOrImpalaData PartialIdentifierOrCursor
   {
     suggestKeywords([ 'INPATH' ]);
   }
 | HiveOrImpalaLoad PartialIdentifierOrCursor
   {
     suggestKeywords([ 'DATA' ]);
   }
 ;

HiveOrImpalaLoad
 : '<hive>LOAD'
 | '<impala>LOAD'
 ;

HiveOrImpalaData
 : '<hive>DATA'
 | '<impala>DATA'
 ;

HiveOrImpalaInpath
 : '<hive>INPATH'
 | '<impala>INPATH'
 ;

UpdateStatement
 : 'UPDATE' TargetTable 'SET' SetClauseList WhereClause
   {
     linkTablePrimaries();
   }
 | 'UPDATE' TargetTable 'SET' SetClauseList 'CURSOR'
   {
     suggestKeywords([ 'WHERE' ]);
   }
 | 'UPDATE' TargetTable 'SET' SetClauseList
   {
     linkTablePrimaries();
   }
 | 'UPDATE' TargetTable 'CURSOR'
   {
     suggestKeywords([ 'SET' ]);
   }
 | 'UPDATE' TargetTable
 | 'UPDATE' PartialIdentifierOrCursor
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 ;

TargetTable
 : TableName
 ;

TableName
 : LocalOrSchemaQualifiedName
   {
     // TODO: Replace with TablePrimary?
     if ($1.partial) {
       if ($1.identifierChain.length === 1) {
         suggestTablesOrColumns($1.identifierChain[0].name);
       }
     } else if (typeof $1.identifierChain !== 'undefined') {
       addTablePrimary($1);
     }
   }
 ;

SetClauseList
 : SetClause
 | SetClauseList ',' SetClause
 ;

SetClause
 : SetTarget '=' UpdateSource
 | SetTarget 'CURSOR'
   {
     suggestKeywords([ '=' ]);
   }
 | PartialIdentifierOrCursor
   {
     suggestColumns();
   }
 ;

SetTarget
 : 'REGULAR_IDENTIFIER'
 ;

UpdateSource
 : ValueExpression
 ;

ValueExpression
 : BooleanValueExpression
 ;

DataDefinition
 : CreateStatement
 | DropStatement
 | ShowStatement
 | UseStatement
 ;

AnyCreate
 : 'CREATE'
 | '<hive>CREATE'
 | '<impala>CREATE'
 ;

AnyTable
 : 'TABLE'
 | '<hive>TABLE'
 | '<impala>TABLE'
 ;

CreateStatement
 : TableDefinition
 | DatabaseDefinition
 | AnyCreate PartialIdentifierOrCursor
   {
     if (isHive() || isImpala()) {
       suggestKeywords(['DATABASE', 'EXTERNAL', 'SCHEMA', 'TABLE']);
     } else {
       suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE']);
     }
   }
 ;

DropStatement
 : 'DROP' PartialIdentifierOrCursor
   {
     if (isHive()) {
       suggestKeywords(['DATABASE', 'FUNCTION', 'INDEX', 'MACRO', 'ROLE', 'SCHEMA', 'TABLE', 'TEMPORARY FUNCTION', 'TEMPORARY MACRO', 'VIEW']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTION', 'DATABASE', 'FUNCTION', 'INCREMENTAL STATS', 'ROLE', 'SCHEMA', 'STATS', 'TABLE', 'VIEW']);
     } else {
       suggestKeywords(['ROLE', 'SCHEMA', 'TABLE', 'VIEW']);
     }
   }
 | DropDatabaseStatement
 | DropTableStatement
 ;

OptionalHiveCascadeOrRestrict
 :
 | '<hive>CASCADE'
 | '<hive>RESTRICT'
 ;

DropDatabaseStatement
 : 'DROP' DatabaseOrSchema OptionalIfExists
 | 'DROP' DatabaseOrSchema OptionalIfExists PartialIdentifierOrCursor
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases();
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists RegularOrBacktickedIdentifier PartialIdentifierOrCursor
   {
     if (isHive()) {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict
 ;

DropTableStatement
 : 'DROP' AnyTable OptionalIfExists
 | 'DROP' AnyTable OptionalIfExists PartialIdentifierOrCursor
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'DROP' AnyTable OptionalIfExists TablePrimary
   {
     if (!$3 && !$4.partial) {
       suggestKeywords(['IF EXISTS']);
     }
     if ($4.partial) {
       if ($4.identifierChain.length === 1) {
         suggestTablesOrColumns($4.identifierChain[0].name);
       } else if ($1.identifierChain.length === 0) {
         suggestTables();
         suggestDatabases({ appendDot: true });
       }
     }
   }
 | 'DROP' AnyTable OptionalIfExists TablePrimary 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['PURGE']);
     }
   }
 ;

DatabaseOrSchema
 : 'DATABASE'
 | 'SCHEMA'
 ;

OptionalIfExists
 : { $$ = false }
 | 'IF' PartialIdentifierOrCursor
   {
     suggestKeywords(['EXISTS']);
   }
 | 'IF' 'EXISTS'
 ;

UseStatement
 : 'USE' 'REGULAR_IDENTIFIER'
   {
     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $2;
     }
   }
 | 'USE' PartialIdentifierOrCursor
   {
     suggestDatabases();
   }
 ;

ShowStatement
 : 'SHOW' PartialIdentifierOrCursor
   {
     if (isHive()) {
       suggestKeywords(['COLUMNS', 'COMPACTIONS', 'CONF', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FORMATTED', 'FUNCTIONS', 'GRANT', 'INDEX', 'INDEXES', 'LOCKS', 'PARTITIONS', 'PRINCIPALS', 'ROLE GRANT', 'ROLES', 'SCHEMAS', 'TABLE EXTENDED', 'TABLES', 'TBLPROPERTIES', 'TRANSACTIONS']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'COLUMN STATS', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FUNCTIONS', 'GRANT ROLE', 'PARTITIONS', 'ROLE GRANT GROUP', 'ROLES', 'SCHEMAS', 'TABLE STATS', 'TABLES']);
     } else {
       suggestKeywords(['COLUMNS', 'DATABASES', 'TABLES']);
     }
   }
 | 'SHOW' PartialIdentifierOrCursor CleanRegularOrBackTickedSchemaQualifiedName
   {
     if (isImpala()) {
       suggestKeywords(['COLUMN STATS', 'CREATE TABLE', 'PARTITIONS', 'TABLE STATS']);
     }
   }
 | 'SHOW' PartialIdentifierOrCursor LIKE SingleQuotedValue
   {
     if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'DATABASES', 'FUNCTIONS', 'SCHEMAS', 'TABLES']);
     } else if (isHive()) {
       suggestKeywords(['DATABASES', 'SCHEMAS', 'TABLE EXTENDED']);
     }
   }
 | ShowColumnStatement
 | ShowColumnsStatement
 | ShowCompactionsStatement
 | ShowConfStatement
 | ShowCreateTableStatement
 | ShowCurrentStatement
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

ShowColumnStatement
 : 'SHOW' '<impala>COLUMN' PartialIdentifierOrCursor
   {
     suggestKeywords(['STATS']);
   }
 | 'SHOW' '<impala>COLUMN' '<impala>STATS' PartialIdentifierOrCursor
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' '<impala>COLUMN' '<impala>STATS' CleanRegularOrBackTickedSchemaQualifiedName
   if ($3.partial && $3.identifierChain.length === 1) {
     suggestTablesOrColumns($3.identifierChain[0].name)
   }
 ;

ShowColumnsStatement
 : 'SHOW' '<hive>COLUMNS' PartialIdentifierOrCursor
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' '<hive>COLUMNS' PartialIdentifierOrCursor RegularOrBacktickedIdentifier
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn PartialIdentifierOrCursor
   {
     suggestTables();
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn PartialIdentifierOrCursor AnyFromOrIn
   {
     suggestTables();
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn PartialIdentifierOrCursor AnyFromOrIn RegularOrBacktickedIdentifier
   {
     suggestTables();
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier PartialIdentifierOrCursor
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier PartialIdentifierOrCursor RegularOrBacktickedIdentifier
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier AnyFromOrIn PartialIdentifierOrCursor
   {
     suggestDatabases();
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 ;

ShowCompactionsStatement
 : 'SHOW' '<hive>COMPACTIONS'
 ;

ShowConfStatement
 : 'SHOW' '<hive>CONF' ConfigurationName
 ;

ConfigurationName
 : 'REGULAR_IDENTIFIER'
 | PartialIdentifierOrCursor
 | ConfigurationName '<hive>.' 'REGULAR_IDENTIFIER'
 | ConfigurationName '<hive>.' PartialIdentifierOrCursor
 | ConfigurationName '<hive>.' 'PARTIAL_CURSOR'
 ;

AnyFromOrIn
 : 'FROM'
 | '<hive>IN'
 ;

ShowCreateTableStatement
 : 'SHOW' HiveOrImpalaCreate PartialIdentifierOrCursor
   {
     suggestKeywords(['TABLE']);
   }
 | 'SHOW' HiveOrImpalaCreate AnyTable PartialIdentifierOrCursor
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' HiveOrImpalaCreate AnyTable CleanRegularOrBackTickedSchemaQualifiedName
   {
     if ($4.partial && $4.identifierChain.length === 1) {
       suggestTablesOrColumns($4.identifierChain[0].name);
     }
   }
 | 'SHOW' HiveOrImpalaCreate PartialIdentifierOrCursor CleanRegularOrBackTickedSchemaQualifiedName
   {
     suggestKeywords(['TABLE']);
   }
 ;

// TODO: Move into RegularOrBackTickedSchemaQualifiedName
CleanRegularOrBackTickedSchemaQualifiedName
 : 'REGULAR_IDENTIFIER'
   {
     $$ = { identifierChain: [ { name: $1 } ] }
   }
 | RegularOrBackTickedSchemaQualifiedName
   {
     $$ = $1;
   }
 ;

HiveOrImpalaCreate
 : '<hive>CREATE'
 | '<impala>CREATE'
 ;

ShowCurrentStatement
 : 'SHOW' HiveOrImpalaCurrent PartialIdentifierOrCursor
   {
     suggestKeywords([ 'ROLES' ]);
   }
 | 'SHOW' PartialIdentifierOrCursor HiveOrImpalaRoles
   {
     suggestKeywords([ 'CURRENT' ]);
   }
 | 'SHOW' HiveOrImpalaCurrent HiveOrImpalaRoles
 ;

HiveOrImpalaCurrent
 : '<hive>CURRENT'
 | '<impala>CURRENT'
 ;

HiveOrImpalaRoles
 : '<hive>ROLES'
 | '<impala>ROLES'
 ;

ShowDatabasesStatement
 : 'SHOW' HiveOrImpalaDatabasesOrSchemas PartialIdentifierOrCursor
   {
     suggestKeywords(['LIKE']);
   }
 | 'SHOW' HiveOrImpalaDatabasesOrSchemas 'LIKE' SingleQuotedValue
 | 'SHOW' '<impala>DATABASES' SingleQuotedValue
 ;

HiveOrImpalaDatabasesOrSchemas
 : '<hive>DATABASES'
 | '<hive>SCHEMAS'
 | '<impala>DATABASES'
 | '<impala>SCHEMAS'
 ;

ShowFunctionsStatement
 : 'SHOW' '<hive>FUNCTIONS'
 | 'SHOW' '<hive>FUNCTIONS' DoubleQuotedValue
 | 'SHOW' AggregateOrAnalytic PartialIdentifierOrCursor
   {
     suggestKeywords(['FUNCTIONS']);
   }
 | 'SHOW' OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase
 | 'SHOW' PartialIdentifierOrCursor '<impala>FUNCTIONS' OptionalInDatabase
   {
     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   }
 | 'SHOW' OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase PartialIdentifierOrCursor
   {
     if (!$4) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   }
 | 'SHOW' OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase 'LIKE' SingleQuoteValue
 | 'SHOW' AggregateOrAnalytic PartialIdentifierOrCursor OptionalInDatabase 'LIKE' SingleQuoteValue
   {
     suggestKeywords(['FUNCTIONS']);
   }
 | 'SHOW' PartialIdentifierOrCursor '<impala>FUNCTIONS' OptionalInDatabase 'LIKE' SingleQuoteValue
   {
     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   }
 | 'SHOW' OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase PartialIdentifierOrCursor SingleQuoteValue
   {
     if (!$4) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   }
 ;

OptionalAggregateOrAnalytic
 :
   {
     $$ = false;
   }
 | AggregateOrAnalytic
   {
     $$ = true;
   }
 ;

AggregateOrAnalytic
 : '<impala>AGGREGATE'
 | '<impala>ANALYTIC'
 ;

ShowGrantStatement
 : 'SHOW' '<hive>GRANT' OptionalPrincipalName
   {
     if ($3) {
       suggestKeywords(['ON']);
     }
   }
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName 'ON' '<hive>ALL'
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName 'ON' PartialIdentifierOrCursor
   {
     suggestKeywords(['ALL', 'TABLE']);
     suggestTables();
   }
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName 'ON' RegularOrBacktickedIdentifier
 | 'SHOW'  '<hive>GRANT' OptionalPrincipalName 'ON' AnyTable PartialIdentifierOrCursor
   {
     suggestTables();
   }
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName 'ON' AnyTable RegularOrBacktickedIdentifier
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName 'ON' PartialIdentifierOrCursor RegularOrBacktickedIdentifier
   {
     suggestKeywords(['TABLE']);
   }
 | 'SHOW' '<impala>GRANT' PartialIdentifierOrCursor
   {
     suggestKeywords(['ROLE']);
   }
 ;

OptionalPrincipalName
 :
 | 'REGULAR_IDENTIFIER'
 | PartialIdentifierOrCursor
   {
     $$ = true;
   }
 | 'REGULAR_IDENTIFIER' 'CURSOR'
   {
     $$ = true;
   }
 ;


ShowIndexStatement
 : 'SHOW' '<hive>FORMATTED' PartialIdentifierOrCursor
   {
     suggestKeywords(['INDEX', 'INDEXES']);
   }
 | 'SHOW' OptionallyFormattedIndex PartialIdentifierOrCursor
   {
     suggestKeywords(['ON']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' PartialIdentifierOrCursor
   {
     suggestTables();
   }
 | 'SHOW' OptionallyFormattedIndex PartialIdentifierOrCursor RegularOrBacktickedIdentifier
   {
     suggestKeywords(['ON']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier PartialIdentifierOrCursor
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier PartialIdentifierOrCursor RegularOrBacktickedIdentifier
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier AnyFromOrIn PartialIdentifierOrCursor
   {
     suggestDatabases();
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' PartialIdentifierOrCursor AnyFromOrIn RegularOrBacktickedIdentifier
   {
     suggestTablesOrColumns($6);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 ;

OptionallyFormattedIndex
 : '<hive>FORMATTED' IndexOrIndexes
 | PartialIdentifierOrCursor IndexOrIndexes
   {
     suggestKeywords(['FORMATTED']);
   }
 | IndexOrIndexes
 ;

IndexOrIndexes
 : '<hive>INDEX'
 | '<hive>INDEXES'
 ;

// TODO: Merge the first two i.e. PartialIdentifierOrCursor | RegularOrBackTickedSchemaQualifiedName
ShowLocksStatement
 : 'SHOW' '<hive>LOCKS' PartialIdentifierOrCursor
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
     suggestKeywords(['DATABASE', 'SCHEMA']);
   }
 | 'SHOW' '<hive>LOCKS' CleanRegularOrBackTickedSchemaQualifiedName
   {
     if ($3.partial && $3.identifierChain.length === 1) {
       suggestTablesOrColumns($3.identifierChain[0].name)
     }
   }
 | 'SHOW' '<hive>LOCKS' CleanRegularOrBackTickedSchemaQualifiedName PartialIdentifierOrCursor
    {
      suggestKeywords(['EXTENDED', 'PARTITION']);
    }
 | 'SHOW' '<hive>LOCKS' CleanRegularOrBackTickedSchemaQualifiedName '<hive>EXTENDED'
   {
     if ($3.partial && $3.identifierChain.length === 1) {
       suggestTablesOrColumns($3.identifierChain[0].name)
     }
   }
 | 'SHOW' '<hive>LOCKS' CleanRegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' '(' PartitionSpecList ')'
   {
     if ($3.partial && $3.identifierChain.length === 1) {
       suggestTablesOrColumns($3.identifierChain[0].name)
     }
   }
 | 'SHOW' '<hive>LOCKS' CleanRegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' '(' PartitionSpecList ')' PartialIdentifierOrCursor
   {
     suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' '<hive>LOCKS' CleanRegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' '(' PartitionSpecList ')' '<hive>EXTENDED'
   {
     // TODO: Move into CleanRegularOrBackTickedSchemaQualifiedName
     if ($3.partial && $3.identifierChain.length === 1) {
       suggestTablesOrColumns($3.identifierChain[0].name)
     }
   }
 | 'SHOW' '<hive>LOCKS' DatabaseOrSchema PartialIdentifierOrCursor
   {
     suggestDatabases();
   }
 | 'SHOW' '<hive>LOCKS' DatabaseOrSchema RegularOrBacktickedIdentifier
 ;

PartitionSpecList
 : PartitionSpec
 | PartitionSpecList ',' PartitionSpec
 ;

PartitionSpec
 : 'REGULAR_IDENTIFIER' '=' SingleQuotedValue
 ;

ShowPartitionsStatement
 : 'SHOW' '<hive>PARTITIONS' PartialIdentifierOrCursor
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' '<hive>PARTITIONS' CleanRegularOrBackTickedSchemaQualifiedName
   if ($3.partial && $3.identifierChain.length === 1) {
     suggestTablesOrColumns($3.identifierChain[0].name)
   }
 | 'SHOW' '<hive>PARTITIONS' CleanRegularOrBackTickedSchemaQualifiedName PartialIdentifierOrCursor
   {
     suggestKeywords(['PARTITION']);
   }
 | 'SHOW' '<hive>PARTITIONS' CleanRegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' PartitionSpecList
 | 'SHOW' '<impala>PARTITIONS' PartialIdentifierOrCursor
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' '<impala>PARTITIONS' CleanRegularOrBackTickedSchemaQualifiedName
   if ($3.partial && $3.identifierChain.length === 1) {
     suggestTablesOrColumns($3.identifierChain[0].name)
   }
 ;

ShowRoleStatement
 : 'SHOW' HiveOrImpalaRole PartialIdentifierOrCursor
   {
     suggestKeywords(['GRANT']);
   }
 | 'SHOW' HiveOrImpalaRole PartialIdentifierOrCursor HiveRoleOrUser 'REGULAR_IDENTIFIER'
   {
     suggestKeywords(['GRANT']);
   }
 | 'SHOW' HiveOrImpalaRole '<hive>GRANT' PartialIdentifierOrCursor
   {
     suggestKeywords(['ROLE', 'USER']);
   }
 | 'SHOW' HiveOrImpalaRole '<hive>GRANT' PartialIdentifierOrCursor 'REGULAR_IDENTIFIER'
   {
     suggestKeywords(['ROLE', 'USER']);
   }
 | 'SHOW' HiveOrImpalaRole '<hive>GRANT' HiveRoleOrUser 'REGULAR_IDENTIFIER'
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' PartialIdentifierOrCursor
   {
     suggestKeywords(['GROUP']);
   }
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' PartialIdentifierOrCursor 'REGULAR_IDENTIFIER'
   {
     suggestKeywords(['GROUP']);
   }
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' '<impala>GROUP' 'REGULAR_IDENTIFIER'
 ;

HiveRoleOrUser
 : '<hive>ROLE'
 | '<hive>USER'
 ;

HiveOrImpalaRole
 : '<hive>ROLE'
 | '<impala>ROLE'
 ;

ShowRolesStatement
 : 'SHOW' '<impala>ROLES'
 ;

ShowTableStatement
 : 'SHOW' '<hive>TABLE' PartialIdentifierOrCursor
   {
     suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase PartialIdentifierOrCursor
    {
      if ($4) {
        suggestKeywords(['LIKE']);
      } else {
        suggestKeywords(['FROM', 'IN', 'LIKE']);
      }
    }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue
 | 'SHOW' '<hive>TABLE' PartialIdentifierOrCursor OptionalFromDatabase 'LIKE' SingleQuotedValue
 | 'SHOW' '<hive>TABLE' PartialIdentifierOrCursor OptionalFromDatabase PartialIdentifierOrCursor SingleQuotedValue
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue PartialIdentifierOrCursor
    {
      suggestKeywords(['PARTITION']);
    }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
 | 'SHOW' '<hive>TABLE' PartialIdentifierOrCursor OptionalFromDatabase 'LIKE' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
   {
     suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase PartialIdentifierOrCursor SingleQuotedValue '<hive>PARTITION' PartitionSpecList
   {
     suggestKeywords(['LIKE']);
   }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue PartialIdentifierOrCursor PartitionSpecList
   {
     suggestKeywords(['PARTITION']);
   }
 | 'SHOW' '<impala>TABLE' PartialIdentifierOrCursor
   {
     suggestKeywords(['STATS']);
   }
 | 'SHOW' '<impala>TABLE' '<impala>STATS' PartialIdentifierOrCursor
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' '<impala>TABLE' '<impala>STATS' CleanRegularOrBackTickedSchemaQualifiedName
   if ($3.partial && $3.identifierChain.length === 1) {
     suggestTablesOrColumns($3.identifierChain[0].name)
   }
 ;

OptionalFromDatabase
 :
   {
     $$ = false;
   }
 | FromOrIn RegularOrBacktickedIdentifier
   {
     $$ = true;
   }
 | FromOrIn PartialIdentifierOrCursor
   {
     $$ = true;
     suggestDatabases();
   }
 ;

FromOrIn
 : 'FROM'
 | '<hive>IN'
 ;

ShowTablesStatement
 : 'SHOW' HiveOrImpalaTables OptionalInDatabase
 | 'SHOW' HiveOrImpalaTables OptionalInDatabase PartialIdentifierOrCursor
   {
     if (!$3) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   }
 | 'SHOW' HiveOrImpalaTables OptionalInDatabase SingleQuotedValue
 | 'SHOW' HiveOrImpalaTables OptionalInDatabase 'LIKE' SingleQuotedValue
 ;

OptionalInDatabase
 :
   {
     $$ = false;
   }
 | HiveOrImpalaIn PartialIdentifierOrCursor
   {
     $$ = true;
     suggestDatabases();
   }
 | HiveOrImpalaIn RegularOrBacktickedIdentifier
   {
     $$ = true;
   }
 ;

HiveOrImpalaTables
 : '<hive>TABLES'
 | '<impala>TABLES'
 ;

HiveOrImpalaIn
 : '<hive>IN'
 | '<impala>IN'
 ;

ShowTblPropertiesStatement
 : 'SHOW' '<hive>TBLPROPERTIES' PartialIdentifierOrCursor
   {
     suggestTables();
   }
 ;

ShowTransactionsStatement
 : 'SHOW' '<hive>TRANSACTIONS'
 ;

OptionalIfNotExists
 :
 | 'IF' PartialIdentifierOrCursor
   {
     suggestKeywords(['NOT EXISTS']);
   }
 | 'IF' 'NOT' PartialIdentifierOrCursor
   {
     suggestKeywords(['EXISTS']);
   }
 | 'IF' 'NOT' 'EXISTS'
 | 'CURSOR'
   {
     suggestKeywords(['IF NOT EXISTS']);
   }
 ;

Comment
 : HiveOrImpalaComment SINGLE_QUOTE
 | HiveOrImpalaComment SINGLE_QUOTE VALUE
 | HiveOrImpalaComment SINGLE_QUOTE VALUE SINGLE_QUOTE
 ;

HivePropertyAssignmentList
 : HivePropertyAssignment
 | HivePropertyAssignmentList ',' HivePropertyAssignment
 ;

HivePropertyAssignment
 : 'REGULAR_IDENTIFIER' '=' 'REGULAR_IDENTIFIER'
 | SINGLE_QUOTE VALUE SINGLE_QUOTE '=' SINGLE_QUOTE VALUE SINGLE_QUOTE
 ;

HiveDbProperties
 : '<hive>WITH' 'DBPROPERTIES' '(' HivePropertyAssignmentList ')'
 | '<hive>WITH' 'DBPROPERTIES'
 | '<hive>WITH' 'CURSOR'
   {
     suggestKeywords(['DBPROPERTIES']);
   }
 ;

DatabaseDefinitionOptionals
 : DatabaseDefinitionOptional
 | DatabaseDefinitionOptional DatabaseDefinitionOptional
 | DatabaseDefinitionOptional DatabaseDefinitionOptional DatabaseDefinitionOptional
 ;

DatabaseDefinitionOptional
 : Comment
   {
     parser.yy.afterComment = true;
   }
 | HdfsLocation
   {
     parser.yy.afterHdfsLocation = true;
   }
 | HiveDbProperties
   {
     parser.yy.afterHiveDbProperties = true;
   }
 ;

CleanUpDatabaseConditions
 : /* empty */
   {
     delete parser.yy.afterComment;
     delete parser.yy.afterHdfsLocation;
     delete parser.yy.afterHiveDbProperties;
   }
 ;

DatabaseDefinition
 : AnyCreate DatabaseOrSchema OptionalIfNotExists
 | AnyCreate DatabaseOrSchema OptionalIfNotExists 'REGULAR_IDENTIFIER'
 | AnyCreate DatabaseOrSchema OptionalIfNotExists 'REGULAR_IDENTIFIER' 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['COMMENT', 'LOCATION', 'WITH DBPROPERTIES']);
     } else if (isImpala()) {
       suggestKeywords(['COMMENT', 'LOCATION']);
     }
   }
 | AnyCreate DatabaseOrSchema OptionalIfNotExists 'REGULAR_IDENTIFIER' CleanUpDatabaseConditions DatabaseDefinitionOptionals error
   // For the HDFS open single quote completion
 | AnyCreate DatabaseOrSchema OptionalIfNotExists 'REGULAR_IDENTIFIER' CleanUpDatabaseConditions DatabaseDefinitionOptionals 'CURSOR'
   {
     var keywords = [];
     if (! parser.yy.afterComment) {
       keywords.push('COMMENT');
     }
     if (! parser.yy.afterHdfsLocation) {
       keywords.push('LOCATION');
     }
     if (! parser.yy.afterHiveDbProperties && isHive()) {
       keywords.push('WITH DBPROPERTIES');
     }
     if (keywords.length > 0) {
       suggestKeywords(keywords);
     }
   }
 ;

TableDefinition
 : AnyCreate TableScope AnyTable 'REGULAR_IDENTIFIER' TableElementList HdfsLocation
 | AnyCreate PartialIdentifierOrCursor AnyTable 'REGULAR_IDENTIFIER' TableElementList
    {
      if (isHive() || isImpala()) {
        suggestKeywords(['EXTERNAL']);
      }
    }
 | AnyCreate PartialIdentifierOrCursor AnyTable 'REGULAR_IDENTIFIER'
    {
      if (isHive() || isImpala()) {
        suggestKeywords(['EXTERNAL']);
      }
    }
 | AnyCreate PartialIdentifierOrCursor AnyTable
    {
      if (isHive() || isImpala()) {
        suggestKeywords(['EXTERNAL']);
      }
    }
 | AnyCreate TableScope AnyTable 'REGULAR_IDENTIFIER' TableElementList PartialIdentifierOrCursor
   {
     if (isHive() || isImpala()) {
       suggestKeywords(['LOCATION']);
     }
   }
 | AnyCreate AnyTable 'REGULAR_IDENTIFIER' TableElementList
 ;

TableScope
 : '<hive>EXTERNAL'
 | '<impala>EXTERNAL'
 ;

TableElementList
 : '(' TableElements ')'
 ;

TableElements
 : TableElement
 | TableElements ',' TableElement
 ;

TableElement
 : ColumnDefinition
 ;

ColumnDefinition
 : 'REGULAR_IDENTIFIER' PrimitiveType
 | 'REGULAR_IDENTIFIER' PartialIdentifierOrCursor
   {
     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   }
 | 'REGULAR_IDENTIFIER' PartialIdentifierOrCursor ColumnDefinitionError error
   // error here is because it expects closing ')'
 ;

ColumnDefinitionError
 : /* empty, on error we should still suggest the keywords */
   {
     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   }
 ;

HdfsLocation
 : HiveOrImpalaLocation HdfsPath
 ;

HiveOrImpalaLocation
 : '<hive>LOCATION'
 | '<impala>LOCATION'
 ;

HiveOrImpalaComment
 : '<hive>COMMENT'
 | '<impala>COMMENT'
 ;

HdfsPath
 : 'HDFS_START_QUOTE' 'HDFS_PATH' 'HDFS_END_QUOTE'
 | 'HDFS_START_QUOTE' 'HDFS_PATH' 'PARTIAL_CURSOR' 'HDFS_PATH' 'HDFS_END_QUOTE'
    {
      suggestHdfs({ path: $2 });
    }
 | 'HDFS_START_QUOTE' 'HDFS_PATH' 'PARTIAL_CURSOR' 'HDFS_END_QUOTE'
   {
     suggestHdfs({ path: $2 });
   }
 | 'HDFS_START_QUOTE' 'HDFS_PATH' 'PARTIAL_CURSOR'
    {
      suggestHdfs({ path: $2 });
    }
 | 'HDFS_START_QUOTE' 'PARTIAL_CURSOR' 'HDFS_END_QUOTE'
   {
     suggestHdfs({ path: '' });
   }
 | 'HDFS_START_QUOTE' 'PARTIAL_CURSOR'
    {
      suggestHdfs({ path: '' });
    }
 ;

AnyDot
 : '.'
 | '<impala>.'
 | '<hive>.'
 ;

// TODO: Support | DECIMAL(precision, scale)  -- (Note: Available in Hive 0.13.0 and later)
PrimitiveType
 : 'TINYINT'
 | 'SMALLINT'
 | 'INT'
 | 'BIGINT'
 | 'BOOLEAN'
 | 'FLOAT'
 | 'DOUBLE'
 | 'STRING'
 | 'DECIMAL'
 | 'CHAR'
 | 'VARCHAR'
 | 'TIMESTAMP'
 | '<hive>BINARY'
 | '<hive>DATE'
 ;

QueryExpression
 : 'SELECT' CleanUpSelectConditions SelectList TableExpression
   {
     linkTablePrimaries();
   }
 | 'SELECT' CleanUpSelectConditions SelectList
 ;

TableExpression
 : FromClause
 | FromClause SelectConditionList
 ;

CleanUpSelectConditions
 : /* empty */
   {
     delete parser.yy.afterGroupBy;
     delete parser.yy.afterLimit;
     delete parser.yy.afterOrderBy;
     delete parser.yy.afterWhere;
   }
 ;

FromClause
 : 'FROM' TableReferenceList
 | 'FROM' PartialIdentifierOrCursor
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 ;

SelectConditionList
 : SelectCondition
 | SelectConditionList SelectCondition
 ;

SelectCondition
 : WhereClause
   {
     parser.yy.afterWhere = true;
   }
 | GroupByClause
   {
     parser.yy.afterGroupBy = true;
     delete parser.yy.result.suggestStar;
   }
 | OrderByClause
   {
     parser.yy.afterOrderBy = true;
     delete parser.yy.result.suggestStar;
   }
 | LimitClause
   {
     parser.yy.afterLimit = true;
     delete parser.yy.result.suggestStar;
   }
 | 'CURSOR'
   {
     var keywords = [];
     if (!parser.yy.afterGroupBy) {
       keywords.push('GROUP BY');
     }
     if (!parser.yy.afterGroupBy && !parser.yy.afterWhere && !parser.yy.afterOrderBy && !parser.yy.afterLimit) {
       keywords.push('JOIN');
       if (isHive()) {
         keywords.push('LATERAL');
       }
     }
     if (!parser.yy.afterLimit) {
       keywords.push('LIMIT');
     }
     if (!parser.yy.afterOrderBy) {
       keywords.push('ORDER BY');
     }
     if (!parser.yy.afterWhere) {
       keywords.push('WHERE');
     }
     if (keywords.length > 0) {
       suggestKeywords(keywords);
     }
   }
 ;

WhereClause
 : 'WHERE' SearchCondition
 | 'WHERE' 'CURSOR'
   {
     suggestColumns();
   }
 ;

SearchCondition
 : BooleanValueExpression
 ;

BooleanValueExpression
 : BooleanTerm
 | BooleanValueExpression 'OR' BooleanTerm
 ;

BooleanTerm
 : BooleanFactor
 | BooleanFactor 'AND' 'CURSOR'
   {
     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   }
 | BooleanFactor 'AND' BooleanTerm
 ;

BooleanFactor
 : 'NOT' BooleanTest
 | BooleanTest
 ;

BooleanTest
 : Predicate
 | Predicate CompOp Predicate
 | Predicate CompOp AnyCursor
   {
     if (typeof $1 !== 'undefined') {
       suggestValues({ identifierChain: $1});
     }
   }
 | Predicate 'IS' TruthValue
 | Predicate 'IS' 'NOT' TruthValue
 ;

Predicate
 : ParenthesizedBooleanValueExpression
 | NonParenthesizedValueExpressionPrimary
   {
     $$ = $1;
   }
 ;

CompOp
 : '='
 | '<>'
 | '<='
 | '>='
 | '<'
 | '>'
 ;

ParenthesizedBooleanValueExpression
 : '(' BooleanValueExpression ')'
 | '(' AnyCursor // Could be either (| or ( |
   {
     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   }
 ;

SignedInteger
 : 'UNSIGNED_INTEGER'
 | '-' 'UNSIGNED_INTEGER'
 ;

SingleQuotedValue
 : 'SINGLE_QUOTE' 'VALUE' 'SINGLE_QUOTE'
 ;

DoubleQuotedValue
 : 'DOUBLE_QUOTE' 'VALUE' 'DOUBLE_QUOTE'
   {
     $$ = $2;
   }
 ;

NonParenthesizedValueExpressionPrimary
 : ColumnReference // TODO: Expand with more choices
   {
     $$ = $1;
   }
 | SignedInteger
 | SingleQuotedValue
 ;

ColumnReference
 : BasicIdentifierChain
   {
     $$ = $1;
   }
 ;

BasicIdentifierChain
 : InitIdentifierChain IdentifierChain
   {
     $$ = parser.yy.identifierChain;
     delete parser.yy.identifierChain;
   }
 ;

InitIdentifierChain
 : /* empty */
   {
     parser.yy.identifierChain = [];
   }
 ;

IdentifierChain
 : Identifier
 | IdentifierChain AnyDot 'PARTIAL_CURSOR'
   {
     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   }
 | IdentifierChain AnyDot Identifier
 ;

Identifier
 : ColumnIdentifier
   {
     parser.yy.identifierChain.push($1);
   }
 | ColumnIdentifier 'PARTIAL_CURSOR'
   {
     suggestColumns();
   }
 | '"' 'REGULAR_IDENTIFIER' '"'
   {
     parser.yy.identifierChain.push({ name: $2 });
   }
 ;

AnyGroup
 : 'GROUP'
 | '<hive>GROUP'
 | '<impala>GROUP'
 ;

GroupByClause
 : AnyGroup 'BY' ColumnList
 | AnyGroup PartialIdentifierOrCursor
   {
     suggestKeywords(['BY']);
   }
 ;

OrderByClause
 : 'ORDER' 'BY' ColumnList
 | 'ORDER' PartialIdentifierOrCursor
   {
     suggestKeywords(['BY']);
   }
 ;

LimitClause
 : 'LIMIT' 'UNSIGNED_INTEGER'
 | 'LIMIT' PartialIdentifierOrCursor
   {
     suggestNumbers([1, 5, 10]);
   }
 ;

SelectList
 : ColumnList
 | ColumnList PartialIdentifierOrCursor
   {
     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   }
 | '*' PartialIdentifierOrCursor
   {
     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   }
 | '*'
 ;

ColumnList
 : DerivedColumn
 | ColumnList ',' DerivedColumn
 ;

ColumnIdentifier
 : 'REGULAR_IDENTIFIER'
   {
     $$ = { name: $1 }
   }
 | 'REGULAR_IDENTIFIER' '[' DoubleQuotedValue ']'
   {
     $$ = { name: $1, key: '"' + $3 + '"' }
   }
 | 'REGULAR_IDENTIFIER' '[' 'UNSIGNED_INTEGER' ']'
   {
     $$ = { name: $1, key: parseInt($3) }
   }
 | 'REGULAR_IDENTIFIER' '[' ']'
   {
     $$ = { name: $1, key: null }
   }
 ;

DerivedColumn
 : ColumnIdentifier
 | ColumnIdentifier AnyDot PartialIdentifierOrPartialCursor
   {
     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $1.key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $1 ]
     });
   }
 | ColumnIdentifier 'PARTIAL_CURSOR'
   {
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | ColumnIdentifier AnyDot '*'
 | ColumnIdentifier AnyDot DerivedColumnChain
   {
      delete parser.yy.derivedColumnChain;
   }
 | ColumnIdentifier AnyDot DerivedColumnChain '<impala>.' 'PARTIAL_CURSOR'
   {
      parser.yy.derivedColumnChain.unshift($1);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    }
 | ColumnIdentifier AnyDot DerivedColumnChain '<hive>.' 'PARTIAL_CURSOR'
   {
      parser.yy.derivedColumnChain.unshift($1);
      suggestColumns({
        identifierChain: parser.yy.derivedColumnChain
      });
      delete parser.yy.derivedColumnChain;
    }
 | AnyCursor
   {
     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 ;

DerivedColumnChain
 : ColumnIdentifier
   {
     if (typeof parser.yy.derivedColumnChain === 'undefined') {
       parser.yy.derivedColumnChain = [];
     }
     parser.yy.derivedColumnChain.push($1);
     $$ = parser.yy.derivedColumnChain;
   }
 | DerivedColumnChain AnyDot ColumnIdentifier
   {
     parser.yy.derivedColumnChain.push($3);
     $$ = parser.yy.derivedColumnChain;
   }
 ;

TableReferenceList
 : TableReference
 | TableReferenceList ',' TableReference
 ;

TableReference
 : TablePrimaryOrJoinedTable
 ;

TablePrimaryOrJoinedTable
 : TablePrimary
   {
     if ($1.partial) {
       if ($1.identifierChain.length === 1) {
         suggestTablesOrColumns($1.identifierChain[0].name);
       } else if ($1.identifierChain.length === 0) {
         suggestTables();
         suggestDatabases({ appendDot: true });
       }
     } else if (typeof $1.identifierChain !== 'undefined') {
       addTablePrimary($1);
     }
   }
 | LateralViewDefinition
   {
     addTablePrimary($1);
   }
 | JoinedTable
 ;

LateralViewDefinition
 :'REGULAR_IDENTIFIER' LateralViews
   {
     $$ = { identifierChain: [ { name: $1 } ], lateralViews: $2 }
   }
 | 'REGULAR_IDENTIFIER' 'REGULAR_IDENTIFIER' LateralViews
   {
     $$ = { identifierChain: [ { name: $1 } ], alias: $2, lateralViews: $3 };
   }
 ;

TablePrimary
 : LocalOrSchemaQualifiedName
 ;

RegularOrBacktickedIdentifier
 : 'REGULAR_IDENTIFIER'
 | 'BACKTICK' 'VALUE' 'BACKTICK'
   {
     $$ = $1;
   }
 ;

RegularOrBackTickedSchemaQualifiedName
 : 'REGULAR_IDENTIFIER' AnyDot 'REGULAR_IDENTIFIER'
   {
     $$ = { identifierChain: [ { name: $1 }, { name: $3 } ] }
   }
 | 'BACKTICK' 'VALUE' 'BACKTICK' AnyDot 'REGULAR_IDENTIFIER'
   {
     $$ = { identifierChain: [ { name: $2 }, { name: $5 } ] }
   }
 | 'REGULAR_IDENTIFIER' AnyDot 'BACKTICK' 'VALUE' 'BACKTICK'
   {
     $$ = { identifierChain: [ { name: $1 }, { name: $4 } ] }
   }
 | 'BACKTICK' 'VALUE' 'BACKTICK' AnyDot 'BACKTICK' 'VALUE' 'BACKTICK'
   {
     $$ = { identifierChain: [ { name: $2 }, { name: $6 } ] }
   }
 | 'BACKTICK' 'VALUE' 'BACKTICK' AnyDot 'BACKTICK' 'PARTIAL_VALUE'
   {
     $$ = { partial: true, identifierChain: [ { name: $2 } ] };
   }
 | 'REGULAR_IDENTIFIER' AnyDot PartialIdentifierOrPartialCursor
   {
     $$ = { partial: true, identifierChain: [ { name: $1 } ] };
   }
 | 'BACKTICK' 'VALUE' 'BACKTICK' AnyDot 'PARTIAL_CURSOR'
   {
     $$ = { partial: true, identifierChain: [ { name: $2 } ] };
   }
 | 'BACKTICK' 'PARTIAL_VALUE'
   {
     $$ = { partial: true, identifierChain: [ ] };
   }
 | 'BACKTICK' 'VALUE' 'BACKTICK'
   {
     $$ = { identifierChain: [ { name: $2 } ] }
   }
 ;

LocalOrSchemaQualifiedName
 : 'REGULAR_IDENTIFIER'
   {
     $$ = { identifierChain: [ { name: $1 } ] }
   }
 | 'REGULAR_IDENTIFIER' 'REGULAR_IDENTIFIER'
   {
     $$ = { identifierChain: [ { name: $1 } ], alias: $2 };
   }
 | RegularOrBackTickedSchemaQualifiedName
 | RegularOrBackTickedSchemaQualifiedName 'REGULAR_IDENTIFIER'
   {
     $$ = { identifierChain: $1.identifierChain, alias: $2 }
   }
 ;

// TODO: '<hive>[pos]explode' '(' 'CURSOR' possible?
userDefinedTableGeneratingFunction
 : '<hive>explode' '(' DerivedColumnChain ')'
   {
     delete parser.yy.derivedColumnChain;
     $$ = { function: $1, expression: $3 }
   }
 | '<hive>explode' '(' PartialIdentifierOrPartialCursor error
 | '<hive>posexplode' '(' DerivedColumnChain ')'
    {
      delete parser.yy.derivedColumnChain;
      $$ = { function: $1, expression: $3 }
    }
 | '<hive>posexplode' '(' PartialIdentifierOrPartialCursor error
 ;

LateralViews
 : LateralView
   {
     if (typeof parser.yy.currentViews === 'undefined') {
       parser.yy.currentViews = [];
     }
     parser.yy.currentViews.push($1);
     $$ = parser.yy.currentViews;
   }
 | LateralViews LateralView
   {
     parser.yy.currentViews.push($2);
     $$ = parser.yy.currentViews;
   }
 ;

LateralView
 : '<hive>LATERAL' 'VIEW' userDefinedTableGeneratingFunction 'REGULAR_IDENTIFIER' LateralViewColumnAliases
   {
     $$ = { udtf: $3, tableAlias: $4, columnAliases: $5 }
   }
 | '<hive>LATERAL' 'VIEW' userDefinedTableGeneratingFunction LateralViewColumnAliases
    {
      $$ = { udtf: $3, columnAliases: $4 }
    }
 | '<hive>LATERAL' 'VIEW' userDefinedTableGeneratingFunction 'REGULAR_IDENTIFIER' PartialIdentifierOrCursor
   {
     suggestKeywords(['AS']);
   }
 | '<hive>LATERAL' 'VIEW' userDefinedTableGeneratingFunction PartialIdentifierOrCursor
   {
     suggestKeywords(['AS']);
   }
 | '<hive>LATERAL' 'VIEW' PartialIdentifierOrCursor
   {
     suggestKeywords(['explode', 'posexplode']);
   }
 | '<hive>LATERAL' PartialIdentifierOrCursor
   {
     suggestKeywords(['VIEW']);
   }
 ;

LateralViewColumnAliases
 : '<hive>AS' 'REGULAR_IDENTIFIER'
   {
     $$ = [ $2 ]
   }
 | '<hive>AS' '(' 'REGULAR_IDENTIFIER' ',' 'REGULAR_IDENTIFIER' ')'
   {
     $$ = [ $3, $5 ]
   }
 ;

JoinedTable
 : TableReference 'JOIN' TableReference JoinSpecification
 | TableReference 'JOIN' TableReference 'CURSOR'
   {
     suggestKeywords(['ON']);
   }
 | TableReference 'JOIN' 'CURSOR'
   {
     suggestTables({});
     suggestDatabases({ appendDot: true });
   }
 ;

JoinSpecification
 : JoinCondition
 ;

JoinCondition
 : 'ON' SearchCondition
 ;

%%

var isHive = function () {
  return parser.yy.dialect === 'hive';
}

var isImpala = function () {
  return parser.yy.dialect === 'impala';
}


var prioritizeSuggestions = function () {
  parser.yy.result.lowerCase = parser.yy.lowerCase || false;
  if (typeof parser.yy.result.suggestIdentifiers !== 'undefined' &&  parser.yy.result.suggestIdentifiers.length > 0) {
    if (!parser.yy.keepColumns) {
     delete parser.yy.result.suggestColumns;
    }
    delete parser.yy.result.suggestTables;
    delete parser.yy.result.suggestDatabases;
    return;
  }
  if (typeof parser.yy.result.suggestColumns !== 'undefined') {
    if (typeof parser.yy.result.suggestColumns.table === 'undefined') {
      delete parser.yy.result.suggestColumns;
    } else {
      delete parser.yy.result.suggestTables;
      delete parser.yy.result.suggestDatabases;
    }
    return;
  }
}


/**
 * Impala supports referencing maps and arrays in the the table reference list i.e.
 *
 *  SELECT m['foo'].bar.| FROM someDb.someTable t, t.someMap m;
 *
 * From this the tablePrimaries would look like:
 *
 * [ { alias: 't', identifierChain: [ { name: 'someDb' }, { name: 'someTable' } ] },
 *   { alias: 'm', identifierChain: [ { name: 't' }, { name: 'someMap' } ] } ]
 *
 * with an identifierChain from the select list:
 *
 * [ { name: 'm', key: 'foo' }, { name: 'bar' } ]
 *
 * Calling this would return an expanded identifierChain, given the above it would be:
 *
 * [ { name: 't' }, { name: 'someMap', key: 'foo' }, { name: 'bar' } ]
 */
parser.expandImpalaIdentifierChain = function (tablePrimaries, identifierChain) {
  if (typeof identifierChain === 'undefined' || identifierChain.length === 0) {
    return identifierChain;
  }
  var firstIdentifier = identifierChain[0].name;

  foundPrimary = tablePrimaries.filter(function (tablePrimary) {
    return tablePrimary.alias === firstIdentifier;
  });

  if (foundPrimary.length === 1) {
    var firstPart = foundPrimary[0].identifierChain.concat();
    var secondPart = identifierChain.slice(1);
    if (typeof identifierChain[0].key !== 'undefined') {
      var lastFromFirst = firstPart.pop();
      firstPart.push({
        name: lastFromFirst.name,
        key: identifierChain[0].key
      })
    }
    return firstPart.concat(secondPart);
  }

  return identifierChain;
};

parser.expandLateralViews = function (tablePrimaries, identifierChain) {
  var firstIdentifier = identifierChain[0];
  var identifierChainParts = [];
  tablePrimaries.forEach(function (tablePrimary) {
    if (typeof tablePrimary.lateralViews !== 'undefined') {
      tablePrimary.lateralViews.reverse().forEach(function (lateralView) {
        if (firstIdentifier.name === lateralView.tableAlias && identifierChain.length > 1) {
          identifierChain.shift();
          firstIdentifier = identifierChain[0];
        } else if (firstIdentifier.name === lateralView.tableAlias && identifierChain.length === 1 && typeof parser.yy.result.suggestColumns !== 'undefined') {
          if (typeof parser.yy.result.suggestIdentifiers === 'undefined') {
            parser.yy.result.suggestIdentifiers = [];
          }
          lateralView.columnAliases.forEach(function (columnAlias) {
            parser.yy.result.suggestIdentifiers.push({ name: columnAlias, type: 'alias' });
          });
          delete parser.yy.result.suggestColumns;
          return identifierChain;
        }
        if (lateralView.columnAliases.indexOf(firstIdentifier.name) !== -1) {
          if (lateralView.columnAliases.length === 2 && lateralView.udtf.function.toLowerCase() === 'explode' && firstIdentifier.name === lateralView.columnAliases[0]) {
            identifierChain[0] = { name: 'key' };
          } else if (lateralView.columnAliases.length === 2 && lateralView.udtf.function.toLowerCase() === 'explode' && firstIdentifier.name === lateralView.columnAliases[1]) {
            identifierChain[0] = { name: 'value' };
          } else {
            identifierChain[0] = { name: 'item' };
          }
          identifierChain = lateralView.udtf.expression.concat(identifierChain);
          firstIdentifier = identifierChain[0];
        }
      });
    }
  });
  return identifierChain;
};

var linkSuggestion = function (suggestion, isColumnSuggestion) {
  var identifierChain = suggestion.identifierChain;
  var tablePrimaries = parser.yy.latestTablePrimaries;
  // Impala can have references to maps or array, i.e. FROM table t, t.map m
  // We need to replace those in the identifierChain
  if (isImpala()) {
    identifierChain = parser.expandImpalaIdentifierChain(tablePrimaries, identifierChain);
    suggestion.identifierChain = identifierChain;
  }

  // Expand exploded views in the identifier chain
  if (isHive()) {
    if (identifierChain.length === 0) {
      if (typeof parser.yy.result.suggestIdentifiers === 'undefined') {
        parser.yy.result.suggestIdentifiers = [];
      }
      tablePrimaries.forEach(function (tablePrimary) {
        if (typeof tablePrimary.lateralViews !== 'undefined') {
          tablePrimary.lateralViews.forEach(function (lateralView) {
            if (typeof lateralView.tableAlias !== 'undefined') {
              parser.yy.result.suggestIdentifiers.push({ name: lateralView.tableAlias + '.', type: 'alias' });
              parser.yy.keepColumns = true;
            }
            lateralView.columnAliases.forEach(function (columnAlias) {
              parser.yy.result.suggestIdentifiers.push({ name: columnAlias, type: 'alias' });
              parser.yy.keepColumns = true;
            });
          });
        }
      });
      if (parser.yy.result.suggestIdentifiers.length === 0) {
        delete parser.yy.result.suggestIdentifiers;
      }
    } else {
      identifierChain = parser.expandLateralViews(tablePrimaries, identifierChain);
      suggestion.identifierChain = identifierChain;
    }
  }

  // IdentifierChain contains a possibly started identifier or empty, example: a.b.c = ['a', 'b', 'c']
  // Reduce the tablePrimaries to the one that matches the first identifier if found
  if (identifierChain.length > 0) {
    var foundTable = tablePrimaries.filter(function (tablePrimary) {
      return identifierChain[0].name === tablePrimary.alias;
    });

    var dbAndTable = false;
    if (foundTable.length === 0) {
      foundTable = tablePrimaries.filter(function (tablePrimary) {
        if (identifierChain[0].name === tablePrimary.identifierChain[0].name) {
          if (identifierChain.length > 1 && tablePrimary.identifierChain.length > 1) {
            dbAndTable = identifierChain[1].name === tablePrimary.identifierChain[1].name;
          }
          return true;
        }
        return false;
      })
    }

    if (foundTable.length === 1) {
      tablePrimaries = foundTable;
      identifierChain.shift();
      if (dbAndTable) {
        identifierChain.shift();
      }
    }
  }

  if (identifierChain.length == 0) {
    delete suggestion.identifierChain;
  }

  if (tablePrimaries.length === 1) {
    if (tablePrimaries[0].identifierChain.length == 2) {
      suggestion.database = tablePrimaries[0].identifierChain[0].name;
      suggestion.table = tablePrimaries[0].identifierChain[1].name;
    } else {
      suggestion.table = tablePrimaries[0].identifierChain[0].name;
    }
  } else if (tablePrimaries.length > 1 && isColumnSuggestion) {
    // Table identifier is required for column completion
    delete parser.yy.result.suggestColumns;
    suggestTablePrimariesAsIdentifiers();
  }
}

var suggestTablePrimariesAsIdentifiers = function () {
  if (typeof parser.yy.result.suggestIdentifiers === 'undefined') {
    parser.yy.result.suggestIdentifiers = [];
  }
  parser.yy.latestTablePrimaries.forEach(function (tablePrimary) {
    if (typeof tablePrimary.alias !== 'undefined') {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.alias + '.', type: 'alias' });
    } else {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.identifierChain[0].name + '.', type: 'table' });
    }
  });
  if (parser.yy.result.suggestIdentifiers.length === 0) {
    delete parser.yy.result.suggestIdentifiers;
  }
}

var linkTablePrimaries = function () {
   if (!parser.yy.cursorFound) {
     return;
   }
   if (typeof parser.yy.result.suggestColumns !== 'undefined') {
     linkSuggestion(parser.yy.result.suggestColumns, true);
   }
   if (typeof parser.yy.result.suggestValues !== 'undefined') {
     linkSuggestion(parser.yy.result.suggestValues, false);
     if (parser.yy.latestTablePrimaries.length > 1) {
       suggestTablePrimariesAsIdentifiers();
     }
   }
}

var addTablePrimary = function (ref) {
  if (typeof parser.yy.latestTablePrimaries === 'undefined') {
    parser.yy.latestTablePrimaries = [];
  }
  parser.yy.latestTablePrimaries.push(ref);
}

var suggestNumbers = function (numbers) {
  parser.yy.result.suggestNumbers = numbers;
}

var suggestDdlAndDmlKeywords = function () {
  var keywords = ['ALTER', 'CREATE', 'DELETE', 'DESCRIBE', 'DROP', 'EXPLAIN', 'INSERT', 'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE'];

  if (parser.yy.dialect == 'hive') {
    keywords = keywords.concat(['ANALYZE', 'EXPORT', 'IMPORT', 'LOAD', 'MSCK']);
  }

  if (parser.yy.dialect == 'impala') {
    keywords = keywords.concat(['COMPUTE', 'INVALIDATE', 'LOAD', 'REFRESH']);
  }
  keywords.sort();

  suggestKeywords(keywords);
}


var suggestKeywords = function (keywords) {
  parser.yy.result.suggestKeywords = keywords;
}

var suggestTablesOrColumns = function (identifier) {
  if (typeof parser.yy.latestTablePrimaries == 'undefined') {
    suggestTables({ database: identifier });
    return;
  }
  var tableRef = parser.yy.latestTablePrimaries.filter(function (tablePrimary) {
    return tablePrimary.alias === identifier;
  });
  if (tableRef.length > 0) {
    suggestColumns({ identifierChain: [ { name: identifier } ] });
  } else {
    suggestTables({ database: identifier });
  }
}

var suggestColumns = function (details) {
  parser.yy.result.suggestColumns = details || { identifierChain: [] };
}

var suggestTables = function (details) {
  parser.yy.result.suggestTables = details || {};
}

var suggestDatabases = function (details) {
  parser.yy.result.suggestDatabases = details || {};
}

var suggestHdfs = function (details) {
  parser.yy.result.suggestHdfs = details || {}
}

var suggestValues = function (details) {
  parser.yy.result.suggestValues = details || { identifierChain: [] }
}

var determineCase = function (text) {
  parser.yy.lowerCase = text.toLowerCase() === text;
};

var lexerModified = false;

/**
 * Main parser function
 */
parser.parseSql = function(beforeCursor, afterCursor, dialect) {
  if (dialect === 'generic') {
    dialect = undefined;
  }
  parser.yy.activeDialect = dialect;
  parser.yy.result = {};
  parser.yy.lowerCase = false;

  // Hack to set the inital state of the lexer without first having to hit a token
  // has to be done as the first token found can be dependant on dialect
  if (!lexerModified && typeof dialect !== 'undefined') {
    var originalSetInput = parser.lexer.setInput;
    parser.lexer.setInput = function (input) {
      var lexer = originalSetInput.bind(parser.lexer)(input);
      if (typeof parser.yy.activeDialect !== 'undefined') {
        lexer.begin(parser.yy.activeDialect)
      }
    }
    lexerModified = true;
  }

  var result;
  parser.yy.dialect = dialect;
  try {
    // Add |CURSOR| or |PARTIAL_CURSOR| to represent the different cursor states in the lexer
    result = parser.parse(beforeCursor + (beforeCursor.length == 0 || /.*\s+$/.test(beforeCursor) ? ' \u2020 ' : '\u2021') + afterCursor);
  } catch (err) {
    // On any error try to at least return any existing result
    if (typeof parser.yy.result === 'undefined') {
      throw err;
    }
    result = parser.yy.result;
  }

  if (typeof result.error !== 'undefined' && typeof result.error.expected !== 'undefined') {
    // Remove any expected tokens from other dialects, jison doesn't remove tokens from other lexer states.
    var actualExpected = [];
    result.error.expected.forEach(function (expected) {
      var match = expected.match(/\<([a-z]+)\>(.*)/);
      if (match !== null) {
        if (typeof parser.yy.dialect !== 'undefined' && parser.yy.dialect === match[1]) {
          actualExpected.push(match[2]);
        }
      } else {
        actualExpected.push(expected);
      }
    });
    result.error.expected = actualExpected;
  }

  if (typeof result.error !== 'undefined' && result.error.recoverable) {
    delete result.error;
  }

  return result;
}

/*
 Hive Select syntax from https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Select

 [WITH CommonTableExpression (, CommonTableExpression)*]    (Note: Only available starting with Hive 0.13.0)
 SELECT [ALL | DISTINCT] select_expr, select_expr, ...
 FROM table_reference
 [WHERE where_condition]
 [GROUP BY col_list]
 [CLUSTER BY col_list
   | [DISTRIBUTE BY col_list] [SORT BY col_list]
 ]
 [LIMIT number]
*/