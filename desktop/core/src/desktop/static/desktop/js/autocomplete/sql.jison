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
%options case-insensitive flex
%s between hive impala
%x hdfs DoubleQuotedValue SingleQuotedValue backtickedValue
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
<impala>'INNER'                     { return '<impala>INNER'; }
<impala>'LAST'                      { return '<impala>LAST'; }
<impala>'LOAD'                      { return '<impala>LOAD'; }
<impala>'LOCATION'                  { this.begin('hdfs'); return '<impala>LOCATION'; }
<impala>'NULLS'                     { return '<impala>NULLS'; }
<impala>'OVER'                      { return '<impala>OVER'; }
<impala>'PARTITIONS'                { return '<impala>PARTITIONS'; }
<impala>'RIGHT'                     { return '<impala>RIGHT'; }
<impala>'ROLE'                      { return '<impala>ROLE'; }
<impala>'ROLES'                     { return '<impala>ROLES'; }
<impala>'SCHEMAS'                   { return '<impala>SCHEMAS'; }
<impala>'STATS'                     { return '<impala>STATS'; }
<impala>'TABLE'                     { return '<impala>TABLE'; }
<impala>'TABLES'                    { return '<impala>TABLES'; }
<impala>\[SHUFFLE\]                 { return '<impala>SHUFFLE'; }
<impala>\[BROADCAST\]               { return '<impala>BROADCAST'; }

<impala>[.]                         { return '<impala>.'; }
<impala>\[                          { return '<impala>['; }
<impala>\]                          { return '<impala>]'; }

<between>'AND'                      { this.popState(); return 'BETWEEN_AND'; }

'ALL'                               { return 'ALL'; }
'AND'                               { return 'AND'; }
'AS'                                { return 'AS'; }
'ASC'                               { return 'ASC'; }
'BETWEEN'                           { this.begin('between'); return 'BETWEEN'; }
'BIGINT'                            { return 'BIGINT'; }
'BOOLEAN'                           { return 'BOOLEAN'; }
'BY'                                { return 'BY'; }
'CHAR'                              { return 'CHAR'; }
'CREATE'                            { determineCase(yytext); return 'CREATE'; }
'DATABASE'                          { return 'DATABASE'; }
'DECIMAL'                           { return 'DECIMAL'; }
'DESC'                              { return 'DESC'; }
'DISTINCT'                          { return 'DISTINCT'; }
'DOUBLE'                            { return 'DOUBLE'; }
'DROP'                              { determineCase(yytext); return 'DROP'; }
'EXISTS'                            { parser.yy.correlatedSubquery = true; return 'EXISTS'; }
'FALSE'                             { return 'FALSE'; }
'FILTER' // CHECK                   { return 'FILTER'; }
'FLOAT'                             { return 'FLOAT'; }
'FROM'                              { return 'FROM'; }
'OUTER'                             { return 'OUTER'; }
'INNER'                             { return 'INNER'; }
'RIGHT'                             { return 'RIGHT'; }
'RLIKE'                             { return 'RLIKE'; }
'REGEXP'                            { return 'REGEXP'; }
'FULL'                              { return 'FULL'; }
'GROUP'                             { return 'GROUP'; }
'GROUPING'                          { return 'GROUPING'; }
'IF'                                { return 'IF'; }
'INT'                               { return 'INT'; }
'INTO'                              { return 'INTO'; }
'IS'                                { return 'IS'; }
'IN'                                { return 'IN'; }
'JOIN'                              { return 'JOIN'; }
'LEFT'                              { return 'LEFT'; }
'LIKE'                              { return 'LIKE'; }
'NOT'                               { return 'NOT'; }
'NULL'                              { return 'NULL'; }
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
'WITHIN'                            { return 'WITHIN'; }

// --- UDFs ---
CAST\(                              { return 'CAST('; }
COUNT\(                             { return 'COUNT('; }
SUM\(                               { return 'SUM('; }
[A-Za-z][A-Za-z0-9_]*\(             { return 'UDF('; }

[0-9]+                              { return 'UNSIGNED_INTEGER'; }
[0-9]+E                             { return 'UNSIGNED_INTEGER_E'; }
[A-Za-z][A-Za-z0-9_]*               { return 'REGULAR_IDENTIFIER'; }

<hdfs>'\u2020'                      { parser.yy.cursorFound = true; return 'CURSOR'; }
<hdfs>'\u2021'                      { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }
<hdfs>\s+[']                        { return 'HDFS_START_QUOTE'; }
<hdfs>[^'\u2020\u2021]+             { return 'HDFS_PATH'; }
<hdfs>[']                           { this.popState(); return 'HDFS_END_QUOTE'; }
<hdfs><<EOF>>                       { return 'EOF'; }

'&&'                                { return 'AND'; }
'||'                                { return 'OR'; }

'='                                 { return '='; }
'!='                                { return 'COMPARISON_OPERATOR'; }
'<'                                 { return 'COMPARISON_OPERATOR'; }
'>'                                 { return 'COMPARISON_OPERATOR'; }
'<='                                { return 'COMPARISON_OPERATOR'; }
'>='                                { return 'COMPARISON_OPERATOR'; }
'<>'                                { return 'COMPARISON_OPERATOR'; }
'<=>'                               { return 'COMPARISON_OPERATOR'; }

'-'                                 { return '-'; }
'*'                                 { return '*'; }
'+'                                 { return 'ARITHMETIC_OPERATOR'; }
'/'                                 { return 'ARITHMETIC_OPERATOR'; }
'%'                                 { return 'ARITHMETIC_OPERATOR'; }
'|'                                 { return 'ARITHMETIC_OPERATOR'; }
'^'                                 { return 'ARITHMETIC_OPERATOR'; }
'&'                                 { return 'ARITHMETIC_OPERATOR'; }

[~(),.;!]                           { return yytext; }

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

\'                                  { this.begin('SingleQuotedValue'); return 'SINGLE_QUOTE'; }
<SingleQuotedValue>[^']+            { return 'VALUE'; }
<SingleQuotedValue>\'               { this.popState(); return 'SINGLE_QUOTE'; }

\"                                  { this.begin('DoubleQuotedValue'); return 'DOUBLE_QUOTE'; }
<DoubleQuotedValue>[^"]+            { return 'VALUE'; }
<DoubleQuotedValue>\"               { this.popState(); return 'DOUBLE_QUOTE'; }

<<EOF>>                             { return 'EOF'; }

/lex

/* operators and precedence levels */

%left 'AND' 'OR'
%left 'BETWEEN'
%left 'NOT' '!' '~'
%left '=' 'COMPARISON_OPERATOR'
%left '-' '*' 'ARITHMETIC_OPERATOR'

%nonassoc 'CURSOR' 'PARTIAL_CURSOR'
%nonassoc 'IN' 'IS' 'LIKE' 'RLIKE' 'REGEXP' 'EXISTS' NEGATION

%start Sql

%%

RegularIdentifier
 : 'REGULAR_IDENTIFIER'
 ;

InitResults
 : /* empty */
   {
     parser.yy.result = {};
     parser.yy.cursorFound = false;

     // TODO: Move these below before token or use $$ instead
     delete parser.yy.latestTablePrimaries;
     delete parser.yy.correlatedSubquery
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
 | QuerySpecification
 | QuerySpecification_EDIT
 | RegularIdentifier 'PARTIAL_CURSOR' RegularIdentifier
 | RegularIdentifier 'PARTIAL_CURSOR'
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
 | 'IN'
 ;

AnyTable
 : 'TABLE'
 | '<hive>TABLE'
 | '<impala>TABLE'
 ;

DatabaseOrSchema
 : 'DATABASE'
 | 'SCHEMA'
 ;

FromOrIn
 : 'FROM'
 | 'IN'
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

SingleQuotedValue
 : 'SINGLE_QUOTE' 'VALUE' 'SINGLE_QUOTE'         -> $2
 ;

DoubleQuotedValue
 : 'DOUBLE_QUOTE' 'VALUE' 'DOUBLE_QUOTE'         -> $2
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

OptionallyFormattedIndex
 : '<hive>FORMATTED' HiveIndexOrIndexes
 | HiveIndexOrIndexes
 ;

OptionallyFormattedIndex_EDIT
 : '<hive>FORMATTED' 'CURSOR'
   {
     suggestKeywords(['INDEX', 'INDEXES']);
   }
 | 'CURSOR' HiveIndexOrIndexes
   {
     suggestKeywords(['FORMATTED']);
   }
 ;

OptionalFromDatabase
 :
 | FromOrIn DatabaseIdentifier
 ;

OptionalFromDatabase_EDIT
 : FromOrIn DatabaseIdentifier_EDIT
 ;

OptionalHiveCascadeOrRestrict
 :
 | '<hive>CASCADE'
 | '<hive>RESTRICT'
 ;

OptionalIfExists
 :
 | 'IF' 'EXISTS'
   {
     parser.yy.correlatedSubquery = false;
   }
 ;


OptionalIfExists_EDIT
 : 'IF' 'CURSOR'
   {
     suggestKeywords(['EXISTS']);
   }
 ;

OptionalIfNotExists
 :
 | 'IF' 'NOT' 'EXISTS'
   {
     parser.yy.correlatedSubquery = false;
   }
 ;

OptionalIfNotExists_EDIT
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
 | 'IN' DatabaseIdentifier
 | 'IN' DatabaseIdentifier_EDIT
 ;

ConfigurationName
 : RegularIdentifier
 | 'CURSOR'
 | ConfigurationName '<hive>.' RegularIdentifier
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

RightParenthesisOrError
 : ')'
 | error
 ;

SchemaQualifiedTableIdentifier
 : RegularOrBacktickedIdentifier
   {
     $$ = { identifierChain: [{ name: $1 }] }
   }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     $$ = { identifierChain: [{ name: $1 }, { name: $3 }] }
   }
 ;

SchemaQualifiedTableIdentifier_EDIT
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

DatabaseIdentifier
 : RegularOrBacktickedIdentifier
 ;

DatabaseIdentifier_EDIT
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
 : RegularIdentifier '=' SingleQuotedValue
 ;

// TODO: Move into RegularOrBackTickedSchemaQualifiedName
CleanRegularOrBackTickedSchemaQualifiedName
 : RegularIdentifier
   {
     $$ = { identifierChain: [ { name: $1 } ] }
   }
 | RegularOrBackTickedSchemaQualifiedName
 ;


RegularOrBacktickedIdentifier
 : RegularIdentifier
 | 'BACKTICK' 'VALUE' 'BACKTICK'         -> $2
 ;

RegularOrBackTickedSchemaQualifiedName
 : RegularIdentifier AnyDot RegularIdentifier
   {
     $$ = { identifierChain: [ { name: $1 }, { name: $3 } ] }
   }
 | 'BACKTICK' 'VALUE' 'BACKTICK' AnyDot RegularIdentifier
   {
     $$ = { identifierChain: [ { name: $2 }, { name: $5 } ] }
   }
 | RegularIdentifier AnyDot 'BACKTICK' 'VALUE' 'BACKTICK'
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
 | RegularIdentifier AnyDot PartialBacktickedOrPartialCursor
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
 : RegularIdentifier
   {
     $$ = { identifierChain: [ { name: $1 } ] }
   }
 | RegularIdentifier RegularIdentifier
   {
     $$ = { identifierChain: [ { name: $1 } ], alias: $2 };
   }
 | RegularOrBackTickedSchemaQualifiedName
 | RegularOrBackTickedSchemaQualifiedName RegularIdentifier
   {
     $$ = { identifierChain: $1.identifierChain, alias: $2 }
   }
 ;

DerivedColumnChain
 : ColumnIdentifier
   {
     $$ = [ $1 ]
   }
 | DerivedColumnChain AnyDot ColumnIdentifier
   {
     $$ = $1.concat($3)
   }
 ;

DerivedColumnChain_EDIT
 : DerivedColumnChain AnyDot PartialBacktickedIdentifierOrPartialCursor
   {
     $$ = { identifierChain: $1 }
   }
 ;

PartialBacktickedIdentifierOrPartialCursor
 : PartialBacktickedIdentifier
 | 'PARTIAL_CURSOR'
 ;

ColumnIdentifier
 : RegularOrBacktickedIdentifier OptionalMapOrArrayKey
   {
     if ($2) {
       $$ = { name: $1, key: $2.key }
     } else {
       $$ = { name: $1 }
     }
   }
 ;

ColumnIdentifier_EDIT
 : PartialBacktickedOrCursor OptionalMapOrArrayKey
 ;

OptionalMapOrArrayKey
 :
 | HiveOrImpalaLeftSquareBracket DoubleQuotedValue HiveOrImpalaRightSquareBracket
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
 : RegularIdentifier '=' RegularIdentifier
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
 : AnyCreate DatabaseOrSchema OptionalIfNotExists
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_EDIT
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_EDIT RegularIdentifier
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals error
   // For the HDFS open single quote completion
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals 'CURSOR'
   {
     checkForKeywords($5);
   }
 ;

TableDefinition
 : AnyCreate TableScope AnyTable RegularIdentifier TableElementList HdfsLocation
 | AnyCreate 'CURSOR' AnyTable RegularIdentifier TableElementList
    {
      if (isHive() || isImpala()) {
        suggestKeywords(['EXTERNAL']);
      }
    }
 | AnyCreate 'CURSOR' AnyTable RegularIdentifier
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
 | AnyCreate TableScope AnyTable RegularIdentifier TableElementList 'CURSOR'
   {
     if (isHive() || isImpala()) {
       suggestKeywords(['LOCATION']);
     }
   }
 | AnyCreate AnyTable RegularIdentifier TableElementList
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
 : RegularIdentifier PrimitiveType
 | RegularIdentifier 'CURSOR'
   {
     suggestTypeKeywords();
   }
 | RegularIdentifier 'CURSOR' ColumnDefinitionError error
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
     suggestTypeKeywords();
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
 | HiveDescribeStatement_EDIT
 | ImpalaDescribeStatement
 ;

HiveDescribeStatement
 : '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalExtended DatabaseIdentifier
 ;

HiveDescribeStatement_EDIT
 : '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier_EDIT
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain_EDIT
   {
     addTablePrimary($3);
     suggestColumns($4);
     linkTablePrimaries();
   }
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier 'CURSOR'
   {
     addTablePrimary($3);
     suggestColumns();
     linkTablePrimaries();
   }
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted 'CURSOR'
   {
     if (!$2) {
       suggestKeywords(['DATABASE', 'EXTENDED', 'FORMATTED', 'SCHEMA']);
     }
     suggestTables();
     suggestDatabases({ appendDot: true });
    }
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalExtended DatabaseIdentifier_EDIT
   {
     if (!$3) {
       suggestKeywords(['EXTENDED']);
     }
   }
 ;

ImpalaDescribeStatement
 : '<impala>DESCRIBE' OptionalFormatted SchemaQualifiedTableIdentifier
 | '<impala>DESCRIBE' OptionalFormatted SchemaQualifiedTableIdentifier_EDIT
 | '<impala>DESCRIBE' OptionalFormatted 'CURSOR' SchemaQualifiedTableIdentifier
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
 | 'DROP' DatabaseOrSchema OptionalIfExists RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict
 | 'DROP' DatabaseOrSchema OptionalIfExists_EDIT RegularOrBacktickedIdentifier OptionalHiveCascadeOrRestrict
 ;

DropTableStatement
 : 'DROP' AnyTable OptionalIfExists
 | 'DROP' AnyTable OptionalIfExists_EDIT
 | 'DROP' AnyTable OptionalIfExists 'CURSOR'
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
 | 'DROP' AnyTable OptionalIfExists TablePrimary_EDIT
   {
     if ($4.identifierChain && $4.identifierChain.length === 1) {
       suggestTablesOrColumns($4.identifierChain[0].name);
     } else if ($4.identifierChain && $4.identifierChain.length === 0) {
       suggestTables();
       suggestDatabases({ appendDot: true });
     }
   }
 | 'DROP' AnyTable OptionalIfExists_EDIT TablePrimary
 | 'DROP' AnyTable OptionalIfExists TablePrimary 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['PURGE']);
     }
   }
 ;



// ===================================== LOAD statement =====================================

LoadStatement
 : HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath 'INTO' AnyTable RegularIdentifier
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

QuerySpecification
 : 'SELECT' OptionalAllOrDistinct SelectList // TODO: Needed?
 | 'SELECT' OptionalAllOrDistinct SelectList TableExpression
   {
     linkTablePrimaries();
   }
 ;

QuerySpecification_EDIT
 : 'SELECT' OptionalAllOrDistinct SelectList_EDIT
   {
     if ($3.cursorAtStart) {
       if ($2) {
         suggestKeywords(['*']);
       } else {
         suggestKeywords(['*', 'ALL', 'DISTINCT']);
       }
     } else {
       checkForKeywords($3);
     }

     if ($3.suggestAggregateFunctions && (!$2 || $2 === 'ALL')) {
       suggestAggregateFunctions();
     }
   }
 | 'SELECT' OptionalAllOrDistinct 'CURSOR'
   {
     if ($2) {
       suggestKeywords(['*']);
       if ($2 === 'ALL') {
         suggestAggregateFunctions();
       }
     } else {
       suggestKeywords(['*', 'ALL', 'DISTINCT']);
       suggestAggregateFunctions();
     }
     suggestFunctions();
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'SELECT' OptionalAllOrDistinct SelectList TableExpression_EDIT
   {
     linkTablePrimaries();
   }
 | 'SELECT' OptionalAllOrDistinct SelectList_EDIT TableExpression
   {
     if ($3.cursorAtStart) {
       if ($2) {
         suggestKeywords(['*']);
       } else {
         suggestKeywords(['*', 'ALL', 'DISTINCT']);
       }
     } else {
       checkForKeywords($3);
     }

     if ($3.suggestAggregateFunctions && (!$2 || $2 === 'ALL')) {
       suggestAggregateFunctions();
     }
     linkTablePrimaries();
   }
 | 'SELECT' OptionalAllOrDistinct 'CURSOR' TableExpression
   {
     if ($2) {
       suggestKeywords(['*']);
       if ($2 === 'ALL') {
         suggestAggregateFunctions();
       }
     } else {
       suggestKeywords(['*', 'ALL', 'DISTINCT']);
       suggestAggregateFunctions();
     }
     suggestFunctions();
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
     linkTablePrimaries();
   }
 | 'SELECT' OptionalAllOrDistinct error TableExpression
   {
     linkTablePrimaries();
   }
 | 'SELECT' OptionalAllOrDistinct error TableExpression_EDIT
   {
     linkTablePrimaries();
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' TableExpression
   {
     checkForKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' ',' TableExpression
   {
     checkForKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' ',' error TableExpression
   {
     checkForKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR'
   {
     checkForKeywords($3);
     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   }
 ;

OptionalAllOrDistinct
 :
 | '<hive>ALL'
 | 'ALL'
 | 'DISTINCT'
 ;

TableExpression
 : FromClause SelectConditions
 ;

TableExpression_EDIT
 : FromClause SelectConditions_EDIT
 | FromClause_EDIT SelectConditions
 | FromClause SelectConditions 'CURSOR'
   {
     if ($2.suggestKeywords && $2.suggestKeywords.length == 0) {
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
     } else {
       checkForKeywords($2);
     }
   }
 ;

FromClause
 : 'FROM' TableReferenceList
   {
     $$ = $2;
   }
 ;

FromClause_EDIT
 : 'FROM' TableReferenceList_EDIT
 | 'FROM' 'CURSOR'
   {
       suggestTables();
       suggestDatabases({ appendDot: true });
   }
 ;

SelectConditions
 : OptionalWhereClause OptionalGroupByClause OptionalOrderByClause OptionalLimitClause
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

SelectConditions_EDIT
 : OptionalWhereClause_EDIT OptionalGroupByClause OptionalOrderByClause OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause_EDIT OptionalOrderByClause OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause OptionalOrderByClause_EDIT OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause OptionalOrderByClause OptionalLimitClause_EDIT
 ;

OptionalWhereClause
 :
 | 'WHERE' SearchCondition         -> $2
 ;

OptionalWhereClause_EDIT
 : 'WHERE' SearchCondition_EDIT
 | 'WHERE' 'CURSOR'
   {
     suggestFunctions();
     suggestColumns();
     suggestKeywords(['EXISTS', 'NOT EXISTS']);
   }
 ;

OptionalGroupByClause
 :
 | AnyGroup 'BY' GroupByColumnList
 ;

OptionalGroupByClause_EDIT
 : AnyGroup 'BY' GroupByColumnList_EDIT
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

GroupByColumnList
 : DerivedColumnOrUnsignedInteger
 | GroupByColumnList, DerivedColumnOrUnsignedInteger
 ;

GroupByColumnList_EDIT
 : DerivedColumnOrUnsignedInteger_EDIT
 | 'CURSOR' DerivedColumnOrUnsignedInteger
   {
     suggestColumns();
   }
 | GroupByColumnList ',' GroupByColumnListPartTwo_EDIT
 | GroupByColumnList ',' GroupByColumnListPartTwo_EDIT ','
 | GroupByColumnList ',' GroupByColumnListPartTwo_EDIT ',' GroupByColumnList
 ;

GroupByColumnListPartTwo_EDIT
 : DerivedColumnOrUnsignedInteger_EDIT
 | AnyCursor
   {
     suggestColumns();
   }
 ;

OptionalOrderByClause
 :
 | 'ORDER' 'BY' OrderByColumnList         -> $3
 ;

OptionalOrderByClause_EDIT
 : 'ORDER' 'BY' OrderByColumnList_EDIT
 | 'ORDER' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

OrderByColumnList
 : OrderByIdentifier
 | OrderByColumnList ',' OrderByIdentifier         -> $3
 ;

OrderByColumnList_EDIT
 : OrderByIdentifier_EDIT
 | 'CURSOR' OrderByIdentifier
   {
     suggestColumns();
   }
 | OrderByColumnList ',' OrderByIdentifier_EDIT
 | OrderByColumnList ',' OrderByIdentifier_EDIT ','
 | OrderByColumnList ',' OrderByIdentifier_EDIT ',' OrderByColumnList
 ;

OrderByIdentifier
 : DerivedColumnOrUnsignedInteger OptionalAscOrDesc OptionalImpalaNullsFirstOrLast
   {
     $$ = mergeSuggestKeywords($2, $3);
   }
 ;

OrderByIdentifier_EDIT
 : DerivedColumnOrUnsignedInteger_EDIT OptionalAscOrDesc OptionalImpalaNullsFirstOrLast
 | DerivedColumnOrUnsignedInteger OptionalAscOrDesc OptionalImpalaNullsFirstOrLast_EDIT
 | AnyCursor OptionalAscOrDesc OptionalImpalaNullsFirstOrLast
   {
     suggestColumns();
   }
 ;

DerivedColumnOrUnsignedInteger
 : DerivedColumn_TWO
 | 'UNSIGNED_INTEGER'
 ;

DerivedColumnOrUnsignedInteger_EDIT
 : DerivedColumn_EDIT_TWO
 ;

OptionalAscOrDesc
 :
  {
    $$ = { suggestKeywords: ['ASC', 'DESC'] }
  }
 | 'ASC'
 | 'DESC'
 ;

OptionalImpalaNullsFirstOrLast
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

OptionalImpalaNullsFirstOrLast_EDIT
 : '<impala>NULLS' 'CURSOR'
   {
     suggestKeywords(['FIRST', 'LAST']);
   }
 ;

OptionalLimitClause
 :
 | 'LIMIT' 'UNSIGNED_INTEGER'
 ;

OptionalLimitClause_EDIT
 : 'LIMIT' 'CURSOR'
   {
     suggestNumbers([1, 5, 10]);
   }
 ;

SearchCondition
 : ValueExpression
 ;

SearchCondition_EDIT
 : ValueExpression_EDIT
 ;

ValueExpression
 : NonParenthesizedValueExpressionPrimary                                           -> valueExpressionKeywords($1)
// | NumericValueFunction                                                           -> valueExpressionKeywords($1)
 | 'NOT' ValueExpression                                                            -> valueExpressionKeywords($2)
 | '!' ValueExpression                                                              -> valueExpressionKeywords($2)
 | '~' ValueExpression                                                              -> valueExpressionKeywords($2)
 | '-' ValueExpression %prec NEGATION                                               -> valueExpressionKeywords()
 | 'EXISTS' TableSubquery
   {
     $$ = valueExpressionKeywords();
     // clear correlated flag after completed subquery (set by lexer)
     parser.yy.correlatedSubquery = false;
   }
 | ValueExpression 'NOT' 'LIKE' SingleQuotedValue                                   -> valueExpressionKeywords()
 | ValueExpression 'LIKE' SingleQuotedValue                                         -> valueExpressionKeywords()
 | ValueExpression 'RLIKE' SingleQuotedValue                                        -> valueExpressionKeywords()
 | ValueExpression 'REGEXP' SingleQuotedValue                                       -> valueExpressionKeywords()
 | '(' ValueExpression ')'                                                          -> valueExpressionKeywords()
 | ValueExpression 'IS' OptionalNot 'NULL'                                          -> valueExpressionKeywords()
 | ValueExpression '=' ValueExpression                                              -> valueExpressionKeywords()
 | ValueExpression 'COMPARISON_OPERATOR' ValueExpression                            -> valueExpressionKeywords()
 | ValueExpression '-' ValueExpression                                              -> valueExpressionKeywords()
 | ValueExpression '*' ValueExpression                                              -> valueExpressionKeywords()
 | ValueExpression 'ARITHMETIC_OPERATOR' ValueExpression                            -> valueExpressionKeywords()
 | ValueExpression 'OR' ValueExpression                                             -> valueExpressionKeywords()
 | ValueExpression 'AND' ValueExpression                                            -> valueExpressionKeywords()
 ;

ValueExpression
 : ValueExpression 'NOT' 'IN' '(' TableSubqueryInner ')'                            -> valueExpressionKeywords()
 | ValueExpression 'NOT' 'IN' '(' InValueList ')'                                   -> valueExpressionKeywords()
 | ValueExpression 'IN' '(' TableSubqueryInner ')'                                  -> valueExpressionKeywords()
 | ValueExpression 'IN' '(' InValueList ')'                                         -> valueExpressionKeywords()
 ;

ValueExpression
 : ValueExpression 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression    -> valueExpressionKeywords()
 | ValueExpression 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression          -> valueExpressionKeywords()
 ;

ValueExpression_EDIT
 : NonParenthesizedValueExpressionPrimary_EDIT
 | 'NOT' ValueExpression_EDIT                               -> $2
 | 'NOT' 'CURSOR'
   {
     suggestFunctions();
     suggestColumns();
     suggestKeywords(['EXISTS']);
   }
 | '!' ValueExpression_EDIT                                 -> $2
 | '!' AnyCursor
   {
     suggestFunctions();
     suggestColumns();
   }
 | '~' ValueExpression_EDIT                                 -> $2
 | '~' 'PARTIAL_CURSOR'
   {
     suggestFunctions();
     suggestColumns();
   }
 | '-' ValueExpression_EDIT %prec NEGATION                  -> $2
 | '-' 'PARTIAL_CURSOR' %prec NEGATION
   {
     suggestFunctions();
     suggestColumns();
   }
 | 'EXISTS' TableSubquery_EDIT
 | ValueExpression_EDIT 'NOT' 'LIKE' SingleQuotedValue      -> $1
 | ValueExpression_EDIT 'LIKE' SingleQuotedValue            -> $1
 | ValueExpression_EDIT 'RLIKE' SingleQuotedValue           -> $1
 | ValueExpression_EDIT 'REGEXP' SingleQuotedValue          -> $1
 | ValueExpression_EDIT 'NOT' 'EXISTS' TableSubquery        -> $1
 | ValueExpression_EDIT 'EXISTS' TableSubquery              -> $1
 | '(' ValueExpression_EDIT RightParenthesisOrError         -> $2
 | ValueExpression 'IS' 'NOT' 'CURSOR'
   {
     suggestKeywords(['NULL']);
   }
 | ValueExpression 'IS' 'CURSOR'
   {
     suggestKeywords(['NOT NULL', 'NULL']);
   }
 | ValueExpression 'IS' 'CURSOR' 'NULL'
   {
     suggestKeywords(['NOT']);
   }
 | ValueExpression 'NOT' 'CURSOR'
   {
     suggestKeywords(['BETWEEN', 'EXISTS', 'IN', 'LIKE']);
   }
 ;

ValueExpression_EDIT
 : ValueExpression 'NOT' 'IN' ValueExpressionInSecondPart_EDIT
   {
     if ($4.inValueEdit) {
       valueExpressionSuggest($1)
     }
     if ($4.cursorAtStart) {
       suggestKeywords(['SELECT']);
     }
   }
 | ValueExpression 'IN' ValueExpressionInSecondPart_EDIT
   {
     if ($3.inValueEdit) {
       valueExpressionSuggest($1)
     }
     if ($3.cursorAtStart) {
       suggestKeywords(['SELECT']);
     }
   }
 | ValueExpression_EDIT 'NOT' 'IN' '(' InValueList RightParenthesisOrError
 | ValueExpression_EDIT 'NOT' 'IN' '(' TableSubqueryInner RightParenthesisOrError
 | ValueExpression_EDIT 'IN' '(' InValueList RightParenthesisOrError
 | ValueExpression_EDIT 'IN' '(' TableSubqueryInner RightParenthesisOrError
 ;

ValueExpressionInSecondPart_EDIT
 : '(' TableSubqueryInner_EDIT RightParenthesisOrError
 | '(' InValueList_EDIT RightParenthesisOrError           -> { inValueEdit: true }
 | '(' AnyCursor RightParenthesisOrError                  -> { inValueEdit: true, cursorAtStart: true }
 ;

ValueExpression_EDIT
 : ValueExpression_EDIT 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression_EDIT 'BETWEEN_AND' ValueExpression
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression_EDIT
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' 'CURSOR'
   {
     valueExpressionSuggest($1);
   }
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression 'CURSOR'
   {
     suggestKeywords(['AND']);
   }
 | ValueExpression 'NOT' 'BETWEEN' 'CURSOR'
   {
     valueExpressionSuggest($1);
   }
 | ValueExpression_EDIT 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression
 | ValueExpression 'BETWEEN' ValueExpression_EDIT 'BETWEEN_AND' ValueExpression
 | ValueExpression 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression_EDIT
 | ValueExpression 'BETWEEN' ValueExpression 'BETWEEN_AND' 'CURSOR'
   {
     valueExpressionSuggest($1);
   }
 | ValueExpression 'BETWEEN' ValueExpression 'CURSOR'
   {
     suggestKeywords(['AND']);
   }
 | ValueExpression 'BETWEEN' 'CURSOR'
   {
     valueExpressionSuggest($1);
   }
 ;

ValueExpression_EDIT
 : ValueExpression '=' ValueExpression_EDIT
 | ValueExpression 'COMPARISON_OPERATOR' ValueExpression_EDIT
 | ValueExpression '-' ValueExpression_EDIT
 | ValueExpression '*' ValueExpression_EDIT
 | ValueExpression 'ARITHMETIC_OPERATOR' ValueExpression_EDIT
 | ValueExpression 'OR' ValueExpression_EDIT
 | ValueExpression 'AND' ValueExpression_EDIT
 | ValueExpression '=' RightPart_EDIT { valueExpressionSuggest($1) }
 | ValueExpression 'COMPARISON_OPERATOR' RightPart_EDIT { valueExpressionSuggest($1) }
 | ValueExpression '-' RightPart_EDIT { valueExpressionSuggest() }
 | ValueExpression '*' RightPart_EDIT { valueExpressionSuggest() }
 | ValueExpression 'ARITHMETIC_OPERATOR' RightPart_EDIT { valueExpressionSuggest() }
 | ValueExpression 'OR' RightPart_EDIT { valueExpressionSuggest() }
 | ValueExpression 'AND' RightPart_EDIT { valueExpressionSuggest() }
 ;

ValueExpression_EDIT
 : ValueExpression_EDIT '=' ValueExpression
 | ValueExpression_EDIT 'COMPARISON_OPERATOR' ValueExpression
 | ValueExpression_EDIT '-' ValueExpression
 | ValueExpression_EDIT '*' ValueExpression
 | ValueExpression_EDIT 'ARITHMETIC_OPERATOR' ValueExpression
 | ValueExpression_EDIT 'OR' ValueExpression
 | ValueExpression_EDIT 'AND' ValueExpression
 | 'CURSOR' '=' ValueExpression { valueExpressionSuggest($3) }
 | 'CURSOR' 'COMPARISON_OPERATOR' ValueExpression { valueExpressionSuggest($3) }
// | 'CURSOR' '-' ValueExpression { valueExpressionSuggest() }
 | 'CURSOR' '*' ValueExpression { valueExpressionSuggest() }
 | 'CURSOR' 'ARITHMETIC_OPERATOR' ValueExpression { valueExpressionSuggest() }
 | 'CURSOR' 'OR' ValueExpression { valueExpressionSuggest() }
 | 'CURSOR' 'AND' ValueExpression { valueExpressionSuggest() }
 ;

ValueExpressionList
 : ValueExpression                                                         -> $1
 | ValueExpressionList ',' ValueExpression                                 -> $3
 ;

ValueExpressionList_EDIT
 : ValueExpression_EDIT
 | ValueExpressionList ',' ValueExpression_EDIT
 | ValueExpression_EDIT ',' ValueExpressionList
 | ValueExpressionList ',' ValueExpression_EDIT ',' ValueExpressionList
 | ValueExpressionList ',' AnyCursor
   {
     valueExpressionSuggest();
   }
 | ValueExpressionList ',' AnyCursor ',' ValueExpressionList
   {
     valueExpressionSuggest();
   }
 | AnyCursor ',' ValueExpressionList
   {
     valueExpressionSuggest();
   }
 | AnyCursor ','
   {
     valueExpressionSuggest();
   }
 | ',' AnyCursor
   {
     valueExpressionSuggest();
   }
 | ',' AnyCursor ',' ValueExpressionList
   {
     valueExpressionSuggest();
   }
 ;

InValueList
 : NonParenthesizedValueExpressionPrimary
 | InValueList ',' NonParenthesizedValueExpressionPrimary
 ;

InValueList_EDIT
 : NonParenthesizedValueExpressionPrimary_EDIT
 | InValueList ',' AnyCursor
 | InValueList ',' NonParenthesizedValueExpressionPrimary_EDIT
 | InValueList ',' NonParenthesizedValueExpressionPrimary_EDIT ',' InValueList
 | NonParenthesizedValueExpressionPrimary_EDIT ',' InValueList
 ;

RightPart_EDIT
 : AnyCursor
 | PartialBacktickedIdentifier
 ;

// TODO: Expand with more choices
NonParenthesizedValueExpressionPrimary
 : UnsignedValueSpecification
 | ColumnReference
   {
     $$ = { columnReference: $1 };
   }
 | UserDefinedFunction
 | GroupingOperation
 | HiveComplexTypeConstructor
 | 'NULL'
 ;

NonParenthesizedValueExpressionPrimary_EDIT
 : ColumnReference_EDIT
 | UserDefinedFunction_EDIT
 | HiveComplexTypeConstructor_EDIT
 ;

UnsignedValueSpecification
 : UnsignedLiteral
// | GeneralValueSpecification
 ;

UnsignedLiteral
 : UnsignedNumericLiteral
 | GeneralLiteral
 ;

UnsignedNumericLiteral
 : ExactNumericLiteral
 | ApproximateNumericLiteral
 ;

ExactNumericLiteral
 : 'UNSIGNED_INTEGER'
 | 'UNSIGNED_INTEGER' '.'
 | 'UNSIGNED_INTEGER' '.' 'UNSIGNED_INTEGER'
 | '.' 'UNSIGNED_INTEGER'
 ;

ApproximateNumericLiteral
 : UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 | '.' UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 | 'UNSIGNED_INTEGER' '.' UNSIGNED_INTEGER_E 'UNSIGNED_INTEGER'
 ;

GeneralLiteral
 : SingleQuotedValue
 ;

TruthValue
 : 'TRUE'
 | 'FALSE'
 ;

OptionalNot
 :
 | 'NOT'
 ;

ColumnReferenceList
 : ColumnReference
 | ColumnReferenceList ',' ColumnReference
 ;

ColumnReference
 : BasicIdentifierChain
 | BasicIdentifierChain AnyDot '*'
 ;

ColumnReference_EDIT
 : BasicIdentifierChain_EDIT
 ;

BasicIdentifierChain
 : Identifier
   {
     $$ = [ $1 ];
   }
 | BasicIdentifierChain AnyDot Identifier
   {
     $$ = $1.concat($3);
   }
 ;

BasicIdentifierChain_EDIT
 : Identifier_EDIT
 | BasicIdentifierChain AnyDot Identifier_EDIT
 | BasicIdentifierChain AnyDot PartialBacktickedOrPartialCursor
   {
     $$ = {
       suggestKeywords: ['*']
     }
     suggestColumns({
       identifierChain: $1
     });
   }
 ;

Identifier
 : ColumnIdentifier
 | DoubleQuotedValue
   {
     $$ = { name: $1 }
   }
 ;

Identifier_EDIT
 : ColumnIdentifier 'PARTIAL_CURSOR'
   {
     suggestColumns();
   }
 ;

SelectSubList
 : ValueExpression OptionalCorrelationName         -> $2 // <derived column>
 | '*'
 ;

SelectSubList_EDIT
 : ValueExpression_EDIT OptionalCorrelationName         -> $1
 | ValueExpression OptionalCorrelationName_EDIT         -> $2
 ;

SelectList
 : SelectSubList
 | SelectList ',' SelectSubList         -> $3
 ;

SelectList_EDIT
 : SelectSubList_EDIT
 | 'CURSOR' SelectList
   {
     $$ = { cursorAtStart : true, suggestAggregateFunctions: true };
     suggestFunctions();
     suggestColumns();
     suggestFunctions();
   }
 | SelectList ',' SelectListPartTwo_EDIT                        -> $3
 | SelectList ',' SelectListPartTwo_EDIT ','                    -> $3
 | SelectList ',' SelectListPartTwo_EDIT ',' SelectList         -> $3
 ;

SelectListPartTwo_EDIT
 : SelectSubList_EDIT
 | AnyCursor
   {
     $$ = { suggestKeywords: ['*'], suggestAggregateFunctions: true };
     suggestFunctions();
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 ;

DerivedColumn_TWO
 : ColumnIdentifier
 | ColumnIdentifier AnyDot '*'
 | ColumnIdentifier AnyDot DerivedColumnChain
 ;

DerivedColumn_EDIT_TWO
 : ColumnIdentifier AnyDot PartialBacktickedOrPartialCursor
   {
     // TODO: Check if valid: SELECT testMap["key"].* FROM foo
     if (typeof $1.key === 'undefined') {
       parser.yy.result.suggestStar = true;
     }
     suggestColumns({
       identifierChain: [ $1 ]
     });
   }
 | ColumnIdentifier AnyDot DerivedColumnChain '<impala>.' 'PARTIAL_CURSOR'
   {
      $3.unshift($1);
      suggestColumns({
        identifierChain: $3
      });
    }
 | ColumnIdentifier AnyDot DerivedColumnChain '<hive>.' 'PARTIAL_CURSOR'
   {
      $3.unshift($1);
      suggestColumns({
        identifierChain: $3
      });
    }
 ;

TableReferenceList
 : TableReference
 | TableReferenceList ',' TableReference         -> $3
 ;

TableReferenceList_EDIT
 : TableReference_EDIT
 | TableReferenceList_EDIT ',' TableReference
 | TableReferenceList ',' TableReference_EDIT
 | TableReferenceList ',' 'CURSOR'
   {
       suggestTables();
       suggestDatabases({ appendDot: true });
   }
 ;

TableReference
 : TablePrimaryOrJoinedTable
 ;

TableReference_EDIT
 : TablePrimaryOrJoinedTable_EDIT
 ;

TablePrimaryOrJoinedTable
 : TablePrimary
 | JoinedTable
 ;

TablePrimaryOrJoinedTable_EDIT
 : TablePrimary_EDIT
 | JoinedTable_EDIT
 ;

JoinedTable
 : TablePrimary Joins         -> $2
 ;

JoinedTable_EDIT
 : TablePrimary Joins_EDIT
 | TablePrimary_EDIT Joins
 ;

// TODO: Joins 'JOIN' Joins
Joins
 : JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary
   {
     $$ = { hasJoinCondition: false }
   }
 | JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition
   {
     $$ = { hasJoinCondition: true }
   }
 | Joins JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary
   {
     $$ = { hasJoinCondition: false }
   }
 | Joins JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition
   {
     $$ = { hasJoinCondition: true }
   }
 ;

OptionalImpalaBroadcastOrShuffle
 :
 | '<impala>BROADCAST'
 | '<impala>SHUFFLE'
 ;

Joins_EDIT
 : JoinTypes_EDIT 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary
 | JoinTypes_EDIT 'JOIN' OptionalImpalaBroadcastOrShuffle
 | JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary_EDIT
 | JoinTypes_EDIT 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition
 | JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary_EDIT JoinCondition
 | JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition_EDIT
 | Joins_EDIT JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary
 | Joins JoinTypes_EDIT 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary
 | Joins JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary_EDIT
 | Joins_EDIT JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition
 | Joins JoinTypes_EDIT 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition
 | Joins JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary_EDIT JoinCondition
 | Joins JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition_EDIT
 | JoinsTableSuggestions_EDIT
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 ;

JoinsTableSuggestions_EDIT
 : JoinTypes 'JOIN' 'CURSOR'
 | JoinTypes 'JOIN' 'CURSOR' JoinCondition
 | Joins JoinTypes 'JOIN' 'CURSOR'
 | Joins JoinTypes 'JOIN' 'CURSOR' JoinCondition
 ;

JoinTypes
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

JoinTypes_EDIT
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

JoinCondition
 : 'ON' JoinEqualityExpression
 | 'ON' ParenthesizedJoinEqualityExpression
 ;

JoinCondition_EDIT
 : 'ON' JoinEqualityExpression_EDIT
 | 'ON' ParenthesizedJoinEqualityExpression_EDIT
 | 'ON' 'CURSOR'
   {
     suggestColumns();
   }
 ;

ParenthesizedJoinEqualityExpression
 : '(' JoinEqualityExpression ')'
 ;

ParenthesizedJoinEqualityExpression_EDIT
 : '(' JoinEqualityExpression_EDIT RightParenthesisOrError
 | '(' PartialBacktickedOrPartialCursor RightParenthesisOrError
   {
     suggestColumns();
   }
 | '(' PartialBacktickedOrPartialCursor 'AND' JoinEqualityExpression RightParenthesisOrError
    {
      suggestColumns();
    }
 ;

JoinEqualityExpression
 : EqualityExpression
 | JoinEqualityExpression 'AND' EqualityExpression
 ;

JoinEqualityExpression_EDIT
 : EqualityExpression_EDIT
 | EqualityExpression_EDIT 'AND' JoinEqualityExpression
 | 'CURSOR' 'AND' JoinEqualityExpression
   {
     suggestColumns();
   }
 | JoinEqualityExpression 'AND' EqualityExpression_EDIT
 | JoinEqualityExpression 'AND' PartialBacktickedOrCursor
   {
     suggestColumns();
   }
 | JoinEqualityExpression 'AND' EqualityExpression_EDIT 'AND' JoinEqualityExpression
 | JoinEqualityExpression 'AND' PartialBacktickedOrCursor 'AND' JoinEqualityExpression
   {
     suggestColumns();
   }
 ;

EqualityExpression
 : ColumnReference '=' ColumnReference
 ;

EqualityExpression_EDIT
 : ColumnReference '=' ColumnReference_EDIT
 | ColumnReference_EDIT '=' ColumnReference
 | ColumnReference '=' 'CURSOR'
   {
     suggestColumns();
   }
 | 'CURSOR' '=' ColumnReference
   {
     suggestColumns();
   }
 | 'PARTIAL_CURSOR' '=' ColumnReference
   {
     suggestColumns();
   }
 | ColumnReference '=' 'PARTIAL_CURSOR'
   {
     suggestColumns();
   }
 | ColumnReference_EDIT
 ;

TablePrimary
 : TableOrQueryName OptionalCorrelationName OptionalLateralViews
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
 | DerivedTable OptionalCorrelationName
   {
     if ($2 && !$2.suggestKeywords) {
       // TODO: Potentially add columns for SELECT bla.| FROM (SELECT * FROM foo) AS bla;
       addTablePrimary({ subqueryAlias: $2 });
     }
   }
 ;

TablePrimary_EDIT
 : TableOrQueryName_EDIT OptionalCorrelationName OptionalLateralViews
 | TableOrQueryName OptionalCorrelationName OptionalLateralViews_EDIT
   {
     if ($2 && !$2.suggestKeywords) {
       $1.alias = $2;
     }
     addTablePrimary($1);
   }
 | DerivedTable_EDIT OptionalCorrelationName
   {
     if ($2 && !$2.suggestKeywords) {
       // TODO: Potentially add columns for SELECT bla.| FROM (SELECT * FROM foo) AS bla;
       addTablePrimary({ subqueryAlias: $2 });
     }
   }
 | DerivedTable OptionalCorrelationName_EDIT // TODO: OptionalLateralViews?
 ;

TableOrQueryName
 : SchemaQualifiedTableIdentifier
 ;

TableOrQueryName_EDIT
 : SchemaQualifiedTableIdentifier_EDIT
 ;

DerivedTable
 : TableSubquery
 ;

DerivedTable_EDIT
 : TableSubquery_EDIT
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
     if (parser.yy.correlatedSubquery) {
       parser.yy.latestTablePrimaries = parser.yy.latestTablePrimaries.concat();
     } else {
       parser.yy.latestTablePrimaries = [];
     }
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

TableSubquery
 : '(' TableSubqueryInner ')'
 ;

TableSubquery_EDIT
 : '(' TableSubqueryInner_EDIT RightParenthesisOrError
 | '(' AnyCursor RightParenthesisOrError
   {
     suggestKeywords(['SELECT']);
   }
 ;

TableSubqueryInner
 : PushQueryState Subquery PopQueryState
 ;

TableSubqueryInner_EDIT
 : PushQueryState Subquery_EDIT PopQueryState
 ;

Subquery
 : QueryExpression
 ;

Subquery_EDIT
 : QueryExpression_EDIT
 ;

QueryExpression
 : QueryExpressionBody
 ;

QueryExpression_EDIT
 : QueryExpressionBody_EDIT
 ;

QueryExpressionBody
 : NonJoinQueryExpression
 ;

QueryExpressionBody_EDIT
 : NonJoinQueryExpression_EDIT
 ;

NonJoinQueryExpression
 : NonJoinQueryTerm
 ;

NonJoinQueryExpression_EDIT
 : NonJoinQueryTerm_EDIT
 ;

NonJoinQueryTerm
 : NonJoinQueryPrimary
 ;

NonJoinQueryTerm_EDIT
 : NonJoinQueryPrimary_EDIT
 ;

NonJoinQueryPrimary
 : SimpleTable
 ;

NonJoinQueryPrimary_EDIT
 : SimpleTable_EDIT
 ;

SimpleTable
 : QuerySpecification
 ;

SimpleTable_EDIT
 : QuerySpecification_EDIT
 ;

OptionalCorrelationName
 :
   {
     $$ = { suggestKeywords: ['AS'] }
   }
 | RegularOrBacktickedIdentifier
 | AnyAs RegularOrBacktickedIdentifier         -> $2
 ;

OptionalCorrelationName_EDIT
 : PartialBacktickedIdentifier
 | AnyAs PartialBacktickedIdentifier
 | AnyAs 'CURSOR'
 ;

OptionalLateralViews
 :
 | OptionalLateralViews LateralView
   {
     if ($1) {
       $$ = $1.concat($2);
     } else {
       $$ = $2;
     }
   }
 ;

OptionalLateralViews_EDIT
 : OptionalLateralViews LateralView_EDIT OptionalLateralViews
 ;

// TODO: '<hive>[pos]explode' '(' 'CURSOR' possible?
UserDefinedTableGeneratingFunction
 : '<hive>EXPLODE(' DerivedColumnChain ')'
   {
     $$ = { function: $1.substring(0, $1.length - 1), expression: $2 }
   }
 | '<hive>POSEXPLODE(' DerivedColumnChain ')'
   {
     $$ = { function: $1.substring(0, $1.length - 1), expression: $2 }
   }
 ;

UserDefinedTableGeneratingFunction_EDIT
 : '<hive>EXPLODE(' DerivedColumnChain_EDIT error
   {
     suggestColumns($2);
   }
 | '<hive>EXPLODE(' PartialBacktickedOrPartialCursor error
    {
      suggestColumns();
    }
 | '<hive>POSEXPLODE(' PartialBacktickedOrPartialCursor error
    {
      suggestColumns();
    }
 ;

GroupingOperation
 : 'GROUPING' '(' ColumnReferenceList ')'
 ;

OptionalFilterClause
 :
 | 'FILTER' '(' 'WHERE' SearchCondition ')'
 | '<impala>OVER' '(' 'WHERE' SearchCondition ')'
 ;

UserDefinedFunction
 : CountFunction
 | SumFunction
 | CastFunction
 | ArbitraryFunction
 ;

UserDefinedFunction_EDIT
 : CountFunction_EDIT
 | SumFunction_EDIT
 | CastFunction_EDIT
 | ArbitraryFunction_EDIT
 ;

ArbitraryFunction
 : 'UDF(' ')'
 | 'UDF(' ValueExpressionList ')'
   {
     $$ = { function: $1.substring(0, $1.length - 1), expression: $2 };
   }
 ;

ArbitraryFunction_EDIT
 : 'UDF(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
   }
 | 'UDF(' ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     checkForKeywords($2);
   }
 | 'UDF(' ValueExpressionList 'CURSOR' ',' ValueExpressionList RightParenthesisOrError
   {
     checkForKeywords($2);
   }
 | 'UDF(' ValueExpressionList_EDIT RightParenthesisOrError
 ;

CountFunction
 : 'COUNT(' '*' ')'
 | 'COUNT(' OptionalAllOrDistinct ValueExpressionList ')'
 ;

CountFunction_EDIT
 : 'COUNT(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     suggestColumns();
     if (!$2) {
       if (isImpala()) {
         suggestKeywords(['*', 'ALL', 'DISTINCT']);
       } else {
         suggestKeywords(['*', 'DISTINCT']);
       }
     }
   }
 | 'COUNT(' OptionalAllOrDistinct ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     checkForKeywords($3);
   }
 | 'COUNT(' OptionalAllOrDistinct ValueExpressionList_EDIT RightParenthesisOrError
 ;

SumFunction
 : 'SUM(' OptionalAllOrDistinct ValueExpression ')'
 ;

SumFunction_EDIT
 : 'SUM(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     if (!$2) {
       if (isImpala()) {
         suggestKeywords(['ALL', 'DISTINCT']);
       } else {
         suggestKeywords(['DISTINCT']);
       }
     }
   }
 | 'SUM(' OptionalAllOrDistinct ValueExpression 'CURSOR' RightParenthesisOrError
   {
     checkForKeywords($3);
   }
 | 'SUM(' OptionalAllOrDistinct ValueExpression_EDIT RightParenthesisOrError
 ;

CastFunction
 : 'CAST(' ValueExpression AnyAs PrimitiveType ')'
 ;

CastFunction_EDIT
 : 'CAST(' AnyCursor AnyAs PrimitiveType RightParenthesisOrError
   {
     valueExpressionSuggest();
   }
 | 'CAST(' AnyCursor AnyAs RightParenthesisOrError
   {
     valueExpressionSuggest();
   }
 | 'CAST(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
   }
 | 'CAST(' ValueExpression_EDIT AnyAs PrimitiveType RightParenthesisOrError
 | 'CAST(' ValueExpression_EDIT AnyAs RightParenthesisOrError
 | 'CAST(' ValueExpression_EDIT RightParenthesisOrError
 | 'CAST(' ValueExpression 'CURSOR' PrimitiveType RightParenthesisOrError
   {
     suggestKeywords(mergeSuggestKeywords({ suggestKeywords: ['AS'] }, $2).suggestKeywords);
   }
 | 'CAST(' ValueExpression 'CURSOR' RightParenthesisOrError
   {
     suggestKeywords(mergeSuggestKeywords({ suggestKeywords: ['AS'] }, $2).suggestKeywords);
   }
 | 'CAST(' ValueExpression AnyAs 'CURSOR' RightParenthesisOrError
   {
     suggestTypeKeywords();
   }
 | 'CAST(' AnyAs 'CURSOR' RightParenthesisOrError
    {
      suggestTypeKeywords();
    }
 ;

WithinGroupSpecification
 : 'WITHIN' 'GROUP' '(' 'ORDER' 'BY' SortSpecificationList ')'
 ;

LateralView
 : '<hive>LATERAL' 'VIEW' UserDefinedFunction RegularIdentifier LateralViewColumnAliases
   {
     $$ = [{ udtf: $3, tableAlias: $4, columnAliases: $5 }]
   }
 | '<hive>LATERAL' 'VIEW' UserDefinedFunction LateralViewColumnAliases
   {
     $$ = [{ udtf: $3, columnAliases: $4 }]
   }
 ;

LateralView_EDIT
 : '<hive>LATERAL' 'VIEW' UserDefinedFunction_EDIT
 | '<hive>LATERAL' 'VIEW' UserDefinedFunction_EDIT LateralViewColumnAliases
 | '<hive>LATERAL' 'VIEW' UserDefinedFunction RegularIdentifier 'CURSOR'
   {
     $$ = [];
     suggestKeywords(['AS']);
   }
 | '<hive>LATERAL' 'VIEW' UserDefinedFunction 'CURSOR'
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

LateralViewColumnAliases
 : '<hive>AS' RegularIdentifier
   {
     $$ = [ $2 ]
   }
 | '<hive>AS' '(' RegularIdentifier ',' RegularIdentifier ')'
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
 | 'SHOW' 'CURSOR' LIKE SingleQuotedValue
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
 | ShowGrantStatement_EDIT
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
 | 'SHOW' HiveOrImpalaDatabasesOrSchemas 'LIKE' SingleQuotedValue
 | 'SHOW' '<impala>DATABASES' SingleQuotedValue
 ;

ShowFunctionsStatement
 : 'SHOW' '<hive>FUNCTIONS'
 | 'SHOW' '<hive>FUNCTIONS' DoubleQuotedValue
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

ShowGrantStatement
 : 'SHOW' '<hive>GRANT' OptionalPrincipalName
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName 'ON' '<hive>ALL'
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName 'ON' RegularOrBacktickedIdentifier
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName 'ON' AnyTable RegularOrBacktickedIdentifier
 ;

ShowGrantStatement_EDIT
 : 'SHOW' '<hive>GRANT' OptionalPrincipalName_EDIT
   {
     suggestKeywords(['ON']);
   }
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName_EDIT 'ON' '<hive>ALL'
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName 'ON' 'CURSOR'
   {
     suggestKeywords(['ALL', 'TABLE']);
     suggestTables();
   }
 | 'SHOW'  '<hive>GRANT' OptionalPrincipalName 'ON' AnyTable 'CURSOR'
   {
     suggestTables();
   }
 | 'SHOW' '<hive>GRANT' OptionalPrincipalName 'ON' 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['TABLE']);
   }
 | 'SHOW' '<impala>GRANT' 'CURSOR'
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
 : 'SHOW' OptionallyFormattedIndex
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex_EDIT
 | 'SHOW' OptionallyFormattedIndex_EDIT 'ON' RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex_EDIT 'ON' RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex 'CURSOR'
   {
     suggestKeywords(['ON']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' 'CURSOR'
   {
     suggestTables();
   }
 | 'SHOW' OptionallyFormattedIndex 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['ON']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier 'CURSOR'
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier 'CURSOR' RegularOrBacktickedIdentifier
   {
     suggestKeywords(['FROM', 'IN']);
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier AnyFromOrIn 'CURSOR'
   {
     suggestDatabases();
   }
 | 'SHOW' OptionallyFormattedIndex 'ON' 'CURSOR' AnyFromOrIn RegularOrBacktickedIdentifier
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
 | 'SHOW' HiveOrImpalaRole 'CURSOR' HiveRoleOrUser RegularIdentifier
   {
     suggestKeywords(['GRANT']);
   }
 | 'SHOW' HiveOrImpalaRole '<hive>GRANT' 'CURSOR'
   {
     suggestKeywords(['ROLE', 'USER']);
   }
 | 'SHOW' HiveOrImpalaRole '<hive>GRANT' 'CURSOR' RegularIdentifier
   {
     suggestKeywords(['ROLE', 'USER']);
   }
 | 'SHOW' HiveOrImpalaRole '<hive>GRANT' HiveRoleOrUser RegularIdentifier
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' 'CURSOR'
   {
     suggestKeywords(['GROUP']);
   }
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' 'CURSOR' RegularIdentifier
   {
     suggestKeywords(['GROUP']);
   }
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' '<impala>GROUP' RegularIdentifier
 ;

ShowRolesStatement
 : 'SHOW' '<impala>ROLES'
 ;

ShowTableStatement
 : 'SHOW' '<hive>TABLE' 'CURSOR'
   {
     suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_EDIT
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'CURSOR'
    {
      if ($4) {
        suggestKeywords(['LIKE']);
      } else {
        suggestKeywords(['FROM', 'IN', 'LIKE']);
      }
    }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_EDIT 'LIKE' SingleQuotedValue
 | 'SHOW' '<hive>TABLE' 'CURSOR' OptionalFromDatabase 'LIKE' SingleQuotedValue
    {
      if (isHive())
        suggestKeywords(['EXTENDED']);
      }
    }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'CURSOR' SingleQuotedValue
    {
      suggestKeywords(['LIKE']);
    }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue 'CURSOR'
    {
      suggestKeywords(['PARTITION']);
    }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_EDIT 'LIKE' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
 | 'SHOW' '<hive>TABLE' 'CURSOR' OptionalFromDatabase 'LIKE' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
   {
     suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'CURSOR' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
   {
     suggestKeywords(['LIKE']);
   }
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue 'CURSOR' PartitionSpecList
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
 | 'SHOW' HiveOrImpalaTables OptionalInDatabase SingleQuotedValue
 | 'SHOW' HiveOrImpalaTables OptionalInDatabase 'LIKE' SingleQuotedValue
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
 : 'UPDATE' TargetTable 'SET' SetClauseList OptionalWhereClause
   {
     linkTablePrimaries();
   }
 | 'UPDATE' TargetTable 'SET' SetClauseList OptionalWhereClause_EDIT
    {
      linkTablePrimaries();
    }
 | 'UPDATE' TargetTable 'SET' SetClauseList OptionalWhereClause 'CURSOR'
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
 : RegularIdentifier
 ;

UpdateSource
 : ValueExpression
 ;


// ===================================== USE Statement =====================================

UseStatement
 : 'USE' RegularIdentifier
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

var valueExpressionKeywords = function (firstRef) {
  var result = { suggestKeywords: ['<', '<=', '<>', '=', '>', '>=', 'AND', 'BETWEEN', 'IN', 'IS NOT NULL', 'IS NULL', 'NOT BETWEEN', 'NOT IN', 'OR'] };
  if (isHive()) {
    result.suggestKeywords.push('<=>');
  }
  if (firstRef && firstRef.columnReference) {
    result.columnReference = firstRef.columnReference;
    result.suggestKeywords.push('LIKE');
    result.suggestKeywords.push('NOT LIKE');
    result.suggestKeywords.push('RLIKE');
    result.suggestKeywords.push('REGEX');
  }
  return result;
}

var suggestTypeKeywords = function () {
  if (isHive()) {
    suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
  } else {
    suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
  }
}

var valueExpressionSuggest = function(other) {
  if (other && other.columnReference) {
    suggestValues({ identifierChain: other.columnReference });
  }
  suggestColumns();
  suggestFunctions();
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
  var beforeMatch = beforeCursor.match(/[0-9a-zA-Z_]*$/);
  var afterMatch = afterCursor.match(/^[0-9a-zA-Z_]*/);
  return { left: beforeMatch ? beforeMatch[0].length : 0, right: afterMatch ? afterMatch[0].length : 0}
};

parser.expandLateralViews = function (tablePrimaries, identifierChain) {
  var firstIdentifier = identifierChain[0];
  var identifierChainParts = [];
  tablePrimaries.forEach(function (tablePrimary) {
    if (typeof tablePrimary.lateralViews !== 'undefined') {
      tablePrimary.lateralViews.reverse().forEach(function (lateralView) {
        if (!lateralView.udtf.expression.columnReference) {
          return;
        }
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
          identifierChain = lateralView.udtf.expression.columnReference.concat(identifierChain);
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

var checkForKeywords = function (rule) {
  if (rule && rule.suggestKeywords && rule.suggestKeywords.length > 0) {
    suggestKeywords(rule.suggestKeywords);
  }
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

var suggestFunctions = function () {
  parser.yy.result.suggestFunctions = true;
}

var suggestAggregateFunctions = function () {
  parser.yy.result.suggestAggregateFunctions = true;
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
    var actualExpected = {};
    result.error.expected.forEach(function (expected) {
      var match = expected.match(/\<([a-z]+)\>(.*)/);
      if (match !== null) {
        if (typeof parser.yy.dialect !== 'undefined' && parser.yy.dialect === match[1]) {
          actualExpected[("'" + match[2])] = true;
        }
      } else if (expected.indexOf('CURSOR') == - 1) {
        actualExpected[expected] = true;
      }
    });
    result.error.expected = Object.keys(actualExpected);
  }

  if (typeof result.error !== 'undefined' && result.error.recoverable) {
    delete result.error;
  }

  return result;
}