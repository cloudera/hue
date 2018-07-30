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

var SqlParseSupport = (function () {

  // endsWith polyfill from hue_utils.js, needed as workers live in their own js environment
  if (!String.prototype.endsWith) {
    String.prototype.endsWith = function (searchString, position) {
      var subjectString = this.toString();
      if (typeof position !== 'number' || !isFinite(position) || Math.floor(position) !== position || position > subjectString.length) {
        position = subjectString.length;
      }
      position -= searchString.length;
      var lastIndex = subjectString.lastIndexOf(searchString, position);
      return lastIndex !== -1 && lastIndex === position;
    };
  }

  /**
   * Calculates the Optimal String Alignment distance between two strings. Returns 0 when the strings are equal and the
   * distance when not, distances is less than or equal to the length of the longest string.
   *
   * @param strA
   * @param strB
   * @param [ignoreCase]
   * @returns {number} The similarity
   */
  var stringDistance = function (strA, strB, ignoreCase) {
    if (ignoreCase) {
      strA = strA.toLowerCase();
      strB = strB.toLowerCase();
    }

    // TODO: Consider other algorithms for performance
    var strALength = strA.length;
    var strBLength = strB.length;
    if (strALength === 0) {
      return strBLength;
    }
    if (strBLength === 0) {
      return strALength;
    }

    var distances = new Array(strALength);

    var cost, deletion, insertion, substitution, transposition;
    for (var i = 0; i <= strALength; i++) {
      distances[i] = new Array(strBLength);
      distances[i][0] = i;
      for (var j = 1; j <= strBLength; j++) {
        if (!i){
          distances[0][j] = j;
        } else {
          cost = strA[i-1] === strB[j-1] ? 0 : 1;
          deletion = distances[i - 1][j] + 1;
          insertion = distances[i][j - 1] + 1;
          substitution = distances[i - 1][j - 1] + cost;
          if (deletion <= insertion && deletion <= substitution) {
            distances[i][j] = deletion;
          } else if (insertion <= deletion && insertion <= substitution) {
            distances[i][j] = insertion;
          } else {
            distances[i][j] = substitution;
          }

          if (i > 1 && j > 1 && strA[i] === strB[j - 1] && strA[i - 1] === strB[j]) {
            transposition = distances[i - 2][j - 2] + cost;
            if (transposition < distances[i][j]) {
              distances[i][j] = transposition;
            }
          }
        }
      }
    }

    return distances[strALength][strBLength];
  };

  var equalIgnoreCase = function (a, b) {
    return a && b && a.toLowerCase() === b.toLowerCase();
  };

  var initSqlParser = function (parser) {

    var SIMPLE_TABLE_REF_SUGGESTIONS = ['suggestJoinConditions', 'suggestAggregateFunctions', 'suggestFilters', 'suggestGroupBys', 'suggestOrderBys'];

    parser.prepareNewStatement = function () {
      linkTablePrimaries();
      parser.commitLocations();

      delete parser.yy.lateralViews;
      delete parser.yy.latestCommonTableExpressions;
      delete parser.yy.correlatedSubQuery;
      parser.yy.subQueries = [];
      parser.yy.selectListAliases = [];
      parser.yy.latestTablePrimaries = [];

      prioritizeSuggestions();
    };

    parser.yy.parseError = function (message, error) {
      parser.yy.errors.push(error);
      return message;
    };

    parser.addCommonTableExpressions = function (identifiers) {
      parser.yy.result.commonTableExpressions = identifiers;
      parser.yy.latestCommonTableExpressions = identifiers;
    };

    parser.isInSubquery = function () {
      return !!parser.yy.primariesStack.length
    };

    parser.pushQueryState = function () {
      parser.yy.resultStack.push(parser.yy.result);
      parser.yy.locationsStack.push(parser.yy.locations);
      parser.yy.lateralViewsStack.push(parser.yy.lateralViews);
      parser.yy.selectListAliasesStack.push(parser.yy.selectListAliases);
      parser.yy.primariesStack.push(parser.yy.latestTablePrimaries);
      parser.yy.subQueriesStack.push(parser.yy.subQueries);

      parser.yy.result = {};
      parser.yy.locations = [];
      parser.yy.selectListAliases = []; // Not allowed in correlated sub-queries
      parser.yy.lateralViews = []; // Not allowed in correlated sub-queries

      if (parser.yy.correlatedSubQuery) {
        parser.yy.latestTablePrimaries = parser.yy.latestTablePrimaries.concat();
        parser.yy.subQueries = parser.yy.subQueries.concat();
      } else {
        parser.yy.latestTablePrimaries = [];
        parser.yy.subQueries = [];
      }
    };

    parser.popQueryState = function (subQuery) {
      linkTablePrimaries();
      parser.commitLocations();

      if (Object.keys(parser.yy.result).length === 0) {
        parser.yy.result = parser.yy.resultStack.pop();
      } else {
        parser.yy.resultStack.pop();
      }
      var oldSubQueries = parser.yy.subQueries;
      parser.yy.subQueries = parser.yy.subQueriesStack.pop();
      if (subQuery) {
        if (oldSubQueries.length > 0) {
          subQuery.subQueries = oldSubQueries;
        }
        parser.yy.subQueries.push(subQuery);
      }

      parser.yy.lateralViews = parser.yy.lateralViewsStack.pop();
      parser.yy.latestTablePrimaries = parser.yy.primariesStack.pop();
      parser.yy.locations = parser.yy.locationsStack.pop();
      parser.yy.selectListAliases = parser.yy.selectListAliasesStack.pop();
    };

    parser.suggestSelectListAliases = function () {
      if (parser.yy.selectListAliases && parser.yy.selectListAliases.length > 0 && parser.yy.result.suggestColumns
        && (typeof parser.yy.result.suggestColumns.identifierChain === 'undefined' || parser.yy.result.suggestColumns.identifierChain.length === 0)) {
        parser.yy.result.suggestColumnAliases = parser.yy.selectListAliases;
      }
    };

    parser.isHive = function () {
      return parser.yy.activeDialect === 'hive';
    };

    parser.isImpala = function () {
      return parser.yy.activeDialect === 'impala';
    };

    parser.mergeSuggestKeywords = function () {
      var result = [];
      Array.prototype.slice.call(arguments).forEach(function (suggestion) {
        if (typeof suggestion !== 'undefined' && typeof suggestion.suggestKeywords !== 'undefined') {
          result = result.concat(suggestion.suggestKeywords);
        }
      });
      if (result.length > 0) {
        return {suggestKeywords: result};
      }
      return {};
    };

    parser.suggestValueExpressionKeywords = function (valueExpression, extras) {
      var expressionKeywords = parser.getValueExpressionKeywords(valueExpression, extras);
      parser.suggestKeywords(expressionKeywords.suggestKeywords);
      if (expressionKeywords.suggestColRefKeywords) {
        parser.suggestColRefKeywords(expressionKeywords.suggestColRefKeywords);
      }
      if (valueExpression.lastType) {
        parser.addColRefIfExists(valueExpression.lastType);
      } else {
        parser.addColRefIfExists(valueExpression);
      }
    };

    parser.getSelectListKeywords = function (excludeAsterisk) {
      var keywords = [{ value: 'CASE', weight: 450 }, 'FALSE', 'TRUE', 'NULL'];
      if (!excludeAsterisk) {
        keywords.push({ value: '*', weight: 10000 });
      }
      if (parser.isHive()) {
        keywords = keywords.concat(['EXISTS', 'NOT']);
      }
      return keywords;
    };

    parser.getValueExpressionKeywords = function (valueExpression, extras) {
      var types = valueExpression.lastType ? valueExpression.lastType.types : valueExpression.types;
      // We could have valueExpression.columnReference to suggest based on column type
      var keywords = ['<', '<=', '<=>', '<>', '=', '>', '>=', 'BETWEEN', 'IN', 'IS NOT NULL', 'IS NULL', 'IS NOT TRUE', 'IS TRUE', 'IS NOT FALSE', 'IS FALSE', 'NOT BETWEEN', 'NOT IN'];
      if (parser.isImpala()) {
        keywords = keywords.concat(['IS DISTINCT FROM', 'IS NOT DISTINCT FROM', 'IS NOT UNKNOWN', 'IS UNKNOWN']);
      }
      if (extras) {
        keywords = keywords.concat(extras);
      }
      if (valueExpression.suggestKeywords) {
        keywords = keywords.concat(valueExpression.suggestKeywords);
      }
      if (types.length === 1 && types[0] === 'COLREF') {
        return {
          suggestKeywords: keywords,
          suggestColRefKeywords: {
            BOOLEAN: ['AND', 'OR'],
            NUMBER: ['+', '-', '*', '/', '%', 'DIV'],
            STRING: parser.isImpala() ? ['ILIKE', 'IREGEXP', 'LIKE', 'NOT LIKE', 'REGEXP', 'RLIKE'] : ['LIKE', 'NOT LIKE', 'REGEXP', 'RLIKE']
          }
        }
      }
      if (typeof SqlFunctions === 'undefined' || SqlFunctions.matchesType(parser.yy.activeDialect, ['BOOLEAN'], types)) {
        keywords = keywords.concat(['AND', 'OR']);
      }
      if (typeof SqlFunctions === 'undefined' || SqlFunctions.matchesType(parser.yy.activeDialect, ['NUMBER'], types)) {
        keywords = keywords.concat(['+', '-', '*', '/', '%', 'DIV']);
      }
      if (typeof SqlFunctions === 'undefined' || SqlFunctions.matchesType(parser.yy.activeDialect, ['STRING'], types)) {
        keywords = keywords.concat(parser.isImpala() ? ['ILIKE', 'IREGEXP', 'LIKE', 'NOT LIKE', 'REGEXP', 'RLIKE'] : ['LIKE', 'NOT LIKE', 'REGEXP', 'RLIKE']);
      }
      return { suggestKeywords: keywords };
    };

    parser.getTypeKeywords = function () {
      if (parser.isHive()) {
        return ['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'DOUBLE PRECISION', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR'];
      }
      if (parser.isImpala()) {
        return ['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'REAL', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR'];
      }
      return ['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR'];
    };

    parser.getColumnDataTypeKeywords = function () {
      if (parser.isHive()) {
        return parser.getTypeKeywords().concat(['ARRAY<>', 'MAP<>', 'STRUCT<>', 'UNIONTYPE<>']);
      }
      if (parser.isImpala()) {
        return parser.getTypeKeywords().concat(['ARRAY<>', 'MAP<>', 'STRUCT<>']);
      }
      return parser.getTypeKeywords();
    };

    parser.addColRefIfExists = function (valueExpression) {
      if (valueExpression.columnReference) {
        parser.yy.result.colRef = {identifierChain: valueExpression.columnReference};
      }
    };

    parser.selectListNoTableSuggest = function (selectListEdit, hasDistinctOrAll) {
      if (selectListEdit.cursorAtStart) {
        var keywords = parser.getSelectListKeywords();
        if (!hasDistinctOrAll) {
          keywords = keywords.concat([{ value: 'ALL', weight: 2 }, { value: 'DISTINCT', weight: 2 }]);
        }
        if (parser.isImpala()) {
          keywords.push('STRAIGHT_JOIN');
        }
        parser.suggestKeywords(keywords);
      } else {
        parser.checkForKeywords(selectListEdit);
      }
      if (selectListEdit.suggestFunctions) {
        parser.suggestFunctions();
      }
      if (selectListEdit.suggestColumns) {
        parser.suggestColumns();
      }
      if (selectListEdit.suggestAggregateFunctions && (!hasDistinctOrAll || hasDistinctOrAll === 'ALL')) {
        parser.suggestAggregateFunctions();
        parser.suggestAnalyticFunctions();
      }
    };

    parser.suggestJoinConditions = function (details) {
      parser.yy.result.suggestJoinConditions = details || {};
      if (parser.yy.latestTablePrimaries && !parser.yy.result.suggestJoinConditions.tablePrimaries) {
        parser.yy.result.suggestJoinConditions.tablePrimaries = parser.yy.latestTablePrimaries.concat();
      }
    };

    parser.suggestJoins = function (details) {
      parser.yy.result.suggestJoins = details || {};
    };

    parser.valueExpressionSuggest = function (oppositeValueExpression, operator) {
      if (oppositeValueExpression && oppositeValueExpression.columnReference) {
        parser.suggestValues();
        parser.yy.result.colRef = {identifierChain: oppositeValueExpression.columnReference};
      }
      parser.suggestColumns();
      parser.suggestFunctions();
      var keywords = [{ value: 'CASE', weight: 450 }, { value: 'FALSE', weight: 450 }, { value: 'NULL', weight: 450 }, { value: 'TRUE', weight: 450 }];
      if (parser.isHive() || typeof oppositeValueExpression === 'undefined' || typeof operator === 'undefined') {
        keywords = keywords.concat(['EXISTS', 'NOT']);
      }
      if (oppositeValueExpression && oppositeValueExpression.types[0] === 'NUMBER') {
        parser.applyTypeToSuggestions(['NUMBER']);
      } else if (parser.isImpala() && (typeof operator === 'undefined' || operator === '-' || operator === '+')) {
        keywords.push('INTERVAL');
      }
      parser.suggestKeywords(keywords);
    };

    parser.applyTypeToSuggestions = function (types) {
      if (types[0] === 'BOOLEAN') {
        return;
      }
      if (parser.yy.result.suggestFunctions && !parser.yy.result.suggestFunctions.types) {
        parser.yy.result.suggestFunctions.types = types;
      }
      if (parser.yy.result.suggestColumns && !parser.yy.result.suggestColumns.types) {
        parser.yy.result.suggestColumns.types = types;
      }
    };

    parser.findCaseType = function (whenThenList) {
      var types = {};
      whenThenList.caseTypes.forEach(function (valueExpression) {
        valueExpression.types.forEach(function (type) {
          types[type] = true;
        });
      });
      if (Object.keys(types).length === 1) {
        return {types: [Object.keys(types)[0]]};
      }
      return {types: ['T']};
    };

    parser.findReturnTypes = function (functionName) {
      return typeof SqlFunctions === 'undefined' ? ['T'] : SqlFunctions.getReturnTypes(parser.yy.activeDialect, functionName.toLowerCase());
    };

    parser.applyArgumentTypesToSuggestions = function (functionName, position) {
      var foundArguments = typeof SqlFunctions === 'undefined' ? ['T'] : SqlFunctions.getArgumentTypes(parser.yy.activeDialect, functionName.toLowerCase(), position);
      if (foundArguments.length == 0 && parser.yy.result.suggestColumns) {
        delete parser.yy.result.suggestColumns;
        delete parser.yy.result.suggestKeyValues;
        delete parser.yy.result.suggestValues;
        delete parser.yy.result.suggestFunctions;
        delete parser.yy.result.suggestIdentifiers;
        delete parser.yy.result.suggestKeywords;
      } else {
        parser.applyTypeToSuggestions(foundArguments);
      }
    };

    var getCleanImpalaPrimaries = function (primaries) {
      var cleanPrimaries = [];
      for (var i = primaries.length - 1; i >= 0; i--) {
        var cleanPrimary = primaries[i];
        if (cleanPrimary.identifierChain && cleanPrimary.identifierChain.length > 0) {
          for (var j = i - 1; j >=0; j--) {
            var parentPrimary = primaries[j];
            if (parentPrimary.alias && cleanPrimary.identifierChain[0].name === parentPrimary.alias) {
              var restOfChain = cleanPrimary.identifierChain.concat();
              restOfChain.shift();
              if (cleanPrimary.alias) {
                cleanPrimary = { identifierChain: parentPrimary.identifierChain.concat(restOfChain), alias: cleanPrimary.alias, impalaComplex: true };
              } else {
                cleanPrimary = { identifierChain: parentPrimary.identifierChain.concat(restOfChain), impalaComplex: true };
              }
            }
          }
        }
        cleanPrimaries.push(cleanPrimary);
      }
      return cleanPrimaries;
    };

    parser.commitLocations = function () {
      if (parser.yy.locations.length === 0) {
        return;
      }

      var tablePrimaries = parser.yy.latestTablePrimaries;

      if (parser.isImpala()) {
        tablePrimaries = [];
        getCleanImpalaPrimaries(parser.yy.latestTablePrimaries).forEach(function (primary) {
          var cleanPrimary = primary;
          if (primary.identifierChain && primary.identifierChain.length > 0) {
            for (var j = parser.yy.primariesStack.length - 1; j >= 0; j--) {
              getCleanImpalaPrimaries(parser.yy.primariesStack[j]).every(function (parentPrimary) {
                if (parentPrimary.alias && parentPrimary.alias === primary.identifierChain[0].name) {
                  var identifierChain = primary.identifierChain.concat();
                  identifierChain.shift();
                  cleanPrimary = { identifierChain: parentPrimary.identifierChain.concat(identifierChain) };
                  if (primary.alias) {
                    cleanPrimary.alias = primary.alias;
                  }
                  return false;
                }
                return true;
              });
            }
          }
          tablePrimaries.unshift(cleanPrimary);
        });
      }
      var i = parser.yy.locations.length;

      while (i--) {
        var location = parser.yy.locations[i];
        if (location.type === 'variable' && location.colRef) {
          parser.expandIdentifierChain({ wrapper: location.colRef, tablePrimaries: tablePrimaries, isColumnWrapper: true });
          delete location.colRef.linked;
        }

        // Impala can have references to previous tables after FROM, i.e. FROM testTable t, t.testArray
        // In this testArray would be marked a type table so we need to switch it to column.
        if (location.type === 'table' && typeof location.identifierChain !== 'undefined' && location.identifierChain.length > 1 && tablePrimaries) {
          var allPrimaries = tablePrimaries;
          parser.yy.primariesStack.forEach(function (parentPrimaries) {
            allPrimaries = getCleanImpalaPrimaries(parentPrimaries).concat(allPrimaries);
          });
          var found = allPrimaries.filter(function (primary) {
            return equalIgnoreCase(primary.alias, location.identifierChain[0].name);
          });
          if (found.length > 0) {
            location.type = 'column';
          }
        }

        if (location.type === 'database' && typeof location.identifierChain !== 'undefined' && location.identifierChain.length > 0 && tablePrimaries) {
          var allPrimaries = tablePrimaries;
          parser.yy.primariesStack.forEach(function (parentPrimaries) {
            allPrimaries = getCleanImpalaPrimaries(parentPrimaries).concat(allPrimaries);
          });
          var foundAlias = allPrimaries.filter(function (primary) {
            return equalIgnoreCase(primary.alias, location.identifierChain[0].name);
          });
          if (foundAlias.length > 0 && parser.isImpala()) {
            // Impala complex reference in FROM clause, i.e. FROM testTable t, t.testMap tm
            location.type = 'table';
            parser.expandIdentifierChain({ tablePrimaries: allPrimaries, wrapper: location, anyOwner: true });
            location.type = location.identifierChain.length === 1 ? 'table' : 'complex';
            continue;
          }
        }

        if (location.type === 'unknown') {
          if (typeof location.identifierChain !== 'undefined' && location.identifierChain.length > 0 && location.identifierChain.length <= 2 && tablePrimaries) {
            var found = tablePrimaries.filter(function (primary) {
              return equalIgnoreCase(primary.alias, location.identifierChain[0].name) || (primary.identifierChain && equalIgnoreCase(primary.identifierChain[0].name, location.identifierChain[0].name));
            });
            if (!found.length && location.firstInChain) {
              found = tablePrimaries.filter(function (primary) {
                return !primary.alias && primary.identifierChain && equalIgnoreCase(primary.identifierChain[primary.identifierChain.length - 1].name, location.identifierChain[0].name);
              });
            }

            if (found.length) {
              if (found[0].identifierChain.length > 1 && location.identifierChain.length === 1 && equalIgnoreCase(found[0].identifierChain[0].name, location.identifierChain[0].name)) {
                location.type = 'database';
              } else if (found[0].alias && equalIgnoreCase(location.identifierChain[0].name, found[0].alias) && location.identifierChain.length > 1) {
                location.type = 'column';
                parser.expandIdentifierChain({ tablePrimaries: tablePrimaries, wrapper: location, anyOwner: true });
              } else if (!found[0].alias && found[0].identifierChain && equalIgnoreCase(location.identifierChain[0].name, found[0].identifierChain[found[0].identifierChain.length - 1].name) && location.identifierChain.length > 1) {
                location.type = 'column';
                parser.expandIdentifierChain({ tablePrimaries: tablePrimaries, wrapper: location, anyOwner: true });
              } else {
                location.type = found[0].impalaComplex ? 'column' : 'table';
                parser.expandIdentifierChain({ tablePrimaries: tablePrimaries, wrapper: location, anyOwner: true });
              }
            } else {
              if (parser.yy.subQueries) {
                found = parser.yy.subQueries.filter(function (subQuery) {
                  return equalIgnoreCase(subQuery.alias, location.identifierChain[0].name);
                });
                if (found.length > 0) {
                  location.type = 'subQuery';
                  location.identifierChain = [{subQuery: found[0].alias}];
                }
              }
            }
          }
        }

        if (location.type === 'asterisk' && !location.linked) {

          if (tablePrimaries && tablePrimaries.length > 0) {
            location.tables = [];
            location.linked = false;
            if (!location.identifierChain) {
              location.identifierChain = [{ asterisk: true }];
            }
            parser.expandIdentifierChain({ tablePrimaries: tablePrimaries, wrapper: location, anyOwner: false });
            if (location.tables.length === 0) {
              parser.yy.locations.splice(i, 1);
            }
          } else {
            parser.yy.locations.splice(i, 1);
          }
        }

        if (location.type === 'table' && typeof location.identifierChain !== 'undefined' && location.identifierChain.length === 1 && location.identifierChain[0].name) {
          // Could be a cte reference
          parser.yy.locations.some(function (otherLocation) {
            if (otherLocation.type === 'alias' && otherLocation.source === 'cte' && SqlUtils.identifierEquals(otherLocation.alias, location.identifierChain[0].name)) {
              // TODO: Possibly add the other location if we want to show the link in the future.
              //       i.e. highlight select definition on hover over alias, also for subquery references.
              location.type = 'alias';
              location.target = 'cte';
              location.alias = location.identifierChain[0].name;
              delete location.identifierChain;
              return true;
            }
          });
        }

        if (location.type === 'table' && (typeof location.identifierChain === 'undefined' || location.identifierChain.length === 0)) {
          parser.yy.locations.splice(i, 1);
        }

        if (location.type === 'unknown') {
          location.type = 'column';
        }

        // A column location might refer to a previously defined alias, i.e. last 'foo' in "SELECT cast(id AS int) foo FROM tbl ORDER BY foo;"
        if (location.type === 'column') {
          for (var j = i - 1; j >= 0; j--) {
            var otherLocation = parser.yy.locations[j];
            if (otherLocation.type === 'alias' && otherLocation.source === 'column' && location.identifierChain && location.identifierChain.length === 1 && location.identifierChain[0].name && otherLocation.alias && location.identifierChain[0].name.toLowerCase() === otherLocation.alias.toLowerCase()) {
              location.type = 'alias';
              location.source = 'column';
              location.alias = location.identifierChain[0].name;
              delete location.identifierChain;
              location.parentLocation = otherLocation.parentLocation;
              break;
            }
          }
        }

        if (location.type === 'column') {
          if (parser.isHive() && !location.linked) {
            location.identifierChain = parser.expandLateralViews(parser.yy.lateralViews, location.identifierChain);
          }

          var initialIdentifierChain = location.identifierChain ? location.identifierChain.concat() : undefined;

          parser.expandIdentifierChain({ tablePrimaries: tablePrimaries, wrapper: location, anyOwner: true, isColumnWrapper: true, isColumnLocation: true });

          if (typeof location.identifierChain === 'undefined') {
            parser.yy.locations.splice(i, 1);
          } else if (location.identifierChain.length === 0 && initialIdentifierChain && initialIdentifierChain.length === 1) {
            // This is for the case "SELECT tblOrColName FROM db.tblOrColName";
            location.identifierChain = initialIdentifierChain;
          }
        }
        if (location.type === 'column' && location.identifierChain) {
          if (location.identifierChain.length > 1 && location.tables && location.tables.length > 0) {
            location.type = 'complex';
          }
        }
        delete location.firstInChain;
        if (location.type !== 'column' && location.type !== 'complex') {
          delete location.qualified;
        } else if (typeof location.qualified === 'undefined') {
          location.qualified = false;
        }
      }

      if (parser.yy.locations.length > 0) {
        parser.yy.allLocations = parser.yy.allLocations.concat(parser.yy.locations);
        parser.yy.locations = [];
      }
    };

    var prioritizeSuggestions = function () {
      parser.yy.result.lowerCase = parser.yy.lowerCase || false;

      var cteIndex = {};

      if (typeof parser.yy.latestCommonTableExpressions !== 'undefined') {
        parser.yy.latestCommonTableExpressions.forEach(function (cte) {
          cteIndex[cte.alias.toLowerCase()] = cte;
        })
      }

      SIMPLE_TABLE_REF_SUGGESTIONS.forEach(function (suggestionType) {
        if (suggestionType !== 'suggestAggregateFunctions' && typeof parser.yy.result[suggestionType] !== 'undefined' && parser.yy.result[suggestionType].tables.length === 0) {
          delete parser.yy.result[suggestionType];
        } else if (typeof parser.yy.result[suggestionType] !== 'undefined' && typeof parser.yy.result[suggestionType].tables !== 'undefined') {
          for (var i = parser.yy.result[suggestionType].tables.length - 1; i >= 0; i--) {
            var table = parser.yy.result[suggestionType].tables[i];
            if (table.identifierChain.length === 1 && typeof table.identifierChain[0].name !== 'undefined' && typeof cteIndex[table.identifierChain[0].name.toLowerCase()] !== 'undefined') {
              parser.yy.result[suggestionType].tables.splice(i, 1);
            }
          }
        }
      });

      if (typeof parser.yy.result.colRef !== 'undefined') {
        if (!parser.yy.result.colRef.linked || typeof parser.yy.result.colRef.identifierChain === 'undefined' || parser.yy.result.colRef.identifierChain.length === 0) {
          delete parser.yy.result.colRef;
          if (typeof parser.yy.result.suggestColRefKeywords !== 'undefined') {
            Object.keys(parser.yy.result.suggestColRefKeywords).forEach(function (type) {
              parser.yy.result.suggestKeywords = parser.yy.result.suggestKeywords.concat(parser.createWeightedKeywords(parser.yy.result.suggestColRefKeywords[type], -1));
            });
            delete parser.yy.result.suggestColRefKeywords;
          }
          if (parser.yy.result.suggestColumns && parser.yy.result.suggestColumns.types.length === 1 && parser.yy.result.suggestColumns.types[0] === 'COLREF') {
            parser.yy.result.suggestColumns.types = ['T'];
          }
          delete parser.yy.result.suggestValues;
        }
      }

      if (typeof parser.yy.result.colRef !== 'undefined') {
        if (!parser.yy.result.suggestValues && !parser.yy.result.suggestColRefKeywords &&
          (!parser.yy.result.suggestColumns ||
          parser.yy.result.suggestColumns.types[0] !== 'COLREF')) {
          delete parser.yy.result.colRef;
        }
      }
      if (typeof parser.yy.result.suggestIdentifiers !== 'undefined' && parser.yy.result.suggestIdentifiers.length > 0) {
        delete parser.yy.result.suggestTables;
        delete parser.yy.result.suggestDatabases;
      }
      if (typeof parser.yy.result.suggestColumns !== 'undefined') {
        var suggestColumns = parser.yy.result.suggestColumns;
        if (typeof suggestColumns.tables === 'undefined' || suggestColumns.tables.length === 0) {
          // Impala supports statements like SELECT * FROM tbl1, tbl2 WHERE db.tbl1.col = tbl2.bla
          if (parser.yy.result.suggestColumns.linked && parser.isImpala() && typeof suggestColumns.identifierChain !== 'undefined' && suggestColumns.identifierChain.length > 0) {
            if (suggestColumns.identifierChain.length === 1) {
              parser.yy.result.suggestTables = suggestColumns;
              delete parser.yy.result.suggestColumns
            } else {
              suggestColumns.tables = [{identifierChain: suggestColumns.identifierChain}];
              delete suggestColumns.identifierChain;
            }
          } else {
            delete parser.yy.result.suggestColumns;
            delete parser.yy.result.subQueries;
          }
        } else {
          delete parser.yy.result.suggestTables;
          delete parser.yy.result.suggestDatabases;

          suggestColumns.tables.forEach(function (table) {
            if (typeof table.identifierChain !== 'undefined' && table.identifierChain.length === 1 && typeof table.identifierChain[0].name !== 'undefined') {
              var cte = cteIndex[table.identifierChain[0].name.toLowerCase()];
              if (typeof cte !== 'undefined') {
                delete table.identifierChain[0].name;
                table.identifierChain[0].cte = cte.alias;
              }
            } else if (typeof table.identifierChain === 'undefined' && table.subQuery) {
              table.identifierChain = [{ subQuery: table.subQuery }];
              delete table.subQuery;
            }
          });

          if (typeof suggestColumns.identifierChain !== 'undefined' && suggestColumns.identifierChain.length === 0) {
            delete suggestColumns.identifierChain;
          }
        }
      } else {
        delete parser.yy.result.subQueries;
      }

      if (typeof parser.yy.result.suggestJoinConditions !== 'undefined') {
        if (typeof parser.yy.result.suggestJoinConditions.tables === 'undefined' || parser.yy.result.suggestJoinConditions.tables.length === 0) {
          delete parser.yy.result.suggestJoinConditions;
        }
      }

      if (typeof parser.yy.result.suggestTables !== 'undefined' && typeof parser.yy.latestCommonTableExpressions !== 'undefined') {
        var ctes = [];
        parser.yy.latestCommonTableExpressions.forEach(function (cte) {
          var suggestion = {name: cte.alias};
          if (parser.yy.result.suggestTables.prependFrom) {
            suggestion.prependFrom = true
          }
          if (parser.yy.result.suggestTables.prependQuestionMark) {
            suggestion.prependQuestionMark = true;
          }
          ctes.push(suggestion);
        });
        if (ctes.length > 0) {
          parser.yy.result.suggestCommonTableExpressions = ctes;
        }
      }
    };

    /**
     * Impala supports referencing maps and arrays in the the table reference list i.e.
     *
     *  SELECT m['foo'].bar.| FROM someDb.someTable t, t.someMap m;
     *
     * From this the tablePrimaries would look like:
     *
     * [ { alias: 't', identifierChain: [ { name: 'someDb' }, { name: 'someTable' } ] },
     *   { alias: 'm', identifierChain: [ { name: 't' }, { name: 'someMap' } ] } ]
     *
     * with an identifierChain from the select list:
     *
     * [ { name: 'm', keySet: true }, { name: 'bar' } ]
     *
     * Calling this would return an expanded identifierChain, given the above it would be:
     *
     * [ { name: 't' }, { name: 'someMap', keySet: true }, { name: 'bar' } ]
     */
    parser.expandImpalaIdentifierChain = function (tablePrimaries, identifierChain) {
      var expandedChain = identifierChain.concat(); // Clone in case it's called multiple times.
      if (typeof expandedChain === 'undefined' || expandedChain.length === 0) {
        return identifierChain;
      }
      var expand = function (identifier, expandedChain) {
        var foundPrimary = tablePrimaries.filter(function (tablePrimary) {
          var primaryIdentifier = tablePrimary.alias;
          if (!primaryIdentifier && tablePrimary.identifierChain && tablePrimary.identifierChain.length > 0) {
            primaryIdentifier = tablePrimary.identifierChain[tablePrimary.identifierChain.length - 1].name;
          }
          return equalIgnoreCase(primaryIdentifier, identifier);
        });

        if (foundPrimary.length === 1 && foundPrimary[0].identifierChain) {
          var parentPrimary = tablePrimaries.filter(function (tablePrimary) {
            return equalIgnoreCase(tablePrimary.alias, foundPrimary[0].identifierChain[0].name);
          });
          if (parentPrimary.length === 1) {
            var keySet = expandedChain[0].keySet;
            var secondPart = expandedChain.slice(1);
            var firstPart = [];
            // Clone to make sure we don't add keySet to the primaries
            foundPrimary[0].identifierChain.forEach(function (identifier) {
              firstPart.push({name: identifier.name});
            });
            if (keySet && firstPart.length > 0) {
              firstPart[firstPart.length - 1].keySet = true;
            }

            if (firstPart.length === 0 || typeof secondPart === 'undefined' || secondPart.length === 0) {
              return firstPart;
            }
            var result = firstPart.concat(secondPart);
            if (result.length > 0) {
              return expand(firstPart[0].name, result);
            } else {
              return result;
            }
          }
        }
        return expandedChain;
      };
      return expand(expandedChain[0].name, expandedChain);
    };

    parser.identifyPartials = function (beforeCursor, afterCursor) {
      var beforeMatch = beforeCursor.match(/[0-9a-zA-Z_]*$/);
      var afterMatch = afterCursor.match(/^[0-9a-zA-Z_]*(?:\((?:[^)]*\))?)?/);
      return {left: beforeMatch ? beforeMatch[0].length : 0, right: afterMatch ? afterMatch[0].length : 0};
    };

    parser.expandLateralViews = function (lateralViews, originalIdentifierChain, columnSuggestion) {
      var identifierChain = originalIdentifierChain.concat(); // Clone in case it's re-used
      var firstIdentifier = identifierChain[0];
      if (typeof lateralViews !== 'undefined') {
        lateralViews.concat().reverse().forEach(function (lateralView) {
          if (!lateralView.udtf.expression.columnReference) {
            return;
          }
          if (equalIgnoreCase(firstIdentifier.name, lateralView.tableAlias) && identifierChain.length > 1) {
            identifierChain.shift();
            firstIdentifier = identifierChain[0];
            if (columnSuggestion) {
              delete parser.yy.result.suggestKeywords;
            }
          } else if (equalIgnoreCase(firstIdentifier.name, lateralView.tableAlias) && identifierChain.length === 1 && typeof parser.yy.result.suggestColumns !== 'undefined') {
            if (columnSuggestion) {
              if (typeof parser.yy.result.suggestIdentifiers === 'undefined') {
                parser.yy.result.suggestIdentifiers = [];
              }
              lateralView.columnAliases.forEach(function (columnAlias) {
                parser.yy.result.suggestIdentifiers.push({name: columnAlias, type: 'alias'});
              });
              delete parser.yy.result.suggestColumns;
              delete parser.yy.result.suggestKeywords;
            }
            return identifierChain;
          }
          if (lateralView.columnAliases.indexOf(firstIdentifier.name) !== -1) {
            if (lateralView.columnAliases.length === 2 && lateralView.udtf.function.toLowerCase() === 'explode' && equalIgnoreCase(firstIdentifier.name, lateralView.columnAliases[0])) {
              identifierChain[0] = {name: 'key'};
            } else if (lateralView.columnAliases.length === 2 && lateralView.udtf.function.toLowerCase() === 'explode' && equalIgnoreCase(firstIdentifier.name, lateralView.columnAliases[1])) {
              identifierChain[0] = {name: 'value'};
            } else {
              identifierChain[0] = {name: 'item'};
            }
            identifierChain = lateralView.udtf.expression.columnReference.concat(identifierChain);
            firstIdentifier = identifierChain[0];
          }
        });
      }
      return identifierChain;
    };

    var addCleanTablePrimary = function (tables, tablePrimary) {
      if (tablePrimary.alias) {
        tables.push({alias: tablePrimary.alias, identifierChain: tablePrimary.identifierChain});
      } else {
        tables.push({identifierChain: tablePrimary.identifierChain});
      }
    };

    parser.expandIdentifierChain = function (options) {
      var wrapper = options.wrapper;
      var anyOwner = options.anyOwner;
      var isColumnWrapper = options.isColumnWrapper;
      var isColumnLocation = options.isColumnLocation;
      var tablePrimaries = options.tablePrimaries || parser.yy.latestTablePrimaries;

      if (typeof wrapper.identifierChain === 'undefined' || typeof tablePrimaries === 'undefined') {
        return;
      }
      var identifierChain = wrapper.identifierChain.concat();

      if (tablePrimaries.length === 0) {
        delete wrapper.identifierChain;
        return;
      }

      if (!anyOwner) {
        tablePrimaries = filterTablePrimariesForOwner(tablePrimaries, wrapper.owner);
      }

      if (identifierChain.length > 0 && identifierChain[identifierChain.length - 1].asterisk) {
        var tables = [];
        tablePrimaries.forEach(function (tablePrimary) {
          if (identifierChain.length > 1 && !tablePrimary.subQueryAlias) {
            if (identifierChain.length === 2 && equalIgnoreCase(tablePrimary.alias, identifierChain[0].name)) {
              addCleanTablePrimary(tables, tablePrimary);
            } else if (identifierChain.length === 2 && equalIgnoreCase(tablePrimary.identifierChain[0].name, identifierChain[0].name)) {
              addCleanTablePrimary(tables, tablePrimary);
            } else if (identifierChain.length === 3 && tablePrimary.identifierChain.length > 1 &&
              equalIgnoreCase(tablePrimary.identifierChain[0].name, identifierChain[0].name) &&
              equalIgnoreCase(tablePrimary.identifierChain[1].name, identifierChain[1].name)) {
              addCleanTablePrimary(tables, tablePrimary);
            }
          } else {
            if (tablePrimary.subQueryAlias) {
              tables.push({identifierChain: [{subQuery: tablePrimary.subQueryAlias}]});
            } else {
              addCleanTablePrimary(tables, tablePrimary);
            }
          }
        });
        // Possible Joins
        if (tables.length > 0) {
          wrapper.tables = tables;
          delete wrapper.identifierChain;
          return;
        }
      }

      // Impala can have references to maps or array, i.e. FROM table t, t.map m
      // We need to replace those in the identifierChain
      if (parser.isImpala()) {
        var lengthBefore = identifierChain.length;
        identifierChain = parser.expandImpalaIdentifierChain(tablePrimaries, identifierChain);
        // Change type of any locations marked as table
        if (wrapper.type === 'table' && identifierChain.length > lengthBefore) {
          wrapper.type = 'column';
        }
        wrapper.identifierChain = identifierChain;
      }
      // Expand exploded views in the identifier chain
      if (parser.isHive() && identifierChain.length > 0) {
        identifierChain = parser.expandLateralViews(parser.yy.lateralViews, identifierChain);
        wrapper.identifierChain = identifierChain;
      }

      // IdentifierChain contains a possibly started identifier or empty, example: a.b.c = ['a', 'b', 'c']
      // Reduce the tablePrimaries to the one that matches the first identifier if found
      var foundPrimary;
      var doubleMatch = false;
      var aliasMatch = false;
      if (identifierChain.length > 0) {
        for (var i = 0; i < tablePrimaries.length; i++) {
          if (tablePrimaries[i].subQueryAlias) {
            if (equalIgnoreCase(tablePrimaries[i].subQueryAlias, identifierChain[0].name)) {
              foundPrimary = tablePrimaries[i];
            }
          } else if (equalIgnoreCase(tablePrimaries[i].alias, identifierChain[0].name)) {
            foundPrimary = tablePrimaries[i];
            aliasMatch = true;
            break;
          } else if (tablePrimaries[i].identifierChain.length > 1 && identifierChain.length > 1 &&
            equalIgnoreCase(tablePrimaries[i].identifierChain[0].name, identifierChain[0].name) &&
            equalIgnoreCase(tablePrimaries[i].identifierChain[1].name, identifierChain[1].name)) {
            foundPrimary = tablePrimaries[i];
            doubleMatch = true;
            break;
          } else if (!foundPrimary && equalIgnoreCase(tablePrimaries[i].identifierChain[0].name, identifierChain[0].name) && identifierChain.length > (isColumnLocation ? 1 : 0)) {
            foundPrimary = tablePrimaries[i];
            // No break as first two can still match.
          } else if (!foundPrimary && tablePrimaries[i].identifierChain.length > 1 && !tablePrimaries[i].alias
            && equalIgnoreCase(tablePrimaries[i].identifierChain[tablePrimaries[i].identifierChain.length - 1].name, identifierChain[0].name)) {
            // This is for the case SELECT baa. FROM bla.baa, blo.boo;
            foundPrimary = tablePrimaries[i];
            break;
          }
        }
      }

      if (foundPrimary) {
        if (foundPrimary.impalaComplex && wrapper.type === 'column') {
          wrapper.type = 'complex';
        }
        identifierChain.shift();
        if (doubleMatch) {
          identifierChain.shift();
        }
      } else if (tablePrimaries.length === 1 && !isColumnWrapper) {
        foundPrimary = tablePrimaries[0];
      }

      if (foundPrimary) {
        if (isColumnWrapper) {
          wrapper.identifierChain = identifierChain;
          if (foundPrimary.subQueryAlias) {
            wrapper.tables = [{ subQuery: foundPrimary.subQueryAlias }];
          } else if (foundPrimary.alias) {
            if (!isColumnLocation && isColumnWrapper && aliasMatch) {
              // TODO: add alias on table in suggestColumns (needs support in sqlAutocomplete3.js)
              // the case is: SELECT cu.| FROM customers cu;
              // This prevents alias from being added automatically in sqlAutocompleter3.js
              wrapper.tables = [{ identifierChain: foundPrimary.identifierChain }];
            } else {
              wrapper.tables = [{ identifierChain: foundPrimary.identifierChain, alias: foundPrimary.alias }];
            }
          } else {
            wrapper.tables = [{ identifierChain: foundPrimary.identifierChain }];
          }
        } else {
          if (foundPrimary.subQueryAlias) {
            identifierChain.unshift({ subQuery: foundPrimary.subQueryAlias });
          } else {
            identifierChain = foundPrimary.identifierChain.concat(identifierChain);
          }
          if (wrapper.tables) {
            wrapper.tables.push({identifierChain: identifierChain});
            delete wrapper.identifierChain;
          } else {
            wrapper.identifierChain = identifierChain;
          }
        }
      } else {
        if (isColumnWrapper) {
          wrapper.tables = [];
        }
        tablePrimaries.forEach(function (tablePrimary) {
          var targetTable = tablePrimary.subQueryAlias ? { subQuery: tablePrimary.subQueryAlias } : { identifierChain: tablePrimary.identifierChain } ;
          if (tablePrimary.alias) {
            targetTable.alias = tablePrimary.alias;
          }
          if (wrapper.tables) {
            wrapper.tables.push(targetTable)
          }
        });
      }
      delete wrapper.owner;
      wrapper.linked = true;
    };

    var suggestLateralViewAliasesAsIdentifiers = function () {
      if (typeof parser.yy.lateralViews === 'undefined' || parser.yy.lateralViews.length === 0) {
        return;
      }
      if (typeof parser.yy.result.suggestIdentifiers === 'undefined') {
        parser.yy.result.suggestIdentifiers = [];
      }
      parser.yy.lateralViews.forEach(function (lateralView) {
        if (typeof lateralView.tableAlias !== 'undefined') {
          parser.yy.result.suggestIdentifiers.push({name: lateralView.tableAlias + '.', type: 'alias'});
        }
        lateralView.columnAliases.forEach(function (columnAlias) {
          parser.yy.result.suggestIdentifiers.push({name: columnAlias, type: 'alias'});
        });
      });
      if (parser.yy.result.suggestIdentifiers.length === 0) {
        delete parser.yy.result.suggestIdentifiers;
      }
    };

    var filterTablePrimariesForOwner = function (tablePrimaries, owner) {
      var result = [];
      tablePrimaries.forEach(function (primary) {
        if (typeof owner === 'undefined' && typeof primary.owner === 'undefined') {
          result.push(primary);
        } else if (owner === primary.owner) {
          result.push(primary);
        }
      });
      return result;
    };

    var convertTablePrimariesToSuggestions = function (tablePrimaries) {
      var tables = [];
      var identifiers = [];
      tablePrimaries.forEach(function (tablePrimary) {
        if (tablePrimary.identifierChain && tablePrimary.identifierChain.length > 0) {
          var table = {identifierChain: tablePrimary.identifierChain};
          if (tablePrimary.alias) {
            table.alias = tablePrimary.alias;
            identifiers.push({name: table.alias + '.', type: 'alias'});
            if (parser.isImpala()) {
              var testForImpalaAlias = [{name: table.alias}];
              var result = parser.expandImpalaIdentifierChain(tablePrimaries, testForImpalaAlias);
              if (result.length > 1) {
                // Continue if it's a reference to a complex type
                return;
              }
            }
          } else {
            var lastIdentifier = tablePrimary.identifierChain[tablePrimary.identifierChain.length - 1];
            if (typeof lastIdentifier.name !== 'undefined') {
              identifiers.push({name: lastIdentifier.name + '.', type: 'table'});
            } else if (typeof lastIdentifier.subQuery !== 'undefined') {
              identifiers.push({name: lastIdentifier.subQuery + '.', type: 'sub-query'});
            }
          }
          tables.push(table);
        } else if (tablePrimary.subQueryAlias) {
          identifiers.push({name: tablePrimary.subQueryAlias + '.', type: 'sub-query'});
          tables.push({identifierChain: [{subQuery: tablePrimary.subQueryAlias}]});
        }
      });
      if (identifiers.length > 0) {
        if (typeof parser.yy.result.suggestIdentifiers === 'undefined') {
          parser.yy.result.suggestIdentifiers = identifiers;
        } else {
          parser.yy.result.suggestIdentifiers = identifiers.concat(parser.yy.result.suggestIdentifiers);
        }
      }
      parser.yy.result.suggestColumns.tables = tables;
      if (parser.yy.result.suggestColumns.identifierChain && parser.yy.result.suggestColumns.identifierChain.length === 0) {
        delete parser.yy.result.suggestColumns.identifierChain;
      }
      parser.yy.result.suggestColumns.linked = true;
    };

    var linkTablePrimaries = function () {
      if (!parser.yy.cursorFound || typeof parser.yy.latestTablePrimaries === 'undefined') {
        return;
      }

      SIMPLE_TABLE_REF_SUGGESTIONS.forEach(function (suggestionType) {
        if (typeof parser.yy.result[suggestionType] !== 'undefined' && parser.yy.result[suggestionType].tablePrimaries && !parser.yy.result[suggestionType].linked) {
          parser.yy.result[suggestionType].tables = [];
          parser.yy.result[suggestionType].tablePrimaries.forEach(function (tablePrimary) {
            if (!tablePrimary.subQueryAlias) {
              parser.yy.result[suggestionType].tables.push(tablePrimary.alias ? {
                identifierChain: tablePrimary.identifierChain.concat(),
                alias: tablePrimary.alias
              } : {identifierChain: tablePrimary.identifierChain.concat()});
            }
          });
          delete parser.yy.result[suggestionType].tablePrimaries;
          parser.yy.result[suggestionType].linked = true;
        }
      });

      if (typeof parser.yy.result.suggestColumns !== 'undefined' && !parser.yy.result.suggestColumns.linked) {
        var tablePrimaries = filterTablePrimariesForOwner(parser.yy.latestTablePrimaries, parser.yy.result.suggestColumns.owner);
        if (!parser.yy.result.suggestColumns.tables) {
          parser.yy.result.suggestColumns.tables = [];
        }
        if (parser.yy.subQueries.length > 0) {
          parser.yy.result.subQueries = parser.yy.subQueries;
        }
        if (typeof parser.yy.result.suggestColumns.identifierChain === 'undefined' || parser.yy.result.suggestColumns.identifierChain.length === 0) {
          if (tablePrimaries.length > 1) {
            convertTablePrimariesToSuggestions(tablePrimaries);
          } else {
            suggestLateralViewAliasesAsIdentifiers();
            if (tablePrimaries.length === 1 && (tablePrimaries[0].alias || tablePrimaries[0].subQueryAlias)) {
              convertTablePrimariesToSuggestions(tablePrimaries);
            }
            parser.expandIdentifierChain({ wrapper: parser.yy.result.suggestColumns, anyOwner: false, isColumnWrapper: true });
          }
        } else {
          // Expand exploded views in the identifier chain
          if (parser.isHive() && !parser.yy.result.suggestColumns.linked) {
            var originalLength = parser.yy.result.suggestColumns.identifierChain.length;
            parser.yy.result.suggestColumns.identifierChain = parser.expandLateralViews(parser.yy.lateralViews, parser.yy.result.suggestColumns.identifierChain, true);
            // Drop '*' keyword for lateral views
            if (typeof parser.yy.result.suggestColumns !== 'undefined') {
              if (parser.yy.result.suggestColumns.identifierChain.length > originalLength &&
                typeof parser.yy.result.suggestKeywords !== 'undefined' &&
                parser.yy.result.suggestKeywords.length === 1 &&
                parser.yy.result.suggestKeywords[0].value === '*') {
                delete parser.yy.result.suggestKeywords;
              }
              parser.expandIdentifierChain({ wrapper: parser.yy.result.suggestColumns, anyOwner: false, isColumnWrapper: true });
            }
          } else {
            parser.expandIdentifierChain({ wrapper: parser.yy.result.suggestColumns, anyOwner: false, isColumnWrapper: true });
          }
        }
      }

      if (typeof parser.yy.result.colRef !== 'undefined' && !parser.yy.result.colRef.linked) {
        parser.expandIdentifierChain({ wrapper: parser.yy.result.colRef });

        var primaries = filterTablePrimariesForOwner(parser.yy.latestTablePrimaries);
        if (primaries.length === 0 || (primaries.length > 1 && parser.yy.result.colRef.identifierChain.length === 1)) {
          parser.yy.result.colRef.identifierChain = [];
        }
      }
      if (typeof parser.yy.result.suggestKeyValues !== 'undefined' && !parser.yy.result.suggestKeyValues.linked) {
        parser.expandIdentifierChain({ wrapper: parser.yy.result.suggestKeyValues });
      }
    };

    parser.getSubQuery = function (cols) {
      var columns = [];
      cols.selectList.forEach(function (col) {
        var result = {};
        if (col.alias) {
          result.alias = col.alias;
        }
        if (col.valueExpression && col.valueExpression.columnReference) {
          result.identifierChain = col.valueExpression.columnReference
        } else if (col.asterisk) {
          result.identifierChain = [{asterisk: true}];
        }
        if (col.valueExpression && col.valueExpression.types && col.valueExpression.types.length === 1) {
          result.type = col.valueExpression.types[0];
        }

        columns.push(result);
      });

      return {
        columns: columns
      };
    };

    parser.addTablePrimary = function (ref) {
      if (typeof parser.yy.latestTablePrimaries === 'undefined') {
        parser.yy.latestTablePrimaries = [];
      }
      parser.yy.latestTablePrimaries.push(ref);
    };

    parser.suggestFileFormats = function () {
      if (parser.isHive()) {
        parser.suggestKeywords(['AVRO', 'INPUTFORMAT', 'ORC', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']);
      } else {
        parser.suggestKeywords(['AVRO', 'KUDU', 'ORC', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']);
      }
    };

    parser.getKeywordsForOptionalsLR = function (optionals, keywords, override) {
      var result = [];

      for (var i = 0; i < optionals.length; i++) {
        if (!optionals[i] && (typeof override === 'undefined' || override[i])) {
          if (keywords[i] instanceof Array) {
            result = result.concat(keywords[i]);
          } else {
            result.push(keywords[i]);
          }
        } else if (optionals[i]) {
          break;
        }
      }
      return result;
    };

    parser.suggestDdlAndDmlKeywords = function (extraKeywords) {
      var keywords = ['ALTER', 'CREATE', 'DESCRIBE', 'DROP', 'GRANT', 'INSERT', 'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE', 'WITH'];

      if (extraKeywords) {
        keywords = keywords.concat(extraKeywords);
      }

      if (parser.isHive()) {
        keywords = keywords.concat(['ABORT', 'ANALYZE TABLE', 'DELETE', 'EXPORT', 'IMPORT', 'LOAD', 'MERGE', 'MSCK', 'RELOAD FUNCTION', 'RESET']);
      }

      if (parser.isImpala()) {
        keywords = keywords.concat(['COMMENT ON', 'COMPUTE', 'DELETE', 'INVALIDATE METADATA', 'LOAD', 'REFRESH', 'UPSERT']);
      }

      parser.suggestKeywords(keywords);
    };

    parser.checkForSelectListKeywords = function (selectList) {
      if (selectList.length === 0) {
        return;
      }
      var last = selectList[selectList.length - 1];
      if (!last || !last.valueExpression) {
        return;
      }
      var valueExpressionKeywords = parser.getValueExpressionKeywords(last.valueExpression);
      var keywords = [];
      if (last.suggestKeywords) {
        keywords = keywords.concat(last.suggestKeywords);
      }
      if (valueExpressionKeywords.suggestKeywords) {
        keywords = keywords.concat(valueExpressionKeywords.suggestKeywords);
      }
      if (valueExpressionKeywords.suggestColRefKeywords) {
        parser.suggestColRefKeywords(valueExpressionKeywords.suggestColRefKeywords);
        parser.addColRefIfExists(last.valueExpression);
      }
      if (!last.alias) {
        keywords.push('AS');
      }
      if (keywords.length > 0) {
        parser.suggestKeywords(keywords);
      }
    };

    parser.checkForKeywords = function (expression) {
      if (expression) {
        if (expression.suggestKeywords && expression.suggestKeywords.length > 0) {
          parser.suggestKeywords(expression.suggestKeywords);
        }
        if (expression.suggestColRefKeywords) {
          parser.suggestColRefKeywords(expression.suggestColRefKeywords);
          parser.addColRefIfExists(expression);
        }
      }
    };

    parser.createWeightedKeywords = function (keywords, weight) {
      var result = [];
      keywords.forEach(function (keyword) {
        if (typeof keyword.weight !== 'undefined') {
          keyword.weight = weight + (keyword.weight / 10);
          result.push(keyword);
        } else {
          result.push({value: keyword, weight: weight});
        }
      });
      return result;
    };

    parser.suggestKeywords = function (keywords) {
      var weightedKeywords = [];
      if (keywords.length == 0) {
        return;
      }
      keywords.forEach(function (keyword) {
        if (typeof keyword.weight !== 'undefined') {
          weightedKeywords.push(keyword);
        } else {
          weightedKeywords.push({value: keyword, weight: -1})
        }
      });
      weightedKeywords.sort(function (a, b) {
        if (a.weight !== b.weight) {
          return b.weight - a.weight;
        }
        return a.value.localeCompare(b.value);
      });
      parser.yy.result.suggestKeywords = weightedKeywords;
    };

    parser.suggestColRefKeywords = function (colRefKeywords) {
      parser.yy.result.suggestColRefKeywords = colRefKeywords;
    };

    parser.suggestTablesOrColumns = function (identifier) {
      if (typeof parser.yy.latestTablePrimaries == 'undefined') {
        parser.suggestTables({identifierChain: [{name: identifier}]});
        return;
      }
      var tableRef = parser.yy.latestTablePrimaries.filter(function (tablePrimary) {
        return equalIgnoreCase(tablePrimary.alias, identifier);
      });
      if (tableRef.length > 0) {
        parser.suggestColumns({identifierChain: [{name: identifier}]});
      } else {
        parser.suggestTables({identifierChain: [{name: identifier}]});
      }
    };

    parser.suggestFunctions = function (details) {
      parser.yy.result.suggestFunctions = details || {};
    };

    parser.suggestAggregateFunctions = function () {
      var primaries = [];
      var aliases = {};
      parser.yy.latestTablePrimaries.forEach(function (primary) {
        if (typeof primary.alias !== 'undefined') {
          aliases[primary.alias] = true;
        }
        // Drop if the first one refers to a table alias (...FROM tbl t, t.map tm ...)
        if (typeof primary.identifierChain !== 'undefined' && !aliases[primary.identifierChain[0].name] && typeof primary.owner === 'undefined') {
          primaries.push(primary);
        }
      });
      parser.yy.result.suggestAggregateFunctions = {tablePrimaries: primaries};
    };

    parser.suggestAnalyticFunctions = function () {
      parser.yy.result.suggestAnalyticFunctions = true;
    };

    parser.suggestSetOptions = function () {
      parser.yy.result.suggestSetOptions = true;
    };

    parser.suggestIdentifiers = function (identifiers) {
      parser.yy.result.suggestIdentifiers = identifiers;
    };

    parser.suggestColumns = function (details) {
      if (typeof details === 'undefined') {
        details = {identifierChain: []};
      } else if (typeof details.identifierChain === 'undefined') {
        details.identifierChain = [];
      }
      parser.yy.result.suggestColumns = details;
    };

    parser.suggestGroupBys = function (details) {
      parser.yy.result.suggestGroupBys = details || {};
    };

    parser.suggestOrderBys = function (details) {
      parser.yy.result.suggestOrderBys = details || {};
    };

    parser.suggestFilters = function (details) {
      parser.yy.result.suggestFilters = details || {};
    };

    parser.suggestKeyValues = function (details) {
      parser.yy.result.suggestKeyValues = details || {};
    };

    parser.suggestTables = function (details) {
      parser.yy.result.suggestTables = details || {};
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

    parser.addFunctionLocation = function (location, functionName) {
      // Remove trailing '(' from location
      var adjustedLocation = {
        first_line: location.first_line,
        last_line: location.last_line,
        first_column: location.first_column,
        last_column: location.last_column - 1
      };
      parser.yy.locations.push({
        type: 'function',
        location: adjustLocationForCursor(adjustedLocation),
        function: functionName.toLowerCase()
      });
    };

    parser.addStatementLocation = function (location) {
      // Don't report lonely cursor as a statement
      if (location.first_line === location.last_line && Math.abs(location.last_column - location.first_column) === 1) {
        return;
      }
      var adjustedLocation;
      if (parser.yy.cursorFound && parser.yy.cursorFound.last_line === location.last_line &&
        parser.yy.cursorFound.first_column >= location.first_column && parser.yy.cursorFound.last_column <= location.last_column) {
        var additionalSpace = parser.yy.partialLengths.left + parser.yy.partialLengths.right;
        adjustedLocation = {
          first_line: location.first_line,
          last_line: location.last_line,
          first_column: location.first_column + 1,
          last_column: location.last_column + additionalSpace - (parser.yy.partialCursor ? 0 : 2)
        }
      } else {
        adjustedLocation = {
          first_line: location.first_line,
          last_line: location.last_line,
          first_column: location.first_column + 1,
          last_column: location.last_column + 1
        }
      }

      parser.yy.locations.push({
        type: 'statement',
        location: adjustedLocation
      });
    };

    parser.firstDefined = function () {
      for (var i = 0; i + 1 < arguments.length; i += 2) {
        if (arguments[i]) {
          return arguments[i + 1];
        }
      }
    };

    parser.addClauseLocation = function (type, precedingLocation, locationIfPresent, isCursor) {
      var location;
      if (isCursor) {
        if (parser.yy.partialLengths.left === 0 && parser.yy.partialLengths.right === 0) {
          location = {
            type: type,
            missing: true,
            location: adjustLocationForCursor({
              first_line: precedingLocation.last_line,
              first_column: precedingLocation.last_column,
              last_line: precedingLocation.last_line,
              last_column: precedingLocation.last_column
            })
          }
        } else {
          location = {
            type: type,
            missing: false,
            location: {
              first_line: locationIfPresent.last_line,
              first_column: locationIfPresent.last_column - 1,
              last_line: locationIfPresent.last_line,
              last_column: locationIfPresent.last_column - 1 + parser.yy.partialLengths.right + parser.yy.partialLengths.left
            }
          }
        }
      } else {
        location = {
          type: type,
          missing: !locationIfPresent,
          location: adjustLocationForCursor(locationIfPresent || {
            first_line: precedingLocation.last_line,
            first_column: precedingLocation.last_column,
            last_line: precedingLocation.last_line,
            last_column: precedingLocation.last_column
          })
        };
      }
      if (parser.isInSubquery()) {
        location.subquery = true;
      }
      parser.yy.locations.push(location)
    };

    parser.addStatementTypeLocation = function (identifier, location, additionalText) {
      if (!parser.isImpala()) {
        return;
      }
      var loc = {
        type: 'statementType',
        location: adjustLocationForCursor(location),
        identifier: identifier
      };
      if (typeof additionalText !== 'undefined') {
        switch (identifier) {
          case 'ALTER':
            if (/ALTER\s+VIEW/i.test(additionalText)) {
              loc.identifier = 'ALTER VIEW';
            } else {
              loc.identifier = 'ALTER TABLE';
            }
            break;
          case 'COMPUTE':
            loc.identifier = 'COMPUTE STATS';
            break;
          case 'CREATE':
            if (/CREATE\s+VIEW/i.test(additionalText)) {
              loc.identifier = 'CREATE VIEW';
            } else if (/CREATE\s+TABLE/i.test(additionalText)) {
              loc.identifier = 'CREATE TABLE';
            } else if (/CREATE\s+DATABASE/i.test(additionalText)) {
              loc.identifier = 'CREATE DATABASE';
            } else if (/CREATE\s+ROLE/i.test(additionalText)) {
              loc.identifier = 'CREATE ROLE';
            } else if (/CREATE\s+FUNCTION/i.test(additionalText)) {
              loc.identifier = 'CREATE FUNCTION';
            } else {
              loc.identifier = 'CREATE TABLE';
            }
            break;
          case 'DROP':
            if (/DROP\s+VIEW/i.test(additionalText)) {
              loc.identifier = 'DROP VIEW';
            } else if (/DROP\s+TABLE/i.test(additionalText)) {
              loc.identifier = 'DROP TABLE';
            } else if (/DROP\s+DATABASE/i.test(additionalText)) {
              loc.identifier = 'DROP DATABASE';
            } else if (/DROP\s+ROLE/i.test(additionalText)) {
              loc.identifier = 'DROP ROLE';
            } else if (/DROP\s+STATS/i.test(additionalText)) {
              loc.identifier = 'DROP STATS';
            } else if (/DROP\s+FUNCTION/i.test(additionalText)) {
              loc.identifier = 'DROP FUNCTION';
            } else {
              loc.identifier = 'DROP TABLE';
            }
            break;
          case 'INVALIDATE':
            loc.identifier = 'INVALIDATE METADATA';
            break;
          case 'LOAD':
            loc.identifier = 'LOAD DATA';
            break;
          case 'TRUNCATE':
            loc.identifier = 'TRUNCATE TABLE';
            break;
          default:
        }
      }
      parser.yy.locations.push(loc);
    };

    parser.addFileLocation = function (location, path) {
      parser.yy.locations.push({
        type: 'file',
        location: adjustLocationForCursor(location),
        path: path
      });
    };

    parser.addDatabaseLocation = function (location, identifierChain) {
      parser.yy.locations.push({
        type: 'database',
        location: adjustLocationForCursor(location),
        identifierChain: identifierChain
      });
    };

    parser.addTableLocation = function (location, identifierChain) {
      parser.yy.locations.push({
        type: 'table',
        location: adjustLocationForCursor(location),
        identifierChain: identifierChain
      });
    };

    parser.addColumnAliasLocation = function (location, alias, parentLocation) {
      var aliasLocation = {
        type: 'alias',
        source: 'column',
        alias: alias,
        location: adjustLocationForCursor(location),
        parentLocation: adjustLocationForCursor(parentLocation)
      };
      if (parser.yy.locations.length && parser.yy.locations[parser.yy.locations.length - 1].type === 'column') {
        var closestColumn = parser.yy.locations[parser.yy.locations.length - 1];
        if (closestColumn.location.first_line === aliasLocation.parentLocation.first_line &&
          closestColumn.location.last_line === aliasLocation.parentLocation.last_line &&
          closestColumn.location.first_column === aliasLocation.parentLocation.first_column &&
          closestColumn.location.last_column === aliasLocation.parentLocation.last_column) {
          parser.yy.locations[parser.yy.locations.length - 1].alias = alias;
        }
      }
      parser.yy.locations.push(aliasLocation);
    };

    parser.addTableAliasLocation = function (location, alias, identifierChain) {
      parser.yy.locations.push({
        type: 'alias',
        source: 'table',
        alias: alias,
        location: adjustLocationForCursor(location),
        identifierChain: identifierChain
      });
    };

    parser.addSubqueryAliasLocation = function (location, alias) {
      parser.yy.locations.push({
        type: 'alias',
        source: 'subquery',
        alias: alias,
        location: adjustLocationForCursor(location)
      });
    };

    parser.addAsteriskLocation = function (location, identifierChain) {
      parser.yy.locations.push({
        type: 'asterisk',
        location: adjustLocationForCursor(location),
        identifierChain: identifierChain
      });
    };

    parser.addVariableLocation = function (location, value) {
      if (/\$\{[^}]*\}/.test(value)) {
        parser.yy.locations.push({
          type: 'variable',
          location: adjustLocationForCursor(location),
          value: value
        });
      }
    };

    parser.addColumnLocation = function (location, identifierChain) {
      var isVariable = identifierChain.length && /\$\{[^}]*\}/.test(identifierChain[identifierChain.length - 1].name);
      if (isVariable) {
        parser.yy.locations.push({
          type: 'variable',
          location: adjustLocationForCursor(location),
          value: identifierChain[identifierChain.length - 1].name
        });
      } else {
        parser.yy.locations.push({
          type: 'column',
          location: adjustLocationForCursor(location),
          identifierChain: identifierChain,
          qualified: identifierChain.length > 1
        });
      }
    };

    parser.addCteAliasLocation = function (location, alias) {
      parser.yy.locations.push({
        type: 'alias',
        source: 'cte',
        alias: alias,
        location: adjustLocationForCursor(location)
      });
    };

    parser.addUnknownLocation = function (location, identifierChain) {
      var isVariable = identifierChain.length && /\$\{[^}]*\}/.test(identifierChain[identifierChain.length - 1].name);
      var loc;
      if (isVariable) {
        loc = {
          type: 'variable',
          location: adjustLocationForCursor(location),
          value: identifierChain[identifierChain.length - 1].name
        };
      } else {
        loc = {
          type: 'unknown',
          location: adjustLocationForCursor(location),
          identifierChain: identifierChain,
          qualified: identifierChain.length > 1
        };
      }
      parser.yy.locations.push(loc);
      return loc;
    };

    parser.addColRefToVariableIfExists = function (left, right) {
      if (left && left.columnReference && left.columnReference.length && right && right.columnReference && right.columnReference.length && parser.yy.locations.length > 1) {
        var addColRefToVariableLocation = function (variableValue, colRef) {
          // See if colref is actually an alias
          if (colRef.length === 1 && colRef[0].name) {
            parser.yy.locations.some(function (location) {
              if (location.type === 'column' && location.alias === colRef[0].name) {
                colRef = location.identifierChain;
                return true;
              }
            });
          }

          for (var i = parser.yy.locations.length - 1; i > 0; i--) {
            var location = parser.yy.locations[i];
            if (location.type === 'variable' && location.value === variableValue) {
              location.colRef = { identifierChain: colRef };
              break;
            }
          }
        };

        if (/\$\{[^}]*\}/.test(left.columnReference[0].name)) {
          // left is variable
          addColRefToVariableLocation(left.columnReference[0].name, right.columnReference);
        } else if (/\$\{[^}]*\}/.test(right.columnReference[0].name)) {
          // right is variable
          addColRefToVariableLocation(right.columnReference[0].name, left.columnReference);
        }
      }
    };

    parser.suggestDatabases = function (details) {
      parser.yy.result.suggestDatabases = details || {};
    };

    parser.suggestHdfs = function (details) {
      parser.yy.result.suggestHdfs = details || {};
    };

    parser.suggestValues = function (details) {
      parser.yy.result.suggestValues = details || {};
    };

    parser.determineCase = function (text) {
      if (!parser.yy.caseDetermined) {
        parser.yy.lowerCase = text.toLowerCase() === text;
        parser.yy.caseDetermined = true;
      }
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

    var lexerModified = false;

    /**
     * Main parser function
     */
    parser.parseSql = function (beforeCursor, afterCursor, dialect, debug) {
      // Jison counts CRLF as two lines in the locations
      beforeCursor = beforeCursor.replace(/\r\n|\n\r/gm, '\n');
      afterCursor = afterCursor.replace(/\r\n|\n\r/gm, '\n');
      parser.yy.result = {locations: []};
      parser.yy.lowerCase = false;
      parser.yy.locations = [];
      parser.yy.allLocations = [];
      parser.yy.subQueries = [];
      parser.yy.errors = [];
      parser.yy.selectListAliases = [];

      parser.yy.locationsStack = [];
      parser.yy.primariesStack = [];
      parser.yy.lateralViewsStack = [];
      parser.yy.subQueriesStack = [];
      parser.yy.resultStack = [];
      parser.yy.selectListAliasesStack = [];

      delete parser.yy.caseDetermined;
      delete parser.yy.cursorFound;
      delete parser.yy.partialCursor;

      parser.prepareNewStatement();

      var REASONABLE_SURROUNDING_LENGTH = 150000; // About 3000 lines before and after

      if (beforeCursor.length > REASONABLE_SURROUNDING_LENGTH) {
        if ((beforeCursor.length - beforeCursor.lastIndexOf(';')) > REASONABLE_SURROUNDING_LENGTH) {
          // Bail out if the last complete statement is more than 150000 chars before
          return {};
        }
        // Cut it at the first statement found within 150000 chars before
        var lastReasonableChunk = beforeCursor.substring(beforeCursor.length - REASONABLE_SURROUNDING_LENGTH);
        beforeCursor = lastReasonableChunk.substring(lastReasonableChunk.indexOf(';') + 1);
      }

      if (afterCursor.length > REASONABLE_SURROUNDING_LENGTH) {
        if ((afterCursor.length - afterCursor.indexOf(';')) > REASONABLE_SURROUNDING_LENGTH) {
          // No need to bail out for what's comes after, we can still get keyword completion
          afterCursor = '';
        } else {
          // Cut it at the last statement found within 150000 chars after
          var firstReasonableChunk = afterCursor.substring(0, REASONABLE_SURROUNDING_LENGTH);
          afterCursor = firstReasonableChunk.substring(0, firstReasonableChunk.lastIndexOf(';'));
        }
      }

      parser.yy.partialLengths = parser.identifyPartials(beforeCursor, afterCursor);

      if (parser.yy.partialLengths.left > 0) {
        beforeCursor = beforeCursor.substring(0, beforeCursor.length - parser.yy.partialLengths.left);
      }

      if (parser.yy.partialLengths.right > 0) {
        afterCursor = afterCursor.substring(parser.yy.partialLengths.right);
      }

      parser.yy.activeDialect = (dialect !== 'hive' && dialect !== 'impala') ? undefined : dialect;

      // Hack to set the inital state of the lexer without first having to hit a token
      // has to be done as the first token found can be dependant on dialect
      if (!lexerModified) {
        var originalSetInput = parser.lexer.setInput;
        parser.lexer.setInput = function (input, yy) {
          var lexer = originalSetInput.bind(parser.lexer)(input, yy);
          if (typeof parser.yy.activeDialect !== 'undefined') {
            lexer.begin(parser.yy.activeDialect);
          }
          return lexer;
        };
        lexerModified = true;
      }

      var result;
      try {
        // Add |CURSOR| or |PARTIAL_CURSOR| to represent the different cursor states in the lexer
        result = parser.parse(beforeCursor + (beforeCursor.length == 0 || /[\s\(]$$/.test(beforeCursor) ? ' \u2020 ' : '\u2021') + afterCursor);
      } catch (err) {
        // On any error try to at least return any existing result
        if (typeof parser.yy.result === 'undefined') {
          throw err;
        }
        if (debug) {
          console.log(err);
          console.error(err.stack);
        }
        result = parser.yy.result;
      }
      if (parser.yy.errors.length > 0) {
        parser.yy.result.errors = parser.yy.errors;
        if (debug) {
          console.log(parser.yy.errors);
        }
      }
      try {
        linkTablePrimaries();
        parser.commitLocations();
        // Clean up and prioritize
        prioritizeSuggestions();
      } catch (err) {
        if (debug) {
          console.log(err);
          console.error(err.stack);
        }
      }


      parser.yy.allLocations.sort(function (a, b) {
        if (a.location.first_line !== b.location.first_line) {
          return a.location.first_line - b.location.first_line;
        }
        if (a.location.first_column !== b.location.first_column) {
          return a.location.first_column - b.location.first_column;
        }
        if (a.location.last_column !== b.location.last_column) {
          return b.location.last_column - a.location.last_column;
        }
        return b.type.localeCompare(a.type);
      });
      parser.yy.result.locations = parser.yy.allLocations;

      parser.yy.result.locations.forEach(function (location) {
        delete location.linked;
      });
      if (typeof parser.yy.result.suggestColumns !== 'undefined') {
        delete parser.yy.result.suggestColumns.linked;
      }

      SIMPLE_TABLE_REF_SUGGESTIONS.forEach(function (suggestionType) {
        if (typeof parser.yy.result[suggestionType] !== 'undefined') {
          delete parser.yy.result[suggestionType].linked;
        }
      });

      if (typeof parser.yy.result.colRef !== 'undefined') {
        delete parser.yy.result.colRef.linked;
      }
      if (typeof parser.yy.result.suggestKeyValues !== 'undefined') {
        delete parser.yy.result.suggestKeyValues.linked;
      }

      if (typeof result.error !== 'undefined' && typeof result.error.expected !== 'undefined') {
        // Remove any expected tokens from other dialects, jison doesn't remove tokens from other lexer states.
        var actualExpected = {};
        result.error.expected.forEach(function (expected) {
          var match = expected.match(/\<([a-z]+)\>(.*)/);
          if (match !== null) {
            if (typeof parser.yy.activeDialect !== 'undefined' && parser.yy.activeDialect === match[1]) {
              actualExpected[("'" + match[2])] = true;
            }
          } else if (expected.indexOf('CURSOR') == -1) {
            actualExpected[expected] = true;
          }
        });
        result.error.expected = Object.keys(actualExpected);
      }

      if (typeof result.error !== 'undefined' && result.error.recoverable) {
        delete result.error;
      }

      // Adjust all the statement locations to include white space surrounding them
      var lastStatementLocation = null;
      result.locations.forEach(function (location) {
        if (location.type === 'statement') {
          if (lastStatementLocation === null) {
            location.location.first_line = 1;
            location.location.first_column = 1;
          } else {
            location.location.first_line = lastStatementLocation.location.last_line;
            location.location.first_column = lastStatementLocation.location.last_column + 1;
          }
          lastStatementLocation = location;
        }
      });

      return result;
    };
  };

  var SYNTAX_PARSER_NOOP_FUNCTIONS = ['prepareNewStatement', 'addCommonTableExpressions', 'pushQueryState', 'popQueryState', 'suggestSelectListAliases',
    'suggestValueExpressionKeywords', 'getSelectListKeywords', 'getValueExpressionKeywords', 'addColRefIfExists', 'selectListNoTableSuggest', 'suggestJoinConditions',
    'suggestJoins', 'valueExpressionSuggest', 'applyTypeToSuggestions', 'applyArgumentTypesToSuggestions', 'commitLocations', 'identifyPartials',
    'getSubQuery', 'addTablePrimary', 'suggestFileFormats', 'suggestDdlAndDmlKeywords', 'checkForSelectListKeywords', 'checkForKeywords',
    'suggestKeywords', 'suggestColRefKeywords', 'suggestTablesOrColumns', 'suggestFunctions', 'suggestAggregateFunctions', 'suggestAnalyticFunctions',
    'suggestColumns', 'suggestGroupBys', 'suggestIdentifiers', 'suggestOrderBys', 'suggestFilters', 'suggestKeyValues', 'suggestTables', 'addFunctionLocation',
    'addStatementLocation', 'firstDefined', 'addClauseLocation', 'addStatementTypeLocation', 'addFileLocation', 'addDatabaseLocation', 'addColumnAliasLocation',
    'addTableAliasLocation', 'addSubqueryAliasLocation', 'addTableLocation', 'addAsteriskLocation', 'addVariableLocation', 'addColumnLocation', 'addCteAliasLocation',
    'addUnknownLocation', 'addColRefToVariableIfExists', 'suggestDatabases', 'suggestHdfs', 'suggestValues'];

  var SYNTAX_PARSER_NOOP = function () {};

  var initSyntaxParser = function (parser) {

    // Noop functions for compatibility with the autocomplete parser as the grammar is shared
    SYNTAX_PARSER_NOOP_FUNCTIONS.forEach(function (noopFn) {
      parser[noopFn] = SYNTAX_PARSER_NOOP
    });

    parser.yy.locations = [{}];

    parser.determineCase = function (text) {
      if (!parser.yy.caseDetermined) {
        parser.yy.lowerCase = text.toLowerCase() === text;
        parser.yy.caseDetermined = true;
      }
    };

    parser.getKeywordsForOptionalsLR = function () {
      return [];
    };

    parser.mergeSuggestKeywords = function () {
      return {};
    };

    parser.getTypeKeywords = function () {
      return [];
    };

    parser.getColumnDataTypeKeywords = function () {
      return [];
    };

    parser.findCaseType = function () {
      return {types: ['T']};
    };

    parser.findReturnTypes = function (functionName) {
      return ['T'];
    };

    parser.isHive = function () {
      return parser.yy.activeDialect === 'hive';
    };

    parser.isImpala = function () {
      return parser.yy.activeDialect === 'impala';
    };

    parser.expandImpalaIdentifierChain = function () {
      return [];
    };

    parser.expandIdentifierChain = function () {
      return [];
    };

    parser.expandLateralViews = function () {
      return [];
    };

    parser.createWeightedKeywords = function () {
      return [];
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

    var lexerModified = false;

    parser.yy.parseError = function (str, hash) {
      parser.yy.error = hash;
    };

    var IGNORED_EXPECTED = {
      ';': true,
      '.': true,
      'EOF': true,
      'UNSIGNED_INTEGER': true,
      'UNSIGNED_INTEGER_E': true,
      'REGULAR_IDENTIFIER': true, // TODO: Indicate that an identifier was expected
      'CURSOR': true,
      'PARTIAL_CURSOR': true,
      'HDFS_START_QUOTE': true,
      'HDFS_PATH': true,
      'HDFS_END_QUOTE' : true,
      'COMPARISON_OPERATOR': true, // TODO: Expand in results when found
      'ARITHMETIC_OPERATOR' : true, // TODO: Expand in results when found
      'VARIABLE_REFERENCE': true,
      'BACKTICK': true,
      'VALUE': true,
      'PARTIAL_VALUE': true,
      'SINGLE_QUOTE': true,
      'DOUBLE_QUOTE': true
    };

    var CLEAN_EXPECTED = {
      'BETWEEN_AND': 'AND',
      'OVERWRITE_DIRECTORY' : 'OVERWRITE',
      'STORED_AS_DIRECTORIES' : 'STORED',
      'LIKE_PARQUET' : 'LIKE',
      'PARTITION_VALUE' : 'PARTITION'
    };

    parser.parseSyntax = function (beforeCursor, afterCursor, dialect, debug) {
      parser.yy.caseDetermined = false;
      parser.yy.error = undefined;

      parser.yy.latestTablePrimaries = [];
      parser.yy.subQueries = [];
      parser.yy.selectListAliases = [];
      parser.yy.latestTablePrimaries = [];

      parser.yy.activeDialect = (dialect !== 'hive' && dialect !== 'impala') ? undefined : dialect;

      // Hack to set the inital state of the lexer without first having to hit a token
      // has to be done as the first token found can be dependant on dialect
      if (!lexerModified) {
        var originalSetInput = parser.lexer.setInput;
        parser.lexer.setInput = function (input, yy) {
          var lexer = originalSetInput.bind(parser.lexer)(input, yy);
          if (typeof parser.yy.activeDialect !== 'undefined') {
            lexer.begin(parser.yy.activeDialect);
          }
          return lexer;
        };
        lexerModified = true;
      }

      // TODO: Find a way around throwing an exception when the parser finds a syntax error
      try {
        parser.yy.error = false;
        parser.parse(beforeCursor + afterCursor);
      } catch (err) {
        if (debug) {
          console.log(err);
          console.error(err.stack);
          console.log(parser.yy.error);
        }
      }

      if (parser.yy.error && (parser.yy.error.loc.last_column < beforeCursor.length || !beforeCursor.endsWith(parser.yy.error.text))) {
        var weightedExpected = [];

        var addedExpected = {};

        var isLowerCase = parser.yy.caseDetermined && parser.yy.lowerCase || parser.yy.error.text.toLowerCase() === parser.yy.error.text;

        if (parser.yy.error.expected.length == 2 && parser.yy.error.expected.indexOf('\';\'') !== -1 && parser.yy.error.expected.indexOf('\'EOF\'') !== -1) {
          parser.yy.error.expected = [];
          parser.yy.error.expectedStatementEnd = true;
          return parser.yy.error;
        }
        for (var i = 0; i < parser.yy.error.expected.length; i++) {
          var expected = parser.yy.error.expected[i];
          // Strip away the surrounding ' chars
          expected = expected.substring(1, expected.length - 1);
          // TODO: Only suggest alphanumeric?
          if (!IGNORED_EXPECTED[expected] && /[a-z_]+/i.test(expected)) {
            if (dialect && expected.indexOf('<' + dialect + '>') == 0) {
              expected = expected.substring(dialect.length + 2);
            } else if (/^<[a-z]+>/.test(expected)) {
              continue;
            }
            expected = CLEAN_EXPECTED[expected] || expected;
            if (expected === parser.yy.error.text.toUpperCase()) {
              // Can happen when the lexer entry for a rule contains multiple words like 'stored' in 'stored as parquet'
              return false;
            }
            var text = isLowerCase ? expected.toLowerCase() : expected;
            if (text && !addedExpected[text]) {
              addedExpected[text] = true;
              weightedExpected.push({
                text: text,
                distance: stringDistance(parser.yy.error.text, text, true)
              });
            }
          }
        }
        if (weightedExpected.length === 0) {
          parser.yy.error.expected = [];
          parser.yy.error.incompleteStatement = true;
          return parser.yy.error;
        }
        weightedExpected.sort(function (a, b) {
          if (a.distance === b.distance) {
            return a.text.localeCompare(b.text);
          }
          return a.distance - b.distance
        });
        parser.yy.error.expected = weightedExpected;
        parser.yy.error.incompleteStatement = true;
        return parser.yy.error;
      } else if (parser.yy.error) {
        parser.yy.error.expected = [];
        parser.yy.error.incompleteStatement = true;
        return parser.yy.error;
      }
      return false;
    }
  };

  var initGlobalSearchParser = function (parser) {

    parser.identifyPartials = function (beforeCursor, afterCursor) {
      var beforeMatch = beforeCursor.match(/[0-9a-zA-Z_]*$/);
      var afterMatch = afterCursor.match(/^[0-9a-zA-Z_]*(?:\((?:[^)]*\))?)?/);
      return {left: beforeMatch ? beforeMatch[0].length : 0, right: afterMatch ? afterMatch[0].length : 0};
    };

    parser.mergeFacets = function (a, b) {
      if (!a.facets) {
        a.facets = {};
      }
      if (!b.facets) {
        return;
      }
      Object.keys(b.facets).forEach(function (key) {
        if (a.facets[key]) {
          Object.keys(b.facets[key]).forEach(function (val) {
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
        var cursorIndex = yytext.indexOf('\u2020');
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

    parser.parseGlobalSearch = function (beforeCursor, afterCursor, debug) {
      delete parser.yy.cursorFound;

      var result;
      try {
        result = parser.parse(beforeCursor + '\u2020' + afterCursor);
      } catch (err) {
        if (debug) {
          console.log(err);
          console.error(err.stack);
          console.log(parser.yy.error);
        }
        return {
          facets: {},
          text: []
        }
      }
      return result;
    };
  };

  return {
    initSqlParser: initSqlParser,
    initSyntaxParser: initSyntaxParser,
    stringDistance: stringDistance,
    initGlobalSearchParser: initGlobalSearchParser
  };
})();
