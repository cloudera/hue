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

'('                                        { return '('; }
')'                                        { return ')'; }

'\u2020'                                   { parser.yy.cursorFound = yylloc; return 'CURSOR'; }

[0-9]+(?:[,.][0-9]+)?                      { return 'NUMBER'; }

[^\u2020()]+                               { parser.addFieldLocation(yylloc, yytext); return 'IDENTIFIER'; }

<<EOF>>                                    { return 'EOF'; }

/lex

%start SolrQueryAutocomplete

%%

SolrQueryAutocomplete
 : SolrQuery 'EOF'
 | SolrQuery_EDIT 'EOF'
   {
     return $1;
   }
 | 'CURSOR' 'EOF'
   {
     return { suggestFields: true }
   }
 ;

SolrQuery
 : NonParenthesizedSolrQuery
 | '(' NonParenthesizedSolrQuery ')'
 ;

SolrQuery
 : NonParenthesizedSolrQuery_EDIT
 | '(' NonParenthesizedSolrQuery_EDIT RightParenthesisOrError  --> $2
 ;

NonParenthesizedSolrQuery
 : 'NUMBER'
 | 'IDENTIFIER'
 ;

NonParenthesizedSolrQuery_EDIT
 : 'NUMBER' 'CURSOR'                                                --> { suggestOperators: true }
 | 'IDENTIFIER' 'CURSOR'                                            --> { suggestOperators: true }
 | 'CURSOR' 'NUMBER'                                                --> { suggestFields: true }
 | 'CURSOR' 'IDENTIFIER'                                            --> { suggestFields: true }
 ;

RightParenthesisOrError
 : ')'
 | error
 ;

%%

parser.yy.parseError = function () { return false; }

parser.addFieldLocation = function (location, name) {
  parser.yy.locations.push({ type: 'field', name: name, location: adjustLocationForCursor(location) });
}

parser.identifyPartials = function (beforeCursor, afterCursor) {
  var beforeMatch = beforeCursor.match(/[^()-*+/,\s]*$/);
  var afterMatch = afterCursor.match(/^[^()-*+/,\s]*/);
  return { left: beforeMatch ? beforeMatch[0].length : 0, right: afterMatch ? afterMatch[0].length : 0 };
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

parser.parseSolrQuery = function (query, debug) {
  parser.yy.cursorFound = false;
  parser.yy.locations = [];
  query = query.replace(/\r\n|\n\r/gm, '\n');

  var result;
  try {
    result = parser.parse(query);
  } catch (err) {
    if (debug) {
      console.log(beforeCursor + '\u2020' + afterCursor);
      console.log(err);
      console.error(err.stack);
    }
  }
  return result || false;
}

parser.autocompleteSolrQuery = function (beforeCursor, afterCursor, debug) {
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