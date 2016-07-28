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
%x hdfs doubleQuotedValue singleQuotedValue backtickedValue
%%

[ \t\n]                                    { /* skip whitespace */ }
'--'.*                                     { /* skip comments */ }
[/][*][^*]*[*]+([^/*][^*]*[*]+)*[/]        { /* skip comments */ }

'\u2020'                                   { parser.yy.partialCursor = false; parser.yy.cursorFound = yylloc; return 'CURSOR'; }
'\u2021'                                   { parser.yy.partialCursor = true; parser.yy.cursorFound = yylloc; return 'PARTIAL_CURSOR'; }

// Reserved Keywords
<hive>'ALL'                                { return '<hive>ALL'; }
<hive>'ARRAY'                              { return '<hive>ARRAY'; }
<hive>'AS'                                 { return '<hive>AS'; }
<hive>'BINARY'                             { return '<hive>BINARY'; }
<hive>'CONF'                               { return '<hive>CONF'; }
<hive>'CREATE'                             { determineCase(yytext); return '<hive>CREATE'; }
<hive>'CROSS'                              { return '<hive>CROSS'; }
<hive>'CURRENT'                            { return '<hive>CURRENT'; }
<hive>'DATE'                               { return '<hive>DATE'; }
<hive>'DESCRIBE'                           { determineCase(yytext); return '<hive>DESCRIBE'; }
<hive>'EXTENDED'                           { return '<hive>EXTENDED'; }
<hive>'EXTERNAL'                           { return '<hive>EXTERNAL'; }
<hive>'FUNCTION'                           { return '<hive>FUNCTION'; }
<hive>'GRANT'                              { return '<hive>GRANT'; }
<hive>'LATERAL'                            { return '<hive>LATERAL'; }
<hive>'MACRO'                              { return '<hive>MACRO'; }
<hive>'MAP'                                { return '<hive>MAP'; }
<hive>'PARTITION'                          { return '<hive>PARTITION'; }
<hive>'TABLE'                              { return '<hive>TABLE'; }
<hive>'USER'                               { return '<hive>USER'; }

// Non-reserved Keywords
<hive>'ASC'                                { return '<hive>ASC'; }
<hive>'AVRO'                               { return '<hive>AVRO'; }
<hive>'BUCKETS'                            { return '<hive>BUCKETS'; }
<hive>'CLUSTERED'                          { return '<hive>CLUSTERED'; }
<hive>'COLLECTION'                         { return '<hive>COLLECTION'; }
<hive>'COLUMNS'                            { return '<hive>COLUMNS'; }
<hive>'COMMENT'                            { return '<hive>COMMENT'; }
<hive>'COMPACTIONS'                        { return '<hive>COMPACTIONS'; }
<hive>'DATA'                               { return '<hive>DATA'; }
<hive>'DATABASES'                          { return '<hive>DATABASES'; }
<hive>'DEFINED'                            { return '<hive>DEFINED'; }
<hive>'DELIMITED'                          { return '<hive>DELIMITED'; }
<hive>'DESC'                               { return '<hive>DESC'; }
<hive>STORED[ \t\n]+AS[ \t\n]+DIRECTORIES  { return '<hive>STORED_AS_DIRECTORIES'; }
<hive>'ESCAPED'                            { return '<hive>ESCAPED'; }
<hive>'FIELDS'                             { return '<hive>FIELDS'; }
<hive>'FORMAT'                             { return '<hive>FORMAT'; }
<hive>'FORMATTED'                          { return '<hive>FORMATTED'; }
<hive>'FUNCTIONS'                          { return '<hive>FUNCTIONS'; }
<hive>'INDEX'                              { return '<hive>INDEX'; }
<hive>'INDEXES'                            { return '<hive>INDEXES'; }
<hive>'INPATH'                             { this.begin('hdfs'); return '<hive>INPATH'; }
<hive>'INPUTFORMAT'                        { return '<hive>INPUTFORMAT'; }
<hive>'ITEMS'                              { return '<hive>ITEMS'; }
<hive>'KEYS'                               { return '<hive>KEYS'; }
<hive>'LIMIT'                              { return '<hive>LIMIT'; }
<hive>'LINES'                              { return '<hive>LINES'; }
<hive>'LOAD'                               { determineCase(yytext); return '<hive>LOAD'; }
<hive>'LOCATION'                           { this.begin('hdfs'); return '<hive>LOCATION'; }
<hive>'LOCKS'                              { return '<hive>LOCKS'; }
<hive>'ORC'                                { return '<hive>ORC'; }
<hive>'OUTPUTFORMAT'                       { return '<hive>OUTPUTFORMAT'; }
<hive>'PARQUET'                            { return '<hive>PARQUET'; }
<hive>'PARTITIONED'                        { return '<hive>PARTITIONED'; }
<hive>'PARTITIONS'                         { return '<hive>PARTITIONS'; }
<hive>'RCFILE'                             { return '<hive>RCFILE'; }
<hive>'ROLE'                               { return '<hive>ROLE'; }
<hive>'ROLES'                              { return '<hive>ROLES'; }
<hive>'SCHEMA'                             { return '<hive>SCHEMA'; }
<hive>'SCHEMAS'                            { return '<hive>SCHEMAS'; }
<hive>'SEQUENCEFILE'                       { return '<hive>SEQUENCEFILE'; }
<hive>'SERDE'                              { return '<hive>SERDE'; }
<hive>'SERDEPROPERTIES'                    { return '<hive>SERDEPROPERTIES'; }
<hive>'SHOW'                               { determineCase(yytext); return '<hive>SHOW'; }
<hive>'SKEWED'                             { return '<hive>SKEWED'; }
<hive>'SORTED'                             { return '<hive>SORTED'; }
<hive>'STORED'                             { return '<hive>STORED'; }
<hive>'STRING'                             { return '<hive>STRING'; }
<hive>'STRUCT'                             { return '<hive>STRUCT'; }
<hive>'TABLES'                             { return '<hive>TABLES'; }
<hive>'TBLPROPERTIES'                      { return '<hive>TBLPROPERTIES'; }
<hive>'TEMPORARY'                          { return '<hive>TEMPORARY'; }
<hive>'TERMINATED'                         { return '<hive>TERMINATED'; }
<hive>'TEXTFILE'                           { return '<hive>TEXTFILE'; }
<hive>'TINYINT'                            { return '<hive>TINYINT'; }
<hive>'TRANSACTIONS'                       { return '<hive>TRANSACTIONS'; }
<hive>'UNIONTYPE'                          { return '<hive>UNIONTYPE'; }
<hive>'USE'                                { determineCase(yytext); return '<hive>USE'; }
<hive>'VIEW'                               { return '<hive>VIEW'; }

<hive>[.]                                  { return '<hive>.'; }
<hive>'['                                  { return '<hive>['; }
<hive>']'                                  { return '<hive>]'; }

// Reserved Keywords
<impala>'AGGREGATE'                        { return '<impala>AGGREGATE'; }
<impala>'AVRO'                             { return '<impala>AVRO'; }
<impala>'CACHED'                           { return '<impala>CACHED'; }
<impala>'COLUMN'                           { return '<impala>COLUMN'; }
<impala>'COMMENT'                          { return '<impala>COMMENT'; }
<impala>'CREATE'                           { determineCase(yytext); return '<impala>CREATE'; }
<impala>'DATA'                             { return '<impala>DATA'; }
<impala>'DATABASES'                        { return '<impala>DATABASES'; }
<impala>'DELIMITED'                        { return '<impala>DELIMITED'; }
<impala>'DESCRIBE'                         { determineCase(yytext); return '<impala>DESCRIBE'; }
<impala>'ESCAPED'                          { return '<impala>ESCAPED'; }
<impala>'EXTERNAL'                         { return '<impala>EXTERNAL'; }
<impala>'FIELDS'                           { return '<impala>FIELDS'; }
<impala>'FIRST'                            { return '<impala>FIRST'; }
<impala>'FORMAT'                           { return '<impala>FORMAT'; }
<impala>'FORMATTED'                        { return '<impala>FORMATTED'; }
<impala>'FUNCTION'                         { return '<impala>FUNCTION'; }
<impala>'FUNCTIONS'                        { return '<impala>FUNCTIONS'; }
<impala>'GROUP'                            { return '<impala>GROUP'; }
<impala>'INCREMENTAL'                      { return '<impala>INCREMENTAL'; }
<impala>'INPATH'                           { this.begin('hdfs'); return '<impala>INPATH'; }
<impala>'LAST'                             { return '<impala>LAST'; }
<impala>LIKE[ \t\n]+PARQUET                { this.begin('hdfs'); return '<impala>LIKE_PARQUET'; }
<impala>'LINES'                            { return '<impala>LINES'; }
<impala>'LOAD'                             { determineCase(yytext); return '<impala>LOAD'; }
<impala>'LOCATION'                         { this.begin('hdfs'); return '<impala>LOCATION'; }
<impala>'NULLS'                            { return '<impala>NULLS'; }
<impala>'PARQUET'                          { return '<impala>PARQUET'; }
<impala>'PARTITIONED'                      { return '<impala>PARTITIONED'; }
<impala>'PARTITIONS'                       { return '<impala>PARTITIONS'; }
<impala>'RCFILE'                           { return '<impala>RCFILE'; }
<impala>'REAL'                             { return '<impala>REAL'; }
<impala>'SEQUENCEFILE'                     { return '<impala>SEQUENCEFILE'; }
<impala>'SERDEPROPERTIES'                  { return '<impala>SERDEPROPERTIES'; }
<impala>'SCHEMAS'                          { return '<impala>SCHEMAS'; }
<impala>'STATS'                            { return '<impala>STATS'; }
<impala>'STORED'                           { return '<impala>STORED'; }
<impala>'TABLE'                            { return '<impala>TABLE'; }
<impala>'TABLES'                           { return '<impala>TABLES'; }
<impala>'TBLPROPERTIES'                    { return '<impala>TBLPROPERTIES'; }
<impala>'TERMINATED'                       { return '<impala>TERMINATED'; }
<impala>'TEXTFILE'                         { return '<impala>TEXTFILE'; }
<impala>'USING'                            { return '<impala>USING'; }

// Non-reserved Keywords
<impala>'ANALYTIC'                         { return '<impala>ANALYTIC'; }
<impala>'ANTI'                             { return '<impala>ANTI'; }
<impala>'CURRENT'                          { return '<impala>CURRENT'; }
<impala>'GRANT'                            { return '<impala>GRANT'; }
<impala>'OVER'                             { return '<impala>OVER'; }
<impala>'ROLE'                             { return '<impala>ROLE'; }
<impala>'ROLES'                            { return '<impala>ROLES'; }

<impala>\[SHUFFLE\]                        { return '<impala>SHUFFLE'; }
<impala>\[BROADCAST\]                      { return '<impala>BROADCAST'; }
<impala>[.]                                { return '<impala>.'; }
<impala>'['                                { return '<impala>['; }
<impala>']'                                { return '<impala>]'; }

<between>'AND'                             { this.popState(); return 'BETWEEN_AND'; }

// Reserved Keywords
'ALL'                                      { return 'ALL'; }
'AND'                                      { return 'AND'; }
'AS'                                       { return 'AS'; }
'ASC'                                      { return 'ASC'; }
'BETWEEN'                                  { this.begin('between'); return 'BETWEEN'; }
'BIGINT'                                   { return 'BIGINT'; }
'BOOLEAN'                                  { return 'BOOLEAN'; }
'BY'                                       { return 'BY'; }
'CASE'                                     { return 'CASE'; }
'CHAR'                                     { return 'CHAR'; }
'CREATE'                                   { determineCase(yytext); return 'CREATE'; }
'DATABASE'                                 { return 'DATABASE'; }
'DECIMAL'                                  { return 'DECIMAL'; }
'DISTINCT'                                 { return 'DISTINCT'; }
'DOUBLE'                                   { return 'DOUBLE'; }
'DESC'                                     { return 'DESC'; }
'DROP'                                     { determineCase(yytext); return 'DROP'; }
'ELSE'                                     { return 'ELSE'; }
'END'                                      { return 'END'; }
'EXISTS'                                   { parser.yy.correlatedSubQuery = true; return 'EXISTS'; }
'FALSE'                                    { return 'FALSE'; }
'FLOAT'                                    { return 'FLOAT'; }
'FROM'                                     { return 'FROM'; }
'FULL'                                     { return 'FULL'; }
'GROUP'                                    { return 'GROUP'; }
'GROUPING'                                 { return 'GROUPING'; } // Not in Impala?
'IF'                                       { return 'IF'; }
'IN'                                       { return 'IN'; }
'INNER'                                    { return 'INNER'; }
'INT'                                      { return 'INT'; }
'INTO'                                     { return 'INTO'; }
'IS'                                       { return 'IS'; }
'JOIN'                                     { return 'JOIN'; }
'LEFT'                                     { return 'LEFT'; }
'LIKE'                                     { return 'LIKE'; }
'LIMIT'                                    { return 'LIMIT'; }
'NOT'                                      { return 'NOT'; }
'NULL'                                     { return 'NULL'; }
'ON'                                       { return 'ON'; }
'OR'                                       { return 'OR'; }
'ORDER'                                    { return 'ORDER'; }
'OUTER'                                    { return 'OUTER'; }
'REGEXP'                                   { return 'REGEXP'; }
'RIGHT'                                    { return 'RIGHT'; }
'RLIKE'                                    { return 'RLIKE'; }
'ROW'                                      { return 'ROW'; }
'SCHEMA'                                   { return 'SCHEMA'; }
'SELECT'                                   { determineCase(yytext); return 'SELECT'; }
'SEMI'                                     { return 'SEMI'; }
'SET'                                      { return 'SET'; }
'SHOW'                                     { determineCase(yytext); return 'SHOW'; }
'SMALLINT'                                 { return 'SMALLINT'; }
'STRING'                                   { return 'STRING'; }
'TABLE'                                    { return 'TABLE'; }
'THEN'                                     { return 'THEN'; }
'TIMESTAMP'                                { return 'TIMESTAMP'; }
'TINYINT'                                  { return 'TINYINT'; }
'TRUE'                                     { return 'TRUE'; }
'UPDATE'                                   { determineCase(yytext); return 'UPDATE'; }
'USE'                                      { determineCase(yytext); return 'USE'; }
'VARCHAR'                                  { return 'VARCHAR'; } // Not in Impala
'WHEN'                                     { return 'WHEN'; }
'WHERE'                                    { return 'WHERE'; }
'WITH'                                     { return 'WITH'; }

// Non-reserved Keywords
'ROLE'                                     { return 'ROLE'; }

// --- UDFs ---
'AVG('                                     { addFunctionLocation(yylloc, 'avg'); return 'AVG('; }
'CAST('                                    { addFunctionLocation(yylloc, 'cast');return 'CAST('; }
'COUNT('                                   { addFunctionLocation(yylloc, 'count');return 'COUNT('; }
'MAX('                                     { addFunctionLocation(yylloc, 'max');return 'MAX('; }
'MIN('                                     { addFunctionLocation(yylloc, 'min');return 'MIN('; }
'STDDEV_POP('                              { addFunctionLocation(yylloc, 'stddev_pop');return 'STDDEV_POP('; }
'STDDEV_SAMP('                             { addFunctionLocation(yylloc, 'stddev_samp');return 'STDDEV_SAMP('; }
'SUM('                                     { addFunctionLocation(yylloc, 'sum');return 'SUM('; }
'VARIANCE('                                { addFunctionLocation(yylloc, 'variance');return 'VARIANCE('; }
'VAR_POP('                                 { addFunctionLocation(yylloc, 'var_pop');return 'VAR_POP('; }
'VAR_SAMP('                                { addFunctionLocation(yylloc, 'var_samp');return 'VAR_SAMP('; }
<hive>'COLLECT_SET('                       { addFunctionLocation(yylloc, 'collect_set');return '<hive>COLLECT_SET('; }
<hive>'COLLECT_LIST('                      { addFunctionLocation(yylloc, 'collect_list');return '<hive>COLLECT_LIST('; }
<hive>'CORR('                              { addFunctionLocation(yylloc, 'corr');return '<hive>CORR('; }
<hive>'COVAR_POP('                         { addFunctionLocation(yylloc, 'covar_pop');return '<hive>COVAR_POP('; }
<hive>'COVAR_SAMP('                        { addFunctionLocation(yylloc, 'covar_samp');return '<hive>COVAR_SAMP('; }
<hive>'HISTOGRAM_NUMERIC('                 { addFunctionLocation(yylloc, 'histogram_numeric');return '<hive>HISTOGRAM_NUMERIC('; }
<hive>'NTILE('                             { addFunctionLocation(yylloc, 'ntile');return '<hive>NTILE('; }
<hive>'PERCENTILE('                        { addFunctionLocation(yylloc, 'percentile');return '<hive>PERCENTILE('; }
<hive>'PERCENTILE_APPROX('                 { addFunctionLocation(yylloc, 'percentile_approx');return '<hive>PERCENTILE_APPROX('; }
<impala>'APPX_MEDIAN('                     { addFunctionLocation(yylloc, 'appx_median');return '<impala>APPX_MEDIAN('; }
<impala>'EXTRACT('                         { addFunctionLocation(yylloc, 'extract');return '<impala>EXTRACT('; }
<impala>'GROUP_CONCAT('                    { addFunctionLocation(yylloc, 'group_concat');return '<impala>GROUP_CONCAT('; }
<impala>'STDDEV('                          { addFunctionLocation(yylloc, 'stddev');return '<impala>STDDEV('; }
<impala>'VARIANCE_POP('                    { addFunctionLocation(yylloc, 'variance_pop');return '<impala>VARIANCE_POP('; }
<impala>'VARIANCE_SAMP('                   { addFunctionLocation(yylloc, 'variance_samp');return '<impala>VARIANCE_SAMP('; }
[A-Za-z][A-Za-z0-9_]*\(                    { addFunctionLocation(yylloc, yytext.substring(0, yytext.length - 1)); return 'UDF('; }

[0-9]+                                     { return 'UNSIGNED_INTEGER'; }
[0-9]+E                                    { return 'UNSIGNED_INTEGER_E'; }
[A-Za-z][A-Za-z0-9_]*                      { return 'REGULAR_IDENTIFIER'; }

<hdfs>'\u2020'                             { parser.yy.cursorFound = true; return 'CURSOR'; }
<hdfs>'\u2021'                             { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }
<hdfs>\s+[']                               { return 'HDFS_START_QUOTE'; }
<hdfs>[^'\u2020\u2021]+                    { return 'HDFS_PATH'; }
<hdfs>[']                                  { this.popState(); return 'HDFS_END_QUOTE'; }
<hdfs><<EOF>>                              { return 'EOF'; }

'&&'                                       { return 'AND'; }
'||'                                       { return 'OR'; }

'='                                        { return '='; }
'<'                                        { return '<'; }
'>'                                        { return '>'; }
'!='                                       { return 'COMPARISON_OPERATOR'; }
'<='                                       { return 'COMPARISON_OPERATOR'; }
'>='                                       { return 'COMPARISON_OPERATOR'; }
'<>'                                       { return 'COMPARISON_OPERATOR'; }
'<=>'                                      { return 'COMPARISON_OPERATOR'; }

'-'                                        { return '-'; }
'*'                                        { return '*'; }
'+'                                        { return 'ARITHMETIC_OPERATOR'; }
'/'                                        { return 'ARITHMETIC_OPERATOR'; }
'%'                                        { return 'ARITHMETIC_OPERATOR'; }
'|'                                        { return 'ARITHMETIC_OPERATOR'; }
'^'                                        { return 'ARITHMETIC_OPERATOR'; }
'&'                                        { return 'ARITHMETIC_OPERATOR'; }

'-'                                        { return '-'; }
'*'                                        { return '*'; }
'+'                                        { return 'ARITHMETIC_OPERATOR'; }
'/'                                        { return 'ARITHMETIC_OPERATOR'; }
'%'                                        { return 'ARITHMETIC_OPERATOR'; }
'|'                                        { return 'ARITHMETIC_OPERATOR'; }
'^'                                        { return 'ARITHMETIC_OPERATOR'; }
'&'                                        { return 'ARITHMETIC_OPERATOR'; }

','                                        { return ','; }
'.'                                        { return '.'; }
':'                                        { return ':'; }
';'                                        { return ';'; }
'~'                                        { return '~'; }
'!'                                        { return '!'; }

'('                                        { return '('; }
')'                                        { return ')'; }
'['                                        { return '['; }
']'                                        { return ']'; }

\$\{[^}]*\}                                { return 'VARIABLE_REFERENCE'; }

\`                                         { this.begin('backtickedValue'); return 'BACKTICK'; }
<backtickedValue>[^`]+                     {
                                             if (yytext.indexOf('\u2020') !== -1 || yytext.indexOf('\u2021') !== -1) {
                                               this.popState();
                                               return 'PARTIAL_VALUE';
                                             }
                                             return 'VALUE';
                                           }
<backtickedValue>\`                        { this.popState(); return 'BACKTICK'; }

\'                                         { this.begin('singleQuotedValue'); return 'SINGLE_QUOTE'; }
<singleQuotedValue>[^']+                   { return 'VALUE'; }
<singleQuotedValue>\'                      { this.popState(); return 'SINGLE_QUOTE'; }

\"                                         { this.begin('doubleQuotedValue'); return 'DOUBLE_QUOTE'; }
<doubleQuotedValue>[^"]+                   { return 'VALUE'; }
<doubleQuotedValue>\"                      { this.popState(); return 'DOUBLE_QUOTE'; }

<<EOF>>                                    { return 'EOF'; }

.                                          { /* To prevent console logging of unknown chars */ }

/lex

/* operators and precedence levels */

%left 'AND' 'OR'
%left 'BETWEEN'
%left 'NOT' '!' '~'
%left '=' '<' '>' 'COMPARISON_OPERATOR'
%left '-' '*' 'ARITHMETIC_OPERATOR'

%left ';'
%nonassoc 'CURSOR' 'PARTIAL_CURSOR'
%nonassoc 'IN' 'IS' 'LIKE' 'RLIKE' 'REGEXP' 'EXISTS' NEGATION

%start Sql

%%

NonReservedKeyword
 : '<hive>AVRO'
 | '<hive>BUCKETS'
 | '<hive>CLUSTERED'
 | '<hive>COLLECTION'
 | '<hive>COLUMNS'
 | '<hive>COMMENT'
 | '<hive>COMPACTIONS'
 | '<hive>DATA'
 | '<hive>DATABASES'
 | '<hive>DEFINED'
 | '<hive>DELIMITED'
 | '<hive>ESCAPED'
 | '<hive>FIELDS'
 | '<hive>FORMAT'
 | '<hive>FUNCTIONS'
 | '<hive>INPATH'
 | '<hive>INPUTFORMAT'
 | '<hive>ITEMS'
 | '<hive>KEYS'
 | '<hive>LINES'
 | '<hive>LOAD'
 | '<hive>LOCATION'
 | '<hive>LOCKS'
 | '<hive>ORC'
 | '<hive>OUTPUTFORMAT'
 | '<hive>PARQUET'
 | '<hive>PARTITIONED'
 | '<hive>PARTITIONS'
 | '<hive>RCFILE'
 | '<hive>ROLE'
 | '<hive>ROLES'
 | '<hive>SCHEMAS'
 | '<hive>SEQUENCEFILE'
 | '<hive>SERDE'
 | '<hive>SERDEPROPERTIES'
 | '<hive>SKEWED'
 | '<hive>SORTED'
 | '<hive>STORED'
 | '<hive>STRING'
 | '<hive>STRUCT'
 | '<hive>TABLES'
 | '<hive>TBLPROPERTIES'
 | '<hive>TEMPORARY'
 | '<hive>TERMINATED'
 | '<hive>TEXTFILE'
 | '<hive>TINYINT'
 | '<hive>TRANSACTIONS'
 | '<hive>UNIONTYPE'
 | '<hive>USE'
 | '<hive>VIEW'
// | '<hive>ASC'      // These cause conflicts, we need separate lexer state for DESCRIBE and SHOW then it should be fine
// | '<hive>DESC'
// | '<hive>FORMATTED'
// | '<hive>INDEX'
// | '<hive>INDEXES'
// | '<hive>LIMIT'
// | '<hive>SCHEMA'
// | '<hive>SHOW'
 | '<impala>ANALYTIC'
 | '<impala>ANTI'
 | '<impala>CURRENT'
 | '<impala>GRANT'
 | '<impala>OVER'
 | '<impala>ROLE'
 | '<impala>ROLES'
 | 'ROLE'
 ;

RegularIdentifier
 : 'REGULAR_IDENTIFIER'
 | 'VARIABLE_REFERENCE'
 | NonReservedKeyword
 ;

NewStatement
 : /* empty */
   {
     prepareNewStatement();
   }
 ;

Sql
 : NewStatement SqlStatements EOF
   {
     return parser.yy.result;
   }
 | NewStatement SqlStatements_EDIT EOF
   {
     return parser.yy.result;
   }
 ;

SqlStatements
 :
 | ErrorStatement
 | DataDefinition
 | DataManipulation
 | QuerySpecification
 | SqlStatements ';' NewStatement SqlStatements
 ;


ErrorStatement
 : error
 | NonStartingToken error // Having just ': error' does not work for some reason, jison bug?
 ;

// This is a work-around for error handling when a statement starts with some token that the parser can understand but
// it's not a valid statement (see ErrorStatement). It contains everything except valid starting tokens ('SELECT', 'USE' etc.)
NonStartingToken
 : '<hive>ALL' | '<hive>ARRAY' | '<hive>AVRO' | '<hive>BINARY' | '<hive>BUCKETS' | '<hive>AS' | '<hive>CLUSTERED' | '<hive>COLLECTION' | '<hive>CONF' | '<hive>CROSS' | '<hive>CURRENT' | '<hive>DATE' | '<hive>DELIMITED' | '<hive>ESCAPED' | '<hive>EXTENDED' | '<hive>EXTERNAL' | '<hive>FIELDS' | '<hive>FORMAT' | '<hive>FUNCTION' | '<hive>GRANT' | '<hive>LATERAL' | '<hive>MACRO' | '<hive>PARTITION' | '<hive>TABLE' | '<hive>USER' | '<hive>ASC' | '<hive>COLUMNS' | '<hive>COMMENT' | '<hive>COMPACTIONS' | '<hive>DATA' | '<hive>DATABASES' | '<hive>DEFINED' | '<hive>DESC' | '<hive>STORED_AS_DIRECTORIES' | '<hive>FORMATTED' | '<hive>FUNCTIONS' | '<hive>INDEX' | '<hive>INDEXES' | '<hive>INPATH' | '<hive>INPUTFORMAT' | '<hive>ITEMS' | '<hive>LIMIT' | '<hive>KEYS' | '<hive>LINES' | '<hive>LOCATION' | '<hive>LOCKS' | '<hive>MAP' | '<hive>ORC' | '<hive>OUTPUTFORMAT' | '<hive>PARQUET' | '<hive>PARTITIONED' | '<hive>PARTITIONS' | '<hive>RCFILE' | '<hive>ROLE' | '<hive>ROLES' | '<hive>SCHEMA' | '<hive>SCHEMAS' | '<hive>SEQUENCEFILE' | '<hive>SERDE' | '<hive>SERDEPROPERTIES' | '<hive>SKEWED' | '<hive>SORTED' | '<hive>STORED' | '<hive>STRING' | '<hive>STRUCT' | '<hive>TABLES' | '<hive>TBLPROPERTIES' | '<hive>TEMPORARY' | '<hive>TERMINATED' | '<hive>TEXTFILE' | '<hive>TINYINT' | '<hive>TRANSACTIONS' | '<hive>UNIONTYPE' | '<hive>VIEW' | '<hive>.' | '<hive>[' | '<hive>]'
 | '<impala>AGGREGATE' | '<impala>AVRO' | '<impala>CACHED' | '<impala>COLUMN' | '<impala>COMMENT' | '<impala>DATA' | '<impala>DATABASES' | '<impala>DELIMITED' | '<impala>ESCAPED' | '<impala>EXTERNAL' | '<impala>FIELDS' | '<impala>FIRST' | '<impala>FORMAT' | '<impala>FORMATTED' | '<impala>FUNCTION' | '<impala>FUNCTIONS' | '<impala>GROUP' | '<impala>INCREMENTAL' | '<impala>INPATH' | '<impala>LAST' | '<impala>LINES' | '<impala>LOCATION' | '<impala>NULLS' | '<impala>PARTITIONS' | '<impala>REAL' | '<impala>SCHEMAS' | '<impala>STATS' | '<impala>TABLE' | '<impala>TABLES' | '<impala>USING' | '<impala>ANALYTIC' | '<impala>ANTI' | '<impala>CURRENT' | '<impala>GRANT' | '<impala>OVER' | '<impala>PARQUET' | '<impala>PARTITIONED' | '<impala>RCFILE' | '<impala>ROLE' | '<impala>ROLES' | '<impala>SEQUENCEFILE' | '<impala>SERDEPROPERTIES' | '<impala>SHUFFLE' | '<impala>STORED' | '<impala>TBLPROPERTIES' | '<impala>TERMINATED' | '<impala>TEXTFILE' | '<impala>BROADCAST' | '<impala>.' | '<impala>[' | '<impala>]'
 | 'ALL' | 'AS' | 'ASC' | 'BETWEEN' | 'BIGINT' | 'BOOLEAN' | 'BY' | 'CASE' | 'CHAR' | 'DATABASE' | 'DECIMAL' | 'DISTINCT' | 'DOUBLE' | 'DESC' | 'ELSE' | 'END' | 'EXISTS' | 'FALSE' | 'FLOAT' | 'FROM' | 'FULL' | 'GROUP' | 'GROUPING' | 'IF' | 'IN' | 'INNER' | 'INT' | 'INTO' | 'IS' | 'JOIN' | 'LEFT' | 'LIKE' | 'LIMIT' | 'NOT' | 'NULL' | 'ON' | 'ORDER' | 'OUTER' | 'REGEXP' | 'RIGHT' | 'RLIKE' | 'ROW' | 'SCHEMA' | 'SEMI' | 'SET' | 'SMALLINT' | 'STRING' | 'TABLE' | 'THEN' | 'TIMESTAMP' | 'TINYINT' | 'TRUE' | 'VARCHAR' | 'WHEN' | 'WHERE' | 'WITH' | 'ROLE' | 'AVG(' | 'CAST(' | 'COUNT(' | 'MAX(' | 'MIN(' | 'STDDEV_POP(' | 'STDDEV_SAMP(' | 'SUM(' | 'VARIANCE(' | 'VAR_POP(' | 'VAR_SAMP('
 | '<hive>COLLECT_SET(' | '<hive>COLLECT_LIST(' | '<hive>CORR(' | '<hive>COVAR_POP(' | '<hive>COVAR_SAMP(' | '<hive>HISTOGRAM_NUMERIC(' | '<hive>NTILE(' | '<hive>PERCENTILE(' | '<hive>PERCENTILE_APPROX('
 | '<impala>APPX_MEDIAN(' | '<impala>EXTRACT(' | '<impala>GROUP_CONCAT(' | '<impala>STDDEV(' | '<impala>VARIANCE_POP(' | '<impala>VARIANCE_SAMP('
 | 'UDF('
 | 'UNSIGNED_INTEGER' | 'UNSIGNED_INTEGER_E' | 'REGULAR_IDENTIFIER' | 'HDFS_START_QUOTE' | 'AND' | 'OR' | '=' | '<' | '>' | 'COMPARISON_OPERATOR' | '-' | '*' | 'ARITHMETIC_OPERATOR' | ',' | '.' | '~' | '!' | '(' | ')' | '[' | ']' | 'VARIABLE_REFERENCE' | 'BACKTICK' | 'SINGLE_QUOTE' | 'DOUBLE_QUOTE'
 ;


SqlStatements_EDIT
 : SqlStatement_EDIT
 | SqlStatement_EDIT ';' NewStatement SqlStatements
 | SqlStatements ';' NewStatement SqlStatement_EDIT
 | SqlStatements ';' NewStatement SqlStatement_EDIT ';' NewStatement SqlStatements
 ;

SqlStatement_EDIT
 : AnyCursor
   {
     suggestDdlAndDmlKeywords();
   }
 | DataDefinition_EDIT
 | DataManipulation_EDIT
 | QuerySpecification_EDIT
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
 | '<hive>SCHEMA'
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

HiveOrImpalaTables
 : '<hive>TABLES'
 | '<impala>TABLES'
 ;

HiveRoleOrUser
 : '<hive>ROLE'
 | '<hive>USER'
 ;

SingleQuotedValue
 : 'SINGLE_QUOTE' 'VALUE' 'SINGLE_QUOTE'  -> $2
 | 'SINGLE_QUOTE' 'SINGLE_QUOTE'          -> ''
 ;

DoubleQuotedValue
 : 'DOUBLE_QUOTE' 'VALUE' 'DOUBLE_QUOTE'  -> $2
 | 'DOUBLE_QUOTE' 'DOUBLE_QUOTE'          -> ''
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
     parser.yy.correlatedSubQuery = false;
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
     parser.yy.correlatedSubQuery = false;
   }
 ;

OptionalIfNotExists_EDIT
 : 'IF' 'CURSOR'
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

PartialBacktickedOrAnyCursor
 : AnyCursor
 | PartialBacktickedIdentifier
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
     addTableLocation(@1, [ { name: $1 } ]);
     $$ = { identifierChain: [ { name: $1 } ] };
   }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     addTableLocation(@3, [ { name: $1 }, { name: $3 } ]);
     $$ = { identifierChain: [ { name: $1 }, { name: $3 } ] };
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
 | 'BACKTICK' 'BACKTICK'          -> ''
 ;

// TODO: Same as SchemaQualifiedTableIdentifier?
RegularOrBackTickedSchemaQualifiedName
 : RegularOrBacktickedIdentifier
   {
     addTableLocation(@1, [ { name: $1 } ]);
     $$ = { identifierChain: [ { name: $1 } ] };
   }
 | RegularOrBacktickedIdentifier AnyDot RegularOrBacktickedIdentifier
   {
     addTableLocation(@3, [ { name: $1 }, { name: $3 } ]);
     $$ = { identifierChain: [ { name: $1 }, { name: $3 } ] };
   }
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

ColumnReference
 : BasicIdentifierChain
   {
     addColumnLocation(@1, $1);
   }
 | BasicIdentifierChain AnyDot '*'
   {
     addColumnLocation(@1, $1);
   }
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
 | '<hive>TINYINT'
 | 'SMALLINT'
 | 'INT'
 | 'BIGINT'
 | 'BOOLEAN'
 | 'FLOAT'
 | 'DOUBLE'
 | '<impala>REAL'
 | 'STRING'
 | '<hive>STRING'
 | 'DECIMAL'
 | 'CHAR'
 | 'VARCHAR'
 | 'TIMESTAMP'
 | '<hive>BINARY'
 | '<hive>DATE'
 ;

// ===================================== CREATE statement =====================================

CreateStatement
 : DatabaseDefinition
 | TableDefinition
 ;

CreateStatement_EDIT
 : DatabaseDefinition_EDIT
 | TableDefinition_EDIT
 | AnyCreate OptionalHiveTemporary OptionalExternal 'CURSOR'
   {
     if ($3) {
       suggestKeywords(['TABLE']);
     } else if (isHive()) {
       if ($2) {
         suggestKeywords(['EXTERNAL TABLE', 'TABLE']);
       } else {
         suggestKeywords(['DATABASE', 'EXTERNAL TABLE', 'SCHEMA', 'TABLE', 'TEMPORARY EXTERNAL TABLE', 'TEMPORARY TABLE']);
       }
     } else if (isImpala()) {
       suggestKeywords(['DATABASE', 'EXTERNAL TABLE', 'SCHEMA', 'TABLE']);
     } else {
       suggestKeywords(['DATABASE', 'SCHEMA', 'TABLE']);
     }
   }
 ;


DatabaseDefinition
 : AnyCreate DatabaseOrSchema OptionalIfNotExists
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals
 ;

DatabaseDefinition_EDIT
 : AnyCreate DatabaseOrSchema OptionalIfNotExists 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_EDIT
 | AnyCreate DatabaseOrSchema OptionalIfNotExists 'CURSOR' RegularIdentifier
   {
     if (!$3) {
       suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate DatabaseOrSchema OptionalIfNotExists_EDIT RegularIdentifier
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals_EDIT error
 | AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals 'CURSOR'
 ;

DatabaseDefinitionOptionals
 : OptionalComment OptionalHdfsLocation OptionalHiveDbProperties
   {
     var keywords = [];
     if (!$3 && isHive()) {
       keywords.push('WITH DBPROPERTIES');
     }
     if (!$2 && !$3) {
       keywords.push('LOCATION');
     }
     if (!$1 && !$2 && !$3) {
       keywords.push('COMMENT');
     }
     if (keywords.length > 0) {
       suggestKeywords(keywords);
     }
   }
 ;

DatabaseDefinitionOptionals_EDIT
 : OptionalComment_INVALID OptionalHdfsLocation OptionalHiveDbProperties
 | OptionalComment OptionalHdfsLocation_EDIT OptionalHiveDbProperties
 ;

OptionalComment
 :
 | Comment
 ;

Comment
 : HiveOrImpalaComment SingleQuotedValue
 ;

Comment_INVALID
 : HiveOrImpalaComment SINGLE_QUOTE
 | HiveOrImpalaComment SINGLE_QUOTE VALUE
 ;

OptionalComment_INVALID
 : Comment_INVALID
 ;

OptionalHdfsLocation
 :
 | HdfsLocation
 ;

OptionalHdfsLocation_EDIT
 : HdfsLocation_EDIT
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

OptionalHiveDbProperties
 :
 | HiveDbProperties
 ;

HiveDbProperties
 : '<hive>WITH' 'DBPROPERTIES' ParenthesizedPropertyAssignmentList
 | '<hive>WITH' 'DBPROPERTIES'
 | '<hive>WITH' 'CURSOR'
   {
     suggestKeywords(['DBPROPERTIES']);
   }
 ;

ParenthesizedPropertyAssignmentList
 : '(' PropertyAssignmentList ')'
 ;

PropertyAssignmentList
 : PropertyAssignment
 | PropertyAssignmentList ',' PropertyAssignment
 ;

PropertyAssignment
 : QuotedValue '=' UnsignedValueSpecification
 ;

TableDefinition
 : AnyCreate OptionalHiveTemporary OptionalExternal AnyTable OptionalIfNotExists TableDefinitionRightPart
 ;

TableDefinition_EDIT
 : AnyCreate OptionalHiveTemporary OptionalExternal AnyTable OptionalIfNotExists TableDefinitionRightPart_EDIT
 | AnyCreate OptionalHiveTemporary OptionalExternal AnyTable OptionalIfNotExists 'CURSOR'
   {
     if (!$5) {
       suggestKeywords(['IF NOT EXISTS']);
     }
   }
 | AnyCreate OptionalHiveTemporary OptionalExternal AnyTable OptionalIfNotExists_EDIT
 ;

TableDefinitionRightPart
 : TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 ;

TableDefinitionRightPart_EDIT
 : TableIdentifierAndOptionalColumnSpecification_EDIT OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy_EDIT OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties_EDIT OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy_EDIT
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy_EDIT OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy_EDIT OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation_EDIT OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn_EDIT OptionalAsSelectStatement
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn OptionalAsSelectStatement_EDIT
 | TableIdentifierAndOptionalColumnSpecification OptionalComment OptionalPartitionedBy OptionalImpalaWithSerdeproperties OptionalHiveClusteredBy
   OptionalHiveSkewedBy OptionalStoredAsOrBy OptionalHdfsLocation OptionalTblproperties OptionalImpalaCachedIn 'CURSOR'
   {
     // TODO: Don't always sort the keywords as order is important
     var keywords = [];
     if (!$1 && !$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
       keywords.push('LIKE');
       if (isImpala()) {
         keywords.push('LIKE PARQUET');
       }
     } else {
       keywords.push('AS');
       if (!$2 && !$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push('COMMENT');
       }
       if (!$3 && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push('PARTITIONED BY');
       }
       if (isImpala() && !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push('WITH SERDEPROPERTIES');
       }
       if (isHive() && !$5 && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push('CLUSTERED BY');
       }
       if (isHive() && !$6 && !$7 && !$8 && !$9 && !$10) {
         keywords.push('SKEWED BY');
       } else if (isHive() && $6 && $6.suggestKeywords && !$7 && !$8 && !$9 && !$10) {
         keywords = keywords.concat($6.suggestKeywords); // Get the last optional from SKEWED BY
       }
       if (!$7 && !$8 && !$9 && !$10) {
         keywords.push('ROW FORMAT');
         keywords.push('STORED AS');
         if (isHive()) {
          keywords.push('STORED BY');
         }
       } else if ($7 && $7.suggestKeywords && !$8 && !$9 && !$10) {
         keywords = keywords.concat($7.suggestKeywords);
       }
       if (!$8 && !$9 && !$10) {
         keywords.push('LOCATION');
       }
       if (!$9 && !$10) {
         keywords.push('TBLPROPERTIES');
       }
       if (isImpala() && !$10) {
         keywords.push('CACHED IN');
       }
     }

     if (keywords.length > 0) {
       suggestKeywords(keywords);
     }
   }
 ;

// Hack as no space is required between table name and '(' which would be read as UDF(
// can be dropped if switched to LR(*)
TableIdentifierAndOptionalColumnSpecification
 : SchemaQualifiedTableIdentifier OptionalColumnSpecificationsOrLike  -> $2
 | 'UDF(' DropLastLocation ColumnSpecificationList ')'
 | RegularOrBacktickedIdentifier AnyDot 'UDF(' DropLastLocation ColumnSpecificationList ')'
 ;

TableIdentifierAndOptionalColumnSpecification_EDIT
 : SchemaQualifiedTableIdentifier OptionalColumnSpecificationsOrLike_EDIT
 | 'UDF(' DropLastLocation ColumnSpecificationList_EDIT RightParenthesisOrError
 | RegularOrBacktickedIdentifier AnyDot 'UDF(' DropLastLocation ColumnSpecificationList_EDIT RightParenthesisOrError
 ;

DropLastLocation
 : /* Empty */
   {
     if (parser.yy.locations.length > 0) {
       parser.yy.locations.pop();
     }
   }
 ;

OptionalHiveTemporary
 :
 | '<hive>TEMPORARY'
 ;

OptionalExternal
 :
 | '<hive>EXTERNAL'
 | '<impala>EXTERNAL'
 ;

OptionalColumnSpecificationsOrLike
 :
 | ParenthesizedColumnSpecificationList
 | '<impala>LIKE_PARQUET' HdfsPath
 | 'LIKE' SchemaQualifiedTableIdentifier
 ;

OptionalColumnSpecificationsOrLike_EDIT
 : ParenthesizedColumnSpecificationList_EDIT
 | '<impala>LIKE_PARQUET' HdfsPath_EDIT
 | 'LIKE' 'CURSOR'
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
     if (isImpala()) {
       suggestKeywords(['PARQUET']);
     }
   }
 | 'LIKE' SchemaQualifiedTableIdentifier_EDIT
 ;

ParenthesizedColumnSpecificationList
 : '(' ColumnSpecificationList ')'
 ;

ParenthesizedColumnSpecificationList_EDIT
 : '(' ColumnSpecificationList_EDIT RightParenthesisOrError
 ;

ColumnSpecificationList
 : ColumnSpecification
 | ColumnSpecificationList ',' ColumnSpecification
 ;

ColumnSpecificationList_EDIT
 : ColumnSpecification_EDIT
 | ColumnSpecification_EDIT ',' ColumnSpecificationList
 | ColumnSpecificationList ',' ColumnSpecification_EDIT
 | ColumnSpecificationList ',' ColumnSpecification_EDIT ',' ColumnSpecificationList
 ;

ColumnSpecification
 : ColumnIdentifier ColumnDataType OptionalComment
 ;

ColumnSpecification_EDIT
 : ColumnIdentifier 'CURSOR' OptionalComment
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | ColumnIdentifier ColumnDataType_EDIT
 | ColumnIdentifier ColumnDataType OptionalComment 'CURSOR'
   {
     if (!$3) {
       suggestKeywords(['COMMENT']);
     }
   }
 ;

ColumnDataType
 : PrimitiveType
 | ArrayType
 | MapType
 | StructType
 | UnionType
 | ArrayType_INVALID
 | MapType_INVALID
 | StructType_INVALID
 | UnionType_INVALID
 ;

ColumnDataType_EDIT
 : ArrayType_EDIT
 | MapType_EDIT
 | StructType_EDIT
 | UnionType_EDIT
 ;

ArrayType
 : '<hive>ARRAY' '<' ColumnDataType '>'
 ;

ArrayType_INVALID
 : '<hive>ARRAY' '<' '>'
 ;

ArrayType_EDIT
 : '<hive>ARRAY' '<' AnyCursor GreaterThanOrError
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | '<hive>ARRAY' '<' ColumnDataType_EDIT GreaterThanOrError
 ;

MapType
 : '<hive>MAP' '<' PrimitiveType ',' ColumnDataType '>'
 ;

MapType_INVALID
 : '<hive>MAP' '<' '>'
 ;

MapType_EDIT
 : '<hive>MAP' '<' PrimitiveType ',' ColumnDataType_EDIT GreaterThanOrError
 | '<hive>MAP' '<' AnyCursor GreaterThanOrError
   {
     suggestKeywords(getTypeKeywords());
   }
 | '<hive>MAP' '<' PrimitiveType ',' AnyCursor GreaterThanOrError
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | '<hive>MAP' '<' ',' AnyCursor GreaterThanOrError
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 ;

StructType
 : '<hive>STRUCT' '<' StructDefinitionList '>'
 ;

StructType_INVALID
 : '<hive>STRUCT' '<' '>'
 ;

StructType_EDIT
 : '<hive>STRUCT' '<' StructDefinitionList_EDIT GreaterThanOrError
 ;

StructDefinitionList
 : StructDefinition
 | StructDefinitionList ',' StructDefinition
 ;

StructDefinitionList_EDIT
 : StructDefinition_EDIT
 | StructDefinition_EDIT Commas
 | StructDefinition_EDIT Commas StructDefinitionList
 | StructDefinitionList ',' StructDefinition_EDIT
 | StructDefinitionList ',' StructDefinition_EDIT Commas StructDefinitionList
 ;

Commas
 : ','
 | Commas ','
 ;

StructDefinition
 : RegularOrBacktickedIdentifier ':' ColumnDataType OptionalComment
 ;

StructDefinition_EDIT
 : Commas RegularOrBacktickedIdentifier ':' ColumnDataType 'CURSOR'
   {
     suggestKeywords(['COMMENT']);
   }
 | Commas RegularOrBacktickedIdentifier ':' AnyCursor
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | Commas RegularOrBacktickedIdentifier ':' ColumnDataType_EDIT
 | RegularOrBacktickedIdentifier ':' ColumnDataType 'CURSOR'
   {
     suggestKeywords(['COMMENT']);
   }
 | RegularOrBacktickedIdentifier ':' AnyCursor
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | RegularOrBacktickedIdentifier ':' ColumnDataType_EDIT
 ;

UnionType
 : '<hive>UNIONTYPE' '<' ColumnDataTypeList '>'
 ;

UnionType_INVALID
 : '<hive>UNIONTYPE' '<' '>'
 ;

UnionType_EDIT
 : '<hive>UNIONTYPE' '<' ColumnDataTypeList_EDIT GreaterThanOrError
 ;

ColumnDataTypeList
 : ColumnDataType
 | ColumnDataTypeList ',' ColumnDataType
 ;

ColumnDataTypeList_EDIT
 : ColumnDataTypeListInner_EDIT
 | ColumnDataTypeListInner_EDIT Commas
 | ColumnDataTypeList ',' ColumnDataTypeListInner_EDIT
 | ColumnDataTypeListInner_EDIT Commas ColumnDataTypeList
 | ColumnDataTypeList ',' ColumnDataTypeListInner_EDIT Commas ColumnDataTypeList
 ;

ColumnDataTypeListInner_EDIT
 : Commas AnyCursor
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | Commas ColumnDataType_EDIT
 | AnyCursor
   {
     suggestKeywords(getColumnDataTypeKeywords());
   }
 | ColumnDataType_EDIT
 ;

GreaterThanOrError
 : '>'
 | error
 ;

OptionalPartitionedBy
 :
 | HiveOrImpalaPartitioned 'BY' ParenthesizedColumnSpecificationList
 ;

OptionalPartitionedBy_EDIT
 : HiveOrImpalaPartitioned 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | HiveOrImpalaPartitioned 'CURSOR' ParenthesizedColumnSpecificationList
   {
     suggestKeywords(['BY']);
   }
 | HiveOrImpalaPartitioned 'BY' ParenthesizedColumnSpecificationList_EDIT
 | HiveOrImpalaPartitioned ParenthesizedColumnSpecificationList_EDIT
 ;

ParenthesizedColumnList
 : '(' ColumnList ')'
 ;

ColumnList
 : ColumnIdentifier
 | ColumnList ',' ColumnIdentifier
 ;

OptionalHiveClusteredBy
 :
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'INTO' 'UNSIGNED_INTEGER' '<hive>BUCKETS'
 ;

OptionalHiveClusteredBy_EDIT
 : '<hive>CLUSTERED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'CURSOR'
   {
     if (!$4) {
       suggestKeywords(['INTO', 'SORTED BY']);
     } else {
       suggestKeywords(['INTO']);
     }
   }
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy 'INTO' 'UNSIGNED_INTEGER' 'CURSOR'
   {
     suggestKeywords(['BUCKETS']);
   }
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy_EDIT 'INTO' 'UNSIGNED_INTEGER' '<hive>BUCKETS'
 | '<hive>CLUSTERED' 'BY' ParenthesizedColumnList OptionalHiveSortedBy_EDIT
 ;

OptionalHiveSortedBy
 :
 | '<hive>SORTED' 'BY' ParenthesizedSortList
 ;

OptionalHiveSortedBy_EDIT
 : '<hive>SORTED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | '<hive>SORTED' 'BY' ParenthesizedSortList_EDIT
 ;

ParenthesizedSortList
 : '(' SortList ')'
 ;

ParenthesizedSortList_EDIT
 : '(' SortList_EDIT RightParenthesisOrError
 ;

SortList
 : SortIdentifier
 | SortList ',' SortIdentifier
 ;

SortList_EDIT
 : SortIdentifier_EDIT
 | SortIdentifier_EDIT ',' SortList
 | SortList ',' SortIdentifier_EDIT
 | SortList ',' SortIdentifier_EDIT ',' SortList
 ;

SortIdentifier
 : ColumnIdentifier OptionalAscOrDesc
 ;

SortIdentifier_EDIT
 : ColumnIdentifier OptionalAscOrDesc 'CURSOR'
   {
     checkForKeywords($2);
   }
 ;


OptionalHiveSkewedBy
 :
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList ON ParenthesizedSkewedValueList  -> { suggestKeywords: ['STORED AS DIRECTORIES'] }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList ON ParenthesizedSkewedValueList '<hive>STORED_AS_DIRECTORIES' // Hack otherwise ambiguous with OptionalHiveStoredAsOrBy
 ;

OptionalHiveSkewedBy_EDIT
 : '<hive>SKEWED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | '<hive>SKEWED' 'BY' ParenthesizedColumnList 'CURSOR'
   {
     suggestKeywords(['ON']);
   }
 ;

ParenthesizedSkewedValueList
 : '(' SkewedValueList ')'
 ;

SkewedValueList
 : ParenthesizedSimpleValueList
 | SkewedValueList ',' ParenthesizedSimpleValueList
 ;

ParenthesizedSimpleValueList
 : '(' SimpleValueList ')'
 ;

SimpleValueList
 : UnsignedValueSpecification
 | SimpleValueList ',' UnsignedValueSpecification
 ;

OptionalStoredAsOrBy
 :
 | StoredAs
 | 'ROW' HiveOrImpalaFormat HiveOrImpalaRowFormat OptionalStoredAs
   {
     $$ = mergeSuggestKeywords($3, $4)
   }
 | '<hive>STORED' 'BY' QuotedValue OptionalHiveWithSerdeproperties
  {
    if (!$4) {
      $$ = { suggestKeywords: ['WITH SERDEPROPERTIES'] };
    }
  }
 ;

OptionalStoredAsOrBy_EDIT
 : HiveOrImpalaStored 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['AS', 'BY']);
     } else {
       suggestKeywords(['AS']);
     }
   }
 | StoredAs_EDIT
 | 'ROW' 'CURSOR'
   {
     suggestKeywords(['FORMAT']);
   }
 | 'ROW' HiveOrImpalaFormat 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['DELIMITED', 'SERDE']);
     } else {
       suggestKeywords(['DELIMITED']);
     }
   }
 | 'ROW' HiveOrImpalaFormat HiveOrImpalaRowFormat_EDIT
 | 'ROW' HiveOrImpalaFormat HiveOrImpalaRowFormat HiveOrImpalaStored 'CURSOR'
   {
     suggestKeywords(['AS']);
   }
 | 'ROW' HiveOrImpalaFormat HiveOrImpalaRowFormat StoredAs_EDIT
 | '<hive>STORED' 'BY' QuotedValue OptionalHiveWithSerdeproperties_EDIT
 ;

OptionalStoredAs
 :           -> { suggestKeywords: ['STORED AS'] }
 | StoredAs
 ;

StoredAs
 : HiveOrImpalaStored AnyAs FileFormat
 ;

StoredAs_EDIT
 : HiveOrImpalaStored AnyAs 'CURSOR'
   {
     if (isHive()) {
       suggestKeywords(['AVRO', 'INPUTFORMAT', 'ORC', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']);
     } else {
       suggestKeywords(['AVRO', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']);
     }
   }
 ;

HiveOrImpalaFormat
 : '<hive>FORMAT'
 | '<impala>FORMAT'
 ;

HiveOrImpalaStored
 : '<hive>STORED'
 | '<impala>STORED'
 ;

FileFormat
 : '<hive>AVRO'
 | '<hive>INPUTFORMAT' QuotedValue '<hive>OUTPUTFORMAT' QuotedValue
 | '<hive>ORC'
 | '<hive>PARQUET'
 | '<hive>RCFILE'
 | '<hive>SEQUENCEFILE'
 | '<hive>TEXTFILE'
 | '<impala>AVRO'
 | '<impala>PARQUET'
 | '<impala>RCFILE'
 | '<impala>SEQUENCEFILE'
 | '<impala>TEXTFILE'
 ;

HiveOrImpalaRowFormat
 : HiveRowFormat
 | ImpalaRowFormat
 ;

HiveOrImpalaRowFormat_EDIT
 : ImpalaRowFormat_EDIT
 | HiveRowFormat_EDIT
 ;

HiveRowFormat
 : '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs
   {
     if (!$2 && !$3 && !$4 && !$5 && !$6) {
       $$ = { suggestKeywords: ['COLLECTION ITEMS TERMINATED BY', 'FIELDS TERMINATED BY', 'LINES TERMINATED BY', 'MAP KEYS TERMINATED BY', 'NULL DEFINED AS'] };
     } else if ($2 && $2.suggestKeywords && !$3 && !$4 && !$5 && !$6) {
       $$ = { suggestKeywords: $2.suggestKeywords.concat(['COLLECTION ITEMS TERMINATED BY', 'LINES TERMINATED BY', 'MAP KEYS TERMINATED BY', 'NULL DEFINED AS']) };
     } else if (!$3 && !$4 && !$5 && !$6) {
       $$ = { suggestKeywords: ['COLLECTION ITEMS TERMINATED BY', 'LINES TERMINATED BY', 'MAP KEYS TERMINATED BY', 'NULL DEFINED AS'] };
     } else if (!$4 && !$5 && !$6) {
       $$ = { suggestKeywords: ['LINES TERMINATED BY', 'MAP KEYS TERMINATED BY', 'NULL DEFINED AS'] };
     } else if (!$5 && !$6) {
       $$ = { suggestKeywords: ['LINES TERMINATED BY', 'NULL DEFINED AS'] };
     } else if (!$6) {
       $$ = { suggestKeywords: ['NULL DEFINED AS'] };
     }
   }
 | '<hive>SERDE' QuotedValue OptionalHiveWithSerdeproperties
   {
     if (!$3) {
       $$ = { suggestKeywords: ['WITH SERDEPROPERTIES'] };
     }
   }
 ;

HiveRowFormat_EDIT
 : '<hive>DELIMITED' OptionalFieldsTerminatedBy_EDIT OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs
 | '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy_EDIT OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs
 | '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy_EDIT
   OptionalLinesTerminatedBy OptionalNullDefinedAs
 | '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy_EDIT OptionalNullDefinedAs
 | '<hive>DELIMITED' OptionalFieldsTerminatedBy OptionalCollectionItemsTerminatedBy OptionalMapKeysTerminatedBy
   OptionalLinesTerminatedBy OptionalNullDefinedAs_EDIT
 ;

ImpalaRowFormat
 : '<impala>DELIMITED' OptionalFieldsTerminatedBy OptionalLinesTerminatedBy
   {
     if (!$2 && !$3) {
       $$ = { suggestKeywords: ['FIELDS TERMINATED BY', 'LINES TERMINATED BY'] };
     } else if ($2 && $2.suggestKeywords && !$3) {
       $$ = { suggestKeywords: $2.suggestKeywords.concat(['LINES TERMINATED BY']) };
     } else if (!$3) {
       $$ = { suggestKeywords: ['LINES TERMINATED BY'] };
     }
   }
 ;

ImpalaRowFormat_EDIT
 : '<impala>DELIMITED' OptionalFieldsTerminatedBy_EDIT OptionalLinesTerminatedBy
 | '<impala>DELIMITED' OptionalFieldsTerminatedBy OptionalLinesTerminatedBy_EDIT
 ;

OptionalFieldsTerminatedBy
 :
 | HiveOrImpalaFields HiveOrImpalaTerminated 'BY' SingleQuotedValue  -> { suggestKeywords: ['ESCAPED BY'] }
 | HiveOrImpalaFields HiveOrImpalaTerminated 'BY' SingleQuotedValue HiveOrImpalaEscaped 'BY' SingleQuotedValue
 ;

OptionalFieldsTerminatedBy_EDIT
 : HiveOrImpalaFields 'CURSOR'
   {
     suggestKeywords(['TERMINATED BY']);
   }
 | HiveOrImpalaFields HiveOrImpalaTerminated 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 | HiveOrImpalaFields HiveOrImpalaTerminated 'BY' SingleQuotedValue 'ESCAPED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

HiveOrImpalaFields
 : '<hive>FIELDS'
 | '<impala>FIELDS'
 ;

HiveOrImpalaTerminated
 : '<hive>TERMINATED'
 | '<impala>TERMINATED'
 ;

HiveOrImpalaEscaped
 : '<hive>ESCAPED'
 | '<impala>ESCAPED'
 ;

OptionalCollectionItemsTerminatedBy
 :
 | '<hive>COLLECTION' '<hive>ITEMS' '<hive>TERMINATED' 'BY' SingleQuotedValue
 ;

OptionalCollectionItemsTerminatedBy_EDIT
 : '<hive>COLLECTION' 'CURSOR'
   {
     suggestKeywords(['ITEMS TERMINATED BY']);
   }
 | '<hive>COLLECTION' '<hive>ITEMS' 'CURSOR'
   {
     suggestKeywords(['TERMINATED BY']);
   }
 | '<hive>COLLECTION' '<hive>ITEMS' '<hive>TERMINATED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

OptionalMapKeysTerminatedBy
 :
 | '<hive>MAP' '<hive>KEYS' '<hive>TERMINATED' 'BY' SingleQuotedValue
 ;

OptionalMapKeysTerminatedBy_EDIT
 : '<hive>MAP' 'CURSOR'
   {
     suggestKeywords(['KEYS TERMINATED BY']);
   }
 | '<hive>MAP' '<hive>KEYS' 'CURSOR'
   {
     suggestKeywords(['TERMINATED BY']);
   }
 | '<hive>MAP' '<hive>KEYS' '<hive>TERMINATED' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

OptionalLinesTerminatedBy
 :
 | HiveOrImpalaLines HiveOrImpalaTerminated 'BY' SingleQuotedValue
 ;

OptionalLinesTerminatedBy_EDIT
 : HiveOrImpalaLines 'CURSOR'
   {
     suggestKeywords(['TERMINATED BY']);
   }
 | HiveOrImpalaLines HiveOrImpalaTerminated 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

HiveOrImpalaLines
 : '<hive>LINES'
 | '<impala>LINES'
 ;

OptionalNullDefinedAs
 :
 | 'NULL' '<hive>DEFINED' '<hive>AS' SingleQuotedValue
 ;

OptionalNullDefinedAs_EDIT
 : 'NULL' 'CURSOR'
   {
     suggestKeywords(['DEFINED AS']);
   }
 | 'NULL' '<hive>DEFINED' 'CURSOR'
   {
     suggestKeywords(['AS']);
   }
 ;

OptionalHiveWithSerdeproperties
 :
 | 'WITH' '<hive>SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

OptionalHiveWithSerdeproperties_EDIT
 : OptionalImpalaWithSerdeproperties_EDIT
 ;

OptionalImpalaWithSerdeproperties
 :
 | 'WITH' '<impala>SERDEPROPERTIES' ParenthesizedPropertyAssignmentList
 ;

OptionalImpalaWithSerdeproperties_EDIT
 : 'WITH' 'CURSOR'
   {
     suggestKeywords(['SERDEPROPERTIES']);
   }
 | 'WITH' 'CURSOR' ParenthesizedPropertyAssignmentList
   {
     suggestKeywords(['SERDEPROPERTIES']);
   }
 ;

OptionalTblproperties
 :
 | HiveOrImpalaTblproperties ParenthesizedPropertyAssignmentList
 ;

OptionalAsSelectStatement
 :
 | AnyAs CommitLocations QuerySpecification
 ;

OptionalAsSelectStatement_EDIT
 : AnyAs CommitLocations 'CURSOR'
   {
     suggestKeywords(['SELECT']);
   }
 | AnyAs CommitLocations QuerySpecification_EDIT
 ;

CommitLocations
 : /* empty */
   {
     commitLocations();
   }
 ;

OptionalImpalaCachedIn
 :
 | '<impala>CACHED' 'IN' QuotedValue
 ;

OptionalImpalaCachedIn_EDIT
 : '<impala>CACHED' 'CURSOR'
   {
     suggestKeywords(['IN']);
   }
 ;

QuotedValue
 : SingleQuotedValue
 | DoubleQuotedValue
 ;

HiveOrImpalaTblproperties
 : '<hive>TBLPROPERTIES'
 | '<impala>TBLPROPERTIES'
 ;

HiveOrImpalaPartitioned
 : '<hive>PARTITIONED'
 | '<impala>PARTITIONED'
 ;

// '<impala>AVRO'
// '<impala>CACHED'
// '<impala>DELIMITED'
// '<impala>ESCAPED'
// '<impala>FIELDS'
// '<impala>FORMAT'
// '<impala>LINES'
// '<impala>PARQUET'
// '<impala>PARTITIONED'
// '<impala>RCFILE'
// '<impala>SEQUENCEFILE'
// '<impala>SERDEPROPERTIES'
// '<impala>STORED'
// '<impala>TBLPROPERTIES'
// '<impala>TERMINATED'
// '<impala>TEXTFILE'
// '<hive>ARRAY'
// '<hive>MAP'
// 'AS'
// 'BY'
// 'IN'
// 'INTO'
// 'NULL'
// 'ON'
// 'ROW'
// 'WITH'
// '<hive>AVRO'
// '<hive>DELIMITED'
// '<hive>ESCAPED'
// '<hive>FIELDS'
// '<hive>FORMAT'
// '<hive>LINES'
// '<hive>PARQUET'
// '<hive>PARTITIONED'
// '<hive>ORC'
// '<hive>RCFILE'
// '<hive>SEQUENCEFILE'
// '<hive>SERDEPROPERTIES'
// '<hive>STORED'
// '<hive>TBLPROPERTIES'
// '<hive>TEMPORARY'
// '<hive>TERMINATED'
// '<hive>TEXTFILE'
// '<hive>BUCKETS'
// '<hive>INPUTFORMAT'
// '<hive>CLUSTERED'
// '<hive>COLLECTION'
// '<hive>DEFINED
// '<hive>DIRECTORIES'
// '<hive>ITEMS'
// '<hive>KEYS'
// '<hive>OUTPUTFORMAT'
// '<hive>SERDE'
// '<hive>SKEWED'
// '<hive>SORTED'
// '<hive>STRUCT'
// '<hive>UNIONTYPE'


// ===================================== DESCRIBE statement =====================================

DescribeStatement
 : HiveDescribeStatement
 | ImpalaDescribeStatement
 ;

DescribeStatement_EDIT
 : HiveDescribeStatement_EDIT
 | ImpalaDescribeStatement_EDIT
 ;

HiveDescribeStatement
 : '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier DerivedColumnChain
   {
     addTablePrimary($3);
     addColumnLocation(@4, $4);
   }
 | '<hive>DESCRIBE' OptionalExtendedOrFormatted SchemaQualifiedTableIdentifier
   {
     addTablePrimary($3);
   }
 | '<hive>DESCRIBE' DatabaseOrSchema OptionalExtended DatabaseIdentifier
   {
     addDatabaseLocation(@4, $4);
   }
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
   {
     addTablePrimary($3);
   }
 ;

ImpalaDescribeStatement_EDIT
 : '<impala>DESCRIBE' OptionalFormatted SchemaQualifiedTableIdentifier_EDIT
 | '<impala>DESCRIBE' OptionalFormatted 'CURSOR' SchemaQualifiedTableIdentifier
   {
     addTablePrimary($4);
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
 : 'SELECT' OptionalAllOrDistinct SelectList                  -> { selectList: $3 }
 | 'SELECT' OptionalAllOrDistinct SelectList TableExpression  -> { selectList: $3, tableExpression: $4 }
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
       checkForSelectListKeywords($3);
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
 | 'SELECT' OptionalAllOrDistinct SelectList_EDIT error TableExpression
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
 | 'SELECT' OptionalAllOrDistinct SelectList error TableExpression        // Causes conflict but solves issue
 | 'SELECT' OptionalAllOrDistinct SelectList error TableExpression_EDIT   // with SELECT a, b, cos(| c AS d
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' TableExpression
   {
     checkForSelectListKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' ',' TableExpression
   {
     checkForSelectListKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' ',' error TableExpression
   {
     checkForSelectListKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR'
   {
     checkForSelectListKeywords($3);
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
 : FromClause OptionalSelectConditions
 ;

TableExpression_EDIT
 : FromClause OptionalSelectConditions_EDIT
 | FromClause_EDIT OptionalSelectConditions
 | FromClause OptionalSelectConditions 'CURSOR' OptionalJoins
   {
     // A couple of things are going on here:
     // - If there are no SelectConditions (WHERE, GROUP BY, etc.) we should suggest complete join options
     // - If there's an OptionalJoin at the end, i.e. 'SELECT * FROM foo | JOIN ...' we should suggest
     //   different join types
     // - The FromClause could end with a valueExpression, in which case we should suggest keywords like '='
     //   or 'AND' based on type
     // The reason for the join mess is because for "SELECT * FROM foo | JOIN bar" the parts surrounding the
     // cursor are complete and not in _EDIT rules.

     if (!$2) {
       var keywords = [];
       if (typeof $1.hasJoinCondition !== 'undefined' && ! $1.hasJoinCondition) {
         keywords.push('ON');
         if (isImpala()) {
           keywords.push('USING');
         }
       }
       if (isHive()) {
         if ($4 && $4.joinType.toUpperCase() === 'JOIN') {
           keywords = keywords.concat(['CROSS', 'FULL', 'FULL OUTER', 'LEFT', 'LEFT OUTER', 'LEFT SEMI', 'RIGHT', 'RIGHT OUTER']);
         } else {
           keywords = keywords.concat(['CROSS JOIN', 'FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'JOIN', 'LATERAL VIEW', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']);
         }
       } else if (isImpala()) {
         if ($4 && $4.joinType.toUpperCase() === 'JOIN') {
           keywords = keywords.concat(['FULL', 'FULL OUTER', 'INNER', 'LEFT ANTI', 'LEFT', 'LEFT OUTER', 'LEFT SEMI', 'RIGHT ANTI', 'RIGHT', 'RIGHT OUTER', 'RIGHT SEMI']);
         } else {
           keywords = keywords.concat(['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT ANTI JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LEFT SEMI JOIN', 'LIMIT', 'ORDER BY', 'RIGHT ANTI JOIN', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'RIGHT SEMI JOIN', 'WHERE']);
         }
       } else {
         if ($4 && $4.joinType.toUpperCase() === 'JOIN') {
           keywords = keywords.concat(['FULL', 'FULL OUTER', 'INNER', 'LEFT', 'LEFT OUTER', 'RIGHT', 'RIGHT OUTER']);
         } else {
           keywords = keywords.concat(['FULL JOIN', 'FULL OUTER JOIN', 'GROUP BY', 'INNER JOIN', 'JOIN', 'LEFT JOIN', 'LEFT OUTER JOIN', 'LIMIT', 'ORDER BY', 'RIGHT JOIN', 'RIGHT OUTER JOIN', 'WHERE']);
         }
       }
       if ($1.suggestKeywords) {
         keywords = keywords.concat($1.suggestKeywords);
         suggestKeywords(keywords);
       } else if ($1.types) {
        // Checks if valueExpression could happen when there's no OptionalJoinCondition
         suggestValueExpressionKeywords($1, keywords);
       } else {
         suggestKeywords(keywords);
       }
     } else {
       checkForKeywords($2);
     }
   }
 ;

OptionalJoins
 :
 | Joins
 | Joins_INVALID
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

OptionalSelectConditions
 : OptionalWhereClause OptionalGroupByClause OptionalOrderByClause OptionalLimitClause
   {
     if ($1 && !$2 && !$3 && !$4) {
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

OptionalSelectConditions_EDIT
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
 | GroupByColumnList ',' DerivedColumnOrUnsignedInteger
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
 | '<hive>ASC'
 | 'DESC'
 | '<hive>DESC'
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

AnyLimit
 : 'LIMIT'
 | '<hive>LIMIT'
 ;

OptionalLimitClause
 :
 | AnyLimit 'UNSIGNED_INTEGER'
 ;

OptionalLimitClause_EDIT
 : AnyLimit 'CURSOR'
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
 | 'EXISTS' TableSubQuery
   {
     $$ = { types: [ 'BOOLEAN' ] };
     // clear correlated flag after completed sub-query (set by lexer)
     parser.yy.correlatedSubQuery = false;
   }
 | ValueExpression 'NOT' 'LIKE' ValueExpression
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'LIKE' ValueExpression
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'RLIKE' ValueExpression
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'REGEXP' ValueExpression
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | '(' ValueExpression ')'                                -> $2
 | ValueExpression 'IS' OptionalNot 'NULL'                -> { types: [ 'BOOLEAN' ] }
 | ValueExpression '=' ValueExpression                    -> { types: [ 'BOOLEAN' ] }
 | ValueExpression '<' ValueExpression  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression '>' ValueExpression  -> { types: [ 'BOOLEAN' ] }
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
 : ValueExpression 'NOT' 'IN' '(' TableSubQueryInner ')'  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'NOT' 'IN' '(' InValueList ')'         -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'IN' '(' TableSubQueryInner ')'        -> { types: [ 'BOOLEAN' ] }
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

// CASE
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
 | 'EXISTS' TableSubQuery_EDIT                               -> { types: [ 'BOOLEAN' ] }
 | '(' ValueExpression_EDIT RightParenthesisOrError          -> $2
 | '(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     $$ = { types: ['T'] };
   }
 ;

// UNARY
ValueExpression_EDIT
 : 'NOT' ValueExpression_EDIT                           -> { types: [ 'BOOLEAN' ] }
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

// LIKE, RLIKE, REGEXP
ValueExpression_EDIT
 : ValueExpression_EDIT 'NOT' 'LIKE' ValueExpression         -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'LIKE' ValueExpression               -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'RLIKE' ValueExpression              -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'REGEXP' ValueExpression             -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'NOT' 'LIKE' ValueExpression_EDIT         -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'LIKE' ValueExpression_EDIT               -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'RLIKE' ValueExpression_EDIT              -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'REGEXP' ValueExpression_EDIT             -> { types: [ 'BOOLEAN' ] }
 | 'CURSOR' 'NOT' 'LIKE' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'STRING' ]);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' 'LIKE' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'STRING' ]);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' 'RLIKE' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'STRING' ]);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' 'REGEXP' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'STRING' ]);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'LIKE' PartialBacktickedOrCursor
   {
     suggestFunctions({ types: [ 'STRING' ] });
     suggestColumns({ types: [ 'STRING' ] });
     $$ = { types: ['BOOLEAN'] }
   }
 | ValueExpression 'RLIKE' PartialBacktickedOrCursor
   {
     suggestFunctions({ types: [ 'STRING' ] });
     suggestColumns({ types: [ 'STRING' ] });
     $$ = { types: ['BOOLEAN'] }
   }
 | ValueExpression 'REGEXP' PartialBacktickedOrCursor
   {
     suggestFunctions({ types: [ 'STRING' ] });
     suggestColumns({ types: [ 'STRING' ] });
     $$ = { types: ['BOOLEAN'] }
   }
 ;

// IN
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
 | ValueExpression_EDIT 'NOT' 'IN' '(' TableSubQueryInner RightParenthesisOrError  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'IN' '(' InValueList RightParenthesisOrError               -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'IN' '(' TableSubQueryInner RightParenthesisOrError        -> { types: [ 'BOOLEAN' ] }
 ;

ValueExpressionInSecondPart_EDIT
 : '(' TableSubQueryInner_EDIT RightParenthesisOrError
 | '(' InValueList_EDIT RightParenthesisOrError         -> { inValueEdit: true }
 | '(' AnyCursor RightParenthesisOrError                -> { inValueEdit: true, cursorAtStart: true }
 ;

// BETWEEN
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

// COMPARISON
ValueExpression_EDIT
 : 'CURSOR' '=' ValueExpression
   {
     valueExpressionSuggest($3);
     applyTypeToSuggestions($3.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' '<' ValueExpression
   {
     valueExpressionSuggest($3);
     applyTypeToSuggestions($3.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' '>' ValueExpression
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
 | ValueExpression_EDIT '=' ValueExpression
   {
     applyTypeToSuggestions($3.types);
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression_EDIT '<' ValueExpression
   {
     applyTypeToSuggestions($3.types);
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression_EDIT '>' ValueExpression
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
 | ValueExpression '=' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression '<' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression '>' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'COMPARISON_OPERATOR' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression '=' ValueExpression_EDIT
   {
     applyTypeToSuggestions($1.types);
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression '<' ValueExpression_EDIT
   {
     applyTypeToSuggestions($1.types);
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression '>' ValueExpression_EDIT
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
 ;

// ARITHMETIC
ValueExpression_EDIT
 : 'CURSOR' '*' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'NUMBER' ]);
     $$ = { types: [ 'NUMBER' ] };
   }
 | 'CURSOR' 'ARITHMETIC_OPERATOR' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'NUMBER' ]);
     $$ = { types: [ 'NUMBER' ] };
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
 | ValueExpression '-' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['NUMBER']);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression '*' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['NUMBER']);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'ARITHMETIC_OPERATOR' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['NUMBER']);
     $$ = { types: [ 'NUMBER' ] };
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
 ;

// AND or OR
ValueExpression_EDIT
 : 'CURSOR' 'OR' ValueExpression
   {
     valueExpressionSuggest();
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression_EDIT 'OR' ValueExpression
   {
     addColRefIfExists();
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression 'OR' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest();
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'OR' ValueExpression_EDIT
   {
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | 'CURSOR' 'AND' ValueExpression
   {
     valueExpressionSuggest();
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression_EDIT 'AND' ValueExpression
   {
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression 'AND' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest();
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'AND' ValueExpression_EDIT
   {
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
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
 | ValueExpressionList 'CURSOR' ',' ValueExpressionList
   {
     suggestValueExpressionKeywords($1);
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

NonParenthesizedValueExpressionPrimary
 : UnsignedValueSpecification
 | ColumnReference             -> { types: ['COLREF'], columnReference: $1 }
 | UserDefinedFunction
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
     if ($2) {
       $$ = { valueExpression: $1, alias: $2 };
     } else {
       $$ = { valueExpression: $1 }
     }
   }
 | '*'
   {
     $$ = { asterisk: true }
   }
 ;

SelectSubList_EDIT
 : ValueExpression_EDIT OptionalCorrelationName
 | ValueExpression OptionalCorrelationName_EDIT  -> $2
 ;

SelectList
 : SelectSubList                 -> [ $1 ]
 | SelectList ',' SelectSubList
   {
     $1.push($3);
   }
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
     // TODO: Only if there's no FROM
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
     $$ = { suggestKeywords: ['*'], suggestAggregateFunctions: true };
   }
 ;

DerivedColumn_TWO
 : ColumnIdentifier
   {
     addColumnLocation(@1, [$1]);
   }
 | ColumnIdentifier AnyDot '*'
   {
     addColumnLocation(@1, [$1]);
   }
 | ColumnIdentifier AnyDot DerivedColumnChain
   {
     addColumnLocation(@2, [$1].concat($3));
   }
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

Joins
 : JoinTypes OptionalImpalaBroadcastOrShuffle TablePrimary OptionalJoinCondition
   {
     $4.joinType = $1;
     $$ = $4;
   }
 | Joins JoinTypes OptionalImpalaBroadcastOrShuffle TablePrimary OptionalJoinCondition
   {
     $5.joinType = $1;
     $$ = $5;
   }
 ;

Joins_INVALID
 : JoinTypes OptionalImpalaBroadcastOrShuffle                                           -> { joinType: $1 }
 | JoinTypes OptionalImpalaBroadcastOrShuffle Joins                                     -> { joinType: $1 }
 ;
OptionalImpalaBroadcastOrShuffle
 :
 | '<impala>BROADCAST'
 | '<impala>SHUFFLE'
 ;

Join_EDIT
 : JoinTypes_EDIT OptionalImpalaBroadcastOrShuffle TablePrimary OptionalJoinCondition
 | JoinTypes_EDIT OptionalImpalaBroadcastOrShuffle
 | JoinTypes OptionalImpalaBroadcastOrShuffle TablePrimary_EDIT OptionalJoinCondition
 | JoinTypes OptionalImpalaBroadcastOrShuffle TablePrimary JoinCondition_EDIT
 | JoinTypes OptionalImpalaBroadcastOrShuffle 'CURSOR' OptionalJoinCondition
   {
     if (!$2 && isImpala()) {
       suggestKeywords(['[BROADCAST]', '[SHUFFLE]']);
     }
     suggestTables();
     suggestDatabases({
       appendDot: true
     });
   }
 ;

Joins_EDIT
 : Join_EDIT
 | Join_EDIT Joins
 | Joins Join_EDIT
 | Joins Join_EDIT Joins
 ;

JoinTypes
 : 'JOIN'
 | '<hive>CROSS' 'JOIN'
 | 'INNER' 'JOIN'
 | 'FULL' 'JOIN'
 | 'FULL' 'OUTER' 'JOIN'
 | 'LEFT' 'JOIN'
 | 'LEFT' '<impala>ANTI' 'JOIN'
 | 'LEFT' 'OUTER' 'JOIN'
 | 'LEFT' 'SEMI' 'JOIN'
 | 'RIGHT' 'JOIN'
 | 'RIGHT' '<impala>ANTI' 'JOIN'
 | 'RIGHT' 'OUTER' 'JOIN'
 | 'RIGHT' 'SEMI' 'JOIN'
 ;

JoinTypes_EDIT
 : '<hive>CROSS' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'INNER' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'FULL' 'CURSOR' error
   {
     suggestKeywords(['JOIN', 'OUTER JOIN']);
   }
 | 'FULL' 'OUTER' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'FULL' 'CURSOR' 'JOIN'
   {
     suggestKeywords(['OUTER']);
   }
 | 'LEFT' 'CURSOR' error
   {
     if (isHive()) {
       suggestKeywords(['JOIN', 'OUTER JOIN', 'SEMI JOIN']);
     } else if (isImpala()) {
       suggestKeywords(['ANTI JOIN', 'JOIN', 'OUTER JOIN', 'SEMI JOIN']);
     } else {
       suggestKeywords(['JOIN', 'OUTER JOIN']);
     }
   }
 | 'LEFT' 'SEMI' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'LEFT' 'OUTER' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'LEFT' '<impala>ANTI' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'LEFT' 'CURSOR' 'JOIN'
   {
     if (isImpala()) {
       suggestKeywords(['ANTI', 'OUTER', 'SEMI']);
     } else if (isHive()) {
       suggestKeywords(['OUTER', 'SEMI']);
     } else {
       suggestKeywords(['OUTER']);
     }
   }
 | 'RIGHT' 'CURSOR' error
   {
     if (isImpala()) {
       suggestKeywords(['ANTI JOIN', 'JOIN', 'OUTER JOIN', 'SEMI JOIN']);
     } else {
       suggestKeywords(['JOIN', 'OUTER JOIN']);
     }
   }
 | 'RIGHT' '<impala>ANTI' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'RIGHT' 'OUTER' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'RIGHT' 'SEMI' 'CURSOR'
   {
     suggestKeywords(['JOIN']);
   }
 | 'RIGHT' 'CURSOR' 'JOIN'
   {
     if (isImpala()) {
       suggestKeywords(['ANTI', 'SEMI', 'OUTER']);
     } else {
       suggestKeywords(['OUTER']);
     }
   }
 ;

OptionalJoinCondition
 :                       -> { suggestKeywords: isImpala() ? ['ON', 'USING'] : ['ON'] }
 | 'ON' ValueExpression  -> $2
 | '<impala>USING' '(' UsingColList ')'
 ;

UsingColList
 : RegularOrBacktickedIdentifier
 | UsingColList ',' RegularOrBacktickedIdentifier
 ;

JoinCondition_EDIT
 : 'ON' ValueExpression_EDIT
 | 'ON' 'CURSOR'
   {
     valueExpressionSuggest();
   }
 ;

TablePrimary
 : TableOrQueryName OptionalCorrelationName OptionalLateralViews
   {
     if ($1.identifierChain) {
       if ($2) {
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
      if ($2) {
       $1.alias = $2;
       addTablePrimary({ subQueryAlias: $2 });
     }
   }
 ;

TablePrimary_EDIT
 : TableOrQueryName_EDIT OptionalCorrelationName OptionalLateralViews
 | TableOrQueryName OptionalCorrelationName OptionalLateralViews_EDIT
   {
     if ($2) {
       $1.alias = $2;
     }
     addTablePrimary($1);
   }
 | DerivedTable_EDIT OptionalCorrelationName
   {
     if ($2) {
       // TODO: Potentially add columns for SELECT bla.| FROM (SELECT * FROM foo) AS bla;
       addTablePrimary({ subQueryAlias: $2 });
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
 : TableSubQuery
 ;

DerivedTable_EDIT
 : TableSubQuery_EDIT
 ;

PushQueryState
 :
   {
     if (typeof parser.yy.locationsStack === 'undefined') {
       parser.yy.locationsStack = [];
     }
     if (typeof parser.yy.primariesStack === 'undefined') {
       parser.yy.primariesStack = [];
     }
     if (typeof parser.yy.subQueriesStack === 'undefined') {
       parser.yy.subQueriesStack = [];
     }

     if (typeof parser.yy.resultStack === 'undefined') {
       parser.yy.resultStack = [];
     }
     parser.yy.primariesStack.push(parser.yy.latestTablePrimaries);
     parser.yy.resultStack.push(parser.yy.result);
     parser.yy.locationsStack.push(parser.yy.locations);
     parser.yy.subQueriesStack.push(parser.yy.subQueries);

     parser.yy.result = {};
     parser.yy.locations = [];
     if (parser.yy.correlatedSubQuery) {
       parser.yy.latestTablePrimaries = parser.yy.latestTablePrimaries.concat();
       parser.yy.subQueries = parser.yy.subQueries.concat();
     } else {
       parser.yy.latestTablePrimaries = [];
       parser.yy.subQueries = [];
     }
   }
 ;

PopQueryState
 :
   {
     popQueryState();
   }
 ;

TableSubQuery
 : '(' TableSubQueryInner ')'  -> $2
 | '(' DerivedTable OptionalCorrelationName ')'
   {
     if ($3) {
       $2.alias = $3;
       addTablePrimary({ subQueryAlias: $3 });
     }
     $$ = $2;
   }
 ;

TableSubQuery_EDIT
 : '(' TableSubQueryInner_EDIT RightParenthesisOrError
 | '(' AnyCursor RightParenthesisOrError
   {
     suggestKeywords(['SELECT']);
   }
 ;

TableSubQueryInner
 : PushQueryState SubQuery
   {
     var subQuery = getSubQuery($2);
     subQuery.columns.forEach(function (column) {
       expandIdentifierChain(column);
       delete column.linked;
     });
     popQueryState(subQuery);
     $$ = subQuery;
   }
 ;

TableSubQueryInner_EDIT
 : PushQueryState SubQuery_EDIT PopQueryState
 ;

SubQuery
 : QueryExpression
 ;

SubQuery_EDIT
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
     suggestKeywords(getTypeKeywords());
     $$ = { types: [ 'T' ] };
   }
 | 'CAST(' AnyAs 'CURSOR' RightParenthesisOrError
   {
     suggestKeywords(getTypeKeywords());
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

LateralView
 : '<hive>LATERAL' '<hive>VIEW' UserDefinedFunction RegularIdentifier LateralViewColumnAliases  -> [{ udtf: $3, tableAlias: $4, columnAliases: $5 }]
 | '<hive>LATERAL' '<hive>VIEW' UserDefinedFunction LateralViewColumnAliases                    -> [{ udtf: $3, columnAliases: $4 }]
 | LateralView_INVALID
 ;

LateralView_INVALID
 : '<hive>LATERAL' '<hive>VIEW' UserDefinedFunction RegularIdentifier error                     -> []
 | '<hive>LATERAL' '<hive>VIEW' UserDefinedFunction error                                       -> []
 | '<hive>LATERAL' '<hive>VIEW' error                                                           -> []
 | '<hive>LATERAL' error                                                                  -> []
 ;

LateralView_EDIT
 : '<hive>LATERAL' '<hive>VIEW' UserDefinedFunction_EDIT
 | '<hive>LATERAL' '<hive>VIEW' UserDefinedFunction_EDIT LateralViewColumnAliases
 | '<hive>LATERAL' '<hive>VIEW' UserDefinedFunction RegularIdentifier 'CURSOR'
   {
     suggestKeywords(['AS']);
     $$ = [];
   }
 | '<hive>LATERAL' '<hive>VIEW' UserDefinedFunction 'CURSOR'
   {
     suggestKeywords(['AS']);
     $$ = [];
   }
 | '<hive>LATERAL' '<hive>VIEW' 'CURSOR'
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
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' '(' PartitionSpecList ')'
   {
     addTablePrimary($3);
   }
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' '(' PartitionSpecList ')' '<hive>EXTENDED'
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
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT '<hive>PARTITION' '(' PartitionSpecList ')'
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' '(' PartitionSpecList ')' 'CURSOR'
   {
     addTablePrimary($3);
     suggestKeywords(['EXTENDED']);
   }
 | AnyShow '<hive>LOCKS' RegularOrBackTickedSchemaQualifiedName_EDIT '<hive>PARTITION' '(' PartitionSpecList ')' '<hive>EXTENDED'
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
 | AnyShow '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName '<hive>PARTITION' PartitionSpecList
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
 | AnyShow '<hive>PARTITIONS' RegularOrBackTickedSchemaQualifiedName_EDIT '<hive>PARTITION' PartitionSpecList
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
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'LIKE' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
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
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase_EDIT 'LIKE' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
 | AnyShow '<hive>TABLE' 'CURSOR' OptionalFromDatabase 'LIKE' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
   {
     suggestKeywords(['EXTENDED']);
   }
 | AnyShow '<hive>TABLE' '<hive>EXTENDED' OptionalFromDatabase 'CURSOR' SingleQuotedValue '<hive>PARTITION' PartitionSpecList
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



// ===================================== UPDATE statement =====================================

UpdateStatement
 : 'UPDATE' TargetTable 'SET' SetClauseList OptionalWhereClause
 ;

UpdateStatement_EDIT
 : 'UPDATE' TargetTable_EDIT 'SET' SetClauseList OptionalWhereClause
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
 : ColumnReference
 ;

UpdateSource
 : ValueExpression
 ;

UpdateSource_EDIT
 : ValueExpression_EDIT
 ;


// ===================================== USE Statement =====================================

AnyUse
 : 'USE'
 | '<hive>USE'
 ;

UseStatement
 : AnyUse RegularIdentifier
   {
     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $2;
     }
   }
 ;

UseStatement_EDIT
 : AnyUse 'CURSOR'
   {
     suggestDatabases();
   }
 ;


// ===================================== Fin =====================================
%%

var prepareNewStatement = function () {
  linkTablePrimaries();
  commitLocations();

  delete parser.yy.latestTablePrimaries;
  delete parser.yy.correlatedSubQuery;
  parser.yy.subQueries = [];

  parser.parseError = function (message, error) {
    parser.yy.errors.push(error);
    return message;
  };
};

var popQueryState = function (subQuery) {
  linkTablePrimaries();
  commitLocations();

  if (Object.keys(parser.yy.result).length === 0) {
    parser.yy.result = parser.yy.resultStack.pop();
  } else {
    parser.yy.resultStack.pop();
  }
  var oldSubQueries = parser.yy.subQueries;
  parser.yy.subQueries = parser.yy.subQueriesStack.pop();
  if (subQuery) {
    if (oldSubQueries.length > 0) {
      subQuery.subQueries = oldSubQueries;
    }
    parser.yy.subQueries.push(subQuery);
  }

  parser.yy.latestTablePrimaries = parser.yy.primariesStack.pop();
  parser.yy.locations = parser.yy.locationsStack.pop();
};

var isHive = function () {
  return parser.yy.activeDialect === 'hive';
};

var isImpala = function () {
  return parser.yy.activeDialect === 'impala';
};

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
};

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
};

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
};

var getTypeKeywords = function () {
  if (isHive()) {
    return ['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR'];
  }
  if (isImpala()) {
    return ['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'REAL', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR'];
  }
  return ['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR'];
};

var getColumnDataTypeKeywords = function () {
  if (isHive()) {
    return getTypeKeywords().concat(['ARRAY<>', 'MAP<>', 'STRUCT<>', 'UNIONTYPE<>']);
  }
  return getTypeKeywords();
};

var addColRefIfExists = function (valueExpression) {
  if (valueExpression.columnReference) {
    parser.yy.result.colRef = { identifierChain: valueExpression.columnReference };
  }
};

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
};

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
};

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
};

findReturnTypes = function (funcToken) {
  var funcName = funcToken.substring(0, funcToken.length - 1).toLowerCase();
  return parser.yy.sqlFunctions.getReturnTypes(parser.yy.activeDialect, funcName);
};

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
};

var commitLocations = function () {
  var i = parser.yy.locations.length;
  while (i--) {
    var location = parser.yy.locations[i];
    expandIdentifierChain(location);
    // Impala can have references to previous tables after FROM, i.e. FROM testTable t, t.testArray
    // In this testArray would be marked a type table so we need to switch it to column.
    if (location.type === 'table' && location.table && typeof location.identifierChain !== 'undefined' && location.identifierChain.length > 0) {
      location.type = 'column';
    }
    if (location.type === 'table' && typeof location.table === 'undefined') {
      parser.yy.locations.splice(i, 1);
    }
    if (location.type === 'column' && (typeof location.table === 'undefined' || typeof location.identifierChain === 'undefined')) {
      parser.yy.locations.splice(i, 1);
    }
  }
  if (parser.yy.locations.length > 0) {
    parser.yy.allLocations = parser.yy.allLocations.concat(parser.yy.locations);
    parser.yy.locations = [];
  }
};

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
    delete parser.yy.result.suggestTables;
    delete parser.yy.result.suggestDatabases;
  } else if (typeof parser.yy.result.suggestColumns !== 'undefined') {
    if (typeof parser.yy.result.suggestColumns.table === 'undefined' && typeof parser.yy.result.suggestColumns.subQuery === 'undefined') {
      delete parser.yy.result.suggestColumns;
      delete parser.yy.result.subQueries;
    } else {
      if (typeof parser.yy.result.suggestColumns.subQuery === 'undefined') {
        delete parser.yy.result.subQueries;
      }
      delete parser.yy.result.suggestTables;
      delete parser.yy.result.suggestDatabases;
      if (typeof parser.yy.result.suggestColumns.identifierChain !== 'undefined' && parser.yy.result.suggestColumns.identifierChain.length === 0) {
        delete parser.yy.result.suggestColumns.identifierChain;
      }
    }
    return;
  } else {
    delete parser.yy.result.subQueries;
  }
};

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
  var expandedChain = identifierChain.concat(); // Clone in case it's called multiple times.
  if (typeof expandedChain === 'undefined' || expandedChain.length === 0) {
    return identifierChain;
  }

  var expand = function (identifier, expandedChain) {
    var foundPrimary = tablePrimaries.filter(function (tablePrimary) {
      return tablePrimary.alias === identifier;
    });

    if (foundPrimary.length === 1 && foundPrimary[0].identifierChain) {
      var parentPrimary = tablePrimaries.filter(function (tablePrimary) {
        return tablePrimary.alias === foundPrimary[0].identifierChain[0].name;
      });
      if (parentPrimary.length === 1) {
        var keySet = expandedChain[0].keySet;
        var secondPart = expandedChain.slice(1);
        var firstPart = [];
        // Clone to make sure we don't add keySet to the primaries
        foundPrimary[0].identifierChain.forEach(function (identifier) {
          firstPart.push({ name: identifier.name });
        });
        if (keySet && firstPart.length > 0) {
          firstPart[firstPart.length - 1].keySet = true;
        }

        var result = firstPart.concat(secondPart);
        if (result.length > 0) {
          return expand(firstPart[0].name, result);
        } else {
          return result;
        }
      }
    }
    return expandedChain;
  };
  return expand(expandedChain[0].name, expandedChain);
};

parser.identifyPartials = function (beforeCursor, afterCursor) {
  var beforeMatch = beforeCursor.match(/[0-9a-zA-Z_]*$/);
  var afterMatch = afterCursor.match(/^[0-9a-zA-Z_]*/);
  return { left: beforeMatch ? beforeMatch[0].length : 0, right: afterMatch ? afterMatch[0].length : 0};
};

parser.expandLateralViews = function (tablePrimaries, originalIdentifierChain) {
  var identifierChain = originalIdentifierChain.concat(); // Clone in case it's re-used
  var firstIdentifier = identifierChain[0];
  tablePrimaries.forEach(function (tablePrimary) {
    if (typeof tablePrimary.lateralViews !== 'undefined') {
      tablePrimary.lateralViews.concat().reverse().forEach(function (lateralView) {
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

var expandIdentifierChain = function (wrapper, isColumnSuggestion) {
  if (typeof wrapper.identifierChain === 'undefined' || typeof parser.yy.latestTablePrimaries === 'undefined') {
    return;
  }

  var identifierChain = wrapper.identifierChain.concat();
  var tablePrimaries = parser.yy.latestTablePrimaries;

  if (identifierChain.length > 0 && identifierChain[identifierChain.length - 1].asterisk) {
    var tables = [];
    tablePrimaries.forEach(function (tablePrimary) {
      if (tablePrimary.identifierChain && tablePrimary.identifierChain.length == 1) {
        tables.push({ table: tablePrimary.identifierChain[0].name });
      } else if (tablePrimary.identifierChain && tablePrimary.identifierChain.length == 2) {
        tables.push({ database: tablePrimary.identifierChain[0].name, table: tablePrimary.identifierChain[1].name });
      }
    });
    // Possible Joins
    if (tables.length > 1) {
      wrapper.tables = tables;
      delete wrapper.identifierChain;
      return;
    } else if (tables.length === 1) {
      if (tables[0].database) {
        wrapper.database = tables[0].database;
      }
      wrapper.table = tables[0].table;
      delete wrapper.identifierChain;
      return;
    }
  }

  // Impala can have references to maps or array, i.e. FROM table t, t.map m
  // We need to replace those in the identifierChain
  if (isImpala()) {
    identifierChain = parser.expandImpalaIdentifierChain(tablePrimaries, identifierChain);
    wrapper.identifierChain = identifierChain;
  }
  // Expand exploded views in the identifier chain
  if (isHive() && identifierChain.length > 0) {
    identifierChain = parser.expandLateralViews(tablePrimaries, identifierChain);
    wrapper.identifierChain = identifierChain;
  }

  // IdentifierChain contains a possibly started identifier or empty, example: a.b.c = ['a', 'b', 'c']
  // Reduce the tablePrimaries to the one that matches the first identifier if found
  if (identifierChain.length > 0) {
    var foundTable = tablePrimaries.filter(function (tablePrimary) {
      return identifierChain[0].name === tablePrimary.alias || identifierChain[0].name === tablePrimary.subQueryAlias;
    });

    var dbAndTable = false;
    if (foundTable.length === 0) {
      // Give priority to the ones that match both DB and table
      if (identifierChain.length > 1) {
        foundTable = tablePrimaries.filter(function (tablePrimary) {
          return tablePrimary.identifierChain && tablePrimary.identifierChain.length > 1 &&
              tablePrimary.identifierChain[0].name === identifierChain[0].name &&
              tablePrimary.identifierChain[1].name === identifierChain[1].name;
        });
        dbAndTable = foundTable.length > 0;
      }
      if (foundTable.length == 0) {
        foundTable = tablePrimaries.filter(function (tablePrimary) {
          return tablePrimary.identifierChain && tablePrimary.identifierChain.length > 0 &&
              tablePrimary.identifierChain[0].name === identifierChain[0].name;
        });
      }
    }

    if (foundTable.length === 1) {
      tablePrimaries = foundTable;
      identifierChain.shift();
      if (dbAndTable) {
        identifierChain.shift();
      }
      wrapper.identifierChain = identifierChain;
    }
  }

  if (identifierChain.length == 0) {
    delete wrapper.identifierChain;
  }

  if (tablePrimaries.length === 1) {
    if (typeof tablePrimaries[0].identifierChain !== 'undefined') {
      if (tablePrimaries[0].identifierChain.length == 2) {
        wrapper.database = tablePrimaries[0].identifierChain[0].name;
        wrapper.table = tablePrimaries[0].identifierChain[1].name;
      } else {
        wrapper.table = tablePrimaries[0].identifierChain[0].name;
      }
    } else if (tablePrimaries[0].subQueryAlias !== 'undefined') {
      wrapper.subQuery = tablePrimaries[0].subQueryAlias;
    }
  }
  wrapper.linked = true;
};

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
    } else if (typeof tablePrimary.subQueryAlias !== 'undefined') {
      parser.yy.result.suggestIdentifiers.push({ name: tablePrimary.subQueryAlias + '.', type: 'sub-query' });
    }
  });
  if (parser.yy.result.suggestIdentifiers.length === 0) {
    delete parser.yy.result.suggestIdentifiers;
  }
};

var suggestLateralViewAliasesAsIdentifiers = function () {
  if (typeof parser.yy.result.suggestIdentifiers === 'undefined') {
    parser.yy.result.suggestIdentifiers = [];
  }
  parser.yy.latestTablePrimaries.forEach(function (tablePrimary) {
    if (typeof tablePrimary.lateralViews !== 'undefined') {
      tablePrimary.lateralViews.forEach(function (lateralView) {
        if (typeof lateralView.tableAlias !== 'undefined') {
          parser.yy.result.suggestIdentifiers.push({ name: lateralView.tableAlias + '.', type: 'alias' });
        }
        lateralView.columnAliases.forEach(function (columnAlias) {
          parser.yy.result.suggestIdentifiers.push({ name: columnAlias, type: 'alias' });
        });
      });
    }
  });
  if (parser.yy.result.suggestIdentifiers.length === 0) {
    delete parser.yy.result.suggestIdentifiers;
  }
};

var linkTablePrimaries = function () {
  if (!parser.yy.cursorFound || typeof parser.yy.latestTablePrimaries === 'undefined') {
    return;
  }
  if (typeof parser.yy.result.suggestColumns !== 'undefined' && !parser.yy.result.suggestColumns.linked) {
    if (parser.yy.subQueries.length > 0) {
      parser.yy.result.subQueries = parser.yy.subQueries;
    }
    if (typeof parser.yy.result.suggestColumns.identifierChain === 'undefined' || parser.yy.result.suggestColumns.identifierChain.length === 0) {
      if (parser.yy.latestTablePrimaries.length > 1) {
        suggestTablePrimariesAsIdentifiers();
        delete parser.yy.result.suggestColumns;
      } else {
        suggestLateralViewAliasesAsIdentifiers();
        if (parser.yy.latestTablePrimaries.length == 1 && (parser.yy.latestTablePrimaries[0].alias || parser.yy.latestTablePrimaries[0].subQueryAlias)) {
          suggestTablePrimariesAsIdentifiers();
        }
        expandIdentifierChain(parser.yy.result.suggestColumns);
      }
    } else {
      expandIdentifierChain(parser.yy.result.suggestColumns);
    }
  }
  if (typeof parser.yy.result.colRef !== 'undefined' && !parser.yy.result.colRef.linked) {
    expandIdentifierChain(parser.yy.result.colRef);
  }
  if (typeof parser.yy.result.suggestKeyValues !== 'undefined' && !parser.yy.result.suggestKeyValues.linked) {
    expandIdentifierChain(parser.yy.result.suggestKeyValues);
  }
};

var getSubQuery = function (cols) {
  var columns = [];
  cols.selectList.forEach(function (col) {
    var result = {}
    if (col.alias) {
      result.alias = col.alias;
    }
    if (col.valueExpression && col.valueExpression.columnReference) {
      result.identifierChain = col.valueExpression.columnReference
    } else if (col.asterisk) {
      result.identifierChain = [{ asterisk: true }];
    }
    if (col.valueExpression && col.valueExpression.types && col.valueExpression.types.length === 1) {
      result.type = col.valueExpression.types[0];
    }

    columns.push(result);
  });

  return {
    columns: columns
  };
};

var addTablePrimary = function (ref) {
  if (typeof parser.yy.latestTablePrimaries === 'undefined') {
    parser.yy.latestTablePrimaries = [];
  }
  parser.yy.latestTablePrimaries.push(ref);
};

var suggestNumbers = function (numbers) {
  parser.yy.result.suggestNumbers = numbers;
};

var suggestDdlAndDmlKeywords = function () {
  var keywords = ['ALTER', 'CREATE', 'DELETE', 'DESCRIBE', 'DROP', 'EXPLAIN', 'INSERT', 'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE'];

  if (isHive()) {
    keywords = keywords.concat(['ANALYZE', 'EXPORT', 'IMPORT', 'LOAD', 'MSCK']);
  }

  if (isImpala()) {
    keywords = keywords.concat(['COMPUTE', 'INVALIDATE', 'LOAD', 'REFRESH']);
  }

  suggestKeywords(keywords);
};

var checkForSelectListKeywords = function (selectList) {
  if (selectList.length === 0) {
    return;
  }
  var last = selectList[selectList.length - 1];
  if (!last || !last.valueExpression) {
    return;
  }
  var valueExpressionKeywords = getValueExpressionKeywords(last.valueExpression);
  var keywords = [];
  if (valueExpressionKeywords.suggestKeywords) {
    keywords = keywords.concat(valueExpressionKeywords.suggestKeywords);
  }
  if (valueExpressionKeywords.suggestColRefKeywords) {
    suggestColRefKeywords(valueExpressionKeywords.suggestColRefKeywords)
    addColRefIfExists(last.valueExpression);
  }
  if (!last.alias) {
    keywords.push('AS');
  }
  if (keywords.length > 0) {
    suggestKeywords(keywords);
  }
};

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
};

var suggestKeywords = function (keywords) {
  parser.yy.result.suggestKeywords = keywords.sort();
};

var suggestColRefKeywords = function (colRefKeywords) {
  parser.yy.result.suggestColRefKeywords = colRefKeywords;
};

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
};

var suggestFunctions = function (details) {
  parser.yy.result.suggestFunctions = details || {};
};

var suggestAggregateFunctions = function () {
  parser.yy.result.suggestAggregateFunctions = true;
};

var suggestColumns = function (details) {
  if (typeof details === 'undefined') {
    details = { identifierChain: [] };
  } else if (typeof details.identifierChain === 'undefined') {
    details.identifierChain = [];
  }
  parser.yy.result.suggestColumns = details;
};

var suggestKeyValues = function (details) {
  parser.yy.result.suggestKeyValues = details || {};
};

var suggestTables = function (details) {
  parser.yy.result.suggestTables = details || {};
};

var adjustLocationForCursor = function (location) {
   // columns are 0-based and lines not, so add 1 to cols
   var newLocation = {
     first_line: location.first_line,
     last_line: location.last_line,
     first_column: location.first_column + 1,
     last_column: location.last_column + 1
   };
   if (parser.yy.cursorFound) {
     if (parser.yy.cursorFound.first_line === newLocation.first_line && parser.yy.cursorFound.last_column <= newLocation.first_column) {
       var additionalSpace = parser.yy.partialLengths.left + parser.yy.partialLengths.right;
       additionalSpace -= parser.yy.partialCursor ? 1 : 3; // For some reason the normal cursor eats 3 positions.
       newLocation.first_column = newLocation.first_column + additionalSpace;
       newLocation.last_column = newLocation.last_column + additionalSpace;
     }
   }
   return newLocation;
};

var addFunctionLocation = function (location, functionName) {
  // Remove trailing '(' from location
  var adjustedLocation = {
    first_line: location.first_line,
    last_line: location.last_line,
    first_column: location.first_column,
    last_column: location.last_column - 1
  }
  parser.yy.locations.push({ type: 'function', location: adjustLocationForCursor(adjustedLocation), function: functionName.toLowerCase() });
};

var addDatabaseLocation = function (location, database) {
  parser.yy.locations.push({ type: 'database', location: adjustLocationForCursor(location), database: database });
};

var addTableLocation = function (location, identifierChain) {
  parser.yy.locations.push({ type: 'table', location: adjustLocationForCursor(location), identifierChain: identifierChain });
};

var addColumnLocation = function (location, identifierChain) {
  parser.yy.locations.push({ type: 'column', location: adjustLocationForCursor(location), identifierChain: identifierChain });
};

var suggestDatabases = function (details) {
  parser.yy.result.suggestDatabases = details || {};
};

var suggestHdfs = function (details) {
  parser.yy.result.suggestHdfs = details || {};
};

var suggestValues = function (details) {
  parser.yy.result.suggestValues = true;
};

var determineCase = function (text) {
  parser.yy.lowerCase = text.toLowerCase() === text;
};

var lexerModified = false;

/**
 * Main parser function
 */
parser.parseSql = function(beforeCursor, afterCursor, dialect, sqlFunctions, debug) {
  parser.yy.sqlFunctions = sqlFunctions;
  parser.yy.result = { locations: [] };
  parser.yy.lowerCase = false;
  parser.yy.locations = [];
  parser.yy.allLocations = [];
  parser.yy.subQueries = [];
  parser.yy.errors = [];

  delete parser.yy.cursorFound;
  delete parser.yy.partialCursor;

  prepareNewStatement();

  parser.yy.partialLengths = parser.identifyPartials(beforeCursor, afterCursor);

  if (parser.yy.partialLengths.left > 0) {
    beforeCursor = beforeCursor.substring(0, beforeCursor.length - parser.yy.partialLengths.left);
  }

  if (parser.yy.partialLengths.right > 0) {
    afterCursor = afterCursor.substring(parser.yy.partialLengths.right);
  }

  parser.yy.activeDialect = (dialect !== 'hive' && dialect !== 'impala') ? undefined : dialect;

  // Hack to set the inital state of the lexer without first having to hit a token
  // has to be done as the first token found can be dependant on dialect
  if (!lexerModified) {
    var originalSetInput = parser.lexer.setInput;
    parser.lexer.setInput = function (input, yy) {
      var lexer = originalSetInput.bind(parser.lexer)(input, yy);
      if (typeof parser.yy.activeDialect !== 'undefined') {
        lexer.begin(parser.yy.activeDialect);
      }
      return lexer;
    }
    lexerModified = true;
  }

  var result;
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
    result = parser.yy.result;
  }
  if (parser.yy.errors.length > 0) {
    parser.yy.result.errors = parser.yy.errors;
    if (debug) {
      console.log(parser.yy.errors);
    }
  }
  linkTablePrimaries();
  commitLocations();

  // Clean up and prioritize
  parser.yy.allLocations.sort(function (a, b) {
    if (a.location.first_line !== b.location.first_line) {
      return a.location.first_line - b.location.first_line;
    }
    return a.location.first_column - b.location.first_column;
  });
  parser.yy.result.locations = parser.yy.allLocations;

  parser.yy.result.locations.forEach(function (location) {
    delete location.linked;
  })
  if (typeof parser.yy.result.suggestColumns !== 'undefined') {
    delete parser.yy.result.suggestColumns.linked;
  }
  if (typeof parser.yy.result.colRef !== 'undefined') {
    delete parser.yy.result.colRef.linked;
  }
  if (typeof parser.yy.result.suggestKeyValues !== 'undefined') {
    delete parser.yy.result.suggestKeyValues.linked;
  }

  prioritizeSuggestions();

  if (typeof result.error !== 'undefined' && typeof result.error.expected !== 'undefined') {
    // Remove any expected tokens from other dialects, jison doesn't remove tokens from other lexer states.
    var actualExpected = {};
    result.error.expected.forEach(function (expected) {
      var match = expected.match(/\<([a-z]+)\>(.*)/);
      if (match !== null) {
        if (typeof parser.yy.activeDialect !== 'undefined' && parser.yy.activeDialect === match[1]) {
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
};