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
define([
  'desktop/js/autocomplete/sql'
], function(sql) {
  return {
    autocompleteMatcher : {
      toEqualAutocompleteValues : function() {
        return {
          compare: function(actualItems, expectedValues) {
            if (actualItems.length !== expectedValues.length) {
              return { pass: false };
            }

            for (var i = 0; i < expectedValues.length; i++) {
              var stringValue = typeof actualItems[i] !== "string" ? '' + actualItems[i].value : actualItems[i].value;
              if (stringValue !== expectedValues[i]) {
                return { pass: false };
              }
            }
            return { pass: true };
          }
        }
      }
    },
    testDefinitionMatcher: {
      toEqualDefinition : function() {
        return {
          compare: function(actualResponse, testDefinition) {
            if (testDefinition.ignoreErrors) {
              delete actualResponse.error;
            }
            if (typeof testDefinition.containsKeywords !== 'undefined') {
              var keywords = actualResponse.suggestKeywords;
              var contains = true;
              testDefinition.containsKeywords.forEach(function (keyword) {
                if (typeof keywords === 'undefined' || keywords.indexOf(keyword) === -1) {
                  contains = false;
                  return false;
                }
              });
              if (!contains) {
                return {
                  pass: false,
                  message: '\n        Statement: ' + testDefinition.beforeCursor + '|' + testDefinition.afterCursor + '\n' +
                             '          Dialect: ' + testDefinition.dialect + '\n' +
                             'Expected keywords: ' + JSON.stringify(testDefinition.containsKeywords) + '\n' +
                             '  Parser keywords: ' + JSON.stringify(keywords) +   '\n'
                }
              }
              delete actualResponse.suggestKeywords;
            }
            if (typeof testDefinition.containsFunctions !== 'undefined') {
              var funcs = actualResponse.suggestFunctions;
              var contains = true;
              testDefinition.containsFunctions.forEach(function (func) {
                if (typeof funcs !== 'undefined') {
                  var foundFuncs = funcs.filter(function (otherFunc) {
                    return otherFunc.name === func;
                  });
                  if (foundFuncs.length === 0) {
                    contains = false;
                    return false;
                  }
                } else {
                  contains = false;
                  return false;
                }
              });
              if (!contains) {
                return {
                  pass: false,
                  message: '\n         Statement: ' + testDefinition.beforeCursor + '|' + testDefinition.afterCursor + '\n' +
                  '           Dialect: ' + testDefinition.dialect + '\n' +
                  'Expected functions: ' + JSON.stringify(testDefinition.containsFunctions) + '\n' +
                  '  Parser functions: ' + JSON.stringify(funcs) +   '\n'
                }
              }
              delete actualResponse.suggestFunctions;
            }
            return {
              pass: jasmine.matchersUtil.equals(actualResponse, testDefinition.expectedResult),
              message: '\n        Statement: ' + testDefinition.beforeCursor + '|' + testDefinition.afterCursor + '\n' +
                         '          Dialect: ' + testDefinition.dialect + '\n' +
                         'Expected response: ' + JSON.stringify(testDefinition.expectedResult) + '\n' +
                         '  Parser response: ' + JSON.stringify(actualResponse) +   '\n'
            };
          }
        }
      }
    },
    assertAutocomplete: function(testDefinition) {
      if (typeof testDefinition.dialect === 'undefined') {
        expect(sql.parseSql(testDefinition.beforeCursor, testDefinition.afterCursor, testDefinition.dialect)).toEqualDefinition(testDefinition);
        testDefinition.dialect = 'hive';
        expect(sql.parseSql(testDefinition.beforeCursor, testDefinition.afterCursor, testDefinition.dialect)).toEqualDefinition(testDefinition);
        testDefinition.dialect = 'impala';
        expect(sql.parseSql(testDefinition.beforeCursor, testDefinition.afterCursor, 'impala')).toEqualDefinition(testDefinition);
      } else {
        expect(sql.parseSql(testDefinition.beforeCursor, testDefinition.afterCursor, testDefinition.dialect)).toEqualDefinition(testDefinition);
      }
    }
  }
});