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
     parser.suggestDdlAndDmlKeywords(['EXPLAIN']);
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

JoinType_EDIT
 : 'FULL' 'CURSOR' error
   {
     parser.suggestKeywords(['JOIN', 'OUTER JOIN']);
   }
 | 'LEFT' 'CURSOR' error
   {
     parser.suggestKeywords(['ANTI JOIN', 'INNER JOIN', 'JOIN', 'OUTER JOIN', 'SEMI JOIN']);
   }
 | 'RIGHT' 'CURSOR' error
   {
     parser.suggestKeywords(['ANTI JOIN', 'INNER JOIN', 'JOIN', 'OUTER JOIN', 'SEMI JOIN']);
   }
 ;

OptionalSelectConditions_EDIT
 : WhereClause error 'CURSOR' OptionalGroupByClause OptionalHavingClause OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$4, $5, $6, $7, $8], [{ value: 'GROUP BY', weight: 6 }, { value: 'HAVING', weight: 5 }, { value: 'ORDER BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, true, true, true, true]),
       cursorAtEnd: !$4 && !$5 && !$6 && !$7 && !$8
     };
   }
 | OptionalWhereClause OptionalGroupByClause HavingClause error 'CURSOR' OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$6, $7, $8], [{ value: 'ORDER BY', weight: 4 }, { value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, true, true]),
       cursorAtEnd: !$6 && !$7 && !$8
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OrderByClause error 'CURSOR' OptionalLimitClause OptionalOffsetClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$7, $8], [{ value: 'LIMIT', weight: 3 }, { value: 'OFFSET', weight: 2 }], [true, true]),
       cursorAtEnd: !$7 && !$8
     }
   }
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OptionalOrderByClause LimitClause error 'CURSOR' OptionalOffsetClause
   {
     $$ = {
       suggestKeywords: parser.getKeywordsForOptionalsLR([$8], [{ value: 'OFFSET', weight: 2 }], [true]),
       cursorAtEnd: !$8
     }
   }
 ;

OptionalSelectConditions_EDIT
 : WhereClause error GroupByClause_EDIT OptionalHavingClause OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
 | WhereClause error OptionalGroupByClause HavingClause_EDIT OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause OrderByClause_EDIT OptionalLimitClause OptionalOffsetClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause OptionalOrderByClause LimitClause_EDIT OptionalOffsetClause
 | WhereClause error OptionalGroupByClause OptionalHavingClause OptionalOrderByClause OptionalLimitClause OffsetClause_EDIT
 | OptionalWhereClause GroupByClause error HavingClause_EDIT OptionalOrderByClause OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause OrderByClause_EDIT OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause OptionalOrderByClause LimitClause_EDIT OptionalOffsetClause
 | OptionalWhereClause GroupByClause error OptionalHavingClause OptionalOrderByClause OptionalLimitClause OffsetClause_EDIT
 | OptionalWhereClause OptionalGroupByClause HavingClause error OrderByClause_EDIT OptionalLimitClause OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause HavingClause error OptionalOrderByClause LimitClause_EDIT OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause HavingClause error OptionalOrderByClause OptionalLimitClause OffsetClause_EDIT
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OrderByClause error LimitClause_EDIT OptionalOffsetClause
 | OptionalWhereClause OptionalGroupByClause OptionalHavingClause OrderByClause error OptionalLimitClause OffsetClause_EDIT
 ;

DatabaseDefinition_EDIT
 : 'CREATE' DatabaseOrSchema OptionalIfNotExists RegularIdentifier DatabaseDefinitionOptionals_EDIT error
 ;
