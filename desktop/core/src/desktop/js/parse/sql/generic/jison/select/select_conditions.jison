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
