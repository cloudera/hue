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

%lex
%options case-insensitive
%%

\s                                         { /* skip whitespace */ }
'--'.*                                     { /* skip comments */ }
[/][*][^*]*[*]+([^/*][^*]*[*]+)*[/]        { /* skip comments */ }

'\u2020'                                   { parser.yy.cursorFound = yylloc; return 'CURSOR'; }

[0-9]+(?:[,.][0-9]+)?                      { return 'NUMBER'; }

'-'                                        { return '-'; }
'+'                                        { return '+'; }
'*'                                        { return '*'; }
'/'                                        { return '/'; }

[a-z]+\s*\(                                {
                                             yy.lexer.unput('(');
                                             parser.addFunctionLocation({
                                               first_line: yylloc.first_line,
                                               first_column: yylloc.first_column,
                                               last_line: yylloc.first_line,
                                               last_column: yylloc.first_column + yytext.trim().length
                                             }, yytext.trim());
                                             return 'FUNCTION';
                                           }

','                                        { return ','; }
'('                                        { return '('; }
')'                                        { return ')'; }

<<EOF>>                                    { return 'EOF'; }

[^\s\u2020()]+                             { parser.addFieldLocation(yylloc, yytext); return 'IDENTIFIER'; }

/lex

%left '+' '-'
%left '*' '/'

%start SolrFormulaAutocomplete

%%

SolrFormulaAutocomplete
 : SolrFormula 'EOF'
   {
     return {
       parsedValue: $1
     };
   }
 | SolrFormula_EDIT 'EOF'
   {
     return $1
   }
 | 'CURSOR' 'EOF'
   {
     return { suggestAggregateFunctions: true }
   }
 ;

SolrFormula
 : NonParenthesizedSolrFormula
 | '(' NonParenthesizedSolrFormula ')'  -> $1 + $2 + $3
 ;

SolrFormula_EDIT
 : NonParenthesizedSolrFormula_EDIT
 | '(' NonParenthesizedSolrFormula_EDIT RightParenthesisOrError  --> $2
 ;

NonParenthesizedSolrFormula
 : 'NUMBER'
 | 'IDENTIFIER'
 | 'FUNCTION' '(' ArgumentList ')'    -> $1 + $2 + $3 + $4
 | SolrFormula '+' SolrFormula  -> 'sum(' + $1 + ',' + $3 + ')'
 | SolrFormula '-' SolrFormula  -> 'sub(' + $1 + ',' + $3 + ')'
 | SolrFormula '*' SolrFormula  -> 'mul(' + $1 + ',' + $3 + ')'
 | SolrFormula '/' SolrFormula  -> 'div(' + $1 + ',' + $3 + ')'
 | '-' SolrFormula                 -> 'sub(0,' + $2 + ')'
 ;

NonParenthesizedSolrFormula_EDIT
 : 'NUMBER' 'CURSOR'                                             --> { suggestOperators: true }
 | 'IDENTIFIER' 'CURSOR'                                         --> { suggestOperators: true }
 | 'CURSOR' 'NUMBER'                                             --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | 'CURSOR' 'IDENTIFIER'                                         --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 ;

NonParenthesizedSolrFormula_EDIT
 : 'FUNCTION' '(' 'CURSOR' RightParenthesisOrError               --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | 'FUNCTION' '(' ArgumentList_EDIT RightParenthesisOrError      --> $3
 | 'FUNCTION' '(' ArgumentList ')' 'CURSOR'                      --> { suggestOperators: true }
 ;

NonParenthesizedSolrFormula_EDIT
 : SolrFormula '+' 'CURSOR'                                      --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | 'CURSOR' '+' SolrFormula                                      --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | SolrFormula_EDIT '+' SolrFormula                              --> $1
 | SolrFormula '+' SolrFormula_EDIT                              --> $3
 ;

NonParenthesizedSolrFormula_EDIT
 : SolrFormula '-' 'CURSOR'                                      --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | 'CURSOR' '-' SolrFormula                                      --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | SolrFormula_EDIT '-' SolrFormula                              --> $1
 | SolrFormula '-' SolrFormula_EDIT                              --> $3
 ;

NonParenthesizedSolrFormula_EDIT
 : SolrFormula '*' 'CURSOR'                                      --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | 'CURSOR' '*' SolrFormula                                      --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | SolrFormula_EDIT '*' SolrFormula                              --> $1
 | SolrFormula '*' SolrFormula_EDIT                              --> $3
 ;

NonParenthesizedSolrFormula_EDIT
 : SolrFormula '/' 'CURSOR'                                      --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | 'CURSOR' '/' SolrFormula                                      --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | SolrFormula_EDIT '/' SolrFormula                              --> $1
 | SolrFormula '/' SolrFormula_EDIT                              --> $3
 ;

NonParenthesizedSolrFormula_EDIT
 : '-' 'CURSOR'                                                  --> { suggestAggregateFunctions: true, suggestFunctions: true, suggestFields: true }
 | '-' SolrFormula_EDIT                                          --> $2
 ;

ArgumentList
 : SolrFormula
 | ArgumentList ',' SolrFormula
 ;

ArgumentList_EDIT
 : SolrFormula_EDIT
 | ArgumentList ',' SolrFormula_EDIT                             --> $3
 | SolrFormula_EDIT ',' ArgumentList
 | ArgumentList ',' SolrFormula_EDIT ',' ArgumentList            --> $3
 ;


RightParenthesisOrError
 : ')'
 | error
 ;

%%

parser.yy.parseError = function () { return false; }

parser.identifyPartials = function (beforeCursor, afterCursor) {
  var beforeMatch = beforeCursor.match(/[^()-*+/,\s]*$/);
  var afterMatch = afterCursor.match(/^[^()-*+/,\s]*/);
  return {left: beforeMatch ? beforeMatch[0].length : 0, right: afterMatch ? afterMatch[0].length : 0};
};

var adjustLocationForCursor = function (location) {
  // columns are 0-based and lines not, so add 1 to cols
  var newLocation = {
    first_line: location.first_line,
    last_line: location.last_line,
    first_column: location.first_column + 1,
    last_column: location.last_column + 1
  };
  if (parser.yy.cursorFound) {
    if (parser.yy.cursorFound.first_line === newLocation.first_line && parser.yy.cursorFound.last_column <= newLocation.first_column) {
      var additionalSpace = parser.yy.partialLengths.left + parser.yy.partialLengths.right;
      additionalSpace -= parser.yy.partialCursor ? 1 : 3; // For some reason the normal cursor eats 3 positions.
      newLocation.first_column = newLocation.first_column + additionalSpace;
      newLocation.last_column = newLocation.last_column + additionalSpace;
    }
  }
  return newLocation;
};

parser.addFunctionLocation = function (location, name) {
  parser.yy.locations.push({ type: 'function', name: name, location: adjustLocationForCursor(location) });
}

parser.addFieldLocation = function (location, name) {
  parser.yy.locations.push({ type: 'field', name: name, location: adjustLocationForCursor(location) });
}

parser.parseSolrFormula = function (formula, debug) {
  parser.yy.cursorFound = false;
  parser.yy.locations = [];
  formula = formula.replace(/\r\n|\n\r/gm, '\n');

  var result;
  try {
    result = parser.parse(formula);
  } catch (err) {
    if (debug) {
      console.log(beforeCursor + '\u2020' + afterCursor);
      console.log(err);
      console.error(err.stack);
    }
  }
  return result || false;
}

parser.autocompleteSolrFormula = function (beforeCursor, afterCursor, debug) {
  parser.yy.cursorFound = false;
  parser.yy.locations = [];

  beforeCursor = beforeCursor.replace(/\r\n|\n\r/gm, '\n');
  afterCursor = afterCursor.replace(/\r\n|\n\r/gm, '\n');

  parser.yy.partialLengths = parser.identifyPartials(beforeCursor, afterCursor);

  if (parser.yy.partialLengths.left > 0) {
    beforeCursor = beforeCursor.substring(0, beforeCursor.length - parser.yy.partialLengths.left);
  }

  if (parser.yy.partialLengths.right > 0) {
    afterCursor = afterCursor.substring(parser.yy.partialLengths.right);
  }

  var result;
  try {
    result = parser.parse(beforeCursor + '\u2020' + afterCursor);
  } catch (err) {
    // Workaround for too many missing parentheses (it's the only error we handle in the parser)
    if (err && err.toString().indexOf('Parsing halted while starting to recover from another error') !== -1) {
      var leftCount = (beforeCursor.match(/\(/g) || []).length;
      var rightCount = (beforeCursor.match(/\)/g) || []).length;
      var parenthesisPad = '';
      while (rightCount < leftCount) {
        parenthesisPad += ')';
        rightCount++;
      }
      try {
        result = parser.parse(beforeCursor + '\u2020' + parenthesisPad);
      } catch (err) {
        return {}
      }
    } else {
      if (debug) {
        console.log(beforeCursor + '\u2020' + afterCursor);
        console.log(err);
        console.error(err.stack);
      }
      return {}
    }
  }
  result.locations = parser.yy.locations;
  return result;
};