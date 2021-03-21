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

AggregateFunction
 : SumFunction
 ;

AggregateFunction_EDIT
 : SumFunction_EDIT
 ;

SumFunction
 : 'SUM' '(' OptionalAllOrDistinct ValueExpression ')'
   {
     parser.addFunctionArgumentLocations($1, $4.expressions);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'SUM' '(' ')'
   {
     $$ = { function: $1, types: ['UDFREF'] }
   }
 ;

SumFunction_EDIT
 : 'SUM' '(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyArgumentTypesToSuggestions($1, 1);
     var keywords = parser.getSelectListKeywords(true);
     if (!$3) {
       keywords.push('DISTINCT');
     }
     if (parser.yy.result.suggestKeywords) {
       keywords = parser.yy.result.suggestKeywords.concat(keywords);
     }
     parser.suggestKeywords(keywords);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'SUM' '(' OptionalAllOrDistinct ValueExpression 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($4);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'SUM' '(' OptionalAllOrDistinct ValueExpression_EDIT RightParenthesisOrError
   {
     if (parser.yy.result.suggestFunctions && !parser.yy.result.suggestFunctions.types) {
       parser.applyArgumentTypesToSuggestions($1, 1);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 ;
