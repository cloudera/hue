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
