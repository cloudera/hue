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

ValueExpression
 : 'NOT' ValueExpression
   {
     // verifyType($2, 'BOOLEAN');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | '!' ValueExpression
   {
     // verifyType($2, 'BOOLEAN');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | '~' ValueExpression                                                              -> $2
 | '-' ValueExpression %prec NEGATION
   {
     // verifyType($2, 'NUMBER');
     $$ = $2;
     $2.types = ['NUMBER'];
   }
 | ValueExpression 'IS' OptionalNot 'NULL'              -> { types: [ 'BOOLEAN' ] }
 ;

ValueExpression_EDIT
 : 'NOT' ValueExpression_EDIT                           -> { types: [ 'BOOLEAN' ] }
 | 'NOT' 'CURSOR'
   {
     suggestFunctions();
     suggestColumns();
     suggestKeywords(['EXISTS']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | '!' ValueExpression_EDIT                             -> { types: [ 'BOOLEAN' ] }
 | '!' AnyCursor
   {
     suggestFunctions({ types: [ 'BOOLEAN' ] });
     suggestColumns({ types: [ 'BOOLEAN' ] });
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | '~' ValueExpression_EDIT                             -> { types: [ 'T' ] }
 | '~' 'PARTIAL_CURSOR'
   {
     suggestFunctions();
     suggestColumns();
     $$ = { types: [ 'T' ] };
   }
 | '-' ValueExpression_EDIT %prec NEGATION
   {
     applyTypeToSuggestions('NUMBER')
     $$ = { types: [ 'NUMBER' ] };
   }
 | '-' 'PARTIAL_CURSOR' %prec NEGATION
   {
     suggestFunctions({ types: [ 'NUMBER' ] });
     suggestColumns({ types: [ 'NUMBER' ] });
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'IS' 'NOT' 'CURSOR'
    {
      suggestKeywords(['NULL']);
      $$ = { types: [ 'BOOLEAN' ] };
    }
 | ValueExpression 'IS' 'CURSOR'
   {
     suggestKeywords(['NOT NULL', 'NULL']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'IS' 'CURSOR' 'NULL'
   {
     suggestKeywords(['NOT']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 ;

// ------------------  EXISTS and parenthesized ------------------
ValueExpression
 : 'EXISTS' TableSubQuery
   {
     $$ = { types: [ 'BOOLEAN' ] };
     // clear correlated flag after completed sub-query (set by lexer)
     parser.yy.correlatedSubQuery = false;
   }
 | '(' ValueExpression ')'                                -> $2
 ;

ValueExpression_EDIT
 : 'EXISTS' TableSubQuery_EDIT                               -> { types: [ 'BOOLEAN' ] }
 | '(' ValueExpression_EDIT RightParenthesisOrError          -> $2
 | '(' AnyCursor RightParenthesisOrError
   {
     valueExpressionSuggest();
     $$ = { types: ['T'] };
   }
 ;

// ------------------  COMPARISON ------------------

ValueExpression
 : ValueExpression '=' ValueExpression                    -> { types: [ 'BOOLEAN' ] }
 | ValueExpression '<' ValueExpression  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression '>' ValueExpression  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'COMPARISON_OPERATOR' ValueExpression  -> { types: [ 'BOOLEAN' ] }
 ;

ValueExpression_EDIT
 : 'CURSOR' '=' ValueExpression
   {
     valueExpressionSuggest($3);
     applyTypeToSuggestions($3.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' '<' ValueExpression
   {
     valueExpressionSuggest($3);
     applyTypeToSuggestions($3.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' '>' ValueExpression
   {
     valueExpressionSuggest($3);
     applyTypeToSuggestions($3.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' 'COMPARISON_OPERATOR' ValueExpression
   {
     valueExpressionSuggest($3);
     applyTypeToSuggestions($3.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression_EDIT '=' ValueExpression
   {
     applyTypeToSuggestions($3.types);
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression_EDIT '<' ValueExpression
   {
     applyTypeToSuggestions($3.types);
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression_EDIT '>' ValueExpression
   {
     applyTypeToSuggestions($3.types);
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression_EDIT 'COMPARISON_OPERATOR' ValueExpression
   {
     applyTypeToSuggestions($3.types);
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression '=' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression '<' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression '>' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'COMPARISON_OPERATOR' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression '=' ValueExpression_EDIT
   {
     applyTypeToSuggestions($1.types);
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression '<' ValueExpression_EDIT
   {
     applyTypeToSuggestions($1.types);
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression '>' ValueExpression_EDIT
   {
     applyTypeToSuggestions($1.types);
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression 'COMPARISON_OPERATOR' ValueExpression_EDIT
   {
     applyTypeToSuggestions($1.types);
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 ;


// ------------------  IN ------------------

ValueExpression
 : ValueExpression 'NOT' 'IN' '(' TableSubQueryInner ')'  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'NOT' 'IN' '(' InValueList ')'         -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'IN' '(' TableSubQueryInner ')'        -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'IN' '(' InValueList ')'               -> { types: [ 'BOOLEAN' ] }
 ;

ValueExpression_EDIT
 : ValueExpression 'NOT' 'IN' ValueExpressionInSecondPart_EDIT
   {
     if ($4.inValueEdit) {
       valueExpressionSuggest($1);
       applyTypeToSuggestions($1.types);
     }
     if ($4.cursorAtStart) {
       suggestKeywords(['SELECT']);
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'IN' ValueExpressionInSecondPart_EDIT
   {
     if ($3.inValueEdit) {
       valueExpressionSuggest($1);
       applyTypeToSuggestions($1.types);
     }
     if ($3.cursorAtStart) {
       suggestKeywords(['SELECT']);
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression_EDIT 'NOT' 'IN' '(' InValueList RightParenthesisOrError         -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'NOT' 'IN' '(' TableSubQueryInner RightParenthesisOrError  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'IN' '(' InValueList RightParenthesisOrError               -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'IN' '(' TableSubQueryInner RightParenthesisOrError        -> { types: [ 'BOOLEAN' ] }
 ;

ValueExpressionInSecondPart_EDIT
 : '(' TableSubQueryInner_EDIT RightParenthesisOrError
 | '(' InValueList_EDIT RightParenthesisOrError         -> { inValueEdit: true }
 | '(' AnyCursor RightParenthesisOrError                -> { inValueEdit: true, cursorAtStart: true }
 ;

// ------------------  BETWEEN ------------------

ValueExpression
 : ValueExpression 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression  -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression        -> { types: [ 'BOOLEAN' ] }
 ;

ValueExpression_EDIT
 : ValueExpression_EDIT 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression
   {
     if ($4.types[0] === $6.types[0]) {
       applyTypeToSuggestions($4.types);
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression_EDIT 'BETWEEN_AND' ValueExpression
   {
     if ($1.types[0] === $6.types[0]) {
       applyTypeToSuggestions($1.types);
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression_EDIT
   {
     if ($1.types[0] === $4.types[0]) {
       applyTypeToSuggestions($1.types);
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression 'BETWEEN_AND' 'CURSOR'
   {
     valueExpressionSuggest($1);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'BETWEEN' ValueExpression 'CURSOR'
   {
     suggestValueExpressionKeywords($4, ['AND']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'NOT' 'BETWEEN' 'CURSOR'
   {
     valueExpressionSuggest($1);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression_EDIT 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression
   {
     if ($1.types[0] === $3.types[0]) {
       applyTypeToSuggestions($1.types)
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'BETWEEN' ValueExpression_EDIT 'BETWEEN_AND' ValueExpression
   {
     if ($1.types[0] === $3.types[0]) {
       applyTypeToSuggestions($1.types)
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'BETWEEN' ValueExpression 'BETWEEN_AND' ValueExpression_EDIT
   {
     if ($1.types[0] === $3.types[0]) {
       applyTypeToSuggestions($1.types)
     }
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'BETWEEN' ValueExpression 'BETWEEN_AND' 'CURSOR'
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'BETWEEN' ValueExpression 'CURSOR'
   {
     suggestValueExpressionKeywords($3, ['AND']);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'BETWEEN' 'CURSOR'
   {
     valueExpressionSuggest($1);
     applyTypeToSuggestions($1.types);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 ;

// ------------------  BOOLEAN ------------------

ValueExpression
 : ValueExpression 'OR' ValueExpression
   {
     // verifyType($1, 'BOOLEAN');
     // verifyType($3, 'BOOLEAN');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'AND' ValueExpression
   {
     // verifyType($1, 'BOOLEAN');
     // verifyType($3, 'BOOLEAN');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 ;

ValueExpression_EDIT
 : 'CURSOR' 'OR' ValueExpression
   {
     valueExpressionSuggest();
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression_EDIT 'OR' ValueExpression
   {
     addColRefIfExists();
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression 'OR' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest();
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'OR' ValueExpression_EDIT
   {
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | 'CURSOR' 'AND' ValueExpression
   {
     valueExpressionSuggest();
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression_EDIT 'AND' ValueExpression
   {
     addColRefIfExists($3);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 | ValueExpression 'AND' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest();
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'AND' ValueExpression_EDIT
   {
     addColRefIfExists($1);
     $$ = { types: [ 'BOOLEAN' ] }
   }
 ;

// ------------------  ARITHMETIC ------------------

ValueExpression
 : ValueExpression '-' ValueExpression
   {
     // verifyType($1, 'NUMBER');
     // verifyType($3, 'NUMBER');
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression '*' ValueExpression
   {
     // verifyType($1, 'NUMBER');
     // verifyType($3, 'NUMBER');
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'ARITHMETIC_OPERATOR' ValueExpression
   {
     // verifyType($1, 'NUMBER');
     // verifyType($3, 'NUMBER');
     $$ = { types: [ 'NUMBER' ] };
   }
 ;

ValueExpression_EDIT
 : 'CURSOR' '*' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'NUMBER' ]);
     $$ = { types: [ 'NUMBER' ] };
   }
 | 'CURSOR' 'ARITHMETIC_OPERATOR' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'NUMBER' ]);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression_EDIT '-' ValueExpression
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($3);
     $$ = { types: [ 'NUMBER' ] }
   }
 | ValueExpression_EDIT '*' ValueExpression
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($3);
     $$ = { types: [ 'NUMBER' ] }
   }
 | ValueExpression_EDIT 'ARITHMETIC_OPERATOR' ValueExpression
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($3);
     $$ = { types: [ 'NUMBER' ] }
   }
 | ValueExpression '-' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['NUMBER']);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression '*' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['NUMBER']);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'ARITHMETIC_OPERATOR' PartialBacktickedOrAnyCursor
   {
     valueExpressionSuggest();
     applyTypeToSuggestions(['NUMBER']);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression '-' ValueExpression_EDIT
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($1);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression '*' ValueExpression_EDIT
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($1);
     $$ = { types: [ 'NUMBER' ] };
   }
 | ValueExpression 'ARITHMETIC_OPERATOR' ValueExpression_EDIT
   {
     applyTypeToSuggestions(['NUMBER']);
     addColRefIfExists($1);
     $$ = { types: [ 'NUMBER' ] };
   }
 ;

// ------------------  LIKE, RLIKE and REGEXP ------------------

ValueExpression
 : ValueExpression 'NOT' 'LIKE' ValueExpression
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'LIKE' ValueExpression
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'RLIKE' ValueExpression
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'REGEXP' ValueExpression
   {
     // verifyType($1, 'STRING');
     $$ = { types: [ 'BOOLEAN' ] };
   }
 ;

ValueExpression_EDIT
 : ValueExpression_EDIT 'NOT' 'LIKE' ValueExpression         -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'LIKE' ValueExpression               -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'RLIKE' ValueExpression              -> { types: [ 'BOOLEAN' ] }
 | ValueExpression_EDIT 'REGEXP' ValueExpression             -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'NOT' 'LIKE' ValueExpression_EDIT         -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'LIKE' ValueExpression_EDIT               -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'RLIKE' ValueExpression_EDIT              -> { types: [ 'BOOLEAN' ] }
 | ValueExpression 'REGEXP' ValueExpression_EDIT             -> { types: [ 'BOOLEAN' ] }
 | 'CURSOR' 'NOT' 'LIKE' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'STRING' ]);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' 'LIKE' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'STRING' ]);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' 'RLIKE' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'STRING' ]);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | 'CURSOR' 'REGEXP' ValueExpression
   {
     valueExpressionSuggest();
     applyTypeToSuggestions([ 'STRING' ]);
     $$ = { types: [ 'BOOLEAN' ] };
   }
 | ValueExpression 'LIKE' PartialBacktickedOrCursor
   {
     suggestFunctions({ types: [ 'STRING' ] });
     suggestColumns({ types: [ 'STRING' ] });
     $$ = { types: ['BOOLEAN'] }
   }
 | ValueExpression 'RLIKE' PartialBacktickedOrCursor
   {
     suggestFunctions({ types: [ 'STRING' ] });
     suggestColumns({ types: [ 'STRING' ] });
     $$ = { types: ['BOOLEAN'] }
   }
 | ValueExpression 'REGEXP' PartialBacktickedOrCursor
   {
     suggestFunctions({ types: [ 'STRING' ] });
     suggestColumns({ types: [ 'STRING' ] });
     $$ = { types: ['BOOLEAN'] }
   }
 ;

// ------------------  CASE, WHEN, THEN ------------------

ValueExpression
 : 'CASE' CaseRightPart                  -> $2
 | 'CASE' ValueExpression CaseRightPart  -> $3
 ;

ValueExpression_EDIT
 : 'CASE' CaseRightPart_EDIT                         -> $2
 | 'CASE' 'CURSOR' EndOrError
   {
     valueExpressionSuggest();
     suggestKeywords(['WHEN']);
     $$ = { types: [ 'T' ] };
   }
 | 'CASE' ValueExpression CaseRightPart_EDIT         -> $3
 | 'CASE' ValueExpression 'CURSOR' EndOrError
   {
     suggestValueExpressionKeywords($2, ['WHEN']);
     $$ = { types: [ 'T' ] };
   }
 | 'CASE' ValueExpression_EDIT CaseRightPart         -> $3
 | 'CASE' ValueExpression_EDIT EndOrError            -> { types: [ 'T' ] }
 | 'CASE' 'CURSOR' CaseRightPart                     -> { types: [ 'T' ] }
 ;

CaseRightPart
 : CaseWhenThenList 'END'                         -> findCaseType($1)
 | CaseWhenThenList 'ELSE' ValueExpression 'END'
   {
     $1.caseTypes.push($3);
     $$ = findCaseType($1);
   }
 ;

CaseRightPart_EDIT
 : CaseWhenThenList_EDIT EndOrError                            -> findCaseType($1)
 | CaseWhenThenList 'ELSE' ValueExpression 'CURSOR'
   {
     suggestValueExpressionKeywords($3, ['END']);
     $1.caseTypes.push($3);
     $$ = findCaseType($1);
   }
 | CaseWhenThenList_EDIT 'ELSE' ValueExpression EndOrError
   {
     $1.caseTypes.push($3);
     $$ = findCaseType($1);
   }
 | CaseWhenThenList_EDIT 'ELSE' EndOrError                      -> findCaseType($1)
 | CaseWhenThenList 'CURSOR' ValueExpression EndOrError
   {
     if ($4.toLowerCase() !== 'end') {
       suggestValueExpressionKeywords($1, ['END', 'ELSE', 'WHEN']);
     } else {
       suggestValueExpressionKeywords($1, ['ELSE', 'WHEN']);
     }
     $$ = findCaseType($1);
   }
 | CaseWhenThenList 'CURSOR' EndOrError
   {
     if ($3.toLowerCase() !== 'end') {
       suggestValueExpressionKeywords($1, ['END', 'ELSE', 'WHEN']);
     } else {
       suggestValueExpressionKeywords($1, ['ELSE', 'WHEN']);
     }
     $$ = findCaseType($1);
   }
 | CaseWhenThenList 'ELSE' ValueExpression_EDIT EndOrError
   {
     $1.caseTypes.push($3);
     $$ = findCaseType($1);
   }
 | CaseWhenThenList 'ELSE' 'CURSOR' EndOrError
   {
     valueExpressionSuggest();
     $$ = findCaseType($1);
   }
 | 'ELSE' 'CURSOR' EndOrError
   {
     valueExpressionSuggest();
     $$ = { types: [ 'T' ] };
   }
 | 'CURSOR' 'ELSE' ValueExpression EndOrError
   {
     valueExpressionSuggest();
     suggestKeywords(['WHEN']);
     $$ = $3;
   }
 | 'CURSOR' 'ELSE' EndOrError
   {
     valueExpressionSuggest();
     suggestKeywords(['WHEN']);
     $$ = { types: [ 'T' ] };
   }
 ;

EndOrError
 : 'END'
 | error
 ;

CaseWhenThenList
 : CaseWhenThenListPartTwo                   -> { caseTypes: [ $1 ], lastType: $1 }
 | CaseWhenThenList CaseWhenThenListPartTwo
   {
     $1.caseTypes.push($2);
     $$ = { caseTypes: $1.caseTypes, lastType: $2 };
   }
 ;

CaseWhenThenList_EDIT
 : CaseWhenThenListPartTwo_EDIT
 | CaseWhenThenList CaseWhenThenListPartTwo_EDIT
 | CaseWhenThenList CaseWhenThenListPartTwo_EDIT CaseWhenThenList
 | CaseWhenThenList 'CURSOR' CaseWhenThenList
   {
     suggestValueExpressionKeywords($1, ['WHEN']);
   }
 | CaseWhenThenListPartTwo_EDIT CaseWhenThenList                   -> $2
 ;

CaseWhenThenListPartTwo
 : 'WHEN' ValueExpression 'THEN' ValueExpression  -> $4
 ;

CaseWhenThenListPartTwo_EDIT
 : 'WHEN' ValueExpression_EDIT                         -> { caseTypes: [{ types: ['T'] }] }
 | 'WHEN' ValueExpression_EDIT 'THEN'                  -> { caseTypes: [{ types: ['T'] }] }
 | 'WHEN' ValueExpression_EDIT 'THEN' ValueExpression  -> { caseTypes: [$4] }
 | 'WHEN' ValueExpression 'THEN' ValueExpression_EDIT  -> { caseTypes: [$4] }
 | 'WHEN' 'THEN' ValueExpression_EDIT                  -> { caseTypes: [$3] }
 | 'CURSOR' ValueExpression 'THEN'
   {
     suggestKeywords(['WHEN']);
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'CURSOR' ValueExpression 'THEN' ValueExpression
   {
     suggestKeywords(['WHEN']);
     $$ = { caseTypes: [$4] };
   }
 | 'CURSOR' 'THEN'
   {
     valueExpressionSuggest();
     suggestKeywords(['WHEN']);
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'CURSOR' 'THEN' ValueExpression
    {
      valueExpressionSuggest();
      suggestKeywords(['WHEN']);
      $$ = { caseTypes: [{ types: ['T'] }] };
    }
 | 'WHEN' 'CURSOR'
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' 'CURSOR' ValueExpression
   {
     valueExpressionSuggest();
     suggestKeywords(['THEN']);
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' 'CURSOR' 'THEN'
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' 'CURSOR' 'THEN' ValueExpression
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [$4] };
   }
 | 'WHEN' ValueExpression 'CURSOR'
   {
     suggestValueExpressionKeywords($2, ['THEN']);
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' ValueExpression 'CURSOR' ValueExpression
   {
     suggestValueExpressionKeywords($2, ['THEN']);
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' ValueExpression 'THEN' 'CURSOR'
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' ValueExpression 'THEN' 'CURSOR' ValueExpression
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' 'THEN' 'CURSOR' ValueExpression
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 | 'WHEN' 'THEN' 'CURSOR'
   {
     valueExpressionSuggest();
     $$ = { caseTypes: [{ types: ['T'] }] };
   }
 ;