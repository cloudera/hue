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

<between>'AND'                             { this.popState(); return 'BETWEEN_AND'; }

// Reserved Keywords
'ADVANCE'                                  { return 'ADVANCE'; }
'ANALYZE'                                  { return 'ANALYZE'; }
'AND'                                      { return 'AND'; }
'ARRAY'                                    { return 'ARRAY'; }
'AS'                                       { return 'AS'; }
'AT'                                       { return 'AT'; }
'BEGINNING'                                { return 'BEGINNING' }
'BETWEEN'                                  { this.begin('between'); return 'BETWEEN'; }
'BIGINT'                                   { return 'BIGINT'; }
'BOOLEAN'                                  { return 'BOOLEAN'; }
'BY'                                       { return 'BY'; }
'CASE'                                     { return 'CASE'; }
'CAST'                                     { return 'CAST'; }
'CATALOG'                                  { return 'CATALOG'; }
'CHANGES'                                  { return 'CHANGES'; }
'COLUMN'                                   { return 'COLUMN'; }
'COLUMNS'                                  { return 'COLUMNS'; }
'CONNECTOR'                                { return 'CONNECTOR'; }
'CONNECTORS'                               { return 'CONNECTORS'; }
'CREATE'                                   { parser.determineCase(yytext); return 'CREATE'; }
'DATE'                                     { return 'DATE'; }
'DAY'                                      { return 'DAY'; }
'DECIMAL'                                  { return 'DECIMAL'; }
'DELETE'                                   { return 'DELETE'; }
'DESCRIBE'                                 { return 'DESCRIBE'; }
'DISTINCT'                                 { return 'DISTINCT'; }
'DOUBLE'                                   { return 'DOUBLE'; }
'DROP'                                     { parser.determineCase(yytext); parser.addStatementTypeLocation('DROP', yylloc, yy.lexer.upcomingInput()); return 'DROP'; }
'ELSE'                                     { return 'ELSE'; }
'EMIT'                                     { return 'EMIT'; }
'END'                                      { return 'END'; }
'EXISTS'                                   { parser.yy.correlatedSubQuery = true; return 'EXISTS'; }
'EXPLAIN'                                  { parser.determineCase(yytext); return 'EXPLAIN'; }
'EXPORT'                                   { return 'EXPORT'; }
'EXTENDED'                                 { return 'EXTENDED'; }
'FROM'                                     { parser.determineCase(yytext); return 'FROM'; }
'FULL'                                     { return 'FULL'; }
'FUNCTION'                                 { return 'FUNCTION'; }
'FUNCTIONS'                                { return 'FUNCTIONS'; }
'GROUP'                                    { return 'GROUP'; }
'HAVING'                                   { return 'HAVING'; }
'HOPPING'                                  { return 'HOPPING'; }
'HOUR'                                     { return 'HOUR'; }
'HOURS'                                    { return 'HOURS'; }
'IF'                                       { return 'IF'; }
'IN'                                       { return 'IN'; }
'INNER'                                    { return 'INNER'; }
'INSERT'                                   { return 'INSERT'; }
'INT'                                      { return 'INT'; }
'INTEGER'                                  { return 'INTEGER'; }
'INTO'                                     { return 'INTO'; }
'IS'                                       { return 'IS'; }
'JOIN'                                     { return 'JOIN'; }
'KEY'                                      { return 'KEY'; }
'LEFT'                                     { return 'LEFT'; }
'LIKE'                                     { return 'LIKE'; }
'LIMIT'                                    { return 'LIMIT'; }
'LIST'                                     { return 'LIST'; }
'LOAD'                                     { return 'LOAD'; }
'MAP'                                      { return 'MAP'; }
'MILLISECOND'                              { return 'MILLISECOND'; }
'MILLISECONDS'                             { return 'MILLISECONDS'; }
'MINUTE'                                   { return 'MINUTE'; }
'MINUTES'                                  { return 'MINUTES'; }
'MONTH'                                    { return 'MONTH'; }
'MONTHS'                                   { return 'MONTHS'; }
'NOT'                                      { return 'NOT'; }
'NULL'                                     { return 'NULL'; }
'ON'                                       { return 'ON'; }
'OR'                                       { return 'OR'; }
'OUTER'                                    { return 'OUTER'; }
'PARTITION'                                { return 'PARTITION'; }
'PARTITIONS'                               { return 'PARTITIONS'; }
'PRINT'                                    { return 'PRINT'; }
'PROPERTIES'                               { return 'PROPERTIES'; }
'QUERIES'                                  { return 'QUERIES'; }
'QUERY'                                    { return 'QUERY'; }
'RENAME'                                   { return 'RENAME'; }
'RESET'                                    { return 'RESET'; }
'RIGHT'                                    { return 'RIGHT'; }
'RUN'                                      { return 'RUN'; }
'SAMPLE'                                   { return 'SAMPLE'; }
'SCRIPT'                                   { return 'SCRIPT'; }
'SECOND'                                   { return 'SECOND'; }
'SECOND'                                   { return 'SECOND'; }
'SELECT'                                   { parser.determineCase(yytext); parser.addStatementTypeLocation('SELECT', yylloc); return 'SELECT'; }
'SESSION'                                  { return 'SESSION'; }
'SET'                                      { parser.determineCase(yytext); parser.addStatementTypeLocation('SET', yylloc); return 'SET'; }
'SHOW'                                     { parser.determineCase(yytext); parser.addStatementTypeLocation('SHOW', yylloc); return 'SHOW'; }
'SINK'                                     { return 'SINK'; }
'SOURCE'                                   { return 'SOURCE'; }
'STREAM'                                   { return 'STREAM'; }
'STREAMS'                                  { return 'STREAMS'; }
'STRING'                                   { return 'STRING'; }
'STRUCT'                                   { return 'STRUCT'; }
'TABLE'                                    { return 'TABLE'; }
'TABLES'                                   { return 'TABLES'; }
'TERMINATE'                                { return 'TERMINATE'; }
'THEN'                                     { return 'THEN'; }
'TIME'                                     { return 'TIME'; }
'TIMESTAMP'                                { return 'TIMESTAMP'; }
'TO'                                       { return 'TO'; }
'TRUE'                                     { return 'TRUE'; }
'TOPIC'                                    { return 'TOPIC'; }
'TOPICS'                                   { return 'TOPICS'; }
'TUMBLING'                                 { return 'TUMBLING'; }
'TYPE'                                     { return 'TYPE'; }
'TYPES'                                    { return 'TYPES'; }
'UNSET'                                    { return 'UNSET'; }
'VALUES'                                   { return 'VALUES'; }
'VARCHAR'                                  { return 'VARCHAR'; }
'WHEN'                                     { return 'WHEN'; }
'WHERE'                                    { return 'WHERE'; }
'WITH'                                     { parser.determineCase(yytext); parser.addStatementTypeLocation('WITH', yylloc); return 'WITH'; }
'WITHIN'                                   { return 'WITHIN'; }
'YEAR'                                     { return 'YEAR'; }
'YEARS'                                    { return 'YEARS'; }
'ZONE'                                     { return 'ZONE'; }

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

<hdfs>'\u2020'                             { parser.yy.cursorFound = true; return 'CURSOR'; }
<hdfs>'\u2021'                             { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }
<hdfs>\s+['"]                              { return 'HDFS_START_QUOTE'; }
<hdfs>[^'"\u2020\u2021]+                   { parser.addFileLocation(yylloc, yytext); return 'HDFS_PATH'; }
<hdfs>['"]                                 { this.popState(); return 'HDFS_END_QUOTE'; }
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
<hdfs>.                                    { }
<backtickedValue>.                         { }
<singleQuotedValue>.                       { }
<doubleQuotedValue>.                       { }
