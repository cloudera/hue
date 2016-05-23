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

%{
  parser.yy.result = {};
%}

%lex
%options case-insensitive
%%

'|CURSOR|'                          { parser.yy.cursorFound = true; return 'CURSOR'; }
'|PARTIAL_CURSOR|'                  { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }

[A-Za-z][A-Za-z0-9_]*               { return 'REGULAR_IDENTIFIER'; }


[-+&~|^/%*(),.;!]                   { return yytext; }

[ \t\n]                             { /* skip whitespace */ }
'--'.*                              { /* skip comments */ }
[/][*][^*]*[*]+([^/*][^*]*[*]+)*[/] { /* skip comments */ }

<<EOF>>                             { return 'EOF'; }

/lex

%start Sql

%%

Sql
 : CleanResults SqlStatements ';' EOF
   {
     prioritizeSuggestions();
     return parser.yy.result;
   }
 | CleanResults SqlStatements EOF
   {
     prioritizeSuggestions();
     return parser.yy.result;
   }
 ;

CleanResults
 : /* empty */
   {
     parser.yy.result = {};
     parser.yy.cursorFound = false;
     delete parser.yy.latestTableReferences;
   }
 ;

SqlStatements
 :
 | SqlStatements ';' SqlStatement
 ;

DirectSqlStatement
 : DirectSelectStatement ';'
 ;

CleanReferences
 : /* empty */
   {
     delete parser.yy.latestTableReferences;
   }
 ;

AnyCursor
 : 'CURSOR'
 | 'PARTIAL_CURSOR'
 ;

SqlStatement
 : UseStatement
 | QueryExpression
 | CHARACTER_PRIMARY AnyCursor CHARACTER_PRIMARY
 | CHARACTER_PRIMARY AnyCursor
   {
     determineCase($1);
     suggestKeywords(['SELECT', 'USE']);
   }
 | AnyCursor
   {
     suggestKeywords(['SELECT', 'USE']);
   }
 ;

UseStatement
 : USE CHARACTER_PRIMARY AnyCursor
   {
     determineCase($1);
     suggestDatabases();
   }
 | 'USE' CHARACTER_PRIMARY
   {
     determineCase($1);
     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $2;
     }
   }
 | 'USE' AnyCursor
   {
     determineCase($1);
     suggestDatabases();
   }
 ;

QueryExpression
 : 'SELECT' SelectList TableExpression
   {
     determineCase($1);
     completeSuggestColumns();
   }
 | 'SELECT' SelectList
   {
     determineCase($1);
   }
 ;

TableExpression
 : FromClause
 | FromClause 'PARTIAL_CURSOR'
   {
     determineCase($1);
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | FromClause SelectConditionList
 ;

FromClause
 : 'FROM' TableReferenceList
 ;

SelectConditionList
 : SelectCondition
 | SelectConditionList SelectCondition
 ;

SelectCondition
 : WhereClause
 | GroupByClause
 | OrderByClause
 | 'CURSOR'
   {
     suggestKeywords(['WHERE', 'GROUP BY', 'CLUSTER BY', 'LIMIT']);
   }
 ;

WhereClause
 : 'WHERE' SearchCondition
 ;

GroupByClause
 : 'GROUP' 'BY' ColumnList
 | 'GROUP' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

OrderByClause
 : 'ORDER' 'BY' ColumnList
 | 'ORDER' 'CURSOR'
   {
     suggestKeywords(['BY']);
   }
 ;

SelectList
 : ColumnList
   {
     if ($1 == '|CURSOR|') {
       parser.yy.result.suggestColumns.includeStar = true;
     }
   }
 | '*' CHARACTER_PRIMARY 'PARTIAL_CURSOR'
   {
     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   }
 | '*' 'CURSOR'
   {
     suggestTables({ prependFrom: true });
     suggestDatabases({ prependFrom: true, appendDot: true });
   }
 | '*'
 ;

ColumnList
 : DerivedColumn
 | ColumnList ',' DerivedColumn
 ;

DerivedColumn
 : CHARACTER_PRIMARY
 | CHARACTER_PRIMARY '.' CHARACTER_PRIMARY
 | CHARACTER_PRIMARY '.' AnyCursor
 | CHARACTER_PRIMARY 'PARTIAL_CURSOR'
   {
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'CURSOR'
   {
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 ;

TableReferenceList
 : TableReference
 | TableReferenceList ',' TableReference
 ;

TableReference
 : TablePrimaryOrJoinedTable
 ;

TablePrimaryOrJoinedTable
 : TablePrimary
 | JoinedTable
 ;

TablePrimary
 : CHARACTER_PRIMARY
   {
     addTableReference({ table: $1 });
   }
 | CHARACTER_PRIMARY CHARACTER_PRIMARY
   {
     addTableReference({ table: $1, alias: $2 });
   }
 | CHARACTER_PRIMARY '.' CHARACTER_PRIMARY
   {
     addTableReference({ database: $1, table: $3 });
   }
 | CHARACTER_PRIMARY '.' CHARACTER_PRIMARY CHARACTER_PRIMARY
   {
     addTableReference({ database: $1, table: $3, alias: $4 });
   }
 | CHARACTER_PRIMARY '.' AnyCursor
   {
     suggestTables({ database: $1 });
   }
 | AnyCursor
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 ;

JoinedTable
 : TableReference JOIN TableReference JoinSpecification
 ;

JoinSpecification
 : JoinCondition
 ;

JoinCondition
 : 'ON' SearchCondition
 ;

%%

var prioritizeSuggestions = function () {
   if (typeof parser.yy.result.suggestColumns !== 'undefined') {
     if (typeof parser.yy.result.suggestColumns.tables === 'undefined') {
       delete parser.yy.result.suggestColumns;
     } else {
       delete parser.yy.result.suggestTables;
       delete parser.yy.result.suggestDatabases;
     }
   }
}

var completeSuggestColumns = function () {
   if (parser.yy.cursorFound &&
       typeof parser.yy.result.suggestColumns !== 'undefined') {
     parser.yy.result.suggestColumns.tables = parser.yy.latestTableReferences;
   }
}

var addTableReference = function (ref) {
  if (typeof parser.yy.latestTableReferences === 'undefined') {
    parser.yy.latestTableReferences = [];
  }
  parser.yy.latestTableReferences.push(ref);
}

var suggestKeywords = function (keywords) {
  parser.yy.result.suggestKeywords = keywords;
}

var suggestColumns = function (details) {
  parser.yy.result.suggestColumns = details || {};
}

var suggestTables = function (details) {
  parser.yy.result.suggestTables = details || {};
}

var suggestDatabases = function (details) {
  parser.yy.result.suggestDatabases = details || {};
}

var determineCase = function (text) {
  parser.yy.result.lowerCase = text.toLowerCase() === text;
};

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