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
 : ExtractFunction
 ;

UserDefinedFunction_EDIT
 : ExtractFunction_EDIT
 ;

ExtractFunction
 : 'EXTRACT' '(' DateField 'FROM' ValueExpression ')'
   {
     parser.addFunctionArgumentLocations($1, [{
       expression: $5,
       location: {
         first_line: @3.first_line,
         last_line: @5.last_line,
         first_column: @3.first_column,
         last_column: @5.last_column
       }
     }]);
     $$ = { types: ['INT', 'INTEGER'] }
   }
 ;

ExtractFunction_EDIT
 : 'EXTRACT' '(' AnyCursor RightParenthesisOrError
   {
     parser.suggestKeywords(['DAY', 'DAYOFWEEK', 'HOUR', 'MINUTE', 'MONTH', 'QUARTER', 'SECOND', 'WEEK', 'YEAR']);
     $$ = { types: ['INT', 'INTEGER'] }
   }
 | 'EXTRACT' '(' DateField 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(['FROM']);
     $$ = { types: ['INT', 'INTEGER'] }
   }
 | 'EXTRACT' '(' DateField 'FROM' 'CURSOR' RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: ['INT', 'INTEGER'] }
   }
 | 'EXTRACT' '(' DateField 'FROM' ValueExpression_EDIT RightParenthesisOrError  -> { types: ['INT', 'INTEGER'] }
 | 'EXTRACT' '(' AnyCursor 'FROM' ValueExpression RightParenthesisOrError
   {
      parser.suggestKeywords(['DAY', 'DAYOFWEEK', 'HOUR', 'MINUTE', 'MONTH', 'QUARTER', 'SECOND', 'WEEK', 'YEAR']);
      $$ = { types: ['INT', 'INTEGER'] }
   }
 | 'EXTRACT' '(' DateField 'CURSOR' ValueExpression RightParenthesisOrError
   {
     parser.suggestKeywords(['FROM']);
     $$ = { types: ['INT', 'INTEGER'] }
   }
 ;

DateField
 : 'DAY'
 | 'DAYOFWEEK'
 | 'HOUR'
 | 'MINUTE'
 | 'MONTH'
 | 'QUARTER'
 | 'SECOND'
 | 'WEEK'
 | 'YEAR'
 ;
