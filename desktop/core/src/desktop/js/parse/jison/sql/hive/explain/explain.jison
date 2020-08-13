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

SqlStatement
 : ExplainClause DataDefinition
 | ExplainClause DataManipulation
 | ExplainClause QuerySpecification
 ;

SqlStatement_EDIT
 : ExplainClause_EDIT
 | ExplainClause DataDefinition_EDIT
 | ExplainClause DataManipulation_EDIT
 | ExplainClause QuerySpecification_EDIT
 | ExplainClause_EDIT DataDefinition
 | ExplainClause_EDIT DataManipulation
 | ExplainClause_EDIT QuerySpecification
 ;

ExplainClause
 : 'EXPLAIN' OptionalExplainTypes
 ;

ExplainClause_EDIT
 : 'EXPLAIN' OptionalExplainTypes 'CURSOR'
   {
     if (!$2) {
       parser.suggestDdlAndDmlKeywords([
         { value: 'AST', weight: 2 },
         { value: 'AUTHORIZATION', weight: 2 },
         { value: 'CBO', weight: 2 },
         { value: 'DEPENDENCY', weight: 2 },
         { value: 'EXTENDED', weight: 2 },
         { value: 'FORMATTED CBO', weight: 2 },
         { value: 'LOCKS', weight: 2 },
         { value: 'VECTORIZATION', weight: 2 }
       ]);
     } else if ($2 && $2.suggestKeywords) {
       parser.suggestDdlAndDmlKeywords($2.suggestKeywords);
     } else {
       parser.suggestDdlAndDmlKeywords();
     }
   }
 | 'EXPLAIN' 'FORMATTED' 'CURSOR'
   {
     parser.suggestKeywords(['CBO']);
   }
 ;

OptionalExplainTypes
 :
 | 'AST'
 | 'AUTHORIZATION'
 | 'FORMATTED' 'CBO' OptionalCostOrJoincost
   {
     if (!$3) {
       $$ = { suggestKeywords: ['COST', 'JOINCOST'] };
     }
   }
 | 'CBO' OptionalCostOrJoincost
   {
     if (!$2) {
       $$ = { suggestKeywords: ['COST', 'JOINCOST'] };
     }
   }
 | 'DEPENDENCY'
 | 'EXTENDED'
 | 'LOCKS'
 | 'VECTORIZATION' OptionalOnly OptionalVectorizationTypes
   {
     var keywords = [];
     if (!$3) {
       keywords = keywords.concat([
         { weight: 1, value: 'DETAIL' },
         { weight: 1, value: 'EXPRESSION' },
         { weight: 1, value: 'OPERATOR' },
         { weight: 1, value: 'SUMMARY' }
       ]);
     }
     if (!$2) {
       keywords.push({ weight: 2, value: 'ONLY' });
     }
     if (keywords.length) {
       $$ = { suggestKeywords: keywords };
     }
   }
 ;

OptionalCostOrJoincost
 :
 | 'COST'
 | 'JOINCOST'
 ;

OptionalOnly
 :
 | 'ONLY'
 ;

OptionalVectorizationTypes
 :
 | 'DETAIL'
 | 'EXPRESSION'
 | 'OPERATOR'
 | 'SUMMARY'
 ;
