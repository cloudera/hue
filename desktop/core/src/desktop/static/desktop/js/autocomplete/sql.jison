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
<hive>'['                           { return '<hive>['; }
<hive>']'                           { return '<hive>]'; }

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
<impala>'REAL'                      { return '<impala>REAL'; }
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
<impala>'['                          { return '<impala>['; }
<impala>']'                          { return '<impala>]'; }

<between>'AND'                      { this.popState(); return 'BETWEEN_AND'; }

'ALL'                               { return 'ALL'; }
'AND'                               { return 'AND'; }
'AS'                                { return 'AS'; }
'ASC'                               { return 'ASC'; }
'BETWEEN'                           { this.begin('between'); return 'BETWEEN'; }
'BIGINT'                            { return 'BIGINT'; }
'BOOLEAN'                           { return 'BOOLEAN'; }
'BY'                                { return 'BY'; }
'CASE'                              { return 'CASE'; }
'CHAR'                              { return 'CHAR'; }
'CREATE'                            { determineCase(yytext); return 'CREATE'; }
'DATABASE'                          { return 'DATABASE'; }
'DECIMAL'                           { return 'DECIMAL'; }
'DESC'                              { return 'DESC'; }
'DISTINCT'                          { return 'DISTINCT'; }
'DOUBLE'                            { return 'DOUBLE'; }
'DROP'                              { determineCase(yytext); return 'DROP'; }
'ELSE'                              { return 'ELSE'; }
'END'                               { return 'END'; }
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
'THEN'                              { return 'THEN'; }
'TIMESTAMP'                         { return 'TIMESTAMP'; }
'TINYINT'                           { return 'TINYINT'; }
'TRUE'                              { return 'TRUE'; }
'UPDATE'                            { determineCase(yytext); return 'UPDATE'; }
'USE'                               { determineCase(yytext); return 'USE'; }
'VARCHAR'                           { return 'VARCHAR'; }
'VIEW'                              { return 'VIEW'; }
'WHEN'                              { return 'WHEN'; }
'WHERE'                             { return 'WHERE'; }
'WITHIN'                            { return 'WITHIN'; }

// --- UDFs ---
'AVG('                              { return 'AVG('; }
'CAST('                             { return 'CAST('; }
'COUNT('                            { return 'COUNT('; }
'MAX('                              { return 'MAX('; }
'MIN('                              { return 'MIN('; }
'STDDEV_POP('                       { return 'STDDEV_POP('; }
'STDDEV_SAMP('                      { return 'STDDEV_SAMP('; }
'SUM('                              { return 'SUM('; }
'VARIANCE('                         { return 'VARIANCE('; }
'VAR_POP('                          { return 'VAR_POP('; }
'VAR_SAMP('                         { return 'VAR_SAMP('; }
<hive>'COLLECT_SET('                { return '<hive>COLLECT_SET('; }
<hive>'COLLECT_LIST('               { return '<hive>COLLECT_LIST('; }
<hive>'CORR('                       { return '<hive>CORR('; }
<hive>'COVAR_POP('                  { return '<hive>COVAR_POP('; }
<hive>'COVAR_SAMP('                 { return '<hive>COVAR_SAMP('; }
<hive>'HISTOGRAM_NUMERIC('          { return '<hive>HISTOGRAM_NUMERIC('; }
<hive>'NTILE('                      { return '<hive>NTILE('; }
<hive>'PERCENTILE('                 { return '<hive>PERCENTILE('; }
<hive>'PERCENTILE_APPROX('          { return '<hive>PERCENTILE_APPROX('; }
<impala>'APPX_MEDIAN('              { return '<impala>APPX_MEDIAN('; }
<impala>'EXTRACT('                  { return '<impala>EXTRACT('; }
<impala>'GROUP_CONCAT('             { return '<impala>GROUP_CONCAT('; }
<impala>'STDDEV('                   { return '<impala>STDDEV('; }
<impala>'VARIANCE_POP('             { return '<impala>VARIANCE_POP('; }
<impala>'VARIANCE_SAMP('            { return '<impala>VARIANCE_SAMP('; }
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

'-'                                 { return '-'; }
'*'                                 { return '*'; }
'+'                                 { return 'ARITHMETIC_OPERATOR'; }
'/'                                 { return 'ARITHMETIC_OPERATOR'; }
'%'                                 { return 'ARITHMETIC_OPERATOR'; }
'|'                                 { return 'ARITHMETIC_OPERATOR'; }
'^'                                 { return 'ARITHMETIC_OPERATOR'; }
'&'                                 { return 'ARITHMETIC_OPERATOR'; }

','                                 { return ','; }
'.'                                 { return '.'; }
';'                                 { return ';'; }
'~'                                 { return '~'; }
'!'                                 { return '!'; }

'('                                 { return '('; }
')'                                 { return ')'; }
'['                                 { return '['; }
']'                                 { return ']'; }

\`                                  { this.begin('backtickedValue'); return 'BACKTICK'; }
<backtickedValue>[^`]+              {
                                      if (yytext.indexOf('\u2020') !== -1 || yytext.indexOf('\u2021') !== -1) {
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

%left ';'
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
     delete parser.yy.correlatedSubquery;
     delete parser.yy.keepColumns;

     parser.parseError = function (message, error) {
       if (typeof parser.yy.result.suggestColumns !== 'undefined') {
         linkTablePrimaries();
       }
       parser.yy.result.error = error;
       return message;
     };
   }
 ;

Sql
 : InitResults SqlStatements EOF
   {
     return parser.yy.result;
   }
 | InitResults SqlStatements_EDIT EOF
   {
     return parser.yy.result;
   }
// | InitResults SqlStatements_EDIT error EOF // TODO: Investigate what this would mean
//    {
//      return parser.yy.result;
//    }
 ;

SqlStatements
 :
 | DataDefinition
 | DataManipulation
 | QuerySpecification
 | SqlStatements ';' SqlStatements
 ;

SqlStatements_EDIT
 : AnyCursor
   {
     suggestDdlAndDmlKeywords();
   }
 | DataDefinition_EDIT
 | DataManipulation_EDIT
 | QuerySpecification_EDIT
   {
     linkTablePrimaries();
   }
 | SqlStatements_EDIT ';' SqlStatements
 | SqlStatements ';' SqlStatements_EDIT
 ;

DataDefinition
 : CreateStatement
 | DescribeStatement
 | DropStatement
 | ShowStatement
 | UseStatement
 ;

DataDefinition_EDIT
 : CreateStatement_EDIT
 | DescribeStatement_EDIT
 | DropStatement_EDIT
 | ShowStatement_EDIT
 | UseStatement_EDIT
 ;

DataManipulation
 : LoadStatement
 | UpdateStatement
 ;

DataManipulation_EDIT
 : LoadStatement_EDIT
 | UpdateStatement_EDIT
   {
     linkTablePrimaries();
   }
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
 : RegularOrBacktickedIdentifier                                       -> { identifierChain: [{ name: $1 }] }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier  -> { identifierChain: [{ name: $1 }, { name: $3 }] }
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
     $$ = { identifierChain: [{ name: $1 }] };
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
     suggestDatabases();
     $$ = { cursorOrPartialIdentifier: true };
   }
 ;

PartitionSpecList
 : PartitionSpec
 | PartitionSpecList ',' PartitionSpec
 ;

PartitionSpec
 : RegularOrBacktickedIdentifier '=' SingleQuotedValue
 ;

RegularOrBacktickedIdentifier
 : RegularIdentifier
 | 'BACKTICK' 'VALUE' 'BACKTICK'  -> $2
 ;

RegularOrBackTickedSchemaQualifiedName
 : RegularOrBacktickedIdentifier                                       -> { identifierChain: [ { name: $1 } ] }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier  -> { identifierChain: [ { name: $1 }, { name: $3 } ] }
 ;

RegularOrBackTickedSchemaQualifiedName_EDIT
 : PartialBacktickedIdentifier
   {
     suggestTables();
     suggestDatabases({ prependDot: true });
   }
 | RegularOrBacktickedIdentifier AnyDot PartialBacktickedOrPartialCursor
   {
     suggestTablesOrColumns($1);
   }
 ;


LocalOrSchemaQualifiedName
 : RegularOrBackTickedSchemaQualifiedName
 | RegularOrBackTickedSchemaQualifiedName RegularOrBacktickedIdentifier  -> { identifierChain: $1.identifierChain, alias: $2 }
 ;

LocalOrSchemaQualifiedName_EDIT
 : RegularOrBackTickedSchemaQualifiedName_EDIT
 | RegularOrBackTickedSchemaQualifiedName_EDIT RegularOrBacktickedIdentifier
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
 : ColumnIdentifier                              -> [ $1 ]
 | BasicIdentifierChain AnyDot ColumnIdentifier
   {
     $1.push($3);
   }
 ;

// TODO: Merge with DerivedColumnChain_EDIT ( issue is starting with PartialBacktickedOrPartialCursor)
BasicIdentifierChain_EDIT
 : ColumnIdentifier_EDIT
   {
     if ($1.insideKey) {
       suggestKeyValues({ identifierChain: [{ name: $1.name }] });
       suggestColumns();
       suggestFunctions();
     }
   }
 | BasicIdentifierChain AnyDot ColumnIdentifier_EDIT
   {
     if ($3.insideKey) {
       suggestKeyValues({ identifierChain: $1.concat({ name: $3.name }) });
       suggestColumns();
       suggestFunctions();
     }
   }
 | BasicIdentifierChain AnyDot ColumnIdentifier_EDIT AnyDot BasicIdentifierChain
 | ColumnIdentifier_EDIT AnyDot BasicIdentifierChain
 | BasicIdentifierChain AnyDot PartialBacktickedOrPartialCursor
   {
     suggestColumns({
       identifierChain: $1
     });
     $$ = { suggestKeywords: ['*'] };
   }
 | BasicIdentifierChain AnyDot PartialBacktickedOrPartialCursor AnyDot BasicIdentifierChain
   {
     suggestColumns({
       identifierChain: $1
     });
     $$ = { suggestKeywords: ['*'] };
   }
 ;

DerivedColumnChain
 : ColumnIdentifier  -> [ $1 ]
 | DerivedColumnChain AnyDot ColumnIdentifier
   {
     $1.push($3);
   }
 ;

DerivedColumnChain_EDIT
 : ColumnIdentifier_EDIT
   {
     if ($1.insideKey) {
       suggestKeyValues({ identifierChain: [{ name: $1.name }] });
       suggestColumns();
       suggestFunctions();
     }
   }
 | DerivedColumnChain AnyDot ColumnIdentifier_EDIT
   {
     if ($3.insideKey) {
       suggestKeyValues({ identifierChain: $1.concat({ name: $3.name }) });
       suggestColumns();
       suggestFunctions();
     }
   }
 | DerivedColumnChain AnyDot ColumnIdentifier_EDIT AnyDot DerivedColumnChain
   {
     if ($3.insideKey) {
       suggestKeyValues({ identifierChain: $1.concat({ name: $3.name }) });
       suggestColumns();
       suggestFunctions();
     }
   }
 | ColumnIdentifier_EDIT AnyDot DerivedColumnChain
   {
     if ($1.insideKey) {
       suggestKeyValues({ identifierChain: [{ name: $1.name }] });
       suggestColumns();
       suggestFunctions();
     }
   }
 | PartialBacktickedIdentifierOrPartialCursor
   {
     suggestColumns();
   }
 | DerivedColumnChain AnyDot PartialBacktickedIdentifierOrPartialCursor
   {
     suggestColumns({ identifierChain: $1 });
   }
 | DerivedColumnChain AnyDot PartialBacktickedIdentifierOrPartialCursor AnyDot DerivedColumnChain
   {
     suggestColumns({ identifierChain: $1 });
   }
 | PartialBacktickedIdentifierOrPartialCursor AnyDot DerivedColumnChain
   {
     suggestColumns();
   }
 ;

ColumnIdentifier
 : RegularOrBacktickedIdentifier OptionalMapOrArrayKey
   {
     if ($2) {
       $$ = { name: $1, keySet: true };
     } else {
       $$ = { name: $1 };
     }
   }
 ;

ColumnIdentifier_EDIT
 : RegularOrBacktickedIdentifier HiveOrImpalaLeftSquareBracket AnyCursor HiveOrImpalaRightSquareBracketOrError
   {
     $$ = { name: $1, insideKey: true }
   }
 | RegularOrBacktickedIdentifier HiveOrImpalaLeftSquareBracket ValueExpression_EDIT HiveOrImpalaRightSquareBracketOrError
   {
     $$ = { name: $1 }
   }
 ;

PartialBacktickedIdentifierOrPartialCursor
 : PartialBacktickedIdentifier
 | 'PARTIAL_CURSOR'
 ;

OptionalMapOrArrayKey
 :
 | HiveOrImpalaLeftSquareBracket ValueExpression HiveOrImpalaRightSquareBracket
 | HiveOrImpalaLeftSquareBracket HiveOrImpalaRightSquareBracket
 ;

HiveOrImpalaRightSquareBracketOrError
 : HiveOrImpalaRightSquareBracket
 | error
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
 | '<impala>REAL'
 | 'STRING'
 | 'DECIMAL'
 | 'CHAR'
 | 'VARCHAR'
 | 'TIMESTAMP'
 | '<hive>BINARY'
 | '<hive>DATE'
 ;

// ===================================== CREATE statement =====================================

CreateStatement
 : TableDefinition
 | DatabaseDefinition
 ;

CreateStatement_EDIT
 : TableDefinition_EDIT
 | DatabaseDefinition_EDIT
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
 : HiveOrImpalaComment SINGLE_QUOTE VALUE SINGLE_QUOTE
 ;

Comment_EDIT
 : HiveOrImpalaComment SINGLE_QUOTE
 | HiveOrImpalaComment SINGLE_QUOTE VALUE
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
 : OptionalComment OptionalHdfsLocation OptionalHiveDbProperties  -> mergeSuggestKeywords($1, $2, $3)
 ;

DatabaseDefinitionOptionals_EDIT
 : OptionalComment OptionalHdfsLocation_EDIT OptionalHiveDbProperties
 | OptionalComment_EDIT OptionalHdfsLocation OptionalHiveDbProperties
 ;

OptionalComment
 : {
     $$ = { suggestKeywords: ['COMMENT'] };
   }
 | Comment
 ;

OptionalComment_EDIT
 : Comment_EDIT
 ;

OptionalHdfsLocation
 :
   {
     $$ = { suggestKeywords: ['LOCATION'] };
   }
 | HdfsLocation
 ;

OptionalHdfsLocation_EDIT
 : HdfsLocation_EDIT
 ;

OptionalHiveDbProperties
 :
   {
     $$ = { suggestKeywords: isHive() ? ['WITH DBPROPERTIES'] : [] };
   }
 | HiveDbProperties
 ;

DatabaseDefinition
 : AnyCreate DatabaseOrSchema OptionalIfNotExists
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier
 ;

DatabaseDefinition_EDIT
 : AnyCreate DatabaseOrSchema OptionalIfNotExists_EDIT
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_EDIT RegularIdentifier
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals_EDIT error
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals 'CURSOR'
   {
     checkForKeywords($5);
   }
 ;

TableDefinition
 : AnyCreate TableScope AnyTable RegularIdentifier TableElementList HdfsLocation
 | AnyCreate AnyTable RegularIdentifier TableElementList
 ;

TableDefinition_EDIT
 : AnyCreate TableScope AnyTable RegularIdentifier TableElementList_EDIT HdfsLocation
 | AnyCreate TableScope AnyTable RegularIdentifier TableElementList HdfsLocation_EDIT
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
 | AnyCreate AnyTable RegularIdentifier TableElementList_EDIT
 ;

TableScope
 : HiveOrImpalaExternal
 ;

TableElementList
 : '(' TableElements ')'
 ;

TableElementList_EDIT
 : '(' TableElements_EDIT RightParenthesisOrError
 ;

TableElements
 : TableElement
 | TableElements ',' TableElement
 ;

TableElements_EDIT
 : TableElement_EDIT
 | TableElements ',' TableElement_EDIT
 | TableElement_EDIT ',' TableElements
 | TableElements ',' TableElement_EDIT ',' TableElements
 ;

TableElement
 : ColumnDefinition
 ;

TableElement_EDIT
 : ColumnDefinition_EDIT
 ;

ColumnDefinition
 : RegularIdentifier PrimitiveType
 ;

ColumnDefinition_EDIT
 : RegularIdentifier 'CURSOR'
   {
     suggestTypeKeywords();
   }
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

HdfsLocation_EDIT
 : HiveOrImpalaLocation HdfsPath_EDIT
 ;

HdfsPath
 : 'HDFS_START_QUOTE' 'HDFS_PATH' 'HDFS_END_QUOTE'
 ;

HdfsPath_EDIT
 : 'HDFS_START_QUOTE' 'HDFS_PATH' 'PARTIAL_CURSOR' 'HDFS_PATH' 'HDFS_END_QUOTE'
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

DescribeStatement_EDIT
 : HiveDescribeStatement_EDIT
   {
     linkTablePrimaries();
   }
 | ImpalaDescribeStatement_EDIT
 ;

HiveDescribeStatement
 : '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalExtended DatabaseIdentifier
 | '<hive>DESCRIBE' '<hive>FUNCTION' OptionalExtended RegularIdentifier
 ;

HiveDescribeStatement_EDIT
 : '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier_EDIT
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain_EDIT
   {
     addTablePrimary($3);
   }
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier 'CURSOR'
   {
     addTablePrimary($3);
     suggestColumns();
   }
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted 'CURSOR'
   {
     if (!$2) {
       suggestKeywords(['DATABASE', 'EXTENDED', 'FORMATTED', 'FUNCTION', 'SCHEMA']);
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
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalExtended 'CURSOR' DatabaseIdentifier
    {
      if (!$3) {
        suggestKeywords(['EXTENDED']);
      }
    }
 | '<hive>DESCRIBE' '<hive>FUNCTION' OptionalExtended 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['EXTENDED']);
     }
   }
 | '<hive>DESCRIBE' '<hive>FUNCTION' OptionalExtended 'CURSOR' RegularIdentifier
    {
      if (!$3) {
        suggestKeywords(['EXTENDED']);
      }
    }
 ;

ImpalaDescribeStatement
 : '<impala>DESCRIBE' OptionalFormatted SchemaQualifiedTableIdentifier
 ;

ImpalaDescribeStatement_EDIT
 : '<impala>DESCRIBE' OptionalFormatted SchemaQualifiedTableIdentifier_EDIT
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
     $$ = { cursorOrPartialIdentifier: true };
   }
 ;

// ===================================== DROP Statement =====================================

DropStatement
 : DropDatabaseStatement
 | DropTableStatement
 ;

DropStatement_EDIT
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
 | DropDatabaseStatement_EDIT
 | DropTableStatement_EDIT
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

DropTableStatement
 : 'DROP' AnyTable OptionalIfExists TablePrimary
 ;

DropTableStatement_EDIT
 : 'DROP' AnyTable OptionalIfExists_EDIT
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
 ;

LoadStatement_EDIT
 : HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath_EDIT 'INTO' AnyTable RegularIdentifier
 | HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath 'INTO' 'CURSOR'
   {
     suggestKeywords([ 'TABLE' ]);
   }
 | HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath 'CURSOR'
   {
     suggestKeywords([ 'INTO' ]);
   }
 | HiveOrImpalaLoad HiveOrImpalaData HiveOrImpalaInpath HdfsPath_EDIT
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
   }
 | 'SELECT' OptionalAllOrDistinct error TableExpression
 | 'SELECT' OptionalAllOrDistinct error TableExpression_EDIT
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
 : 'FROM' TableReferenceList  -> $2
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
       $$ = { suggestKeywords: [] };
     } else if ($1 && !$2 && !$3 && !$4) {
       $$ = getValueExpressionKeywords($1, ['GROUP BY', 'LIMIT', 'ORDER BY']);
       if ($1.columnReference) {
         $$.columnReference = $1.columnReference
       }
     } else if ($2 && !$3 && !$4) {
       $$ = { suggestKeywords: ['ORDER BY', 'LIMIT'] };
     } else if ($3 && !$4) {
       if ($3.suggestKeywords) {
         $$ = { suggestKeywords: $3.suggestKeywords.concat(['LIMIT']) };
       } else {
         $$ = { suggestKeywords: ['LIMIT'] };
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
 | 'WHERE' SearchCondition  -> $2
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
 | 'ORDER' 'BY' OrderByColumnList  -> $3
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
 | OrderByColumnList ',' OrderByIdentifier  -> $3
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
 : DerivedColumnOrUnsignedInteger OptionalAscOrDesc OptionalImpalaNullsFirstOrLast  -> mergeSuggestKeywords($2, $3)
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
    $$ = { suggestKeywords: ['ASC', 'DESC'] };
  }
 | 'ASC'
 | 'DESC'
 ;

OptionalImpalaNullsFirstOrLast
 :
  {
    if (isImpala()) {
      $$ = { suggestKeywords: ['NULLS FIRST', 'NULLS LAST'] };
    } else {
      $$ = {};
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
 : NonParenthesizedValueExpressionPrimary
 | 'NOT' ValueExpression
   {
     // verifyType($2, 'BOOLEAN');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | '!' ValueExpression
   {
     // verifyType($2, 'BOOLEAN');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | '~' ValueExpression                                                              -> $2
 | '-' ValueExpression %prec NEGATION
   {
     // verifyType($2, 'NUMBER');
     $$ = $2;
     $2.types = ['NUMBER'];
   }
 | 'EXISTS' TableSubquery
   {
     $$ = { types: [ 'BOOLEAN' ] };
     // clear correlated flag after completed subquery (set by lexer)
     parser.yy.correlatedSubquery = false;
   }
 | ValueExpression 'NOT' 'LIKE' SingleQuotedValue
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'LIKE' SingleQuotedValue
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'RLIKE' SingleQuotedValue
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'REGEXP' SingleQuotedValue
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | '(' ValueExpression ')'                                -> $2
 | ValueExpression 'IS' OptionalNot 'NULL'                -> { types: [ 'BOOLEAN' ] }
 | ValueExpression '=' ValueExpression                    -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'COMPARISON_OPERATOR' ValueExpression  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression '-' ValueExpression
   {
     // verifyType($1, 'NUMBER');
     // verifyType($3, 'NUMBER');
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression '*' ValueExpression
   {
     // verifyType($1, 'NUMBER');
     // verifyType($3, 'NUMBER');
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'ARITHMETIC_OPERATOR' ValueExpression
   {
     // verifyType($1, 'NUMBER');
     // verifyType($3, 'NUMBER');
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'OR' ValueExpression
   {
     // verifyType($1, 'BOOLEAN');
     // verifyType($3, 'BOOLEAN');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'AND' ValueExpression
   {
     // verifyType($1, 'BOOLEAN');
     // verifyType($3, 'BOOLEAN');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 ;

ValueExpression
 : ValueExpression 'NOT' 'IN' '(' TableSubqueryInner ')'  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'NOT' 'IN' '(' InValueList ')'         -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'IN' '(' TableSubqueryInner ')'        -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'IN' '(' InValueList ')'               -> { types: [ 'BOOLEAN' ] }
 ;

ValueExpression
 : ValueExpression 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression        -> { types: [ 'BOOLEAN' ] }
 ;

ValueExpression
 : 'CASE' CaseRightPart                  -> $2
 | 'CASE' ValueExpression CaseRightPart  -> $3
 ;

ValueExpression_EDIT
 : 'CASE' CaseRightPart_EDIT                         -> $2
 | 'CASE' 'CURSOR' EndOrError
   {
     valueExpressionSuggest();
     suggestKeywords(['WHEN']);
     $$ = { types: [ 'T' ] };
   }
 | 'CASE' ValueExpression CaseRightPart_EDIT         -> $3
 | 'CASE' ValueExpression 'CURSOR' EndOrError
   {
     suggestValueExpressionKeywords($2, ['WHEN']);
     $$ = { types: [ 'T' ] };
   }
 | 'CASE' ValueExpression_EDIT CaseRightPart         -> $3
 | 'CASE' ValueExpression_EDIT EndOrError            -> { types: [ 'T' ] }
 | 'CASE' 'CURSOR' CaseRightPart                     -> { types: [ 'T' ] }
 ;

CaseRightPart
 : CaseWhenThenList 'END'                         -> findCaseType($1)
 | CaseWhenThenList 'ELSE' ValueExpression 'END'
   {
     $1.caseTypes.push($3);
     $$ = findCaseType($1);
   }
 ;

CaseRightPart_EDIT
 : CaseWhenThenList_EDIT EndOrError                            -> findCaseType($1)
 | CaseWhenThenList 'ELSE' ValueExpression 'CURSOR'
   {
     suggestValueExpressionKeywords($3, ['END']);
     $1.caseTypes.push($3);
     $$ = findCaseType($1);
   }
 | CaseWhenThenList_EDIT 'ELSE' ValueExpression EndOrError
   {
     $1.caseTypes.push($3);
     $$ = findCaseType($1);
   }
 | CaseWhenThenList_EDIT 'ELSE' EndOrError                      -> findCaseType($1)
 | CaseWhenThenList 'CURSOR' ValueExpression EndOrError
   {
     if ($4.toLowerCase() !== 'end') {
       suggestValueExpressionKeywords($1, ['END', 'ELSE', 'WHEN']);
     } else {
       suggestValueExpressionKeywords($1, ['ELSE', 'WHEN']);
     }
     $$ = findCaseType($1);
   }
 | CaseWhenThenList 'CURSOR' EndOrError
   {
     if ($3.toLowerCase() !== 'end') {
       suggestValueExpressionKeywords($1, ['END', 'ELSE', 'WHEN']);
     } else {
       suggestValueExpressionKeywords($1, ['ELSE', 'WHEN']);
     }
     $$ = findCaseType($1);
   }
 | CaseWhenThenList 'ELSE' ValueExpression_EDIT EndOrError
   {
     $1.caseTypes.push($3);
     $$ = findCaseType($1);
   }
 | CaseWhenThenList 'ELSE' 'CURSOR' EndOrError
   {
     valueExpressionSuggest();
     $$ = findCaseType($1);
   }
 | 'ELSE' 'CURSOR' EndOrError
   {
     valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CURSOR' 'ELSE' ValueExpression EndOrError
   {
     valueExpressionSuggest();
     suggestKeywords(['WHEN']);
     $$ = $3;
   }
 | 'CURSOR' 'ELSE' EndOrError
   {
     valueExpressionSuggest();
     suggestKeywords(['WHEN']);
     $$ = { types: [ 'T' ] };
   }
 ;

EndOrError
 : 'END'
 | error
 ;

CaseWhenThenList
 : CaseWhenThenListPartTwo                   -> { caseTypes: [ $1 ], lastType: $1 }
 | CaseWhenThenList CaseWhenThenListPartTwo
   {
     $1.caseTypes.push($2);
     $$ = { caseTypes: $1.caseTypes, lastType: $2 };
   }
 ;

CaseWhenThenList_EDIT
 : CaseWhenThenListPartTwo_EDIT
 | CaseWhenThenList CaseWhenThenListPartTwo_EDIT
 | CaseWhenThenList CaseWhenThenListPartTwo_EDIT CaseWhenThenList
 | CaseWhenThenList 'CURSOR' CaseWhenThenList
   {
     suggestValueExpressionKeywords($1, ['WHEN']);
   }
 | CaseWhenThenListPartTwo_EDIT CaseWhenThenList                   -> $2
 ;

CaseWhenThenListPartTwo
 : 'WHEN' ValueExpression 'THEN' ValueExpression  -> $4
 ;

CaseWhenThenListPartTwo_EDIT
 : 'WHEN' ValueExpression_EDIT                         -> { caseTypes: [{ types: ['T'] }] }
 | 'WHEN' ValueExpression_EDIT 'THEN'                  -> { caseTypes: [{ types: ['T'] }] }
 | 'WHEN' ValueExpression_EDIT 'THEN' ValueExpression  -> { caseTypes: [$4] }
 | 'WHEN' ValueExpression 'THEN' ValueExpression_EDIT  -> { caseTypes: [$4] }
 | 'WHEN' 'THEN' ValueExpression_EDIT                  -> { caseTypes: [$3] }
 | 'CURSOR' ValueExpression 'THEN'
   {
     suggestKeywords(['WHEN']);
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'CURSOR' ValueExpression 'THEN' ValueExpression
   {
     suggestKeywords(['WHEN']);
     $$ = { caseTypes: [$4] };
   }
 | 'CURSOR' 'THEN'
   {
     valueExpressionSuggest();
     suggestKeywords(['WHEN']);
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'CURSOR' 'THEN' ValueExpression
    {
      valueExpressionSuggest();
      suggestKeywords(['WHEN']);
      $$ = { caseTypes: [{ types: ['T'] }] };
    }
 | 'WHEN' 'CURSOR'
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' 'CURSOR' ValueExpression
   {
     valueExpressionSuggest();
     suggestKeywords(['THEN']);
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' 'CURSOR' 'THEN'
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' 'CURSOR' 'THEN' ValueExpression
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [$4] };
   }
 | 'WHEN' ValueExpression 'CURSOR'
   {
     suggestValueExpressionKeywords($2, ['THEN']);
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' ValueExpression 'CURSOR' ValueExpression
   {
     suggestValueExpressionKeywords($2, ['THEN']);
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' ValueExpression 'THEN' 'CURSOR'
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' ValueExpression 'THEN' 'CURSOR' ValueExpression
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' 'THEN' 'CURSOR' ValueExpression
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' 'THEN' 'CURSOR'
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 ;

ValueExpression_EDIT
 : NonParenthesizedValueExpressionPrimary_EDIT
 | 'NOT' ValueExpression_EDIT                           -> { types: [ 'BOOLEAN' ] }
 | 'NOT' 'CURSOR'
   {
     suggestFunctions();
     suggestColumns();
     suggestKeywords(['EXISTS']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | '!' ValueExpression_EDIT                             -> { types: [ 'BOOLEAN' ] }
 | '!' AnyCursor
   {
     suggestFunctions({ types: [ 'BOOLEAN' ] });
     suggestColumns({ types: [ 'BOOLEAN' ] });
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | '~' ValueExpression_EDIT                             -> { types: [ 'T' ] }
 | '~' 'PARTIAL_CURSOR'
   {
     suggestFunctions();
     suggestColumns();
     $$ = { types: [ 'T' ] };
   }
 | '-' ValueExpression_EDIT %prec NEGATION
   {
     applyTypeToSuggestions('NUMBER')
     $$ = { types: [ 'NUMBER' ] };
   }
 | '-' 'PARTIAL_CURSOR' %prec NEGATION
   {
     suggestFunctions({ types: [ 'NUMBER' ] });
     suggestColumns({ types: [ 'NUMBER' ] });
     $$ = { types: [ 'NUMBER' ] };
   }
 | 'EXISTS' TableSubquery_EDIT                          -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'NOT' 'LIKE' SingleQuotedValue  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'LIKE' SingleQuotedValue        -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'RLIKE' SingleQuotedValue       -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'REGEXP' SingleQuotedValue      -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'NOT' 'EXISTS' TableSubquery    -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'EXISTS' TableSubquery          -> { types: [ 'BOOLEAN' ] }
 | '(' ValueExpression_EDIT RightParenthesisOrError     -> $2
 | ValueExpression 'IS' 'NOT' 'CURSOR'
   {
     suggestKeywords(['NULL']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'IS' 'CURSOR'
   {
     suggestKeywords(['NOT NULL', 'NULL']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'IS' 'CURSOR' 'NULL'
   {
     suggestKeywords(['NOT']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'CURSOR'
   {
     suggestKeywords(['BETWEEN', 'EXISTS', 'IN', 'LIKE']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 ;

ValueExpression_EDIT
 : ValueExpression 'NOT' 'IN' ValueExpressionInSecondPart_EDIT
   {
     if ($4.inValueEdit) {
       valueExpressionSuggest($1);
       applyTypeToSuggestions($1.types);
     }
     if ($4.cursorAtStart) {
       suggestKeywords(['SELECT']);
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'IN' ValueExpressionInSecondPart_EDIT
   {
     if ($3.inValueEdit) {
       valueExpressionSuggest($1);
       applyTypeToSuggestions($1.types);
     }
     if ($3.cursorAtStart) {
       suggestKeywords(['SELECT']);
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression_EDIT 'NOT' 'IN' '(' InValueList RightParenthesisOrError         -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'NOT' 'IN' '(' TableSubqueryInner RightParenthesisOrError  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'IN' '(' InValueList RightParenthesisOrError               -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'IN' '(' TableSubqueryInner RightParenthesisOrError        -> { types: [ 'BOOLEAN' ] }
 ;

ValueExpressionInSecondPart_EDIT
 : '(' TableSubqueryInner_EDIT RightParenthesisOrError
 | '(' InValueList_EDIT RightParenthesisOrError         -> { inValueEdit: true }
 | '(' AnyCursor RightParenthesisOrError                -> { inValueEdit: true, cursorAtStart: true }
 ;

ValueExpression_EDIT
 : ValueExpression_EDIT 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression
   {
     if ($4.types[0] === $6.types[0]) {
       applyTypeToSuggestions($4.types);
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression_EDIT 'BETWEEN_AND' ValueExpression
   {
     if ($1.types[0] === $6.types[0]) {
       applyTypeToSuggestions($1.types);
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression_EDIT
   {
     if ($1.types[0] === $4.types[0]) {
       applyTypeToSuggestions($1.types);
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' 'CURSOR'
   {
     valueExpressionSuggest($1);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression 'CURSOR'
   {
     suggestValueExpressionKeywords($4, ['AND']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'BETWEEN' 'CURSOR'
   {
     valueExpressionSuggest($1);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression_EDIT 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression
   {
     if ($1.types[0] === $3.types[0]) {
       applyTypeToSuggestions($1.types)
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'BETWEEN' ValueExpression_EDIT 'BETWEEN_AND' ValueExpression
   {
     if ($1.types[0] === $3.types[0]) {
       applyTypeToSuggestions($1.types)
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression_EDIT
   {
     if ($1.types[0] === $3.types[0]) {
       applyTypeToSuggestions($1.types)
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'BETWEEN' ValueExpression 'BETWEEN_AND' 'CURSOR'
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'BETWEEN' ValueExpression 'CURSOR'
   {
     suggestValueExpressionKeywords($3, ['AND']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'BETWEEN' 'CURSOR'
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 ;

ValueExpression_EDIT
 : ValueExpression '=' ValueExpression_EDIT
   {
     applyTypeToSuggestions($1.types);
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression 'COMPARISON_OPERATOR' ValueExpression_EDIT
   {
     applyTypeToSuggestions($1.types);
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression '-' ValueExpression_EDIT
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($1);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression '*' ValueExpression_EDIT
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($1);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'ARITHMETIC_OPERATOR' ValueExpression_EDIT
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($1);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'OR' ValueExpression_EDIT
   {
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression 'AND' ValueExpression_EDIT
   {
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression '=' RightPart_EDIT
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'COMPARISON_OPERATOR' RightPart_EDIT
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression '-' RightPart_EDIT
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['NUMBER']);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression '*' RightPart_EDIT
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['NUMBER']);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'ARITHMETIC_OPERATOR' RightPart_EDIT
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['NUMBER']);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'OR' RightPart_EDIT
   {
     valueExpressionSuggest();
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'AND' RightPart_EDIT
   {
     valueExpressionSuggest();
     $$ = { types: [ 'BOOLEAN' ] };
   }
 ;

ValueExpression_EDIT
 : ValueExpression_EDIT '=' ValueExpression
   {
     applyTypeToSuggestions($3.types);
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression_EDIT 'COMPARISON_OPERATOR' ValueExpression
   {
     applyTypeToSuggestions($3.types);
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression_EDIT '-' ValueExpression
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($3);
     $$ = { types: [ 'NUMBER' ] }
   }
 | ValueExpression_EDIT '*' ValueExpression
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($3);
     $$ = { types: [ 'NUMBER' ] }
   }
 | ValueExpression_EDIT 'ARITHMETIC_OPERATOR' ValueExpression
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($3);
     $$ = { types: [ 'NUMBER' ] }
   }
 | ValueExpression_EDIT 'OR' ValueExpression
   {
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression_EDIT 'AND' ValueExpression
   {
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | 'CURSOR' '=' ValueExpression
   {
     valueExpressionSuggest($3);
     applyTypeToSuggestions($3.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' 'COMPARISON_OPERATOR' ValueExpression
   {
     valueExpressionSuggest($3);
     applyTypeToSuggestions($3.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' '*' ValueExpression
   {
     valueExpressionSuggest($3);
     applyTypeToSuggestions([ 'NUMBER' ]);
     $$ = { types: [ 'NUMBER' ] };
   }
 | 'CURSOR' 'ARITHMETIC_OPERATOR' ValueExpression
   {
     valueExpressionSuggest($3);
     applyTypeToSuggestions([ 'NUMBER' ]);
     $$ = { types: [ 'NUMBER' ] };
   }
 | 'CURSOR' 'OR' ValueExpression
   {
     valueExpressionSuggest($3);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' 'AND' ValueExpression
   {
     valueExpressionSuggest($3);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 ;

ValueExpressionList
 : ValueExpression
   {
     $1.position = 1;
   }
 | ValueExpressionList ',' ValueExpression
   {
     $3.position = $1.position + 1;
     $$ = $3;
   }
 ;

ValueExpressionList_EDIT
 : ValueExpression_EDIT
   {
     $1.position = 1;
   }
 | ValueExpressionList ',' ValueExpression_EDIT
   {
     $1.position += 1;
   }
 | ValueExpression_EDIT ',' ValueExpressionList
   {
     $1.position = 1;
   }
 | ValueExpressionList ',' ValueExpression_EDIT ',' ValueExpressionList
   {
     // $3.position = $1.position + 1;
     // $$ = $3
     $1.position += 1;
   }
 | ValueExpressionList ',' AnyCursor
   {
     valueExpressionSuggest();
     $1.position += 1;
   }
 | ValueExpressionList ',' AnyCursor ',' ValueExpressionList
   {
     valueExpressionSuggest();
     $1.position += 1;
   }
 | AnyCursor ',' ValueExpressionList
   {
     valueExpressionSuggest();
     $$ = { cursorAtStart : true, position: 1 };
   }
 | AnyCursor ','
   {
     valueExpressionSuggest();
     $$ = { cursorAtStart : true, position: 1 };
   }
 | ',' AnyCursor
   {
     valueExpressionSuggest();
     $$ = { position: 2 };
   }
 | ',' AnyCursor ',' ValueExpressionList
   {
     valueExpressionSuggest();
     $$ = { position: 2 };
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
 | ColumnReference             -> { types: ['COLREF'], columnReference: $1 }
 | UserDefinedFunction
// | GroupingOperation
 | 'NULL'                      -> { types: [ 'NULL' ] }
 ;

NonParenthesizedValueExpressionPrimary_EDIT
 : ColumnReference_EDIT
   {
     if ($1.suggestKeywords) {
       $$ = { types: ['COLREF'], columnReference: $1, suggestKeywords: $1.suggestKeywords };
     } else {
       $$ = { types: ['COLREF'], columnReference: $1 };
     }
   }
 | UserDefinedFunction_EDIT
 ;

UnsignedValueSpecification
 : UnsignedLiteral
 ;

UnsignedLiteral
 : UnsignedNumericLiteral  -> { types: [ 'NUMBER' ] }
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
 : SingleQuotedValue  -> { types: [ 'STRING' ] }
 | DoubleQuotedValue  -> { types: [ 'STRING' ] }
 | TruthValue         -> { types: [ 'BOOLEAN' ] }
 ;

TruthValue
 : 'TRUE'
 | 'FALSE'
 ;

OptionalNot
 :
 | 'NOT'
 ;

SelectSubList
 : ValueExpression OptionalCorrelationName
   {
     if ($2 && $2.suggestKeywords) {
       var result = getValueExpressionKeywords($1, $2.suggestKeywords || [])
       if ($1.columnReference) {
         result.columnReference = $1.columnReference;
       }
       $$ = result;
     } else {
       $$ = $2;
     }
   }
 | '*'
 ;

SelectSubList_EDIT
 : ValueExpression_EDIT OptionalCorrelationName
 | ValueExpression OptionalCorrelationName_EDIT  -> $2
 ;

SelectList
 : SelectSubList
 | SelectList ',' SelectSubList  -> $3
 ;

SelectList_EDIT
 : SelectSubList_EDIT
 | 'CURSOR' SelectList
   {
     suggestFunctions();
     suggestColumns();
     suggestFunctions();
     $$ = { cursorAtStart : true, suggestAggregateFunctions: true };
   }
 | SelectList 'CURSOR' SelectList
 | SelectList ',' AnyCursor SelectList
   {
     suggestFunctions();
     suggestColumns();
     suggestFunctions();
     $$ = { suggestAggregateFunctions: true, suggestKeywords: ['*'] };
   }
 | SelectList ',' SelectListPartTwo_EDIT                 -> $3
 | SelectList ',' SelectListPartTwo_EDIT ','             -> $3
 | SelectList ',' SelectListPartTwo_EDIT ',' SelectList  -> $3
 ;

SelectListPartTwo_EDIT
 : SelectSubList_EDIT
 | AnyCursor
   {
     suggestFunctions();
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
     $$ = { suggestKeywords: ['*'], suggestAggregateFunctions: true };
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
 | TableReferenceList ',' TableReference  -> $3
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
 : TablePrimary Joins  -> $2
 ;

JoinedTable_EDIT
 : TablePrimary Joins_EDIT
 | TablePrimary_EDIT Joins
 ;

// TODO: Joins 'JOIN' Joins
Joins
 : JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary                      -> { hasJoinCondition: false }
 | JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition        -> { hasJoinCondition: true }
 | Joins JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary                -> { hasJoinCondition: false }
 | Joins JoinTypes 'JOIN' OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition  -> { hasJoinCondition: true }
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
   {
     linkTablePrimaries();
   }
 ;

OptionalCorrelationName
 :
   {
     $$ = { suggestKeywords: ['AS'] };
   }
 | RegularOrBacktickedIdentifier
 | AnyAs RegularOrBacktickedIdentifier  -> $2
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
 : '<hive>EXPLODE(' DerivedColumnChain ')'     -> { function: $1.substring(0, $1.length - 1), expression: $2 }
 | '<hive>POSEXPLODE(' DerivedColumnChain ')'  -> { function: $1.substring(0, $1.length - 1), expression: $2 }
 ;

UserDefinedTableGeneratingFunction_EDIT
 : '<hive>EXPLODE(' DerivedColumnChain_EDIT error
   {
     suggestColumns($2);
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
 : ArbitraryFunction
 | AggregateFunction
 | CastFunction
 | ExtractFunction
 ;

UserDefinedFunction_EDIT
 : ArbitraryFunction_EDIT
 | AggregateFunction_EDIT
 | CastFunction_EDIT
 | ExtractFunction_EDIT
 ;

ArbitraryFunction
 : 'UDF(' ')'                      -> { types: findReturnTypes($1) }
 | 'UDF(' ValueExpressionList ')'  -> { function: $1.substring(0, $1.length - 1), expression: $2, types: findReturnTypes($1) }
 ;

ArbitraryFunction_EDIT
 : 'UDF(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyArgumentTypesToSuggestions($1, 1);
     $$ = { types: findReturnTypes($1) };
   }
 | 'UDF(' ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($2);
     $$ = { types: findReturnTypes($1) };
   }
 | 'UDF(' ValueExpressionList 'CURSOR' ',' ValueExpressionList RightParenthesisOrError
   {
     suggestValueExpressionKeywords($2);
     $$ = { types: findReturnTypes($1) };
   }
 | 'UDF(' ValueExpressionList_EDIT RightParenthesisOrError
   {
     applyArgumentTypesToSuggestions($1, $2.position);
     $$ = { types: findReturnTypes($1) };
   }
 ;

AggregateFunction
 : CountFunction
 | SumFunction
 | OtherAggregateFunction
 ;

AggregateFunction_EDIT
 : CountFunction_EDIT
 | SumFunction_EDIT
 | OtherAggregateFunction_EDIT
 ;

CastFunction
 : 'CAST(' ValueExpression AnyAs PrimitiveType ')'  -> { types: [ $4.toUpperCase() ] }
 | 'CAST(' ')'                                      -> { types: [ 'T' ] }
 ;

CastFunction_EDIT
 : 'CAST(' AnyCursor AnyAs PrimitiveType RightParenthesisOrError
   {
     valueExpressionSuggest();
     $$ = { types: [ $4.toUpperCase() ] };
   }
 | 'CAST(' AnyCursor AnyAs RightParenthesisOrError
   {
     valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST(' ValueExpression_EDIT AnyAs PrimitiveType RightParenthesisOrError  -> { types: [ $4.toUpperCase() ] }
 | 'CAST(' ValueExpression_EDIT AnyAs RightParenthesisOrError                -> { types: [ 'T' ] }
 | 'CAST(' ValueExpression_EDIT RightParenthesisOrError                      -> { types: [ 'T' ] }
 | 'CAST(' ValueExpression 'CURSOR' PrimitiveType RightParenthesisOrError
   {
     suggestValueExpressionKeywords($2, ['AS']);
     $$ =  { types: [ $4.toUpperCase() ] };
   }
 | 'CAST(' ValueExpression 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($2, ['AS']);
     $$ = { types: [ 'T' ] };
   }
 | 'CAST(' ValueExpression AnyAs 'CURSOR' RightParenthesisOrError
   {
     suggestTypeKeywords();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST(' AnyAs 'CURSOR' RightParenthesisOrError
   {
     suggestTypeKeywords();
     $$ = { types: [ 'T' ] };
   }
 ;

CountFunction
 : 'COUNT(' '*' ')'                                        -> { types: findReturnTypes($1) }
 | 'COUNT(' ')'                                            -> { types: findReturnTypes($1) }
 | 'COUNT(' OptionalAllOrDistinct ValueExpressionList ')'  -> { types: findReturnTypes($1) }
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
     $$ = { types: findReturnTypes($1) };
   }
 | 'COUNT(' OptionalAllOrDistinct ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($3);
     $$ = { types: findReturnTypes($1) };
   }
 | 'COUNT(' OptionalAllOrDistinct ValueExpressionList_EDIT RightParenthesisOrError
   {
     if ($3.cursorAtStart && !$2) {
       if (isImpala()) {
         suggestKeywords(['ALL', 'DISTINCT']);
       } else {
         suggestKeywords(['DISTINCT']);
       }
     }
     $$ = { types: findReturnTypes($1) };
   }
 ;

OtherAggregateFunction
 : OtherAggregateFunction_Type OptionalAllOrDistinct ')'                      -> { types: findReturnTypes($1) }
 | OtherAggregateFunction_Type OptionalAllOrDistinct ValueExpressionList ')'  -> { types: findReturnTypes($1) }
 ;

OtherAggregateFunction_EDIT
 : OtherAggregateFunction_Type OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     suggestFunctions();
     suggestColumns();
     if (!$2) {
       if ($1.toLowerCase() === 'group_concat(') {
         suggestKeywords(['ALL' ]);
       } else if (isImpala()) {
         suggestKeywords(['ALL', 'DISTINCT']);
       } else {
         suggestKeywords(['DISTINCT']);
       }
     }
     applyArgumentTypesToSuggestions($1, 1);
     $$ = { types: findReturnTypes($1) };
   }
 | OtherAggregateFunction_Type OptionalAllOrDistinct ValueExpressionList 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($3);
     $$ = { types: findReturnTypes($1) };
   }
 | OtherAggregateFunction_Type OptionalAllOrDistinct ValueExpressionList_EDIT RightParenthesisOrError
   {
     if ($3.cursorAtStart && !$2) {
       if ($1.toLowerCase() === 'group_concat(') {
         suggestKeywords(['ALL' ]);
       } else if (isImpala()) {
         suggestKeywords(['ALL', 'DISTINCT']);
       } else {
         suggestKeywords(['DISTINCT']);
       }
     }
     if (parser.yy.result.suggestFunctions && !parser.yy.result.suggestFunctions.types) {
       applyArgumentTypesToSuggestions($1, $3.position);
     }
     $$ = { types: findReturnTypes($1) };
   }
 ;

OtherAggregateFunction_Type
 : '<impala>APPX_MEDIAN('
 | 'AVG('
 | '<hive>COLLECT_SET('
 | '<hive>COLLECT_LIST('
 | '<hive>CORR('
 | '<hive>COVAR_POP('
 | '<hive>COVAR_SAMP('
 | '<impala>GROUP_CONCAT('
 | '<hive>HISTOGRAM_NUMERIC'
 | '<impala>STDDEV('
 | 'STDDEV_POP('
 | 'STDDEV_SAMP('
 | 'MAX('
 | 'MIN('
 | '<hive>NTILE('
 | '<hive>PERCENTILE('
 | '<hive>PERCENTILE_APPROX('
 | 'VARIANCE('
 | '<impala>VARIANCE_POP('
 | '<impala>VARIANCE_SAMP('
 | 'VAR_POP('
 | 'VAR_SAMP('
 ;

ExtractFunction
 : '<impala>EXTRACT(' ValueExpression FromOrComma ValueExpression ')'
 | '<impala>EXTRACT(' ')'
 ;

ExtractFunction_EDIT
 : '<impala>EXTRACT(' AnyCursor FromOrComma ValueExpression RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyTypeToSuggestions($3.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' AnyCursor FromOrComma RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyTypeToSuggestions($3.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['STRING', 'TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' ValueExpression_EDIT FromOrComma ValueExpression RightParenthesisOrError
   {
     applyTypeToSuggestions($3.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' ValueExpression_EDIT FromOrComma RightParenthesisOrError
   {
     applyTypeToSuggestions($3.toLowerCase() === 'from' ? ['STRING'] : ['TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' ValueExpression_EDIT RightParenthesisOrError
   {
     applyTypeToSuggestions(['STRING', 'TIMESTAMP']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' ValueExpression FromOrComma AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyTypeToSuggestions($3.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' FromOrComma AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyTypeToSuggestions($3.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' ValueExpression FromOrComma ValueExpression_EDIT RightParenthesisOrError
   {
     applyTypeToSuggestions($3.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' FromOrComma ValueExpression_EDIT RightParenthesisOrError
   {
    applyTypeToSuggestions($3.toLowerCase() === 'from' ? ['TIMESTAMP'] : ['STRING']);
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' ValueExpression 'CURSOR' ValueExpression RightParenthesisOrError
   {
     if ($1.types[0] === 'STRING') {
       suggestValueExpressionKeywords($2, ['FROM']);
     } else {
       suggestValueExpressionKeywords($2);
     }
     $$ = { types: findReturnTypes($1) };
   }
 | '<impala>EXTRACT(' ValueExpression 'CURSOR' RightParenthesisOrError
   {
     if ($1.types[0] === 'STRING') {
       suggestValueExpressionKeywords($2, ['FROM']);
     } else {
       suggestValueExpressionKeywords($2);
     }
     $$ = { types: findReturnTypes($1) };
   }
 ;

FromOrComma
 : 'FROM'
 | ','
 ;

SumFunction
 : 'SUM(' OptionalAllOrDistinct ValueExpression ')'  -> { types: findReturnTypes($1) }
 | 'SUM(' ')'                                        -> { types: findReturnTypes($1) }
 ;

SumFunction_EDIT
 : 'SUM(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     applyArgumentTypesToSuggestions($1, 1);
     if (!$2) {
       if (isImpala()) {
         suggestKeywords(['ALL', 'DISTINCT']);
       } else {
         suggestKeywords(['DISTINCT']);
       }
     }
     $$ = { types: findReturnTypes($1) };
   }
 | 'SUM(' OptionalAllOrDistinct ValueExpression 'CURSOR' RightParenthesisOrError
   {
     suggestValueExpressionKeywords($3);
     $$ = { types: findReturnTypes($1) };
   }
 | 'SUM(' OptionalAllOrDistinct ValueExpression_EDIT RightParenthesisOrError
   {
     if (parser.yy.result.suggestFunctions && ! parser.yy.result.suggestFunctions.types) {
       applyArgumentTypesToSuggestions($1, 1);
     }
     $$ = { types: findReturnTypes($1) };
   }
 ;

// TODO: WITHIN
//WithinGroupSpecification
// : 'WITHIN' 'GROUP' '(' 'ORDER' 'BY' SortSpecificationList ')'
// ;

LateralView
 : '<hive>LATERAL' 'VIEW' UserDefinedFunction RegularIdentifier LateralViewColumnAliases  -> [{ udtf: $3, tableAlias: $4, columnAliases: $5 }]
 | '<hive>LATERAL' 'VIEW' UserDefinedFunction LateralViewColumnAliases                    -> [{ udtf: $3, columnAliases: $4 }]
 | LateralView_ERROR
 ;

LateralView_ERROR
 : '<hive>LATERAL' 'VIEW' UserDefinedFunction RegularIdentifier error                     -> []
 | '<hive>LATERAL' 'VIEW' UserDefinedFunction error                                       -> []
 | '<hive>LATERAL' 'VIEW' error                                                           -> []
 | '<hive>LATERAL' error                                                                  -> []
 ;

LateralView_EDIT
 : '<hive>LATERAL' 'VIEW' UserDefinedFunction_EDIT
 | '<hive>LATERAL' 'VIEW' UserDefinedFunction_EDIT LateralViewColumnAliases
 | '<hive>LATERAL' 'VIEW' UserDefinedFunction RegularIdentifier 'CURSOR'
   {
     suggestKeywords(['AS']);
     $$ = [];
   }
 | '<hive>LATERAL' 'VIEW' UserDefinedFunction 'CURSOR'
   {
     suggestKeywords(['AS']);
     $$ = [];
   }
 | '<hive>LATERAL' 'VIEW' 'CURSOR'
   {
     suggestKeywords(['explode', 'posexplode']);
     $$ = [];
   }
 | '<hive>LATERAL' 'CURSOR'
   {
     suggestKeywords(['VIEW']);
     $$ = [];
   }
 ;

LateralViewColumnAliases
 : '<hive>AS' RegularIdentifier                                -> [ $2 ]
 | '<hive>AS' '(' RegularIdentifier ',' RegularIdentifier ')'  -> [ $3, $5 ]
 ;

// ===================================== SHOW Statement =====================================

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

ShowStatement_EDIT
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
 | 'SHOW' 'CURSOR' RegularOrBackTickedSchemaQualifiedName
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
 : 'SHOW' '<impala>COLUMN' '<impala>STATS' RegularOrBackTickedSchemaQualifiedName
 ;

ShowColumnStatsStatement_EDIT
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
 | 'SHOW' '<impala>COLUMN' '<impala>STATS' RegularOrBackTickedSchemaQualifiedName_EDIT
 ;

ShowColumnsStatement
 : 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier
 | 'SHOW' '<hive>COLUMNS' AnyFromOrIn RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 ;

ShowColumnsStatement_EDIT
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
 ;

ShowCompactionsStatement
 : 'SHOW' '<hive>COMPACTIONS'
 ;

ShowConfStatement
 : 'SHOW' '<hive>CONF' ConfigurationName
 ;

ShowCreateTableStatement
 : 'SHOW' HiveOrImpalaCreate AnyTable RegularOrBackTickedSchemaQualifiedName
 ;

ShowCreateTableStatement_EDIT
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
 | 'SHOW' HiveOrImpalaCreate AnyTable RegularOrBackTickedSchemaQualifiedName_EDIT
 | 'SHOW' HiveOrImpalaCreate 'CURSOR' RegularOrBackTickedSchemaQualifiedName
   {
     suggestKeywords(['TABLE']);
   }
 ;

ShowCurrentRolesStatement
 : 'SHOW' HiveOrImpalaCurrent HiveOrImpalaRoles
 ;

ShowCurrentRolesStatement_EDIT
 : 'SHOW' HiveOrImpalaCurrent 'CURSOR'
   {
     suggestKeywords([ 'ROLES' ]);
   }
 | 'SHOW' 'CURSOR' HiveOrImpalaRoles
   {
     suggestKeywords([ 'CURRENT' ]);
   }
 ;

ShowDatabasesStatement
 : 'SHOW' HiveOrImpalaDatabasesOrSchemas 'LIKE' SingleQuotedValue
 | 'SHOW' '<impala>DATABASES' SingleQuotedValue
 ;

ShowDatabasesStatement_EDIT
 : 'SHOW' HiveOrImpalaDatabasesOrSchemas 'CURSOR'
   {
     suggestKeywords(['LIKE']);
   }
 ;

ShowFunctionsStatement
 : 'SHOW' '<hive>FUNCTIONS'
 | 'SHOW' '<hive>FUNCTIONS' DoubleQuotedValue
 | 'SHOW' OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase
 | 'SHOW' OptionalAggregateOrAnalytic '<impala>FUNCTIONS' OptionalInDatabase 'LIKE' SingleQuoteValue
 ;

ShowFunctionsStatement_EDIT
 : 'SHOW' AggregateOrAnalytic 'CURSOR'
   {
     suggestKeywords(['FUNCTIONS']);
   }
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
 : 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier
 | 'SHOW' OptionallyFormattedIndex 'ON' RegularOrBacktickedIdentifier AnyFromOrIn RegularOrBacktickedIdentifier
 ;

ShowIndexStatement_EDIT
 : 'SHOW' OptionallyFormattedIndex
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

ShowLocksStatement
 : 'SHOW' '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName
 | 'SHOW' '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName '<hive>EXTENDED'
 | 'SHOW' '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' '(' PartitionSpecList ')'
 | 'SHOW' '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' '(' PartitionSpecList ')' '<hive>EXTENDED'
 | 'SHOW' '<hive>LOCKS' DatabaseOrSchema RegularOrBacktickedIdentifier
 ;

ShowLocksStatement_EDIT
 : 'SHOW' '<hive>LOCKS' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
     suggestKeywords(['DATABASE', 'SCHEMA']);
   }
 | 'SHOW' '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT
 | 'SHOW' '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName 'CURSOR'
    {
      suggestKeywords(['EXTENDED', 'PARTITION']);
    }
 | 'SHOW' '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT '<hive>EXTENDED'
 | 'SHOW' '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT '<hive>PARTITION' '(' PartitionSpecList ')'
 | 'SHOW' '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' '(' PartitionSpecList ')' 'CURSOR'
   {
     suggestKeywords(['EXTENDED']);
   }
 | 'SHOW' '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT '<hive>PARTITION' '(' PartitionSpecList ')' '<hive>EXTENDED'
 | 'SHOW' '<hive>LOCKS' DatabaseOrSchema 'CURSOR'
   {
     suggestDatabases();
   }
 ;

ShowPartitionsStatement
 : 'SHOW' '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName
 | 'SHOW' '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' PartitionSpecList
 | 'SHOW' '<impala>PARTITIONS' RegularOrBackTickedSchemaQualifiedName
 ;

ShowPartitionsStatement_EDIT
 : 'SHOW' '<hive>PARTITIONS' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName_EDIT
 | 'SHOW' '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName 'CURSOR'
   {
     suggestKeywords(['PARTITION']);
   }
 | 'SHOW' '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName_EDIT '<hive>PARTITION' PartitionSpecList
 | 'SHOW' '<impala>PARTITIONS' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 | 'SHOW' '<impala>PARTITIONS' RegularOrBackTickedSchemaQualifiedName_EDIT
 ;

ShowRoleStatement
 : 'SHOW' HiveOrImpalaRole '<hive>GRANT' HiveRoleOrUser RegularIdentifier
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' '<impala>GROUP' RegularIdentifier
 ;

ShowRoleStatement_EDIT
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
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' 'CURSOR'
   {
     suggestKeywords(['GROUP']);
   }
 | 'SHOW' HiveOrImpalaRole '<impala>GRANT' 'CURSOR' RegularIdentifier
   {
     suggestKeywords(['GROUP']);
   }
 ;

ShowRolesStatement
 : 'SHOW' '<impala>ROLES'
 ;

ShowTableStatement
 : 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
 ;

ShowTableStatement_EDIT
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
 | 'SHOW' '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_EDIT 'LIKE' SingleQuotedValue
 | 'SHOW' '<hive>TABLE' 'CURSOR' OptionalFromDatabase 'LIKE' SingleQuotedValue
    {
      if (isHive()) {
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
 | 'SHOW' '<impala>TABLE' '<impala>STATS' RegularOrBackTickedSchemaQualifiedName
 | 'SHOW' '<impala>TABLE' '<impala>STATS' RegularOrBackTickedSchemaQualifiedName_EDIT
 ;

ShowTablesStatement
 : 'SHOW' HiveOrImpalaTables OptionalInDatabase
 | 'SHOW' HiveOrImpalaTables OptionalInDatabase SingleQuotedValue
 | 'SHOW' HiveOrImpalaTables OptionalInDatabase 'LIKE' SingleQuotedValue
 ;

ShowTablesStatement_EDIT
 : 'SHOW' HiveOrImpalaTables OptionalInDatabase 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IN', 'LIKE']);
     } else {
       suggestKeywords(['LIKE']);
     }
   }
 ;

ShowTblPropertiesStatement
 : 'SHOW' '<hive>TBLPROPERTIES' RegularOrBackTickedSchemaQualifiedName
 ;

ShowTblPropertiesStatement_EDIT
 : 'SHOW' '<hive>TBLPROPERTIES' RegularOrBackTickedSchemaQualifiedName_EDIT
 | 'SHOW' '<hive>TBLPROPERTIES' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({ prependDot: true });
   }
 ;

ShowTransactionsStatement
 : 'SHOW' '<hive>TRANSACTIONS'
 ;



// ===================================== UPDATE statement =====================================

UpdateStatement
 : 'UPDATE' TargetTable 'SET' SetClauseList OptionalWhereClause
 ;

UpdateStatement_EDIT
 : 'UPDATE' TargetTable_EDIT 'SET' SetClauseList OptionalWhereClause
   }
 | 'UPDATE' TargetTable 'SET' SetClauseList_EDIT OptionalWhereClause
 | 'UPDATE' TargetTable 'SET' SetClauseList OptionalWhereClause_EDIT
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
 | 'UPDATE' TargetTable_EDIT
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

TargetTable_EDIT
 : TableName_EDIT
 ;

TableName
 : LocalOrSchemaQualifiedName
   {
     addTablePrimary($1);
   }
 ;

TableName_EDIT
 : LocalOrSchemaQualifiedName_EDIT
 ;

SetClauseList
 : SetClause
 | SetClauseList ',' SetClause
 ;

SetClauseList_EDIT
 : SetClause_EDIT
 | SetClauseList ',' SetClause_EDIT
 | SetClause_EDIT ',' SetClauseList
 | SetClauseList ',' SetClause_EDIT ',' SetClauseList
 ;

SetClause
 : SetTarget '=' UpdateSource
 ;

SetClause_EDIT
 : SetTarget '=' UpdateSource_EDIT
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

UpdateSource_EDIT
 : ValueExpression_EDIT
 ;


// ===================================== USE Statement =====================================

UseStatement
 : 'USE' RegularIdentifier
   {
     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $2;
     }
   }
 ;

UseStatement_EDIT
 : 'USE' 'CURSOR'
   {
     suggestDatabases();
   }
 ;


// ===================================== Fin =====================================
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
    return { suggestKeywords: result };
  }
  return {};
}

var suggestValueExpressionKeywords = function (valueExpression, extras) {
  var expressionKeywords = getValueExpressionKeywords(valueExpression, extras)
  suggestKeywords(expressionKeywords.suggestKeywords);
  if (expressionKeywords.suggestColRefKeywords) {
    suggestColRefKeywords(expressionKeywords.suggestColRefKeywords);
  }
  if (valueExpression.lastType) {
    addColRefIfExists(valueExpression.lastType);
  } else {
    addColRefIfExists(valueExpression);
  }
}

var getValueExpressionKeywords = function (valueExpression, extras) {
  var types = valueExpression.lastType ? valueExpression.lastType.types : valueExpression.types;
  // We could have valueExpression.columnReference to suggest based on column type
  var keywords = ['<', '<=', '<>', '=', '>', '>=', 'BETWEEN', 'IN', 'IS NOT NULL', 'IS NULL', 'NOT BETWEEN', 'NOT IN'];
  if (isHive()) {
    keywords.push('<=>');
  }
  if (extras) {
    keywords = keywords.concat(extras);
  }
  if (valueExpression.suggestKeywords) {
    keywords = keywords.concat(valueExpression.suggestKeywords);
  }
  if (types.length === 1 &&  types[0] === 'COLREF') {
    return {
      suggestKeywords: keywords,
      suggestColRefKeywords: {
        BOOLEAN: ['AND', 'OR'],
        NUMBER: ['+', '-', '*', '/', '%'],
        STRING: ['LIKE', 'NOT LIKE', 'REGEX', 'RLIKE']
      }
    }
  }
  if (parser.yy.sqlFunctions.matchesType(parser.yy.activeDialect, ['BOOLEAN'], types)) {
    keywords = keywords.concat(['AND', 'OR']);
  }
  if (parser.yy.sqlFunctions.matchesType(parser.yy.activeDialect, ['NUMBER'], types)) {
    keywords = keywords.concat(['+', '-', '*', '/', '%']);
  }
  if (parser.yy.sqlFunctions.matchesType(parser.yy.activeDialect, ['STRING'], types)) {
    keywords = keywords.concat(['LIKE', 'NOT LIKE', 'REGEX', 'RLIKE']);
  }
  return { suggestKeywords: keywords };
}

var suggestTypeKeywords = function () {
  if (isHive()) {
    suggestKeywords(['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
  } else if (isImpala()) {
    suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'REAL', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
  } else {
    suggestKeywords(['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR']);
  }
}

var addColRefIfExists = function (valueExpression) {
  if (valueExpression.columnReference) {
    parser.yy.result.colRef = { identifierChain: valueExpression.columnReference };
  }
}

var valueExpressionSuggest = function (oppositeValueExpression) {
  if (oppositeValueExpression && oppositeValueExpression.columnReference) {
    suggestValues();
    parser.yy.result.colRef = { identifierChain: oppositeValueExpression.columnReference };
  }
  suggestColumns();
  suggestFunctions();
  if (oppositeValueExpression && oppositeValueExpression.types[0] === 'NUMBER') {
    applyTypeToSuggestions(['NUMBER']);
  }
}

var applyTypeToSuggestions = function (types) {
  if (types[0] === 'BOOLEAN') {
    return;
  }
  if (parser.yy.result.suggestFunctions) {
    parser.yy.result.suggestFunctions.types = types;
  }
  if (parser.yy.result.suggestColumns) {
    parser.yy.result.suggestColumns.types = types;
  }
}

var findCaseType = function (whenThenList) {
  var types = {};
  whenThenList.caseTypes.forEach(function (valueExpression) {
    valueExpression.types.forEach(function (type) {
      types[type] = true;
    });
  });
  if (Object.keys(types).length === 1) {
    return { types: [Object.keys(types)[0]] };
  }
  return { types: [ 'T' ] };
}

findReturnTypes = function (funcToken) {
  var funcName = funcToken.substring(0, funcToken.length - 1).toLowerCase();
  return parser.yy.sqlFunctions.getReturnTypes(parser.yy.activeDialect, funcName);
}

var applyArgumentTypesToSuggestions = function (funcToken, position) {
  var funcName = funcToken.substring(0, funcToken.length - 1).toLowerCase();
  var foundArguments = parser.yy.sqlFunctions.getArgumentTypes(parser.yy.activeDialect, funcName, position);
  if (foundArguments.length == 0 && parser.yy.result.suggestColumns) {
    delete parser.yy.result.suggestColumns;
    delete parser.yy.result.suggestKeyValues;
    delete parser.yy.result.suggestValues;
    delete parser.yy.result.suggestFunctions;
    delete parser.yy.result.suggestIdentifiers;
  } else {
    applyTypeToSuggestions(foundArguments);
  }
}

var prioritizeSuggestions = function () {
  parser.yy.result.lowerCase = parser.yy.lowerCase || false;
  if (typeof parser.yy.result.colRef !== 'undefined') {
    if (typeof parser.yy.result.colRef.table === 'undefined') {
      delete parser.yy.result.colRef;
      if (typeof parser.yy.result.suggestColRefKeywords !== 'undefined') {
        Object.keys(parser.yy.result.suggestColRefKeywords).forEach(function (type) {
          parser.yy.result.suggestKeywords = parser.yy.result.suggestKeywords.concat(parser.yy.result.suggestColRefKeywords[type]);
        });
        delete parser.yy.result.suggestColRefKeywords;
      }
      if (parser.yy.result.suggestColumns && parser.yy.result.suggestColumns.types.length === 1 && parser.yy.result.suggestColumns.types[0] === 'COLREF') {
        parser.yy.result.suggestColumns.types = ['T'];
      }
      delete parser.yy.result.suggestValues;
    }
  }

  if (typeof parser.yy.result.colRef !== 'undefined') {
    if (!parser.yy.result.suggestValues &&
        !parser.yy.result.suggestColRefKeywords &&
        (!parser.yy.result.suggestColumns ||
          parser.yy.result.suggestColumns.types[0] !== 'COLREF')) {
      delete parser.yy.result.colRef;
    }
  }
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
 * [ { name: 'm', keySet: true }, { name: 'bar' } ]
 *
 * Calling this would return an expanded identifierChain, given the above it would be:
 *
 * [ { name: 't' }, { name: 'someMap', keySet: true }, { name: 'bar' } ]
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
    if (typeof identifierChain[0].keySet !== 'undefined') {
      var lastFromFirst = firstPart.pop();
      firstPart.push({
        name: lastFromFirst.name,
        keySet: identifierChain[0].keySet
      });
    }
    return firstPart.concat(secondPart);
  }

  return identifierChain;
};

parser.identifyPartials = function (beforeCursor, afterCursor) {
  var beforeMatch = beforeCursor.match(/[0-9a-zA-Z_]*$/);
  var afterMatch = afterCursor.match(/^[0-9a-zA-Z_]*/);
  return { left: beforeMatch ? beforeMatch[0].length : 0, right: afterMatch ? afterMatch[0].length : 0};
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
      });
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
   if (typeof parser.yy.result.colRef !== 'undefined') {
     linkSuggestion(parser.yy.result.colRef, false);
   }
   if (typeof parser.yy.result.suggestKeyValues !== 'undefined') {
     linkSuggestion(parser.yy.result.suggestKeyValues, true);
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

var checkForKeywords = function (expression) {
  if (expression) {
    if (expression.suggestKeywords && expression.suggestKeywords.length > 0) {
      suggestKeywords(expression.suggestKeywords);
    }
    if (expression.suggestColRefKeywords) {
      suggestColRefKeywords(expression.suggestColRefKeywords)
      addColRefIfExists(expression);
    }
  }
}

var suggestKeywords = function (keywords) {
  parser.yy.result.suggestKeywords = keywords.sort();
}

var suggestColRefKeywords = function (colRefKeywords) {
  parser.yy.result.suggestColRefKeywords = colRefKeywords;
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

var suggestFunctions = function (details) {
  parser.yy.result.suggestFunctions = details || {};
}

var suggestAggregateFunctions = function () {
  parser.yy.result.suggestAggregateFunctions = true;
}

var suggestColumns = function (details) {
  if (typeof details === 'undefined') {
    details = { identifierChain: [] };
  } else if (typeof details.identifierChain === 'undefined') {
    details.identifierChain = [];
  }
  parser.yy.result.suggestColumns = details;
}

var suggestKeyValues = function (details) {
  parser.yy.result.suggestKeyValues = details || {};
}

var suggestTables = function (details) {
  parser.yy.result.suggestTables = details || {};
}

var suggestDatabases = function (details) {
  parser.yy.result.suggestDatabases = details || {};
}

var suggestHdfs = function (details) {
  parser.yy.result.suggestHdfs = details || {};
}

var suggestValues = function (details) {
  parser.yy.result.suggestValues = true;
}

var determineCase = function (text) {
  parser.yy.lowerCase = text.toLowerCase() === text;
};

var lexerModified = false;

/**
 * Main parser function
 */
parser.parseSql = function(beforeCursor, afterCursor, dialect, sqlFunctions, debug) {
  if (dialect === 'generic') {
    dialect = undefined;
  }
  parser.yy.sqlFunctions = sqlFunctions;
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
        lexer.begin(parser.yy.activeDialect);
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
    if (debug) {
      console.log(err);
      console.error(err.stack);
    }
    if (parser.yy.result.error && !parser.yy.result.error.recoverable) {
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