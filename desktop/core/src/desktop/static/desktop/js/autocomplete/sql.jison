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
%options case-insensitive
%%

[ \t\n]                             { /* skip whitespace */ }
'--'.*                              { /* skip comments */ }
[/][*][^*]*[*]+([^/*][^*]*[*]+)*[/] { /* skip comments */ }

'|CURSOR|'                          { parser.yy.cursorFound = true; return 'CURSOR'; }
'|PARTIAL_CURSOR|'                  { parser.yy.cursorFound = true; return 'PARTIAL_CURSOR'; }

'AND'                               { return 'AND'; }
'BY'                                { return 'BY'; }
'FROM'                              { return 'FROM'; }
'GROUP'                             { return 'GROUP'; }
'IS'                                { return 'IS'; }
'JOIN'                              { return 'JOIN'; }
'NOT'                               { return 'NOT'; }
'ON'                                { return 'ON'; }
'OR'                                { return 'OR'; }
'ORDER'                             { return 'ORDER'; }
'SELECT'                            { determineCase(yytext); return 'SELECT'; }
'USE'                               { determineCase(yytext); return 'USE'; }
'WHERE'                             { return 'WHERE'; }

[0-9]+                              { return 'UNSIGNED_INTEGER'; }
[A-Za-z][A-Za-z0-9_]*               { return 'REGULAR_IDENTIFIER'; }

[-+&~|^/%*(),.;!]                   { return yytext; }
[=<>]                               { return yytext; }

<<EOF>>                             { return 'EOF'; }

/lex

%start Sql

%%

AnyCursor
 : 'CURSOR'
 | 'PARTIAL_CURSOR'
 ;

InitResults
 : /* empty */
   {
     parser.yy.result = {};
     parser.yy.cursorFound = false;
     delete parser.yy.latestTableReferences;
     parser.parseError = function (message, error) {
       if (typeof parser.yy.result.suggestColumns !== 'undefined') {
         completeSuggestColumns();
       }
       prioritizeSuggestions();
       parser.yy.result.error = error;
       return message;
     }
   }
 ;

Sql
 : InitResults SqlStatements ';' EOF
   {
     prioritizeSuggestions();
     return parser.yy.result;
   }
 | InitResults SqlStatements EOF
   {
     prioritizeSuggestions();
     return parser.yy.result;
   }
 ;

SqlStatements
 : SqlStatement
 | SqlStatements ';' SqlStatement
 ;

SqlStatement
 : UseStatement
 | QueryExpression
 | 'REGULAR_IDENTIFIER' AnyCursor 'REGULAR_IDENTIFIER'
 | 'REGULAR_IDENTIFIER' AnyCursor
   {
     suggestKeywords(['SELECT', 'USE']);
   }
 | AnyCursor
   {
     suggestKeywords(['SELECT', 'USE']);
   }
 ;

UseStatement
 : 'USE' 'REGULAR_IDENTIFIER' AnyCursor
   {
     suggestDatabases();
   }
 | 'USE' 'REGULAR_IDENTIFIER'
   {
     if (! parser.yy.cursorFound) {
       parser.yy.result.useDatabase = $2;
     }
   }
 | 'USE' AnyCursor
   {
     suggestDatabases();
   }
 ;

QueryExpression
 : 'SELECT' SelectList TableExpression
   {
     completeSuggestColumns();
   }
 | 'SELECT' SelectList
 ;

TableExpression
 : FromClause
 | FromClause 'PARTIAL_CURSOR'
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 | FromClause SelectConditionList
 ;

FromClause
 : 'FROM' TableReferenceList
 | 'FROM' AnyCursor
   {
     suggestTables();
     suggestDatabases({ appendDot: true });
   }
 ;

SelectConditionList
 : SelectCondition
 | SelectConditionList SelectCondition
 ;

SelectCondition
 : WhereClause
 | GroupByClause
   {
     delete parser.yy.result.suggestStar;
   }
 | OrderByClause
   {
     delete parser.yy.result.suggestStar;
   }
 | LimitClause
   {
     delete parser.yy.result.suggestStar;
   }
 | 'CURSOR'
   {
     suggestKeywords(['WHERE', 'GROUP BY', 'LIMIT']);
   }
 ;

WhereClause
 : 'WHERE' SearchCondition
 | 'WHERE' 'CURSOR'
   {
     suggestColumns();
   }
 ;

SearchCondition
 : BooleanValueExpression
 ;

BooleanValueExpression
 : BooleanTerm
 | BooleanValueExpression 'OR' BooleanTerm
 ;

BooleanTerm
 : BooleanFactor
 | BooleanFactor 'AND' 'CURSOR'
   {
     // TODO: Fix issue when EOF after 'CURSOR' in started parenthesized expression it now throws a parser error
     suggestColumns();
   }
 | BooleanFactor 'AND' BooleanTerm
 ;

BooleanFactor
 : 'NOT' BooleanTest
 | BooleanTest
 ;

BooleanTest
 : Predicate
 | Predicate CompOp Predicate
 | Predicate 'IS' TruthValue
 | Predicate 'IS' 'NOT' TruthValue
 ;

Predicate
 : ParenthesizedBooleanValueExpression
 | NonParenthesizedValueExpressionPrimary
 ;

CompOp
 : '='
 | '<>'
 | '<'
 | '>'
 | '<='
 | '>='
 ;

ParenthesizedBooleanValueExpression
 : '(' BooleanValueExpression ')'
 | '(' AnyCursor
   {
     // For '...FROM tableA JOIN tableB ON (|', might need an ON flag
     suggestColumns();
   }
 ;

NonParenthesizedValueExpressionPrimary
 : ColumnReference // TODO: Expand with more choices
 ;

ColumnReference
 : BasicIdentifierChain
 ;

BasicIdentifierChain
 : InitIdentifierChain IdentifierChain
   {
     delete parser.yy.identifierChain;
   }
 ;

InitIdentifierChain
 : /* empty */
   {
     parser.yy.identifierChain = [];
   }
 ;

IdentifierChain
 : Identifier
 | IdentifierChain '.' 'PARTIAL_CURSOR'
   {
     suggestColumns({
       identifierChain: parser.yy.identifierChain
     });
   }
 | IdentifierChain '.' Identifier
 ;

Identifier
 : 'REGULAR_IDENTIFIER'
   {
     parser.yy.identifierChain.push($1);
   }
 | '"' 'REGULAR_IDENTIFIER' '"'
   {
     parser.yy.identifierChain.push($2);
   }
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

LimitClause
 : 'LIMIT' 'UNSIGNED_INTEGER'
 | 'LIMIT' 'CURSOR'
   {
     suggestNumbers([5, 10, 15]);
   }
 ;

SelectList
 : ColumnList
 | '*' 'REGULAR_IDENTIFIER' 'PARTIAL_CURSOR' // TODO: Support partials differently, for instance remove before parsing
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

// Needs revising REGULAR_IDENTIFIER should be CHARACTER_PRIMARY
DerivedColumn
 : 'REGULAR_IDENTIFIER' '.' 'REGULAR_IDENTIFIER'
 | 'REGULAR_IDENTIFIER' '.' '*'
 | 'REGULAR_IDENTIFIER' '.' AnyCursor
   {
     parser.yy.result.suggestStar = true;
     suggestColumns({
       identifierChain: [ $1 ]
     });
   }
 | 'REGULAR_IDENTIFIER' 'PARTIAL_CURSOR'
   {
     suggestColumns();
     suggestTables({ prependQuestionMark: true, prependFrom: true });
     suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'REGULAR_IDENTIFIER'
 | 'CURSOR'
   {
     parser.yy.result.suggestStar = true;
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
 : 'REGULAR_IDENTIFIER'
   {
     addTableReference({ table: $1 });
   }
 | 'REGULAR_IDENTIFIER' 'REGULAR_IDENTIFIER'
   {
     addTableReference({ table: $1, alias: $2 });
   }
 | 'REGULAR_IDENTIFIER' '.' 'REGULAR_IDENTIFIER'
   {
     addTableReference({ database: $1, table: $3 });
   }
 | 'REGULAR_IDENTIFIER' '.' 'REGULAR_IDENTIFIER' 'REGULAR_IDENTIFIER'
   {
     addTableReference({ database: $1, table: $3, alias: $4 });
   }
 | 'REGULAR_IDENTIFIER' '.' AnyCursor
   {
     suggestTables({ database: $1 });
   }
 ;

JoinedTable
 : TableReference 'JOIN' TableReference JoinSpecification
 | TableReference 'JOIN' AnyCursor
   {
     suggestTables({});
     suggestDatabases({ appendDot: true });
   }
 ;

JoinSpecification
 : JoinCondition
 ;

JoinCondition
 : 'ON' SearchCondition
 ;

%%

var prioritizeSuggestions = function () {
   parser.yy.result.lowerCase = parser.yy.lowerCase || false;
   if (typeof parser.yy.result.suggestIdentifiers !== 'undefined' &&  parser.yy.result.suggestIdentifiers.length > 0) {
     delete parser.yy.result.suggestColumns;
     delete parser.yy.result.suggestTables;
     delete parser.yy.result.suggestDatabases;
     return;
   }
   if (typeof parser.yy.result.suggestColumns !== 'undefined') {
     if (typeof parser.yy.result.suggestColumns.table === 'undefined') {
       delete parser.yy.result.suggestColumns;
     } else {
       delete parser.yy.result.suggestTables;
       delete parser.yy.result.suggestDatabases;
     }
     return;
   }
}

var completeSuggestColumns = function () {
   if (parser.yy.cursorFound &&
       typeof parser.yy.result.suggestColumns !== 'undefined') {
     var identifierChain = parser.yy.result.suggestColumns.identifierChain;
     delete parser.yy.result.suggestColumns.identifierChain;
     var tableReferences = parser.yy.latestTableReferences;

     // IdentifierChain contains a possibly started identifier or empty, example: a.b.c = ['a', 'b', 'c']
     if (identifierChain.length > 0) {
       var foundTable = tableReferences.filter(function (tableRef) {
         return identifierChain[0] === tableRef.alias || identifierChain[0] === tableRef.table;
       })
       if (foundTable.length === 1) {
         tableReferences = foundTable;
       }
     }

     if (tableReferences.length === 1) {
       parser.yy.result.suggestColumns.table = tableReferences[0].table;
       if (typeof tableReferences[0].database !== 'undefined') {
         parser.yy.result.suggestColumns.database = tableReferences[0].database;
       }
     } else if (tableReferences.length > 1) {
       // Table identifier is required for column completion
       delete parser.yy.result.suggestColumns;
       parser.yy.result.suggestIdentifiers = [];
       tableReferences.forEach(function (tableRef) {
         parser.yy.result.suggestIdentifiers.push((tableRef.alias || tableRef.table) + '.');
       });
     }
   }
}

var addTableReference = function (ref) {
  if (typeof parser.yy.latestTableReferences === 'undefined') {
    parser.yy.latestTableReferences = [];
  }
  parser.yy.latestTableReferences.push(ref);
}

var suggestNumbers = function (numbers) {
  parser.yy.result.suggestNumbers = numbers;
}

var suggestKeywords = function (keywords) {
  parser.yy.result.suggestKeywords = keywords;
}

var suggestColumns = function (details) {
  parser.yy.result.suggestColumns = details || { identifierChain: [] };
}

var suggestTables = function (details) {
  parser.yy.result.suggestTables = details || {};
}

var suggestDatabases = function (details) {
  parser.yy.result.suggestDatabases = details || {};
}

var determineCase = function (text) {
  parser.yy.lowerCase = text.toLowerCase() === text;
};

/**
 * Main parser function
 */
parser.parseSql = function(beforeCursor, afterCursor, dialect) {
  var result;
  parser.yy.dialect = dialect;
  try {
    // Add |CURSOR| or |PARTIAL_CURSOR| to represent the different cursor states in the lexer
    result = parser.parse(beforeCursor + (beforeCursor.length == 0 || beforeCursor.indexOf(' ', beforeCursor.length - 1) !== -1 ? ' |CURSOR| ' : '|PARTIAL_CURSOR|') + afterCursor);
  } catch (err) {
    // On any error try to at least return any existing result
    if (typeof parser.yy.result === 'undefined') {
      throw err;
    }
    result = parser.yy.result;
  }

  return result;
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