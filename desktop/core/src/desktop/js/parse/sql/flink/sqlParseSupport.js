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

import { matchesType } from 'sql/reference/typeUtils';
import {
  initSharedAutocomplete,
  initSyntaxParser,
  identifierEquals,
  equalIgnoreCase,
  SIMPLE_TABLE_REF_SUGGESTIONS
} from 'parse/sql/sqlParseUtils';

const initSqlParser = function (parser) {
  initSharedAutocomplete(parser);

  parser.prepareNewStatement = function () {
    linkTablePrimaries();
    parser.commitLocations();

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
    return !!parser.yy.primariesStack.length;
  };

  parser.pushQueryState = function () {
    parser.yy.resultStack.push(parser.yy.result);
    parser.yy.locationsStack.push(parser.yy.locations);
    parser.yy.selectListAliasesStack.push(parser.yy.selectListAliases);
    parser.yy.primariesStack.push(parser.yy.latestTablePrimaries);
    parser.yy.subQueriesStack.push(parser.yy.subQueries);

    parser.yy.result = {};
    parser.yy.locations = [];
    parser.yy.selectListAliases = []; // Not allowed in correlated sub-queries

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
    const oldSubQueries = parser.yy.subQueries;
    parser.yy.subQueries = parser.yy.subQueriesStack.pop();
    if (subQuery) {
      if (oldSubQueries.length > 0) {
        subQuery.subQueries = oldSubQueries;
      }
      parser.yy.subQueries.push(subQuery);
    }

    parser.yy.latestTablePrimaries = parser.yy.primariesStack.pop();
    parser.yy.locations = parser.yy.locationsStack.pop();
    parser.yy.selectListAliases = parser.yy.selectListAliasesStack.pop();
  };

  parser.suggestSelectListAliases = function () {
    if (
      parser.yy.selectListAliases &&
      parser.yy.selectListAliases.length > 0 &&
      parser.yy.result.suggestColumns &&
      (typeof parser.yy.result.suggestColumns.identifierChain === 'undefined' ||
        parser.yy.result.suggestColumns.identifierChain.length === 0)
    ) {
      parser.yy.result.suggestColumnAliases = parser.yy.selectListAliases;
    }
  };

  parser.mergeSuggestKeywords = function () {
    let result = [];
    Array.prototype.slice.call(arguments).forEach(suggestion => {
      if (typeof suggestion !== 'undefined' && typeof suggestion.suggestKeywords !== 'undefined') {
        result = result.concat(suggestion.suggestKeywords);
      }
    });
    if (result.length > 0) {
      return { suggestKeywords: result };
    }
    return {};
  };

  parser.suggestValueExpressionKeywords = function (valueExpression, extras) {
    const expressionKeywords = parser.getValueExpressionKeywords(valueExpression, extras);
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
    const keywords = [{ value: 'CASE', weight: 450 }, 'FALSE', 'TRUE', 'NULL'];
    if (!excludeAsterisk) {
      keywords.push({ value: '*', weight: 10000 });
    }
    return keywords;
  };

  parser.getValueExpressionKeywords = function (valueExpression, extras) {
    const types = valueExpression.lastType ? valueExpression.lastType.types : valueExpression.types;
    // We could have valueExpression.columnReference to suggest based on column type
    let keywords = [
      '<',
      '<=',
      '<=>',
      '<>',
      '=',
      '>',
      '>=',
      'BETWEEN',
      'IN',
      'IS NOT NULL',
      'IS NULL',
      'IS NOT TRUE',
      'IS TRUE',
      'IS NOT FALSE',
      'IS FALSE',
      'NOT BETWEEN',
      'NOT IN'
    ];
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
          STRING: ['LIKE', 'NOT LIKE', 'REGEXP', 'RLIKE']
        }
      };
    }
    if (matchesType(parser.yy.activeDialect, ['BOOLEAN'], types)) {
      keywords = keywords.concat(['AND', 'OR']);
    }
    if (matchesType(parser.yy.activeDialect, ['NUMBER'], types)) {
      keywords = keywords.concat(['+', '-', '*', '/', '%', 'DIV']);
    }
    if (matchesType(parser.yy.activeDialect, ['STRING'], types)) {
      keywords = keywords.concat(['LIKE', 'NOT LIKE', 'REGEXP', 'RLIKE']);
    }
    return { suggestKeywords: keywords };
  };

  parser.getTypeKeywords = function () {
    return [
      'BIGINT',
      'BOOLEAN',
      'CHAR',
      'DECIMAL',
      'DOUBLE',
      'FLOAT',
      'INT',
      'SMALLINT',
      'TIMESTAMP',
      'STRING',
      'TINYINT',
      'VARCHAR'
    ];
  };

  parser.getColumnDataTypeKeywords = function () {
    return parser.getTypeKeywords();
  };

  parser.addColRefIfExists = function (valueExpression) {
    if (valueExpression.columnReference) {
      parser.yy.result.colRef = { identifierChain: valueExpression.columnReference };
    }
  };

  parser.selectListNoTableSuggest = function (selectListEdit, hasDistinctOrAll) {
    if (selectListEdit.cursorAtStart) {
      let keywords = parser.getSelectListKeywords();
      if (!hasDistinctOrAll) {
        keywords = keywords.concat([
          { value: 'ALL', weight: 2 },
          { value: 'DISTINCT', weight: 2 }
        ]);
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
    if (
      selectListEdit.suggestAggregateFunctions &&
      (!hasDistinctOrAll || hasDistinctOrAll === 'ALL')
    ) {
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

  parser.findCaseType = function (whenThenList) {
    const types = {};
    whenThenList.caseTypes.forEach(valueExpression => {
      valueExpression.types.forEach(type => {
        types[type] = true;
      });
    });
    if (Object.keys(types).length === 1) {
      return { types: [Object.keys(types)[0]] };
    }
    return { types: ['T'] };
  };

  parser.applyArgumentTypesToSuggestions = function (functionName, position) {
    if (parser.yy.result.suggestFunctions || parser.yy.result.suggestColumns) {
      parser.yy.result.udfArgument = {
        name: functionName.toLowerCase(),
        position: position
      };
    }
  };

  parser.commitLocations = function () {
    if (parser.yy.locations.length === 0) {
      return;
    }

    const tablePrimaries = parser.yy.latestTablePrimaries;

    let i = parser.yy.locations.length;

    while (i--) {
      const location = parser.yy.locations[i];
      if (location.type === 'variable' && location.colRef) {
        parser.expandIdentifierChain({
          wrapper: location.colRef,
          tablePrimaries: tablePrimaries,
          isColumnWrapper: true
        });
        delete location.colRef.linked;
      }

      if (location.type === 'unknown') {
        if (
          typeof location.identifierChain !== 'undefined' &&
          location.identifierChain.length > 0 &&
          location.identifierChain.length <= 2 &&
          tablePrimaries
        ) {
          let found = tablePrimaries.filter(primary => {
            return (
              equalIgnoreCase(primary.alias, location.identifierChain[0].name) ||
              (primary.identifierChain &&
                equalIgnoreCase(primary.identifierChain[0].name, location.identifierChain[0].name))
            );
          });
          if (!found.length && location.firstInChain) {
            found = tablePrimaries.filter(primary => {
              return (
                !primary.alias &&
                primary.identifierChain &&
                equalIgnoreCase(
                  primary.identifierChain[primary.identifierChain.length - 1].name,
                  location.identifierChain[0].name
                )
              );
            });
          }

          if (found.length) {
            if (
              found[0].identifierChain.length > 1 &&
              location.identifierChain.length === 1 &&
              equalIgnoreCase(found[0].identifierChain[0].name, location.identifierChain[0].name)
            ) {
              location.type = 'database';
            } else if (
              found[0].alias &&
              equalIgnoreCase(location.identifierChain[0].name, found[0].alias) &&
              location.identifierChain.length > 1
            ) {
              location.type = 'column';
              parser.expandIdentifierChain({
                tablePrimaries: tablePrimaries,
                wrapper: location,
                anyOwner: true
              });
            } else if (
              !found[0].alias &&
              found[0].identifierChain &&
              equalIgnoreCase(
                location.identifierChain[0].name,
                found[0].identifierChain[found[0].identifierChain.length - 1].name
              ) &&
              location.identifierChain.length > 1
            ) {
              location.type = 'column';
              parser.expandIdentifierChain({
                tablePrimaries: tablePrimaries,
                wrapper: location,
                anyOwner: true
              });
            } else {
              location.type = 'table';
              parser.expandIdentifierChain({
                tablePrimaries: tablePrimaries,
                wrapper: location,
                anyOwner: true
              });
            }
          } else if (parser.yy.subQueries) {
            found = parser.yy.subQueries.filter(subQuery => {
              return equalIgnoreCase(subQuery.alias, location.identifierChain[0].name);
            });
            if (found.length > 0) {
              location.type = 'subQuery';
              location.identifierChain = [{ subQuery: found[0].alias }];
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
          parser.expandIdentifierChain({
            tablePrimaries: tablePrimaries,
            wrapper: location,
            anyOwner: false
          });
          if (location.tables.length === 0) {
            parser.yy.locations.splice(i, 1);
          }
        } else {
          parser.yy.locations.splice(i, 1);
        }
      }

      if (
        location.type === 'table' &&
        typeof location.identifierChain !== 'undefined' &&
        location.identifierChain.length === 1 &&
        location.identifierChain[0].name
      ) {
        // Could be a cte reference
        parser.yy.locations.some(otherLocation => {
          if (
            otherLocation.type === 'alias' &&
            otherLocation.source === 'cte' &&
            identifierEquals(otherLocation.alias, location.identifierChain[0].name)
          ) {
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

      if (
        location.type === 'table' &&
        (typeof location.identifierChain === 'undefined' || location.identifierChain.length === 0)
      ) {
        parser.yy.locations.splice(i, 1);
      }

      if (location.type === 'unknown') {
        location.type = 'column';
      }

      // A column location might refer to a previously defined alias, i.e. last 'foo' in "SELECT cast(id AS int) foo FROM tbl ORDER BY foo;"
      if (location.type === 'column') {
        for (let j = i - 1; j >= 0; j--) {
          const otherLocation = parser.yy.locations[j];
          if (
            otherLocation.type === 'alias' &&
            otherLocation.source === 'column' &&
            location.identifierChain &&
            location.identifierChain.length === 1 &&
            location.identifierChain[0].name &&
            otherLocation.alias &&
            location.identifierChain[0].name.toLowerCase() === otherLocation.alias.toLowerCase()
          ) {
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
        const initialIdentifierChain = location.identifierChain
          ? location.identifierChain.concat()
          : undefined;

        parser.expandIdentifierChain({
          tablePrimaries: tablePrimaries,
          wrapper: location,
          anyOwner: true,
          isColumnWrapper: true,
          isColumnLocation: true
        });

        if (typeof location.identifierChain === 'undefined') {
          parser.yy.locations.splice(i, 1);
        } else if (
          location.identifierChain.length === 0 &&
          initialIdentifierChain &&
          initialIdentifierChain.length === 1
        ) {
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

  const prioritizeSuggestions = function () {
    parser.yy.result.lowerCase = parser.yy.lowerCase || false;

    const cteIndex = {};

    if (typeof parser.yy.latestCommonTableExpressions !== 'undefined') {
      parser.yy.latestCommonTableExpressions.forEach(cte => {
        cteIndex[cte.alias.toLowerCase()] = cte;
      });
    }

    SIMPLE_TABLE_REF_SUGGESTIONS.forEach(suggestionType => {
      if (
        suggestionType !== 'suggestAggregateFunctions' &&
        typeof parser.yy.result[suggestionType] !== 'undefined' &&
        parser.yy.result[suggestionType].tables.length === 0
      ) {
        delete parser.yy.result[suggestionType];
      } else if (
        typeof parser.yy.result[suggestionType] !== 'undefined' &&
        typeof parser.yy.result[suggestionType].tables !== 'undefined'
      ) {
        for (let i = parser.yy.result[suggestionType].tables.length - 1; i >= 0; i--) {
          const table = parser.yy.result[suggestionType].tables[i];
          if (
            table.identifierChain.length === 1 &&
            typeof table.identifierChain[0].name !== 'undefined' &&
            typeof cteIndex[table.identifierChain[0].name.toLowerCase()] !== 'undefined'
          ) {
            parser.yy.result[suggestionType].tables.splice(i, 1);
          }
        }
      }
    });

    if (typeof parser.yy.result.colRef !== 'undefined') {
      if (
        !parser.yy.result.colRef.linked ||
        typeof parser.yy.result.colRef.identifierChain === 'undefined' ||
        parser.yy.result.colRef.identifierChain.length === 0
      ) {
        delete parser.yy.result.colRef;
        if (typeof parser.yy.result.suggestColRefKeywords !== 'undefined') {
          Object.keys(parser.yy.result.suggestColRefKeywords).forEach(type => {
            parser.yy.result.suggestKeywords = parser.yy.result.suggestKeywords.concat(
              parser.createWeightedKeywords(parser.yy.result.suggestColRefKeywords[type], -1)
            );
          });
          delete parser.yy.result.suggestColRefKeywords;
        }
        if (
          parser.yy.result.suggestColumns &&
          parser.yy.result.suggestColumns.types.length === 1 &&
          parser.yy.result.suggestColumns.types[0] === 'COLREF'
        ) {
          parser.yy.result.suggestColumns.types = ['T'];
        }
        delete parser.yy.result.suggestValues;
      }
    }

    if (typeof parser.yy.result.colRef !== 'undefined') {
      if (
        !parser.yy.result.suggestValues &&
        !parser.yy.result.suggestColRefKeywords &&
        (!parser.yy.result.suggestColumns || parser.yy.result.suggestColumns.types[0] !== 'COLREF')
      ) {
        delete parser.yy.result.colRef;
      }
    }
    if (
      typeof parser.yy.result.suggestIdentifiers !== 'undefined' &&
      parser.yy.result.suggestIdentifiers.length > 0
    ) {
      delete parser.yy.result.suggestTables;
      delete parser.yy.result.suggestDatabases;
    }
    if (typeof parser.yy.result.suggestColumns !== 'undefined') {
      const suggestColumns = parser.yy.result.suggestColumns;
      if (typeof suggestColumns.tables === 'undefined' || suggestColumns.tables.length === 0) {
        delete parser.yy.result.suggestColumns;
        delete parser.yy.result.subQueries;
      } else {
        delete parser.yy.result.suggestTables;
        delete parser.yy.result.suggestDatabases;

        suggestColumns.tables.forEach(table => {
          if (
            typeof table.identifierChain !== 'undefined' &&
            table.identifierChain.length === 1 &&
            typeof table.identifierChain[0].name !== 'undefined'
          ) {
            const cte = cteIndex[table.identifierChain[0].name.toLowerCase()];
            if (typeof cte !== 'undefined') {
              delete table.identifierChain[0].name;
              table.identifierChain[0].cte = cte.alias;
            }
          } else if (typeof table.identifierChain === 'undefined' && table.subQuery) {
            table.identifierChain = [{ subQuery: table.subQuery }];
            delete table.subQuery;
          }
        });

        if (
          typeof suggestColumns.identifierChain !== 'undefined' &&
          suggestColumns.identifierChain.length === 0
        ) {
          delete suggestColumns.identifierChain;
        }
      }
    } else {
      delete parser.yy.result.subQueries;
    }

    if (typeof parser.yy.result.suggestJoinConditions !== 'undefined') {
      if (
        typeof parser.yy.result.suggestJoinConditions.tables === 'undefined' ||
        parser.yy.result.suggestJoinConditions.tables.length === 0
      ) {
        delete parser.yy.result.suggestJoinConditions;
      }
    }

    if (
      typeof parser.yy.result.suggestTables !== 'undefined' &&
      typeof parser.yy.result.commonTableExpressions !== 'undefined'
    ) {
      const ctes = [];
      parser.yy.result.commonTableExpressions.forEach(cte => {
        const suggestion = { name: cte.alias };
        if (parser.yy.result.suggestTables.prependFrom) {
          suggestion.prependFrom = true;
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

  parser.identifyPartials = function (beforeCursor, afterCursor) {
    const beforeMatch = beforeCursor.match(/[0-9a-zA-Z_]*$/);
    const afterMatch = afterCursor.match(/^[0-9a-zA-Z_]*(?:\((?:[^)]*\))?)?/);
    return {
      left: beforeMatch ? beforeMatch[0].length : 0,
      right: afterMatch ? afterMatch[0].length : 0
    };
  };

  const addCleanTablePrimary = function (tables, tablePrimary) {
    if (tablePrimary.alias) {
      tables.push({ alias: tablePrimary.alias, identifierChain: tablePrimary.identifierChain });
    } else {
      tables.push({ identifierChain: tablePrimary.identifierChain });
    }
  };

  parser.expandIdentifierChain = function (options) {
    const wrapper = options.wrapper;
    const anyOwner = options.anyOwner;
    const isColumnWrapper = options.isColumnWrapper;
    const isColumnLocation = options.isColumnLocation;
    let tablePrimaries = options.tablePrimaries || parser.yy.latestTablePrimaries;

    if (typeof wrapper.identifierChain === 'undefined' || typeof tablePrimaries === 'undefined') {
      return;
    }
    let identifierChain = wrapper.identifierChain.concat();

    if (tablePrimaries.length === 0) {
      delete wrapper.identifierChain;
      return;
    }

    if (!anyOwner) {
      tablePrimaries = filterTablePrimariesForOwner(tablePrimaries, wrapper.owner);
    }

    if (identifierChain.length > 0 && identifierChain[identifierChain.length - 1].asterisk) {
      const tables = [];
      tablePrimaries.forEach(tablePrimary => {
        if (identifierChain.length > 1 && !tablePrimary.subQueryAlias) {
          if (
            identifierChain.length === 2 &&
            equalIgnoreCase(tablePrimary.alias, identifierChain[0].name)
          ) {
            addCleanTablePrimary(tables, tablePrimary);
          } else if (
            identifierChain.length === 2 &&
            equalIgnoreCase(tablePrimary.identifierChain[0].name, identifierChain[0].name)
          ) {
            addCleanTablePrimary(tables, tablePrimary);
          } else if (
            identifierChain.length === 3 &&
            tablePrimary.identifierChain.length > 1 &&
            equalIgnoreCase(tablePrimary.identifierChain[0].name, identifierChain[0].name) &&
            equalIgnoreCase(tablePrimary.identifierChain[1].name, identifierChain[1].name)
          ) {
            addCleanTablePrimary(tables, tablePrimary);
          }
        } else if (tablePrimary.subQueryAlias) {
          tables.push({ identifierChain: [{ subQuery: tablePrimary.subQueryAlias }] });
        } else {
          addCleanTablePrimary(tables, tablePrimary);
        }
      });
      // Possible Joins
      if (tables.length > 0) {
        wrapper.tables = tables;
        delete wrapper.identifierChain;
        return;
      }
    }

    // IdentifierChain contains a possibly started identifier or empty, example: a.b.c = ['a', 'b', 'c']
    // Reduce the tablePrimaries to the one that matches the first identifier if found
    let foundPrimary;
    let doubleMatch = false;
    let aliasMatch = false;
    if (identifierChain.length > 0) {
      for (let i = 0; i < tablePrimaries.length; i++) {
        if (tablePrimaries[i].subQueryAlias) {
          if (equalIgnoreCase(tablePrimaries[i].subQueryAlias, identifierChain[0].name)) {
            foundPrimary = tablePrimaries[i];
          }
        } else if (equalIgnoreCase(tablePrimaries[i].alias, identifierChain[0].name)) {
          foundPrimary = tablePrimaries[i];
          aliasMatch = true;
          break;
        } else if (
          tablePrimaries[i].identifierChain.length > 1 &&
          identifierChain.length > 1 &&
          equalIgnoreCase(tablePrimaries[i].identifierChain[0].name, identifierChain[0].name) &&
          equalIgnoreCase(tablePrimaries[i].identifierChain[1].name, identifierChain[1].name)
        ) {
          foundPrimary = tablePrimaries[i];
          doubleMatch = true;
          break;
        } else if (
          !foundPrimary &&
          equalIgnoreCase(tablePrimaries[i].identifierChain[0].name, identifierChain[0].name) &&
          identifierChain.length > (isColumnLocation ? 1 : 0)
        ) {
          foundPrimary = tablePrimaries[i];
          // No break as first two can still match.
        } else if (
          !foundPrimary &&
          tablePrimaries[i].identifierChain.length > 1 &&
          !tablePrimaries[i].alias &&
          equalIgnoreCase(
            tablePrimaries[i].identifierChain[tablePrimaries[i].identifierChain.length - 1].name,
            identifierChain[0].name
          )
        ) {
          // This is for the case SELECT baa. FROM bla.baa, blo.boo;
          foundPrimary = tablePrimaries[i];
          break;
        }
      }
    }

    if (foundPrimary) {
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
            // This prevents alias from being added automatically in sqlAutocompleter.js
            wrapper.tables = [{ identifierChain: foundPrimary.identifierChain }];
          } else {
            wrapper.tables = [
              { identifierChain: foundPrimary.identifierChain, alias: foundPrimary.alias }
            ];
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
          wrapper.tables.push({ identifierChain: identifierChain });
          delete wrapper.identifierChain;
        } else {
          wrapper.identifierChain = identifierChain;
        }
      }
    } else {
      if (isColumnWrapper) {
        wrapper.tables = [];
      }
      tablePrimaries.forEach(tablePrimary => {
        const targetTable = tablePrimary.subQueryAlias
          ? { subQuery: tablePrimary.subQueryAlias }
          : { identifierChain: tablePrimary.identifierChain };
        if (tablePrimary.alias) {
          targetTable.alias = tablePrimary.alias;
        }
        if (wrapper.tables) {
          wrapper.tables.push(targetTable);
        }
      });
    }
    delete wrapper.owner;
    wrapper.linked = true;
  };

  const filterTablePrimariesForOwner = function (tablePrimaries, owner) {
    const result = [];
    tablePrimaries.forEach(primary => {
      if (typeof owner === 'undefined' && typeof primary.owner === 'undefined') {
        result.push(primary);
      } else if (owner === primary.owner) {
        result.push(primary);
      }
    });
    return result;
  };

  const convertTablePrimariesToSuggestions = function (tablePrimaries) {
    const tables = [];
    const identifiers = [];
    tablePrimaries.forEach(tablePrimary => {
      if (tablePrimary.identifierChain && tablePrimary.identifierChain.length > 0) {
        const table = { identifierChain: tablePrimary.identifierChain };
        if (tablePrimary.alias) {
          table.alias = tablePrimary.alias;
          identifiers.push({ name: table.alias + '.', type: 'alias' });
        } else {
          const lastIdentifier =
            tablePrimary.identifierChain[tablePrimary.identifierChain.length - 1];
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
        parser.yy.result.suggestIdentifiers = identifiers.concat(
          parser.yy.result.suggestIdentifiers
        );
      }
    }
    parser.yy.result.suggestColumns.tables = tables;
    if (
      parser.yy.result.suggestColumns.identifierChain &&
      parser.yy.result.suggestColumns.identifierChain.length === 0
    ) {
      delete parser.yy.result.suggestColumns.identifierChain;
    }
    parser.yy.result.suggestColumns.linked = true;
  };

  const linkTablePrimaries = function () {
    if (!parser.yy.cursorFound || typeof parser.yy.latestTablePrimaries === 'undefined') {
      return;
    }

    SIMPLE_TABLE_REF_SUGGESTIONS.forEach(suggestionType => {
      if (
        typeof parser.yy.result[suggestionType] !== 'undefined' &&
        parser.yy.result[suggestionType].tablePrimaries &&
        !parser.yy.result[suggestionType].linked
      ) {
        parser.yy.result[suggestionType].tables = [];
        parser.yy.result[suggestionType].tablePrimaries.forEach(tablePrimary => {
          if (!tablePrimary.subQueryAlias) {
            parser.yy.result[suggestionType].tables.push(
              tablePrimary.alias
                ? {
                    identifierChain: tablePrimary.identifierChain.concat(),
                    alias: tablePrimary.alias
                  }
                : { identifierChain: tablePrimary.identifierChain.concat() }
            );
          }
        });
        delete parser.yy.result[suggestionType].tablePrimaries;
        parser.yy.result[suggestionType].linked = true;
      }
    });

    if (
      typeof parser.yy.result.suggestColumns !== 'undefined' &&
      !parser.yy.result.suggestColumns.linked
    ) {
      const tablePrimaries = filterTablePrimariesForOwner(
        parser.yy.latestTablePrimaries,
        parser.yy.result.suggestColumns.owner
      );
      if (!parser.yy.result.suggestColumns.tables) {
        parser.yy.result.suggestColumns.tables = [];
      }
      if (parser.yy.subQueries.length > 0) {
        parser.yy.result.subQueries = parser.yy.subQueries;
      }
      if (
        typeof parser.yy.result.suggestColumns.identifierChain === 'undefined' ||
        parser.yy.result.suggestColumns.identifierChain.length === 0
      ) {
        if (tablePrimaries.length > 1) {
          convertTablePrimariesToSuggestions(tablePrimaries);
        } else {
          if (
            tablePrimaries.length === 1 &&
            (tablePrimaries[0].alias || tablePrimaries[0].subQueryAlias)
          ) {
            convertTablePrimariesToSuggestions(tablePrimaries);
          }
          parser.expandIdentifierChain({
            wrapper: parser.yy.result.suggestColumns,
            anyOwner: false,
            isColumnWrapper: true
          });
        }
      } else {
        parser.expandIdentifierChain({
          wrapper: parser.yy.result.suggestColumns,
          anyOwner: false,
          isColumnWrapper: true
        });
      }
    }

    if (typeof parser.yy.result.colRef !== 'undefined' && !parser.yy.result.colRef.linked) {
      parser.expandIdentifierChain({ wrapper: parser.yy.result.colRef });

      const primaries = filterTablePrimariesForOwner(parser.yy.latestTablePrimaries);
      if (
        primaries.length === 0 ||
        (primaries.length > 1 && parser.yy.result.colRef.identifierChain.length === 1)
      ) {
        parser.yy.result.colRef.identifierChain = [];
      }
    }
    if (
      typeof parser.yy.result.suggestKeyValues !== 'undefined' &&
      !parser.yy.result.suggestKeyValues.linked
    ) {
      parser.expandIdentifierChain({ wrapper: parser.yy.result.suggestKeyValues });
    }
  };

  parser.addTablePrimary = function (ref) {
    if (typeof parser.yy.latestTablePrimaries === 'undefined') {
      parser.yy.latestTablePrimaries = [];
    }
    parser.yy.latestTablePrimaries.push(ref);
  };

  parser.suggestFileFormats = function () {
    parser.suggestKeywords([
      'AVRO',
      'KUDU',
      'ORC',
      'PARQUET',
      'RCFILE',
      'SEQUENCEFILE',
      'TEXTFILE'
    ]);
  };

  parser.getKeywordsForOptionalsLR = function (optionals, keywords, override) {
    let result = [];

    for (let i = 0; i < optionals.length; i++) {
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
    let keywords = [
      'ALTER',
      'CREATE',
      'DESCRIBE',
      'DROP',
      'GRANT',
      'INSERT',
      'REVOKE',
      'SELECT',
      'SET',
      'SHOW',
      'TRUNCATE',
      'UPDATE',
      'USE',
      'WITH'
    ];

    if (extraKeywords) {
      keywords = keywords.concat(extraKeywords);
    }

    parser.suggestKeywords(keywords);
  };

  parser.checkForSelectListKeywords = function (selectList) {
    if (selectList.length === 0) {
      return;
    }
    const last = selectList[selectList.length - 1];
    if (!last || !last.valueExpression) {
      return;
    }
    const valueExpressionKeywords = parser.getValueExpressionKeywords(last.valueExpression);
    let keywords = [];
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
    const result = [];
    keywords.forEach(keyword => {
      if (typeof keyword.weight !== 'undefined') {
        keyword.weight = weight + keyword.weight / 10;
        result.push(keyword);
      } else {
        result.push({ value: keyword, weight: weight });
      }
    });
    return result;
  };

  parser.suggestKeywords = function (keywords) {
    const weightedKeywords = [];
    if (keywords.length === 0) {
      return;
    }
    keywords.forEach(keyword => {
      if (typeof keyword.weight !== 'undefined') {
        weightedKeywords.push(keyword);
      } else {
        weightedKeywords.push({ value: keyword, weight: -1 });
      }
    });
    weightedKeywords.sort((a, b) => {
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
      parser.suggestTables({ identifierChain: [{ name: identifier }] });
      return;
    }
    const tableRef = parser.yy.latestTablePrimaries.filter(tablePrimary => {
      return equalIgnoreCase(tablePrimary.alias, identifier);
    });
    if (tableRef.length > 0) {
      parser.suggestColumns({ identifierChain: [{ name: identifier }] });
    } else {
      parser.suggestTables({ identifierChain: [{ name: identifier }] });
    }
  };

  parser.suggestFunctions = function (details) {
    parser.yy.result.suggestFunctions = details || {};
  };

  parser.suggestAggregateFunctions = function () {
    const primaries = [];
    const aliases = {};
    parser.yy.latestTablePrimaries.forEach(primary => {
      if (typeof primary.alias !== 'undefined') {
        aliases[primary.alias] = true;
      }
      // Drop if the first one refers to a table alias (...FROM tbl t, t.map tm ...)
      if (
        typeof primary.identifierChain !== 'undefined' &&
        !aliases[primary.identifierChain[0].name] &&
        typeof primary.owner === 'undefined'
      ) {
        primaries.push(primary);
      }
    });
    parser.yy.result.suggestAggregateFunctions = { tablePrimaries: primaries };
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
      details = { identifierChain: [] };
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

  parser.firstDefined = function () {
    for (let i = 0; i + 1 < arguments.length; i += 2) {
      if (arguments[i]) {
        return arguments[i + 1];
      }
    }
  };

  parser.addColRefToVariableIfExists = function (left, right) {
    if (
      left &&
      left.columnReference &&
      left.columnReference.length &&
      right &&
      right.columnReference &&
      right.columnReference.length &&
      parser.yy.locations.length > 1
    ) {
      const addColRefToVariableLocation = function (variableValue, colRef) {
        // See if colref is actually an alias
        if (colRef.length === 1 && colRef[0].name) {
          parser.yy.locations.some(location => {
            if (location.type === 'column' && location.alias === colRef[0].name) {
              colRef = location.identifierChain;
              return true;
            }
          });
        }

        for (let i = parser.yy.locations.length - 1; i > 0; i--) {
          const location = parser.yy.locations[i];
          if (location.type === 'variable' && location.value === variableValue) {
            location.colRef = { identifierChain: colRef };
            break;
          }
        }
      };

      if (/\${[^}]*}/.test(left.columnReference[0].name)) {
        // left is variable
        addColRefToVariableLocation(left.columnReference[0].name, right.columnReference);
      } else if (/\${[^}]*}/.test(right.columnReference[0].name)) {
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
      const cursorIndex = parser.yy.partialCursor
        ? yytext.indexOf('\u2021')
        : yytext.indexOf('\u2020');
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

  let lexerModified = false;

  /**
   * Main parser function
   */
  parser.parseSql = function (beforeCursor, afterCursor, debug) {
    // Jison counts CRLF as two lines in the locations
    beforeCursor = beforeCursor.replace(/\r\n|\n\r/gm, '\n');
    afterCursor = afterCursor.replace(/\r\n|\n\r/gm, '\n');
    parser.yy.result = { locations: [] };
    parser.yy.lowerCase = false;
    parser.yy.locations = [];
    parser.yy.definitions = [];
    parser.yy.allLocations = [];
    parser.yy.subQueries = [];
    parser.yy.errors = [];
    parser.yy.selectListAliases = [];
    parser.yy.activeDialect = 'generic';

    parser.yy.locationsStack = [];
    parser.yy.primariesStack = [];
    parser.yy.subQueriesStack = [];
    parser.yy.resultStack = [];
    parser.yy.selectListAliasesStack = [];

    delete parser.yy.caseDetermined;
    delete parser.yy.cursorFound;
    delete parser.yy.partialCursor;

    // Fix for parser bug when switching lexer states
    if (!lexerModified) {
      const originalSetInput = parser.lexer.setInput;
      parser.lexer.setInput = function (input, yy) {
        return originalSetInput.bind(parser.lexer)(input, yy);
      };
      lexerModified = true;
    }

    parser.prepareNewStatement();

    const REASONABLE_SURROUNDING_LENGTH = 150000; // About 3000 lines before and after

    if (beforeCursor.length > REASONABLE_SURROUNDING_LENGTH) {
      if (beforeCursor.length - beforeCursor.lastIndexOf(';') > REASONABLE_SURROUNDING_LENGTH) {
        // Bail out if the last complete statement is more than 150000 chars before
        return {};
      }
      // Cut it at the first statement found within 150000 chars before
      const lastReasonableChunk = beforeCursor.substring(
        beforeCursor.length - REASONABLE_SURROUNDING_LENGTH
      );
      beforeCursor = lastReasonableChunk.substring(lastReasonableChunk.indexOf(';') + 1);
    }

    if (afterCursor.length > REASONABLE_SURROUNDING_LENGTH) {
      if (afterCursor.length - afterCursor.indexOf(';') > REASONABLE_SURROUNDING_LENGTH) {
        // No need to bail out for what's comes after, we can still get keyword completion
        afterCursor = '';
      } else {
        // Cut it at the last statement found within 150000 chars after
        const firstReasonableChunk = afterCursor.substring(0, REASONABLE_SURROUNDING_LENGTH);
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

    let result;
    try {
      // Add |CURSOR| or |PARTIAL_CURSOR| to represent the different cursor states in the lexer
      result = parser.parse(
        beforeCursor +
          (beforeCursor.length === 0 || /[\s(]$/.test(beforeCursor) ? ' \u2020 ' : '\u2021') +
          afterCursor
      );
    } catch (err) {
      // On any error try to at least return any existing result
      if (typeof parser.yy.result === 'undefined') {
        throw err;
      }
      if (debug) {
        console.warn(err);
        console.warn(err.stack);
      }
      result = parser.yy.result;
    }
    if (parser.yy.errors.length > 0) {
      parser.yy.result.errors = parser.yy.errors;
      if (debug) {
        console.warn(parser.yy.errors);
      }
    }
    try {
      linkTablePrimaries();
      parser.commitLocations();
      // Clean up and prioritize
      prioritizeSuggestions();
    } catch (err) {
      if (debug) {
        console.warn(err);
        console.warn(err.stack);
      }
    }

    parser.yy.allLocations.sort((a, b) => {
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
    parser.yy.result.definitions = parser.yy.definitions;

    parser.yy.result.locations.forEach(location => {
      delete location.linked;
    });
    if (typeof parser.yy.result.suggestColumns !== 'undefined') {
      delete parser.yy.result.suggestColumns.linked;
    }

    SIMPLE_TABLE_REF_SUGGESTIONS.forEach(suggestionType => {
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
      // Remove the cursor from expected tokens
      result.error.expected = result.error.expected.filter(token => token.indexOf('CURSOR') === -1);
    }

    if (typeof result.error !== 'undefined' && result.error.recoverable) {
      delete result.error;
    }

    // Adjust all the statement locations to include white space surrounding them
    let lastStatementLocation = null;
    result.locations.forEach(location => {
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

export default {
  initSqlParser: initSqlParser,
  initSyntaxParser: initSyntaxParser
};
