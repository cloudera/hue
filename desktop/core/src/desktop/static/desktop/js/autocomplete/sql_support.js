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

var prepareNewStatement = function () {
  linkTablePrimaries();
  commitLocations();

  delete parser.yy.lateralViews;
  delete parser.yy.latestTablePrimaries;
  delete parser.yy.latestCommonTableExpressions;
  delete parser.yy.correlatedSubQuery;
  parser.yy.subQueries = [];
  parser.yy.selectListAliases = [];

  parser.parseError = function (message, error) {
    parser.yy.errors.push(error);
    return message;
  };
};

var addCommonTableExpressions = function (identifiers) {
  parser.yy.latestCommonTableExpressions = identifiers;
};

var pushQueryState = function () {
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

var popQueryState = function (subQuery) {
  linkTablePrimaries();
  commitLocations();

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

var suggestSelectListAliases = function () {
  if (parser.yy.selectListAliases && parser.yy.selectListAliases.length > 0 && parser.yy.result.suggestColumns
      && (typeof parser.yy.result.suggestColumns.identifierChain === 'undefined' || parser.yy.result.suggestColumns.identifierChain.length === 0)) {
    parser.yy.result.suggestColumnAliases = parser.yy.selectListAliases;
  }
};

var isHive = function () {
  return parser.yy.activeDialect === 'hive';
};

var isImpala = function () {
  return parser.yy.activeDialect === 'impala';
};

var mergeSuggestKeywords = function () {
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

var suggestValueExpressionKeywords = function (valueExpression, extras) {
  var expressionKeywords = getValueExpressionKeywords(valueExpression, extras);
  suggestKeywords(expressionKeywords.suggestKeywords);
  if (expressionKeywords.suggestColRefKeywords) {
    suggestColRefKeywords(expressionKeywords.suggestColRefKeywords);
  }
  if (valueExpression.lastType) {
    addColRefIfExists(valueExpression.lastType);
  } else {
    addColRefIfExists(valueExpression);
  }
};

var getValueExpressionKeywords = function (valueExpression, extras) {
  var types = valueExpression.lastType ? valueExpression.lastType.types : valueExpression.types;
  // We could have valueExpression.columnReference to suggest based on column type
  var keywords = ['<', '<=', '<>', '=', '>', '>=', 'BETWEEN', 'IN', 'IS NOT NULL', 'IS NULL', 'NOT BETWEEN', 'NOT IN'];
  if (isHive()) {
    keywords.push('<=>');
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
        NUMBER: ['+', '-', '*', '/', '%'],
        STRING: ['LIKE', 'NOT LIKE', 'REGEX', 'RLIKE']
      }
    }
  }
  if (parser.yy.sqlFunctions.matchesType(parser.yy.activeDialect, ['BOOLEAN'], types)) {
    keywords = keywords.concat(['AND', 'OR']);
  }
  if (parser.yy.sqlFunctions.matchesType(parser.yy.activeDialect, ['NUMBER'], types)) {
    keywords = keywords.concat(['+', '-', '*', '/', '%']);
  }
  if (parser.yy.sqlFunctions.matchesType(parser.yy.activeDialect, ['STRING'], types)) {
    keywords = keywords.concat(['LIKE', 'NOT LIKE', 'REGEX', 'RLIKE']);
  }
  return {suggestKeywords: keywords};
};

var getTypeKeywords = function () {
  if (isHive()) {
    return ['BIGINT', 'BINARY', 'BOOLEAN', 'CHAR', 'DATE', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR'];
  }
  if (isImpala()) {
    return ['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'REAL', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR'];
  }
  return ['BIGINT', 'BOOLEAN', 'CHAR', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TIMESTAMP', 'STRING', 'TINYINT', 'VARCHAR'];
};

var getColumnDataTypeKeywords = function () {
  if (isHive()) {
    return getTypeKeywords().concat(['ARRAY<>', 'MAP<>', 'STRUCT<>', 'UNIONTYPE<>']);
  }
  return getTypeKeywords();
};

var addColRefIfExists = function (valueExpression) {
  if (valueExpression.columnReference) {
    parser.yy.result.colRef = {identifierChain: valueExpression.columnReference};
  }
};

var selectListNoTableSuggest = function (selectListEdit, hasDistinctOrAll) {
  if (selectListEdit.cursorAtStart) {
    var keywords = [];
    if (hasDistinctOrAll) {
      keywords = [{ value: '*', weight: 1000 }];
    } else {
      keywords = [{ value: '*', weight: 1000 }, 'ALL', 'DISTINCT'];
    }
    if (isImpala()) {
      keywords.push('STRAIGHT_JOIN');
    }
    suggestKeywords(keywords);
  } else {
    checkForKeywords(selectListEdit);
  }
  if (selectListEdit.suggestFunctions) {
    suggestFunctions();
  }
  if (selectListEdit.suggestColumns) {
    suggestColumns();
  }
  if (selectListEdit.suggestAggregateFunctions && (!hasDistinctOrAll || hasDistinctOrAll === 'ALL')) {
    suggestAggregateFunctions();
    suggestAnalyticFunctions();
  }
};

var valueExpressionSuggest = function (oppositeValueExpression, operator) {
  if (oppositeValueExpression && oppositeValueExpression.columnReference) {
    suggestValues();
    parser.yy.result.colRef = {identifierChain: oppositeValueExpression.columnReference};
  }
  suggestColumns();
  suggestFunctions();
  var keywords = ['CASE'];
  if (isHive() || typeof oppositeValueExpression === 'undefined' || typeof operator === 'undefined') {
    keywords = keywords.concat(['EXISTS', 'NOT']);
  }
  if (oppositeValueExpression && oppositeValueExpression.types[0] === 'NUMBER') {
    applyTypeToSuggestions(['NUMBER']);
  } else if (isImpala() && (typeof operator === 'undefined' || operator === '-' || operator === '+')) {
    keywords.push('INTERVAL');
  }
  suggestKeywords(keywords);
};

var applyTypeToSuggestions = function (types) {
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

var findCaseType = function (whenThenList) {
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

findReturnTypes = function (functionName) {
  return parser.yy.sqlFunctions.getReturnTypes(parser.yy.activeDialect, functionName.toLowerCase());
};

var applyArgumentTypesToSuggestions = function (functionName, position) {
  var foundArguments = parser.yy.sqlFunctions.getArgumentTypes(parser.yy.activeDialect, functionName.toLowerCase(), position);
  if (foundArguments.length == 0 && parser.yy.result.suggestColumns) {
    delete parser.yy.result.suggestColumns;
    delete parser.yy.result.suggestKeyValues;
    delete parser.yy.result.suggestValues;
    delete parser.yy.result.suggestFunctions;
    delete parser.yy.result.suggestIdentifiers;
    delete parser.yy.result.suggestKeywords;
  } else {
    applyTypeToSuggestions(foundArguments);
  }
};

var commitLocations = function () {
  var i = parser.yy.locations.length;
  while (i--) {
    var location = parser.yy.locations[i];

    // Impala can have references to previous tables after FROM, i.e. FROM testTable t, t.testArray
    // In this testArray would be marked a type table so we need to switch it to column.
    if (location.type === 'table' && typeof location.identifierChain !== 'undefined' && location.identifierChain.length > 1 && parser.yy.latestTablePrimaries) {
      var found = parser.yy.latestTablePrimaries.filter(function (primary) {
        return primary.alias === location.identifierChain[0].name;
      });
      if (found.length > 0) {
        location.type = 'column';
      }
    }

    if (location.type === 'column') {
      if (isHive() && !location.linked) {
        location.identifierChain = parser.expandLateralViews(parser.yy.lateralViews, location.identifierChain);
      }
      expandIdentifierChain(location, true);
    }

    if (location.type === 'table' && (typeof location.identifierChain === 'undefined' || location.identifierChain.length === 0)) {
      parser.yy.locations.splice(i, 1);
    }
    if (location.type === 'column' && (typeof location.identifierChain === 'undefined' || location.identifierChain.length < 2)) {
      parser.yy.locations.splice(i, 1);
    }
  }
  if (parser.yy.locations.length > 0) {
    parser.yy.allLocations = parser.yy.allLocations.concat(parser.yy.locations);
    parser.yy.locations = [];
  }
};

var prioritizeSuggestions = function () {
  parser.yy.result.lowerCase = parser.yy.lowerCase || false;
  if (typeof parser.yy.result.colRef !== 'undefined') {
    if (!parser.yy.result.colRef.linked || typeof parser.yy.result.colRef.identifierChain === 'undefined' || parser.yy.result.colRef.identifierChain.length === 0) {
      delete parser.yy.result.colRef;
      if (typeof parser.yy.result.suggestColRefKeywords !== 'undefined') {
        Object.keys(parser.yy.result.suggestColRefKeywords).forEach(function (type) {
          parser.yy.result.suggestKeywords = parser.yy.result.suggestKeywords.concat(createWeightedKeywords(parser.yy.result.suggestColRefKeywords[type], -1));
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
      if (parser.yy.result.suggestColumns.linked && isImpala() && typeof suggestColumns.identifierChain !== 'undefined' && suggestColumns.identifierChain.length > 0) {
        if (suggestColumns.identifierChain.length === 1) {
          parser.yy.result.suggestTables = suggestColumns;
          delete parser.yy.result.suggestColumns
        } else {
          suggestColumns.tables = [{ identifierChain: suggestColumns.identifierChain }];
          delete suggestColumns.identifierChain;
        }
      } else {
        delete parser.yy.result.suggestColumns;
        delete parser.yy.result.subQueries;
      }
    } else {
      delete parser.yy.result.suggestTables;
      delete parser.yy.result.suggestDatabases;
      if (typeof suggestColumns.identifierChain !== 'undefined') {
        delete suggestColumns.identifierChain;
      }
    }
  } else {
    delete parser.yy.result.subQueries;
  }

  if (typeof parser.yy.result.suggestTables !== 'undefined' && typeof parser.yy.latestCommonTableExpressions !== 'undefined') {
    var ctes = [];
    parser.yy.latestCommonTableExpressions.forEach(function (identifier) {
      var cte = { name: identifier };
      if (parser.yy.result.suggestTables.prependFrom) {
        cte.prependFrom = true
      }
      if (parser.yy.result.suggestTables.prependQuestionMark) {
        cte.prependQuestionMark = true;
      }
      ctes.push(cte);
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
      return tablePrimary.alias === identifier;
    });

    if (foundPrimary.length === 1 && foundPrimary[0].identifierChain) {
      var parentPrimary = tablePrimaries.filter(function (tablePrimary) {
        return tablePrimary.alias === foundPrimary[0].identifierChain[0].name;
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
  var afterMatch = afterCursor.match(/^[0-9a-zA-Z_]*/);
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
      if (firstIdentifier.name === lateralView.tableAlias && identifierChain.length > 1) {
        identifierChain.shift();
        firstIdentifier = identifierChain[0];
        if (columnSuggestion) {
          delete parser.yy.result.suggestKeywords;
        }
      } else if (firstIdentifier.name === lateralView.tableAlias && identifierChain.length === 1 && typeof parser.yy.result.suggestColumns !== 'undefined') {
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
        if (lateralView.columnAliases.length === 2 && lateralView.udtf.function.toLowerCase() === 'explode' && firstIdentifier.name === lateralView.columnAliases[0]) {
          identifierChain[0] = {name: 'key'};
        } else if (lateralView.columnAliases.length === 2 && lateralView.udtf.function.toLowerCase() === 'explode' && firstIdentifier.name === lateralView.columnAliases[1]) {
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

var expandIdentifierChain = function (wrapper, anyOwner) {
  if (typeof wrapper.identifierChain === 'undefined' || typeof parser.yy.latestTablePrimaries === 'undefined') {
    return;
  }

  var identifierChain = wrapper.identifierChain.concat();
  var tablePrimaries = parser.yy.latestTablePrimaries;

  if (tablePrimaries.length === 0) {
    delete wrapper.identifierChain;
    return;
  }

  if (identifierChain.length > 0 && identifierChain[identifierChain.length - 1].asterisk) {
    var tables = [];
    tablePrimaries.forEach(function (tablePrimary) {
      if (tablePrimary.subQueryAlias) {
        tables.push({ identifierChain: [{ subQuery: tablePrimary.subQueryAlias }]});
      } else {
        tables.push({ identifierChain: tablePrimary.identifierChain });
      }
    });
    // Possible Joins
    if (tables.length > 0) {
      wrapper.tables = tables;
      delete wrapper.identifierChain;
      return;
    }
  }

  if (!anyOwner) {
    tablePrimaries = filterTablePrimariesForOwner(wrapper.owner);
  }
  // Impala can have references to maps or array, i.e. FROM table t, t.map m
  // We need to replace those in the identifierChain
  if (isImpala()) {
    identifierChain = parser.expandImpalaIdentifierChain(tablePrimaries, identifierChain);
    wrapper.identifierChain = identifierChain;
  }
  // Expand exploded views in the identifier chain
  if (isHive() && identifierChain.length > 0) {
    identifierChain = parser.expandLateralViews(parser.yy.lateralViews, identifierChain);
    wrapper.identifierChain = identifierChain;
  }

  // IdentifierChain contains a possibly started identifier or empty, example: a.b.c = ['a', 'b', 'c']
  // Reduce the tablePrimaries to the one that matches the first identifier if found
  if (identifierChain.length > 0) {
    var foundPrimary;
    var doubleMatch = false;
    for (var i = 0; i < tablePrimaries.length; i++) {
      if (tablePrimaries[i].subQueryAlias) {
        if (tablePrimaries[i].subQueryAlias === identifierChain[0].name) {
          foundPrimary = tablePrimaries[i];
        }
      } else if (tablePrimaries[i].alias === identifierChain[0].name) {
        foundPrimary = tablePrimaries[i];
        break;
      } else if (tablePrimaries[i].identifierChain.length > 1 && identifierChain.length > 1 &&
          tablePrimaries[i].identifierChain[0].name === identifierChain[0].name &&
          tablePrimaries[i].identifierChain[1].name === identifierChain[1].name) {
        foundPrimary = tablePrimaries[i];
        doubleMatch = true;
        break;
      } else if (!foundPrimary && tablePrimaries[i].identifierChain[0].name === identifierChain[0].name) {
        foundPrimary = tablePrimaries[i];
        // No break as first two can still match.
      } else if (!foundPrimary && tablePrimaries[i].identifierChain.length > 1
          && tablePrimaries[i].identifierChain[tablePrimaries[i].identifierChain.length - 1].name === identifierChain[0].name) {
        // This is for the case SELECT baa. FROM bla.baa, blo.boo;
        foundPrimary = tablePrimaries[i];
        break;
      }
    }
    if (foundPrimary) {
      identifierChain.shift();
      if (doubleMatch) {
        identifierChain.shift();
      }
    } else if (tablePrimaries.length === 1) {
      foundPrimary = tablePrimaries[0];
    }
    if (foundPrimary) {
      if (foundPrimary.subQueryAlias) {
        identifierChain.unshift({ subQuery: foundPrimary.subQueryAlias });
      } else {
        identifierChain = foundPrimary.identifierChain.concat(identifierChain);
      }
      if (wrapper.tables) {
        wrapper.tables.push({ identifierChain: identifierChain });
        delete wrapper.identifierChain;
      } else {
        wrapper.identifierChain = identifierChain;
      }
    }
  } else {
    tablePrimaries.forEach(function (tablePrimary) {
      var targetTable = { identifierChain: tablePrimary.identifierChain };
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

var filterTablePrimariesForOwner = function (owner) {
  var result = [];
  parser.yy.latestTablePrimaries.forEach(function (primary) {
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
      var table = { identifierChain: tablePrimary.identifierChain };
      if (tablePrimary.alias) {
        table.alias = tablePrimary.alias;
        identifiers.push({ name: table.alias + '.', type: 'alias' });
        if (isImpala()) {
          var testForImpalaAlias = [{ name: table.alias }];
          var result = parser.expandImpalaIdentifierChain(tablePrimaries, testForImpalaAlias);
          if (result.length > 1) {
            // Continue if it's a reference to a complex type
            return;
          }
        }
      } else {
        var lastIdentifier = tablePrimary.identifierChain[tablePrimary.identifierChain.length - 1];
        if (typeof lastIdentifier.name !== 'undefined') {
          identifiers.push({ name: lastIdentifier.name + '.', type: 'table' });
        } else if (typeof lastIdentifier.subQuery !== 'undefined') {
          identifiers.push({ name: lastIdentifier.subQuery + '.', type: 'sub-query' });
        }
      }
      tables.push(table);
    } else if (tablePrimary.subQueryAlias) {
      identifiers.push({ name: tablePrimary.subQueryAlias + '.', type: 'sub-query' });
      tables.push({ identifierChain: [{ subQuery: tablePrimary.subQueryAlias }] });
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
  if (parser.yy.result.suggestColumns.identifierChain && parser.yy.result.suggestColumns.identifierChain.length == 0) {
    delete parser.yy.result.suggestColumns.identifierChain;
  }
  parser.yy.result.suggestColumns.linked = true;
};

var linkTablePrimaries = function () {
  if (!parser.yy.cursorFound || typeof parser.yy.latestTablePrimaries === 'undefined') {
    return;
  }

  var tablePrimaries = parser.yy.latestTablePrimaries;
  if (typeof parser.yy.result.suggestColumns !== 'undefined' && !parser.yy.result.suggestColumns.linked) {
    tablePrimaries = filterTablePrimariesForOwner(parser.yy.result.suggestColumns.owner);
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
        if (tablePrimaries.length == 1 && (tablePrimaries[0].alias || tablePrimaries[0].subQueryAlias)) {
          convertTablePrimariesToSuggestions(tablePrimaries);
        }
        expandIdentifierChain(parser.yy.result.suggestColumns);
      }
    } else {
      // Expand exploded views in the identifier chain
      if (isHive() && !parser.yy.result.suggestColumns.linked) {
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
          expandIdentifierChain(parser.yy.result.suggestColumns);
        }
      } else {
        expandIdentifierChain(parser.yy.result.suggestColumns);
      }
    }
  }

  if (typeof parser.yy.result.colRef !== 'undefined' && !parser.yy.result.colRef.linked) {
    expandIdentifierChain(parser.yy.result.colRef);

    var primaries = filterTablePrimariesForOwner();
    if (primaries.length === 0 || (primaries.length > 1 && parser.yy.result.colRef.identifierChain.length === 1)) {
      parser.yy.result.colRef.identifierChain = [];
    }
  }
  if (typeof parser.yy.result.suggestKeyValues !== 'undefined' && !parser.yy.result.suggestKeyValues.linked) {
    expandIdentifierChain(parser.yy.result.suggestKeyValues);
  }
};

var getSubQuery = function (cols) {
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

var addTablePrimary = function (ref) {
  if (typeof parser.yy.latestTablePrimaries === 'undefined') {
    parser.yy.latestTablePrimaries = [];
  }
  parser.yy.latestTablePrimaries.push(ref);
};

var suggestNumbers = function (numbers) {
  parser.yy.result.suggestNumbers = numbers;
};

var suggestFileFormats = function () {
  if (isHive()) {
    suggestKeywords(['AVRO', 'INPUTFORMAT', 'ORC', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']);
  } else {
    suggestKeywords(['AVRO', 'PARQUET', 'RCFILE', 'SEQUENCEFILE', 'TEXTFILE']);
  }
};

var getKeywordsForOptionalsLR = function (optionals, keywords, override) {
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

var suggestDdlAndDmlKeywords = function (extraKeywords) {
  var keywords = ['ALTER', 'CREATE', 'DESCRIBE', 'DROP', 'INSERT', 'REVOKE', 'SELECT', 'SET', 'SHOW', 'TRUNCATE', 'UPDATE', 'USE', 'WITH'];

  if (extraKeywords) {
    keywords = keywords.concat(extraKeywords);
  }

  if (isHive()) {
    keywords = keywords.concat(['ANALYZE', 'DELETE', 'EXPORT', 'IMPORT', 'LOAD', 'MSCK', 'RELOAD FUNCTION', 'RESET']);
  }

  if (isImpala()) {
    keywords = keywords.concat(['COMPUTE', 'INVALIDATE', 'LOAD', 'REFRESH']);
  }

  suggestKeywords(keywords);
};

var checkForSelectListKeywords = function (selectList) {
  if (selectList.length === 0) {
    return;
  }
  var last = selectList[selectList.length - 1];
  if (!last || !last.valueExpression) {
    return;
  }
  var valueExpressionKeywords = getValueExpressionKeywords(last.valueExpression);
  var keywords = [];
  if (last.suggestKeywords) {
    keywords = keywords.concat(last.suggestKeywords);
  }
  if (valueExpressionKeywords.suggestKeywords) {
    keywords = keywords.concat(valueExpressionKeywords.suggestKeywords);
  }
  if (valueExpressionKeywords.suggestColRefKeywords) {
    suggestColRefKeywords(valueExpressionKeywords.suggestColRefKeywords);
    addColRefIfExists(last.valueExpression);
  }
  if (!last.alias) {
    keywords.push('AS');
  }
  if (keywords.length > 0) {
    suggestKeywords(keywords);
  }
};

var checkForKeywords = function (expression) {
  if (expression) {
    if (expression.suggestKeywords && expression.suggestKeywords.length > 0) {
      suggestKeywords(expression.suggestKeywords);
    }
    if (expression.suggestColRefKeywords) {
      suggestColRefKeywords(expression.suggestColRefKeywords);
      addColRefIfExists(expression);
    }
  }
};

var createWeightedKeywords = function (keywords, weight) {
  var result = [];
  keywords.forEach(function (keyword) {
    if (typeof keyword.weight !== 'undefined') {
      keyword.weight = weight + (keyword.weight / 10);
      result.push(keyword);
    } else {
      result.push({value: keyword, weight: weight });
    }
  });
  return result;
};

var suggestKeywords = function (keywords) {
  var weightedKeywords = [];
  if (keywords.length == 0) {
    return;
  }
  keywords.forEach(function (keyword) {
    if (typeof keyword.weight !== 'undefined') {
      weightedKeywords.push(keyword);
    } else {
      weightedKeywords.push({ value: keyword, weight: -1 })
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

var suggestColRefKeywords = function (colRefKeywords) {
  parser.yy.result.suggestColRefKeywords = colRefKeywords;
};

var suggestTablesOrColumns = function (identifier) {
  if (typeof parser.yy.latestTablePrimaries == 'undefined') {
    suggestTables({ identifierChain: [{ name: identifier }] });
    return;
  }
  var tableRef = parser.yy.latestTablePrimaries.filter(function (tablePrimary) {
    return tablePrimary.alias === identifier;
  });
  if (tableRef.length > 0) {
    suggestColumns({identifierChain: [{ name: identifier }]});
  } else {
    suggestTables({ identifierChain: [{ name: identifier }] });
  }
};

var suggestFunctions = function (details) {
  parser.yy.result.suggestFunctions = details || {};
};

var suggestAggregateFunctions = function () {
  parser.yy.result.suggestAggregateFunctions = true;
};

var suggestAnalyticFunctions = function () {
  parser.yy.result.suggestAnalyticFunctions = true;
};

var suggestColumns = function (details) {
  if (typeof details === 'undefined') {
    details = {identifierChain: []};
  } else if (typeof details.identifierChain === 'undefined') {
    details.identifierChain = [];
  }
  parser.yy.result.suggestColumns = details;
};

var suggestKeyValues = function (details) {
  parser.yy.result.suggestKeyValues = details || {};
};

var suggestTables = function (details) {
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

var addFunctionLocation = function (location, functionName) {
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

var addDatabaseLocation = function (location, database) {
  parser.yy.locations.push({type: 'database', location: adjustLocationForCursor(location), database: database});
};

var addTableLocation = function (location, identifierChain) {
  parser.yy.locations.push({
    type: 'table',
    location: adjustLocationForCursor(location),
    identifierChain: identifierChain
  });
};

var addColumnLocation = function (location, identifierChain) {
  parser.yy.locations.push({
    type: 'column',
    location: adjustLocationForCursor(location),
    identifierChain: identifierChain
  });
};

var suggestDatabases = function (details) {
  parser.yy.result.suggestDatabases = details || {};
};

var suggestHdfs = function (details) {
  parser.yy.result.suggestHdfs = details || {};
};

var suggestValues = function (details) {
  parser.yy.result.suggestValues = true;
};

var determineCase = function (text) {
  if (!parser.yy.caseDetermined) {
    parser.yy.lowerCase = text.toLowerCase() === text;
    parser.yy.caseDetermined = true;
  }
};

var lexerModified = false;

/**
 * Main parser function
 */
parser.parseSql = function (beforeCursor, afterCursor, dialect, sqlFunctions, debug) {
  parser.yy.sqlFunctions = sqlFunctions;
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

  prepareNewStatement();

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
  linkTablePrimaries();
  commitLocations();

  // Clean up and prioritize
  prioritizeSuggestions();

  parser.yy.allLocations.sort(function (a, b) {
    if (a.location.first_line !== b.location.first_line) {
      return a.location.first_line - b.location.first_line;
    }
    return a.location.first_column - b.location.first_column;
  });
  parser.yy.result.locations = parser.yy.allLocations;

  parser.yy.result.locations.forEach(function (location) {
    delete location.linked;
  });
  if (typeof parser.yy.result.suggestColumns !== 'undefined') {
    delete parser.yy.result.suggestColumns.linked;
  }
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

  return result;
};