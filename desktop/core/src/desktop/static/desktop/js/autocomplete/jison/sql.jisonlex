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

\s                                         { /* skip whitespace */ }
'--'.*                                     { /* skip comments */ }
[/][*][^*]*[*]+([^/*][^*]*[*]+)*[/]        { /* skip comments */ }

'\u2020'                                   { parser.yy.partialCursor = false; parser.yy.cursorFound = yylloc; return 'CURSOR'; }
'\u2021'                                   { parser.yy.partialCursor = true; parser.yy.cursorFound = yylloc; return 'PARTIAL_CURSOR'; }

// Reserved Keywords
<hive>'ALL'                                { return '<hive>ALL'; }
<hive>'ARRAY'                              { return '<hive>ARRAY'; }
<hive>'AS'                                 { return '<hive>AS'; }
<hive>'AUTHORIZATION'                      { return '<hive>AUTHORIZATION'; }
<hive>'BINARY'                             { return '<hive>BINARY'; }
<hive>'COLUMN'                             { return '<hive>COLUMN'; }
<hive>'CONF'                               { return '<hive>CONF'; }
<hive>'CREATE'                             { parser.determineCase(yytext); return '<hive>CREATE'; }
<hive>'CROSS'                              { return '<hive>CROSS'; }
<hive>'CUBE'                               { return '<hive>CUBE'; }
<hive>'CURRENT'                            { return '<hive>CURRENT'; }
<hive>'DATE'                               { return '<hive>DATE'; }
<hive>'DELETE'                             { parser.determineCase(yytext); return '<hive>DELETE'; }
<hive>'DESCRIBE'                           { parser.determineCase(yytext); return '<hive>DESCRIBE'; }
<hive>'EXTENDED'                           { return '<hive>EXTENDED'; }
<hive>'EXTERNAL'                           { return '<hive>EXTERNAL'; }
<hive>'FOR'                                { return '<hive>FOR'; }
<hive>'FUNCTION'                           { return '<hive>FUNCTION'; }
<hive>'GRANT'                              { return '<hive>GRANT'; }
<hive>'GROUPING'                           { return '<hive>GROUPING'; }
<hive>'IMPORT'                             { parser.determineCase(yytext); return '<hive>IMPORT'; }
<hive>'INSERT'                             { parser.determineCase(yytext); return '<hive>INSERT'; }
<hive>'LATERAL'                            { return '<hive>LATERAL'; }
<hive>'LOCAL'                              { return '<hive>LOCAL'; }
<hive>'MACRO'                              { return '<hive>MACRO'; }
<hive>'MAP'                                { return '<hive>MAP'; }
<hive>'NONE'                               { return '<hive>NONE'; }
<hive>'OF'                                 { return '<hive>OF'; }
<hive>'OUT'                                { return '<hive>OUT'; }
<hive>'REVOKE'                             { return '<hive>REVOKE'; }
<hive>'ROLLUP'                             { return '<hive>ROLLUP'; }
<hive>'TABLE'                              { return '<hive>TABLE'; }
<hive>'USER'                               { return '<hive>USER'; }
<hive>'USING'                              { return '<hive>USING'; }

// Non-reserved Keywords
<hive>'ADD'                                { return '<hive>ADD'; }
<hive>'ADMIN'                              { return '<hive>ADMIN'; }
<hive>'AFTER'                              { return '<hive>AFTER'; }
<hive>'ANALYZE'                            { parser.determineCase(yytext); return '<hive>ANALYZE'; }
<hive>'ARCHIVE'                            { return '<hive>ARCHIVE'; }
<hive>'ASC'                                { return '<hive>ASC'; }
<hive>'AVRO'                               { return '<hive>AVRO'; }
<hive>'BUCKET'                             { return '<hive>BUCKET'; }
<hive>'BUCKETS'                            { return '<hive>BUCKETS'; }
<hive>'CACHE'                              { return '<hive>CACHE'; }
<hive>'CASCADE'                            { return '<hive>CASCADE'; }
<hive>'CHANGE'                             { return '<hive>CHANGE'; }
<hive>'CLUSTER'                            { return '<hive>CLUSTER'; }
<hive>'CLUSTERED'                          { return '<hive>CLUSTERED'; }
<hive>'COLLECTION'                         { return '<hive>COLLECTION'; }
<hive>'COLUMNS'                            { return '<hive>COLUMNS'; }
<hive>'COMMENT'                            { return '<hive>COMMENT'; }
<hive>'COMPACT'                            { return '<hive>COMPACT'; }
<hive>'COMPACTIONS'                        { return '<hive>COMPACTIONS'; }
<hive>'COMPUTE'                            { return '<hive>COMPUTE'; }
<hive>'CONCATENATE'                        { return '<hive>CONCATENATE'; }
<hive>'DATA'                               { return '<hive>DATA'; }
<hive>'DATABASES'                          { return '<hive>DATABASES'; }
<hive>'DEFERRED'                           { return '<hive>DEFERRED'; }
<hive>'DEFINED'                            { return '<hive>DEFINED'; }
<hive>'DELIMITED'                          { return '<hive>DELIMITED'; }
<hive>'DEPENDENCY'                         { return '<hive>DEPENDENCY'; }
<hive>'DESC'                               { return '<hive>DESC'; }
<hive>'DIRECTORY'                          { this.begin('hdfs'); return '<hive>DIRECTORY'; }
<hive>'DISABLE'                            { return '<hive>DISABLE'; }
<hive>'DISTRIBUTE'                         { return '<hive>DISTRIBUTE'; }
<hive>'ESCAPED'                            { return '<hive>ESCAPED'; }
<hive>'ENABLE'                             { return '<hive>ENABLE'; }
<hive>'EXCHANGE'                           { return '<hive>EXCHANGE'; }
<hive>'EXPLAIN'                            { parser.determineCase(yytext); return '<hive>EXPLAIN'; }
<hive>'EXPORT'                             { parser.determineCase(yytext); return '<hive>EXPORT'; }
<hive>'FIELDS'                             { return '<hive>FIELDS'; }
<hive>'FILE'                               { return '<hive>FILE'; }
<hive>'FILEFORMAT'                         { return '<hive>FILEFORMAT'; }
<hive>'FIRST'                              { return '<hive>FIRST'; }
<hive>'FORMAT'                             { return '<hive>FORMAT'; }
<hive>'FORMATTED'                          { return '<hive>FORMATTED'; }
<hive>'FUNCTION'                           { return '<hive>FUNCTION'; }
<hive>'FUNCTIONS'                          { return '<hive>FUNCTIONS'; }
<hive>'IDXPROPERTIES'                      { return '<hive>IDXPROPERTIES'; }
<hive>'INDEX'                              { return '<hive>INDEX'; }
<hive>'INDEXES'                            { return '<hive>INDEXES'; }
<hive>'INPATH'                             { this.begin('hdfs'); return '<hive>INPATH'; }
<hive>'INPUTFORMAT'                        { return '<hive>INPUTFORMAT'; }
<hive>'ITEMS'                              { return '<hive>ITEMS'; }
<hive>'JAR'                                { return '<hive>JAR'; }
<hive>'KEYS'                               { return '<hive>KEYS'; }
<hive>'LINES'                              { return '<hive>LINES'; }
<hive>'LOAD'                               { parser.determineCase(yytext); return '<hive>LOAD'; }
<hive>'LOCATION'                           { this.begin('hdfs'); return '<hive>LOCATION'; }
<hive>'LOCK'                               { return '<hive>LOCK'; }
<hive>'LOCKS'                              { return '<hive>LOCKS'; }
<hive>'METADATA'                           { return '<hive>METADATA'; }
<hive>'MSCK'                               { return '<hive>MSCK'; }
<hive>'NOSCAN'                             { return '<hive>NOSCAN'; }
<hive>'NO_DROP'                            { return '<hive>NO_DROP'; }
<hive>'OFFLINE'                            { return '<hive>OFFLINE'; }
<hive>'ORC'                                { return '<hive>ORC'; }
<hive>'OUTPUTFORMAT'                       { return '<hive>OUTPUTFORMAT'; }
<hive>'OVERWRITE'                          { return '<hive>OVERWRITE'; }
<hive>OVERWRITE\s+DIRECTORY                { this.begin('hdfs'); return '<hive>OVERWRITE_DIRECTORY'; }
<hive>'PARQUET'                            { return '<hive>PARQUET'; }
<hive>'PARTITIONED'                        { return '<hive>PARTITIONED'; }
<hive>'PARTITIONS'                         { return '<hive>PARTITIONS'; }
<hive>'PRIVILEGES'                         { return '<hive>PRIVILEGES'; }
<hive>'PURGE'                              { return '<hive>PURGE'; }
<hive>'RCFILE'                             { return '<hive>RCFILE'; }
<hive>'REBUILD'                            { return '<hive>REBUILD'; }
<hive>'RELOAD'                             { parser.determineCase(yytext); return '<hive>RELOAD'; }
<hive>'REPAIR'                             { return '<hive>REPAIR'; }
<hive>'REPLICATION'                        { return '<hive>REPLICATION'; }
<hive>'RECOVER'                            { return '<hive>RECOVER'; }
<hive>'RENAME'                             { return '<hive>RENAME'; }
<hive>'REPLACE'                            { return '<hive>REPLACE'; }
<hive>'RESTRICT'                           { return '<hive>RESTRICT'; }
<hive>'ROLE'                               { return '<hive>ROLE'; }
<hive>'ROLES'                              { return '<hive>ROLES'; }
<hive>'SCHEMA'                             { return '<hive>SCHEMA'; }
<hive>'SCHEMAS'                            { return '<hive>SCHEMAS'; }
<hive>'SEQUENCEFILE'                       { return '<hive>SEQUENCEFILE'; }
<hive>'SERDE'                              { return '<hive>SERDE'; }
<hive>'SERDEPROPERTIES'                    { return '<hive>SERDEPROPERTIES'; }
<hive>'SETS'                               { return '<hive>SETS'; }
<hive>'SHOW'                               { parser.determineCase(yytext); return '<hive>SHOW'; }
<hive>'SHOW_DATABASE'                      { return '<hive>SHOW_DATABASE'; }
<hive>'SKEWED'                             { return '<hive>SKEWED'; }
<hive>'SKEWED LOCATION'                    { return '<hive>SKEWED_LOCATION'; } // Hack to prevent hdfs lexer state
<hive>'SORT'                               { return '<hive>SORT'; }
<hive>'SORTED'                             { return '<hive>SORTED'; }
<hive>'STATISTICS'                         { return '<hive>STATISTICS'; }
<hive>'STORED'                             { return '<hive>STORED'; }
<hive>STORED\s+AS\s+DIRECTORIES            { return '<hive>STORED_AS_DIRECTORIES'; }
<hive>'STRING'                             { return '<hive>STRING'; }
<hive>'STRUCT'                             { return '<hive>STRUCT'; }
<hive>'TABLES'                             { return '<hive>TABLES'; }
<hive>'TABLESAMPLE'                        { return '<hive>TABLESAMPLE'; }
<hive>'TBLPROPERTIES'                      { return '<hive>TBLPROPERTIES'; }
<hive>'TEMPORARY'                          { return '<hive>TEMPORARY'; }
<hive>'TERMINATED'                         { return '<hive>TERMINATED'; }
<hive>'TEXTFILE'                           { return '<hive>TEXTFILE'; }
<hive>'TINYINT'                            { return '<hive>TINYINT'; }
<hive>'TOUCH'                              { return '<hive>TOUCH'; }
<hive>'TRANSACTIONS'                       { return '<hive>TRANSACTIONS'; }
<hive>'UNARCHIVE'                          { return '<hive>UNARCHIVE'; }
<hive>'UNIONTYPE'                          { return '<hive>UNIONTYPE'; }
<hive>'USE'                                { parser.determineCase(yytext); return '<hive>USE'; }
<hive>'VIEW'                               { return '<hive>VIEW'; }
<hive>'WINDOW'                             { return '<hive>WINDOW'; }

<hive>'.'                                  { return '<hive>.'; }
<hive>'['                                  { return '<hive>['; }
<hive>']'                                  { return '<hive>]'; }

// Reserved Keywords
<impala>'ADD'                              { return '<impala>ADD'; }
<impala>'AGGREGATE'                        { return '<impala>AGGREGATE'; }
<impala>'AVRO'                             { return '<impala>AVRO'; }
<impala>'CACHED'                           { return '<impala>CACHED'; }
<impala>'CHANGE'                           { return '<impala>CHANGE'; }
<impala>'CLOSE_FN'                         { return '<impala>CLOSE_FN'; }
<impala>'COLUMN'                           { return '<impala>COLUMN'; }
<impala>'COLUMNS'                          { return '<impala>COLUMNS'; }
<impala>'COMMENT'                          { return '<impala>COMMENT'; }
<impala>'COMPUTE'                          { parser.determineCase(yytext); return '<impala>COMPUTE'; }
<impala>'CREATE'                           { parser.determineCase(yytext); return '<impala>CREATE'; }
<impala>'DATA'                             { return '<impala>DATA'; }
<impala>'DATABASES'                        { return '<impala>DATABASES'; }
<impala>'DELIMITED'                        { return '<impala>DELIMITED'; }
<impala>'DESCRIBE'                         { parser.determineCase(yytext); return '<impala>DESCRIBE'; }
<impala>'ESCAPED'                          { return '<impala>ESCAPED'; }
<impala>'EXPLAIN'                          { parser.determineCase(yytext); return '<impala>EXPLAIN'; }
<impala>'EXTERNAL'                         { return '<impala>EXTERNAL'; }
<impala>'EXTENDED'                         { return '<impala>EXTENDED'; }
<impala>'FIELDS'                           { return '<impala>FIELDS'; }
<impala>'FILEFORMAT'                       { return '<impala>FILEFORMAT'; }
<impala>'FINALIZE_FN'                      { return '<impala>FINALIZE_FN'; }
<impala>'FIRST'                            { return '<impala>FIRST'; }
<impala>'FORMAT'                           { return '<impala>FORMAT'; }
<impala>'FORMATTED'                        { return '<impala>FORMATTED'; }
<impala>'FUNCTION'                         { return '<impala>FUNCTION'; }
<impala>'FUNCTIONS'                        { return '<impala>FUNCTIONS'; }
<impala>'GROUP'                            { return '<impala>GROUP'; }
<impala>'HASH'                             { return '<impala>HASH'; }
<impala>'INCREMENTAL'                      { return '<impala>INCREMENTAL'; }
<impala>'INSERT'                           { parser.determineCase(yytext); return '<impala>INSERT'; }
<impala>'INTERVAL'                         { return '<impala>INTERVAL'; }
<impala>'INIT_FN'                          { return '<impala>INIT_FN'; }
<impala>'INVALIDATE'                       { parser.determineCase(yytext); return '<impala>INVALIDATE'; }
<impala>'INPATH'                           { this.begin('hdfs'); return '<impala>INPATH'; }
<impala>'KEY'                              { return '<impala>KEY'; }
<impala>'KUDU'                             { return '<impala>KUDU'; }
<impala>'LAST'                             { return '<impala>LAST'; }
<impala>LIKE\s+PARQUET                     { this.begin('hdfs'); return '<impala>LIKE_PARQUET'; }
<impala>'LIMIT'                            { return '<impala>LIMIT'; }
<impala>'LINES'                            { return '<impala>LINES'; }
<impala>'LOAD'                             { parser.determineCase(yytext); return '<impala>LOAD'; }
<impala>'LOCATION'                         { this.begin('hdfs'); return '<impala>LOCATION'; }
<impala>'MERGE_FN'                         { return '<impala>MERGE_FN'; }
<impala>'METADATA'                         { return '<impala>METADATA'; }
<impala>'NULLS'                            { return '<impala>NULLS'; }
<impala>'OFFSET'                           { return '<impala>OFFSET'; }
<impala>'OVERWRITE'                        { return '<impala>OVERWRITE'; }
<impala>'PARQUET'                          { return '<impala>PARQUET'; }
<impala>'PARTITIONED'                      { return '<impala>PARTITIONED'; }
<impala>'PARTITIONS'                       { return '<impala>PARTITIONS'; }
<impala>'PREPARE_FN'                       { return '<impala>PREPARE_FN'; }
<impala>'PRIMARY'                          { return '<impala>PRIMARY'; }
<impala>'RCFILE'                           { return '<impala>RCFILE'; }
<impala>'REAL'                             { return '<impala>REAL'; }
<impala>'REFRESH'                          { parser.determineCase(yytext); return '<impala>REFRESH'; }
<impala>'RENAME'                           { return '<impala>RENAME'; }
<impala>'REPLACE'                          { return '<impala>REPLACE'; }
<impala>'RETURNS'                          { return '<impala>RETURNS'; }
<impala>'REVOKE'                           { return '<impala>REVOKE'; }
<impala>'SEQUENCEFILE'                     { return '<impala>SEQUENCEFILE'; }
<impala>'SERDEPROPERTIES'                  { return '<impala>SERDEPROPERTIES'; }
<impala>'SCHEMAS'                          { return '<impala>SCHEMAS'; }
<impala>'SERIALIZE_FN'                     { return '<impala>SERIALIZE_FN'; }
<impala>'SERVER'                           { return '<impala>SERVER'; }
<impala>'STATS'                            { return '<impala>STATS'; }
<impala>'STORED'                           { return '<impala>STORED'; }
<impala>'STRAIGHT_JOIN'                    { return '<impala>STRAIGHT_JOIN'; }
<impala>'SYMBOL'                           { return '<impala>SYMBOL'; }
<impala>'TABLE'                            { return '<impala>TABLE'; }
<impala>'TABLES'                           { return '<impala>TABLES'; }
<impala>'TBLPROPERTIES'                    { return '<impala>TBLPROPERTIES'; }
<impala>'TERMINATED'                       { return '<impala>TERMINATED'; }
<impala>'TEXTFILE'                         { return '<impala>TEXTFILE'; }
<impala>'UNCACHED'                         { return '<impala>UNCACHED'; }
<impala>'UPDATE_FN'                        { return '<impala>UPDATE_FN'; }
<impala>'URI'                              { return '<impala>URI'; }
<impala>'USING'                            { return '<impala>USING'; }
<impala>PARTITION\s+VALUE\s                { return '<impala>PARTITION_VALUE'; }

// Non-reserved Keywords
<impala>'ANALYTIC'                         { return '<impala>ANALYTIC'; }
<impala>'ANTI'                             { return '<impala>ANTI'; }
<impala>'BLOCK_SIZE'                       { return '<impala>BLOCK_SIZE'; }
<impala>'COMPRESSION'                      { return '<impala>COMPRESSION'; }
<impala>'CURRENT'                          { return '<impala>CURRENT'; }
<impala>'DEFAULT'                          { return '<impala>DEFAULT'; }
<impala>'ENCODING'                         { return '<impala>ENCODING'; }
<impala>'GRANT'                            { return '<impala>GRANT'; }
<impala>'ROLE'                             { return '<impala>ROLE'; }
<impala>'ROLES'                            { return '<impala>ROLES'; }
<impala>\[BROADCAST\]                      { return '<impala>BROADCAST'; }
<impala>\[NOSHUFFLE\]                      { return '<impala>NOSHUFFLE'; }
<impala>\[SHUFFLE\]                        { return '<impala>SHUFFLE'; }

<impala>'...'                              { return '<impala>...'; }
<impala>'.'                                { return '<impala>.'; }
<impala>'['                                { return '<impala>['; }
<impala>']'                                { return '<impala>]'; }

<between>'AND'                             { this.popState(); return 'BETWEEN_AND'; }

// Reserved Keywords
'ALL'                                      { return 'ALL'; }
'ALTER'                                    { parser.determineCase(yytext); return 'ALTER'; }
'AND'                                      { return 'AND'; }
'AS'                                       { return 'AS'; }
'ASC'                                      { return 'ASC'; }
'BETWEEN'                                  { this.begin('between'); return 'BETWEEN'; }
'BIGINT'                                   { return 'BIGINT'; }
'BOOLEAN'                                  { return 'BOOLEAN'; }
'BY'                                       { return 'BY'; }
'CASE'                                     { return 'CASE'; }
'CHAR'                                     { return 'CHAR'; }
'CREATE'                                   { parser.determineCase(yytext); return 'CREATE'; }
'CURRENT'                                  { return 'CURRENT'; }
'DATABASE'                                 { return 'DATABASE'; }
'DECIMAL'                                  { return 'DECIMAL'; }
'DISTINCT'                                 { return 'DISTINCT'; }
'DOUBLE'                                   { return 'DOUBLE'; }
'DESC'                                     { return 'DESC'; }
'DROP'                                     { parser.determineCase(yytext); return 'DROP'; }
'ELSE'                                     { return 'ELSE'; }
'END'                                      { return 'END'; }
'EXISTS'                                   { parser.yy.correlatedSubQuery = true; return 'EXISTS'; }
'FALSE'                                    { return 'FALSE'; }
'FLOAT'                                    { return 'FLOAT'; }
'FOLLOWING'                                { return 'FOLLOWING'; }
'FROM'                                     { parser.determineCase(yytext); return 'FROM'; }
'FULL'                                     { return 'FULL'; }
'GROUP'                                    { return 'GROUP'; }
'HAVING'                                   { return 'HAVING'; }
'IF'                                       { return 'IF'; }
'IN'                                       { return 'IN'; }
'INNER'                                    { return 'INNER'; }
'INSERT'                                   { return 'INSERT'; }
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
'OPTION'                                   { return 'OPTION'; }
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
'SELECT'                                   { parser.determineCase(yytext); return 'SELECT'; }
'SEMI'                                     { return 'SEMI'; }
'SET'                                      { parser.determineCase(yytext); return 'SET'; }
'SHOW'                                     { parser.determineCase(yytext); return 'SHOW'; }
'SMALLINT'                                 { return 'SMALLINT'; }
'STRING'                                   { return 'STRING'; }
'TABLE'                                    { return 'TABLE'; }
'THEN'                                     { return 'THEN'; }
'TIMESTAMP'                                { return 'TIMESTAMP'; }
'TINYINT'                                  { return 'TINYINT'; }
'TO'                                       { return 'TO'; }
'TRUE'                                     { return 'TRUE'; }
'TRUNCATE'                                 { parser.determineCase(yytext); return 'TRUNCATE'; }
'UNBOUNDED'                                { return 'UNBOUNDED'; }
'UPDATE'                                   { parser.determineCase(yytext); return 'UPDATE'; }
'USE'                                      { parser.determineCase(yytext); return 'USE'; }
'UNION'                                    { return 'UNION'; }
'VIEW'                                     { return 'VIEW'; }
'VARCHAR'                                  { return 'VARCHAR'; } // Not in Impala
'VALUES'                                   { return 'VALUES'; }
'WHEN'                                     { return 'WHEN'; }
'WHERE'                                    { return 'WHERE'; }
'WITH'                                     { parser.determineCase(yytext); return 'WITH'; }

// Non-reserved Keywords
'OVER'                                     { return 'OVER'; }
'ROLE'                                     { return 'ROLE'; }

// --- UDFs ---
AVG\s*\(                                   { yy.lexer.unput('('); yytext = 'avg'; parser.addFunctionLocation(yylloc, yytext); return 'AVG'; }
CAST\s*\(                                  { yy.lexer.unput('('); yytext = 'cast'; parser.addFunctionLocation(yylloc, yytext); return 'CAST'; }
COUNT\s*\(                                 { yy.lexer.unput('('); yytext = 'count'; parser.addFunctionLocation(yylloc, yytext); return 'COUNT'; }
MAX\s*\(                                   { yy.lexer.unput('('); yytext = 'max'; parser.addFunctionLocation(yylloc, yytext); return 'MAX'; }
MIN\s*\(                                   { yy.lexer.unput('('); yytext = 'min'; parser.addFunctionLocation(yylloc, yytext); return 'MIN'; }
STDDEV_POP\s*\(                            { yy.lexer.unput('('); yytext = 'stddev_pop'; parser.addFunctionLocation(yylloc, yytext); return 'STDDEV_POP'; }
STDDEV_SAMP\s*\(                           { yy.lexer.unput('('); yytext = 'stddev_samp'; parser.addFunctionLocation(yylloc, yytext); return 'STDDEV_SAMP'; }
SUM\s*\(                                   { yy.lexer.unput('('); yytext = 'sum'; parser.addFunctionLocation(yylloc, yytext); return 'SUM'; }
VARIANCE\s*\(                              { yy.lexer.unput('('); yytext = 'variance'; parser.addFunctionLocation(yylloc, yytext); return 'VARIANCE'; }
VAR_POP\s*\(                               { yy.lexer.unput('('); yytext = 'var_pop'; parser.addFunctionLocation(yylloc, yytext); return 'VAR_POP'; }
VAR_SAMP\s*\(                              { yy.lexer.unput('('); yytext = 'var_samp'; parser.addFunctionLocation(yylloc, yytext); return 'VAR_SAMP'; }
<hive>COLLECT_SET\s*\(                     { yy.lexer.unput('('); yytext = 'collect_set'; parser.addFunctionLocation(yylloc, yytext); return '<hive>COLLECT_SET'; }
<hive>COLLECT_LIST\s*\(                    { yy.lexer.unput('('); yytext = 'collect_list'; parser.addFunctionLocation(yylloc, yytext); return '<hive>COLLECT_LIST'; }
<hive>CORR\s*\(                            { yy.lexer.unput('('); yytext = 'corr'; parser.addFunctionLocation(yylloc, yytext); return '<hive>CORR'; }
<hive>COVAR_POP\s*\(                       { yy.lexer.unput('('); yytext = 'covar_pop'; parser.addFunctionLocation(yylloc, yytext); return '<hive>COVAR_POP'; }
<hive>COVAR_SAMP\s*\(                      { yy.lexer.unput('('); yytext = 'covar_samp'; parser.addFunctionLocation(yylloc, yytext); return '<hive>COVAR_SAMP'; }
<hive>HISTOGRAM_NUMERIC\s*\(               { yy.lexer.unput('('); yytext = 'histogram_numeric'; parser.addFunctionLocation(yylloc, yytext); return '<hive>HISTOGRAM_NUMERIC'; }
<hive>NTILE\s*\(                           { yy.lexer.unput('('); yytext = 'ntile'; parser.addFunctionLocation(yylloc, yytext); return '<hive>NTILE'; }
<hive>PERCENTILE\s*\(                      { yy.lexer.unput('('); yytext = 'percentile'; parser.addFunctionLocation(yylloc, yytext); return '<hive>PERCENTILE'; }
<hive>PERCENTILE_APPROX\s*\(               { yy.lexer.unput('('); yytext = 'percentile_approx'; parser.addFunctionLocation(yylloc, yytext); return '<hive>PERCENTILE_APPROX'; }
<impala>APPX_MEDIAN\s*\(                   { yy.lexer.unput('('); yytext = 'appx_median'; parser.addFunctionLocation(yylloc, yytext); return '<impala>APPX_MEDIAN'; }
<impala>EXTRACT\s*\(                       { yy.lexer.unput('('); yytext = 'extract'; parser.addFunctionLocation(yylloc, yytext); return '<impala>EXTRACT'; }
<impala>GROUP_CONCAT\s*\(                  { yy.lexer.unput('('); yytext = 'group_concat'; parser.addFunctionLocation(yylloc, yytext); return '<impala>GROUP_CONCAT'; }
<impala>STDDEV\s*\(                        { yy.lexer.unput('('); yytext = 'stddev'; parser.addFunctionLocation(yylloc, yytext); return '<impala>STDDEV'; }
<impala>VARIANCE_POP\s*\(                  { yy.lexer.unput('('); yytext = 'variance_pop'; parser.addFunctionLocation(yylloc, yytext); return '<impala>VARIANCE_POP'; }
<impala>VARIANCE_SAMP\s*\(                 { yy.lexer.unput('('); yytext = 'variance_samp'; parser.addFunctionLocation(yylloc, yytext); return '<impala>VARIANCE_SAMP'; }

// Analytical functions
DENSE_RANK\s*\(                            { yy.lexer.unput('('); yytext = 'dense_rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
FIRST_VALUE\s*\(                           { yy.lexer.unput('('); yytext = 'first_value'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LAG\s*\(                                   { yy.lexer.unput('('); yytext = 'lag'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LAST_VALUE\s*\(                            { yy.lexer.unput('('); yytext = 'last_value'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LEAD\s*\(                                  { yy.lexer.unput('('); yytext = 'lead'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
RANK\s*\(                                  { yy.lexer.unput('('); yytext = 'rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
ROW_NUMBER\s*\(                            { yy.lexer.unput('('); yytext = 'row_number'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
<hive>CUME_DIST\s*\(                       { yy.lexer.unput('('); yytext = 'cume_dist'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
<hive>PERCENT_RANK\s*\(                    { yy.lexer.unput('('); yytext = 'percent_rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }

[0-9]+                                     { return 'UNSIGNED_INTEGER'; }
[0-9]+(?:[YSL]|BD)?                        { return 'UNSIGNED_INTEGER'; }
[0-9]+E                                    { return 'UNSIGNED_INTEGER_E'; }
[A-Za-z0-9_]+                              { return 'REGULAR_IDENTIFIER'; }

<hdfs>'\u2020'                             { parser.yy.cursorFound = true; return 'CURSOR'; }
<hdfs>'\u2021'                             { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }
<hdfs>\s+[']                               { return 'HDFS_START_QUOTE'; }
<hdfs>[^'\u2020\u2021]+                    { parser.addHdfsLocation(yylloc, yytext); return 'HDFS_PATH'; }
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
                                             if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '`')) {
                                               return 'PARTIAL_VALUE';
                                             }
                                             return 'VALUE';
                                           }
<backtickedValue>\`                        { this.popState(); return 'BACKTICK'; }

\'                                         { this.begin('singleQuotedValue'); return 'SINGLE_QUOTE'; }
<singleQuotedValue>(?:\\[']|[^'])+         {
                                             if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '\'')) {
                                               return 'PARTIAL_VALUE';
                                             }
                                             return 'VALUE';
                                           }
<singleQuotedValue>\'                      { this.popState(); return 'SINGLE_QUOTE'; }

\"                                         { this.begin('doubleQuotedValue'); return 'DOUBLE_QUOTE'; }
<doubleQuotedValue>(?:\\["]|[^"])+         {
                                             if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '"')) {
                                               return 'PARTIAL_VALUE';
                                             }
                                             return 'VALUE';
                                           }
<doubleQuotedValue>\"                      { this.popState(); return 'DOUBLE_QUOTE'; }

<<EOF>>                                    { return 'EOF'; }

.                                          { /* To prevent console logging of unknown chars */ }
