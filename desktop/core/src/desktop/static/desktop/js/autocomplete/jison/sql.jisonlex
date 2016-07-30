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
<hive>'WINDOW'                             { return '<hive>WINDOW'; }

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
'CURRENT'                                  { return 'CURRENT'; }
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
'FOLLOWING'                                { return 'FOLLOWING'; }
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
'PARTITION'                                { return 'PARTITION'; }
'PRECEDING'                                { return 'PRECEDING'; }
'RANGE'                                    { return 'RANGE'; }
'REGEXP'                                   { return 'REGEXP'; }
'RIGHT'                                    { return 'RIGHT'; }
'RLIKE'                                    { return 'RLIKE'; }
'ROW'                                      { return 'ROW'; }
'ROWS'                                     { return 'ROWS'; }
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
'UNBOUNDED'                                { return 'UNBOUNDED'; }
'UPDATE'                                   { determineCase(yytext); return 'UPDATE'; }
'USE'                                      { determineCase(yytext); return 'USE'; }
'VARCHAR'                                  { return 'VARCHAR'; } // Not in Impala
'WHEN'                                     { return 'WHEN'; }
'WHERE'                                    { return 'WHERE'; }
'WITH'                                     { return 'WITH'; }

// Non-reserved Keywords
'OVER'                                     { return 'OVER'; }
'ROLE'                                     { return 'ROLE'; }

// --- UDFs ---
'AVG('                                     { addFunctionLocation(yylloc, 'avg'); return 'AVG('; }
'CAST('                                    { addFunctionLocation(yylloc, 'cast'); return 'CAST('; }
'COUNT('                                   { addFunctionLocation(yylloc, 'count'); return 'COUNT('; }
'MAX('                                     { addFunctionLocation(yylloc, 'max'); return 'MAX('; }
'MIN('                                     { addFunctionLocation(yylloc, 'min'); return 'MIN('; }
'STDDEV_POP('                              { addFunctionLocation(yylloc, 'stddev_pop'); return 'STDDEV_POP('; }
'STDDEV_SAMP('                             { addFunctionLocation(yylloc, 'stddev_samp'); return 'STDDEV_SAMP('; }
'SUM('                                     { addFunctionLocation(yylloc, 'sum'); return 'SUM('; }
'VARIANCE('                                { addFunctionLocation(yylloc, 'variance'); return 'VARIANCE('; }
'VAR_POP('                                 { addFunctionLocation(yylloc, 'var_pop'); return 'VAR_POP('; }
'VAR_SAMP('                                { addFunctionLocation(yylloc, 'var_samp'); return 'VAR_SAMP('; }
<hive>'COLLECT_SET('                       { addFunctionLocation(yylloc, 'collect_set'); return '<hive>COLLECT_SET('; }
<hive>'COLLECT_LIST('                      { addFunctionLocation(yylloc, 'collect_list'); return '<hive>COLLECT_LIST('; }
<hive>'CORR('                              { addFunctionLocation(yylloc, 'corr'); return '<hive>CORR('; }
<hive>'COVAR_POP('                         { addFunctionLocation(yylloc, 'covar_pop'); return '<hive>COVAR_POP('; }
<hive>'COVAR_SAMP('                        { addFunctionLocation(yylloc, 'covar_samp'); return '<hive>COVAR_SAMP('; }
<hive>'HISTOGRAM_NUMERIC('                 { addFunctionLocation(yylloc, 'histogram_numeric'); return '<hive>HISTOGRAM_NUMERIC('; }
<hive>'NTILE('                             { addFunctionLocation(yylloc, 'ntile'); return '<hive>NTILE('; }
<hive>'PERCENTILE('                        { addFunctionLocation(yylloc, 'percentile'); return '<hive>PERCENTILE('; }
<hive>'PERCENTILE_APPROX('                 { addFunctionLocation(yylloc, 'percentile_approx'); return '<hive>PERCENTILE_APPROX('; }
<impala>'APPX_MEDIAN('                     { addFunctionLocation(yylloc, 'appx_median'); return '<impala>APPX_MEDIAN('; }
<impala>'EXTRACT('                         { addFunctionLocation(yylloc, 'extract'); return '<impala>EXTRACT('; }
<impala>'GROUP_CONCAT('                    { addFunctionLocation(yylloc, 'group_concat'); return '<impala>GROUP_CONCAT('; }
<impala>'STDDEV('                          { addFunctionLocation(yylloc, 'stddev'); return '<impala>STDDEV('; }
<impala>'VARIANCE_POP('                    { addFunctionLocation(yylloc, 'variance_pop'); return '<impala>VARIANCE_POP('; }
<impala>'VARIANCE_SAMP('                   { addFunctionLocation(yylloc, 'variance_samp'); return '<impala>VARIANCE_SAMP('; }

// Analytical functions
'DENSE_RANK('                              { addFunctionLocation(yylloc, 'variance_samp'); return 'ANALYTIC('; }
'FIRST_VALUE('                             { addFunctionLocation(yylloc, 'variance_samp'); return 'ANALYTIC('; }
'LAG('                                     { addFunctionLocation(yylloc, 'variance_samp'); return 'ANALYTIC('; }
'LAST_VALUE('                              { addFunctionLocation(yylloc, 'variance_samp'); return 'ANALYTIC('; }
'LEAD('                                    { addFunctionLocation(yylloc, 'variance_samp'); return 'ANALYTIC('; }
'RANK('                                    { addFunctionLocation(yylloc, 'variance_samp'); return 'ANALYTIC('; }
'ROW_NUMBER('                              { addFunctionLocation(yylloc, 'variance_samp'); return 'ANALYTIC('; }
<hive>'CUME_DIST('                         { addFunctionLocation(yylloc, 'variance_samp'); return 'ANALYTIC('; }
<hive>'PERCENT_RANK('                      { addFunctionLocation(yylloc, 'variance_samp'); return 'ANALYTIC('; }

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
