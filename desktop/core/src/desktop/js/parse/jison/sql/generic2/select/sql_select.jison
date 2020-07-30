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

QuerySpecification
 : SelectStatement OptionalUnions                                   -> $1
 | CommonTableExpression SelectStatement OptionalUnions
 | CommonTableExpression '(' QuerySpecification ')' OptionalUnions  -> $3
 ;

QuerySpecification_EDIT
 : SelectStatement_EDIT OptionalUnions
 | SelectStatement OptionalUnions_EDIT
 | CommonTableExpression '(' QuerySpecification_EDIT ')'
   {
     parser.addCommonTableExpressions($1);
   }
 | CommonTableExpression SelectStatement_EDIT OptionalUnions
   {
     parser.addCommonTableExpressions($1);
   }
 | CommonTableExpression SelectStatement OptionalUnions_EDIT
   {
     parser.addCommonTableExpressions($1);
   }
 | CommonTableExpression_EDIT
 | CommonTableExpression_EDIT '(' QuerySpecification ')'
 | CommonTableExpression_EDIT SelectStatement OptionalUnions
 ;

SelectStatement
 : 'SELECT' OptionalAllOrDistinct SelectList
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     $$ = { selectList: $3 };
   }
 | 'SELECT' OptionalAllOrDistinct SelectList TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     $$ = { selectList: $3, tableExpression: $4 }
   }
 ;

OptionalUnions
 :
 | Unions
 ;

OptionalUnions_EDIT
 : Unions_EDIT
 ;

Unions
 : UnionClause
 | Unions UnionClause
 ;

Unions_EDIT
 : UnionClause_EDIT
 | Unions UnionClause_EDIT
 | UnionClause_EDIT Unions
 | Unions UnionClause_EDIT Unions
 ;

UnionClause
 : 'UNION' NewStatement OptionalAllOrDistinct SelectStatement
 ;

UnionClause_EDIT
 : 'UNION' NewStatement 'CURSOR'
   {
     parser.suggestKeywords(['ALL', 'DISTINCT', 'SELECT']);
   }
 | 'UNION' NewStatement 'CURSOR' SelectStatement
   {
     parser.suggestKeywords(['ALL', 'DISTINCT']);
   }
 | 'UNION' NewStatement OptionalAllOrDistinct SelectStatement_EDIT
 ;

SelectStatement_EDIT
 : 'SELECT' OptionalAllOrDistinct SelectList_EDIT
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     if ($3.cursorAtStart) {
       var keywords = parser.getSelectListKeywords();
       if (!$2) {
         keywords.push({ value: 'ALL', weight: 2 });
         keywords.push({ value: 'DISTINCT', weight: 2 });
       }
       parser.suggestKeywords(keywords);
     } else {
       parser.checkForSelectListKeywords($3);
     }
     if ($3.suggestFunctions) {
       parser.suggestFunctions();
     }
     if ($3.suggestColumns) {
       parser.suggestColumns({ identifierChain: [], source: 'select' });
     }
     if ($3.suggestTables) {
       parser.suggestTables({ prependQuestionMark: true, prependFrom: true });
     }
     if ($3.suggestDatabases) {
       parser.suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
     }
     if ($3.suggestAggregateFunctions && (!$2 || $2 === 'ALL')) {
       parser.suggestAggregateFunctions();
       parser.suggestAnalyticFunctions();
     }
   }
 | 'SELECT' OptionalAllOrDistinct 'CURSOR'
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3, true);
     var keywords = parser.getSelectListKeywords();
     if (!$2 || $2 === 'ALL') {
       parser.suggestAggregateFunctions();
       parser.suggestAnalyticFunctions();
     }
     if (!$2) {
       keywords.push({ value: 'ALL', weight: 2 });
       keywords.push({ value: 'DISTINCT', weight: 2 });
     }
     parser.suggestKeywords(keywords);
     parser.suggestFunctions();
     parser.suggestColumns({ identifierChain: [], source: 'select' });
     parser.suggestTables({ prependQuestionMark: true, prependFrom: true });
     parser.suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'SELECT' OptionalAllOrDistinct SelectList TableExpression_EDIT
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList_EDIT TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     parser.selectListNoTableSuggest($3, $2);
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'select';
     }
   }
 | 'SELECT' OptionalAllOrDistinct 'CURSOR' TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3, true);
     var keywords = parser.getSelectListKeywords();
     if (!$2 || $2 === 'ALL') {
       parser.suggestAggregateFunctions();
       parser.suggestAnalyticFunctions();
     }
     if (!$2) {
       keywords.push({ value: 'ALL', weight: 2 });
       keywords.push({ value: 'DISTINCT', weight: 2 });
     }
     parser.suggestKeywords(keywords);
     parser.suggestFunctions();
     parser.suggestColumns({ identifierChain: [], source: 'select' });
     parser.suggestTables({ prependQuestionMark: true, prependFrom: true });
     parser.suggestDatabases({ prependQuestionMark: true, prependFrom: true, appendDot: true });
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     parser.checkForSelectListKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR' ',' TableExpression
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     parser.checkForSelectListKeywords($3);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList 'CURSOR'
   {
     parser.addClauseLocation('selectList', parser.firstDefined($2, @2, $1, @1), @3);
     parser.checkForSelectListKeywords($3);
     var keywords = ['FROM'];
     if (parser.yy.result.suggestKeywords) {
       keywords = parser.yy.result.suggestKeywords.concat(keywords);
     }
     parser.suggestKeywords(keywords);
     parser.suggestTables({ prependFrom: true });
     parser.suggestDatabases({ prependFrom: true, appendDot: true });
   }
 ;

CommonTableExpression
 : 'WITH' WithQueries  -> $2
 ;

CommonTableExpression_EDIT
 : 'WITH' WithQueries_EDIT
 ;

WithQueries
 : WithQuery                   -> [$1]
 | WithQueries ',' WithQuery   -> $1.concat([$3])
 ;

WithQueries_EDIT
 : WithQuery_EDIT
 | WithQueries ',' WithQuery_EDIT
   {
     parser.addCommonTableExpressions($1);
   }
 | WithQuery_EDIT ',' WithQueries
 | WithQueries ',' WithQuery_EDIT ',' WithQueries
   {
     parser.addCommonTableExpressions($1);
   }
 ;

WithQuery
 : RegularOrBacktickedIdentifier 'AS' '(' TableSubQueryInner ')'
   {
     parser.addCteAliasLocation(@1, $1);
     $4.alias = $1;
     $$ = $4;
   }
 ;

WithQuery_EDIT
 : RegularOrBacktickedIdentifier 'CURSOR'
   {
     parser.suggestKeywords(['AS']);
   }
 | RegularOrBacktickedIdentifier 'AS' '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestKeywords(['SELECT']);
   }
 | RegularOrBacktickedIdentifier 'AS' '(' TableSubQueryInner_EDIT RightParenthesisOrError
 ;

OptionalAllOrDistinct
 :
 | 'ALL'
 | 'DISTINCT'
 ;

TableExpression
 : FromClause OptionalSelectConditions
   {
     parser.addClauseLocation('whereClause', @1, $2.whereClauseLocation);
     parser.addClauseLocation('limitClause', $2.limitClausePreceding || @1, $2.limitClauseLocation);
   }
 ;

TableExpression_EDIT
 : FromClause_EDIT OptionalSelectConditions
   {
     parser.addClauseLocation('whereClause', @1, $2.whereClauseLocation);
     parser.addClauseLocation('limitClause', $2.limitClausePreceding || @1, $2.limitClauseLocation);
   }
 | FromClause 'CURSOR' OptionalSelectConditions OptionalJoins
   {
     var keywords = [];

     parser.addClauseLocation('whereClause', @1, $3.whereClauseLocation);
     parser.addClauseLocation('limitClause', $2.limitClausePreceding || @1, $2.limitClauseLocation);

     if ($1) {
       if (typeof $1.tableReferenceList.hasJoinCondition !== 'undefined' && !$1.tableReferenceList.hasJoinCondition) {
         keywords.push({ value: 'ON', weight: 3 });
       }
       if ($1.suggestKeywords) {
         keywords = parser.createWeightedKeywords($1.suggestKeywords, 3);
       }
       if ($1.tableReferenceList.suggestJoinConditions) {
         parser.suggestJoinConditions($1.tableReferenceList.suggestJoinConditions);
       }
       if ($1.tableReferenceList.suggestJoins) {
         parser.suggestJoins($1.tableReferenceList.suggestJoins);
       }
       if ($1.tableReferenceList.suggestKeywords) {
         keywords = keywords.concat(parser.createWeightedKeywords($1.tableReferenceList.suggestKeywords, 3));
       }

       // Lower the weights for 'TABLESAMPLE'
       keywords.forEach(function (keyword) {
         if (keyword.value === 'TABLESAMPLE') {
           keyword.weight = 1.1;
         }
       });

       if ($1.tableReferenceList.types) {
         var veKeywords = parser.getValueExpressionKeywords($1.tableReferenceList);
         keywords = keywords.concat(veKeywords.suggestKeywords);
         if (veKeywords.suggestColRefKeywords) {
           parser.suggestColRefKeywords(veKeywords.suggestColRefKeywords);
           parser.addColRefIfExists($1.tableReferenceList);
         }
       }
     }

     if ($3.empty && $4 && $4.joinType.toUpperCase() === 'JOIN') {
       keywords = keywords.concat(['FULL', 'FULL OUTER', 'INNER', 'LEFT', 'LEFT OUTER', 'RIGHT', 'RIGHT OUTER']);
       parser.suggestKeywords(keywords);
       return;
     }

     if ($3.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($3.suggestKeywords, 2));
     }

     if ($3.suggestFilters) {
       parser.suggestFilters($3.suggestFilters);
     }
     if ($3.suggestGroupBys) {
       parser.suggestGroupBys($3.suggestGroupBys);
     }
     if ($3.suggestOrderBys) {
       parser.suggestOrderBys($3.suggestOrderBys);
     }

     if ($3.empty) {
       keywords.push({ value: 'UNION', weight: 2.11 });
     }

     keywords = keywords.concat([
       { value: 'FULL JOIN', weight: 1 },
       { value: 'FULL OUTER JOIN', weight: 1 },
       { value: 'INNER JOIN', weight: 1 },
       { value: 'JOIN', weight: 1 },
       { value: 'LEFT JOIN', weight: 1 },
       { value: 'LEFT OUTER JOIN', weight: 1 },
       { value: 'RIGHT JOIN', weight: 1 },
       { value: 'RIGHT OUTER JOIN', weight: 1 }
     ]);
     parser.suggestKeywords(keywords);
  }
 | FromClause OptionalSelectConditions_EDIT OptionalJoins
   {
     // A couple of things are going on here:
     // - If there are no SelectConditions (WHERE, GROUP BY, etc.) we should suggest complete join options
     // - If there's an OptionalJoin at the end, i.e. 'SELECT * FROM foo | JOIN ...' we should suggest
     //   different join types
     // - The FromClause could end with a valueExpression, in which case we should suggest keywords like '='
     //   or 'AND' based on type

     if (!$2) {
       parser.addClauseLocation('whereClause', @1);
       parser.addClauseLocation('limitClause', @1);
       return;
     }
     parser.addClauseLocation('whereClause', @1, $2.whereClauseLocation);
     parser.addClauseLocation('limitClause', $2.limitClausePreceding || @1, $2.limitClauseLocation);
     var keywords = [];

     if ($2.suggestColRefKeywords) {
       parser.suggestColRefKeywords($2.suggestColRefKeywords);
       parser.addColRefIfExists($2);
     }

     if ($2.suggestKeywords && $2.suggestKeywords.length) {
       keywords = keywords.concat(parser.createWeightedKeywords($2.suggestKeywords, 2));
     }

     if ($2.cursorAtEnd) {
       keywords.push({ value: 'UNION', weight: 2.11 });
     }
     parser.suggestKeywords(keywords);
   }
 ;

OptionalJoins
 :
 | Joins
 | Joins_INVALID
 ;

FromClause
 : 'FROM' TableReferenceList
   {
     $$ = { tableReferenceList : $2 }
   }
 ;

FromClause_EDIT
 : 'FROM' 'CURSOR'
   {
       parser.suggestTables();
       parser.suggestDatabases({ appendDot: true });
   }
 | 'FROM' TableReferenceList_EDIT
 ;

OptionalSelectConditions
 : OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalOrderByClause OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$1, $2, $3, $4, $5],
       [{ value: 'WHERE', weight: 7 }, { value: 'GROUP BY', weight: 6 }, { value: 'HAVING', weight: 5 }, { value: 'ORDER BY', weight: 4 }, { value: 'LIMIT', weight: 3 }],
       [true, true, true, true, true]);

     if (keywords.length > 0) {
       $$ = { suggestKeywords: keywords, empty: !$1 && !$2 && !$3 && !$4 && !$5 };
     } else {
       $$ = {};
     }

     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($4, @4, $3, @3, $2, @2, $1, @1);
     $$.limitClauseLocation = $5 ? @5 : undefined;

     if (!$1 && !$2 && !$3 && !$4 && !$5) {
       $$.suggestFilters = { prefix: 'WHERE', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
     if (!$2 && !$3 && !$4 && !$5) {
       $$.suggestGroupBys = { prefix: 'GROUP BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
     if (!$4 && !$5) {
       $$.suggestOrderBys = { prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() };
     }
   }
 ;

OptionalSelectConditions_EDIT
 : WhereClause_EDIT OptionalGroupByClause OptionalHavingClause OptionalOrderByClause OptionalLimitClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'where';
     }
   }
 | OptionalWhereClause GroupByClause_EDIT OptionalHavingClause OptionalOrderByClause OptionalLimitClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'group by';
     }
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause_EDIT OptionalOrderByClause OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OrderByClause_EDIT OptionalLimitClause
   {
     if (parser.yy.result.suggestColumns) {
       parser.yy.result.suggestColumns.source = 'order by';
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalOrderByClause LimitClause_EDIT
 ;

OptionalSelectConditions_EDIT
 : WhereClause 'CURSOR' OptionalGroupByClause OptionalHavingClause OptionalOrderByClause OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$3, $4, $5, $6],
       [{ value: 'GROUP BY', weight: 8 }, { value: 'HAVING', weight: 7 }, { value: 'ORDER BY', weight: 5 }, { value: 'LIMIT', weight: 3 }],
       [true, true, true, true]);
     if ($1.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($1.suggestKeywords, 1));
     }
     $$ = parser.getValueExpressionKeywords($1, keywords);
     $$.cursorAtEnd = !$3 && !$4 && !$5 && !$6;
     if ($1.columnReference) {
       $$.columnReference = $1.columnReference;
     }
     if (!$3) {
       parser.suggestGroupBys({ prefix: 'GROUP BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     if (!$3 && !$4 && !$5) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($5, @5, $4, @4, $3, @3, $1, @1);
     $$.limitClauseLocation = $6 ? @6 : undefined;
   }
 | OptionalWhereClause GroupByClause 'CURSOR' OptionalHavingClause OptionalOrderByClause OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$4, $5, $6],
       [{ value: 'HAVING', weight: 7 }, { value: 'ORDER BY', weight: 5 }, { value: 'LIMIT', weight: 3 }],
       [true, true, true]);
     if ($2.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($2.suggestKeywords, 8));
     }
     if ($2.valueExpression) {
       $$ = parser.getValueExpressionKeywords($2.valueExpression, keywords);
       if ($2.valueExpression.columnReference) {
         $$.columnReference = $2.valueExpression.columnReference;
       }
     } else {
       $$ = { suggestKeywords: keywords };
     }
     $$.cursorAtEnd = !$4 && !$5 && !$6;
     if (!$4 && !$5) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($5, @5, $4, @4, $2, @2);
     $$.limitClauseLocation = $6 ? @6 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause 'CURSOR' OptionalOrderByClause OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$5, $6],
       [{ value: 'ORDER BY', weight: 5 }, { value: 'LIMIT', weight: 3 }],
       [true, true]);
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$5 && !$6 };
     if (!$5) {
       parser.suggestOrderBys({ prefix: 'ORDER BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($5, @5, $3, @3);
     $$.limitClauseLocation = $6 ? @6 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OrderByClause 'CURSOR' OptionalLimitClause
   {
     var keywords = parser.getKeywordsForOptionalsLR(
       [$6],
       [{ value: 'LIMIT', weight: 3 }],
       [true]);
     if ($4.suggestKeywords) {
       keywords = keywords.concat(parser.createWeightedKeywords($4.suggestKeywords, 4));
     }
     $$ = { suggestKeywords: keywords, cursorAtEnd: !$6 };
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($4, @4);
     $$.limitClauseLocation = $6 ? @6 : undefined;
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalOrderByClause LimitClause 'CURSOR'
   {
     $$ = { suggestKeywords: [], cursorAtEnd: true };
     $$.whereClauseLocation = $1 ? @1 : undefined;
     $$.limitClausePreceding = parser.firstDefined($4, @4, $3, @3, $2, @2, $1, @1);
     $$.limitClauseLocation = @5;
   }
 ;

OptionalWhereClause
 :
 | WhereClause
 ;

WhereClause
 : 'WHERE' SearchCondition  -> $2
 ;

WhereClause_EDIT
 : 'WHERE' SearchCondition_EDIT
   {
     if ($2.suggestFilters) {
       parser.suggestFilters({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
   }
 | 'WHERE' 'CURSOR'
   {
     parser.suggestFunctions();
     parser.suggestColumns();
     parser.suggestKeywords(['EXISTS', 'NOT EXISTS']);
     parser.suggestFilters({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 ;

OptionalGroupByClause
 :
 | GroupByClause
 ;

GroupByClause
 : 'GROUP' 'BY' GroupByColumnList
   {
     $$ = { valueExpression: $3 };
   }
 ;

GroupByClause_EDIT
 : 'GROUP' 'BY' GroupByColumnList_EDIT
   {
     parser.suggestSelectListAliases();
   }
 | 'GROUP' 'BY' 'CURSOR'
   {
     parser.valueExpressionSuggest();
     parser.suggestSelectListAliases();
     parser.suggestGroupBys({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 | 'GROUP' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
     parser.suggestGroupBys({ prefix: 'BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 ;

ColumnGroupingSets
 :
 | ColumnReference
 | ColumnGroupingSets ',' ColumnGroupingSets
 | '(' ColumnGroupingSets ')'
 ;

ColumnGroupingSets_EDIT
 : ColumnGroupingSet_EDIT
 | ColumnGroupingSet_EDIT ',' ColumnGroupingSets
 | ColumnGroupingSets ',' ColumnGroupingSet_EDIT
 | ColumnGroupingSets ',' ColumnGroupingSet_EDIT ',' ColumnGroupingSets
 | '(' ColumnGroupingSets_EDIT RightParenthesisOrError
 ;

ColumnGroupingSet_EDIT
 : AnyCursor
   {
     parser.suggestColumns();
   }
 | ColumnReference_EDIT
 ;

GroupByColumnList
 : ValueExpression
 | GroupByColumnList ',' ValueExpression  -> $3
 ;

GroupByColumnList_EDIT
 : ValueExpression_EDIT
 | 'CURSOR' ValueExpression
   {
     parser.valueExpressionSuggest();
   }
 | 'CURSOR' ',' GroupByColumnList
   {
     parser.valueExpressionSuggest();
   }
 | ValueExpression_EDIT ',' GroupByColumnList
 | GroupByColumnList ',' GroupByColumnListPartTwo_EDIT
 | GroupByColumnList ',' GroupByColumnListPartTwo_EDIT ','
 | GroupByColumnList ',' GroupByColumnListPartTwo_EDIT ',' GroupByColumnList
 ;

GroupByColumnListPartTwo_EDIT
 : ValueExpression_EDIT
 | AnyCursor ValueExpression
   {
     parser.valueExpressionSuggest();
   }
 | AnyCursor
   {
     parser.valueExpressionSuggest();
   }
 ;

OptionalOrderByClause
 :
 | OrderByClause
 ;

OrderByClause
 : 'ORDER' 'BY' OrderByColumnList  -> $3
 ;

OrderByClause_EDIT
 : 'ORDER' 'BY' OrderByColumnList_EDIT
   {
     if ($3.emptyOrderBy) {
       parser.suggestOrderBys({ tablePrimaries: parser.yy.latestTablePrimaries.concat() });
     }
   }
 | 'ORDER' 'CURSOR'
   {
     parser.suggestKeywords(['BY']);
     parser.suggestOrderBys({ prefix: 'BY', tablePrimaries: parser.yy.latestTablePrimaries.concat() });
   }
 ;

OrderByColumnList
 : OrderByIdentifier
 | OrderByColumnList ',' OrderByIdentifier  -> $3
 ;

OrderByColumnList_EDIT
 : OrderByIdentifier_EDIT
 | 'CURSOR' OrderByIdentifier
   {
     $$ = { emptyOrderBy: false }
     parser.valueExpressionSuggest();
     parser.suggestAnalyticFunctions();
     parser.suggestSelectListAliases();
   }
 | OrderByColumnList ',' OrderByIdentifier_EDIT                        -> { emptyOrderBy: false }
 | OrderByColumnList ',' OrderByIdentifier_EDIT ','                    -> { emptyOrderBy: false }
 | OrderByColumnList ',' OrderByIdentifier_EDIT ',' OrderByColumnList  -> { emptyOrderBy: false }
 ;

OrderByIdentifier
 : ValueExpression OptionalAscOrDesc  -> parser.mergeSuggestKeywords($2)
 ;

OrderByIdentifier_EDIT
 : ValueExpression_EDIT OptionalAscOrDesc
   {
     parser.suggestSelectListAliases();
   }
 | AnyCursor OptionalAscOrDesc
   {
     $$ = { emptyOrderBy: true }
     parser.valueExpressionSuggest();
     parser.suggestAnalyticFunctions();
     parser.suggestSelectListAliases();
   }
 ;

OptionalAscOrDesc
 :                          -> { suggestKeywords: ['ASC', 'DESC'] };
 | 'ASC'
 | 'DESC'
 ;

OptionalLimitClause
 :
 | LimitClause
 ;

LimitClause
 : 'LIMIT' UnsignedNumericLiteral
 | 'LIMIT' UnsignedNumericLiteral ',' UnsignedNumericLiteral
 | 'LIMIT' 'VARIABLE_REFERENCE'
 | 'LIMIT' 'VARIABLE_REFERENCE' ',' 'VARIABLE_REFERENCE'
 ;

LimitClause_EDIT
 : 'LIMIT' 'CURSOR'
   {
     parser.suggestKeywords([{ value: '10', weight: 10000 }, { value: '100', weight: 10000 }, { value: '1000', weight: 10000 }, { value: '5000', weight: 10000 }, { value: '10000', weight: 10000 }])
   }
 ;

SearchCondition
 : ValueExpression
 ;

SearchCondition_EDIT
 : ValueExpression_EDIT
 ;


SelectSpecification
 : ValueExpression OptionalCorrelationName
   {
     if ($2) {
       parser.addColumnAliasLocation($2.location, $2.alias, @1);
       $$ = { valueExpression: $1, alias: $2.alias };
       if (!parser.yy.selectListAliases) {
         parser.yy.selectListAliases = [];
       }
       parser.yy.selectListAliases.push($1.function && $1.types && $1.types.length && $1.types[0] === 'UDFREF' ? { name: $2.alias, udfRef: $1.function, types: $1.types } : { name: $2.alias, types: $1.types || ['T'] });
     } else {
       $$ = { valueExpression: $1 }
     }
   }
 | '*'
   {
     parser.addAsteriskLocation(@1, [{ asterisk: true }]);
     $$ = { asterisk: true }
   }
 ;

SelectSpecification_EDIT
 : ValueExpression_EDIT OptionalCorrelationName
   {
     if ($2) {
       parser.addColumnAliasLocation($2.location, $2.alias, @1);
     }
   }

 | AnyCursor 'AS' RegularOrBacktickedIdentifier
   {
     parser.suggestFunctions();
     parser.suggestColumns();
     parser.addColumnAliasLocation(@3, $3, @1);
     $$ = { suggestAggregateFunctions: true };
   }
 | ValueExpression OptionalCorrelationName_EDIT  -> $2
 ;

SelectList
 : SelectSpecification                 -> [ $1 ]
 | SelectList ',' SelectSpecification
   {
     $1.push($3);
   }
 ;

SelectList_EDIT
 : SelectSpecification_EDIT
 | 'CURSOR' SelectList
   {
     $$ = { cursorAtStart : true, suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true };
   }
 | 'CURSOR' ',' SelectList
   {
     $$ = { cursorAtStart : true, suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true };
   }
 | SelectSpecification_EDIT ',' SelectList
 | SelectList 'CURSOR' SelectList
   {
     parser.checkForSelectListKeywords($1);
   }
 | SelectList 'CURSOR' ',' SelectList
   {
     parser.checkForSelectListKeywords($1);
   }
 | SelectList ',' AnyCursor
   {
     $$ = { suggestKeywords: parser.getSelectListKeywords(), suggestTables: true, suggestDatabases: true, suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true };
   }
 | SelectList ',' SelectSpecification_EDIT                 -> $3
 | SelectList ',' AnyCursor SelectList
   {
     $$ = { suggestKeywords: parser.getSelectListKeywords(), suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true,  };
   }
 | SelectList ',' AnyCursor ','
   {
     $$ = { suggestKeywords: parser.getSelectListKeywords(), suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true,  };
   }
 | SelectList ',' SelectSpecification_EDIT ','             -> $3
 | SelectList ',' AnyCursor ',' SelectList
   {
     $$ = { suggestKeywords: parser.getSelectListKeywords(), suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true,  };
   }
 | SelectList ',' SelectSpecification_EDIT ',' SelectList  -> $3
 ;

TableReferenceList
 : TableReference
 | TableReferenceList ',' TableReference  -> $3
 ;

TableReferenceList_EDIT
 : TableReference_EDIT
 | TableReference_EDIT ',' TableReference
 | TableReferenceList ',' TableReference_EDIT
 | TableReferenceList ',' TableReference_EDIT ',' TableReferenceList
 | TableReferenceList ',' AnyCursor
   {
       parser.suggestTables();
       parser.suggestDatabases({ appendDot: true });
   }
 ;
