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

var SqlTestUtils = (function() {

  var jsonStringToJsString = function (jsonString) {
    return jsonString.replace(/'([a-zA-Z]+)':/g, function (all, group) {
      return group + ':';
    }).replace(/([:{,])/g, function (all, group) { return group + ' ' }).replace(/[}]/g, ' }');
  };

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
            if (typeof testDefinition.noErrors === 'undefined' && actualResponse.errors) {
              var allRecoverable = true;
              actualResponse.errors.forEach(function (error) {
                allRecoverable = allRecoverable && error.recoverable;
              });
              if (allRecoverable) {
                delete actualResponse.errors;
              }
            }

            if (testDefinition.locationsOnly) {
              return {
                pass: jasmine.matchersUtil.equals(actualResponse.locations, testDefinition.expectedLocations),
                message: '\n        Statement: ' + testDefinition.beforeCursor + '|' + testDefinition.afterCursor + '\n' +
                '          Dialect: ' + testDefinition.dialect + '\n' +
                'Expected locations: ' + JSON.stringify(testDefinition.expectedLocations).replace(/["]/g, '\'') + '\n' +
                '  Parser locations: ' + JSON.stringify(actualResponse.locations).replace(/["]/g, '\'') +   '\n'
              };
            }

            if (actualResponse.suggestKeywords) {
              var weightFreeKeywords = [];
              actualResponse.suggestKeywords.forEach(function (keyword) {
                weightFreeKeywords.push(keyword.value);
              });
              actualResponse.suggestKeywords = weightFreeKeywords;
            }

            if (testDefinition.hasLocations) {
              if (actualResponse.locations.length === 0) {
                return {
                  pass: false,
                  message: '\nStatement: ' + testDefinition.beforeCursor + '|' + testDefinition.afterCursor + '\n' +
                  '  Dialect: ' + testDefinition.dialect + '\n' +
                  '           No locations found'
                }
              }
            }
            if (testDefinition.hasLocations || actualResponse.locations.length === 0) {
              delete actualResponse.locations;
            }
            var deleteKeywords = false;
            if (testDefinition.containsColRefKeywords) {
              if (typeof actualResponse.suggestColRefKeywords == 'undefined') {
                return {
                  pass: false,
                  message: '\nStatement: ' + testDefinition.beforeCursor + '|' + testDefinition.afterCursor + '\n' +
                  '  Dialect: ' + testDefinition.dialect + '\n' +
                  '           No colRef keywords found'
                }
              } else {
                delete actualResponse.suggestColRefKeywords;
              }
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
              deleteKeywords = true;
            }
            if (typeof testDefinition.doesNotContainKeywords !== 'undefined') {
              var keywords = actualResponse.suggestKeywords;
              var contains = false;
              testDefinition.doesNotContainKeywords.forEach(function (keyword) {
                if (typeof keywords === 'undefined' || keywords.indexOf(keyword) !== -1) {
                  contains = true;
                  return false;
                }
              });
              if (contains) {
                return {
                  pass: false,
                  message: '\n            Statement: ' + testDefinition.beforeCursor + '|' + testDefinition.afterCursor + '\n' +
                  '              Dialect: ' + testDefinition.dialect + '\n' +
                  'Not expected keywords: ' + JSON.stringify(testDefinition.doesNotContainKeywords) + '\n' +
                  '      Parser keywords: ' + JSON.stringify(keywords) +   '\n'
                }
              }
              deleteKeywords = true;
            }

            if (deleteKeywords) {
              delete actualResponse.suggestKeywords;
            }
            return {
              pass: jasmine.matchersUtil.equals(actualResponse, testDefinition.expectedResult),
              message: '\n        Statement: ' + testDefinition.beforeCursor + '|' + testDefinition.afterCursor + '\n' +
                         '          Dialect: ' + testDefinition.dialect + '\n' +
                         'Expected response: ' + jsonStringToJsString(JSON.stringify(testDefinition.expectedResult).replace(/["]/g, '\'') + '\n') +
                         '  Parser response: ' + jsonStringToJsString(JSON.stringify(actualResponse).replace(/["]/g, '\'') +   '\n')
            };
          }
        }
      }
    },

    assertAutocomplete: function(testDefinition) {
      var debug = false;
      if (typeof testDefinition.dialect === 'undefined') {
        expect(sql.parseSql(testDefinition.beforeCursor, testDefinition.afterCursor, testDefinition.dialect, debug)).toEqualDefinition(testDefinition);
        testDefinition.dialect = 'hive';
        expect(sql.parseSql(testDefinition.beforeCursor, testDefinition.afterCursor,  testDefinition.dialect, debug)).toEqualDefinition(testDefinition);
        testDefinition.dialect = 'impala';
        expect(sql.parseSql(testDefinition.beforeCursor, testDefinition.afterCursor,  testDefinition.dialect, debug)).toEqualDefinition(testDefinition);
      } else {
        expect(sql.parseSql(testDefinition.beforeCursor, testDefinition.afterCursor, testDefinition.dialect, debug)).toEqualDefinition(testDefinition);
      }
    }
  }
})();