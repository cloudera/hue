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
<hive>'ARRAY'                              { return 'ARRAY'; }
<hive>'AS'                                 { return '<hive>AS'; }
<hive>'AUTHORIZATION'                      { return '<hive>AUTHORIZATION'; }
<hive>'BINARY'                             { return '<hive>BINARY'; }
<hive>'CACHE'                              { return '<hive>CACHE'; }
<hive>'COLUMN'                             { return '<hive>COLUMN'; }
<hive>'CONF'                               { return '<hive>CONF'; }
<hive>'CONSTRAINT'                         { return '<hive>CONSTRAINT'; }
<hive>'CREATE'                             { parser.determineCase(yytext); return '<hive>CREATE'; }
<hive>'CUBE'                               { return '<hive>CUBE'; }
<hive>'CURRENT'                            { return '<hive>CURRENT'; }
<hive>'DATE'                               { return '<hive>DATE'; }
<hive>'DELETE'                             { parser.determineCase(yytext); return '<hive>DELETE'; }
<hive>'DESCRIBE'                           { parser.determineCase(yytext); return '<hive>DESCRIBE'; }
<hive>'EXTENDED'                           { return '<hive>EXTENDED'; }
<hive>'EXTERNAL'                           { return '<hive>EXTERNAL'; }
<hive>'FOR'                                { return '<hive>FOR'; }
<hive>'FOREIGN'                            { return '<hive>FOREIGN'; }
<hive>'FUNCTION'                           { return '<hive>FUNCTION'; }
<hive>'GRANT'                              { return '<hive>GRANT'; }
<hive>'GROUPING'                           { return '<hive>GROUPING'; }
<hive>'IMPORT'                             { parser.determineCase(yytext); return '<hive>IMPORT'; }
<hive>'INSERT'                             { parser.determineCase(yytext); return '<hive>INSERT'; }
<hive>'LATERAL'                            { return '<hive>LATERAL'; }
<hive>'LOCAL'                              { return '<hive>LOCAL'; }
<hive>'MACRO'                              { return '<hive>MACRO'; }
<hive>'MAP'                                { return 'MAP'; }
<hive>'NONE'                               { return '<hive>NONE'; }
<hive>'OF'                                 { return '<hive>OF'; }
<hive>'OUT'                                { return '<hive>OUT'; }
<hive>'PRIMARY'                            { return '<hive>PRIMARY'; }
<hive>'REFERENCES'                         { return '<hive>REFERENCES'; }
<hive>'REVOKE'                             { return '<hive>REVOKE'; }
<hive>'ROLLUP'                             { return '<hive>ROLLUP'; }
<hive>'SYNC'                               { return '<hive>SYNC'; }
<hive>'TABLE'                              { return '<hive>TABLE'; }
<hive>'TIMESTAMP'                          { return '<hive>TIMESTAMP'; }
<hive>'UTC_TIMESTAMP'                      { return '<hive>UTC_TIMESTAMP'; }
<hive>'USER'                               { return '<hive>USER'; }
<hive>'USING'                              { return '<hive>USING'; }
<hive>'VIEWS'                              { return '<hive>VIEWS'; }

// Non-reserved Keywords
<hive>'ABORT'                              { parser.determineCase(yytext); return '<hive>ABORT'; }
<hive>'ADD'                                { return '<hive>ADD'; }
<hive>'ADMIN'                              { return '<hive>ADMIN'; }
<hive>'AFTER'                              { return '<hive>AFTER'; }
<hive>'ANALYZE'                            { parser.determineCase(yytext); return '<hive>ANALYZE'; }
<hive>'ARCHIVE'                            { return '<hive>ARCHIVE'; }
<hive>'ASC'                                { return '<hive>ASC'; }
<hive>'AVRO'                               { return '<hive>AVRO'; }
<hive>'BUCKET'                             { return '<hive>BUCKET'; }
<hive>'BUCKETS'                            { return '<hive>BUCKETS'; }
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
<hive>'DAY'                                { return '<hive>DAY'; }
<hive>'DAYOFWEEK'                          { return '<hive>DAYOFWEEK'; }
<hive>'DBPROPERTIES'                       { return '<hive>DBPROPERTIES'; }
<hive>'DEFERRED'                           { return '<hive>DEFERRED'; }
<hive>'DEFINED'                            { return '<hive>DEFINED'; }
<hive>'DELIMITED'                          { return '<hive>DELIMITED'; }
<hive>'DEPENDENCY'                         { return '<hive>DEPENDENCY'; }
<hive>'DESC'                               { return '<hive>DESC'; }
<hive>'DIRECTORY'                          { this.begin('hdfs'); return '<hive>DIRECTORY'; }
<hive>'DISABLE'                            { return '<hive>DISABLE'; }
<hive>'DISTRIBUTE'                         { return '<hive>DISTRIBUTE'; }
<hive>DOUBLE\s+PRECISION                   { return '<hive>DOUBLE_PRECISION'; }
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
<hive>'HOUR'                               { return '<hive>HOUR'; }
<hive>'IDXPROPERTIES'                      { return '<hive>IDXPROPERTIES'; }
<hive>'INDEX'                              { return '<hive>INDEX'; }
<hive>'INDEXES'                            { return '<hive>INDEXES'; }
<hive>'INPATH'                             { this.begin('hdfs'); return '<hive>INPATH'; }
<hive>'INPUTFORMAT'                        { return '<hive>INPUTFORMAT'; }
<hive>'ITEMS'                              { return '<hive>ITEMS'; }
<hive>'JAR'                                { return '<hive>JAR'; }
<hive>'JSONFILE'                           { return '<hive>JSONFILE'; }
<hive>'KEY'                                { return '<hive>KEY'; }
<hive>'KEYS'                               { return '<hive>KEYS'; }
<hive>'LINES'                              { return '<hive>LINES'; }
<hive>'LOAD'                               { parser.determineCase(yytext); return '<hive>LOAD'; }
<hive>'LOCATION'                           { this.begin('hdfs'); return '<hive>LOCATION'; }
<hive>'LOCK'                               { return '<hive>LOCK'; }
<hive>'LOCKS'                              { return '<hive>LOCKS'; }
<hive>'MATCHED'                            { return '<hive>MATCHED'; }
<hive>'MERGE'                              { return '<hive>MERGE'; }
<hive>'METADATA'                           { return '<hive>METADATA'; }
<hive>'MINUTE'                             { return '<hive>MINUTE'; }
<hive>'MONTH'                              { return '<hive>MONTH'; }
<hive>'MSCK'                               { return '<hive>MSCK'; }
<hive>'NORELY'                             { return '<hive>NORELY'; }
<hive>'NOSCAN'                             { return '<hive>NOSCAN'; }
<hive>'NOVALIDATE'                         { return '<hive>NOVALIDATE'; }
<hive>'NO_DROP'                            { return '<hive>NO_DROP'; }
<hive>'OFFLINE'                            { return '<hive>OFFLINE'; }
<hive>'ORC'                                { return '<hive>ORC'; }
<hive>'OUTPUTFORMAT'                       { return '<hive>OUTPUTFORMAT'; }
<hive>'OVERWRITE'                          { return '<hive>OVERWRITE'; }
<hive>OVERWRITE\s+DIRECTORY                { this.begin('hdfs'); return '<hive>OVERWRITE_DIRECTORY'; }
<hive>'OWNER'                              { return '<hive>OWNER'; }
<hive>'PARQUET'                            { return '<hive>PARQUET'; }
<hive>'PARTITIONED'                        { return '<hive>PARTITIONED'; }
<hive>'PARTITIONS'                         { return '<hive>PARTITIONS'; }
<hive>'PERCENT'                            { return '<hive>PERCENT'; }
<hive>'PRIVILEGES'                         { return '<hive>PRIVILEGES'; }
<hive>'PURGE'                              { return '<hive>PURGE'; }
<hive>'QUARTER'                            { return '<hive>QUARTER'; }
<hive>'RCFILE'                             { return '<hive>RCFILE'; }
<hive>'REBUILD'                            { return '<hive>REBUILD'; }
<hive>'RELOAD'                             { parser.determineCase(yytext); return '<hive>RELOAD'; }
<hive>'RELY'                               { return '<hive>RELY'; }
<hive>'REPAIR'                             { return '<hive>REPAIR'; }
<hive>'REPLICATION'                        { return '<hive>REPLICATION'; }
<hive>'RECOVER'                            { return '<hive>RECOVER'; }
<hive>'RENAME'                             { return '<hive>RENAME'; }
<hive>'REPLACE'                            { return '<hive>REPLACE'; }
<hive>'RESTRICT'                           { return '<hive>RESTRICT'; }
<hive>'ROLE'                               { return '<hive>ROLE'; }
<hive>'ROLES'                              { return '<hive>ROLES'; }
<hive>'SECOND'                             { return '<hive>SECOND'; }
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
<hive>'STRUCT'                             { return 'STRUCT'; }
<hive>'TABLES'                             { return '<hive>TABLES'; }
<hive>'TABLESAMPLE'                        { return '<hive>TABLESAMPLE'; }
<hive>'TBLPROPERTIES'                      { return '<hive>TBLPROPERTIES'; }
<hive>'TEMPORARY'                          { return '<hive>TEMPORARY'; }
<hive>'TERMINATED'                         { return '<hive>TERMINATED'; }
<hive>'TEXTFILE'                           { return '<hive>TEXTFILE'; }
<hive>'TINYINT'                            { return '<hive>TINYINT'; }
<hive>'TOUCH'                              { return '<hive>TOUCH'; }
<hive>'TRANSACTIONAL'                      { return '<hive>TRANSACTIONAL'; }
<hive>'TRANSACTIONS'                       { return '<hive>TRANSACTIONS'; }
<hive>'UNARCHIVE'                          { return '<hive>UNARCHIVE'; }
<hive>'UNIONTYPE'                          { return '<hive>UNIONTYPE'; }
<hive>'USE'                                { parser.determineCase(yytext); return '<hive>USE'; }
<hive>'VIEW'                               { return '<hive>VIEW'; }
<hive>'WAIT'                               { return '<hive>WAIT'; }
<hive>'WEEK'                               { return '<hive>WEEK'; }
<hive>'WINDOW'                             { return '<hive>WINDOW'; }
<hive>'WITH'                               { parser.determineCase(yytext); parser.addStatementTypeLocation('WITH', yylloc); return '<hive>WITH'; }
<hive>'YEAR'                               { return '<hive>YEAR'; }

<hive>'.'                                  { return '<hive>.'; }
<hive>'['                                  { return '<hive>['; }
<hive>']'                                  { return '<hive>]'; }

// Reserved Keywords
<impala>'ADD'                              { return '<impala>ADD'; }
<impala>'AGGREGATE'                        { return '<impala>AGGREGATE'; }
<impala>'ALLOCATE'                         { return '<impala>ALLOCATE'; }
<impala>'ANALYTIC'                         { return '<impala>ANALYTIC'; }
<impala>'ANTI'                             { return '<impala>ANTI'; }
<impala>'ANY'                              { return '<impala>ANY'; }
<impala>'ARE'                              { return '<impala>ARE'; }
<impala>'ARRAY_AGG'                        { return '<impala>ARRAY_AGG'; }
<impala>'ARRAY_MAX_CARDINALITY'            { return '<impala>ARRAY_MAX_CARDINALITY'; }
<impala>'ASENSITIVE'                       { return '<impala>ASENSITIVE'; }
<impala>'ASYMMETRIC'                       { return '<impala>ASYMMETRIC'; }
<impala>'AT'                               { return '<impala>AT'; }
<impala>'ATOMIC'                           { return '<impala>ATOMIC'; }
<impala>'AUTHORIZATION'                    { return '<impala>AUTHORIZATION'; }
<impala>'AVRO'                             { return '<impala>AVRO'; }
<impala>'BEGIN_FRAME'                      { return '<impala>BEGIN_FRAME'; }
<impala>'BEGIN_PARTITION'                  { return '<impala>BEGIN_PARTITION'; }
<impala>'BLOB'                             { return '<impala>BLOB'; }
<impala>'BLOCK_SIZE'                       { return '<impala>BLOCK_SIZE'; }
<impala>'BOTH'                             { return '<impala>BOTH'; }
<impala>'CACHED'                           { return '<impala>CACHED'; }
<impala>'CALLED'                           { return '<impala>CALLED'; }
<impala>'CARDINALITY'                      { return '<impala>CARDINALITY'; }
<impala>'CASCADE'                          { return '<impala>CASCADE'; }
<impala>'CASCADED'                         { return '<impala>CASCADED'; }
<impala>'CHANGE'                           { return '<impala>CHANGE'; }
<impala>'CHARACTER'                        { return '<impala>CHARACTER'; }
<impala>'CLOB'                             { return '<impala>CLOB'; }
<impala>'CLOSE_FN'                         { return '<impala>CLOSE_FN'; }
<impala>'COLLATE'                          { return '<impala>COLLATE'; }
<impala>'COLLECT'                          { return '<impala>COLLECT'; }
<impala>'COLUMN'                           { return '<impala>COLUMN'; }
<impala>'COLUMNS'                          { return '<impala>COLUMNS'; }
<impala>'COMMENT'                          { parser.determineCase(yytext); return '<impala>COMMENT'; }
<impala>'COMMIT'                           { return '<impala>COMMIT'; }
<impala>'COMPRESSION'                      { return '<impala>COMPRESSION'; }
<impala>'COMPUTE'                          { parser.determineCase(yytext); return '<impala>COMPUTE'; }
<impala>'CONDITION'                        { return '<impala>CONDITION'; }
<impala>'CONNECT'                          { return '<impala>CONNECT'; }
<impala>'CONSTRAINT'                       { return '<impala>CONSTRAINT'; }
<impala>'CONTAINS'                         { return '<impala>CONTAINS'; }
<impala>'CONVERT'                          { return '<impala>CONVERT'; }
<impala>'COPY'                             { return '<impala>COPY'; }
<impala>'CORR'                             { return '<impala>CORR'; }
<impala>'CORRESPONDING'                    { return '<impala>CORRESPONDING'; }
<impala>'COVAR_POP'                        { return '<impala>COVAR_POP'; }
<impala>'COVAR_SAMP'                       { return '<impala>COVAR_SAMP'; }
<impala>'CREATE'                           { parser.determineCase(yytext); parser.addStatementTypeLocation('CREATE', yylloc, yy.lexer.upcomingInput()); return '<impala>CREATE'; }
<impala>'CUBE'                             { return '<impala>CUBE'; }
<impala>'CURRENT'                          { return '<impala>CURRENT'; }
<impala>'CURRENT_DATE'                     { return '<impala>CURRENT_DATE'; }
<impala>'CURRENT_DEFAULT_TRANSFORM_GROUP'  { return '<impala>CURRENT_DEFAULT_TRANSFORM_GROUP'; }
<impala>'CURRENT_PATH'                     { return '<impala>CURRENT_PATH'; }
<impala>'CURRENT_ROLE'                     { return '<impala>CURRENT_ROLE'; }
<impala>'CURRENT_ROW'                      { return '<impala>CURRENT_ROW'; }
<impala>'CURRENT_SCHEMA'                   { return '<impala>CURRENT_SCHEMA'; }
<impala>'CURRENT_TIME'                     { return '<impala>CURRENT_TIME'; }
<impala>'CURRENT_TRANSFORM_GROUP_FOR_TYPE' { return '<impala>CURRENT_TRANSFORM_GROUP_FOR_TYPE'; }
<impala>'CURSOR'                           { return '<impala>CURSOR'; }
<impala>'CYCLE'                            { return '<impala>CYCLE'; }
<impala>'DATA'                             { return '<impala>DATA'; }
<impala>'DATABASES'                        { return '<impala>DATABASES'; }
<impala>'DEALLOCATE'                       { return '<impala>DEALLOCATE'; }
<impala>'DEC'                              { return '<impala>DEC'; }
<impala>'DECFLOAT'                         { return '<impala>DECFLOAT'; }
<impala>'DECLARE'                          { return '<impala>DECLARE'; }
<impala>'DEFINE'                           { return '<impala>DEFINE'; }
<impala>'DELETE'                           { return '<impala>DELETE'; }
<impala>'DELIMITED'                        { return '<impala>DELIMITED'; }
<impala>'DEREF'                            { return '<impala>DEREF'; }
<impala>'DESCRIBE'                         { parser.determineCase(yytext); parser.addStatementTypeLocation('DESCRIBE', yylloc); return '<impala>DESCRIBE'; }
<impala>'DETERMINISTIC'                    { return '<impala>DETERMINISTIC'; }
<impala>'DISCONNECT'                       { return '<impala>DISCONNECT'; }
<impala>'DYNAMIC'                          { return '<impala>DYNAMIC'; }
<impala>'EACH'                             { return '<impala>EACH'; }
<impala>'ELEMENT'                          { return '<impala>ELEMENT'; }
<impala>'EMPTY'                            { return '<impala>EMPTY'; }
<impala>'ENCODING'                         { return '<impala>ENCODING'; }
<impala>'END_FRAME'                        { return '<impala>END_FRAME'; }
<impala>'END_PARTITION'                    { return '<impala>END_PARTITION'; }
<impala>'EQUALS'                           { return '<impala>EQUALS'; }
<impala>'ESCAPE'                           { return '<impala>ESCAPE'; }
<impala>'ESCAPED'                          { return '<impala>ESCAPED'; }
<impala>'EVERY'                            { return '<impala>EVERY'; }
<impala>'EXCEPT'                           { return '<impala>EXCEPT'; }
<impala>'EXEC'                             { return '<impala>EXEC'; }
<impala>'EXECUTE'                          { return '<impala>EXECUTE'; }
<impala>'EXPLAIN'                          { parser.determineCase(yytext); parser.addStatementTypeLocation('EXPLAIN', yylloc); return '<impala>EXPLAIN'; }
<impala>'EXTENDED'                         { return '<impala>EXTENDED'; }
<impala>'EXTERNAL'                         { return '<impala>EXTERNAL'; }
<impala>'FETCH'                            { return '<impala>FETCH'; }
<impala>'FIELDS'                           { return '<impala>FIELDS'; }
<impala>'FILEFORMAT'                       { return '<impala>FILEFORMAT'; }
<impala>'FILES'                            { return '<impala>FILES'; }
<impala>'FILTER'                           { return '<impala>FILTER'; }
<impala>'FINALIZE_FN'                      { return '<impala>FINALIZE_FN'; }
<impala>'FIRST'                            { return '<impala>FIRST'; }
<impala>'FOR'                              { return '<impala>FOR'; }
<impala>'FOREIGN'                          { return '<impala>FOREIGN'; }
<impala>'FORMAT'                           { return '<impala>FORMAT'; }
<impala>'FORMATTED'                        { return '<impala>FORMATTED'; }
<impala>'FRAME_ROW'                        { return '<impala>FRAME_ROW'; }
<impala>'FREE'                             { return '<impala>FREE'; }
<impala>'FUNCTION'                         { return '<impala>FUNCTION'; }
<impala>'FUNCTIONS'                        { return '<impala>FUNCTIONS'; }
<impala>'FUSION'                           { return '<impala>FUSION'; }
<impala>'GET'                              { return '<impala>GET'; }
<impala>'GLOBAL'                           { return '<impala>GLOBAL'; }
<impala>'GRANT'                            { parser.determineCase(yytext); parser.addStatementTypeLocation('GRANT', yylloc); return '<impala>GRANT'; }
<impala>'GROUP'                            { return '<impala>GROUP'; }
<impala>'GROUPING'                         { return '<impala>GROUPING'; }
<impala>'GROUPS'                           { return '<impala>GROUPS'; }
<impala>'HASH'                             { return '<impala>HASH'; }
<impala>'HOLD'                             { return '<impala>HOLD'; }
<impala>'IGNORE'                           { return '<impala>IGNORE'; }
<impala>'ILIKE'                            { return '<impala>ILIKE'; }
<impala>'INCREMENTAL'                      { return '<impala>INCREMENTAL'; }
<impala>'INDICATOR'                        { return '<impala>INDICATOR'; }
<impala>'INIT_FN'                          { return '<impala>INIT_FN'; }
<impala>'INITIAL'                          { return '<impala>INITIAL'; }
<impala>'INOUT'                            { return '<impala>INOUT'; }
<impala>'INPATH'                           { this.begin('hdfs'); return '<impala>INPATH'; }
<impala>'INSENSITIVE'                      { return '<impala>INSENSITIVE'; }
<impala>'INSERT'                           { parser.determineCase(yytext); parser.addStatementTypeLocation('INSERT', yylloc); return '<impala>INSERT'; }
<impala>'INTERMEDIATE'                     { return '<impala>INTERMEDIATE'; }
<impala>'INTERSECT'                        { return '<impala>INTERSECT'; }
<impala>'INTERSECTION'                     { return '<impala>INTERSECTION'; }
<impala>'INTERVAL'                         { return '<impala>INTERVAL'; }
<impala>'INVALIDATE'                       { parser.determineCase(yytext); parser.addStatementTypeLocation('INVALIDATE', yylloc, yy.lexer.upcomingInput()); return '<impala>INVALIDATE'; }
<impala>'IREGEXP'                          { return '<impala>IREGEXP'; }
<impala>'JSON_ARRAY'                       { return '<impala>JSON_ARRAY'; }
<impala>'JSON_ARRAYAGG'                    { return '<impala>JSON_ARRAYAGG'; }
<impala>'JSON_EXISTS'                      { return '<impala>JSON_EXISTS'; }
<impala>'JSON_OBJECT'                      { return '<impala>JSON_OBJECT'; }
<impala>'JSON_OBJECTAGG'                   { return '<impala>JSON_OBJECTAGG'; }
<impala>'JSON_QUERY'                       { return '<impala>JSON_QUERY'; }
<impala>'JSON_TABLE'                       { return '<impala>JSON_TABLE'; }
<impala>'JSON_TABLE_PRIMITIVE'             { return '<impala>JSON_TABLE_PRIMITIVE'; }
<impala>'JSON_VALUE'                       { return '<impala>JSON_VALUE'; }
<impala>'KEY'                              { return '<impala>KEY'; }
<impala>'KUDU'                             { return '<impala>KUDU'; }
<impala>'LARGE'                            { return '<impala>LARGE'; }
<impala>'LAST'                             { return '<impala>LAST'; }
<impala>'LATERAL'                          { return '<impala>LATERAL'; }
<impala>'LEADING'                          { return '<impala>LEADING'; }
<impala>LIKE\s+PARQUET                     { this.begin('hdfs'); return '<impala>LIKE_PARQUET'; }
<impala>'LIKE_REGEX'                       { return '<impala>LIKE_REGEX'; }
<impala>'LIMIT'                            { return '<impala>LIMIT'; }
<impala>'LINES'                            { return '<impala>LINES'; }
<impala>'LISTAGG'                          { return '<impala>LISTAGG'; }
<impala>'LOAD'                             { parser.determineCase(yytext); parser.addStatementTypeLocation('LOAD', yylloc, yy.lexer.upcomingInput()); return '<impala>LOAD'; }
<impala>'LOCAL'                            { return '<impala>LOCAL'; }
<impala>'LOCALTIMESTAMP'                   { return '<impala>LOCALTIMESTAMP'; }
<impala>'LOCATION'                         { this.begin('hdfs'); return '<impala>LOCATION'; }
<impala>'MATCH'                            { return '<impala>MATCH'; }
<impala>'MATCH_NUMBER'                     { return '<impala>MATCH_NUMBER'; }
<impala>'MATCH_RECOGNIZE'                  { return '<impala>MATCH_RECOGNIZE'; }
<impala>'MATCHES'                          { return '<impala>MATCHES'; }
<impala>'MERGE'                            { return '<impala>MERGE'; }
<impala>'MERGE_FN'                         { return '<impala>MERGE_FN'; }
<impala>'METADATA'                         { return '<impala>METADATA'; }
<impala>'METHOD'                           { return '<impala>METHOD'; }
<impala>'MODIFIES'                         { return '<impala>MODIFIES'; }
<impala>'MULTISET'                         { return '<impala>MULTISET'; }
<impala>'NATIONAL'                         { return '<impala>NATIONAL'; }
<impala>'NATURAL'                          { return '<impala>NATURAL'; }
<impala>'NCHAR'                            { return '<impala>NCHAR'; }
<impala>'NCLOB'                            { return '<impala>NCLOB'; }
<impala>'NO'                               { return '<impala>NO'; }
<impala>'NONE'                             { return '<impala>NONE'; }
<impala>'NORMALIZE'                        { return '<impala>NORMALIZE'; }
<impala>'NTH_VALUE'                        { return '<impala>NTH_VALUE'; }
<impala>'NULLS'                            { return '<impala>NULLS'; }
<impala>'NUMERIC'                          { return '<impala>NUMERIC'; }
<impala>'OCCURRENCES_REGEX'                { return '<impala>OCCURRENCES_REGEX'; }
<impala>'OCTET_LENGTH'                     { return '<impala>OCTET_LENGTH'; }
<impala>'OF'                               { return '<impala>OF'; }
<impala>'OFFSET'                           { return '<impala>OFFSET'; }
<impala>'OMIT'                             { return '<impala>OMIT'; }
<impala>'ONE'                              { return '<impala>ONE'; }
<impala>'ONLY'                             { return '<impala>ONLY'; }
<impala>'ORC'                              { return '<impala>ORC'; }
<impala>'OUT'                              { return '<impala>OUT'; }
<impala>'OVER'                             { return '<impala>OVER'; }
<impala>'OVERLAPS'                         { return '<impala>OVERLAPS'; }
<impala>'OVERLAY'                          { return '<impala>OVERLAY'; }
<impala>'OVERWRITE'                        { return '<impala>OVERWRITE'; }
<impala>'PARQUET'                          { return '<impala>PARQUET'; }
<impala>PARTITION\s+VALUE\s                { return '<impala>PARTITION_VALUE'; }
<impala>'PARTITIONED'                      { return '<impala>PARTITIONED'; }
<impala>'PARTITIONS'                       { return '<impala>PARTITIONS'; }
<impala>'PATTERN'                          { return '<impala>PATTERN'; }
<impala>'PER'                              { return '<impala>PER'; }
<impala>'PERCENT'                          { return '<impala>PERCENT'; }
<impala>'PERCENTILE_CONT'                  { return '<impala>PERCENTILE_CONT'; }
<impala>'PERCENTILE_DISC'                  { return '<impala>PERCENTILE_DISC'; }
<impala>'PORTION'                          { return '<impala>PORTION'; }
<impala>'POSITION'                         { return '<impala>POSITION'; }
<impala>'POSITION_REGEX'                   { return '<impala>POSITION_REGEX'; }
<impala>'PRECEDES'                         { return '<impala>PRECEDES'; }
<impala>'PREPARE'                          { return '<impala>PREPARE'; }
<impala>'PREPARE_FN'                       { return '<impala>PREPARE_FN'; }
<impala>'PRIMARY'                          { return '<impala>PRIMARY'; }
<impala>'PROCEDURE'                        { return '<impala>PROCEDURE'; }
<impala>'PTF'                              { return '<impala>PTF'; }
<impala>'RANGE'                            { return '<impala>RANGE'; }
<impala>'RCFILE'                           { return '<impala>RCFILE'; }
<impala>'READS'                            { return '<impala>READS'; }
<impala>'REAL'                             { return '<impala>REAL'; }
<impala>'RECOVER'                          { return '<impala>RECOVER'; }
<impala>'RECURSIVE'                        { return '<impala>RECURSIVE'; }
<impala>'REF'                              { return '<impala>REF'; }
<impala>'REFERENCES'                       { return '<impala>REFERENCES'; }
<impala>'REFERENCING'                      { return '<impala>REFERENCING'; }
<impala>'REFRESH'                          { parser.determineCase(yytext); parser.addStatementTypeLocation('REFRESH', yylloc); return '<impala>REFRESH'; }
<impala>'REGR_AVGX'                        { return '<impala>REGR_AVGX'; }
<impala>'REGR_AVGY'                        { return '<impala>REGR_AVGY'; }
<impala>'REGR_COUNT'                       { return '<impala>REGR_COUNT'; }
<impala>'REGR_INTERCEPT'                   { return '<impala>REGR_INTERCEPT'; }
<impala>'REGR_R2REGR_SLOPE'                { return '<impala>REGR_R2REGR_SLOPE'; }
<impala>'REGR_SXX'                         { return '<impala>REGR_SXX'; }
<impala>'REGR_SXY'                         { return '<impala>REGR_SXY'; }
<impala>'REGR_SYY'                         { return '<impala>REGR_SYY'; }
<impala>'RELEASE'                          { return '<impala>RELEASE'; }
<impala>'RENAME'                           { return '<impala>RENAME'; }
<impala>'REPEATABLE'                       { return '<impala>REPEATABLE'; }
<impala>'REPLACE'                          { return '<impala>REPLACE'; }
<impala>'REPLICATION'                      { return '<impala>REPLICATION'; }
<impala>'RESTRICT'                         { return '<impala>RESTRICT'; }
<impala>'RETURNS'                          { return '<impala>RETURNS'; }
<impala>'REVOKE'                           { parser.determineCase(yytext); parser.addStatementTypeLocation('REVOKE', yylloc); return '<impala>REVOKE'; }
<impala>'ROLE'                             { return '<impala>ROLE'; }
<impala>'ROLES'                            { return '<impala>ROLES'; }
<impala>'ROLLBACK'                         { return '<impala>ROLLBACK'; }
<impala>'ROLLUP'                           { return '<impala>ROLLUP'; }
<impala>'RUNNING'                          { return '<impala>RUNNING'; }
<impala>'SAVEPOINT'                        { return '<impala>SAVEPOINT'; }
<impala>'SCHEMAS'                          { return '<impala>SCHEMAS'; }
<impala>'SCOPE'                            { return '<impala>SCOPE'; }
<impala>'SCROLL'                           { return '<impala>SCROLL'; }
<impala>'SEARCH'                           { return '<impala>SEARCH'; }
<impala>'SEEK'                             { return '<impala>SEEK'; }
<impala>'SENSITIVE'                        { return '<impala>SENSITIVE'; }
<impala>'SEQUENCEFILE'                     { return '<impala>SEQUENCEFILE'; }
<impala>'SERDEPROPERTIES'                  { return '<impala>SERDEPROPERTIES'; }
<impala>'SERIALIZE_FN'                     { return '<impala>SERIALIZE_FN'; }
<impala>'SERVER'                           { return '<impala>SERVER'; }
<impala>'SIMILAR'                          { return '<impala>SIMILAR'; }
<impala>'SKIP'                             { return '<impala>SKIP'; }
<impala>'SOME'                             { return '<impala>SOME'; }
<impala>'SORT'                             { return '<impala>SORT'; }
<impala>'SPECIFIC'                         { return '<impala>SPECIFIC'; }
<impala>'SPECIFICTYPE'                     { return '<impala>SPECIFICTYPE'; }
<impala>'SQLEXCEPTION'                     { return '<impala>SQLEXCEPTION'; }
<impala>'SQLSTATE'                         { return '<impala>SQLSTATE'; }
<impala>'SQLWARNING'                       { return '<impala>SQLWARNING'; }
<impala>'STATIC'                           { return '<impala>STATIC'; }
<impala>'STATS'                            { return '<impala>STATS'; }
<impala>'STORED'                           { return '<impala>STORED'; }
<impala>'STRAIGHT_JOIN'                    { return '<impala>STRAIGHT_JOIN'; }
<impala>'SUBMULTISET'                      { return '<impala>SUBMULTISET'; }
<impala>'SUBSET'                           { return '<impala>SUBSET'; }
<impala>'SUBSTRING_REGEX'                  { return '<impala>SUBSTRING_REGEX'; }
<impala>'SUCCEEDS'                         { return '<impala>SUCCEEDS'; }
<impala>'SYMBOL'                           { return '<impala>SYMBOL'; }
<impala>'SYMMETRIC'                        { return '<impala>SYMMETRIC'; }
<impala>'SYSTEM_TIME'                      { return '<impala>SYSTEM_TIME'; }
<impala>'SYSTEM_USER'                      { return '<impala>SYSTEM_USER'; }
<impala>'TABLE'                            { return '<impala>TABLE'; }
<impala>'TABLES'                           { return '<impala>TABLES'; }
<impala>'TABLESAMPLE'                      { return '<impala>TABLESAMPLE'; }
<impala>'TBLPROPERTIES'                    { return '<impala>TBLPROPERTIES'; }
<impala>'TERMINATED'                       { return '<impala>TERMINATED'; }
<impala>'TEXTFILE'                         { return '<impala>TEXTFILE'; }
<impala>'TIMEZONE_HOUR'                    { return '<impala>TIMEZONE_HOUR'; }
<impala>'TIMEZONE_MINUTE'                  { return '<impala>TIMEZONE_MINUTE'; }
<impala>'TRAILING'                         { return '<impala>TRAILING'; }
<impala>'TRANSLATE_REGEX'                  { return '<impala>TRANSLATE_REGEX'; }
<impala>'TRANSLATION'                      { return '<impala>TRANSLATION'; }
<impala>'TREAT'                            { return '<impala>TREAT'; }
<impala>'TRIGGER'                          { return '<impala>TRIGGER'; }
<impala>'TRIM_ARRAY'                       { return '<impala>TRIM_ARRAY'; }
<impala>'UESCAPE'                          { return '<impala>UESCAPE'; }
<impala>'UNCACHED'                         { return '<impala>UNCACHED'; }
<impala>'UNIQUE'                           { return '<impala>UNIQUE'; }
<impala>'UNKNOWN'                          { return '<impala>UNKNOWN'; }
<impala>'UNNEST'                           { return '<impala>UNNEST'; }
<impala>'UPDATE_FN'                        { return '<impala>UPDATE_FN'; }
<impala>'UPSERT'                           { parser.determineCase(yytext); parser.addStatementTypeLocation('UPSERT', yylloc); return '<impala>UPSERT'; }
<impala>'URI'                              { return '<impala>URI'; }
<impala>'USER'                             { return '<impala>USER'; }
<impala>'USING'                            { return '<impala>USING'; }
<impala>'VALUE_OF'                         { return '<impala>VALUE_OF'; }
<impala>'VARBINARY'                        { return '<impala>VARBINARY'; }
<impala>'VARCHAR'                          { return '<impala>VARCHAR'; }
<impala>'VARYING'                          { return '<impala>VARYING'; }
<impala>'VERSIONING'                       { return '<impala>VERSIONING'; }
<impala>'WHENEVER'                         { return '<impala>WHENEVER'; }
<impala>'WIDTH_BUCKET'                     { return '<impala>WIDTH_BUCKET'; }
<impala>'WINDOW'                           { return '<impala>WINDOW'; }
<impala>'WITH'                             { parser.determineCase(yytext); parser.addStatementTypeLocation('WITH', yylloc); return '<impala>WITH'; }
<impala>'WITHIN'                           { return '<impala>WITHIN'; }
<impala>'WITHOUT'                          { return '<impala>WITHOUT'; }

// Non-reserved Keywords
<impala>'ARRAY'                            { return 'ARRAY'; }
<impala>'DEFAULT'                          { return '<impala>DEFAULT'; }
<impala>'MAP'                              { return 'MAP'; }
<impala>'OWNER'                            { return '<impala>OWNER'; }
<impala>'STRUCT'                           { return 'STRUCT'; }
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
'ALTER'                                    { parser.determineCase(yytext); parser.addStatementTypeLocation('ALTER', yylloc, yy.lexer.upcomingInput()); return 'ALTER'; }
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
'CROSS'                                    { return 'CROSS'; }
'CURRENT'                                  { return 'CURRENT'; }
'DATABASE'                                 { return 'DATABASE'; }
'DECIMAL'                                  { return 'DECIMAL'; }
'DISTINCT'                                 { return 'DISTINCT'; }
'DIV'                                      { return 'ARITHMETIC_OPERATOR'; }
'DOUBLE'                                   { return 'DOUBLE'; }
'DESC'                                     { return 'DESC'; }
'DROP'                                     { parser.determineCase(yytext); parser.addStatementTypeLocation('DROP', yylloc, yy.lexer.upcomingInput()); return 'DROP'; }
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
'PURGE'                                    { return 'PURGE'; }
'RANGE'                                    { return 'RANGE'; }
'REGEXP'                                   { return 'REGEXP'; }
'RIGHT'                                    { return 'RIGHT'; }
'RLIKE'                                    { return 'RLIKE'; }
'ROW'                                      { return 'ROW'; }
'ROWS'                                     { return 'ROWS'; }
'SCHEMA'                                   { return 'SCHEMA'; }
'SELECT'                                   { parser.determineCase(yytext); parser.addStatementTypeLocation('SELECT', yylloc); return 'SELECT'; }
'SEMI'                                     { return 'SEMI'; }
'SET'                                      { parser.determineCase(yytext); parser.addStatementTypeLocation('SET', yylloc); return 'SET'; }
'SHOW'                                     { parser.determineCase(yytext); parser.addStatementTypeLocation('SHOW', yylloc); return 'SHOW'; }
'SMALLINT'                                 { return 'SMALLINT'; }
'STRING'                                   { return 'STRING'; }
'TABLE'                                    { return 'TABLE'; }
'THEN'                                     { return 'THEN'; }
'TIMESTAMP'                                { return 'TIMESTAMP'; }
'TINYINT'                                  { return 'TINYINT'; }
'TO'                                       { return 'TO'; }
'TRUE'                                     { return 'TRUE'; }
'TRUNCATE'                                 { parser.determineCase(yytext); parser.addStatementTypeLocation('TRUNCATE', yylloc, yy.lexer.upcomingInput()); return 'TRUNCATE'; }
'UNBOUNDED'                                { return 'UNBOUNDED'; }
'UPDATE'                                   { parser.determineCase(yytext); return 'UPDATE'; }
'USE'                                      { parser.determineCase(yytext); parser.addStatementTypeLocation('USE', yylloc); return 'USE'; }
'UNION'                                    { return 'UNION'; }
'VIEW'                                     { return 'VIEW'; }
'VARCHAR'                                  { return 'VARCHAR'; } // Not in Impala
'VALUES'                                   { return 'VALUES'; }
'WHEN'                                     { return 'WHEN'; }
'WHERE'                                    { return 'WHERE'; }
'WITH'                                     { parser.determineCase(yytext); parser.addStatementTypeLocation('WITH', yylloc); return 'WITH'; }

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
<hive>EXTRACT\s*\(                         { yy.lexer.unput('('); yytext = 'extract'; parser.addFunctionLocation(yylloc, yytext); return '<hive>EXTRACT'; }
<hive>HISTOGRAM_NUMERIC\s*\(               { yy.lexer.unput('('); yytext = 'histogram_numeric'; parser.addFunctionLocation(yylloc, yytext); return '<hive>HISTOGRAM_NUMERIC'; }
<hive>NTILE\s*\(                           { yy.lexer.unput('('); yytext = 'ntile'; parser.addFunctionLocation(yylloc, yytext); return '<hive>NTILE'; }
<hive>PERCENTILE\s*\(                      { yy.lexer.unput('('); yytext = 'percentile'; parser.addFunctionLocation(yylloc, yytext); return '<hive>PERCENTILE'; }
<hive>PERCENTILE_APPROX\s*\(               { yy.lexer.unput('('); yytext = 'percentile_approx'; parser.addFunctionLocation(yylloc, yytext); return '<hive>PERCENTILE_APPROX'; }
<impala>APPX_MEDIAN\s*\(                   { yy.lexer.unput('('); yytext = 'appx_median'; parser.addFunctionLocation(yylloc, yytext); return '<impala>APPX_MEDIAN'; }
<impala>EXTRACT\s*\(                       { yy.lexer.unput('('); yytext = 'extract'; parser.addFunctionLocation(yylloc, yytext); return '<impala>EXTRACT'; }
<impala>GROUP_CONCAT\s*\(                  { yy.lexer.unput('('); yytext = 'group_concat'; parser.addFunctionLocation(yylloc, yytext); return '<impala>GROUP_CONCAT'; }
<impala>NDV\s*\(                           { yy.lexer.unput('('); yytext = 'ndv'; parser.addFunctionLocation(yylloc, yytext); return '<impala>NDV'; }
<impala>STDDEV\s*\(                        { yy.lexer.unput('('); yytext = 'stddev'; parser.addFunctionLocation(yylloc, yytext); return '<impala>STDDEV'; }
<impala>VARIANCE_POP\s*\(                  { yy.lexer.unput('('); yytext = 'variance_pop'; parser.addFunctionLocation(yylloc, yytext); return '<impala>VARIANCE_POP'; }
<impala>VARIANCE_SAMP\s*\(                 { yy.lexer.unput('('); yytext = 'variance_samp'; parser.addFunctionLocation(yylloc, yytext); return '<impala>VARIANCE_SAMP'; }

// Analytical functions
CUME_DIST\s*\(                             { yy.lexer.unput('('); yytext = 'cume_dist'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
DENSE_RANK\s*\(                            { yy.lexer.unput('('); yytext = 'dense_rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
FIRST_VALUE\s*\(                           { yy.lexer.unput('('); yytext = 'first_value'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LAG\s*\(                                   { yy.lexer.unput('('); yytext = 'lag'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LAST_VALUE\s*\(                            { yy.lexer.unput('('); yytext = 'last_value'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LEAD\s*\(                                  { yy.lexer.unput('('); yytext = 'lead'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
RANK\s*\(                                  { yy.lexer.unput('('); yytext = 'rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
ROW_NUMBER\s*\(                            { yy.lexer.unput('('); yytext = 'row_number'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
<hive>CUME_DIST\s*\(                       { yy.lexer.unput('('); yytext = 'cume_dist'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
<hive>PERCENT_RANK\s*\(                    { yy.lexer.unput('('); yytext = 'percent_rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
<impala>NTILE\s*\(                         { yy.lexer.unput('('); yytext = 'ntile'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
<impala>PERCENT_RANK\s*\(                  { yy.lexer.unput('('); yytext = 'percent_rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }

<impala>SYSTEM\s*\(                        { yy.lexer.unput('('); yytext = 'system'; return '<impala>SYSTEM'; }

[0-9]+                                     { return 'UNSIGNED_INTEGER'; }
[0-9]+(?:[YSL]|BD)?                        { return 'UNSIGNED_INTEGER'; }
[0-9]+E                                    { return 'UNSIGNED_INTEGER_E'; }
[A-Za-z0-9_]+                              { return 'REGULAR_IDENTIFIER'; }

<hdfs>'\u2020'                             { parser.yy.cursorFound = true; return 'CURSOR'; }
<hdfs>'\u2021'                             { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }
<hdfs>\s+[']                               { return 'HDFS_START_QUOTE'; }
<hdfs>[^'\u2020\u2021]+                    { parser.addFileLocation(yylloc, yytext); return 'HDFS_PATH'; }
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
<hive>.                                    { }
<impala>.                                  { }
<hdfs>.                                    { }
<backtickedValue>.                         { }
<singleQuotedValue>.                       { }
<doubleQuotedValue>.                       { }