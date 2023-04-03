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
 : 'EXTRACT' '(' ValueExpression FromOrComma ValueExpression ')'
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
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' ')'
   {
     $$ = { function: $1, types: ['UDFREF'] };
   }
 ;

ExtractFunction_EDIT
 : 'EXTRACT' '(' AnyCursor FromOrComma ValueExpression RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyTypeToSuggestions({ types: $4.isFrom ? ['STRING'] : ['TIMESTAMP'] });
     parser.applyArgumentTypesToSuggestions($1, $4.isFrom ? 2 : 1);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' AnyCursor FromOrComma RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     var isFrom = $4.toLowerCase() === 'from';
     parser.applyTypeToSuggestions({ types: $4.isFrom ? ['STRING'] : ['TIMESTAMP'] });
     parser.applyArgumentTypesToSuggestions($1, $4.isFrom ? 2 : 1);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyTypeToSuggestions({ types: ['STRING', 'TIMESTAMP'] });
     parser.applyArgumentTypesToSuggestions($1, 1);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' ValueExpression_EDIT FromOrComma ValueExpression RightParenthesisOrError
   {
     parser.applyTypeToSuggestions({ types: $4.isFrom === 'from' ? ['STRING'] : ['TIMESTAMP'] });
     parser.applyArgumentTypesToSuggestions($1, $4.isFrom ? 2 : 1);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' ValueExpression_EDIT FromOrComma RightParenthesisOrError
   {
     parser.applyTypeToSuggestions({ types: $4.isFrom ? ['STRING'] : ['TIMESTAMP'] });
     parser.applyArgumentTypesToSuggestions($1, $4.isFrom ? 2 : 1);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' ValueExpression_EDIT RightParenthesisOrError
   {
     parser.applyTypeToSuggestions({ types: ['STRING', 'TIMESTAMP'] });
     parser.applyArgumentTypesToSuggestions($1, 1);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' ValueExpression FromOrComma AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyTypeToSuggestions({ types: $4.isFrom ? ['TIMESTAMP'] : ['STRING'] });
     parser.applyArgumentTypesToSuggestions($1, $4.isFrom ? 1 : 2);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' FromOrComma AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyTypeToSuggestions({ types: $4.isFrom ? ['TIMESTAMP'] : ['STRING'] });
     parser.applyArgumentTypesToSuggestions($1, $4.isFrom ? 1 : 2);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' ValueExpression FromOrComma ValueExpression_EDIT RightParenthesisOrError
   {
     parser.applyTypeToSuggestions({ types: $4.isFrom ? ['TIMESTAMP'] : ['STRING'] });
     parser.applyArgumentTypesToSuggestions($1, $4.isFrom ? 1 : 2);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' FromOrComma ValueExpression_EDIT RightParenthesisOrError
   {
     parser.applyTypeToSuggestions({ types: $4.isFrom ? ['TIMESTAMP'] : ['STRING'] });
     parser.applyArgumentTypesToSuggestions($1, $4.isFrom ? 1 : 2);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' ValueExpression 'CURSOR' ValueExpression RightParenthesisOrError
   {
     if ($3.types[0] === 'STRING') {
       parser.suggestValueExpressionKeywords($3, ['FROM']);
     } else {
       parser.suggestValueExpressionKeywords($3);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'EXTRACT' '(' ValueExpression 'CURSOR' RightParenthesisOrError
   {
     if ($3.types[0] === 'STRING') {
       parser.suggestValueExpressionKeywords($3, ['FROM']);
     } else {
       parser.suggestValueExpressionKeywords($3);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 ;

FromOrComma
 : 'FROM' -> { isFrom: true }
 | ','    -> { isFrom: false }
 ;
