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
'ALL'                                      { return 'ALL'; }
'ALTER'                                    { parser.determineCase(yytext); parser.addStatementTypeLocation('ALTER', yylloc, yy.lexer.upcomingInput()); return 'ALTER'; }
'AND'                                      { return 'AND'; }
'AS'                                       { return 'AS'; }
'ASC'                                      { return 'ASC'; }
'BETWEEN'                                  { this.begin('between'); return 'BETWEEN'; }
'BIGINT'                                   { return 'BIGINT'; }
'BOOLEAN'                                  { return 'BOOLEAN'; }
'BY'                                       { return 'BY'; }
'CASCADE'                                  { return 'CASCADE'; }
'CASE'                                     { return 'CASE'; }
'CHAR'                                     { return 'CHAR'; }
'COMMENT'                                  { return 'COMMENT'; }
'CREATE'                                   { parser.determineCase(yytext); return 'CREATE'; }
'CROSS'                                    { return 'CROSS'; }
'CURRENT'                                  { return 'CURRENT'; }
'DATABASE'                                 { return 'DATABASE'; }
'DECIMAL'                                  { return 'DECIMAL'; }
'DESC'                                     { return 'DESC'; }
'DISTINCT'                                 { return 'DISTINCT'; }
'DIV'                                      { return 'ARITHMETIC_OPERATOR'; }
'DOUBLE'                                   { return 'DOUBLE'; }
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
'ROLE'                                     { return 'ROLE'; }
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
'UNION'                                    { return 'UNION'; }
'UPDATE'                                   { parser.determineCase(yytext); return 'UPDATE'; }
'USE'                                      { parser.determineCase(yytext); parser.addStatementTypeLocation('USE', yylloc); return 'USE'; }
'VALUES'                                   { return 'VALUES'; }
'VARCHAR'                                  { return 'VARCHAR'; }
'VIEW'                                     { return 'VIEW'; }
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
