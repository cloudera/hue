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
%options case-insensitive flex
%x squareBracketRange curlyBracketRange doubleQuotedValue singleQuotedValue
%%

\s                                             { /* skip whitespace */ }
'--'.*                                         { /* skip comments */ }
[/][*][^*]*[*]+([^/*][^*]*[*]+)*[/]            { /* skip comments */ }

'\u2020'                                       { parser.yy.cursorFound = yylloc; return 'CURSOR'; }
'\u2021'                                       { parser.yy.cursorFound = yylloc; return 'PARTIAL_CURSOR'; }

'AND'                                          { return 'AND'; }
'&&'                                           { return 'AND'; }
'OR'                                           { return 'OR'; }
'||'                                           { return 'OR'; }
'NOT'                                          { return 'NOT'; }
'!'                                            { return 'NOT'; }
'+'                                            { return '+'; }
'-'                                            { return '-'; }
':'                                            { return ':'; }
'*'                                            { return '*'; }

'('                                            { return '('; }
')'                                            { return ')'; }

[0-9]+(?:[,.][0-9]+)?                          { return 'NUMBER'; }

'['                                            { this.begin('squareBracketRange'); return '['; }
<squareBracketRange>(?:\\[\]]|[^\]])+          {
                                                 if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, ']')) {
                                                   return 'PARTIAL_VALUE';
                                                 }
                                                 return 'VALUE';
                                               }
<singleQuotedValue>\]                          { this.popState(); return ']'; }

'{'                                            { this.begin('curlyBracketRange'); return '{'; }
<curlyBracketRange>(?:\\[\}]|[^\}])+           {
                                                 if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '}')) {
                                                   return 'PARTIAL_VALUE';
                                                 }
                                                 return 'VALUE';
                                               }
<curlyBracketRange>\}                          { this.popState(); return '}'; }

\'                                             { this.begin('singleQuotedValue'); return 'SINGLE_QUOTE'; }
<singleQuotedValue>(?:\\[']|[^'])+             {
                                                 if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '\'')) {
                                                   yytext = yytext.replace(/[\u2020\u2021].*/, '');
                                                   return 'PARTIAL_VALUE';
                                                 }
                                                 return 'VALUE';
                                               }
<singleQuotedValue>\'                          { this.popState(); return 'SINGLE_QUOTE'; }

\"                                             { this.begin('doubleQuotedValue'); return 'DOUBLE_QUOTE'; }
<doubleQuotedValue>(?:\\["]|[^"])+             {
                                                 if (parser.handleQuotedValueWithCursor(this, yytext, yylloc, '"')) {
                                                   yytext = yytext.replace(/[\u2020\u2021].*/, '');
                                                   return 'PARTIAL_VALUE';
                                                 }
                                                 return 'VALUE';
                                               }
<doubleQuotedValue>\"                          { this.popState(); return 'DOUBLE_QUOTE'; }

[^\s\u3000!():"'^+\-!\[\]{}~*?/\u2020\u2021]+  { return 'TERM'; }

<<EOF>>                                        { return 'EOF'; }

/lex

%left 'AND' 'OR' '&&' '||' BooleanOperator
%left 'CURSOR' 'PARTIAL_CURSOR' AnyCursor       // Cursor precedence needed to not conflict with operators i.e. x 'CURSOR' y vs. x 'AND' y

%start SolrQueryAutocomplete

%%

SolrQueryAutocomplete
 : SolrQuery 'EOF'
   {
     return {}
   }
 | SolrQuery_EDIT 'EOF'
   {
     return $1;
   }
 | AnyCursor 'EOF'
   {
     return { suggestFields: {} }
   }
 ;

SolrQuery
 : NonParenthesizedSolrQuery
 | '(' NonParenthesizedSolrQuery ')'
 ;

SolrQuery_EDIT
 : NonParenthesizedSolrQuery_EDIT
 | '(' NonParenthesizedSolrQuery_EDIT RightParenthesisOrError  --> $2
 ;

NonParenthesizedSolrQuery
 : 'NUMBER'
 | 'TERM'
 | KeywordMatch
 ;

NonParenthesizedSolrQuery_EDIT
 : 'TERM' 'PARTIAL_CURSOR'                                     --> { suggestFields: { startsWith: $1 }, suggestValues: { field: $1, prependColon: true }, suggestKeywords: [':'] }
 | KeywordMatch_EDIT
 ;

NonParenthesizedSolrQuery
 : SolrQuery BooleanOperator SolrQuery
 ;

NonParenthesizedSolrQuery_EDIT
 : SolrQuery 'CURSOR'                                          --> { suggestKeywords: ['AND', 'OR', '&&', '||'] }
 | SolrQuery 'CURSOR' SolrQuery                                --> { suggestKeywords: ['AND', 'OR', '&&', '||'] }
 | 'CURSOR' SolrQuery                                          --> { suggestFields: {} }
 ;

NonParenthesizedSolrQuery_EDIT
 : SolrQuery BooleanOperator 'CURSOR'                         --> { suggestFields: {} }
 | 'CURSOR' BooleanOperator SolrQuery                         --> { suggestFields: {} }
 | SolrQuery BooleanOperator SolrQuery_EDIT                    --> $3
 | SolrQuery_EDIT BooleanOperator SolrQuery                    --> $1
 ;

KeywordMatch
 : 'TERM' ':' 'TERM'
 | 'TERM' ':' QuotedValue
 ;

KeywordMatch_EDIT
 : 'TERM' ':' AnyCursor                                        --> { suggestValues: { field: $1 } }
 | 'TERM' ':' 'TERM' 'PARTIAL_CURSOR'                          --> { suggestValues: { field: $1, startsWith: $3 } }
 | 'TERM' ':' QuotedValue_EDIT                                 --> { suggestValues: { field: $1, startsWith: $3 } }
 ;

// ======= Common constructs =======
AnyCursor
: 'CURSOR' | 'PARTIAL_CURSOR';

BooleanOperator
: 'AND' | 'OR' | '&&' | '||';

QuotedValue
: 'SINGLE_QUOTE' 'VALUE' 'SINGLE_QUOTE' | 'DOUBLE_QUOTE' 'VALUE' 'DOUBLE_QUOTE';

QuotedValue_EDIT
: 'SINGLE_QUOTE' 'PARTIAL_VALUE'                               --> $2
| 'DOUBLE_QUOTE' 'PARTIAL_VALUE'                               --> $2
;

RightParenthesisOrError: ')' | error;
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

parser.handleQuotedValueWithCursor = function (lexer, yytext, yylloc, quoteChar) {
  if (yytext.indexOf('\u2020') !== -1 || yytext.indexOf('\u2021') !== -1) {
    parser.yy.partialCursor = yytext.indexOf('\u2021') !== -1;
    var cursorIndex = parser.yy.partialCursor ? yytext.indexOf('\u2021') : yytext.indexOf('\u2020');
    parser.yy.cursorFound = {
      first_line: yylloc.first_line,
      last_line: yylloc.last_line,
      first_column: yylloc.first_column + cursorIndex,
      last_column: yylloc.first_column + cursorIndex + 1
    };
    var remainder = yytext.substring(cursorIndex + 1);
    var remainingQuotes = (lexer.upcomingInput().match(new RegExp(quoteChar, 'g')) || []).length;
    if (remainingQuotes > 0 && remainingQuotes & 1 != 0) {
      parser.yy.missingEndQuote = false;
      lexer.input();
    } else {
      parser.yy.missingEndQuote = true;
      lexer.unput(remainder);
    }
    lexer.popState();
    return true;
  }
  return false;
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

parser.autocompleteSolrQuery = function (beforeCursor, afterCursor, debug) {
  parser.yy.cursorFound = false;
  parser.yy.locations = [];

  beforeCursor = beforeCursor.replace(/\r\n|\n\r/gm, '\n');
  afterCursor = afterCursor.replace(/\r\n|\n\r/gm, '\n');

  parser.yy.partialLengths = parser.identifyPartials(beforeCursor, afterCursor);

  parser.yy.partialCursor = parser.yy.partialLengths.left > 0;


  var cursorChar = parser.yy.partialCursor ? '\u2021' : '\u2020';

  // TODO: Remove left adjust if no need for it
  if (parser.yy.partialCursor) {
    parser.yy.partialLengths.left = 0;
  }

  if (parser.yy.partialLengths.right > 0) {
    afterCursor = afterCursor.substring(parser.yy.partialLengths.right);
  }

  var result;
  try {
    result = parser.parse(beforeCursor + cursorChar + afterCursor);
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
        result = parser.parse(beforeCursor + cursorChar + parenthesisPad);
      } catch (err) {
        return { locations: parser.yy.locations }
      }
    } else {
      if (debug) {
        console.log(beforeCursor + cursorChar + afterCursor);
        console.log(err);
        console.error(err.stack);
      }
      return { locations: parser.yy.locations }
    }
  }
  result.locations = parser.yy.locations;
  return result;
};