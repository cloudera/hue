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

var SqlAutocompleter2 = (function () {

  var IDENTIFIER_REGEX = /[a-zA-Z_0-9\$\u00A2-\uFFFF]/;

  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @param {Number} options.timeout
   * @constructor
   */
  function SqlAutocompleter2(options) {
    var self = this;
    self.snippet = options.snippet;
    self.timeout = options.timeout;
  }

  // Keyword weights come from the parser
  var DEFAULT_WEIGHTS = {
    POPULAR_AGGREGATE: 1500,
    POPULAR_GROUP_BY: 1400,
    POPULAR_ORDER_BY: 1300,
    POPULAR_FILTER: 1200,
    POPULAR_ACTIVE_JOIN: 1200,
    POPULAR_JOIN_CONDITION: 1100,
    COLUMN: 1000,
    SAMPLE: 900,
    IDENTIFIER: 800,
    CTE: 700,
    TABLE: 600,
    DATABASE: 500,
    UDF: 400,
    HDFS: 300,
    VIRTUAL_COLUMN: 200,
    COLREF_KEYWORD: 100,
    VARIABLE: 50,
    JOIN: -1
  };

  SqlAutocompleter2.prototype.autocomplete = function (beforeCursor, afterCursor, callback, editor) {
    var self = this;
    var parseResult = sql.parseSql(beforeCursor, afterCursor, self.snippet.type(), false);

    if (typeof hueDebug !== 'undefined' && hueDebug.showParseResult) {
      console.log(parseResult);
    }

    var deferrals = [];
    var completions = [];
    var columnSuggestions = [];

    if (typeof editor !== 'undefined' && editor !== null) {
      editor.showSpinner();
    }
    if (parseResult.suggestKeywords) {
      parseResult.suggestKeywords.forEach(function (keyword) {
        completions.push({
          value: parseResult.lowerCase ? keyword.value.toLowerCase() : keyword.value,
          meta: 'keyword',
          weight: keyword.weight
        });
      });
    }

    if (parseResult.suggestIdentifiers) {
      parseResult.suggestIdentifiers.forEach(function (identifier) {
        completions.push({value: identifier.name, meta: identifier.type, weight: DEFAULT_WEIGHTS.IDENTIFIER });
      });
    }

    if (parseResult.suggestCommonTableExpressions) {
      parseResult.suggestCommonTableExpressions.forEach(function (expression) {
        var prefix = expression.prependQuestionMark ? '? ' : '';
        if (expression.prependFrom) {
          prefix += parseResult.lowerCase ? 'from ' : 'FROM ';
        }
        completions.push({value: prefix + expression.name, meta: 'CTE', weight: DEFAULT_WEIGHTS.CTE });
      });
    }

    var database = parseResult.useDatabase || self.snippet.database();

    var colRefDeferral = $.Deferred();
    deferrals.push(colRefDeferral);
    var colRef = null;

    if (parseResult.colRef) {
      var colRefCallback = function (data) {
        if (typeof data.type !== 'undefined') {
          colRef = data;
        } else if (typeof data.extended_columns !== 'undefined' && data.extended_columns.length === 1) {
          colRef = data.extended_columns[0];
        }
        colRefDeferral.resolve();
      };

      var foundVarRef = parseResult.colRef.identifierChain.filter(function (identifier) {
        return typeof identifier.name !== 'undefined' && identifier.name.indexOf('${') === 0;
      });

      if (foundVarRef.length > 0) {
        colRefCallback({ type: 'T' });
      } else {
        try {
          self.fetchFieldsForIdentifiers(database, parseResult.colRef.identifierChain, colRefCallback, colRefDeferral.resolve);
        } catch(e) {
          colRefCallback({ type: 'T' });
        } // TODO: Ignore for subqueries
      }
    } else {
      colRefDeferral.resolve();
    }

    if (parseResult.suggestJoins && HAS_OPTIMIZER) {
      var joinsDeferral = $.Deferred();
      deferrals.push(joinsDeferral);
      self.snippet.getApiHelper().fetchNavOptPopularJoins({
        sourceType: self.snippet.type(),
        timeout: self.timeout,
        defaultDatabase: database,
        silenceErrors: true,
        tables: parseResult.suggestJoins.tables,
        successCallback: function (data) {
          data.values.forEach(function (value) {
            var suggestionString = parseResult.suggestJoins.prependJoin ? (parseResult.lowerCase ? 'join ' : 'JOIN ') : '';
            var first = true;

            var existingTables = {};
            parseResult.suggestJoins.tables.forEach(function (table) {
              existingTables[table.identifierChain[table.identifierChain.length - 1].name] = true;
            });

            var joinRequired = false;
            var tablesAdded = false;
            value.tables.forEach(function (table) {
              var tableParts = table.split('.');
              if (!existingTables[tableParts[tableParts.length - 1]]) {
                tablesAdded = true;
                var identifier = self.convertNavOptQualifiedIdentifier(table, database, parseResult.suggestJoins.tables, false);
                suggestionString += joinRequired ? (parseResult.lowerCase ? ' join ' : ' JOIN ') + identifier : identifier;
                joinRequired = true;
              }
            });

            if (value.joinCols.length > 0) {
              if (!tablesAdded && parseResult.suggestJoins.prependJoin) {
                suggestionString = '';
                tablesAdded = true;
              }
              suggestionString += parseResult.lowerCase ? ' on ' : ' ON ';
            }
            if (tablesAdded) {
              value.joinCols.forEach(function (joinColPair) {
                if (!first) {
                  suggestionString += parseResult.lowerCase ? ' and ' : ' AND ';
                }
                suggestionString += self.convertNavOptQualifiedIdentifier(joinColPair.columns[0], database, parseResult.suggestJoins.tables, true) + ' = ' + self.convertNavOptQualifiedIdentifier(joinColPair.columns[1], database, parseResult.suggestJoins.tables, true);
                first = false;
              });
              completions.push({
                value: suggestionString,
                meta: 'join',
                weight: parseResult.suggestJoins.prependJoin ? DEFAULT_WEIGHTS.JOIN : DEFAULT_WEIGHTS.POPULAR_ACTIVE_JOIN,
                docHTML: self.createJoinHtml(suggestionString)
              });
            }
          });
          joinsDeferral.resolve();
        },
        errorCallback: joinsDeferral.resolve
      });
    }

    if (parseResult.suggestJoinConditions && HAS_OPTIMIZER) {
      var joinConditionsDeferral = $.Deferred();
      deferrals.push(joinConditionsDeferral);
      self.snippet.getApiHelper().fetchNavOptPopularJoins({
        sourceType: self.snippet.type(),
        timeout: self.timeout,
        defaultDatabase: database,
        silenceErrors: true,
        tables: parseResult.suggestJoinConditions.tables,
        successCallback: function (data) {
          data.values.forEach(function (value) {
            if (value.joinCols.length > 0) {
              var suggestionString = parseResult.suggestJoinConditions.prependOn ? (parseResult.lowerCase ? 'on ' : 'ON ') : '';
              var first = true;
              value.joinCols.forEach(function (joinColPair) {
                if (!first) {
                  suggestionString += parseResult.lowerCase ? ' and ' : ' AND ';
                }
                suggestionString += self.convertNavOptQualifiedIdentifier(joinColPair.columns[0], database, parseResult.suggestJoinConditions.tables, true) + ' = ' + self.convertNavOptQualifiedIdentifier(joinColPair.columns[1], database,parseResult.suggestJoinConditions.tables, true);
                first = false;
              });
              completions.push({
                value: suggestionString,
                meta: 'condition',
                weight: DEFAULT_WEIGHTS.POPULAR_JOIN_CONDITION,
                docHTML: self.createJoinHtml(suggestionString)
              });
            }
          });
          joinConditionsDeferral.resolve();
        },
        errorCallback: joinConditionsDeferral.resolve
      });
    }

    if (parseResult.suggestFunctions) {
      var suggestFunctionsDeferral = $.Deferred();
      if (parseResult.suggestFunctions.types && parseResult.suggestFunctions.types[0] === 'COLREF') {
        colRefDeferral.done(function () {
          if (colRef !== null && colRef.type) {
            SqlFunctions.suggestFunctions(self.snippet.type(), [colRef.type.toUpperCase()], parseResult.suggestAggregateFunctions || false, parseResult.suggestAnalyticFunctions || false, completions, DEFAULT_WEIGHTS.UDF);
          } else {
            SqlFunctions.suggestFunctions(self.snippet.type(), ['T'], parseResult.suggestAggregateFunctions || false, parseResult.suggestAnalyticFunctions || false, completions, DEFAULT_WEIGHTS.UDF);
          }
          suggestFunctionsDeferral.resolve();
        });
      } else {
        SqlFunctions.suggestFunctions(self.snippet.type(), parseResult.suggestFunctions.types || ['T'], parseResult.suggestAggregateFunctions || false, parseResult.suggestAnalyticFunctions || false, completions, DEFAULT_WEIGHTS.UDF);
        suggestFunctionsDeferral.resolve();
      }

      if (HAS_OPTIMIZER && typeof parseResult.suggestAggregateFunctions !== 'undefined' && parseResult.suggestAggregateFunctions.tables.length > 0) {
        var suggestAggregatesDeferral = $.Deferred();
        deferrals.push(suggestAggregatesDeferral);
        self.snippet.getApiHelper().fetchNavOptTopAggs({
          sourceType: self.snippet.type(),
          timeout: self.timeout,
          defaultDatabase: database,
          silenceErrors: true,
          tables: parseResult.suggestAggregateFunctions.tables,
          successCallback: function (data) {
            if (data.values.length > 0) {

              // TODO: Handle column conflicts with multiple tables

              // Substitute qualified table identifiers with either alias or empty string
              var substitutions = [];
              parseResult.suggestAggregateFunctions.tables.forEach(function (table) {
                var replaceWith = table.alias ? table.alias + '.' : '';
                if (table.identifierChain.length > 1) {
                  substitutions.push({
                    replace: new RegExp($.map(table.identifierChain, function (identifier) {
                          return identifier.name
                        }).join('\.') + '\.', 'gi'),
                    with: replaceWith
                  })
                } else if (table.identifierChain.length === 1) {
                  substitutions.push({
                    replace: new RegExp(database + '\.' + table.identifierChain[0].name + '\.', 'gi'),
                    with: replaceWith
                  });
                  substitutions.push({
                    replace: new RegExp(table.identifierChain[0].name + '\.', 'gi'),
                    with: replaceWith
                  })
                }
              });

              data.values.forEach(function (value) {
                var clean = value.aggregateClause;
                substitutions.forEach(function (substitution) {
                  clean = clean.replace(substitution.replace, substitution.with);
                });

                completions.push({
                  value: clean,
                  meta: 'aggregate *',
                  weight: DEFAULT_WEIGHTS.POPULAR_AGGREGATE + value.totalQueryCount,
                  docHTML: self.createAggregateHtml(value)
                });
              })
            }
            suggestAggregatesDeferral.resolve();
          },
          errorCallback: suggestAggregatesDeferral.resolve
        });
      }
      deferrals.push(suggestFunctionsDeferral);
    }

    if (parseResult.suggestColumnAliases) {
      parseResult.suggestColumnAliases.forEach(function (columnAlias) {
        var type = columnAlias.types && columnAlias.types.length == 1 ? columnAlias.types[0] : 'T';
        if (type === 'COLREF') {
          completions.push({ value: columnAlias.name, meta: 'alias', weight: DEFAULT_WEIGHTS.COLUMN });
        } else {
          completions.push({ value: columnAlias.name, meta: type, weight: DEFAULT_WEIGHTS.COLUMN });
        }
      });
    }

    if (parseResult.suggestValues) {
      var suggestValuesDeferral = $.Deferred();
      if (parseResult.colRef && parseResult.colRef.identifierChain) {
        completions.push({ value: '${' + parseResult.colRef.identifierChain[parseResult.colRef.identifierChain.length - 1].name + '}', meta: 'variable', weight: DEFAULT_WEIGHTS.VARIABLE });
      }
      colRefDeferral.done(function () {
        if (colRef !== null) {
          self.addValues(parseResult, colRef, completions);
        }
        suggestValuesDeferral.resolve();
      });
      deferrals.push(suggestValuesDeferral);
    }

    if (parseResult.suggestColRefKeywords) {
      var suggestColRefKeywordsDeferral = $.Deferred();
      colRefDeferral.done(function () {
        if (colRef !== null) {
          self.addColRefKeywords(parseResult, colRef.type, completions);
        }
        suggestColRefKeywordsDeferral.resolve();
      });
      deferrals.push(suggestColRefKeywordsDeferral);
    }

    var createNavOptIdentifier = function(navOptTableName, navOptColumnName, tables) {
      var path = navOptTableName + '.' + navOptColumnName.split('.').pop();
      for (var i = 0; i < tables.length; i++) {
        var tablePath = '';
        if (tables[i].identifierChain.length == 2) {
          tablePath = $.map(tables[i].identifierChain, function (identifier) { return identifier.name }).join('.');
        } else if (tables[i].identifierChain.length == 1) {
          tablePath = database + '.' + tables[i].identifierChain[0].name;
        }
        if (path.indexOf(tablePath) === 0) {
          path = path.substring(tablePath.length + 1);
          if (tables[i].alias) {
            path = tables[i].alias + '.' + path;
          }
          break;
        }
      }
      return path;
    };

    var createNavOptIdentifierForColumn = function(navOptColumn, tables) {
      for (var i = 0; i < tables.length; i++) {
        if (navOptColumn.dbName && (navOptColumn.dbName !== database || navOptColumn.dbName !== tables[i].identifierChain[0].name)) {
          continue;
        }
        if (navOptColumn.tableName && navOptColumn.tableName === tables[i].identifierChain[tables[i].identifierChain.length - 1].name && tables[i].alias) {
          return tables[i].alias + '.' + navOptColumn.columnName;
        }
      }

      if (navOptColumn.dbName && navOptColumn.dbName !== database) {
        return navOptColumn.dbName + '.' + navOptColumn.tableName + '.' + navOptColumn.columnName;
      }
      if (tables.length > 1) {
        return navOptColumn.tableName + '.' + navOptColumn.columnName;
      }
      return navOptColumn.columnName;
    };

    if (HAS_OPTIMIZER && typeof parseResult.suggestFilters !== 'undefined') {
      var topFiltersDeferral = $.Deferred();
      deferrals.push(topFiltersDeferral);
      self.snippet.getApiHelper().fetchNavOptTopFilters({
        sourceType: self.snippet.type(),
        timeout: self.timeout,
        defaultDatabase: database,
        silenceErrors: true,
        tables: parseResult.suggestFilters.tables,
        successCallback: function (data) {
          data.values.forEach(function (value) {
            if (typeof value.popularValues !== 'undefined' && value.popularValues.length > 0) {
              value.popularValues.forEach(function (popularValue) {
                if (typeof popularValue.group !== 'undefined') {
                  popularValue.group.forEach(function (grp) {
                    var compVal = parseResult.suggestFilters.prefix ? (parseResult.lowerCase ? parseResult.suggestFilters.prefix.toLowerCase() : parseResult.suggestFilters.prefix) + ' ' : '';
                    compVal += createNavOptIdentifier(value.tableName, grp.columnName, parseResult.suggestFilters.tables);
                    if (!/^ /.test(grp.op)) {
                      compVal += ' ';
                    }
                    compVal += parseResult.lowerCase ? grp.op.toLowerCase() : grp.op;
                    if (!/ $/.test(grp.op)) {
                      compVal += ' ';
                    }
                    compVal += grp.literal;
                    completions.push({
                      value: compVal,
                      meta: 'filter *',
                      weight: DEFAULT_WEIGHTS.POPULAR_FILTER,
                      docHTML: self.createFilterHtml()
                    });
                  });
                }
              });
            }
          });

          topFiltersDeferral.resolve();
        },
        errorCallback: topFiltersDeferral.resolve
      });
    }

    if (HAS_OPTIMIZER && (typeof parseResult.suggestGroupBys !== 'undefined' || typeof parseResult.suggestOrderBys !== 'undefined')) {
      var tables = typeof parseResult.suggestGroupBys !== 'undefined' ? parseResult.suggestGroupBys.tables : parseResult.suggestOrderBys.tables;
      var groupAndOrderByDeferral = $.Deferred();
      deferrals.push(groupAndOrderByDeferral);
      self.snippet.getApiHelper().fetchNavOptTopColumns({
        sourceType: self.snippet.type(),
        timeout: self.timeout,
        defaultDatabase: database,
        silenceErrors: true,
        tables: tables,
        successCallback: function (data) {
          if (parseResult.suggestGroupBys && typeof data.values.groupbyColumns !== 'undefined') {
            var prefix = parseResult.suggestGroupBys.prefix ? (parseResult.lowerCase ? parseResult.suggestGroupBys.prefix.toLowerCase() : parseResult.suggestGroupBys.prefix) + ' ' : '';
            data.values.groupbyColumns.forEach(function (col) {
              completions.push({
                value: prefix + createNavOptIdentifierForColumn(col, parseResult.suggestGroupBys.tables),
                meta: 'group *',
                weight: DEFAULT_WEIGHTS.POPULAR_GROUP_BY + Math.min(col.columnCount, 99),
                docHTML: self.createGroupByHtml()
              });
            });
          }
          if (parseResult.suggestOrderBys && typeof data.values.orderbyColumns !== 'undefined') {
            var prefix = parseResult.suggestOrderBys.prefix ? (parseResult.lowerCase ? parseResult.suggestOrderBys.prefix.toLowerCase() : parseResult.suggestOrderBys.prefix) + ' ' : '';
            data.values.orderbyColumns.forEach(function (col) {
              completions.push({
                value: prefix + createNavOptIdentifierForColumn(col, parseResult.suggestOrderBys.tables),
                meta: 'order *',
                weight: DEFAULT_WEIGHTS.POPULAR_ORDER_BY + Math.min(col.columnCount, 99),
                docHTML: self.createOrderByHtml()
              });
            });
          }
          groupAndOrderByDeferral.resolve();
        },
        errorCallback: groupAndOrderByDeferral.resolve
      });
    }

    if (parseResult.suggestColumns) {
      var topColumnsDeferral = $.Deferred();
      deferrals.push(topColumnsDeferral);
      var suggestColumnsDeferral = $.Deferred();
      deferrals.push(suggestColumnsDeferral);
      var mergeNavOptColDeferral = $.Deferred();
      deferrals.push(mergeNavOptColDeferral);

      $.when(topColumnsDeferral, suggestColumnsDeferral).then(function (topColumns, suggestions) {
        if (topColumns.length > 0) {
          suggestions.forEach(function (suggestion) {
            var path = '';
            if (!self.snippet.getApiHelper().isDatabase(suggestion.table.identifierChain[0].name, self.snippet.type())) {
              path = database + '.';
            }
            path += $.map(suggestion.table.identifierChain, function (identifier) { return identifier.name }).join('.') + '.' + suggestion.value.replace(/[\[\]]/g, '');
            for (var i = 0; i < topColumns.length; i++) {
              // TODO: Switch to map once nav opt API is stable
              if (path.toLowerCase().indexOf(topColumns[i].path.toLowerCase()) !== -1) {
                suggestion.weight += Math.min(topColumns[i].columnCount, 99);
                suggestion.meta = suggestion.meta + ' *';
                suggestion.docHTML = self.createTopColumnHtml(topColumns[i]);
                break;
              }
            }
          });
        }
        mergeNavOptColDeferral.resolve();
      });

      if (self.snippet.type() === 'hive' && /[^\.]$/.test(beforeCursor)) {
        completions.push({value: 'BLOCK__OFFSET__INSIDE__FILE', meta: 'virtual', weight: DEFAULT_WEIGHTS.VIRTUAL_COLUMN});
        completions.push({value: 'INPUT__FILE__NAME', meta: 'virtual', weight: DEFAULT_WEIGHTS.VIRTUAL_COLUMN});
      }
      if (parseResult.suggestColumns.types && parseResult.suggestColumns.types[0] === 'COLREF') {
        colRefDeferral.done(function () {
          parseResult.suggestColumns.tables.forEach(function (table) {
            if (colRef !== null) {
              deferrals.push(self.addColumns(parseResult, table, database, [colRef.type.toUpperCase()], columnSuggestions));
            } else {
              deferrals.push(self.addColumns(parseResult, table, database, ['T'], columnSuggestions));
            }
          });
          suggestColumnsDeferral.resolve(columnSuggestions);
        });
      } else {
        parseResult.suggestColumns.tables.forEach(function (table) {
          deferrals.push(self.addColumns(parseResult, table, database, parseResult.suggestColumns.types || ['T'], columnSuggestions));
        });
        suggestColumnsDeferral.resolve(columnSuggestions);
      }

      if (HAS_OPTIMIZER && typeof parseResult.suggestColumns.source !== 'undefined') {
        self.snippet.getApiHelper().fetchNavOptTopColumns({
          sourceType: self.snippet.type(),
          timeout: self.timeout,
          defaultDatabase: database,
          silenceErrors: true,
          tables: parseResult.suggestColumns.tables,
          successCallback: function (data) {
            var topColumns = [];
            var values = [];
            switch (parseResult.suggestColumns.source) {
              case 'select':
                values = data.values.selectColumns;
                break;
              case 'group by':
                values = data.values.groupbyColumns;
                break;
              case 'order by':
                values = data.values.orderbyColumns;
                break;
              default:
                values = [];
            }
            values.forEach(function (col) {
              col.path = col.tableName.split('.').concat(col.columnName.split('.').slice(1)).join('.');
            });

            topColumnsDeferral.resolve(values);
          },
          errorCallback: function () {
            topColumnsDeferral.resolve([]);
          }
        });
      } else {
        topColumnsDeferral.resolve([]);
      }
    }

    if (parseResult.suggestDatabases) {
      deferrals.push(self.addDatabases(parseResult, completions));
    }

    if (parseResult.suggestHdfs) {
      deferrals.push(self.addHdfs(parseResult, completions));
    }

    var adjustWeightsForTopTables = function (database, tableDeferral) {
      if (HAS_OPTIMIZER) {
        var topTablesDeferral = $.Deferred();
        deferrals.push(topTablesDeferral);
        self.snippet.getApiHelper().fetchNavOptTopTables({
          database: database,
          sourceType: self.snippet.type(),
          successCallback: function (data) {
            var popularityIndex = {};
            data.top_tables.forEach(function (topTable) {
              popularityIndex[topTable.name] = topTable.popularity;
            });

            topTablesDeferral.resolve(popularityIndex);
          },
          errorCallback: function () {
            topTablesDeferral.resolve({});
          }
        });
        $.when(topTablesDeferral, tableDeferral).done(function (popularityIndex, tableCompletions) {
          tableCompletions.forEach(function (tableCompletion) {
            if (typeof popularityIndex[tableCompletion.name] !== 'undefined') {
              tableCompletion.meta = tableCompletion.meta + ' *';
              tableCompletion.weight += Math.min(popularityIndex[tableCompletion.name], 99);
              tableCompletion.docHTML = self.createTopTableHtml(popularityIndex[tableCompletion.name]);
            }
          });
        });
      }
    };

    if (parseResult.suggestTables) {
      if (self.snippet.type() == 'impala' && parseResult.suggestTables.identifierChain && parseResult.suggestTables.identifierChain.length === 1) {
        var checkDbDeferral = $.Deferred();
        self.snippet.getApiHelper().loadDatabases({
          sourceType: self.snippet.type(),
          successCallback: function (data) {
            var foundDb = data.filter(function (db) {
              return db.toLowerCase() === parseResult.suggestTables.identifierChain[0].name.toLowerCase();
            });
            if (foundDb.length > 0) {
              var tableDeferral = self.addTables(parseResult, database, completions);
              deferrals.push(tableDeferral);
              adjustWeightsForTopTables(database, tableDeferral);
            } else {
              parseResult.suggestColumns = { tables: [{ identifierChain: parseResult.suggestTables.identifierChain }] };
              delete parseResult.suggestTables;
              deferrals.push(self.addColumns(parseResult, parseResult.suggestColumns.tables[0], database, parseResult.suggestColumns.types || ['T'], columnSuggestions));
            }
            checkDbDeferral.resolve();
          },
          silenceErrors: true,
          errorCallback: checkDbDeferral.resolve
        });
        deferrals.push(checkDbDeferral);
      } else if (self.snippet.type() == 'impala' && parseResult.suggestTables.identifierChain && parseResult.suggestTables.identifierChain.length > 1) {
        parseResult.suggestColumns = { tables: [{ identifierChain: parseResult.suggestTables.identifierChain }] };
        delete parseResult.suggestTables;
        deferrals.push(self.addColumns(parseResult, parseResult.suggestColumns.tables[0], database, parseResult.suggestColumns.types || ['T'], columnSuggestions));
      } else {
        var tableDeferral = self.addTables(parseResult, database, completions);
        deferrals.push(tableDeferral);
        adjustWeightsForTopTables(database, tableDeferral);
      }
    }

    $.when.apply($, deferrals).done(function () {
      self.mergeColumns(columnSuggestions);
      completions = completions.concat(columnSuggestions);
      self.finalizeCompletions(completions, callback, editor);
    });
  };

  SqlAutocompleter2.prototype.convertNavOptQualifiedIdentifier = function (qualifiedIdentifier, defaultDatabase, tables, hasColumn) {
    var aliases = [];
    var tablesHasDefaultDatabase = false;
    tables.forEach(function (table) {
      tablesHasDefaultDatabase = tablesHasDefaultDatabase || table.identifierChain[0].name.toLowerCase() === defaultDatabase.toLowerCase();
      if (table.alias) {
        aliases.push({ qualifiedName: $.map(table.identifierChain, function (identifier) { return identifier.name }).join('.').toLowerCase(), alias: table.alias });
      }
    });

    for (var i = 0; i < aliases.length; i++) {
      if (qualifiedIdentifier.toLowerCase().indexOf(aliases[i].qualifiedName) === 0) {
        return aliases[i].alias + qualifiedIdentifier.substring(aliases[i].qualifiedName.length);
      } else if (qualifiedIdentifier.toLowerCase().indexOf(defaultDatabase.toLowerCase() + '.' + aliases[i].qualifiedName) === 0) {
        return aliases[i].alias + qualifiedIdentifier.substring((defaultDatabase + '.' + aliases[i].qualifiedName).length);
      }
    }

    return qualifiedIdentifier.toLowerCase().indexOf(defaultDatabase.toLowerCase()) === 0 && !tablesHasDefaultDatabase ? qualifiedIdentifier.substring(defaultDatabase.length + 1) : qualifiedIdentifier;
  };

  SqlAutocompleter2.prototype.mergeColumns = function (columnSuggestions) {
    columnSuggestions.sort(function (a, b) {
      return a.value.localeCompare(b.value);
    });

    for (var i = 0; i < columnSuggestions.length; i++) {
      var suggestion = columnSuggestions[i];
      suggestion.isColumn = true;
      var hasDuplicates = false;
      for (i; i + 1 < columnSuggestions.length && columnSuggestions[i + 1].value === suggestion.value; i++) {
        var nextTable = columnSuggestions[i + 1].table;
        if (typeof nextTable.alias !== 'undefined') {
          columnSuggestions[i + 1].value = nextTable.alias + '.' + columnSuggestions[i + 1].value
        } else if (typeof nextTable.identifierChain !== 'undefined' && nextTable.identifierChain.length > 0) {
          var lastIdentifier = nextTable.identifierChain[nextTable.identifierChain.length - 1];
          if (typeof lastIdentifier.name !== 'undefined') {
            columnSuggestions[i + 1].value = lastIdentifier.name + '.' + columnSuggestions[i + 1].value;
          } else if (typeof lastIdentifier.subQuery !== 'undefined') {
            columnSuggestions[i + 1].value = lastIdentifier.subQuery + '.' + columnSuggestions[i + 1].value;
          }
        }
        hasDuplicates = true;
      }
      if (typeof suggestion.table.alias !== 'undefined') {
        suggestion.value = suggestion.table.alias + '.' + suggestion.value;
      } else if (hasDuplicates && typeof suggestion.table.identifierChain !== 'undefined' && suggestion.table.identifierChain.length > 0) {
        var lastIdentifier = suggestion.table.identifierChain[suggestion.table.identifierChain.length - 1];
        if (typeof lastIdentifier.name !== 'undefined') {
          suggestion.value = lastIdentifier.name + '.' + suggestion.value;
        } else if (typeof lastIdentifier.subQuery !== 'undefined') {
          suggestion.value = lastIdentifier.subQuery + '.' + suggestion.value;
        }
      }
      delete suggestion.table;
    }
  };

  SqlAutocompleter2.prototype.createAggregateHtml = function (value) {
    // TODO: Show more relevant details here
    var html = '<div style="max-width: 600px; white-space: normal; overflow-y: auto; height: 100%; padding: 8px;"><p><span style="white-space: pre; font-family: monospace;">Popular aggregation: ' + value.aggregateClause + '</span></p>';
    html += '<div>';
    return html;
  };

  SqlAutocompleter2.prototype.createGroupByHtml = function () {
    // TODO: Show more relevant details here
    var html = '<div style="max-width: 600px; white-space: normal; overflow-y: auto; height: 100%; padding: 8px;"><p><span style="white-space: pre; font-family: monospace;">Popular group by</span></p>';
    html += '<div>';
    return html;
  };

  SqlAutocompleter2.prototype.createOrderByHtml = function () {
    // TODO: Show more relevant details here
    var html = '<div style="max-width: 600px; white-space: normal; overflow-y: auto; height: 100%; padding: 8px;"><p><span style="white-space: pre; font-family: monospace;">Popular order by</span></p>';
    html += '<div>';
    return html;
  };

  SqlAutocompleter2.prototype.createFilterHtml = function () {
    // TODO: Show more relevant details here
    var html = '<div style="max-width: 600px; white-space: normal; overflow-y: auto; height: 100%; padding: 8px;"><p><span style="white-space: pre; font-family: monospace;">Popular filter</span></p>';
    html += '<div>';
    return html;
  };

  SqlAutocompleter2.prototype.createTopTableHtml = function (popularity) {
    // TODO: Show more relevant details here
    var html = '<div style="max-width: 600px; white-space: normal; overflow-y: auto; height: 100%; padding: 8px;"><p><span style="white-space: pre; font-family: monospace;">Popular table, popularity: ' + popularity + '</span></p>';
    html += '<div>';
    return html;
  };

  SqlAutocompleter2.prototype.createTopColumnHtml = function (value) {
    // TODO: Show more relevant details here
    var html = '<div style="max-width: 600px; white-space: normal; overflow-y: auto; height: 100%; padding: 8px;"><p><span style="white-space: pre; font-family: monospace;">Popular column, count: ' + value.columnCount + '</span></p>';
    html += '<div>';
    return html;
  };

  SqlAutocompleter2.prototype.createJoinHtml = function (value) {
    var html = '<div style="max-width: 600px; white-space: normal; overflow-y: auto; height: 100%; padding: 8px;"><p><span style="white-space: pre; font-family: monospace;">' + value + '</span></p>';
    html += '<div>';
    return html;
  };

  SqlAutocompleter2.prototype.addValues = function (parseResult, columnReference, completions) {
    if (columnReference.sample) {
      var suggestValues = parseResult.suggestValues;
      var isString = columnReference.type === "string";
      var startQuote = suggestValues.partialQuote ? '' : '\'';
      var endQuote = typeof suggestValues.missingEndQuote !== 'undefined' && suggestValues.missingEndQuote === false ? '' : suggestValues.partialQuote || '\'';
      columnReference.sample.forEach(function (sample) {
        completions.push({meta: 'value', value: isString ? startQuote + sample + endQuote : new String(sample), weight: DEFAULT_WEIGHTS.SAMPLE })
      });
    }
  };

  SqlAutocompleter2.prototype.addColRefKeywords = function (parseResult, type, completions) {
    var self = this;
    Object.keys(parseResult.suggestColRefKeywords).forEach(function (typeForKeywords) {
      if (SqlFunctions.matchesType(self.snippet.type(), [typeForKeywords], [type.toUpperCase()])) {
        parseResult.suggestColRefKeywords[typeForKeywords].forEach(function (keyword) {
          completions.push({
            value: parseResult.lowerCase ? keyword.toLowerCase() : keyword,
            meta: 'keyword',
            weight: DEFAULT_WEIGHTS.COLREF_KEYWORD
          });
        })
      }
    });
  };

  SqlAutocompleter2.prototype.fetchFieldsForIdentifiers = function (defaultDatabase, originalIdentifierChain, callback, errorCallback) {
    var self = this;

    var identifierChain = originalIdentifierChain.concat();

    var fetchFieldsInternal =  function (table, database, identifierChain, callback, errorCallback, fetchedFields) {
      if (!identifierChain) {
        identifierChain = [];
      }
      if (identifierChain.length > 0) {
        fetchedFields.push(identifierChain[0].name);
        identifierChain = identifierChain.slice(1);
      }

      // Parser sometimes knows if it's a map or array.
      if (identifierChain.length > 0 && (identifierChain[0].name === 'item' || identifierChain[0].name === 'value')) {
        fetchedFields.push(identifierChain[0].name);
        identifierChain = identifierChain.slice(1);
      }

      self.snippet.getApiHelper().fetchFields({
        sourceType: self.snippet.type(),
        databaseName: database,
        tableName: table,
        fields: fetchedFields,
        timeout: self.timeout,
        successCallback: function (data) {
          if (self.snippet.type() === 'hive'
              && typeof data.extended_columns !== 'undefined'
              && data.extended_columns.length === 1
              && data.extended_columns.length
              && /^map|array|struct/i.test(data.extended_columns[0].type)) {
            identifierChain.unshift({ name: data.extended_columns[0].name })
          }
          if (identifierChain.length > 0) {
            if (typeof identifierChain[0].name !== 'undefined' && /value|item|key/i.test(identifierChain[0].name)) {
              fetchedFields.push(identifierChain[0].name);
              identifierChain.shift();
            } else {
              if (data.type === 'array') {
                fetchedFields.push('item')
              }
              if (data.type === 'map') {
                fetchedFields.push('value')
              }
            }
            fetchFieldsInternal(table, database, identifierChain, callback, errorCallback, fetchedFields)
          } else {
            callback(data);
          }
        },
        silenceErrors: true,
        errorCallback: errorCallback
      });
    };

    // For Impala the first parts of the identifier chain could be either database or table, either:
    // SELECT | FROM database.table -or- SELECT | FROM table.column

    // For Hive it could be either:
    // SELECT col.struct FROM db.tbl -or- SELECT col.struct FROM tbl
    if (self.snippet.type() === 'impala' || self.snippet.type() === 'hive') {
      if (identifierChain.length > 1) {
        self.snippet.getApiHelper().loadDatabases({
          sourceType: self.snippet.type(),
          successCallback: function (data) {
            try {
              var foundDb = data.filter(function (db) {
                return db.toLowerCase() === identifierChain[0].name.toLowerCase();
              });
              var databaseName = foundDb.length > 0 ? identifierChain.shift().name : defaultDatabase;
              var tableName = identifierChain.shift().name;
              fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
            } catch(e) {
              callback([]);
            } // TODO: Ignore for subqueries
          },
          silenceErrors: true,
          errorCallback: errorCallback
        });
      } else {
        var databaseName = defaultDatabase;
        var tableName = identifierChain.shift().name;
        fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
      }
    } else {
      var databaseName = identifierChain.length > 1 ? identifierChain.shift().name : defaultDatabase;
      var tableName = identifierChain.shift().name;
      fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
    }
  };

  SqlAutocompleter2.prototype.addTables = function (parseResult, defaultDatabase, completions) {
    var self = this;
    var tableDeferred = $.Deferred();

    var fetchTablesInternal = function (databaseName) {
      var prefix = parseResult.suggestTables.prependQuestionMark ? '? ' : '';
      if (parseResult.suggestTables.prependFrom) {
        prefix += parseResult.lowerCase ? 'from ' : 'FROM ';
      }

      self.snippet.getApiHelper().fetchTables({
        sourceType: self.snippet.type(),
        databaseName: databaseName,
        successCallback: function (data) {
          var tables = [];
          data.tables_meta.forEach(function (tablesMeta) {
            if (parseResult.suggestTables.onlyTables && tablesMeta.type.toLowerCase() !== 'table' ||
                parseResult.suggestTables.onlyViews && tablesMeta.type.toLowerCase() !== 'view') {
              return;
            }
            var table = {
              value: prefix + self.backTickIfNeeded(tablesMeta.name),
              meta: tablesMeta.type.toLowerCase(),
              weight: DEFAULT_WEIGHTS.TABLE,
              name: tablesMeta.name
            };
            completions.push(table);
            tables.push(table);
          });
          tableDeferred.resolve(tables);
        },
        silenceErrors: true,
        errorCallback: function () {
          tableDeferred.resolve([]);
        },
        timeout: self.timeout
      });
    };

    var database = parseResult.suggestTables.identifierChain && parseResult.suggestTables.identifierChain.length === 1 ? parseResult.suggestTables.identifierChain[0].name : defaultDatabase;
    fetchTablesInternal(database);
    return tableDeferred;
  };

  SqlAutocompleter2.prototype.locateSubQuery = function (subQueries, subQueryName) {
    if (typeof subQueries === 'undefined') {
      return null;
    }
    var foundSubQueries = subQueries.filter(function (knownSubQuery) {
      return knownSubQuery.alias === subQueryName
    });
    if (foundSubQueries.length > 0) {
      return foundSubQueries[0];
    }
    return null;
  };

  SqlAutocompleter2.prototype.addColumns = function (parseResult, table, database, types, columnSuggestions) {
    var self = this;
    var addColumnsDeferred = $.Deferred();

    if (typeof table.identifierChain !== 'undefined' && table.identifierChain.length === 1 && typeof table.identifierChain[0].cte !== 'undefined') {
      if (typeof parseResult.commonTableExpressions !== 'undefined' && parseResult.commonTableExpressions.length > 0) {
        parseResult.commonTableExpressions.every(function (cte) {
          if (cte.alias === table.identifierChain[0].cte) {
            cte.columns.forEach(function (column) {
              var type = typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
              if (typeof column.alias !== 'undefined') {
                columnSuggestions.push({value: self.backTickIfNeeded(column.alias), meta: type, weight: DEFAULT_WEIGHTS.COLUMN, table: table })
              } else if (typeof column.identifierChain !== 'undefined' && column.identifierChain.length > 0 && typeof column.identifierChain[column.identifierChain.length - 1].name !== 'undefined') {
                columnSuggestions.push({value: self.backTickIfNeeded(column.identifierChain[column.identifierChain.length - 1].name), meta: type, weight: DEFAULT_WEIGHTS.COLUMN, table: table })
              }
            });
            return false;
          }
          return true;
        })
      }
      addColumnsDeferred.resolve();
    } else if (typeof table.identifierChain !== 'undefined' && table.identifierChain.length === 1 && typeof table.identifierChain[0].subQuery !== 'undefined') {
      var foundSubQuery = self.locateSubQuery(parseResult.subQueries, table.identifierChain[0].subQuery);

      var addSubQueryColumns = function (subQueryColumns) {
        subQueryColumns.forEach(function (column) {
          if (column.alias || column.identifierChain) {
            // TODO: Potentially fetch column types for sub-queries, possible performance hit.
            var type = typeof column.type !== 'undefined' && column.type !== 'COLREF' ? column.type : 'T';
            if (column.alias) {
              columnSuggestions.push({value: self.backTickIfNeeded(column.alias), meta: type, weight: DEFAULT_WEIGHTS.COLUMN, table: table })
            } else if (column.identifierChain && column.identifierChain.length > 0) {
              columnSuggestions.push({value: self.backTickIfNeeded(column.identifierChain[column.identifierChain.length - 1].name), meta: type, weight: DEFAULT_WEIGHTS.COLUMN, table: table })
            }
          } else if (column.subQuery && foundSubQuery.subQueries) {
            var foundNestedSubQuery = self.locateSubQuery(foundSubQuery.subQueries, column.subQuery);
            if (foundNestedSubQuery !== null) {
              addSubQueryColumns(foundNestedSubQuery.columns);
            }
          }
        });
      };
      if (foundSubQuery !== null && foundSubQuery.columns.length > 0) {
        addSubQueryColumns(foundSubQuery.columns);
      }
      addColumnsDeferred.resolve();
    } else {
      var callback = function (data) {
        if (data.extended_columns) {
          data.extended_columns.forEach(function (column) {
            if (column.type.indexOf('map') === 0 && self.snippet.type() === 'hive') {
              columnSuggestions.push({value: self.backTickIfNeeded(column.name) + '[]', meta: 'map', weight: DEFAULT_WEIGHTS.COLUMN, table: table })
            } else if (column.type.indexOf('map') === 0) {
              columnSuggestions.push({value: self.backTickIfNeeded(column.name), meta: 'map', weight: DEFAULT_WEIGHTS.COLUMN, table: table })
            } else if (column.type.indexOf('struct') === 0) {
              columnSuggestions.push({value: self.backTickIfNeeded(column.name), meta: 'struct', weight: DEFAULT_WEIGHTS.COLUMN, table: table })
            } else if (column.type.indexOf('array') === 0 && self.snippet.type() === 'hive') {
              columnSuggestions.push({value: self.backTickIfNeeded(column.name) + '[]', meta: 'array', weight: DEFAULT_WEIGHTS.COLUMN, table: table })
            } else if (column.type.indexOf('array') === 0) {
              columnSuggestions.push({value: self.backTickIfNeeded(column.name), meta: 'array', weight: DEFAULT_WEIGHTS.COLUMN, table: table })
            } else if (types[0].toUpperCase() !== 'T' && types.filter(function (type) { return type.toUpperCase() === column.type.toUpperCase() }).length > 0) {
              columnSuggestions.push({value: self.backTickIfNeeded(column.name), meta: column.type, weight: DEFAULT_WEIGHTS.COLUMN + 1, table: table })
            } else if (SqlFunctions.matchesType(self.snippet.type(), types, [column.type.toUpperCase()]) ||
                SqlFunctions.matchesType(self.snippet.type(), [column.type.toUpperCase()], types)) {
              columnSuggestions.push({value: self.backTickIfNeeded(column.name), meta: column.type, weight: DEFAULT_WEIGHTS.COLUMN, table: table })
            }
          });
        } else if (data.columns) {
          data.columns.forEach(function (column) {
            columnSuggestions.push({value: self.backTickIfNeeded(column), meta: 'column', weight: DEFAULT_WEIGHTS.COLUMN, table: table })
          });
        }
        if (data.type === 'map' && self.snippet.type() === 'impala') {
          columnSuggestions.push({value: 'key', meta: 'key', weight: DEFAULT_WEIGHTS.COLUMN, table: table });
          columnSuggestions.push({value: 'value', meta: 'value', weight: DEFAULT_WEIGHTS.COLUMN, table: table });
        }
        if (data.type === 'struct') {
          data.fields.forEach(function (field) {
            columnSuggestions.push({value: self.backTickIfNeeded(field.name), meta: field.type, weight: DEFAULT_WEIGHTS.COLUMN, table: table })
          });
        } else if (data.type === 'map' && (data.value && data.value.fields)) {
          data.value.fields.forEach(function (field) {
            if (SqlFunctions.matchesType(self.snippet.type(), types, [field.type.toUpperCase()]) ||
                SqlFunctions.matchesType(self.snippet.type(), [field.type.toUpperCase()], types)) {
              columnSuggestions.push({value: self.backTickIfNeeded(field.name), meta: field.type, weight: DEFAULT_WEIGHTS.COLUMN, table: table });
            }
          });
        } else if (data.type === 'array' && data.item) {
          if (data.item.fields) {
            data.item.fields.forEach(function (field) {
              if ((field.type === 'array' || field.type === 'map')) {
                if (self.snippet.type() === 'hive') {
                  columnSuggestions.push({value: self.backTickIfNeeded(field.name) + '[]', meta: field.type, weight: DEFAULT_WEIGHTS.COLUMN, table: table });
                } else {
                  columnSuggestions.push({value: self.backTickIfNeeded(field.name), meta: field.type, weight: DEFAULT_WEIGHTS.COLUMN, table: table });
                }
              } else if (SqlFunctions.matchesType(self.snippet.type(), types, [field.type.toUpperCase()]) ||
                  SqlFunctions.matchesType(self.snippet.type(), [field.type.toUpperCase()], types)) {
                columnSuggestions.push({value: self.backTickIfNeeded(field.name), meta: field.type, weight: DEFAULT_WEIGHTS.COLUMN, table: table });
              }
            });
          } else if (typeof data.item.type !== 'undefined') {
            if (SqlFunctions.matchesType(self.snippet.type(), types, [data.item.type.toUpperCase()])) {
              columnSuggestions.push({value: 'item', meta: data.item.type, weight: DEFAULT_WEIGHTS.COLUMN, table: table });
            }
          }
        }
        addColumnsDeferred.resolve();
      };

      try {
        self.fetchFieldsForIdentifiers(database, table.identifierChain, callback, addColumnsDeferred.resolve);
      } catch(e) {
        addColumnsDeferred.resolve();
      } // TODO: Ignore for subqueries
    }
    return addColumnsDeferred;
  };

  SqlAutocompleter2.prototype.addDatabases = function (parseResult, completions) {
    var self = this;
    var databasesDeferred = $.Deferred();
    var prefix = parseResult.suggestDatabases.prependQuestionMark ? '? ' : '';
    if (parseResult.suggestDatabases.prependFrom) {
      prefix += parseResult.lowerCase ? 'from ' : 'FROM ';
    }
    self.snippet.getApiHelper().loadDatabases({
      sourceType: self.snippet.type(),
      successCallback: function (data) {
        data.forEach(function (db) {
          completions.push({
            value: prefix + self.backTickIfNeeded(db) + (parseResult.suggestDatabases.appendDot ? '.' : ''),
            meta: 'database',
            weight: DEFAULT_WEIGHTS.DATABASE
          });
        });
        databasesDeferred.resolve();
      },
      silenceErrors: true,
      errorCallback: databasesDeferred.resolve
    });
    return databasesDeferred;
  };

  SqlAutocompleter2.prototype.addHdfs = function (parseResult, completions) {
    var self = this;
    var hdfsDeferred = $.Deferred();
    var parts = parseResult.suggestHdfs.path.split('/');
    // Drop the first " or '
    parts.shift();
    // Last one is either partial name or empty
    parts.pop();

    self.snippet.getApiHelper().fetchHdfsPath({
      pathParts: parts,
      successCallback: function (data) {
        if (!data.error) {
          data.files.forEach(function (file) {
            if (file.name !== '..' && file.name !== '.') {
              completions.push({
                value: parseResult.suggestHdfs.path === '' ? '/' + file.name : file.name,
                meta: file.type,
                weight: DEFAULT_WEIGHTS.HDFS
              });
            }
          });
        }
        hdfsDeferred.resolve();
      },
      silenceErrors: true,
      errorCallback: hdfsDeferred.resolve,
      timeout: self.timeout
    });

    return hdfsDeferred;
  };

  SqlAutocompleter2.prototype.finalizeCompletions = function (completions, callback, editor) {
    var self = this;
    self.sortCompletions(completions);
    var currentScore = 1000;
    completions.forEach(function (completion) {
      completion.score = currentScore;
      completion.prioritizeScore = true;
      completion.identifierRegex = IDENTIFIER_REGEX;
      currentScore--;
    });

    if (typeof editor !== 'undefined' && editor !== null) {
      editor.hideSpinner();
    }
    callback(completions);
  };

  SqlAutocompleter2.prototype.sortCompletions = function (completions) {
    completions.sort(function (a, b) {
      if (typeof a.weight !== 'undefined' && typeof b.weight !== 'undefined' && b.weight !== a.weight) {
        return b.weight - a.weight;
      } else if (typeof a.weight !== 'undefined' && typeof b.weight === 'undefined') {
        return -1;
      } else if (typeof b.weight !== 'undefined' && typeof a.weight === 'undefined') {
        return 1;
      }
      return a.value.localeCompare(b.value);
    });
  };

  SqlAutocompleter2.prototype.getDocTooltip = function (item) {

  };

  var hiveReservedKeywords = {
    ALL: true, ALTER: true, AND: true, ARRAY: true, AS: true, AUTHORIZATION: true, BETWEEN: true, BIGINT: true, BINARY: true, BOOLEAN: true, BOTH: true, BY: true, CASE: true, CAST: true, 
    CHAR: true, COLUMN: true, CONF: true, CREATE: true, CROSS: true, CUBE: true, CURRENT: true, CURRENT_DATE: true, CURRENT_TIMESTAMP: true, CURSOR: true, 
    DATABASE: true, DATE: true, DECIMAL: true, DELETE: true, DESCRIBE: true, DISTINCT: true, DOUBLE: true, DROP: true, ELSE: true, END: true, EXCHANGE: true, EXISTS: true, 
    EXTENDED: true, EXTERNAL: true, FALSE: true, FETCH: true, FLOAT: true, FOLLOWING: true, FOR: true, FROM: true, FULL: true, FUNCTION: true, GRANT: true, GROUP: true, 
    GROUPING: true, HAVING: true, IF: true, IMPORT: true, IN: true, INNER: true, INSERT: true, INT: true, INTERSECT: true, INTERVAL: true, INTO: true, IS: true, JOIN: true, LATERAL: true, 
    LEFT: true, LESS: true, LIKE: true, LOCAL: true, MACRO: true, MAP: true, MORE: true, NONE: true, NOT: true, NULL: true, OF: true, ON: true, OR: true, ORDER: true, OUT: true, OUTER: true, OVER: true, 
    PARTIALSCAN: true, PARTITION: true, PERCENT: true, PRECEDING: true, PRESERVE: true, PROCEDURE: true, RANGE: true, READS: true, REDUCE: true, 
    REGEXP: true, REVOKE: true, RIGHT: true, RLIKE: true, ROLLUP: true, ROW: true, ROWS: true, 
    SELECT: true, SET: true, SMALLINT: true, TABLE: true, TABLESAMPLE: true, THEN: true, TIMESTAMP: true, TO: true, TRANSFORM: true, TRIGGER: true, TRUE: true, 
    TRUNCATE: true, UNBOUNDED: true, UNION: true, UNIQUEJOIN: true, UPDATE: true, USER: true, USING: true, VALUES: true, VARCHAR: true, WHEN: true, WHERE: true, 
    WINDOW: true, WITH: true
  };

  var extraHiveReservedKeywords = {
    ASC: true, CLUSTER: true, DESC: true, DISTRIBUTE: true, FORMATTED: true, FUNCTION: true, INDEX: true, INDEXES: true, LIMIT: true, LOCK: true, SCHEMA: true, SORT: true
  };

  var impalaReservedKeywords = {
    ADD: true, AGGREGATE: true, ALL: true, ALTER: true, AND: true, API_VERSION: true, AS: true, ASC: true, AVRO: true, BETWEEN: true, BIGINT: true, BINARY: true, BOOLEAN: true, BY: true, CACHED: true, CASE: true, CAST: true, CHANGE: true, CHAR: true, CLASS: true, CLOSE_FN: true,
    COLUMN: true, COLUMNS: true, COMMENT: true, COMPUTE: true, CREATE: true, CROSS: true, DATA: true, DATABASE: true, DATABASES: true, DATE: true, DATETIME: true, DECIMAL: true, DELIMITED: true, DESC: true, DESCRIBE: true, DISTINCT: true, DIV: true, DOUBLE: true, DROP: true, ELSE: true, END: true,
    ESCAPED: true, EXISTS: true, EXPLAIN: true, EXTERNAL: true, FALSE: true, FIELDS: true, FILEFORMAT: true, FINALIZE_FN: true, FIRST: true, FLOAT: true, FORMAT: true, FORMATTED: true, FROM: true, FULL: true, FUNCTION: true, FUNCTIONS: true, GROUP: true, HAVING: true, IF: true, IN: true, INCREMENTAL: true,
    INIT_FN: true, INNER: true, INPATH: true, INSERT: true, INT: true, INTEGER: true, INTERMEDIATE: true, INTERVAL: true, INTO: true, INVALIDATE: true, IS: true, JOIN: true, KEY: true, KUDU: true, LAST: true, LEFT: true, LIKE: true, LIMIT: true, LINES: true, LOAD: true, LOCATION: true, MERGE_FN: true, METADATA: true,
    NOT: true, NULL: true, NULLS: true, OFFSET: true, ON: true, OR: true, ORDER: true, OUTER: true, OVERWRITE: true, PARQUET: true, PARQUETFILE: true, PARTITION: true, PARTITIONED: true, PARTITIONS: true, PREPARE_FN: true, PRIMARY: true, PRODUCED: true, RCFILE: true, REAL: true, REFRESH: true, REGEXP: true, RENAME: true,
    REPLACE: true, RETURNS: true, RIGHT: true, RLIKE: true, ROW: true, SCHEMA: true, SCHEMAS: true, SELECT: true, SEMI: true, SEQUENCEFILE: true, SERDEPROPERTIES: true, SERIALIZE_FN: true, SET: true, SHOW: true, SMALLINT: true, STATS: true, STORED: true, STRAIGHT_JOIN: true, STRING: true, SYMBOL: true, TABLE: true,
    TABLES: true, TBLPROPERTIES: true, TERMINATED: true, TEXTFILE: true, THEN: true, TIMESTAMP: true, TINYINT: true, TO: true, TRUE: true, UNCACHED: true, UNION: true, UPDATE_FN: true, USE: true, USING: true, VALUES: true, VIEW: true, WHEN: true, WHERE: true, WITH: true
  };

  SqlAutocompleter2.prototype.backTickIfNeeded = function (text) {
    var self = this;
    if (text.indexOf('`') === 0) {
      return text;
    }
    var upperText = text.toUpperCase();
    if (self.snippet.type() === 'hive' && (hiveReservedKeywords[upperText] || extraHiveReservedKeywords[upperText])) {
      return '`' + text + '`';
    } else if (self.snippet.type() === 'impala' && impalaReservedKeywords[upperText]) {
      return '`' + text + '`';
    } else if (impalaReservedKeywords[upperText] || hiveReservedKeywords[upperText] || extraHiveReservedKeywords[upperText]) {
      return '`' + text + '`';
    } else if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(text)) {
      return '`' + text + '`';
    }
    return text;
  };

  return SqlAutocompleter2;
})();