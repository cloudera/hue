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

OptionalJoins
 :
 | Joins
 | Joins_INVALID
 ;

Joins
 : JoinType OptionalBroadcastOrShuffle TablePrimary OptionalJoinCondition
   {
     if ($4 && $4.valueExpression) {
       $$ = $4.valueExpression;
     } else {
       $$ = {};
     }
     $$.joinType = $1;
     if ($4.noJoinCondition) {
       $$.suggestJoinConditions = { prependOn: true, tablePrimaries: parser.yy.latestTablePrimaries.concat() }
     }
     if ($4.suggestKeywords) {
       $$.suggestKeywords = $4.suggestKeywords;
     }
     if (parser.yy.latestTablePrimaries.length > 0) {
        parser.yy.latestTablePrimaries[parser.yy.latestTablePrimaries.length - 1].join = true;
     }
   }
 | Joins JoinType OptionalBroadcastOrShuffle TablePrimary OptionalJoinCondition
   {
     if ($5 && $5.valueExpression) {
       $$ = $5.valueExpression;
     } else {
       $$ = {};
     }
     $$.joinType = $1;
     if ($5.noJoinCondition) {
       $$.suggestJoinConditions = { prependOn: true, tablePrimaries: parser.yy.latestTablePrimaries.concat() }
     }
     if ($5.suggestKeywords) {
       $$.suggestKeywords = $5.suggestKeywords;
     }
     if (parser.yy.latestTablePrimaries.length > 0) {
       parser.yy.latestTablePrimaries[parser.yy.latestTablePrimaries.length - 1].join = true;
     }
   }
 ;

Joins_INVALID
 : JoinType OptionalBroadcastOrShuffle                                           -> { joinType: $1 }
 | JoinType OptionalBroadcastOrShuffle Joins                                     -> { joinType: $1 }
 ;

Join_EDIT
 : JoinType_EDIT OptionalBroadcastOrShuffle TablePrimary OptionalJoinCondition
   {
     if ($1.suggestKeywords) {
       parser.suggestKeywords($1.suggestKeywords);
     }
   }
 | JoinType_EDIT OptionalBroadcastOrShuffle
   {
     if ($1.suggestKeywords) {
       parser.suggestKeywords($1.suggestKeywords);
     }
   }
 | JoinType OptionalBroadcastOrShuffle TablePrimary_EDIT OptionalJoinCondition
 | JoinType OptionalBroadcastOrShuffle TablePrimary JoinCondition_EDIT
 | JoinType OptionalBroadcastOrShuffle 'CURSOR' OptionalJoinCondition
   {
     if (!$2) {
       parser.suggestKeywords(['[BROADCAST]', '[SHUFFLE]']);
     }
     if (!$2 && parser.yy.latestTablePrimaries.length > 0) {
       var idx = parser.yy.latestTablePrimaries.length - 1;
       var tables = [];
       do {
         var tablePrimary = parser.yy.latestTablePrimaries[idx];
         if (!tablePrimary.subQueryAlias) {
           tables.unshift(tablePrimary.alias ? { identifierChain: tablePrimary.identifierChain, alias: tablePrimary.alias } : { identifierChain: tablePrimary.identifierChain })
         }
         idx--;
       } while (idx >= 0 && tablePrimary.join && !tablePrimary.subQueryAlias)

       if (tables.length > 0) {
         parser.suggestJoins({
           prependJoin: false,
           joinType: $1,
           tables: tables
         })
       }
     }
     parser.suggestTables();
     parser.suggestDatabases({
       appendDot: true
     });
   }
 ;

Joins_EDIT
 : Join_EDIT
 | Join_EDIT Joins
 | Joins Join_EDIT
 | Joins Join_EDIT Joins
 ;

JoinType
 : 'JOIN'                         -> 'JOIN'
 | 'ANTI' 'JOIN'          -> 'ANTI JOIN'
 | 'CROSS' 'JOIN'                 -> 'CROSS JOIN'
 | 'INNER' 'JOIN'                 -> 'INNER JOIN'
 | 'OUTER' 'JOIN'                 -> 'OUTER JOIN'
 | 'SEMI' 'JOIN'                  -> 'SEMI JOIN'
 | 'FULL' 'JOIN'                  -> 'FULL JOIN'
 | 'FULL' 'OUTER' 'JOIN'          -> 'FULL OUTER JOIN'
 | 'LEFT' 'JOIN'                  -> 'LEFT JOIN'
 | 'LEFT' 'ANTI' 'JOIN'   -> 'LEFT ANTI JOIN'
 | 'LEFT' 'INNER' 'JOIN'          -> 'LEFT INNER JOIN'
 | 'LEFT' 'OUTER' 'JOIN'          -> 'LEFT OUTER JOIN'
 | 'LEFT' 'SEMI' 'JOIN'           -> 'LEFT SEMI JOIN'
 | 'RIGHT' 'JOIN'                 -> 'RIGHT JOIN'
 | 'RIGHT' 'ANTI' 'JOIN'  -> 'RIGHT ANTI JOIN'
 | 'RIGHT' 'INNER' 'JOIN'         -> 'RIGHT OUTER JOIN'
 | 'RIGHT' 'OUTER' 'JOIN'         -> 'RIGHT OUTER JOIN'
 | 'RIGHT' 'SEMI' 'JOIN'          -> 'RIGHT SEMI JOIN'
 ;

JoinType_EDIT
 : 'ANTI' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'CROSS' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'INNER' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'OUTER' 'CURSOR'                 -> { suggestKeywords: ['JOIN'] }
 | 'SEMI' 'CURSOR'                  -> { suggestKeywords: ['JOIN'] }
 | 'FULL' 'OUTER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'FULL' 'CURSOR' 'JOIN'           -> { suggestKeywords: ['OUTER'] }
 | 'LEFT' 'ANTI' 'CURSOR'   -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'INNER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'OUTER' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'SEMI' 'CURSOR'           -> { suggestKeywords: ['JOIN'] }
 | 'LEFT' 'CURSOR' 'JOIN'           -> { suggestKeywords: ['ANTI', 'INNER', 'OUTER', 'SEMI'] }
 | 'RIGHT' 'ANTI' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'INNER' 'CURSOR'         -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'OUTER' 'CURSOR'         -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'SEMI' 'CURSOR'          -> { suggestKeywords: ['JOIN'] }
 | 'RIGHT' 'CURSOR' 'JOIN'          -> { suggestKeywords: ['ANTI', 'INNER', 'OUTER', 'SEMI'] }
 ;

OptionalBroadcastOrShuffle
 :
 | 'BROADCAST'
 | 'SHUFFLE'
 ;

OptionalJoinCondition
 :                                       -> { noJoinCondition: true, suggestKeywords: ['ON', 'USING'] }
 | 'ON' ValueExpression                  -> { valueExpression: $2 }
 | 'USING' '(' UsingColList ')'          -> {}
 ;

UsingColList
 : RegularOrBacktickedIdentifier
 | UsingColList ',' RegularOrBacktickedIdentifier
 ;

JoinCondition_EDIT
 : 'ON' ValueExpression_EDIT
 | 'ON' 'CURSOR'
   {
     parser.valueExpressionSuggest();
     parser.suggestJoinConditions({ prependOn: false });
   }
 ;
