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

\s+                       { /* skip whitespace */ }
'|CURSOR|'                { return '|CURSOR|'; }
[Ss][Ee][Ll][Ee][Cc][Tt]  { return 'SELECT'; }
[Uu][Ss][Ee]              { return 'USE'; }
[Ff][Rr][Oo][Mm]          { return 'FROM'; }
[a-zA-Z0-9_]*\b           { return 'STRING_IDENTIFIER'; }
','                       { return ','; }
'*'                       { return '*'; }
';'                       { return ';'; }
<<EOF>>                   { return 'EOF'; }

/lex

%start Sql

%%

Sql
 : SqlStatements EOF
 ;

SqlStatements
 : SqlStatement
 | SqlStatements ';' SqlStatement
 ;

SqlStatement
 : SelectStatement
 | UseStatement
 | STRING_IDENTIFIER '|CURSOR|'
   {
     return filterStartsWith(adjustKeywordCase(isLowerCase($1), suggestions.statements), $1);
   }
 | '|CURSOR|'
   {
     return adjustKeywordCase(false, suggestions.statements);
   }
 ;

UseStatement
  : 'USE' STRING_IDENTIFIER ';'
  ;

SelectStatement
 : 'SELECT' SelectExpression 'FROM' TableReference ';'
 | 'SELECT' '|CURSOR|'
   {
     var tables = parser.yy.callbacks.tableHandler({
       prependQuestionMark: true,
       prependFrom: true,
       lowerCase: isLowerCase($1)
     });

     var databases = parser.yy.callbacks.databaseHandler({
       prependQuestionMark: true,
       prependFrom: true,
       lowerCase: isLowerCase($1)
     });

     return tables.concat(databases);
   }
 ;

SelectExpression
 : SelectExpressionList
 | '*' '|CURSOR|'
   {
      var tables = parser.yy.callbacks.tableHandler({
        prependFrom: true,
        lowerCase: isLowerCase($1)
      });

      var databases = parser.yy.callbacks.databaseHandler({
        prependFrom: true,
        lowerCase: isLowerCase($1)
      });

      return tables.concat(databases);
   }
 | '*'
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

var suggestions = {
  statements: [{ value: 'SELECT', meta: 'keyword' }, { value: 'USE', meta: 'keyword' }]
}

var filterStartsWith = function (suggestions, start) {
  var startLower = start.toLowerCase();
  return suggestions.filter(function (suggestion) {
    return suggestion.value.toLowerCase().indexOf(startLower) === 0;
  });
}

var adjustKeywordCase = function (lowerCase, suggestions) {
  if (lowerCase) {
    suggestions.forEach(function (suggestion) {
      if (suggestion.meta === 'keyword') {
        suggestion.value = suggestion.value.toLowerCase();
      }
    });
  } else {
    suggestions.forEach(function (suggestion) {
      if (suggestion.meta === 'keyword') {
        suggestion.value = suggestion.value.toUpperCase();
      }
    });
  }
  return suggestions;
}

var isLowerCase = function (text) {
  return text.toLowerCase() === text;
}

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