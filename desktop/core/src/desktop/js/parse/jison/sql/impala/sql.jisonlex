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
%s between
%x hdfs doubleQuotedValue singleQuotedValue backtickedValue
%%

\s                                         { /* skip whitespace */ }
'--'.*                                     { /* skip comments */ }
[/][*][^*]*[*]+([^/*][^*]*[*]+)*[/]        { /* skip comments */ }

'\u2020'                                   { parser.yy.partialCursor = false; parser.yy.cursorFound = yylloc; return 'CURSOR'; }
'\u2021'                                   { parser.yy.partialCursor = true; parser.yy.cursorFound = yylloc; return 'PARTIAL_CURSOR'; }

// Reserved Keywords
'ADD'                              { return 'ADD'; }
'AGGREGATE'                        { return 'AGGREGATE'; }
'ALL'                              { return 'ALL'; }
'ALLOCATE'                         { return 'ALLOCATE'; }
'ALTER'                            { parser.determineCase(yytext); parser.addStatementTypeLocation('ALTER', yylloc, yy.lexer.upcomingInput()); return 'ALTER'; }
'ANALYTIC'                         { return 'ANALYTIC'; }
'AND'                              { return 'AND'; }
'ANTI'                             { return 'ANTI'; }
'ANY'                              { return 'ANY'; }
'ARE'                              { return 'ARE'; }
'ARRAY_AGG'                        { return 'ARRAY_AGG'; }
'ARRAY_MAX_CARDINALITY'            { return 'ARRAY_MAX_CARDINALITY'; }
'AS'                               { return 'AS'; }
'ASC'                              { return 'ASC'; }
'ASENSITIVE'                       { return 'ASENSITIVE'; }
'ASYMMETRIC'                       { return 'ASYMMETRIC'; }
'AT'                               { return 'AT'; }
'ATOMIC'                           { return 'ATOMIC'; }
'AUTHORIZATION'                    { return 'AUTHORIZATION'; }
'AVRO'                             { return 'AVRO'; }
'BEGIN_FRAME'                      { return 'BEGIN_FRAME'; }
'BEGIN_PARTITION'                  { return 'BEGIN_PARTITION'; }
'BETWEEN'                          { this.begin('between'); return 'BETWEEN'; }
'BIGINT'                           { return 'BIGINT'; }
'BLOB'                             { return 'BLOB'; }
'BLOCK_SIZE'                       { return 'BLOCK_SIZE'; }
'BOOLEAN'                          { return 'BOOLEAN'; }
'BOTH'                             { return 'BOTH'; }
'BY'                               { return 'BY'; }
'CACHED'                           { return 'CACHED'; }
'CALLED'                           { return 'CALLED'; }
'CARDINALITY'                      { return 'CARDINALITY'; }
'CASCADE'                          { return 'CASCADE'; }
'CASCADED'                         { return 'CASCADED'; }
'CASE'                             { return 'CASE'; }
'CHANGE'                           { return 'CHANGE'; }
'CHAR'                             { return 'CHAR'; }
LIKE\s+PARQUET                     { this.begin('hdfs'); return 'LIKE_PARQUET'; }
'CHARACTER'                        { return 'CHARACTER'; }
'CLOB'                             { return 'CLOB'; }
'CLOSE_FN'                         { return 'CLOSE_FN'; }
'COLLATE'                          { return 'COLLATE'; }
'COLLECT'                          { return 'COLLECT'; }
'COLUMN'                           { return 'COLUMN'; }
'COLUMNS'                          { return 'COLUMNS'; }
'COMMENT'                          { parser.determineCase(yytext); return 'COMMENT'; }
'COMMIT'                           { return 'COMMIT'; }
'COMPRESSION'                      { return 'COMPRESSION'; }
'COMPUTE'                          { parser.determineCase(yytext); return 'COMPUTE'; }
'CONDITION'                        { return 'CONDITION'; }
'CONNECT'                          { return 'CONNECT'; }
'CONSTRAINT'                       { return 'CONSTRAINT'; }
'CONTAINS'                         { return 'CONTAINS'; }
'CONVERT'                          { return 'CONVERT'; }
'COPY'                             { return 'COPY'; }
'CORR'                             { return 'CORR'; }
'CORRESPONDING'                    { return 'CORRESPONDING'; }
'COVAR_POP'                        { return 'COVAR_POP'; }
'COVAR_SAMP'                       { return 'COVAR_SAMP'; }
'CREATE'                           { parser.determineCase(yytext); parser.addStatementTypeLocation('CREATE', yylloc, yy.lexer.upcomingInput()); return 'CREATE'; }
'CROSS'                            { return 'CROSS'; }
'CUBE'                             { return 'CUBE'; }
'CURRENT'                          { return 'CURRENT'; }
'CURRENT_DATE'                     { return 'CURRENT_DATE'; }
'CURRENT_DEFAULT_TRANSFORM_GROUP'  { return 'CURRENT_DEFAULT_TRANSFORM_GROUP'; }
'CURRENT_PATH'                     { return 'CURRENT_PATH'; }
'CURRENT_ROLE'                     { return 'CURRENT_ROLE'; }
'CURRENT_ROW'                      { return 'CURRENT_ROW'; }
'CURRENT_SCHEMA'                   { return 'CURRENT_SCHEMA'; }
'CURRENT_TIME'                     { return 'CURRENT_TIME'; }
'CURRENT_TRANSFORM_GROUP_FOR_TYPE' { return 'CURRENT_TRANSFORM_GROUP_FOR_TYPE'; }
'CURSOR'                           { return 'CURSOR'; }
'CYCLE'                            { return 'CYCLE'; }
'DATA'                             { return 'DATA'; }
'DATABASE'                         { return 'DATABASE'; }
'DATABASES'                        { return 'DATABASES'; }
'DEALLOCATE'                       { return 'DEALLOCATE'; }
'DEC'                              { return 'DEC'; }
'DECFLOAT'                         { return 'DECFLOAT'; }
'DECIMAL'                          { return 'DECIMAL'; }
'DECLARE'                          { return 'DECLARE'; }
'DEFINE'                           { return 'DEFINE'; }
'DELETE'                           { return 'DELETE'; }
'DELIMITED'                        { return 'DELIMITED'; }
'DEREF'                            { return 'DEREF'; }
'DESC'                             { return 'DESC'; }
'DESCRIBE'                         { parser.determineCase(yytext); parser.addStatementTypeLocation('DESCRIBE', yylloc); return 'DESCRIBE'; }
'DETERMINISTIC'                    { return 'DETERMINISTIC'; }
'DISCONNECT'                       { return 'DISCONNECT'; }
'DISTINCT'                         { return 'DISTINCT'; }
'DIV'                              { return 'ARITHMETIC_OPERATOR'; }
'DOUBLE'                           { return 'DOUBLE'; }
'DROP'                             { parser.determineCase(yytext); parser.addStatementTypeLocation('DROP', yylloc, yy.lexer.upcomingInput()); return 'DROP'; }
'DYNAMIC'                          { return 'DYNAMIC'; }
'EACH'                             { return 'EACH'; }
'ELEMENT'                          { return 'ELEMENT'; }
'ELSE'                             { return 'ELSE'; }
'EMPTY'                            { return 'EMPTY'; }
'ENCODING'                         { return 'ENCODING'; }
'END'                              { return 'END'; }
'END_FRAME'                        { return 'END_FRAME'; }
'END_PARTITION'                    { return 'END_PARTITION'; }
'EQUALS'                           { return 'EQUALS'; }
'ESCAPE'                           { return 'ESCAPE'; }
'ESCAPED'                          { return 'ESCAPED'; }
'EVERY'                            { return 'EVERY'; }
'EXCEPT'                           { return 'EXCEPT'; }
'EXEC'                             { return 'EXEC'; }
'EXECUTE'                          { return 'EXECUTE'; }
'EXISTS'                           { parser.yy.correlatedSubQuery = true; return 'EXISTS'; }
'EXPLAIN'                          { parser.determineCase(yytext); parser.addStatementTypeLocation('EXPLAIN', yylloc); return 'EXPLAIN'; }
'EXTENDED'                         { return 'EXTENDED'; }
'EXTERNAL'                         { return 'EXTERNAL'; }
'FALSE'                            { return 'FALSE'; }
'FETCH'                            { return 'FETCH'; }
'FIELDS'                           { return 'FIELDS'; }
'FILEFORMAT'                       { return 'FILEFORMAT'; }
'FILES'                            { return 'FILES'; }
'FILTER'                           { return 'FILTER'; }
'FINALIZE_FN'                      { return 'FINALIZE_FN'; }
'FIRST'                            { return 'FIRST'; }
'FLOAT'                            { return 'FLOAT'; }
'FOLLOWING'                        { return 'FOLLOWING'; }
'FOR'                              { return 'FOR'; }
'FOREIGN'                          { return 'FOREIGN'; }
'FORMAT'                           { return 'FORMAT'; }
'FORMATTED'                        { return 'FORMATTED'; }
'FRAME_ROW'                        { return 'FRAME_ROW'; }
'FREE'                             { return 'FREE'; }
'FROM'                             { parser.determineCase(yytext); return 'FROM'; }
'FULL'                             { return 'FULL'; }
'FUNCTION'                         { return 'FUNCTION'; }
'FUNCTIONS'                        { return 'FUNCTIONS'; }
'FUSION'                           { return 'FUSION'; }
'GET'                              { return 'GET'; }
'GLOBAL'                           { return 'GLOBAL'; }
'GRANT'                            { parser.determineCase(yytext); parser.addStatementTypeLocation('GRANT', yylloc); return 'GRANT'; }
'GROUP'                            { return 'GROUP'; }
'GROUPING'                         { return 'GROUPING'; }
'GROUPS'                           { return 'GROUPS'; }
'HASH'                             { return 'HASH'; }
'HAVING'                           { return 'HAVING'; }
'HOLD'                             { return 'HOLD'; }
'IF'                               { return 'IF'; }
'IGNORE'                           { return 'IGNORE'; }
'ILIKE'                            { return 'ILIKE'; }
'IN'                               { return 'IN'; }
'INCREMENTAL'                      { return 'INCREMENTAL'; }
'INDICATOR'                        { return 'INDICATOR'; }
'INIT_FN'                          { return 'INIT_FN'; }
'INITIAL'                          { return 'INITIAL'; }
'INNER'                            { return 'INNER'; }
'INOUT'                            { return 'INOUT'; }
'INPATH'                           { this.begin('hdfs'); return 'INPATH'; }
'INSENSITIVE'                      { return 'INSENSITIVE'; }
'INSERT'                           { parser.determineCase(yytext); parser.addStatementTypeLocation('INSERT', yylloc); return 'INSERT'; }
'INT'                              { return 'INT'; }
'INTERMEDIATE'                     { return 'INTERMEDIATE'; }
'INTERSECT'                        { return 'INTERSECT'; }
'INTERSECTION'                     { return 'INTERSECTION'; }
'INTERVAL'                         { return 'INTERVAL'; }
'INTO'                             { return 'INTO'; }
'INVALIDATE'                       { parser.determineCase(yytext); parser.addStatementTypeLocation('INVALIDATE', yylloc, yy.lexer.upcomingInput()); return 'INVALIDATE'; }
'IREGEXP'                          { return 'IREGEXP'; }
'IS'                               { return 'IS'; }
'JOIN'                             { return 'JOIN'; }
'JSON_ARRAY'                       { return 'JSON_ARRAY'; }
'JSON_ARRAYAGG'                    { return 'JSON_ARRAYAGG'; }
'JSON_EXISTS'                      { return 'JSON_EXISTS'; }
'JSON_OBJECT'                      { return 'JSON_OBJECT'; }
'JSON_OBJECTAGG'                   { return 'JSON_OBJECTAGG'; }
'JSON_QUERY'                       { return 'JSON_QUERY'; }
'JSON_TABLE'                       { return 'JSON_TABLE'; }
'JSON_TABLE_PRIMITIVE'             { return 'JSON_TABLE_PRIMITIVE'; }
'JSON_VALUE'                       { return 'JSON_VALUE'; }
'KEY'                              { return 'KEY'; }
'KUDU'                             { return 'KUDU'; }
'LARGE'                            { return 'LARGE'; }
'LAST'                             { return 'LAST'; }
'LEADING'                          { return 'LEADING'; }
'LEFT'                             { return 'LEFT'; }
'LIKE'                             { return 'LIKE'; }
'LIKE_REGEX'                       { return 'LIKE_REGEX'; }
'LIMIT'                            { return 'LIMIT'; }
'LINES'                            { return 'LINES'; }
'LISTAGG'                          { return 'LISTAGG'; }
'LOAD'                             { parser.determineCase(yytext); parser.addStatementTypeLocation('LOAD', yylloc, yy.lexer.upcomingInput()); return 'LOAD'; }
'LOCAL'                            { return 'LOCAL'; }
'LOCALTIMESTAMP'                   { return 'LOCALTIMESTAMP'; }
'LOCATION'                         { this.begin('hdfs'); return 'LOCATION'; }
'MATCH'                            { return 'MATCH'; }
'MATCH_NUMBER'                     { return 'MATCH_NUMBER'; }
'MATCH_RECOGNIZE'                  { return 'MATCH_RECOGNIZE'; }
'MATCHES'                          { return 'MATCHES'; }
'MERGE'                            { return 'MERGE'; }
'MERGE_FN'                         { return 'MERGE_FN'; }
'METADATA'                         { return 'METADATA'; }
'METHOD'                           { return 'METHOD'; }
'MODIFIES'                         { return 'MODIFIES'; }
'MULTISET'                         { return 'MULTISET'; }
'NATIONAL'                         { return 'NATIONAL'; }
'NATURAL'                          { return 'NATURAL'; }
'NCHAR'                            { return 'NCHAR'; }
'NCLOB'                            { return 'NCLOB'; }
'NO'                               { return 'NO'; }
'NONE'                             { return 'NONE'; }
'NORMALIZE'                        { return 'NORMALIZE'; }
'NOT'                              { return 'NOT'; }
'NTH_VALUE'                        { return 'NTH_VALUE'; }
'NULL'                             { return 'NULL'; }
'NULLS'                            { return 'NULLS'; }
'NUMERIC'                          { return 'NUMERIC'; }
'OCCURRENCES_REGEX'                { return 'OCCURRENCES_REGEX'; }
'OCTET_LENGTH'                     { return 'OCTET_LENGTH'; }
'OF'                               { return 'OF'; }
'OFFSET'                           { return 'OFFSET'; }
'OMIT'                             { return 'OMIT'; }
'ON'                               { return 'ON'; }
'ONE'                              { return 'ONE'; }
'ONLY'                             { return 'ONLY'; }
'OPTION'                           { return 'OPTION'; }
'OR'                               { return 'OR'; }
'ORC'                              { return 'ORC'; }
'ORDER'                            { return 'ORDER'; }
'OUT'                              { return 'OUT'; }
'OUTER'                            { return 'OUTER'; }
'OVER'                             { return 'OVER'; }
'OVERLAPS'                         { return 'OVERLAPS'; }
'OVERLAY'                          { return 'OVERLAY'; }
'OVERWRITE'                        { return 'OVERWRITE'; }
'PARQUET'                          { return 'PARQUET'; }
'PARTITION'                        { return 'PARTITION'; }
PARTITION\s+VALUE\s                { return 'PARTITION_VALUE'; }
'PARTITIONED'                      { return 'PARTITIONED'; }
'PARTITIONS'                       { return 'PARTITIONS'; }
'PATTERN'                          { return 'PATTERN'; }
'PER'                              { return 'PER'; }
'PERCENT'                          { return 'PERCENT'; }
'PERCENTILE_CONT'                  { return 'PERCENTILE_CONT'; }
'PERCENTILE_DISC'                  { return 'PERCENTILE_DISC'; }
'PORTION'                          { return 'PORTION'; }
'POSITION'                         { return 'POSITION'; }
'POSITION_REGEX'                   { return 'POSITION_REGEX'; }
'PRECEDES'                         { return 'PRECEDES'; }
'PRECEDING'                        { return 'PRECEDING'; }
'PREPARE'                          { return 'PREPARE'; }
'PREPARE_FN'                       { return 'PREPARE_FN'; }
'PRIMARY'                          { return 'PRIMARY'; }
'PROCEDURE'                        { return 'PROCEDURE'; }
'PTF'                              { return 'PTF'; }
'PURGE'                            { return 'PURGE'; }
'RANGE'                            { return 'RANGE'; }
'RANGE'                            { return 'RANGE'; }
'RCFILE'                           { return 'RCFILE'; }
'READS'                            { return 'READS'; }
'REAL'                             { return 'REAL'; }
'RECOVER'                          { return 'RECOVER'; }
'RECURSIVE'                        { return 'RECURSIVE'; }
'REF'                              { return 'REF'; }
'REFERENCES'                       { return 'REFERENCES'; }
'REFERENCING'                      { return 'REFERENCING'; }
'REFRESH'                          { parser.determineCase(yytext); parser.addStatementTypeLocation('REFRESH', yylloc); return 'REFRESH'; }
'REGEXP'                           { return 'REGEXP'; }
'REGR_AVGX'                        { return 'REGR_AVGX'; }
'REGR_AVGY'                        { return 'REGR_AVGY'; }
'REGR_COUNT'                       { return 'REGR_COUNT'; }
'REGR_INTERCEPT'                   { return 'REGR_INTERCEPT'; }
'REGR_R2REGR_SLOPE'                { return 'REGR_R2REGR_SLOPE'; }
'REGR_SXX'                         { return 'REGR_SXX'; }
'REGR_SXY'                         { return 'REGR_SXY'; }
'REGR_SYY'                         { return 'REGR_SYY'; }
'RELEASE'                          { return 'RELEASE'; }
'RENAME'                           { return 'RENAME'; }
'REPEATABLE'                       { return 'REPEATABLE'; }
'REPLACE'                          { return 'REPLACE'; }
'REPLICATION'                      { return 'REPLICATION'; }
'RESTRICT'                         { return 'RESTRICT'; }
'RETURNS'                          { return 'RETURNS'; }
'REVOKE'                           { parser.determineCase(yytext); parser.addStatementTypeLocation('REVOKE', yylloc); return 'REVOKE'; }
'RIGHT'                            { return 'RIGHT'; }
'RLIKE'                            { return 'RLIKE'; }
'ROLE'                             { return 'ROLE'; }
'ROLES'                            { return 'ROLES'; }
'ROLLBACK'                         { return 'ROLLBACK'; }
'ROLLUP'                           { return 'ROLLUP'; }
'ROW'                              { return 'ROW'; }
'ROWS'                             { return 'ROWS'; }
'RUNNING'                          { return 'RUNNING'; }
'SAVEPOINT'                        { return 'SAVEPOINT'; }
'SCHEMA'                           { return 'SCHEMA'; }
'SCHEMAS'                          { return 'SCHEMAS'; }
'SCOPE'                            { return 'SCOPE'; }
'SCROLL'                           { return 'SCROLL'; }
'SEARCH'                           { return 'SEARCH'; }
'SEEK'                             { return 'SEEK'; }
'SELECT'                           { parser.determineCase(yytext); parser.addStatementTypeLocation('SELECT', yylloc); return 'SELECT'; }
'SEMI'                             { return 'SEMI'; }
'SENSITIVE'                        { return 'SENSITIVE'; }
'SEQUENCEFILE'                     { return 'SEQUENCEFILE'; }
'SERDEPROPERTIES'                  { return 'SERDEPROPERTIES'; }
'SERIALIZE_FN'                     { return 'SERIALIZE_FN'; }
'SERVER'                           { return 'SERVER'; }
'SET'                              { parser.determineCase(yytext); parser.addStatementTypeLocation('SET', yylloc); return 'SET'; }
'SHOW'                             { parser.determineCase(yytext); parser.addStatementTypeLocation('SHOW', yylloc); return 'SHOW'; }
'SIMILAR'                          { return 'SIMILAR'; }
'SKIP'                             { return 'SKIP'; }
'SMALLINT'                         { return 'SMALLINT'; }
'SOME'                             { return 'SOME'; }
'SORT'                             { return 'SORT'; }
'SPECIFIC'                         { return 'SPECIFIC'; }
'SPECIFICTYPE'                     { return 'SPECIFICTYPE'; }
'SQLEXCEPTION'                     { return 'SQLEXCEPTION'; }
'SQLSTATE'                         { return 'SQLSTATE'; }
'SQLWARNING'                       { return 'SQLWARNING'; }
'STATIC'                           { return 'STATIC'; }
'STATS'                            { return 'STATS'; }
'STORED'                           { return 'STORED'; }
'STRAIGHT_JOIN'                    { return 'STRAIGHT_JOIN'; }
'STRING'                           { return 'STRING'; }
'SUBMULTISET'                      { return 'SUBMULTISET'; }
'SUBSET'                           { return 'SUBSET'; }
'SUBSTRING_REGEX'                  { return 'SUBSTRING_REGEX'; }
'SUCCEEDS'                         { return 'SUCCEEDS'; }
'SYMBOL'                           { return 'SYMBOL'; }
'SYMMETRIC'                        { return 'SYMMETRIC'; }
'SYSTEM_TIME'                      { return 'SYSTEM_TIME'; }
'SYSTEM_USER'                      { return 'SYSTEM_USER'; }
'TABLE'                            { return 'TABLE'; }
'TABLES'                           { return 'TABLES'; }
'TABLESAMPLE'                      { return 'TABLESAMPLE'; }
'TBLPROPERTIES'                    { return 'TBLPROPERTIES'; }
'TERMINATED'                       { return 'TERMINATED'; }
'TEXTFILE'                         { return 'TEXTFILE'; }
'THEN'                             { return 'THEN'; }
'TIMESTAMP'                        { return 'TIMESTAMP'; }
'TIMEZONE_HOUR'                    { return 'TIMEZONE_HOUR'; }
'TIMEZONE_MINUTE'                  { return 'TIMEZONE_MINUTE'; }
'TINYINT'                          { return 'TINYINT'; }
'TO'                               { return 'TO'; }
'TRAILING'                         { return 'TRAILING'; }
'TRANSLATE_REGEX'                  { return 'TRANSLATE_REGEX'; }
'TRANSLATION'                      { return 'TRANSLATION'; }
'TREAT'                            { return 'TREAT'; }
'TRIGGER'                          { return 'TRIGGER'; }
'TRIM_ARRAY'                       { return 'TRIM_ARRAY'; }
'TRUE'                             { return 'TRUE'; }
'TRUNCATE'                         { parser.determineCase(yytext); parser.addStatementTypeLocation('TRUNCATE', yylloc, yy.lexer.upcomingInput()); return 'TRUNCATE'; }
'UESCAPE'                          { return 'UESCAPE'; }
'UNBOUNDED'                        { return 'UNBOUNDED'; }
'UNCACHED'                         { return 'UNCACHED'; }
'UNION'                            { return 'UNION'; }
'UNIQUE'                           { return 'UNIQUE'; }
'UNKNOWN'                          { return 'UNKNOWN'; }
'UNNEST'                           { return 'UNNEST'; }
'UPDATE'                           { parser.determineCase(yytext); return 'UPDATE'; }
'UPDATE_FN'                        { return 'UPDATE_FN'; }
'UPSERT'                           { parser.determineCase(yytext); parser.addStatementTypeLocation('UPSERT', yylloc); return 'UPSERT'; }
'URI'                              { return 'URI'; }
'USE'                              { parser.determineCase(yytext); parser.addStatementTypeLocation('USE', yylloc); return 'USE'; }
'USER'                             { return 'USER'; }
'USING'                            { return 'USING'; }
'VALUE_OF'                         { return 'VALUE_OF'; }
'VALUES'                           { return 'VALUES'; }
'VARBINARY'                        { return 'VARBINARY'; }
'VARCHAR'                          { return 'VARCHAR'; }
'VARCHAR'                          { return 'VARCHAR'; }
'VARYING'                          { return 'VARYING'; }
'VERSIONING'                       { return 'VERSIONING'; }
'VIEW'                             { return 'VIEW'; }
'WHEN'                             { return 'WHEN'; }
'WHENEVER'                         { return 'WHENEVER'; }
'WHERE'                            { return 'WHERE'; }
'WIDTH_BUCKET'                     { return 'WIDTH_BUCKET'; }
'WINDOW'                           { return 'WINDOW'; }
'WITH'                             { parser.determineCase(yytext); parser.addStatementTypeLocation('WITH', yylloc); return 'WITH'; }
'WITH'                             { parser.determineCase(yytext); parser.addStatementTypeLocation('WITH', yylloc); return 'WITH'; }
'WITHIN'                           { return 'WITHIN'; }
'WITHOUT'                          { return 'WITHOUT'; }

// Non-reserved Keywords
'ARRAY'                            { return 'ARRAY'; }
'DEFAULT'                          { return 'DEFAULT'; }
'MAP'                              { return 'MAP'; }
'OVER'                             { return 'OVER'; }
'OWNER'                            { return 'OWNER'; }
'ROLE'                             { return 'ROLE'; }
'STRUCT'                           { return 'STRUCT'; }
\[BROADCAST\]                      { return 'BROADCAST'; }
\[NOSHUFFLE\]                      { return 'NOSHUFFLE'; }
\[SHUFFLE\]                        { return 'SHUFFLE'; }

'...'                              { return '...'; }
'.'                                { return '.'; }
'['                                { return '['; }
']'                                { return ']'; }

<between>'AND'                     { this.popState(); return 'BETWEEN_AND'; }

// Reserved Keywords

// Non-reserved Keywords


// --- UDFs ---
APPX_MEDIAN\s*\(                   { yy.lexer.unput('('); yytext = 'appx_median'; parser.addFunctionLocation(yylloc, yytext); return 'APPX_MEDIAN'; }
AVG\s*\(                           { yy.lexer.unput('('); yytext = 'avg'; parser.addFunctionLocation(yylloc, yytext); return 'AVG'; }
CAST\s*\(                          { yy.lexer.unput('('); yytext = 'cast'; parser.addFunctionLocation(yylloc, yytext); return 'CAST'; }
COUNT\s*\(                         { yy.lexer.unput('('); yytext = 'count'; parser.addFunctionLocation(yylloc, yytext); return 'COUNT'; }
EXTRACT\s*\(                       { yy.lexer.unput('('); yytext = 'extract'; parser.addFunctionLocation(yylloc, yytext); return 'EXTRACT'; }
GROUP_CONCAT\s*\(                  { yy.lexer.unput('('); yytext = 'group_concat'; parser.addFunctionLocation(yylloc, yytext); return 'GROUP_CONCAT'; }
MAX\s*\(                           { yy.lexer.unput('('); yytext = 'max'; parser.addFunctionLocation(yylloc, yytext); return 'MAX'; }
MIN\s*\(                           { yy.lexer.unput('('); yytext = 'min'; parser.addFunctionLocation(yylloc, yytext); return 'MIN'; }
NDV\s*\(                           { yy.lexer.unput('('); yytext = 'ndv'; parser.addFunctionLocation(yylloc, yytext); return 'NDV'; }
STDDEV\s*\(                        { yy.lexer.unput('('); yytext = 'stddev'; parser.addFunctionLocation(yylloc, yytext); return 'STDDEV'; }
STDDEV_POP\s*\(                    { yy.lexer.unput('('); yytext = 'stddev_pop'; parser.addFunctionLocation(yylloc, yytext); return 'STDDEV_POP'; }
STDDEV_SAMP\s*\(                   { yy.lexer.unput('('); yytext = 'stddev_samp'; parser.addFunctionLocation(yylloc, yytext); return 'STDDEV_SAMP'; }
SUM\s*\(                           { yy.lexer.unput('('); yytext = 'sum'; parser.addFunctionLocation(yylloc, yytext); return 'SUM'; }
VAR_POP\s*\(                       { yy.lexer.unput('('); yytext = 'var_pop'; parser.addFunctionLocation(yylloc, yytext); return 'VAR_POP'; }
VAR_SAMP\s*\(                      { yy.lexer.unput('('); yytext = 'var_samp'; parser.addFunctionLocation(yylloc, yytext); return 'VAR_SAMP'; }
VARIANCE\s*\(                      { yy.lexer.unput('('); yytext = 'variance'; parser.addFunctionLocation(yylloc, yytext); return 'VARIANCE'; }
VARIANCE_POP\s*\(                  { yy.lexer.unput('('); yytext = 'variance_pop'; parser.addFunctionLocation(yylloc, yytext); return 'VARIANCE_POP'; }
VARIANCE_SAMP\s*\(                 { yy.lexer.unput('('); yytext = 'variance_samp'; parser.addFunctionLocation(yylloc, yytext); return 'VARIANCE_SAMP'; }

// Analytical functions
CUME_DIST\s*\(                     { yy.lexer.unput('('); yytext = 'cume_dist'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
DENSE_RANK\s*\(                    { yy.lexer.unput('('); yytext = 'dense_rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
FIRST_VALUE\s*\(                   { yy.lexer.unput('('); yytext = 'first_value'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LAG\s*\(                           { yy.lexer.unput('('); yytext = 'lag'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LAST_VALUE\s*\(                    { yy.lexer.unput('('); yytext = 'last_value'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LEAD\s*\(                          { yy.lexer.unput('('); yytext = 'lead'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
NTILE\s*\(                         { yy.lexer.unput('('); yytext = 'ntile'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
PERCENT_RANK\s*\(                  { yy.lexer.unput('('); yytext = 'percent_rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
RANK\s*\(                          { yy.lexer.unput('('); yytext = 'rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
ROW_NUMBER\s*\(                    { yy.lexer.unput('('); yytext = 'row_number'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
SYSTEM\s*\(                        { yy.lexer.unput('('); yytext = 'system'; return 'SYSTEM'; }

[0-9]+                             { return 'UNSIGNED_INTEGER'; }
[0-9]+(?:[YSL]|BD)?                { return 'UNSIGNED_INTEGER'; }
[0-9]+E                            { return 'UNSIGNED_INTEGER_E'; }
[A-Za-z0-9_]+                      { return 'REGULAR_IDENTIFIER'; }

<hdfs>'\u2020'                     { parser.yy.cursorFound = true; return 'CURSOR'; }
<hdfs>'\u2021'                     { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }
<hdfs>\s+[']                       { return 'HDFS_START_QUOTE'; }
<hdfs>[^'\u2020\u2021]+            { parser.addFileLocation(yylloc, yytext); return 'HDFS_PATH'; }
<hdfs>[']                          { this.popState(); return 'HDFS_END_QUOTE'; }
<hdfs><<EOF>>                      { return 'EOF'; }

'&&'                               { return 'AND'; }
'||'                               { return 'OR'; }
'='                                { return '='; }
'<'                                { return '<'; }
'>'                                { return '>'; }
'!='                               { return 'COMPARISON_OPERATOR'; }
'<='                               { return 'COMPARISON_OPERATOR'; }
'>='                               { return 'COMPARISON_OPERATOR'; }
'<>'                               { return 'COMPARISON_OPERATOR'; }
'<=>'                              { return 'COMPARISON_OPERATOR'; }

'-'                                { return '-'; }
'*'                                { return '*'; }
'+'                                { return 'ARITHMETIC_OPERATOR'; }
'/'                                { return 'ARITHMETIC_OPERATOR'; }
'%'                                { return 'ARITHMETIC_OPERATOR'; }
'|'                                { return 'ARITHMETIC_OPERATOR'; }
'^'                                { return 'ARITHMETIC_OPERATOR'; }
'&'                                { return 'ARITHMETIC_OPERATOR'; }

','                                { return ','; }
'.'                                { return '.'; }
':'                                { return ':'; }
';'                                { return ';'; }
'~'                                { return '~'; }
'!'                                { return '!'; }

'('                                { return '('; }
')'                                { return ')'; }
'['                                { return '['; }
']'                                { return ']'; }

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
<singleQuotedValue>(?:\\\\|\\[']|[^'])+         {
                                             if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '\'')) {
                                               return 'PARTIAL_VALUE';
                                             }
                                             return 'VALUE';
                                           }
<singleQuotedValue>\'                      { this.popState(); return 'SINGLE_QUOTE'; }

\"                                         { this.begin('doubleQuotedValue'); return 'DOUBLE_QUOTE'; }
<doubleQuotedValue>(?:\\\\|\\["]|[^"])+         {
                                             if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '"')) {
                                               return 'PARTIAL_VALUE';
                                             }
                                             return 'VALUE';
                                           }
<doubleQuotedValue>\"                      { this.popState(); return 'DOUBLE_QUOTE'; }

<<EOF>>                                    { return 'EOF'; }

.                                          { /* To prevent console logging of unknown chars */ }
<between>.                                 { }
<hdfs>.                                    { }
<backtickedValue>.                         { }
<singleQuotedValue>.                       { }
<doubleQuotedValue>.                       { }
