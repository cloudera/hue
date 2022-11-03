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
%x hdfs sparkfile doubleQuotedValue singleQuotedValue backtickedValue
%%

\s                                         { /* skip whitespace */ }
'--'.*                                     { /* skip comments */ }
[/][*][^*]*[*]+([^/*][^*]*[*]+)*[/]        { /* skip comments */ }

'\u2020'                                   { parser.yy.partialCursor = false; parser.yy.cursorFound = yylloc; return 'CURSOR'; }
'\u2021'                                   { parser.yy.partialCursor = true; parser.yy.cursorFound = yylloc; return 'PARTIAL_CURSOR'; }

<between>'AND'                             { this.popState(); return 'BETWEEN_AND'; }

// Reserved Keywords
'ALL'                                      { return 'ALL'; }
'AND'                                      { return 'AND'; }
'AS'                                       { return 'AS'; }
'ASC'                                      { return 'ASC'; }
'BIGINT'                                   { return 'BIGINT'; }
'BY'                                       { return 'BY'; }
'CASE'                                     { return 'CASE'; }
'COLUMN'                                   { return 'COLUMN'; }
'COLUMNS'                                  { return 'COLUMNS'; }
'CROSS'                                    { return 'CROSS'; }
'DATABASE'                                 { return 'DATABASE'; }
'DESC'                                     { parser.determineCase(yytext); return 'DESC'; }
'DIRECTORY'                                { return 'DIRECTORY'; }
'DISTINCT'                                 { return 'DISTINCT'; }
'EXTENDED'                                 { return 'EXTENDED'; }
'FUNCTION'                                 { return 'FUNCTION'; }
'ELSE'                                     { return 'ELSE'; }
'END'                                      { return 'END'; }
'EXISTS'                                   { parser.yy.correlatedSubQuery = true; return 'EXISTS'; }
'FALSE'                                    { return 'FALSE'; }
'FROM'                                     { parser.determineCase(yytext); return 'FROM'; }
'FULL'                                     { return 'FULL'; }
'GROUP'                                    { return 'GROUP'; }
'HAVING'                                   { return 'HAVING'; }
'IF'                                       { return 'IF'; }
'IN'                                       { return 'IN'; }
'INTO'                                     { return 'INTO'; }
'JOIN'                                     { return 'JOIN'; }
'LEFT'                                     { return 'LEFT'; }
'LIKE'                                     { return 'LIKE'; }
'LIMIT'                                    { return 'LIMIT'; }
'LOCAL'                                    { return 'LOCAL'; }
'NOT'                                      { return 'NOT'; }
'NULL'                                     { return 'NULL'; }
'ON'                                       { return 'ON'; }
'OPTION'                                   { return 'OPTION'; }
'OR'                                       { return 'OR'; }
'ORDER'                                    { return 'ORDER'; }
'OUTER'                                    { return 'OUTER'; }
'PARTITION'                                { return 'PARTITION'; }
'REGEXP'                                   { return 'REGEXP'; }
'RIGHT'                                    { return 'RIGHT'; }
'RLIKE'                                    { return 'RLIKE'; }
'ROLE'                                     { return 'ROLE'; }
'SELECT'                                   { parser.determineCase(yytext); parser.addStatementTypeLocation('SELECT', yylloc); return 'SELECT'; }
'SEMI'                                     { return 'SEMI'; }
'TABLE'                                    { return 'TABLE'; }
'THEN'                                     { return 'THEN'; }
'TRUE'                                     { return 'TRUE'; }
'TRUNCATE'                                 { parser.determineCase(yytext); parser.addStatementTypeLocation('TRUNCATE', yylloc, yy.lexer.upcomingInput()); return 'TRUNCATE'; }
'UNION'                                    { return 'UNION'; }
'WHEN'                                     { return 'WHEN'; }
'WHERE'                                    { return 'WHERE'; }
'WITH'                                     { parser.determineCase(yytext); parser.addStatementTypeLocation('WITH', yylloc); return 'WITH'; }
'MAP'                                      { return 'MAP'; }
'OVERWRITE'                                { return 'OVERWRITE'; }
'QUERY'                                    { return 'QUERY'; }
'USER'                                     { return 'USER'; }

// Non-reserved Keywords
'ADD'                                      { parser.determineCase(yytext); return 'ADD'; }
'ALTER'                                    { parser.determineCase(yytext); parser.addStatementTypeLocation('ALTER', yylloc, yy.lexer.upcomingInput()); return 'ALTER'; }
'ANALYZE'                                  { parser.determineCase(yytext); return 'ANALYZE'; }
'ARCHIVE'                                  { return 'ARCHIVE'; }
'BETWEEN'                                  { this.begin('between'); return 'BETWEEN'; }
'BINARY'                                   { return 'BINARY'; }
'BOOLEAN'                                  { return 'BOOLEAN'; }
'BUCKETS'                                  { return 'BUCKETS'; }
'BYTE'                                     { return 'BYTE'; }
'CACHE'                                    { parser.determineCase(yytext); return 'CACHE'; }
'CASCADE'                                  { return 'CASCADE'; }
'CHANGE'                                   { return 'CHANGE'; }
'CHAR'                                     { return 'CHAR'; }
'CLEAR'                                    { parser.determineCase(yytext); return 'CLEAR'; }
'CLUSTERED'                                { return 'CLUSTERED'; }
'COLLECTION'                               { return 'COLLECTION'; }
'COMMENT'                                  { return 'COMMENT'; }
'COMPUTE'                                  { return 'COMPUTE'; }
'CREATE'                                   { parser.determineCase(yytext); return 'CREATE'; }
'CSV'                                      { return 'CSV'; }
'CURRENT'                                  { return 'CURRENT'; }
'DATA'                                     { return 'DATA'; }
'DATABASES'                                { return 'DATABASES'; }
'DATE'                                     { return 'DATE'; }
'DAY'                                      { return 'DAY'; }
'DBPROPERTIES'                             { return 'DBPROPERTIES'; }
'DEC'                                      { return 'DEC'; }
'DECIMAL'                                  { return 'DECIMAL'; }
'DEFINED'                                  { return 'DEFINED'; }
'DELIMITED'                                { return 'DELIMITED'; }
'DESCRIBE'                                 { parser.determineCase(yytext); return 'DESCRIBE'; }
'DIV'                                      { return 'ARITHMETIC_OPERATOR'; }
'DOUBLE'                                   { return 'DOUBLE'; }
'DROP'                                     { parser.determineCase(yytext); parser.addStatementTypeLocation('DROP', yylloc, yy.lexer.upcomingInput()); return 'DROP'; }
'ESCAPED'                                  { return 'ESCAPED'; }
'EXTERNAL'                                 { return 'EXTERNAL'; }
'FIELDS'                                   { return 'FIELDS'; }
'FILE'                                     { return 'FILE'; }
'FILEFORMAT'                               { return 'FILEFORMAT'; }
'FLOAT'                                    { return 'FLOAT'; }
'FOLLOWING'                                { return 'FOLLOWING'; }
'FOR'                                      { return 'FOR'; }
'FORMAT'                                   { return 'FORMAT'; }
'FUNCTIONS'                                { return 'FUNCTIONS'; }
'GLOBAL'                                   { return 'GLOBAL'; }
'HOUR'                                     { return 'HOUR'; }
'INNER'                                    { return 'INNER'; }
'INPATH'                                   { this.begin('hdfs'); return 'INPATH'; }
'INSERT'                                   { parser.determineCase(yytext); return 'INSERT'; }
'INT'                                      { return 'INT'; }
'INTEGER'                                  { return 'INTEGER'; }
'INTERVAL'                                 { return 'INTERVAL'; }
'IS'                                       { return 'IS'; }
'ITEMS'                                    { return 'ITEMS'; }
'JAR'                                      { return 'JAR'; }
'JDBC'                                     { return 'JDBC'; }
'JSON'                                     { return 'JSON'; }
'KEYS'                                     { return 'KEYS'; }
'LAZY'                                     { return 'LAZY'; }
'LINES'                                    { return 'LINES'; }
'LIST'                                     { return 'LIST'; }
'LOAD'                                     { parser.determineCase(yytext); return 'LOAD'; }
'LOCATION'                                 { return 'LOCATION'; }
'LONG'                                     { return 'LONG'; }
'MINUTE'                                   { return 'MINUTE'; }
'MONTH'                                    { return 'MONTH'; }
'MSCK'                                     { return 'MSCK'; }
'NAMESPACE'                                { return 'NAMESPACE'; }
'NOSCAN'                                   { return 'NOSCAN'; }
'NUMERIC'                                  { return 'NUMERIC'; }
'OPTIONS'                                  { return 'OPTIONS'; }
'ORC'                                      { return 'ORC'; }
'OVER'                                     { return 'OVER'; }
'PARQUET'                                  { return 'PARQUET'; }
'PARTITIONED'                              { return 'PARTITIONED'; }
'PARTITIONS'                               { return 'PARTITIONS'; }
'PRECEDING'                                { return 'PRECEDING'; }
'PROPERTIES'                               { return 'PROPERTIES'; }
'PURGE'                                    { return 'PURGE'; }
'RANGE'                                    { return 'RANGE'; }
'REAL'                                     { return 'REAL'; }
'RECOVER'                                  { return 'RECOVER'; }
'REFRESH'                                  { parser.determineCase(yytext); return 'REFRESH'; }
'RENAME'                                   { return 'RENAME'; }
'REPAIR'                                   { return 'REPAIR'; }
'REPLACE'                                  { return 'REPLACE'; }
'RESET'                                    { parser.determineCase(yytext); return 'RESET'; }
'RESTRICT'                                 { return 'RESTRICT'; }
'ROLE'                                     { return 'ROLE'; }
'ROW'                                      { return 'ROW'; }
'ROWS'                                     { return 'ROWS'; }
'SCHEMA'                                   { return 'SCHEMA'; }
'SCHEMAS'                                  { return 'SCHEMAS'; }
'SECOND'                                   { return 'SECOND'; }
'SERDE'                                    { return 'SERDE'; }
'SERDEPROPERTIES'                          { return 'SERDEPROPERTIES'; }
'SET'                                      { parser.determineCase(yytext); parser.addStatementTypeLocation('SET', yylloc); return 'SET'; }
'SHORT'                                    { return 'SHORT'; }
'SHOW'                                     { parser.determineCase(yytext); parser.addStatementTypeLocation('SHOW', yylloc); return 'SHOW'; }
'SMALLINT'                                 { return 'SMALLINT'; }
'SORTED'                                   { return 'SORTED'; }
'STATISTICS'                               { return 'STATISTICS'; }
'STORED'                                   { return 'STORED'; }
'STRING'                                   { return 'STRING'; }
'SYNC'                                     { return 'SYNC'; }
'SYSTEM'                                   { return 'SYSTEM'; }
'TABLES'                                   { return 'TABLES'; }
'TBLPROPERTIES'                            { return 'TBLPROPERTIES'; }
'TEMPORARY'                                { return 'TEMPORARY'; }
'TERMINATED'                               { return 'TERMINATED'; }
'TEXTFILE'                                 { return 'TEXTFILE'; }
'TIMESTAMP'                                { return 'TIMESTAMP'; }
'TINYINT'                                  { return 'TINYINT'; }
'TO'                                       { return 'TO'; }
'TXT'                                      { return 'TXT'; }
'UNBOUNDED'                                { return 'UNBOUNDED'; }
'UNCACHE'                                  { return 'UNCACHE'; }
'UNSET'                                    { return 'UNSET'; }
'UPDATE'                                   { parser.determineCase(yytext); return 'UPDATE'; }
'USE'                                      { parser.determineCase(yytext); parser.addStatementTypeLocation('USE', yylloc); return 'USE'; }
'USING'                                    { return 'USING'; }
'VALUES'                                   { return 'VALUES'; }
'VARCHAR'                                  { return 'VARCHAR'; }
'VIEW'                                     { return 'VIEW'; }
'VIEWS'                                    { return 'VIEWS'; }
'YEAR'                                     { return 'YEAR'; }

// --- UDFs ---
AVG\s*\(                                   { yy.lexer.unput('('); yytext = 'avg'; parser.addFunctionLocation(yylloc, yytext); return 'AVG'; }
CAST\s*\(                                  { yy.lexer.unput('('); yytext = 'cast'; parser.addFunctionLocation(yylloc, yytext); return 'CAST'; }
COUNT\s*\(                                 { yy.lexer.unput('('); yytext = 'count'; parser.addFunctionLocation(yylloc, yytext); return 'COUNT'; }
MAX\s*\(                                   { yy.lexer.unput('('); yytext = 'max'; parser.addFunctionLocation(yylloc, yytext); return 'MAX'; }
MIN\s*\(                                   { yy.lexer.unput('('); yytext = 'min'; parser.addFunctionLocation(yylloc, yytext); return 'MIN'; }
STDDEV_POP\s*\(                            { yy.lexer.unput('('); yytext = 'stddev_pop'; parser.addFunctionLocation(yylloc, yytext); return 'STDDEV_POP'; }
STDDEV_SAMP\s*\(                           { yy.lexer.unput('('); yytext = 'stddev_samp'; parser.addFunctionLocation(yylloc, yytext); return 'STDDEV_SAMP'; }
SUM\s*\(                                   { yy.lexer.unput('('); yytext = 'sum'; parser.addFunctionLocation(yylloc, yytext); return 'SUM'; }
VAR_POP\s*\(                               { yy.lexer.unput('('); yytext = 'var_pop'; parser.addFunctionLocation(yylloc, yytext); return 'VAR_POP'; }
VAR_SAMP\s*\(                              { yy.lexer.unput('('); yytext = 'var_samp'; parser.addFunctionLocation(yylloc, yytext); return 'VAR_SAMP'; }
VARIANCE\s*\(                              { yy.lexer.unput('('); yytext = 'variance'; parser.addFunctionLocation(yylloc, yytext); return 'VARIANCE'; }

// Analytical functions
CUME_DIST\s*\(                             { yy.lexer.unput('('); yytext = 'cume_dist'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
DENSE_RANK\s*\(                            { yy.lexer.unput('('); yytext = 'dense_rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
FIRST_VALUE\s*\(                           { yy.lexer.unput('('); yytext = 'first_value'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LAG\s*\(                                   { yy.lexer.unput('('); yytext = 'lag'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LAST_VALUE\s*\(                            { yy.lexer.unput('('); yytext = 'last_value'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
LEAD\s*\(                                  { yy.lexer.unput('('); yytext = 'lead'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
RANK\s*\(                                  { yy.lexer.unput('('); yytext = 'rank'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }
ROW_NUMBER\s*\(                            { yy.lexer.unput('('); yytext = 'row_number'; parser.addFunctionLocation(yylloc, yytext); return 'ANALYTIC'; }

[0-9]+                                     { return 'UNSIGNED_INTEGER'; }
[0-9]+(?:[YSL]|BD)?                        { return 'UNSIGNED_INTEGER'; }
[0-9]+E                                    { return 'UNSIGNED_INTEGER_E'; }
[A-Za-z0-9_]+                              { return 'REGULAR_IDENTIFIER'; }

DIRECTORY\s+['"]                           { this.begin('hdfs'); return 'DIRECTORY_PATH'; }
<hdfs>'\u2020'                             { parser.yy.cursorFound = true; return 'CURSOR'; }
<hdfs>'\u2021'                             { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }
<hdfs>\s+['"]                              { return 'HDFS_START_QUOTE'; }
<hdfs>[^'"\u2020\u2021]+                   { parser.addFileLocation(yylloc, yytext); return 'HDFS_PATH'; }
<hdfs>['"]                                 { this.popState(); return 'HDFS_END_QUOTE'; }
<hdfs><<EOF>>                              { return 'EOF'; }

ADD\s+ARCHIVE\s+                           { this.begin('sparkfile'); return 'ADD_ARCHIVE'; }
ADD\s+ARCHIVES\s+                          { this.begin('sparkfile'); return 'ADD_ARCHIVES'; }
ADD\s+FILE\s+                              { this.begin('sparkfile'); return 'ADD_FILE'; }
ADD\s+FILES\s+                             { this.begin('sparkfile'); return 'ADD_FILES'; }
ADD\s+JAR\s+                               { this.begin('sparkfile'); return 'ADD_JAR'; }
ADD\s+JARS\s+                              { this.begin('sparkfile'); return 'ADD_JARS'; }
LIST\s+ARCHIVE\s+                          { this.begin('sparkfile'); return 'LIST_ARCHIVE'; }
LIST\s+ARCHIVES\s+                         { this.begin('sparkfile'); return 'LIST_ARCHIVES'; }
LIST\s+FILE\s+                             { this.begin('sparkfile'); return 'LIST_FILE'; }
LIST\s+FILES\s+                            { this.begin('sparkfile'); return 'LIST_FILES'; }
LIST\s+JAR\s+                              { this.begin('sparkfile'); return 'LIST_JAR'; }
LIST\s+JARS\s+                             { this.begin('sparkfile'); return 'LIST_JARS'; }
<sparkfile>'\u2020'                        { parser.yy.cursorFound = true; return 'CURSOR'; }
<sparkfile>'\u2021'                        { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }
<sparkfile>[^;\s'"\u2020\u2021]+           { parser.addFileLocation(yylloc, yytext); return 'FILE_PATH'; }
<sparkfile>[\s]+                           { return 'WHITESPACE'; }
<sparkfile>['"]                            { return 'FILE_QUOTE'; }
<sparkfile>';'                             { this.popState(); return ';'; }
<sparkfile><<EOF>>                         { this.popState(); return 'EOF'; }

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
<singleQuotedValue>(?:\\\\|\\[']|[^'])+    {
                                             if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '\'')) {
                                               return 'PARTIAL_VALUE';
                                             }
                                             return 'VALUE';
                                           }
<singleQuotedValue>\'                      { this.popState(); return 'SINGLE_QUOTE'; }

\"                                         { this.begin('doubleQuotedValue'); return 'DOUBLE_QUOTE'; }
<doubleQuotedValue>(?:\\\\|\\["]|[^"])+    {
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
