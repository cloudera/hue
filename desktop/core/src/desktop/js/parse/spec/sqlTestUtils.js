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

import sqlAutocompleteParser from 'parse/sqlAutocompleteParser';

// Needed to compare by val without taking attr order into account
const resultEquals = function(a, b) {
  if (typeof a !== typeof b) {
    return false;
  }
  if (a === b) {
    return true;
  }
  if (typeof a === 'object') {
    const aKeys = Object.keys(a);
    if (aKeys.length !== Object.keys(b).length) {
      return false;
    }
    for (let i = 0; i < aKeys.length; i++) {
      if (!resultEquals(a[aKeys[i]], b[aKeys[i]])) {
        return false;
      }
    }
    return true;
  } else {
    // TODO: Jasmine version?
    return jasmine.jasmine.matchersUtil.equals(a, b);
  }
};

const jsonStringToJsString = function(jsonString) {
  return jsonString
    .replace(/'([a-zA-Z]+)':/g, (all, group) => {
      return group + ':';
    })
    .replace(/([:{,])/g, (all, group) => {
      return group + ' ';
    })
    .replace(/[}]/g, ' }')
    .replace(/["]/g, "'")
    .replace(/'([a-z_]+)':/gi, '$1:');
};

const testUtils = {
  autocompleteMatcher: {
    toEqualAutocompleteValues: function() {
      return {
        compare: function(actualItems, expectedValues) {
          if (actualItems.length !== expectedValues.length) {
            return { pass: false };
          }

          for (let i = 0; i < expectedValues.length; i++) {
            const stringValue =
              typeof actualItems[i] !== 'string' ? '' + actualItems[i].value : actualItems[i].value;
            if (stringValue !== expectedValues[i]) {
              return { pass: false };
            }
          }
          return { pass: true };
        }
      };
    }
  },
  testDefinitionMatcher: {
    toEqualDefinition: function() {
      return {
        compare: function(actualResponse, testDefinition) {
          if (typeof testDefinition.noErrors === 'undefined' && actualResponse.errors) {
            let allRecoverable = true;
            actualResponse.errors.forEach(error => {
              allRecoverable = allRecoverable && error.recoverable;
            });
            if (allRecoverable) {
              delete actualResponse.errors;
            }
          }

          if (testDefinition.dialect !== 'impala' && actualResponse.locations) {
            actualResponse.locations = actualResponse.locations.filter(location => {
              if (location.type !== 'statementType') {
                return location;
              }
            });
          }

          if (testDefinition.expectedDefinitions) {
            if (!resultEquals(actualResponse.definitions, testDefinition.expectedDefinitions)) {
              return {
                pass: false,
                message:
                  '\n        Statement: ' +
                  testDefinition.beforeCursor +
                  '|' +
                  testDefinition.afterCursor +
                  '\n' +
                  '          Dialect: ' +
                  testDefinition.dialect +
                  '\n' +
                  'Expected definitions: ' +
                  jsonStringToJsString(JSON.stringify(testDefinition.expectedDefinitions)) +
                  '\n' +
                  '  Parser definitions: ' +
                  jsonStringToJsString(JSON.stringify(actualResponse.definitions)) +
                  '\n'
              };
            }
          } else {
            delete actualResponse.definitions;
          }

          if (testDefinition.locationsOnly) {
            return {
              pass: resultEquals(actualResponse.locations, testDefinition.expectedLocations),
              message:
                '\n        Statement: ' +
                testDefinition.beforeCursor +
                '|' +
                testDefinition.afterCursor +
                '\n' +
                '          Dialect: ' +
                testDefinition.dialect +
                '\n' +
                'Expected locations: ' +
                jsonStringToJsString(JSON.stringify(testDefinition.expectedLocations)) +
                '\n' +
                '  Parser locations: ' +
                jsonStringToJsString(JSON.stringify(actualResponse.locations)) +
                '\n'
            };
          }

          if (actualResponse.suggestKeywords) {
            const weightFreeKeywords = [];
            actualResponse.suggestKeywords.forEach(keyword => {
              weightFreeKeywords.push(keyword.value);
            });
            actualResponse.suggestKeywords = weightFreeKeywords;
          }

          if (!!testDefinition.noLocations) {
            if (actualResponse.locations.length > 0) {
              return {
                pass: false,
                message:
                  '\nStatement: ' +
                  testDefinition.beforeCursor +
                  '|' +
                  testDefinition.afterCursor +
                  '\n' +
                  '  Dialect: ' +
                  testDefinition.dialect +
                  '\n' +
                  '           Expected no locations, found ' +
                  actualResponse.locations.length
              };
            }
          }
          if (typeof testDefinition.expectedResult.locations === 'undefined') {
            delete actualResponse.locations;
          }
          let deleteKeywords = false;
          if (testDefinition.containsColRefKeywords) {
            if (typeof actualResponse.suggestColRefKeywords == 'undefined') {
              return {
                pass: false,
                message:
                  '\nStatement: ' +
                  testDefinition.beforeCursor +
                  '|' +
                  testDefinition.afterCursor +
                  '\n' +
                  '  Dialect: ' +
                  testDefinition.dialect +
                  '\n' +
                  '           No colRef keywords found'
              };
            } else if (testDefinition.containsColRefKeywords !== true) {
              let contains = true;
              testDefinition.containsColRefKeywords.forEach(keyword => {
                contains =
                  contains &&
                  (actualResponse.suggestColRefKeywords.BOOLEAN.indexOf(keyword) !== -1 ||
                    actualResponse.suggestColRefKeywords.NUMBER.indexOf(keyword) !== -1 ||
                    actualResponse.suggestColRefKeywords.STRING.indexOf(keyword) !== -1);
              });
              if (!contains) {
                return {
                  pass: false,
                  message:
                    '\nStatement: ' +
                    testDefinition.beforeCursor +
                    '|' +
                    testDefinition.afterCursor +
                    '\n' +
                    '  Dialect: ' +
                    testDefinition.dialect +
                    '\n' +
                    '           Expected colRef keywords not found ' +
                    'Expected keywords: ' +
                    JSON.stringify(testDefinition.containsColRefKeywords) +
                    '\n' +
                    '  Parser keywords: ' +
                    JSON.stringify(actualResponse.suggestColRefKeywords) +
                    '\n'
                };
              }
            }
            delete actualResponse.suggestColRefKeywords;
          }

          if (typeof testDefinition.containsKeywords !== 'undefined') {
            const keywords = actualResponse.suggestKeywords;
            let contains = true;
            testDefinition.containsKeywords.forEach(keyword => {
              if (typeof keywords === 'undefined' || keywords.indexOf(keyword) === -1) {
                contains = false;
                return false;
              }
            });
            if (!contains) {
              return {
                pass: false,
                message:
                  '\n        Statement: ' +
                  testDefinition.beforeCursor +
                  '|' +
                  testDefinition.afterCursor +
                  '\n' +
                  '          Dialect: ' +
                  testDefinition.dialect +
                  '\n' +
                  'Expected keywords: ' +
                  JSON.stringify(testDefinition.containsKeywords) +
                  '\n' +
                  '  Parser keywords: ' +
                  JSON.stringify(keywords) +
                  '\n'
              };
            }
            deleteKeywords = true;
          }
          if (typeof testDefinition.doesNotContainKeywords !== 'undefined') {
            const keywords = actualResponse.suggestKeywords;
            let contains = false;
            testDefinition.doesNotContainKeywords.forEach(keyword => {
              if (typeof keywords === 'undefined' || keywords.indexOf(keyword) !== -1) {
                contains = true;
                return false;
              }
            });
            if (contains) {
              return {
                pass: false,
                message:
                  '\n            Statement: ' +
                  testDefinition.beforeCursor +
                  '|' +
                  testDefinition.afterCursor +
                  '\n' +
                  '              Dialect: ' +
                  testDefinition.dialect +
                  '\n' +
                  'Not expected keywords: ' +
                  JSON.stringify(testDefinition.doesNotContainKeywords) +
                  '\n' +
                  '      Parser keywords: ' +
                  JSON.stringify(keywords) +
                  '\n'
              };
            }
            deleteKeywords = true;
          }

          if (deleteKeywords) {
            delete actualResponse.suggestKeywords;
          }
          return {
            pass: resultEquals(actualResponse, testDefinition.expectedResult),
            message:
              '\n        Statement: ' +
              testDefinition.beforeCursor +
              '|' +
              testDefinition.afterCursor +
              '\n' +
              '          Dialect: ' +
              testDefinition.dialect +
              '\n' +
              'Expected response: ' +
              jsonStringToJsString(JSON.stringify(testDefinition.expectedResult) + '\n') +
              '  Parser response: ' +
              jsonStringToJsString(JSON.stringify(actualResponse) + '\n')
          };
        }
      };
    }
  },

  assertAutocomplete: function(testDefinition) {
    const debug = false;
    if (typeof testDefinition.dialect === 'undefined') {
      expect(
        sqlAutocompleteParser.parseSql(
          testDefinition.beforeCursor,
          testDefinition.afterCursor,
          undefined,
          debug
        )
      ).toEqualDefinition(testDefinition);
      expect(
        sqlAutocompleteParser.parseSql(
          testDefinition.beforeCursor,
          testDefinition.afterCursor,
          'hive',
          debug
        )
      ).toEqualDefinition(testDefinition);
      expect(
        sqlAutocompleteParser.parseSql(
          testDefinition.beforeCursor,
          testDefinition.afterCursor,
          'impala',
          debug
        )
      ).toEqualDefinition(testDefinition);
    } else {
      expect(
        sqlAutocompleteParser.parseSql(
          testDefinition.beforeCursor,
          testDefinition.afterCursor,
          testDefinition.dialect,
          debug
        )
      ).toEqualDefinition(testDefinition);
    }
  }
};

export default testUtils;
