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
     if ($2.expressions && $2.expressions.length) {
       $$ = { function: fn, expression: $2.expressions[$2.expressions.length - 1].expression, types: ['UDFREF'] }
     } else {
       $$ = { function: fn, types: ['UDFREF'] }
     }
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart
  {
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
     if ($2.activePosition) {
       parser.applyArgumentTypesToSuggestions($1, $2.activePosition);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | UserDefinedFunction_EDIT
 ;

UserDefinedFunction
 : AggregateFunction OptionalOverClause
   {
     if (!$2) {
       $1.suggestKeywords = ['OVER'];
     }
   }
 | AnalyticFunction OverClause
 | CastFunction
 ;

UserDefinedFunction_EDIT
 : AggregateFunction_EDIT
 | AggregateFunction OptionalOverClause_EDIT
 | AnalyticFunction_EDIT
 | AnalyticFunction_EDIT OverClause
 | AnalyticFunction 'CURSOR'
   {
     parser.suggestKeywords(['OVER']);
   }
 | AnalyticFunction OverClause_EDIT
 | CastFunction_EDIT
 ;

ArbitraryFunction
 : RegularIdentifier ArbitraryFunctionRightPart
   {
     parser.addFunctionLocation(@1, $1);
     if ($2.expressions && $2.expressions.length) {
       $$ = { function: $1, expression: $2.expressions[$2.expressions.length - 1].expression, types: ['UDFREF'] }
     } else {
       $$ = { function: $1, types: ['UDFREF'] }
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
 ;

ArbitraryFunction_EDIT
 : RegularIdentifier ArbitraryFunctionRightPart_EDIT
   {
     parser.addFunctionLocation(@1, $1);
     if ($2.activePosition) {
       parser.applyArgumentTypesToSuggestions($1, $2.activePosition);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | ArbitraryFunctionName ArbitraryFunctionRightPart_EDIT
   {
     parser.addFunctionLocation(@1, $1);
     if ($2.activePosition) {
       parser.applyArgumentTypesToSuggestions($1, $2.activePosition);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 ;

ArbitraryFunctionName
 : 'ARRAY'
 | 'IF'
 | 'MAP'
 | 'TRUNCATE'
 ;

ArbitraryFunctionRightPart
 : '(' ')'
 | '(' ArgumentList ')'  -> $2
 ;

ArbitraryFunctionRightPart_EDIT
 : '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = {
       activePosition: 1,
       expressions: [{ expression: undefined, location: @2 }]
     }
   }
 | '(' ArgumentList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($2.expressions[$2.expressions.length - 1].expression);
     $$ = $1;
   }
 | '(' ArgumentList_EDIT RightParenthesisOrError      -> $2
 ;

ArgumentList
 : ValueExpression
   {
     $$ = {
       activePosition: 1,
       expressions: [{ expression: $1, location: @1 }]
     }
   }
 | ArgumentList ',' ValueExpression
   {
     $$ = {
       activePosition: $1.activePosition + 1,
       expressions: $1.expressions.concat([{ expression: $3, location: @3 }])
     }
   }
 ;

ArgumentList_EDIT
 : ValueExpression_EDIT
   {
     $$ = {
       activePosition: 1,
       expressions: [{ expression: $1, location: @1 }]
     }
   }
 | ArgumentList ',' ValueExpression_EDIT
   {
     $$ = {
       activePosition: $1.activePosition + 1,
       expressions: $1.expressions.concat([{ expression: $3, location: @3 }])
     }
   }
 | ValueExpression_EDIT ',' ArgumentList
   {
     $$ = {
       activePosition: 1,
       expressions: [{ expression: $1, location: @1 }].concat($3.expressions)
     }
   }
 | ArgumentList ',' ValueExpression_EDIT ',' ArgumentList
   {
     $$ = {
       activePosition: $1.activePosition + 1,
       expressions: $1.expressions.concat([{ expression: $3, location: @3 }]).concat($5.expressions)
     }
   }
 | ArgumentList ',' AnyCursor
   {
     parser.valueExpressionSuggest();
     $$ = {
       activePosition: $1.activePosition + 1,
       expressions: $1.expressions.concat([{ expression: undefined, location: @3 }])
     }
   }
 | ArgumentList ',' AnyCursor ',' ArgumentList
   {
     parser.valueExpressionSuggest();
     $$ = {
       activePosition: $1.activePosition + 1,
       expressions: $1.expressions.concat([{ expression: undefined, location: @3 }]).concat($5.expressions)
     }
   }
 | ArgumentList 'CURSOR' ',' ArgumentList
   {
     parser.suggestValueExpressionKeywords($1.expressions[$1.expressions.length - 1].expression);
     $$ = {
       activePosition: $1.activePosition,
       expressions: $1.expressions.concat($4.expressions)
     }
   }
 | AnyCursor ',' ArgumentList
   {
     parser.valueExpressionSuggest();
     $$ = {
       cursorAtStart : true,
       activePosition: 1,
       expressions: [{ expression: undefined, location: @1 }].concat($3.expressions)
     };
   }
 | AnyCursor ','
   {
     parser.valueExpressionSuggest();
     $$ = {
       cursorAtStart : true,
       activePosition: 1,
       expressions: [{ expression: undefined, location: @1 }, { expression: undefined, location: @2 }]
     };
   }
 | ',' AnyCursor
   {
     parser.valueExpressionSuggest();
     $$ = {
       activePosition: 2,
       expressions: [{ expression: undefined, location: @1 }, { expression: undefined, location: @2 }]
     };
   }
 | ',' AnyCursor ',' ArgumentList
   {
     parser.valueExpressionSuggest();
     $$ = {
       activePosition: 2,
       expressions: [{ expression: undefined, location: @1 }, { expression: undefined, location: @2 }].concat($4.expressions)
     };
   }
 ;

AggregateFunction
 : CountFunction
 | SumFunction
 | OtherAggregateFunction
 ;

AggregateFunction_EDIT
 : CountFunction_EDIT
 | SumFunction_EDIT
 | OtherAggregateFunction_EDIT
 ;

AnalyticFunction
 : 'ANALYTIC' '(' ')'               -> { function: $1, types: ['UDFREF'] }
 | 'ANALYTIC' '(' ArgumentList ')'  -> { function: $1, expression: $3.expressions[$3.expressions.length - 1].expression, types: ['UDFREF'] }
 ;

AnalyticFunction_EDIT
 : 'ANALYTIC' '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     parser.applyArgumentTypesToSuggestions($1, 1);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'ANALYTIC' '(' ArgumentList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($3.expressions[$3.expressions.length - 1].expression);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'ANALYTIC' '(' ArgumentList_EDIT RightParenthesisOrError
   {
     parser.applyArgumentTypesToSuggestions($1, $3.activePosition);
     $$ = { function: $1, types: ['UDFREF'] };
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

CastFunction
 : 'CAST' '(' ValueExpression 'AS' PrimitiveType ')'  -> { types: [ $5.toUpperCase() ] }
 | 'CAST' '(' ')'                                      -> { types: [ 'T' ] }
 ;

CastFunction_EDIT
 : 'CAST' '(' AnyCursor 'AS' PrimitiveType RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: [ $5.toUpperCase() ] };
   }
 | 'CAST' '(' AnyCursor 'AS' RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' ValueExpression_EDIT 'AS' PrimitiveType RightParenthesisOrError  -> { types: [ $5.toUpperCase() ] }
 | 'CAST' '(' ValueExpression_EDIT 'AS' RightParenthesisOrError                -> { types: [ 'T' ] }
 | 'CAST' '(' ValueExpression_EDIT RightParenthesisOrError                      -> { types: [ 'T' ] }
 | 'CAST' '(' ValueExpression 'CURSOR' PrimitiveType RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($3, [{ value: 'AS', weight: 2 }]);
     $$ =  { types: [ $5.toUpperCase() ] };
   }
 | 'CAST' '(' ValueExpression 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($3, [{ value: 'AS', weight: 2 }]);
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' ValueExpression 'AS' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(parser.getTypeKeywords());
     $$ = { types: [ 'T' ] };
   }
 | 'CAST' '(' 'AS' 'CURSOR' RightParenthesisOrError
   {
     parser.suggestKeywords(parser.getTypeKeywords());
     $$ = { types: [ 'T' ] };
   }
 ;

CountFunction
 : 'COUNT' '(' '*' ')'                                 -> { function: $1, types: ['UDFREF'] }
 | 'COUNT' '(' ')'                                     -> { function: $1, types: ['UDFREF'] }
 | 'COUNT' '(' OptionalAllOrDistinct ArgumentList ')'  -> { function: $1, types: ['UDFREF'] }
 ;

CountFunction_EDIT
 : 'COUNT' '(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     var keywords = parser.getSelectListKeywords();
     if (!$3) {
       keywords.push('DISTINCT');
       if (parser.yy.result.suggestKeywords) {
         keywords = parser.yy.result.suggestKeywords.concat(keywords);
       }
     }
     parser.suggestKeywords(keywords);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'COUNT' '(' OptionalAllOrDistinct ArgumentList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($4.expressions[$4.expressions.length - 1].expression);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | 'COUNT' '(' OptionalAllOrDistinct ArgumentList_EDIT RightParenthesisOrError
   {
     if ($4.cursorAtStart) {
       var keywords = parser.getSelectListKeywords();
       if (!$3) {
         keywords.push('DISTINCT');
       }
       parser.suggestKeywords(keywords);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 ;

OtherAggregateFunction
 : OtherAggregateFunction_Type '(' OptionalAllOrDistinct ')'               -> { function: $1, types: ['UDFREF'] }
 | OtherAggregateFunction_Type '(' OptionalAllOrDistinct ArgumentList ')'  -> { function: $1, types: ['UDFREF'] }
 ;

OtherAggregateFunction_EDIT
 : OtherAggregateFunction_Type '(' OptionalAllOrDistinct AnyCursor RightParenthesisOrError
   {
     parser.valueExpressionSuggest();
     var keywords = parser.getSelectListKeywords(true);
     if (!$3) {
       if ($1.toLowerCase() === 'group_concat') {
         keywords.push('ALL');
       } else {
         keywords.push('DISTINCT');
       }
     }
     if (parser.yy.result.suggestKeywords) {
       keywords = parser.yy.result.suggestKeywords.concat(keywords);
     }
     parser.suggestKeywords(keywords);
     parser.applyArgumentTypesToSuggestions($1, 1);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | OtherAggregateFunction_Type '(' OptionalAllOrDistinct ArgumentList 'CURSOR' RightParenthesisOrError
   {
     parser.suggestValueExpressionKeywords($4.expressions[$4.expressions.length - 1].expression);
     $$ = { function: $1, types: ['UDFREF'] };
   }
 | OtherAggregateFunction_Type '(' OptionalAllOrDistinct ArgumentList_EDIT RightParenthesisOrError
   {
     if ($4.cursorAtStart) {
       var keywords = parser.getSelectListKeywords(true);
       if (!$3) {
         if ($1.toLowerCase() === 'group_concat') {
           keywords.push('ALL');
         } else {
           keywords.push('DISTINCT');
         }
       }
       if (parser.yy.result.suggestKeywords) {
         keywords = parser.yy.result.suggestKeywords.concat(keywords);
       }
       parser.suggestKeywords(keywords);
     }
     if (parser.yy.result.suggestFunctions && !parser.yy.result.suggestFunctions.types) {
       parser.applyArgumentTypesToSuggestions($1, $4.activePosition);
     }
     $$ = { function: $1, types: ['UDFREF'] };
   }
 ;

OtherAggregateFunction_Type
 : 'AVG'
 | 'MAX'
 | 'MIN'
 | 'STDDEV_POP'
 | 'STDDEV_SAMP'
 | 'VAR_POP'
 | 'VAR_SAMP'
 | 'VARIANCE'
 ;

SumFunction
 : 'SUM' '(' OptionalAllOrDistinct ValueExpression ')'  -> { function: $1, types: ['UDFREF'] }
 | 'SUM' '(' ')'                                        -> { function: $1, types: ['UDFREF'] }
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
