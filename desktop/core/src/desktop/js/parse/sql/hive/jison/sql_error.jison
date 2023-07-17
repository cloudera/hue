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

SqlStatements
 : error
 | NonStartingToken error // Having just ': error' does not work for some reason, jison bug?
 ;

SqlStatement_EDIT
 : AnyCursor error
   {
     parser.suggestDdlAndDmlKeywords(['EXPLAIN', 'FROM']);
   }
 ;

SelectStatement
 : 'SELECT' OptionalAllOrDistinct SelectList_ERROR TableExpression
 | 'SELECT' OptionalAllOrDistinct SelectList TableExpression_ERROR
 ;

SelectStatement_EDIT
 : 'SELECT' OptionalAllOrDistinct SelectList_ERROR_EDIT TableExpression
   {
     parser.selectListNoTableSuggest($3, $2);
   }
 | 'SELECT' OptionalAllOrDistinct SelectList_ERROR TableExpression_EDIT
 ;

SelectList_ERROR
 : ErrorList
 | SelectList ',' ErrorList
 | ErrorList ',' SelectList ',' ErrorList
 | ErrorList ',' SelectList
 | SelectList ',' ErrorList ',' SelectList
 ;

SelectList_ERROR_EDIT
 : ErrorList ',' SelectList_EDIT                               -> $3
 | SelectList ',' ErrorList ',' SelectList_EDIT                -> $5
 | ErrorList ',' SelectList ',' ErrorList ',' SelectList_EDIT  -> $7
 | ErrorList ',' AnyCursor
   {
     $$ = { cursorAtStart : false, suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true };
   }
 | SelectList ',' ErrorList ',' AnyCursor
   {
     $$ = { cursorAtStart : false, suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true };
   }
 | ErrorList ',' SelectList ',' Errors ',' AnyCursor
   {
     $$ = { cursorAtStart : true, suggestFunctions: true, suggestColumns: true, suggestAggregateFunctions: true };
   }
 ;

SetSpecification
 : 'SET' SetOption '=' error
 ;

ErrorList
 : error
 | Errors ',' error
 ;

LateralView
 : 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction RegularOrBacktickedIdentifier 'AS' error  -> { }
 | 'LATERAL' 'VIEW' OptionalOuter ArbitraryFunction error                                           -> { }
 | 'LATERAL' 'VIEW' OptionalOuter error                                                               -> { }
 | 'LATERAL' error                                                                                          -> { }
 ;

JoinType_EDIT
 : 'FULL' 'CURSOR' error
   {
     parser.suggestKeywords(['JOIN', 'OUTER JOIN']);
   }
 | 'LEFT' 'CURSOR' error
   {
     parser.suggestKeywords(['JOIN', 'OUTER JOIN', 'SEMI JOIN']);
   }
 | 'RIGHT' 'CURSOR' error
   {
     parser.suggestKeywords(['JOIN', 'OUTER JOIN']);
   }
 ;

OptionalSelectConditions_EDIT
 : WhereClause error 'CURSOR' OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$4, $5, $6, $7, $8, $9], [{ value: 'GROUP BY', weight: 8 }, { value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }], [true, true, true, true, true, true]),
       cursorAtEnd: !$4 && !$5 && !$6 && !$7 && !$8 && !$9
     };
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause error 'CURSOR' OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$6, $7, $8, $9], [{ value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }], [true, true, true, true]),
       cursorAtEnd: !$6 && !$7 && !$8 && !$9
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause error 'CURSOR' OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$7, $8, $9], [{ value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }], [true, true, true]),
       cursorAtEnd: !$7 && !$8 && !$9
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause error 'CURSOR' OptionalClusterOrDistributeBy OptionalLimitClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$8, $9], [[{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }], [true, true]),
       cursorAtEnd: !$8 && !$9
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy error 'CURSOR' OptionalLimitClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$9], [{ value: 'LIMIT', weight: 3 }], [true]),
       cursorAtEnd: !$9
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause error 'CURSOR'
   {
     $$ = {
       suggestKeywords: [],
       cursorAtEnd: true
     }
   }
 ;

OptionalSelectConditions_EDIT
 : WhereClause error GroupByClause_EDIT OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
 | WhereClause error OptionalGroupByClause HavingClause_EDIT OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause WindowClause_EDIT OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause_EDIT OptionalClusterOrDistributeBy OptionalLimitClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy_EDIT OptionalLimitClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause_EDIT
 | OptionalWhereClause GroupByClause error HavingClause_EDIT OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause WindowClause_EDIT OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause OptionalWindowClause OrderByClause_EDIT OptionalClusterOrDistributeBy OptionalLimitClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy_EDIT OptionalLimitClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause_EDIT
 | OptionalWhereClause OptionalGroupByClause HavingClause error WindowClause_EDIT OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause HavingClause error OptionalWindowClause OrderByClause_EDIT OptionalClusterOrDistributeBy OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause HavingClause error OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy_EDIT OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause HavingClause error OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause_EDIT
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause error OrderByClause_EDIT OptionalClusterOrDistributeBy OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause error OptionalOrderByClause ClusterOrDistributeBy_EDIT OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause error OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause_EDIT
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause error ClusterOrDistributeBy_EDIT OptionalLimitClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause error OptionalClusterOrDistributeBy LimitClause_EDIT
 ;

DatabaseDefinition_EDIT
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals_EDIT error
 ;
