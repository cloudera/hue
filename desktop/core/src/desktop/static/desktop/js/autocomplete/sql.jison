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
%%

\s+                   { /* skip whitespace */ }
'|CURSOR|'            { return '|CURSOR|'; }
'SELECT'              { return 'SELECT'; }
'USE'                 { return 'USE'; }
'FROM'                { return 'FROM'; }
[a-zA-Z0-9_]*\b       { return 'STRING_IDENTIFIER'; }
','                   { return ','; }
'*'                   { return '*'; }
';'                   { return ';'; }
<<EOF>>               { return 'EOF'; }

/lex

%start SqlStatement

%{
  var suggestions = {
    statements: [{ value: 'SELECT' }, { value: 'USE' }]
  }
%}

%%

SqlStatement
 : SelectStatement EOF
 | UseStatement EOF
 | STRING_IDENTIFIER '|CURSOR|' EOF
   {
     var upperCase = $1.toUpperCase();
     return suggestions.statements.filter(function (statement) {
       return statement.value.indexOf(upperCase) === 0;
     });
   }
 | '|CURSOR|' EOF
   {
     return suggestions.statements;
   }
 ;

UseStatement
  : 'USE' STRING_IDENTIFIER ';'
  ;

SelectStatement
 : 'SELECT' SelectExpression 'FROM' TableReference ';'
 ;

SelectExpression
 : '*'
 | SelectExpressionList
 ;

SelectExpressionList
 : DerivedColumn
 | SelectExpressionList ',' DerivedColumn
 ;

DerivedColumn
 : STRING_IDENTIFIER
 ;

TableReference
 : STRING_IDENTIFIER
 ;

%%

/*
 Hive Select syntax from https://cwiki.apache.org/confluence/display/Hive/LanguageManual+Select

 [WITH CommonTableExpression (, CommonTableExpression)*]    (Note: Only available starting with Hive 0.13.0)
 SELECT [ALL | DISTINCT] select_expr, select_expr, ...
 FROM table_reference
 [WHERE where_condition]
 [GROUP BY col_list]
 [CLUSTER BY col_list
   | [DISTRIBUTE BY col_list] [SORT BY col_list]
 ]
 [LIMIT number]
*/