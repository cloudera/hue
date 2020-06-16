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

const initGlobalSearchParser = function (parser) {
  parser.identifyPartials = function (beforeCursor, afterCursor) {
    const beforeMatch = beforeCursor.match(/[0-9a-zA-Z_]*$/);
    const afterMatch = afterCursor.match(/^[0-9a-zA-Z_]*(?:\((?:[^)]*\))?)?/);
    return {
      left: beforeMatch ? beforeMatch[0].length : 0,
      right: afterMatch ? afterMatch[0].length : 0
    };
  };

  parser.mergeFacets = function (a, b) {
    if (!a.facets) {
      a.facets = {};
    }
    if (!b.facets) {
      return;
    }
    Object.keys(b.facets).forEach(key => {
      if (a.facets[key]) {
        Object.keys(b.facets[key]).forEach(val => {
          a.facets[key][val.toLowerCase()] = true;
        });
      } else {
        a.facets[key] = b.facets[key];
      }
    });
  };

  parser.mergeText = function (a, b) {
    if (!a.text) {
      a.text = [];
    }
    if (!b.text) {
      return;
    }
    a.text = a.text.concat(b.text);
  };

  parser.handleQuotedValueWithCursor = function (lexer, yytext, yylloc, quoteChar) {
    if (yytext.indexOf('\u2020') !== -1 || yytext.indexOf('\u2021') !== -1) {
      const cursorIndex = yytext.indexOf('\u2020');
      parser.yy.cursorFound = {
        first_line: yylloc.first_line,
        last_line: yylloc.last_line,
        first_column: yylloc.first_column + cursorIndex,
        last_column: yylloc.first_column + cursorIndex + 1
      };
      const remainder = yytext.substring(cursorIndex + 1);
      const remainingQuotes = (lexer.upcomingInput().match(new RegExp(quoteChar, 'g')) || [])
        .length;
      if (remainingQuotes > 0 && (remainingQuotes & 1) !== 0) {
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

  parser.parseGlobalSearch = function (beforeCursor, afterCursor, debug) {
    delete parser.yy.cursorFound;

    let result;
    try {
      result = parser.parse(beforeCursor + '\u2020' + afterCursor);
    } catch (err) {
      if (debug) {
        console.warn(err);
        console.warn(err.stack);
        console.warn(parser.yy.error);
      }
      return {
        facets: {},
        text: []
      };
    }
    return result;
  };
};

export default {
  initGlobalSearchParser: initGlobalSearchParser
};
