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
%x hdfs DoubleQuotedValue_Complete SingleQuotedValue_Complete backtickedValue
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
<hive>'CROSS'                       { return '<hive>CROSS'; }
<hive>'CURRENT'                     { return '<hive>CURRENT'; }
<hive>'DATA'                        { return '<hive>DATA'; }
<hive>'DATABASES'                   { return '<hive>DATABASES'; }
<hive>'DATE'                        { return '<hive>DATE'; }
<hive>'DESCRIBE'                    { determineCase(yytext); return '<hive>DESCRIBE'; }
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
<hive>\[                            { return '<hive>['; }
<hive>\]                            { return '<hive>]'; }


<impala>'AGGREGATE'                 { return '<impala>AGGREGATE'; }
<impala>'ANALYTIC'                  { return '<impala>ANALYTIC'; }
<impala>'ANTI'                      { return '<impala>ANTI'; }
<impala>'COLUMN'                    { return '<impala>COLUMN'; }
<impala>'COMMENT'                   { return '<impala>COMMENT'; }
<impala>'CREATE'                    { determineCase(yytext); return '<impala>CREATE'; }
<impala>'CURRENT'                   { return '<impala>CURRENT'; }
<impala>'DATA'                      { return '<impala>DATA'; }
<impala>'DATABASES'                 { return '<impala>DATABASES'; }
<impala>'DESCRIBE'                  { determineCase(yytext); return '<impala>DESCRIBE'; }
<impala>'EXTERNAL'                  { return '<impala>EXTERNAL'; }
<impala>'FIRST'                     { return '<impala>FIRST'; }
<impala>'FORMATTED'                 { return '<impala>FORMATTED'; }
<impala>'FUNCTION'                  { return '<impala>FUNCTION'; }
<impala>'FUNCTIONS'                 { return '<impala>FUNCTIONS'; }
<impala>'GRANT'                     { return '<impala>GRANT'; }
<impala>'GROUP'                     { return '<impala>GROUP'; }
<impala>'INCREMENTAL'               { return '<impala>INCREMENTAL'; }
<impala>'INPATH'                    { this.begin('hdfs'); return '<impala>INPATH'; }
<impala>'IN'                        { return '<impala>IN'; }
<impala>'INNER'                     { return '<impala>INNER'; }
<impala>'LAST'                      { return '<impala>LAST'; }
<impala>'LOAD'                      { return '<impala>LOAD'; }
<impala>'LOCATION'                  { this.begin('hdfs'); return '<impala>LOCATION'; }
<impala>'NULLS'                     { return '<impala>NULLS'; }
<impala>'PARTITIONS'                { return '<impala>PARTITIONS'; }
<impala>'RIGHT'                     { return '<impala>RIGHT'; }
<impala>'ROLE'                      { return '<impala>ROLE'; }
<impala>'ROLES'                     { return '<impala>ROLES'; }
<impala>'SCHEMAS'                   { return '<impala>SCHEMAS'; }
<impala>'STATS'                     { return '<impala>STATS'; }
<impala>'TABLE'                     { return '<impala>TABLE'; }
<impala>'TABLES'                    { return '<impala>TABLES'; }

<impala>[.]                         { return '<impala>.'; }
<impala>\[                          { return '<impala>['; }
<impala>\]                          { return '<impala>]'; }

'AND'                               { return 'AND'; }
'AS'                                { return 'AS'; }
'ASC'                               { return 'ASC'; }
'BIGINT'                            { return 'BIGINT'; }
'BOOLEAN'                           { return 'BOOLEAN'; }
'BY'                                { return 'BY'; }
'CHAR'                              { return 'CHAR'; }
'CREATE'                            { determineCase(yytext); return 'CREATE'; }
'DATABASE'                          { return 'DATABASE'; }
'DECIMAL'                           { return 'DECIMAL'; }
'DESC'                              { return 'DESC'; }
'DOUBLE'                            { return 'DOUBLE'; }
'DROP'                              { determineCase(yytext); return 'DROP'; }
'EXISTS'                            { return 'EXISTS'; }
'FALSE'                             { return 'FALSE'; }
'FLOAT'                             { return 'FLOAT'; }
'FROM'                              { return 'FROM'; }
'OUTER'                             { return 'OUTER'; }
'INNER'                             { return 'INNER'; }
'RIGHT'                             { return 'RIGHT'; }
'FULL'                              { return 'FULL'; }
'GROUP'                             { return 'GROUP'; }
'IF'                                { return 'IF'; }
'INT'                               { return 'INT'; }
'INTO'                              { return 'INTO'; }
'IS'                                { return 'IS'; }
'IN'                                { return 'IN'; }
'JOIN'                              { return 'JOIN'; }
'LEFT'                              { return 'LEFT'; }
'LIKE'                              { return 'LIKE'; }
'NOT'                               { return 'NOT'; }
'NOT IN'                            { return 'NOT_IN'; }
'ON'                                { return 'ON'; }
'OR'                                { return 'OR'; }
'ORDER'                             { return 'ORDER'; }
'ROLE'                              { return 'ROLE'; }
'SCHEMA'                            { return 'SCHEMA'; }
'SELECT'                            { determineCase(yytext); return 'SELECT'; }
'SEMI'                              { return 'SEMI'; }
'SET'                               { return 'SET'; }
'SHOW'                              { determineCase(yytext); return 'SHOW'; }
'SMALLINT'                          { return 'SMALLINT'; }
'STRING'                            { return 'STRING'; }
'TABLE'                             { return 'TABLE'; }
'TIMESTAMP'                         { return 'TIMESTAMP'; }
'TINYINT'                           { return 'TINYINT'; }
'TRUE'                              { return 'TRUE'; }
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

\'                                  { this.begin('SingleQuotedValue_Complete'); return 'SINGLE_QUOTE'; }
<SingleQuotedValue_Complete>[^']+   { return 'VALUE'; }
<SingleQuotedValue_Complete>\'      { this.popState(); return 'SINGLE_QUOTE'; }

\"                                  { this.begin('DoubleQuotedValue_Complete'); return 'DOUBLE_QUOTE'; }
<DoubleQuotedValue_Complete>[^"]+   { return 'VALUE'; }
<DoubleQuotedValue_Complete>\"      { this.popState(); return 'DOUBLE_QUOTE'; }

<<EOF>>                             { return 'EOF'; }

/lex

%start Sql

%%

InitResults
 : /* empty */
   {
     parser.yy.result = {};
     parser.yy.cursorFound = false;

     // TODO: Move these below before token or use $$ instead
     delete parser.yy.latestTablePrimaries;
     delete parser.yy.keepColumns;

     parser.parseError = function (message, error) {
       if (typeof parser.yy.result.suggestColumns !== 'undefined') {
         linkTablePrimaries();
       }
       parser.yy.result.error = error;
       return message;
     }
   }
 ;

Sql
 : InitResults SqlStatements ';' EOF
   {
     return parser.yy.result;
   }
 | InitResults SqlStatements EOF
   {
     return parser.yy.result;
   }
 ;

SqlStatements
 : SqlStatement
 | SqlStatements ';' SqlStatement
 ;

SqlStatement
 : DataDefinition
 | DataManipulation
 | QuerySpecification_Complete
 | QuerySpecification_Cursored
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

DataDefinition
 : CreateStatement
 | DescribeStatement
 | DropStatement
 | ShowStatement
 | UseStatement
 ;

DataManipulation
 : LoadStatement
 | UpdateStatement
 ;



// ===================================== Commonly used constructs =====================================

AggregateOrAnalytic
 : '<impala>AGGREGATE'
 | '<impala>ANALYTIC'
 ;

AnyCreate
 : 'CREATE'
 | '<hive>CREATE'
 | '<impala>CREATE'
 ;

AnyCursor
 : 'CURSOR'
 | 'PARTIAL_CURSOR'
 ;

AnyDot
 : '.'
 | '<impala>.'
 | '<hive>.'
 ;

AnyFromOrIn
 : 'FROM'
 | '<hive>IN'
 ;

AnyTable
 : 'TABLE'
 | '<hive>TABLE'
 | '<impala>TABLE'
 ;

ComparisonOperators
 : '='
 | '<>'
 | '<='
 | '>='
 | '<'
 | '>'
 ;

DatabaseOrSchema
 : 'DATABASE'
 | 'SCHEMA'
 ;

FromOrIn
 : 'FROM'
 | '<hive>IN'
 ;

HiveIndexOrIndexes
 : '<hive>INDEX'
 | '<hive>INDEXES'
 ;

HiveOrImpalaComment
 : '<hive>COMMENT'
 | '<impala>COMMENT'
 ;

HiveOrImpalaCreate
 : '<hive>CREATE'
 | '<impala>CREATE'
 ;

HiveOrImpalaCurrent
 : '<hive>CURRENT'
 | '<impala>CURRENT'
 ;

HiveOrImpalaData
 : '<hive>DATA'
 | '<impala>DATA'
 ;

HiveOrImpalaDatabasesOrSchemas
 : '<hive>DATABASES'
 | '<hive>SCHEMAS'
 | '<impala>DATABASES'
 | '<impala>SCHEMAS'
 ;

HiveOrImpalaExternal
 : '<hive>EXTERNAL'
 | '<impala>EXTERNAL'
 ;

HiveOrImpalaLoad
 : '<hive>LOAD'
 | '<impala>LOAD'
 ;

HiveOrImpalaIn
 : '<hive>IN'
 | '<impala>IN'
 ;

HiveOrImpalaInpath
 : '<hive>INPATH'
 | '<impala>INPATH'
 ;

HiveOrImpalaLeftSquareBracket
 : '<hive>['
 | '<impala>['
 ;

HiveOrImpalaLocation
 : '<hive>LOCATION'
 | '<impala>LOCATION'
 ;

HiveOrImpalaRightSquareBracket
 : '<hive>]'
 | '<impala>]'
 ;

HiveOrImpalaRole
 : '<hive>ROLE'
 | '<impala>ROLE'
 ;

HiveOrImpalaRoles
 : '<hive>ROLES'
 | '<impala>ROLES'
 ;

HiveOrImpalaTables
 : '<hive>TABLES'
 | '<impala>TABLES'
 ;

HiveRoleOrUser
 : '<hive>ROLE'
 | '<hive>USER'
 ;

SignedInteger_Complete
 : 'UNSIGNED_INTEGER'
 | '-' 'UNSIGNED_INTEGER'
 ;

SingleQuotedValue_Complete
 : 'SINGLE_QUOTE' 'VALUE' 'SINGLE_QUOTE'
   {
     $$ = $2;
   }
 ;

DoubleQuotedValue_Complete
 : 'DOUBLE_QUOTE' 'VALUE' 'DOUBLE_QUOTE'
   {
     $$ = $2;
   }
 ;

AnyAs
 : 'AS'
 | '<hive>AS'
 ;

AnyGroup
 : 'GROUP'
 | '<hive>GROUP'
 | '<impala>GROUP'
 ;

OptionalAggregateOrAnalytic
 :
 | AggregateOrAnalytic
 ;

OptionalExtended
 :
 | '<hive>EXTENDED'
 ;

OptionalExtendedOrFormatted
 :
 | '<hive>EXTENDED'
 | '<hive>FORMATTED'
 ;

OptionalFormatted
 :
 | '<impala>FORMATTED'
 ;

OptionallyFormattedIndex_Complete
 : '<hive>FORMATTED' HiveIndexOrIndexes
 | HiveIndexOrIndexes
 ;

OptionallyFormattedIndex_Cursored
 : '<hive>FORMATTED' 'CURSOR'
   {
     suggestKeywords(['INDEX', 'INDEXES']);
   }
 | 'CURSOR' HiveIndexOrIndexes
   {
     suggestKeywords(['FORMATTED']);
   }
 ;

OptionalFromDatabase_Complete
 :
 | FromOrIn DatabaseIdentifier_Complete
 ;

OptionalFromDatabase_Cursored
 : FromOrIn DatabaseIdentifier_Cursored
 ;


OptionalHiveCascadeOrRestrict_Complete
 :
 | '<hive>CASCADE'
 | '<hive>RESTRICT'
 ;

OptionalIfExists_Complete
 :
 | 'IF' 'EXISTS'
 ;


OptionalIfExists_Cursored
 : 'IF' 'CURSOR'
   {
     suggestKeywords(['EXISTS']);
   }
 ;

OptionalIfNotExists_Complete
 :
 | 'IF' 'NOT' 'EXISTS'
 ;

OptionalIfNotExists_Cursored
 : 'CURSOR'
   {
     suggestKeywords(['IF NOT EXISTS']);
   }
 | 'IF' 'CURSOR'
   {
     suggestKeywords(['NOT EXISTS']);
   }
 | 'IF' 'NOT' 'CURSOR'
   {
     suggestKeywords(['EXISTS']);
   }
 ;

OptionalInDatabase
 :
 | HiveOrImpalaIn DatabaseIdentifier_Complete
 | HiveOrImpalaIn DatabaseIdentifier_Cursored
 ;

ConfigurationName
 : 'REGULAR_IDENTIFIER'
 | 'CURSOR'
 | ConfigurationName '<hive>.' 'REGULAR_IDENTIFIER'
 | ConfigurationName '<hive>.' 'PARTIAL_CURSOR'
 ;

PartialBacktickedOrCursor
 : 'CURSOR'
 | PartialBacktickedIdentifier
 ;

PartialBacktickedOrPartialCursor
 : 'PARTIAL_CURSOR'
 | PartialBacktickedIdentifier
 ;

PartialBacktickedIdentifier
 : 'BACKTICK' 'PARTIAL_VALUE'
 ;

SchemaQualifiedTableIdentifier_Complete
 : RegularOrBacktickedIdentifier
   {
     $$ = { identifierChain: [{ name: $1 }] }
   }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     $$ = { identifierChain: [{ name: $1 }, { name: $3 }] }
   }
 ;

SchemaQualifiedTableIdentifier_Cursored
 : PartialBacktickedIdentifier
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | PartialBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     suggestDatabases();
     $$ = { identifierChain: [{ name: $1 }] }
   }
 | RegularOrBacktickedIdentifier AnyDot PartialBacktickedOrPartialCursor
   {
     // In Impala you can have statements like 'SELECT ... FROM testTable t, t.|'
     suggestTablesOrColumns($1);
   }
 ;

DatabaseIdentifier_Complete
 : RegularOrBacktickedIdentifier
 ;

DatabaseIdentifier_Cursored
 : PartialBacktickedOrCursor
   {
     $$ = { cursorOrPartialIdentifier: true }
     suggestDatabases();
   }
 ;


PartitionSpecList
 : PartitionSpec
 | PartitionSpecList ',' PartitionSpec
 ;

PartitionSpec
 : 'REGULAR_IDENTIFIER' '=' SingleQuotedValue_Complete
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


RegularOrBacktickedIdentifier
 : 'REGULAR_IDENTIFIER'
 | 'BACKTICK' 'VALUE' 'BACKTICK'
   {
     $$ = $2;
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
 | 'BACKTICK' 'VALUE' 'BACKTICK' AnyDot PartialBacktickedOrPartialCursor
   {
     $$ = { partial: true, identifierChain: [ { name: $2 } ] };
   }
 | 'REGULAR_IDENTIFIER' AnyDot PartialBacktickedOrPartialCursor
   {
     $$ = { partial: true, identifierChain: [ { name: $1 } ] };
   }
 | PartialBacktickedIdentifier
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

DerivedColumnChain_Complete
 : ColumnIdentifier_Complete
   {
     $$ = [ $1 ]
   }
 | DerivedColumnChain_Complete AnyDot ColumnIdentifier_Complete
   {
     $$ = $1.concat($3)
   }
 ;

DerivedColumnChain_Cursored
 : DerivedColumnChain_Complete AnyDot PartialBacktickedIdentifier
   {
     $$ = $1;
   }
 | DerivedColumnChain_Complete AnyDot 'PARTIAL_CURSOR'
   {
     $$ = $1;
   }
 ;


ColumnIdentifier_Complete
 : RegularOrBacktickedIdentifier OptionalMapOrArrayKey_Complete
   {
     if (typeof $2.key !== 'undefined') {
       $$ = { name: $1, key: $2.key }
     } else {
       $$ = { name: $1 }
     }
   }
 ;

ColumnIdentifier_Cursored
 : PartialBacktickedOrCursor OptionalMapOrArrayKey_Complete
 ;

OptionalMapOrArrayKey_Complete
 :  { $$ = {} }
 | HiveOrImpalaLeftSquareBracket DoubleQuotedValue_Complete HiveOrImpalaRightSquareBracket
   {
     $$ = { key: '"' + $2 + '"' }
   }
 | HiveOrImpalaLeftSquareBracket 'UNSIGNED_INTEGER' HiveOrImpalaRightSquareBracket
   {
     $$ = { key: parseInt($2) }
   }
 | HiveOrImpalaLeftSquareBracket HiveOrImpalaRightSquareBracket
   {
     $$ = { key: null }
   }
 ;


// ===================================== CREATE statement =====================================

CreateStatement
 : TableDefinition
 | DatabaseDefinition
 | AnyCreate 'CURSOR'
   {
     if (isHive() || isImpala()) {
       suggestKeywords(['DATABASE', 'EXTERNAL', 'SCHEMA', 'TABLE']);
     } else {
       suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE']);
     }
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
 : OptionalComment OptionalHdfsLocation OptionalHiveDbProperties
   {
     $$ = mergeSuggestKeywords($1, $2, $3);
   }
 ;

OptionalComment
 :
   {
     $$ = { suggestKeywords: ['COMMENT'] }
   }
 | Comment
 ;

OptionalHdfsLocation
 :
   {
     $$ = { suggestKeywords: ['LOCATION'] }
   }
 | HdfsLocation
 ;

OptionalHiveDbProperties
 :
   {
     $$ = { suggestKeywords: isHive() ? ['WITH DBPROPERTIES'] : [] }
   }
 | HiveDbProperties
 ;

DatabaseDefinition
 : AnyCreate DatabaseOrSchema OptionalIfNotExists_Complete
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_Cursored
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_Complete 'REGULAR_IDENTIFIER'
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_Cursored 'REGULAR_IDENTIFIER'
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_Complete 'REGULAR_IDENTIFIER' DatabaseDefinitionOptionals error
   // For the HDFS open single quote completion
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_Complete 'REGULAR_IDENTIFIER' DatabaseDefinitionOptionals 'CURSOR'
   {
     if ($5 && $5.suggestKeywords.length > 0) {
       suggestKeywords($5.suggestKeywords);
     }
   }
 ;

TableDefinition
 : AnyCreate TableScope AnyTable 'REGULAR_IDENTIFIER' TableElementList HdfsLocation
 | AnyCreate 'CURSOR' AnyTable 'REGULAR_IDENTIFIER' TableElementList
    {
      if (isHive() || isImpala()) {
        suggestKeywords(['EXTERNAL']);
      }
    }
 | AnyCreate 'CURSOR' AnyTable 'REGULAR_IDENTIFIER'
    {
      if (isHive() || isImpala()) {
        suggestKeywords(['EXTERNAL']);
      }
    }
 | AnyCreate 'CURSOR' AnyTable
    {
      if (isHive() || isImpala()) {
        suggestKeywords(['EXTERNAL']);
      }
    }
 | AnyCreate TableScope AnyTable 'REGULAR_IDENTIFIER' TableElementList 'CURSOR'
   {
     if (isHive() || isImpala()) {
       suggestKeywords(['LOCATION']);
     }
   }
 | AnyCreate AnyTable 'REGULAR_IDENTIFIER' TableElementList
 ;

TableScope
 : HiveOrImpalaExternal
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
 | 'REGULAR_IDENTIFIER' 'CURSOR'
   {
     if (parser.yy.dialect == 'hive') {
       suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     } else {
       suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
     }
   }
 | 'REGULAR_IDENTIFIER' 'CURSOR' ColumnDefinitionError error
   // error here is because it expects closing ')'
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



// ===================================== DESCRIBE statement =====================================

DescribeStatement
 : HiveDescribeStatement
 | ImpalaDescribeStatement
 ;

HiveDescribeStatement
 : '<hive>DESCRIBE' OptionalExtendedOrFormatted DerivedColumnChain_Complete
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted DerivedColumnChain_Cursored
    {
      if ($3.length > 0) {
        var table =  $3.shift().name;
        suggestColumns({
          table: table,
          identifierChain: $3
        });
      } else {
        if (!$2) {
          suggestKeywords(['DATABASE', 'EXTENDED', 'FORMATTED', 'SCHEMA']);
        }
        suggestTables();
      }
    }
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted 'CURSOR'
   {
     if (!$2) {
       suggestKeywords(['DATABASE', 'EXTENDED', 'FORMATTED', 'SCHEMA']);
     }
     suggestTables();
    }
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalExtended DatabaseIdentifier_Complete
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalExtended DatabaseIdentifier_Cursored
   {
     if (!$3) {
       suggestKeywords(['EXTENDED']);
     }
   }
 ;

ImpalaDescribeStatement
 : '<impala>DESCRIBE' OptionalFormatted SchemaQualifiedTableIdentifier_Complete
 | '<impala>DESCRIBE' OptionalFormatted SchemaQualifiedTableIdentifier_Cursored
 | '<impala>DESCRIBE' OptionalFormatted 'CURSOR' SchemaQualifiedTableIdentifier_Complete
    {
      if (!$2) {
        suggestKeywords(['FORMATTED']);
      }
    }
 | '<impala>DESCRIBE' OptionalFormatted 'CURSOR'
    {
      if (!$2) {
        suggestKeywords(['FORMATTED']);
      }
      suggestTables();
      suggestDatabases({ appendDot: true });
      $$ = { cursorOrPartialIdentifier: true }
    } ;



// ===================================== DROP Statement =====================================

DropStatement
 : 'DROP' 'CURSOR'
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

DropDatabaseStatement
 : 'DROP' DatabaseOrSchema OptionalIfExists_Complete
 | 'DROP' DatabaseOrSchema OptionalIfExists_Cursored
 | 'DROP' DatabaseOrSchema OptionalIfExists_Complete 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestDatabases();
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists_Complete RegularOrBacktickedIdentifier 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['CASCADE', 'RESTRICT']);
     }
   }
 | 'DROP' DatabaseOrSchema OptionalIfExists_Complete RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict_Complete
 | 'DROP' DatabaseOrSchema OptionalIfExists_Cursored RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict_Complete
 ;

DropTableStatement
 : 'DROP' AnyTable OptionalIfExists_Complete
 | 'DROP' AnyTable OptionalIfExists_Cursored
 | 'DROP' AnyTable OptionalIfExists_Complete 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF EXISTS']);
     }
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'DROP' AnyTable OptionalIfExists_Complete TablePrimary_Complete
 | 'DROP' AnyTable OptionalIfExists_Complete TablePrimary_Cursored
   {
     if ($4.identifierChain && $4.identifierChain.length === 1) {
       suggestTablesOrColumns($4.identifierChain[0].name);
     } else if ($4.identifierChain && $4.identifierChain.length === 0) {
       suggestTables();
       suggestDatabases({ appendDot: true });
     }
   }
 | 'DROP' AnyTable OptionalIfExists_Cursored TablePrimary_Complete
 | 'DROP' AnyTable OptionalIfExists_Complete TablePrimary_Complete 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['PURGE']);
     }
   }
 ;



// ===================================== LOAD statement =====================================

LoadStatement
 : HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath 'INTO' AnyTable 'REGULAR_IDENTIFIER'
 | HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath 'INTO' 'CURSOR'
   {
     suggestKeywords([ 'TABLE' ]);
   }
 | HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath 'CURSOR'
   {
     suggestKeywords([ 'INTO' ]);
   }
 | HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath
 | HiveOrImpalaLoad HiveOrImpalaData 'CURSOR'
   {
     suggestKeywords([ 'INPATH' ]);
   }
 | HiveOrImpalaLoad 'CURSOR'
   {
     suggestKeywords([ 'DATA' ]);
   }
 ;



// ===================================== SELECT statement =====================================

QuerySpecification_Complete
 : 'SELECT' SelectList_Complete // TODO: Needed?
 | 'SELECT' SelectList_Complete TableExpression_Complete
   {
     linkTablePrimaries();
   }
 ;

QuerySpecification_Cursored
 : 'SELECT' SelectList_Cursored
 | 'SELECT' 'CURSOR'
   {
     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'SELECT' SelectList_Complete TableExpression_Cursored
   {
     linkTablePrimaries();
   }
 | 'SELECT' SelectList_Cursored TableExpression_Complete
   {
     linkTablePrimaries();
   }
 | 'SELECT' 'CURSOR' TableExpression_Complete
   {
     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
     linkTablePrimaries();
   }
 | 'SELECT' error TableExpression_Complete
   {
     linkTablePrimaries();
   }
 | 'SELECT' error TableExpression_Cursored
   {
     linkTablePrimaries();
   }
 | 'SELECT' SelectList_Complete 'CURSOR' TableExpression_Complete
   {
     if ($2.suggestKeywords) {
       suggestKeywords($2.suggestKeywords);
     }
   }
 | 'SELECT' SelectList_Complete 'CURSOR' ',' TableExpression_Complete
 | 'SELECT' SelectList_Complete 'CURSOR' ',' error TableExpression_Complete
    {
      if ($2.suggestKeywords) {
        suggestKeywords($2.suggestKeywords);
      }
    }
 | 'SELECT' SelectList_Complete 'CURSOR'
   {
     if ($2.suggestKeywords) {
       suggestKeywords($2.suggestKeywords);
     }
     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   }
 ;

TableExpression_Complete
 : FromClause_Complete SelectConditions_Complete
 ;

TableExpression_Cursored
 : FromClause_Complete SelectConditions_Cursored
 | FromClause_Cursored SelectConditions_Complete
 | FromClause_Complete SelectConditions_Complete 'CURSOR'
   {
     if ($2.suggestKeywords.length == 0) {
       var keywords = [];
       if (typeof $1.hasJoinCondition !== 'undefined' && ! $1.hasJoinCondition) {
         keywords.push('ON');
       }
       if (isHive()) {
         keywords = keywords.concat(['CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'JOIN', 'LATERAL VIEW', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']);
       } else if (isImpala()) {
         keywords = keywords.concat(['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT ANTI JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT ANTI JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'RIGHT SEMI JOIN', 'WHERE']);
       } else {
         keywords = keywords.concat(['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']);
       }
       suggestKeywords(keywords);
     } else if ($2.suggestKeywords) {
       suggestKeywords($2.suggestKeywords);
     }
   }
 ;

FromClause_Complete
 : 'FROM' TableReferenceList_Complete
   {
     $$ = $2;
   }
 ;

FromClause_Cursored
 : 'FROM' TableReferenceList_Cursored
 | 'FROM' 'CURSOR'
   {
       suggestTables();
       suggestDatabases({ appendDot: true });
   }
 ;

SelectConditions_Complete
 : OptionalWhereClause_Complete OptionalGroupByClause_Complete OptionalOrderByClause_Complete OptionalLimitClause_Complete
   {
     if (!$1 && !$2 && !$3 && !$4) {
       $$ = { suggestKeywords: [] }
     } else if ($1 && !$2 && !$3 && !$4) {
       $$ = mergeSuggestKeywords($1, { suggestKeywords: ['GROUP BY', 'LIMIT', 'ORDER BY'] });
     } else if ($2 && !$3 && !$4) {
       $$ = { suggestKeywords: ['ORDER BY', 'LIMIT'] }
     } else if ($3 && !$4) {
       if ($3.suggestKeywords) {
         $$ = { suggestKeywords: $3.suggestKeywords.concat(['LIMIT']) }
       } else {
         $$ = { suggestKeywords: ['LIMIT'] }
       }
     }
   }
 ;

SelectConditions_Cursored
 : OptionalWhereClause_Cursored OptionalGroupByClause_Complete OptionalOrderByClause_Complete OptionalLimitClause_Complete
 | OptionalWhereClause_Complete OptionalGroupByClause_Cursored OptionalOrderByClause_Complete OptionalLimitClause_Complete
 | OptionalWhereClause_Complete OptionalGroupByClause_Complete OptionalOrderByClause_Cursored OptionalLimitClause_Complete
 | OptionalWhereClause_Complete OptionalGroupByClause_Complete OptionalOrderByClause_Complete OptionalLimitClause_Cursored
 ;

OptionalWhereClause_Complete
 :
 | 'WHERE' SearchCondition_Complete
   {
     $$ = $2;
   }
 ;

OptionalWhereClause_Cursored
 : 'WHERE' SearchCondition_Cursored
 | 'WHERE' 'CURSOR'
   {
     suggestColumns();
   }
 ;

OptionalGroupByClause_Complete
 :
 | AnyGroup 'BY' GroupByColumnList_Complete
 ;

OptionalGroupByClause_Cursored
 : AnyGroup 'BY' GroupByColumnList_Cursored
   {
     delete parser.yy.result.suggestStar;
   }
 | AnyGroup 'BY' 'CURSOR'
   {
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | AnyGroup 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

GroupByColumnList_Complete
 : DerivedColumnOrUnsignedInteger_Complete
 | GroupByColumnList_Complete, DerivedColumnOrUnsignedInteger_Complete
 ;

GroupByColumnList_Cursored
 : DerivedColumnOrUnsignedInteger_Cursored
 | 'CURSOR' DerivedColumnOrUnsignedInteger_Complete
   {
     suggestColumns();
   }
 | GroupByColumnList_Complete ',' GroupByColumnListPartTwo_Cursored
 | GroupByColumnList_Complete ',' GroupByColumnListPartTwo_Cursored ','
 | GroupByColumnList_Complete ',' GroupByColumnListPartTwo_Cursored ',' GroupByColumnList_Complete
 ;

GroupByColumnListPartTwo_Cursored
 : DerivedColumnOrUnsignedInteger_Cursored
 | AnyCursor
   {
     suggestColumns();
   }
 ;

OptionalOrderByClause_Complete
 :
 | 'ORDER' 'BY' OrderByColumnList_Complete
   {
     $$ = $3;
   }
 ;

OptionalOrderByClause_Cursored
 : 'ORDER' 'BY' OrderByColumnList_Cursored
   {
     delete parser.yy.result.suggestStar;
   }
 | 'ORDER' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

OrderByColumnList_Complete
 : OrderByIdentifier_Complete
 | OrderByColumnList_Complete ',' OrderByIdentifier_Complete
   {
     $$ = $3;
   }
 ;

OrderByColumnList_Cursored
 : OrderByIdentifier_Cursored
 | 'CURSOR' OrderByIdentifier_Complete
   {
     suggestColumns();
   }
 | OrderByColumnList_Complete ',' OrderByIdentifier_Cursored
 | OrderByColumnList_Complete ',' OrderByIdentifier_Cursored ','
 | OrderByColumnList_Complete ',' OrderByIdentifier_Cursored ',' OrderByColumnList_Complete
 ;

OrderByIdentifier_Complete
 : DerivedColumnOrUnsignedInteger_Complete OptionalAscOrDesc_Complete OptionalImpalaNullsFirstOrLast_Complete
   {
     $$ = mergeSuggestKeywords($2, $3);
   }
 ;

OrderByIdentifier_Cursored
 : DerivedColumnOrUnsignedInteger_Cursored OptionalAscOrDesc_Complete OptionalImpalaNullsFirstOrLast_Complete
 | DerivedColumnOrUnsignedInteger_Complete OptionalAscOrDesc_Complete OptionalImpalaNullsFirstOrLast_Cursored
 | AnyCursor OptionalAscOrDesc_Complete OptionalImpalaNullsFirstOrLast_Complete
   {
     suggestColumns();
   }
 ;

DerivedColumnOrUnsignedInteger_Complete
 : DerivedColumn_Complete
 | 'UNSIGNED_INTEGER'
 ;

DerivedColumnOrUnsignedInteger_Cursored
 : DerivedColumn_Cursored
 ;

OptionalAscOrDesc_Complete
 :
  {
    $$ = { suggestKeywords: ['ASC', 'DESC'] }
  }
 | 'ASC'
 | 'DESC'
 ;

OptionalImpalaNullsFirstOrLast_Complete
 :
  {
    if (isImpala()) {
      $$ = { suggestKeywords: ['NULLS FIRST', 'NULLS LAST'] }
    } else {
      $$ = {}
    }
  }
 | '<impala>NULLS' '<impala>FIRST'
 | '<impala>NULLS' '<impala>LAST'
 ;

OptionalImpalaNullsFirstOrLast_Cursored
 : '<impala>NULLS' 'CURSOR'
   {
     suggestKeywords(['FIRST', 'LAST']);
   }
 ;

OptionalLimitClause_Complete
 :
 | 'LIMIT' 'UNSIGNED_INTEGER'
 ;

OptionalLimitClause_Cursored
 : 'LIMIT' 'CURSOR'
   {
     suggestNumbers([1, 5, 10]);
   }
 ;

SearchCondition_Complete
 : BooleanValueExpression_Complete
 ;

SearchCondition_Cursored
 : BooleanValueExpression_Cursored
 ;

BooleanValueExpression_Complete
 : BooleanTerm_Complete
 | BooleanValueExpression_Complete 'OR' BooleanTerm_Complete
 ;

BooleanValueExpression_Cursored
 : BooleanTerm_Cursored
 | BooleanValueExpression_Complete 'OR' BooleanTerm_Cursored
 | BooleanValueExpression_Cursored 'OR' BooleanTerm_Complete
 ;

BooleanTerm_Complete
 : BooleanFactor_Complete
 | BooleanFactor_Complete 'AND' BooleanTerm_Complete
 ;

BooleanTerm_Cursored
 : BooleanFactor_Cursored
 | BooleanFactor_Complete 'AND' 'CURSOR'
   {
     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   }
 | BooleanFactor_Complete 'AND' BooleanTerm_Cursored
 | BooleanFactor_Cursored 'AND' BooleanTerm_Complete
 ;

BooleanFactor_Complete
 : 'NOT' BooleanTest_Complete
 | BooleanTest_Complete
 ;

BooleanFactor_Cursored
 : 'NOT' BooleanTest_Cursored
 | BooleanTest_Cursored
 ;

BooleanTest_Complete
 : BooleanPrimary_Complete OptionalIsNotTruthValue_Complete
 ;

BooleanTest_Cursored
 : BooleanPrimary_Cursored OptionalIsNotTruthValue_Complete
 ;

OptionalIsNotTruthValue_Complete
 :
 | 'IS' OptionalNot_Complete TruthValue_Complete
 ;

TruthValue_Complete
 : 'TRUE'
 | 'FALSE'
 ;

OptionalNot_Complete
 :
 | 'NOT'
 ;

BooleanPrimary_Complete
 : Predicate_Complete
 | BooleanPredicand_Complete
   {
     $$ = { suggestKeywords: ['<', '<=', '<>', '=', '=>', '>', 'IN', 'NOT IN'] }
   }
 ;

BooleanPrimary_Cursored
 : Predicate_Cursored
 | BooleanPredicand_Cursored
 ;

Predicate_Complete
 : ComparisonPredicate_Complete
   {
     $$ = { suggestKeywords: ['AND'] }
   }
 | InPredicate_Complete
 ;

Predicate_Cursored
 : ComparisonPredicate_Cursored
 | InPredicate_Cursored
 ;

AnyIn
 : 'IN'
 | '<hive>IN'
 | '<impala>IN'
 ;

ComparisonPredicate_Complete
 : BooleanPredicand_Complete ComparisonOperators BooleanPredicand_Complete
 ;

ComparisonPredicate_Cursored
 : BooleanPredicand_Cursored ComparisonOperators BooleanPredicand_Complete
 | BooleanPredicand_Complete ComparisonOperators BooleanPredicand_Cursored
 | BooleanPredicand_Complete ComparisonOperators AnyCursor
   {
     if (typeof $1 !== 'undefined') {
       suggestValues({ identifierChain: $1});
     }
   }
 ;

BooleanPredicand_Complete
 : ParenthesizedBooleanValueExpression_Complete
 | NonParenthesizedValueExpressionPrimary_Complete
 | CommonValueExpression_Complete
 ;

BooleanPredicand_Cursored
 : ParenthesizedBooleanValueExpression_Cursored
 | NonParenthesizedValueExpressionPrimary_Cursored
 ;

CommonValueExpression_Complete
 : SignedInteger_Complete
 | SingleQuotedValue_Complete
 ;

InPredicate_Complete
 : BooleanPredicand_Complete InPredicatePartTwo_Complete
 ;

InPredicate_Cursored
 : BooleanPredicand_Cursored InPredicatePartTwo_Complete
 | BooleanPredicand_Complete InPredicatePartTwo_Cursored
 ;

InPredicatePartTwo_Complete
 : AnyIn InPredicateValue_Complete
 | 'NOT' AnyIn InPredicateValue_Complete
 ;

InPredicatePartTwo_Cursored
 : AnyIn InPredicateValue_Cursored
 | AnyIn 'CURSOR'
 | 'NOT' AnyIn InPredicateValue_Cursored
 | 'NOT' 'CURSOR'
   {
     suggestKeywords(['IN']);
   }
 ;

InPredicateValue_Complete
 : TableSubquery_Complete
 ;

InPredicateValue_Cursored
 : TableSubquery_Cursored
 ;

ParenthesizedBooleanValueExpression_Complete
 : '(' BooleanValueExpression_Complete ')'
 ;

ParenthesizedBooleanValueExpression_Cursored
 : '(' BooleanValueExpression_Cursored ')'
 | '(' AnyCursor // Could be either (| or ( |
   {
     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   }
 ;


// TODO: Expand with more choices
NonParenthesizedValueExpressionPrimary_Complete
 : ColumnReference_Complete
   {
     $$ = $1;
   }
 ;

NonParenthesizedValueExpressionPrimary_Cursored
 : ColumnReference_Cursored
 ;

ColumnReference_Complete
 : BasicIdentifierChain_Complete
 ;

ColumnReference_Cursored
 : BasicIdentifierChain_Cursored
 ;


BasicIdentifierChain_Complete
 : Identifier_Complete
   {
     $$ = [ $1 ];
   }
 | BasicIdentifierChain_Complete AnyDot Identifier_Complete
   {
     $$ = $1.concat($3);
   }
 ;

BasicIdentifierChain_Cursored
 : Identifier_Cursored
 | BasicIdentifierChain_Complete AnyDot Identifier_Cursored
 | BasicIdentifierChain_Complete AnyDot 'PARTIAL_CURSOR'
   {
     suggestColumns({
       identifierChain: $1
     });
   }
 ;

Identifier_Complete
 : ColumnIdentifier_Complete
 | DoubleQuotedValue_Complete
   {
     $$ = { name: $1 }
   }
 ;

Identifier_Cursored
 : ColumnIdentifier_Complete 'PARTIAL_CURSOR'
   {
     suggestColumns();
   }
 ;

SelectList_Complete
 : SelectSubList_Complete
 | '*'
 ;

SelectList_Cursored
 : SelectSubList_Cursored
 ;

SelectSubList_Complete
 : ColumnList_Complete
 ;

SelectSubList_Cursored
 : ColumnList_Cursored
 ;

ColumnList_Complete
 : DerivedColumn_Complete OptionalCorrelationName_Complete
   {
     $$ = $2;
   }
 | ColumnList_Complete ',' DerivedColumn_Complete OptionalCorrelationName_Complete
   {
     $$ = $4;
   }
 ;

ColumnList_Cursored
 : DerivedColumn_Cursored OptionalCorrelationName_Complete
 | DerivedColumn_Complete OptionalCorrelationName_Cursored
 | 'CURSOR' ColumnList_Complete
   {
     parser.yy.result.suggestStar = true;
     suggestColumns();
   }
 | ColumnList_Complete ',' DerivedColumn_Complete OptionalCorrelationName_Cursored
 | ColumnList_Complete ',' ColumnListPartTwo_Cursored
 | ColumnList_Complete ',' ColumnListPartTwo_Cursored ','
 | ColumnList_Complete ',' ColumnListPartTwo_Cursored ',' ColumnList_Complete
 ;

ColumnListPartTwo_Cursored
 : DerivedColumn_Cursored
 | AnyCursor
   {
     parser.yy.result.suggestStar = true;
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 ;

DerivedColumn_Complete
 : ColumnIdentifier_Complete
 | ColumnIdentifier_Complete AnyDot '*'
 | ColumnIdentifier_Complete AnyDot DerivedColumnChain_Complete
 ;

DerivedColumn_Cursored
 : ColumnIdentifier_Complete AnyDot PartialBacktickedOrPartialCursor
   {
     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $1.key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $1 ]
     });
   }
 | ColumnIdentifier_Complete AnyDot DerivedColumnChain_Complete '<impala>.' 'PARTIAL_CURSOR'
   {
      $3.unshift($1);
      suggestColumns({
        identifierChain: $3
      });
    }
 | ColumnIdentifier_Complete AnyDot DerivedColumnChain_Complete '<hive>.' 'PARTIAL_CURSOR'
   {
      $3.unshift($1);
      suggestColumns({
        identifierChain: $3
      });
    }
 ;

TableReferenceList_Complete
 : TableReference_Complete
 | TableReferenceList_Complete ',' TableReference_Complete
   {
     $$ = $3;
   }
 ;

TableReferenceList_Cursored
 : TableReference_Cursored
 | TableReferenceList_Cursored ',' TableReference_Complete
 | TableReferenceList_Complete ',' TableReference_Cursored
 | TableReferenceList_Complete ',' 'CURSOR'
   {
       suggestTables();
       suggestDatabases({ appendDot: true });
   }
 ;

TableReference_Complete
 : TablePrimaryOrJoinedTable_Complete
 ;

TableReference_Cursored
 : TablePrimaryOrJoinedTable_Cursored
 ;

TablePrimaryOrJoinedTable_Complete
 : TablePrimary_Complete
 | JoinedTable_Complete
 ;

TablePrimaryOrJoinedTable_Cursored
 : TablePrimary_Cursored
 | JoinedTable_Cursored
 ;

JoinedTable_Complete
 : TablePrimary_Complete Joins_Complete
   {
     $$ = $2;
   }
 ;

JoinedTable_Cursored
 : TablePrimary_Complete Joins_Cursored
 | TablePrimary_Cursored Joins_Complete
 ;

Joins_Complete
 : JoinTypes_Complete 'JOIN' TablePrimary_Complete
   {
     $$ = { hasJoinCondition: false }
   }
 | JoinTypes_Complete 'JOIN' TablePrimary_Complete JoinCondition_Complete
   {
     $$ = { hasJoinCondition: true }
   }
 | Joins_Complete JoinTypes_Complete 'JOIN' TablePrimary_Complete
   {
     $$ = { hasJoinCondition: false }
   }
 | Joins_Complete JoinTypes_Complete 'JOIN' TablePrimary_Complete JoinCondition_Complete
   {
     $$ = { hasJoinCondition: true }
   }
 ;

Joins_Cursored
 : JoinTypes_Cursored 'JOIN' TablePrimary_Complete
 | JoinTypes_Complete 'JOIN' TablePrimary_Cursored
 | JoinTypes_Cursored 'JOIN' TablePrimary_Complete JoinCondition_Complete
 | JoinTypes_Complete 'JOIN' TablePrimary_Cursored JoinCondition_Complete
 | JoinTypes_Complete 'JOIN' TablePrimary_Complete JoinCondition_Cursored
 | Joins_Cursored JoinTypes_Complete 'JOIN' TablePrimary_Complete
 | Joins_Complete JoinTypes_Cursored 'JOIN' TablePrimary_Complete
 | Joins_Complete JoinTypes_Complete 'JOIN' TablePrimary_Cursored
 | Joins_Cursored JoinTypes_Complete 'JOIN' TablePrimary_Complete JoinCondition_Complete
 | Joins_Complete JoinTypes_Cursored 'JOIN' TablePrimary_Complete JoinCondition_Complete
 | Joins_Complete JoinTypes_Complete 'JOIN' TablePrimary_Cursored JoinCondition_Complete
 | Joins_Complete JoinTypes_Complete 'JOIN' TablePrimary_Complete JoinCondition_Cursored
 | JoinsTableSuggestions_Cursored
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 ;

JoinsTableSuggestions_Cursored
 : JoinTypes_Complete 'JOIN' 'CURSOR'
 | JoinTypes_Complete 'JOIN' 'CURSOR' JoinCondition_Complete
 | Joins_Complete JoinTypes_Complete 'JOIN' 'CURSOR'
 | Joins_Complete JoinTypes_Complete 'JOIN' 'CURSOR' JoinCondition_Complete
 ;

JoinTypes_Complete
 :
 | '<hive>CROSS'
 | 'FULL' OptionalOuter
 | '<impala>INNER'
 | 'LEFT' 'SEMI'
 | 'LEFT' OptionalOuter
 | 'RIGHT' OptionalOuter
 | '<impala>RIGHT' 'SEMI'
 | '<impala>RIGHT' OptionalOuter
 ;

JoinTypes_Cursored
 : 'FULL' OptionalOuter 'CURSOR'
   {
     if (!$2) {
       suggestKeywords(['OUTER']);
     }
   }
 | 'LEFT' OptionalOuter 'CURSOR'
   {
     var keywords = [];
     if (isImpala()) {
       keywords.push('ANTI');
       keywords.push('SEMI');
     }
     if (isHive()) {
       keywords.push('SEMI');
     }
     if (!$2) {
       keywords.push('OUTER');
     }
     suggestKeywords(keywords);
   }
 | 'RIGHT' OptionalOuter 'CURSOR'
   {
     if (!$2) {
       suggestKeywords(['OUTER']);
     }
   }
 | '<impala>RIGHT' OptionalOuter 'CURSOR'
   {
     if (!$2) {
       suggestKeywords(['ANTI', 'SEMI', 'OUTER']);
     } else {
       suggestKeywords(['ANTI', 'SEMI']);
     }
   }
 ;

OptionalOuter
 :
 | 'OUTER'
 ;

JoinCondition_Cursored
 : 'ON' JoinEqualityExpression_Cursored
 | 'ON' ParenthesizedJoinEqualityExpression_Cursored
 | 'ON' 'CURSOR'
   {
     suggestColumns();
   }
 ;

JoinCondition_Complete
 : 'ON' JoinEqualityExpression_Complete
 | 'ON' ParenthesizedJoinEqualityExpression_Complete
 ;

ParenthesizedJoinEqualityExpression_Complete
 : '(' JoinEqualityExpression_Complete ')'
 ;

ParenthesizedJoinEqualityExpression_Cursored
 : '(' JoinEqualityExpression_Cursored ')'
 | '(' 'PARTIAL_CURSOR'
   {
     suggestColumns();
   }
 | '(' 'PARTIAL_CURSOR' 'AND' JoinEqualityExpression_Complete
    {
      suggestColumns();
    }
 ;

JoinEqualityExpression_Complete
 : EqualityExpression_Complete
 | JoinEqualityExpression_Complete 'AND' EqualityExpression_Complete
 ;

JoinEqualityExpression_Cursored
 : EqualityExpression_Cursored
 | EqualityExpression_Cursored 'AND' JoinEqualityExpression_Complete
 | 'CURSOR' 'AND' JoinEqualityExpression_Complete
   {
     suggestColumns();
   }
 | JoinEqualityExpression_Complete 'AND' EqualityExpression_Cursored
 | JoinEqualityExpression_Complete 'AND' 'CURSOR'
   {
     suggestColumns();
   }
 | JoinEqualityExpression_Complete 'AND' EqualityExpression_Cursored 'AND' JoinEqualityExpression_Complete
 | JoinEqualityExpression_Complete 'AND' 'CURSOR' 'AND' JoinEqualityExpression_Complete
   {
     suggestColumns();
   }
 ;

EqualityExpression_Complete
 : ColumnReference_Complete '=' ColumnReference_Complete
 ;

EqualityExpression_Cursored
 : ColumnReference_Complete '=' ColumnReference_Cursored
 | ColumnReference_Cursored '=' ColumnReference_Complete
 | ColumnReference_Complete '=' 'CURSOR'
   {
     suggestColumns();
   }
 | 'CURSOR' '=' ColumnReference_Complete
   {
     suggestColumns();
   }
 | 'PARTIAL_CURSOR' '=' ColumnReference_Complete
   {
     suggestColumns();
   }
 | ColumnReference_Complete '=' 'PARTIAL_CURSOR'
   {
     suggestColumns();
   }
 ;

TablePrimary_Complete
 : TableOrQueryName_Complete OptionalCorrelationName_Complete OptionalLateralViews_Complete
   {
     if ($1.identifierChain) {
       if ($2 && !$2.suggestKeywords) {
         $1.alias = $2
       }
       if ($3 && $3.length > 0) {
         $1.lateralViews = $3;
       }
       addTablePrimary($1);
     }
   }
 | DerivedTable_Complete OptionalCorrelationName_Complete
   {
     if ($2 && !$2.suggestKeywords) {
       // TODO: Potentially add columns for SELECT bla.| FROM (SELECT * FROM foo) AS bla;
       addTablePrimary({ subqueryAlias: $2 });
     }
   }
 ;

TablePrimary_Cursored
 : TableOrQueryName_Cursored OptionalCorrelationName_Complete OptionalLateralViews_Complete
 | TableOrQueryName_Complete OptionalCorrelationName_Complete OptionalLateralViews_Cursored
 | DerivedTable_Cursored OptionalCorrelationName_Complete
   {
     if ($2 && !$2.suggestKeywords) {
       // TODO: Potentially add columns for SELECT bla.| FROM (SELECT * FROM foo) AS bla;
       addTablePrimary({ subqueryAlias: $2 });
     }
   }
 | DerivedTable_Complete OptionalCorrelationName_Cursored // TODO: OptionalLateralViews?
 ;

TableOrQueryName_Complete
 : SchemaQualifiedTableIdentifier_Complete
 ;

TableOrQueryName_Cursored
 : SchemaQualifiedTableIdentifier_Cursored
 ;

DerivedTable_Complete
 : TableSubquery_Complete
 ;

DerivedTable_Cursored
 : TableSubquery_Cursored
 ;

PushQueryState
 :
   {
     if (typeof parser.yy.primariesStack === 'undefined') {
       parser.yy.primariesStack = [];
     }
     if (typeof parser.yy.resultStack === 'undefined') {
       parser.yy.resultStack = [];
     }
     parser.yy.primariesStack.push(parser.yy.latestTablePrimaries);
     parser.yy.resultStack.push(parser.yy.result);

     parser.yy.result = {};
     parser.yy.latestTablePrimaries = [];
   }
 ;

PopQueryState
 :
   {
     if (Object.keys(parser.yy.result).length === 0) {
       parser.yy.result = parser.yy.resultStack.pop();
       parser.yy.latestTablePrimaries = parser.yy.primariesStack.pop();
     }
   }
 ;

TableSubquery_Complete
 : '(' PushQueryState Subquery_Complete PopQueryState ')'
 ;

TableSubquery_Cursored
 : '(' PushQueryState Subquery_Cursored PopQueryState ')'
 | '(' PushQueryState AnyCursor PopQueryState ')'
   {
     suggestKeywords(['SELECT']);
   }
 | '(' PushQueryState Subquery_Cursored error
 | '(' PushQueryState AnyCursor error
   {
     suggestKeywords(['SELECT']);
   }
 ;

Subquery_Complete
 : QueryExpression_Complete
 ;

Subquery_Cursored
 : QueryExpression_Cursored
 ;

QueryExpression_Complete
 : QueryExpressionBody_Complete
 ;

QueryExpression_Cursored
 : QueryExpressionBody_Cursored
 ;

QueryExpressionBody_Complete
 : NonJoinQueryExpression_Complete
 ;

QueryExpressionBody_Cursored
 : NonJoinQueryExpression_Cursored
 ;

NonJoinQueryExpression_Complete
 : NonJoinQueryTerm_Complete
 ;

NonJoinQueryExpression_Cursored
 : NonJoinQueryTerm_Cursored
 ;

NonJoinQueryTerm_Complete
 : NonJoinQueryPrimary_Complete
 ;

NonJoinQueryTerm_Cursored
 : NonJoinQueryPrimary_Cursored
 ;

NonJoinQueryPrimary_Complete
 : SimpleTable_Complete
 ;

NonJoinQueryPrimary_Cursored
 : SimpleTable_Cursored
 ;

SimpleTable_Complete
 : QuerySpecification_Complete
 ;

SimpleTable_Cursored
 : QuerySpecification_Cursored
 ;

OptionalCorrelationName_Complete
 :
   {
     $$ = { suggestKeywords: ['AS'] }
   }
 | RegularOrBacktickedIdentifier
   {
     $$ = $1
   }
 | AnyAs RegularOrBacktickedIdentifier
   {
     $$ = $2
   }
 ;

OptionalCorrelationName_Cursored
 : PartialBacktickedIdentifier
 | AnyAs PartialBacktickedIdentifier
 | AnyAs 'CURSOR'
 ;

OptionalLateralViews_Complete
 :
 | OptionalLateralViews_Complete LateralView_Complete
   {
     if ($1) {
       $$ = $1.concat($2);
     } else {
       $$ = $2;
     }
   }
 ;

OptionalLateralViews_Cursored
 : OptionalLateralViews_Complete LateralView_Cursored OptionalLateralViews_Complete
 ;

// TODO: '<hive>[pos]explode' '(' 'CURSOR' possible?
UserDefinedTableGeneratingFunction_Complete
 : '<hive>explode' '(' DerivedColumnChain_Complete ')'
   {
     $$ = { function: $1, expression: $3 }
   }
 | '<hive>posexplode' '(' DerivedColumnChain_Complete ')'
   {
     $$ = { function: $1, expression: $3 }
   }
 ;

UserDefinedTableGeneratingFunction_Cursored
 : '<hive>explode' '(' PartialBacktickedOrPartialCursor
 | '<hive>posexplode' '(' PartialBacktickedOrPartialCursor
 ;


LateralView_Complete
 : '<hive>LATERAL' 'VIEW' UserDefinedTableGeneratingFunction_Complete 'REGULAR_IDENTIFIER' LateralViewColumnAliases_Complete
   {
     $$ = [{ udtf: $3, tableAlias: $4, columnAliases: $5 }]
   }
 | '<hive>LATERAL' 'VIEW' UserDefinedTableGeneratingFunction_Complete LateralViewColumnAliases_Complete
    {
      $$ = [{ udtf: $3, columnAliases: $4 }]
    }
 ;

LateralView_Cursored
 : '<hive>LATERAL' 'VIEW' UserDefinedTableGeneratingFunction_Cursored LateralViewColumnAliases_Complete
 | '<hive>LATERAL' 'VIEW' UserDefinedTableGeneratingFunction_Complete 'REGULAR_IDENTIFIER' 'CURSOR'
   {
     $$ = [];
     suggestKeywords(['AS']);
   }
 | '<hive>LATERAL' 'VIEW' UserDefinedTableGeneratingFunction_Complete 'CURSOR'
   {
     $$ = [];
     suggestKeywords(['AS']);
   }
 | '<hive>LATERAL' 'VIEW' 'CURSOR'
   {
     $$ = [];
     suggestKeywords(['explode', 'posexplode']);
   }
 | '<hive>LATERAL' 'CURSOR'
   {
     $$ = [];
     suggestKeywords(['VIEW']);
   }
 ;

LateralViewColumnAliases_Complete
 : '<hive>AS' 'REGULAR_IDENTIFIER'
   {
     $$ = [ $2 ]
   }
 | '<hive>AS' '(' 'REGULAR_IDENTIFIER' ',' 'REGULAR_IDENTIFIER' ')'
   {
     $$ = [ $3, $5 ]
   }
 ;

// ===================================== SHOW Statement =====================================

ShowStatement
 : 'SHOW' 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['COLUMNS', 'COMPACTIONS', 'CONF', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FORMATTED', 'FUNCTIONS', 'GRANT', 'INDEX', 'INDEXES', 'LOCKS', 'PARTITIONS', 'PRINCIPALS', 'ROLE GRANT', 'ROLES', 'SCHEMAS', 'TABLE EXTENDED', 'TABLES', 'TBLPROPERTIES', 'TRANSACTIONS']);
     } else if (isImpala()) {
       suggestKeywords(['AGGREGATE FUNCTIONS', 'ANALYTIC FUNCTIONS', 'COLUMN STATS', 'CREATE TABLE', 'CURRENT ROLES', 'DATABASES', 'FUNCTIONS', 'GRANT ROLE', 'PARTITIONS', 'ROLE GRANT GROUP', 'ROLES', 'SCHEMAS', 'TABLE STATS', 'TABLES']);
     } else {
       suggestKeywords(['COLUMNS', 'DATABASES', 'TABLES']);
     }
   }
 | 'SHOW' 'CURSOR' CleanRegularOrBackTickedSchemaQualifiedName
   {
     if (isImpala()) {
       suggestKeywords(['COLUMN STATS', 'CREATE TABLE', 'PARTITIONS', 'TABLE STATS']);
     }
   }
 | 'SHOW' 'CURSOR' LIKE SingleQuotedValue_Complete
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
 | ShowGrantStatement_Complete
 | ShowGrantStatement_Cursored
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
 : 'SHOW' '<impala>COLUMN' 'CURSOR'
   {
     suggestKeywords(['STATS']);
   }
 | 'SHOW' '<impala>COLUMN' '<impala>STATS' 'CURSOR'
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
 : 'SHOW' '<hive>COLUMNS' 'CURSOR'
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' '<hive>COLUMNS' 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn 'CURSOR'
   {
     suggestTables();
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn 'CURSOR' AnyFromOrIn
   {
     suggestTables();
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn 'CURSOR' AnyFromOrIn RegularOrBacktickedIdentifier
   {
     suggestTables();
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier 'CURSOR'
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier AnyFromOrIn 'CURSOR'
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

ShowCreateTableStatement
 : 'SHOW' HiveOrImpalaCreate 'CURSOR'
   {
     suggestKeywords(['TABLE']);
   }
 | 'SHOW' HiveOrImpalaCreate AnyTable 'CURSOR'
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
 | 'SHOW' HiveOrImpalaCreate 'CURSOR' CleanRegularOrBackTickedSchemaQualifiedName
   {
     suggestKeywords(['TABLE']);
   }
 ;

ShowCurrentStatement
 : 'SHOW' HiveOrImpalaCurrent 'CURSOR'
   {
     suggestKeywords([ 'ROLES' ]);
   }
 | 'SHOW' 'CURSOR' HiveOrImpalaRoles
   {
     suggestKeywords([ 'CURRENT' ]);
   }
 | 'SHOW' HiveOrImpalaCurrent HiveOrImpalaRoles
 ;

ShowDatabasesStatement
 : 'SHOW' HiveOrImpalaDatabasesOrSchemas 'CURSOR'
   {
     suggestKeywords(['LIKE']);
   }
 | 'SHOW' HiveOrImpalaDatabasesOrSchemas 'LIKE' SingleQuotedValue_Complete
 | 'SHOW' '<impala>DATABASES' SingleQuotedValue_Complete
 ;

ShowFunctionsStatement
 : 'SHOW' '<hive>FUNCTIONS'
 | 'SHOW' '<hive>FUNCTIONS' DoubleQuotedValue_Complete
 | 'SHOW' AggregateOrAnalytic 'CURSOR'
   {
     suggestKeywords(['FUNCTIONS']);
   }
 | 'SHOW' OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase
 | 'SHOW' 'CURSOR' '<impala>FUNCTIONS' OptionalInDatabase
   {
     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   }
 | 'SHOW' OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase 'CURSOR'
   {
     if (!$4) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   }
 | 'SHOW' OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase 'LIKE' SingleQuoteValue
 | 'SHOW' AggregateOrAnalytic 'CURSOR' OptionalInDatabase 'LIKE' SingleQuoteValue
   {
     suggestKeywords(['FUNCTIONS']);
   }
 | 'SHOW' 'CURSOR' '<impala>FUNCTIONS' OptionalInDatabase 'LIKE' SingleQuoteValue
   {
     suggestKeywords(['AGGREGATE', 'ANALYTICAL']);
   }
 | 'SHOW' OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase 'CURSOR' SingleQuoteValue
   {
     if (!$4) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   }
 ;

ShowGrantStatement_Complete
 : 'SHOW' '<hive>GRANT' OptionalPrincipalName_Complete
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName_Complete 'ON' '<hive>ALL'
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName_Complete 'ON' RegularOrBacktickedIdentifier
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName_Complete 'ON' AnyTable RegularOrBacktickedIdentifier
 ;

ShowGrantStatement_Cursored
 : 'SHOW' '<hive>GRANT' OptionalPrincipalName_Cursored
   {
     suggestKeywords(['ON']);
   }
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName_Cursored 'ON' '<hive>ALL'
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName_Complete 'ON' 'CURSOR'
   {
     suggestKeywords(['ALL', 'TABLE']);
     suggestTables();
   }
 | 'SHOW'  '<hive>GRANT' OptionalPrincipalName_Complete 'ON' AnyTable 'CURSOR'
   {
     suggestTables();
   }
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName_Complete 'ON' 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['TABLE']);
   }
 | 'SHOW' '<impala>GRANT' 'CURSOR'
   {
     suggestKeywords(['ROLE']);
   }
 ;

OptionalPrincipalName_Complete
 :
 | 'REGULAR_IDENTIFIER'
 ;

OptionalPrincipalName_Cursored
 : 'CURSOR'
 | 'REGULAR_IDENTIFIER' 'CURSOR'
 ;


ShowIndexStatement
 : 'SHOW' OptionallyFormattedIndex_Complete
 | 'SHOW' OptionallyFormattedIndex_Complete 'ON' RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex_Complete 'ON' RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex_Cursored
 | 'SHOW' OptionallyFormattedIndex_Cursored 'ON' RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex_Cursored 'ON' RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex_Complete 'CURSOR'
   {
     suggestKeywords(['ON']);
   }
 | 'SHOW' OptionallyFormattedIndex_Complete 'ON' 'CURSOR'
   {
     suggestTables();
   }
 | 'SHOW' OptionallyFormattedIndex_Complete 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['ON']);
   }
 | 'SHOW' OptionallyFormattedIndex_Complete 'ON' RegularOrBacktickedIdentifier 'CURSOR'
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' OptionallyFormattedIndex_Complete 'ON' RegularOrBacktickedIdentifier 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' OptionallyFormattedIndex_Complete 'ON' RegularOrBacktickedIdentifier AnyFromOrIn 'CURSOR'
   {
     suggestDatabases();
   }
 | 'SHOW' OptionallyFormattedIndex_Complete 'ON' 'CURSOR' AnyFromOrIn RegularOrBacktickedIdentifier
   {
     suggestTablesOrColumns($6);
   }
 ;

// TODO: Merge the first two i.e. 'CURSOR' | RegularOrBackTickedSchemaQualifiedName
ShowLocksStatement
 : 'SHOW' '<hive>LOCKS' 'CURSOR'
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
 | 'SHOW' '<hive>LOCKS' CleanRegularOrBackTickedSchemaQualifiedName 'CURSOR'
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
 | 'SHOW' '<hive>LOCKS' CleanRegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' '(' PartitionSpecList ')' 'CURSOR'
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
 | 'SHOW' '<hive>LOCKS' DatabaseOrSchema 'CURSOR'
   {
     suggestDatabases();
   }
 | 'SHOW' '<hive>LOCKS' DatabaseOrSchema RegularOrBacktickedIdentifier
 ;

ShowPartitionsStatement
 : 'SHOW' '<hive>PARTITIONS' 'CURSOR'
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
 | 'SHOW' '<hive>PARTITIONS' CleanRegularOrBackTickedSchemaQualifiedName 'CURSOR'
   {
     suggestKeywords(['PARTITION']);
   }
 | 'SHOW' '<hive>PARTITIONS' CleanRegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' PartitionSpecList
 | 'SHOW' '<impala>PARTITIONS' 'CURSOR'
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
 : 'SHOW' HiveOrImpalaRole 'CURSOR'
   {
     suggestKeywords(['GRANT']);
   }
 | 'SHOW' HiveOrImpalaRole 'CURSOR' HiveRoleOrUser 'REGULAR_IDENTIFIER'
   {
     suggestKeywords(['GRANT']);
   }
 | 'SHOW' HiveOrImpalaRole '<hive>GRANT' 'CURSOR'
   {
     suggestKeywords(['ROLE', 'USER']);
   }
 | 'SHOW' HiveOrImpalaRole '<hive>GRANT' 'CURSOR' 'REGULAR_IDENTIFIER'
   {
     suggestKeywords(['ROLE', 'USER']);
   }
 | 'SHOW' HiveOrImpalaRole '<hive>GRANT' HiveRoleOrUser 'REGULAR_IDENTIFIER'
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' 'CURSOR'
   {
     suggestKeywords(['GROUP']);
   }
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' 'CURSOR' 'REGULAR_IDENTIFIER'
   {
     suggestKeywords(['GROUP']);
   }
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' '<impala>GROUP' 'REGULAR_IDENTIFIER'
 ;

ShowRolesStatement
 : 'SHOW' '<impala>ROLES'
 ;

ShowTableStatement
 : 'SHOW' '<hive>TABLE' 'CURSOR'
   {
     suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Complete
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Cursored
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Complete 'CURSOR'
    {
      if ($4) {
        suggestKeywords(['LIKE']);
      } else {
        suggestKeywords(['FROM', 'IN', 'LIKE']);
      }
    }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Complete 'LIKE' SingleQuotedValue_Complete
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Cursored 'LIKE' SingleQuotedValue_Complete
 | 'SHOW' '<hive>TABLE' 'CURSOR' OptionalFromDatabase_Complete 'LIKE' SingleQuotedValue_Complete
    {
      if (isHive())
        suggestKeywords(['EXTENDED']);
      }
    }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Complete 'CURSOR' SingleQuotedValue_Complete
    {
      suggestKeywords(['LIKE']);
    }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Complete 'LIKE' SingleQuotedValue_Complete 'CURSOR'
    {
      suggestKeywords(['PARTITION']);
    }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Complete 'LIKE' SingleQuotedValue_Complete '<hive>PARTITION' PartitionSpecList
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Cursored 'LIKE' SingleQuotedValue_Complete '<hive>PARTITION' PartitionSpecList
 | 'SHOW' '<hive>TABLE' 'CURSOR' OptionalFromDatabase_Complete 'LIKE' SingleQuotedValue_Complete '<hive>PARTITION' PartitionSpecList
   {
     suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Complete 'CURSOR' SingleQuotedValue_Complete '<hive>PARTITION' PartitionSpecList
   {
     suggestKeywords(['LIKE']);
   }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_Complete 'LIKE' SingleQuotedValue_Complete 'CURSOR' PartitionSpecList
   {
     suggestKeywords(['PARTITION']);
   }
 | 'SHOW' '<impala>TABLE' 'CURSOR'
   {
     suggestKeywords(['STATS']);
   }
 | 'SHOW' '<impala>TABLE' '<impala>STATS' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' '<impala>TABLE' '<impala>STATS' CleanRegularOrBackTickedSchemaQualifiedName
   {
     if ($3.partial && $3.identifierChain.length === 1) {
       suggestTablesOrColumns($3.identifierChain[0].name)
     }
   }
 ;

ShowTablesStatement
 : 'SHOW' HiveOrImpalaTables OptionalInDatabase
 | 'SHOW' HiveOrImpalaTables OptionalInDatabase 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   }
 | 'SHOW' HiveOrImpalaTables OptionalInDatabase SingleQuotedValue_Complete
 | 'SHOW' HiveOrImpalaTables OptionalInDatabase 'LIKE' SingleQuotedValue_Complete
 ;

ShowTblPropertiesStatement
 : 'SHOW' '<hive>TBLPROPERTIES' 'CURSOR'
   {
     suggestTables();
   }
 ;

ShowTransactionsStatement
 : 'SHOW' '<hive>TRANSACTIONS'
 ;



// ===================================== UPDATE statement =====================================

UpdateStatement
 : 'UPDATE' TargetTable 'SET' SetClauseList OptionalWhereClause_Complete
   {
     linkTablePrimaries();
   }
 | 'UPDATE' TargetTable 'SET' SetClauseList OptionalWhereClause_Cursored
    {
      linkTablePrimaries();
    }
 | 'UPDATE' TargetTable 'SET' SetClauseList OptionalWhereClause_Complete 'CURSOR'
   {
     if (!$5) {
       suggestKeywords([ 'WHERE' ]);
     }
   }
 | 'UPDATE' TargetTable 'CURSOR'
   {
     suggestKeywords([ 'SET' ]);
   }
 | 'UPDATE' TargetTable
 | 'UPDATE' 'CURSOR'
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
 | 'CURSOR'
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
 : BooleanValueExpression_Complete
 | BooleanValueExpression_Cursored
 ;



// ===================================== USE Statement =====================================

UseStatement
 : 'USE' 'REGULAR_IDENTIFIER'
   {
     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $2;
     }
   }
 | 'USE' 'CURSOR'
   {
     suggestDatabases();
   }
 ;
%%

var isHive = function () {
  return parser.yy.dialect === 'hive';
}

var isImpala = function () {
  return parser.yy.dialect === 'impala';
}

var mergeSuggestKeywords = function() {
  var result = [];
  Array.prototype.slice.call(arguments).forEach(function (suggestion) {
    if (typeof suggestion !== 'undefined' && typeof suggestion.suggestKeywords !== 'undefined') {
      result = result.concat(suggestion.suggestKeywords);
    }
  });
  if (result.length > 0) {
    return { suggestKeywords: result }
  }
  return {}
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
      if (typeof parser.yy.result.suggestColumns.identifierChain !== 'undefined' && parser.yy.result.suggestColumns.identifierChain.length === 0) {
        delete parser.yy.result.suggestColumns.identifierChain;
      }
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

parser.identifyPartials = function (beforeCursor, afterCursor) {
  var beforeMatch = beforeCursor.match(/[a-zA-Z_]*$/);
  var afterMatch = afterCursor.match(/^[a-zA-Z_]*/);
  return { left: beforeMatch ? beforeMatch[0].length : 0, right: afterMatch ? afterMatch[0].length : 0}
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

  if (typeof identifierChain === 'undefined' || typeof tablePrimaries === 'undefined') {
    return;
  }

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
    if (typeof tablePrimaries[0].identifierChain !== 'undefined') {
      if (tablePrimaries[0].identifierChain.length == 2) {
        suggestion.database = tablePrimaries[0].identifierChain[0].name;
        suggestion.table = tablePrimaries[0].identifierChain[1].name;
      } else {
        suggestion.table = tablePrimaries[0].identifierChain[0].name;
      }
    } else if (typeof tablePrimaries[0].subqueryAlias !== 'undefined') {
      suggestTablePrimariesAsIdentifiers();
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
    } else if (typeof tablePrimary.identifierChain !== 'undefined' && tablePrimary.identifierChain.length == 2) {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.identifierChain[0].name + '.' + tablePrimary.identifierChain[1].name + '.', type: 'table' });
    } else if (typeof tablePrimary.identifierChain !== 'undefined') {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.identifierChain[0].name + '.', type: 'table' });
    } else if (typeof tablePrimary.subqueryAlias !== 'undefined') {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.subqueryAlias + '.', type: 'subquery' });
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

  suggestKeywords(keywords);
}

var suggestKeywords = function (keywords) {
  parser.yy.result.suggestKeywords = keywords.sort();
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

  var partialLengths = parser.identifyPartials(beforeCursor, afterCursor);

  if (partialLengths.left > 0) {
    beforeCursor = beforeCursor.substring(0, beforeCursor.length - partialLengths.left);
  }

  if (partialLengths.right > 0) {
    afterCursor = afterCursor.substring(partialLengths.right);
  }

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
    if (parser.yy.result.error) {
      console.log(parser.yy.result.error);
    }
    result = parser.yy.result;
  }
  prioritizeSuggestions();

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