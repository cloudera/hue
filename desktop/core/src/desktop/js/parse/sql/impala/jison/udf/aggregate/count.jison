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
 : CountFunction
 ;

AggregateFunction_EDIT
 : CountFunction_EDIT
 ;

CountFunction
 : 'COUNT' '(' '*' ')'
   {
     parser.addFunctionArgumentLocations($1, [{
       expression: { text: $3 },
       location: @3
     }]);
     $$ = { function: $1, types: ['UDFREF'] }
   }
 | 'COUNT' '(' ')'
   {
     $$ = { function: $1, types: ['UDFREF'] }
   }
 | 'COUNT' '(' OptionalAllOrDistinct UdfArgumentList ')'
   {
     parser.addFunctionArgumentLocations($1, $4.expressions);
     $$ = { function: $1, types: ['UDFREF'] }
   }
 ;

CountFunction_EDIT
 : 'COUNT' '(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     var keywords = parser.getSelectListKeywords();
     if (!$3) {
       keywords.push('DISTINCT');
       keywords.push('ALL');
       if (parser.yy.result.suggestKeywords) {
         keywords = parser.yy.result.suggestKeywords.concat(keywords);
       }
     }
     parser.suggestKeywords(keywords);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'COUNT' '(' OptionalAllOrDistinct UdfArgumentList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($4.expressions[$4.expressions.length - 1].expression);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'COUNT' '(' OptionalAllOrDistinct UdfArgumentList_EDIT RightParenthesisOrError
   {
     if ($4.cursorAtStart) {
       var keywords = parser.getSelectListKeywords();
       if (!$3) {
         keywords.push('DISTINCT');
         keywords.push('ALL');
       }
       parser.suggestKeywords(keywords);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 ;
