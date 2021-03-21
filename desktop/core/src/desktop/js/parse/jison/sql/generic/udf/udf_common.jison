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

NonParenthesizedValueExpressionPrimary
 : ColumnOrArbitraryFunctionRef ArbitraryFunctionRightPart
   {
     // We need to handle arbitrary UDFs here instead of inside UserDefinedFunction or there will be a conflict
     // with columnReference for functions like: db.udf(foo)
     var fn = $1.chain[$1.chain.length - 1].name.toLowerCase();
     parser.addFunctionArgumentLocations(fn, $2.expressions, $1.chain);
     if ($1.lastLoc && $1.lastLoc.location) {
       $1.lastLoc.type = 'function';
       $1.lastLoc.function = fn;
       $1.lastLoc.location = {
         first_line: $1.lastLoc.location.first_line,
         last_line: $1.lastLoc.location.last_line,
         first_column: $1.lastLoc.location.first_column,
         last_column: $1.lastLoc.location.last_column - 1
       }
       if ($1.lastLoc !== $1.firstLoc) {
          $1.firstLoc.type = 'database';
       } else {
         delete $1.lastLoc.identifierChain;
       }
     }
     if ($2.expressions && $2.expressions.length) {
       $$ = { function: fn, expression: $2.expressions[$2.expressions.length - 1].expression, types: ['UDFREF'] }
     } else {
       $$ = { function: fn, types: ['UDFREF'] }
     }
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart
  {
    parser.addFunctionLocation(@1, $1);
    if ($2.expressions && $2.expressions.length) {
      $$ = { function: $1, expression: $2.expressions[$2.expressions.length - 1].expression, types: ['UDFREF'] }
    } else {
      $$ = { function: $1, types: ['UDFREF'] }
    }
  }
 | UserDefinedFunction
 ;

NonParenthesizedValueExpressionPrimary_EDIT
 : ColumnOrArbitraryFunctionRef ArbitraryFunctionRightPart_EDIT
   {
     var fn = $1.chain[$1.chain.length - 1].name.toLowerCase();
     parser.addFunctionArgumentLocations(fn, $2.expressions, $1.chain);
     $1.lastLoc.type = 'function';
     $1.lastLoc.function = fn;
     $1.lastLoc.location = {
       first_line: $1.lastLoc.location.first_line,
       last_line: $1.lastLoc.location.last_line,
       first_column: $1.lastLoc.location.first_column,
       last_column: $1.lastLoc.location.last_column - 1
     }
     if ($1.lastLoc !== $1.firstLoc) {
        $1.firstLoc.type = 'database';
     } else {
       delete $1.lastLoc.identifierChain;
     }
     if ($2.activePosition) {
       parser.applyArgumentTypesToSuggestions(fn, $2.activePosition);
     }
     $$ = { function: fn, types: ['UDFREF'] };
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart_EDIT
   {
     parser.addFunctionLocation(@1, $1);
     parser.addFunctionArgumentLocations($1, $2.expressions);
     if ($2.activePosition) {
       parser.applyArgumentTypesToSuggestions($1, $2.activePosition);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | UserDefinedFunction_EDIT
 ;

ArbitraryFunction
 : RegularIdentifier ArbitraryFunctionRightPart
   {
     parser.addFunctionLocation(@1, $1);
     parser.addFunctionArgumentLocations($1, $2.expressions);
     if ($2.expressions && $2.expressions.length) {
       $$ = { function: $1, expression: $2.expressions[$2.expressions.length - 1].expression, types: ['UDFREF'] }
     } else {
       $$ = { function: $1, types: ['UDFREF'] }
     }
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart
   {
     parser.addFunctionLocation(@1, $1);
     parser.addFunctionArgumentLocations($1, $2.expressions);
     if ($2.expressions && $2.expressions.length) {
       $$ = { function: $1, expression: $2.expressions[$2.expressions.length - 1].expression, types: ['UDFREF'] }
     } else {
       $$ = { function: $1, types: ['UDFREF'] }
     }
   }
 ;

ArbitraryFunction_EDIT
 : RegularIdentifier ArbitraryFunctionRightPart_EDIT
   {
     parser.addFunctionLocation(@1, $1);
     parser.addFunctionArgumentLocations($1, $2.expressions);
     if ($2.activePosition) {
       parser.applyArgumentTypesToSuggestions($1, $2.activePosition);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart_EDIT
   {
     parser.addFunctionLocation(@1, $1);
     parser.addFunctionArgumentLocations($1, $2.expressions);
     if ($2.activePosition) {
       parser.applyArgumentTypesToSuggestions($1, $2.activePosition);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 ;

ArbitraryFunctionRightPart
 : '(' ')'
 | '(' UdfArgumentList ')'  -> $2
 ;

ArbitraryFunctionRightPart_EDIT
 : '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = {
       activePosition: 1,
       expressions: [{ expression: { text: '' }, location: @2 }]
     }
   }
 | '(' UdfArgumentList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($2.expressions[$2.expressions.length - 1].expression);
     $$ = $1;
   }
 | '(' UdfArgumentList_EDIT RightParenthesisOrError      -> $2
 ;

UdfArgumentList
 : ValueExpression
   {
     $$ = {
       activePosition: 1,
       expressions: [{ expression: $1, location: @1 }]
     }
   }
 | UdfArgumentList ',' ValueExpression
   {
     $$ = {
       activePosition: $1.activePosition + 1,
       expressions: $1.expressions.concat([{ expression: $3, location: @3 }])
     }
   }
 ;

UdfArgumentList_EDIT
 : ValueExpression_EDIT
   {
     $$ = {
       activePosition: 1,
       expressions: [{ expression: $1, location: @1 }]
     }
   }
 | UdfArgumentList ',' ValueExpression_EDIT
   {
     $$ = {
       activePosition: $1.activePosition + 1,
       expressions: $1.expressions.concat([{ expression: $3, location: @3 }])
     }
   }
 | ValueExpression_EDIT ',' UdfArgumentList
   {
     $$ = {
       activePosition: 1,
       expressions: [{ expression: $1, location: @1 }].concat($3.expressions)
     }
   }
 | UdfArgumentList ',' ValueExpression_EDIT ',' UdfArgumentList
   {
     $$ = {
       activePosition: $1.activePosition + 1,
       expressions: $1.expressions.concat([{ expression: $3, location: @3 }]).concat($5.expressions)
     }
   }
 | UdfArgumentList ',' AnyCursor
   {
     parser.valueExpressionSuggest();
     $$ = {
       activePosition: $1.activePosition + 1,
       expressions: $1.expressions.concat([{ expression: { text: '' }, location: @3 }])
     }
   }
 | UdfArgumentList ',' AnyCursor ',' UdfArgumentList
   {
     parser.valueExpressionSuggest();
     $$ = {
       activePosition: $1.activePosition + 1,
       expressions: $1.expressions.concat([{ expression: { text: '' }, location: @3 }]).concat($5.expressions)
     }
   }
 | UdfArgumentList 'CURSOR' ',' UdfArgumentList
   {
     parser.suggestValueExpressionKeywords($1.expressions[$1.expressions.length - 1].expression);
     $$ = {
       activePosition: $1.activePosition,
       expressions: $1.expressions.concat($4.expressions)
     }
   }
 | AnyCursor ',' UdfArgumentList
   {
     parser.valueExpressionSuggest();
     $$ = {
       cursorAtStart : true,
       activePosition: 1,
       expressions: [{ expression: { text: '' }, location: @1 }].concat($3.expressions)
     };
   }
 | AnyCursor ','
   {
     parser.valueExpressionSuggest();
     $$ = {
       cursorAtStart : true,
       activePosition: 1,
       expressions: [{ expression: { text: '' }, location: @1 }, { expression: { text: '' }, location: @2 }]
     };
   }
 | ',' AnyCursor
   {
     parser.valueExpressionSuggest();
     $$ = {
       activePosition: 2,
       expressions: [{ expression: { text: '' }, location: @1 }, { expression: { text: '' }, location: @2 }]
     };
   }
 | ',' AnyCursor ',' UdfArgumentList
   {
     parser.valueExpressionSuggest();
     $$ = {
       activePosition: 2,
       expressions: [{ expression: { text: '' }, location: @1 }, { expression: { text: '' }, location: @2 }].concat($4.expressions)
     };
   }
 ;

OptionalOverClause
 :
 | OverClause
 ;

OptionalOverClause_EDIT
 : OverClause_EDIT
 ;

OverClause
 : 'OVER' RegularOrBacktickedIdentifier
 | 'OVER' WindowExpression
 ;

OverClause_EDIT
 : 'OVER' WindowExpression_EDIT
 ;
