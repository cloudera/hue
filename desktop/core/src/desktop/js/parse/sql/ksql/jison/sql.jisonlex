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
ABS\s*\(                                   { yy.lexer.unput('('); yytext = 'abs'; parser.addFunctionLocation(yylloc, yytext); return 'ABS'; }
ARRAYCONTAINS\s*\(                         { yy.lexer.unput('('); yytext = 'arraycontains'; parser.addFunctionLocation(yylloc, yytext); return 'ARRAYCONTAINS'; }
CEIL\s*\(                                  { yy.lexer.unput('('); yytext = 'ceil'; parser.addFunctionLocation(yylloc, yytext); return 'CEIL'; }
CONCAT\s*\(                                { yy.lexer.unput('('); yytext = 'concat'; parser.addFunctionLocation(yylloc, yytext); return 'CONCAT'; }
DATETOSTRING\s*\(                          { yy.lexer.unput('('); yytext = 'datetostring'; parser.addFunctionLocation(yylloc, yytext); return 'DATETOSTRING'; }
ELT\s*\(                                   { yy.lexer.unput('('); yytext = 'elt'; parser.addFunctionLocation(yylloc, yytext); return 'ELT'; }
EXTRACTJSONFIELD\s*\(                      { yy.lexer.unput('('); yytext = 'extractjsonfield'; parser.addFunctionLocation(yylloc, yytext); return 'EXTRACTJSONFIELD'; }
FIELD\s*\(                                 { yy.lexer.unput('('); yytext = 'field'; parser.addFunctionLocation(yylloc, yytext); return 'FIELD'; }
FLOOR\s*\(                                 { yy.lexer.unput('('); yytext = 'floor'; parser.addFunctionLocation(yylloc, yytext); return 'FLOOR'; }
GEO_DISTANCE\s*\(                          { yy.lexer.unput('('); yytext = 'geo_distance'; parser.addFunctionLocation(yylloc, yytext); return 'GEO_DISTANCE'; }
IFNULL\s*\(                                { yy.lexer.unput('('); yytext = 'ifnull'; parser.addFunctionLocation(yylloc, yytext); return 'IFNULL'; }
LCASE\s*\(                                 { yy.lexer.unput('('); yytext = 'lcase'; parser.addFunctionLocation(yylloc, yytext); return 'LCASE'; }
LEN\s*\(                                   { yy.lexer.unput('('); yytext = 'len'; parser.addFunctionLocation(yylloc, yytext); return 'LEN'; }
MASK\s*\(                                  { yy.lexer.unput('('); yytext = 'msk'; parser.addFunctionLocation(yylloc, yytext); return 'MASK'; }
MASK_KEEP_LEFT\s*\(                        { yy.lexer.unput('('); yytext = 'mask_keep_left'; parser.addFunctionLocation(yylloc, yytext); return 'MASK_KEEP_LEFT'; }
MASK_KEEP_RIGHT\s*\(                       { yy.lexer.unput('('); yytext = 'mask_keep_right'; parser.addFunctionLocation(yylloc, yytext); return 'MASK_KEEP_RIGHT'; }
MASK_LEFT\s*\(                             { yy.lexer.unput('('); yytext = 'mask_left'; parser.addFunctionLocation(yylloc, yytext); return 'MASK_LEFT'; }
MASK_RIGHT\s*\(                            { yy.lexer.unput('('); yytext = 'mask_right'; parser.addFunctionLocation(yylloc, yytext); return 'MASK_RIGHT'; }
RANDOM\s*\(                                { yy.lexer.unput('('); yytext = 'random'; parser.addFunctionLocation(yylloc, yytext); return 'RANDOM'; }
ROUND\s*\(                                 { yy.lexer.unput('('); yytext = 'round'; parser.addFunctionLocation(yylloc, yytext); return 'ROUND'; }
SPLIT\s*\(                                 { yy.lexer.unput('('); yytext = 'split'; parser.addFunctionLocation(yylloc, yytext); return 'SPLIT'; }
STRINGTODATE\s*\(                          { yy.lexer.unput('('); yytext = 'stringtodate'; parser.addFunctionLocation(yylloc, yytext); return 'STRINGTODATE'; }
STRINGTOTIMESTAMP\s*\(                     { yy.lexer.unput('('); yytext = 'stringtotimestamp'; parser.addFunctionLocation(yylloc, yytext); return 'STRINGTOTIMESTAMP'; }
SUBSTRING\s*\(                             { yy.lexer.unput('('); yytext = 'substring'; parser.addFunctionLocation(yylloc, yytext); return 'SUBSTRING'; }
TIMESTAMPTOSTRING\s*\(                     { yy.lexer.unput('('); yytext = 'timestamptostring'; parser.addFunctionLocation(yylloc, yytext); return 'TIMESTAMPTOSTRING'; }
TRIM\s*\(                                  { yy.lexer.unput('('); yytext = 'trim'; parser.addFunctionLocation(yylloc, yytext); return 'TRIM'; }
UCASE\s*\(                                 { yy.lexer.unput('('); yytext = 'ucase'; parser.addFunctionLocation(yylloc, yytext); return 'UCASE'; }
URL_DECODE_PARAM\s*\(                      { yy.lexer.unput('('); yytext = 'url_decode_param'; parser.addFunctionLocation(yylloc, yytext); return 'URL_DECODE_PARAM'; }
URL_ENCODE_PARAM\s*\(                      { yy.lexer.unput('('); yytext = 'urel_encode_param'; parser.addFunctionLocation(yylloc, yytext); return 'URL_ENCODE_PARAM'; }
URL_EXTRACT_FRAGMENT\s*\(                  { yy.lexer.unput('('); yytext = 'url_extract_fragment'; parser.addFunctionLocation(yylloc, yytext); return 'URL_EXTRACT_FRAGMENT'; }
URL_EXTRACT_HOST\s*\(                      { yy.lexer.unput('('); yytext = 'url_extract_host'; parser.addFunctionLocation(yylloc, yytext); return 'URL_EXTRACT_HOST'; }
URL_EXTRACT_PARAMETER\s*\(                 { yy.lexer.unput('('); yytext = 'url_extract_parameter'; parser.addFunctionLocation(yylloc, yytext); return 'URL_EXTRACT_PARAMETER'; }
URL_EXTRACT_PATH\s*\(                      { yy.lexer.unput('('); yytext = 'url_extrct_path'; parser.addFunctionLocation(yylloc, yytext); return 'URL_EXTRACT_PATH'; }
URL_EXTRACT_PORT\s*\(                      { yy.lexer.unput('('); yytext = 'url_extract_port'; parser.addFunctionLocation(yylloc, yytext); return 'URL_EXTRACT_PORT'; }
URL_EXTRACT_PROTOCOL\s*\(                  { yy.lexer.unput('('); yytext = 'url_extract_protocol'; parser.addFunctionLocation(yylloc, yytext); return 'URL_EXTRACT_PROTOCOL'; }
URL_EXTRACT_QUERY\s*\(                     { yy.lexer.unput('('); yytext = 'url_extract_query'; parser.addFunctionLocation(yylloc, yytext); return 'URL_EXTRACT_QUERY'; }


// Analytical functions
COLLECT_LIST\s*\(                          { yy.lexer.unput('('); yytext = 'collect_list'; parser.addFunctionLocation(yylloc, yytext); return 'COLLECT_LIST'; }
COLLECT_SET\s*\(                           { yy.lexer.unput('('); yytext = 'collect_set'; parser.addFunctionLocation(yylloc, yytext); return 'COLLECT_SET'; }
COUNT\s*\(                                 { yy.lexer.unput('('); yytext = 'count'; parser.addFunctionLocation(yylloc, yytext); return 'COUNT'; }
HISTOGRAM\s*\(                             { yy.lexer.unput('('); yytext = 'historgram'; parser.addFunctionLocation(yylloc, yytext); return 'HISTOGRAM'; }
MAX\s*\(                                   { yy.lexer.unput('('); yytext = 'max'; parser.addFunctionLocation(yylloc, yytext); return 'MAX'; }
MIN\s*\(                                   { yy.lexer.unput('('); yytext = 'min'; parser.addFunctionLocation(yylloc, yytext); return 'MIN'; }
SUM\s*\(                                   { yy.lexer.unput('('); yytext = 'sum'; parser.addFunctionLocation(yylloc, yytext); return 'SUM'; }
TOPK\s*\(                                  { yy.lexer.unput('('); yytext = 'topk'; parser.addFunctionLocation(yylloc, yytext); return 'TOPK'; }
TOPKDISTINCT\s*\(                          { yy.lexer.unput('('); yytext = 'topkdistinct'; parser.addFunctionLocation(yylloc, yytext); return 'TOPKDISTINCT'; }
WindowStart\s*\(                           { yy.lexer.unput('('); yytext = 'windowstart'; parser.addFunctionLocation(yylloc, yytext); return 'WindowStart'; }
WindowEnd\s*\(                             { yy.lexer.unput('('); yytext = 'windowend'; parser.addFunctionLocation(yylloc, yytext); return 'WindowEnd'; }


[0-9]+                                     { return 'UNSIGNED_INTEGER'; }
[0-9]+(?:[YSL]|BD)?                        { return 'UNSIGNED_INTEGER'; }
[0-9]+E                                    { return 'UNSIGNED_INTEGER_E'; }
[A-Za-z0-9_]+                              { return 'REGULAR_IDENTIFIER'; }


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
