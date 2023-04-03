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

UserDefinedFunction
 : AnalyticFunction OverClause
 ;

UserDefinedFunction_EDIT
 : AnalyticFunction_EDIT
 | AnalyticFunction_EDIT OverClause
 | AnalyticFunction 'CURSOR'
   {
     parser.suggestKeywords(['OVER']);
   }
 | AnalyticFunction OverClause_EDIT
 ;

AnalyticFunction
 : 'ANALYTIC' '(' ')'
  {
    $$ = { function: $1, types: ['UDFREF'] }
  }
 | 'ANALYTIC' '(' UdfArgumentList ')'
   {
     parser.addFunctionArgumentLocations($1, $3.expressions);
     $$ = {
       function: $1,
       expression: $3.expressions[$3.expressions.length - 1].expression,
       types: ['UDFREF']
     }
   }
 ;

AnalyticFunction_EDIT
 : 'ANALYTIC' '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyArgumentTypesToSuggestions($1, 1);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'ANALYTIC' '(' UdfArgumentList 'CURSOR' RightParenthesisOrError
   {
     parser.addFunctionArgumentLocations($1, $3.expressions);
     parser.suggestValueExpressionKeywords($3.expressions[$3.expressions.length - 1].expression);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'ANALYTIC' '(' UdfArgumentList_EDIT RightParenthesisOrError
   {
     parser.addFunctionArgumentLocations($1, $3.expressions);
     parser.applyArgumentTypesToSuggestions($1, $3.activePosition);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 ;
