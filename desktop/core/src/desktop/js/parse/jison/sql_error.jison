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
     if (parser.isHive()) {
       parser.suggestDdlAndDmlKeywords(['EXPLAIN', 'FROM']);
     } else if (parser.isImpala()) {
       parser.suggestDdlAndDmlKeywords(['EXPLAIN']);
     } else {
       parser.suggestDdlAndDmlKeywords();
     }
   }
 ;

SelectStatement
 : 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList_ERROR TableExpression
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList TableExpression_ERROR
 ;

SelectStatement_EDIT
 : 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList_ERROR_EDIT TableExpression
   {
     parser.selectListNoTableSuggest($4, $2);
   }
 | 'SELECT' OptionalAllOrDistinct OptionalStraightJoin SelectList_ERROR TableExpression_EDIT
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
 : '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction RegularOrBacktickedIdentifier '<hive>AS' error  -> { }
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter ArbitraryFunction error                                           -> { }
 | '<hive>LATERAL' '<hive>VIEW' OptionalOuter error                                                               -> { }
 | '<hive>LATERAL' error                                                                                          -> { }
 ;

JoinType_EDIT
 : 'FULL' 'CURSOR' error
   {
     parser.suggestKeywords(['JOIN', 'OUTER JOIN']);
   }
 | 'LEFT' 'CURSOR' error
   {
     if (parser.isHive()) {
       parser.suggestKeywords(['JOIN', 'OUTER JOIN', 'SEMI JOIN']);
     } else if (parser.isImpala()) {
       parser.suggestKeywords(['ANTI JOIN', 'INNER JOIN', 'JOIN', 'OUTER JOIN', 'SEMI JOIN']);
     } else {
       parser.suggestKeywords(['JOIN', 'OUTER JOIN']);
     }
   }
 | 'RIGHT' 'CURSOR' error
   {
     if (parser.isImpala()) {
       parser.suggestKeywords(['ANTI JOIN', 'INNER JOIN', 'JOIN', 'OUTER JOIN', 'SEMI JOIN']);
     } else {
       parser.suggestKeywords(['JOIN', 'OUTER JOIN']);
     }
   }
 ;

OptionalSelectConditions_EDIT
 : WhereClause error 'CURSOR' OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$4, $5, $6, $7, $8, $9, $10], [{ value: 'GROUP BY', weight: 8 }, { value: 'HAVING', weight: 7 }, { value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, true, parser.isHive(), true, parser.isHive(), true, parser.isImpala()]),
       cursorAtEnd: !$4 && !$5 && !$6 && !$7 && !$8 && !$9 && !$10
     };
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause error 'CURSOR' OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$6, $7, $8, $9, $10], [{ value: 'WINDOW', weight: 6 }, { value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [parser.isHive(), true, parser.isHive(), true, parser.isImpala()]),
       cursorAtEnd: !$6 && !$7 && !$8 && !$9 && !$10
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause error 'CURSOR' OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$7, $8, $9, $10], [{ value: 'ORDER BY', weight: 5 }, [{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, parser.isHive(), true, parser.isImpala()]),
       cursorAtEnd: !$7 && !$8 && !$9 && !$10
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause error 'CURSOR' OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$8, $9, $10], [[{ value: 'CLUSTER BY', weight: 4 }, { value: 'DISTRIBUTE BY', weight: 4 }, { value: 'SORT BY', weight: 4 }], { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [parser.isHive(), true, parser.isImpala()]),
       cursorAtEnd: !$8 && !$9 && !$10
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy error 'CURSOR' OptionalLimitClause OptionalOffsetClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$9, $10], [{ value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, parser.isImpala()]),
       cursorAtEnd: !$9 && !$10
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause error 'CURSOR' OptionalOffsetClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$10], [{ value: 'OFFSET', weight: 2 }], [parser.isImpala()]),
       cursorAtEnd: !$10
     }
   }
 ;

OptionalSelectConditions_EDIT
 : WhereClause error GroupByClause_EDIT OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | WhereClause error OptionalGroupByClause HavingClause_EDIT OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause WindowClause_EDIT OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause_EDIT OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy_EDIT OptionalLimitClause OptionalOffsetClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause_EDIT OptionalOffsetClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OffsetClause_EDIT
 | OptionalWhereClause GroupByClause error HavingClause_EDIT OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause WindowClause_EDIT OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause OptionalWindowClause OrderByClause_EDIT OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy_EDIT OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause_EDIT OptionalOffsetClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OffsetClause_EDIT
 | OptionalWhereClause OptionalGroupByClause HavingClause error WindowClause_EDIT OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause HavingClause error OptionalWindowClause OrderByClause_EDIT OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause HavingClause error OptionalWindowClause OptionalOrderByClause ClusterOrDistributeBy_EDIT OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause HavingClause error OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause_EDIT OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause HavingClause error OptionalWindowClause OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OffsetClause_EDIT
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause error OrderByClause_EDIT OptionalClusterOrDistributeBy OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause error OptionalOrderByClause ClusterOrDistributeBy_EDIT OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause error OptionalOrderByClause OptionalClusterOrDistributeBy LimitClause_EDIT OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause WindowClause error OptionalOrderByClause OptionalClusterOrDistributeBy OptionalLimitClause OffsetClause_EDIT
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause error ClusterOrDistributeBy_EDIT OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause error OptionalClusterOrDistributeBy LimitClause_EDIT OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalWindowClause OrderByClause error OptionalClusterOrDistributeBy OptionalLimitClause OffsetClause_EDIT
 ;

DatabaseDefinition_EDIT
 : AnyCreate DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals_EDIT error
 ;
