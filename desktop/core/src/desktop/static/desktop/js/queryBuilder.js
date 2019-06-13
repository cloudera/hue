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

(function (window) {

  function defineQueryBuilder() {
    var QueryBuilder = {};
    var PROJECT = "Project",
      AGGREGATE = "Aggregate",
      ORDER = "Order",
      FROM = "From",
      FILTER = "Filter",
      SELECT = "Select",
      SELECT_DISTINCT = "Select distinct",
      COUNT = "Count",
      COUNT_DISTINCT = "Count distinct",
      SUM = "Sum",
      MINIMUM = "Minimum",
      MAXIMUM = "Maximum",
      AVERAGE = "Average",
      IS_NULL = "Is null",
      IS_NOT_NULL = "Is not null",
      EQUAL_TO = "Equal to",
      NOT_EQUAL_TO = "Not equal to",
      GREATER_THAN = "Greater than",
      LESS_THAN = "Less than",
      ASCENDING = "Ascending",
      DESCENDING = "Descending";

    /** Callback to be used on rule add. */
    QueryBuilder.callbackOnRuleAdd = null;

    /**
     * Format string
     * @param {string} Input template string
     * @param {...Object} Objects to be used in template
     */
    QueryBuilder.formatString = function (template) {
      var i, regEx;
      for (i = 1; i < arguments.length; i += 1) {
        regEx = new RegExp("\\{" + (i - 1) + "\\}", "gm");
        template = template.replace(regEx, arguments[i]);
      }
      return template;
    };

    /**
     * Get row by datbase, table, column, and rule
     * @param {string} database
     * @param {string} table
     * @param {string} column
     * @param {string} rule
     * @return {Object} Query rule row
     */
    QueryBuilder.getRule = function (database, table, column, rule) {
      return $('.queryBuilderRow[database="' + database + '"][table="' + table + '"][column="' + column + '"][rule="' + rule + '"]');
    };

    /**
     * Count number of rules by database, table, column and category combination.
     * @param {string} database
     * @param {string} table
     * @param {string} column
     * @param {string} category
     * @return {number} Number of matching rows
     */
    QueryBuilder.countRulesByCategory = function (database, table, column, category) {
      return $('.queryBuilderRow[database="' + database + '"][table="' + table + '"][column="' + column + '"][category="' + category + '"]').length;
    };

    /**
     * Get the first row matching the database, table and column.
     * @param {string} database
     * @param {string} table
     * @param {string} column
     * @return {Object} Query row
     */
    QueryBuilder.getFirstMatchingRow = function (database, table, column) {
      return $('.queryBuilderRow[database="' + database + '"][table="' + table + '"][column="' + column + '"]').first();
    };

    /**
     * Count the number of rules matching database, table and column.
     * @param {string} database
     * @param {string} table
     * @param {string} column
     * @return {number} Number of matching rules
     */
    QueryBuilder.countMatchingRows = function (database, table, column) {
      return $('.queryBuilderRow[database="' + database + '"][table="' + table + '"][column="' + column + '"]').length;
    };

    /**
     * Deletes a rule from the query builder.
     * @param {Object} row Row to delete
     */
    QueryBuilder.deleteRule = function (row) {
      var database = row.attr('database');
      var table = row.attr('table');
      var column = row.attr('column');
      var isVisible = row.find('.databaseAndTable').css('visibility');

      // Remove the row
      row.remove();

      // Check if row was the first row, and if there are other rows for this column
      if (isVisible == 'visible' && QueryBuilder.countMatchingRows(database, table, column) > 0) {
        // Change the visibility for the next row
        var nextRow = QueryBuilder.getFirstMatchingRow(database, table, column);
        nextRow.children('.databaseAndTable').css('visibility', 'visible');
        nextRow.children('.column').css('visibility', 'visible');
      }
    };

    /**
     * Add rule to table.
     * @param{string} database Database to use
     * @param{string} table Table to use
     * @param{string} column Column to use
     * @param{string} rule Rule name
     * @param{string} category Category for the rule
     * @param{string} template Template string to use for building the query
     * @param{boolean} hasInput Set to true if the rule uses input
     * @param{boolean} allowDuplicate Set to true if the rule allows duplicates
     */
    QueryBuilder.addRule = function (database, table, column, rule, category, template, hasInput, allowDuplicate) {
      // Check if we allow duplicates of this rule
      if (!allowDuplicate) {
        // Check if rule already exists
        if (QueryBuilder.getRule(database, table, column, rule).length) {
          // Don't add rule
          return;
        }
      }

      // Count matching rules, used later to hide
      var numOfMatchingRows = QueryBuilder.countMatchingRows(database, table, column);

      // Should we hide databaseAndTable and column?
      var visibility = '';
      if (numOfMatchingRows) {
        visibility = 'style="visibility:hidden"';
      }

      // Should we have an input field?
      var inputField = '';
      if (hasInput) {
        inputField = '<input type="text" placeholder="' + window.I18n('Insert value here') + '" required>';
      }

      // Used to store new rule
      var row = '<tr class="queryBuilderRow" database="' + database + '" table="' + table + '" column="' + column + '" rule="' + rule + '" category="' + category + '" template="' + template + '">' +
        '<td class="databaseAndTable" ' + visibility + '>' + database + '.' + table + '</td>' +
        '<td class="column" ' + visibility + '>' + column + '</td>' +
        '<td class="rule">' + rule + '</td>' +
        '<td class="input">' + inputField + '</td>' +
        '<td class="deleteRule" onclick="QueryBuilder.deleteRule($(this).closest(\'tr\'))"><i class="fa fa-times"></i></td>' +
        '</tr>';

      // Check if the column is already in the rules
      if (numOfMatchingRows) {
        // Add after the last rule for this column
        $('.queryBuilderRow[database="' + database + '"][table="' + table + '"][column="' + column + '"]').last().after(row);
      } else {
        // Add at end of rules
        $('#queryBuilder').append(row);
      }

      // Perform callback.
      QueryBuilder.callbackOnRuleAdd();
    };

    /**
     * Add database and table to query from list.
     * @param {string} category
     * @param {object} query JSON query object
     * @param {object} row Row rule object
     */
    QueryBuilder.addRuleToQuery = function (category, query, row) {
      query[category].push({
        "rule": row.attr('rule'),
        "column": row.attr('column'),
        "table": row.attr('table'),
        "input": row.find('input').val(),
        "template": row.attr('template')
      });

      // Add database and table to data sources
      if (!query[FROM].hasOwnProperty(row.attr('database'))) {
        query[FROM][row.attr('database')] = [];
      }
      if (!query[FROM][row.attr('database')].hasOwnProperty(row.attr('table'))) {
        query[FROM][row.attr('database')].push(row.attr('table'));
      }
    };

    /**
     * Convert the rules into a JSON object.
     * @return {Object} JSON representation of the query
     */
    QueryBuilder.convertRulesToJson = function () {
      var _query;

      // Stores the JSONified query
      var query = (_query = {}, _query[PROJECT] = [], _query[AGGREGATE] = [], _query[FILTER] = [], _query[ORDER] = [], _query[FROM] = {}, _query);

      // Populate project
      $('.queryBuilderRow[category="' + PROJECT + '"]').each(function () {
        QueryBuilder.addRuleToQuery(PROJECT, query, $(this));
      });

      // Populate aggregate
      $('.queryBuilderRow[category="' + AGGREGATE + '"]').each(function () {
        QueryBuilder.addRuleToQuery(AGGREGATE, query, $(this));
      });

      // Populate filter
      $('.queryBuilderRow[category="' + FILTER + '"]').each(function () {
        QueryBuilder.addRuleToQuery(FILTER, query, $(this));
      });

      // Populate order
      $('.queryBuilderRow[category="' + ORDER + '"]').each(function () {
        QueryBuilder.addRuleToQuery(ORDER, query, $(this));
      });

      return query;
    };

    // Build a SQL query based on rules
    /**
     * Build a HiveQL query based on the provided rules.
     * @param {string} X
     * @return {{status: String, message: String, query: String}} JSON
     *         object result. A 'status' of 'fail' will have error message in
     *         'message'. A 'status' of 'pass' will have query in 'query'.
     */
    QueryBuilder.buildHiveQuery = function () {
      // Get the rules in JSON format
      var rules = QueryBuilder.convertRulesToJson();

      // First, validate provided rules
      if (rules[PROJECT].length < 1 && rules[AGGREGATE].length < 1) {
        return {
          "status": "fail",
          "message": window.I18n('Query requires a select or aggregate.')
        };
      }

      // Stores the final rules
      var finalQuery;
      // Indent for select
      var selectIndent;
      // Check if using SELECT DISTINCT
      if ($('.queryBuilderRow[rule="' + SELECT_DISTINCT + '"]').length > 0) {
        finalQuery = 'SELECT DISTINCT ';
        selectIndent = '                ';
      } else {
        finalQuery = 'SELECT ';
        selectIndent = '       ';
      }

      // Build SELECT rules
      var selectColumns = [];
      $.each(rules[PROJECT], function (index, value) {
        selectColumns.push(value.table + '.' + value.column);
      });

      // Build aggregate rules using templates
      // {0} == database
      // {1} == table
      // {2} == input
      var aggregateColumns = [];
      $.each(rules[AGGREGATE], function (index, value) {
        aggregateColumns.push(QueryBuilder.formatString(value.template, value.table, value.column, value.input));
      });

      // Add select and aggregate columns to final rules
      finalQuery += $.merge($.merge([], selectColumns), aggregateColumns).join(',\n' + selectIndent);

      // Build FROM rules
      var databaseAndTables = [];
      $.each(rules[FROM], function (database, tableArray) {
        $.each(tableArray, function (i, table) {
          databaseAndTables.push(database + '.' + table);
        });
      });
      $.unique(databaseAndTables);
      finalQuery += '\n' + 'FROM ' + databaseAndTables.join(',\n     ');

      // Build WHERE rules
      var whereColumns = [];
      $.each(rules[FILTER], function (index, value) {
        // Check if the string is numeric
        if (/^\d+$/.test(value.input)) {
          whereColumns.push(QueryBuilder.formatString(value.template, value.table, value.column, value.input));
        } else {
          whereColumns.push(QueryBuilder.formatString(value.template, value.table, value.column, "'" + value.input + "'"));
        }
      });
      if (whereColumns.length > 0) {
        finalQuery += '\n' + 'WHERE ' + whereColumns.join('\n  AND ');
      }

      // Build GROUP rules
      // If we have any aggregates, group on all projected columns
      if (aggregateColumns.length > 0) {
        if (selectColumns.length > 0) {
          finalQuery += '\n' + 'GROUP BY ' + selectColumns.join(',\n         ');
        }
      }

      // Build ORDER rules
      var orderColumns = [];
      $.each(rules[ORDER], function (index, value) {
        orderColumns.push(QueryBuilder.formatString(value.template, value.table, value.column));
      });
      if (orderColumns.length > 0) {
        finalQuery += '\n' + 'ORDER BY ' + orderColumns.join(',\n         ');
      }

      // Add final semicolon
      finalQuery += ';';

      // Return the output query
      return {
        "status": "pass",
        "query": finalQuery
      };
    };

    /**
     * Binds context menu to a provided selector class.
     * Each object using the selector class is expected to have several attributes: 'database', 'table' and 'column'
     * Each rule internally has a template that will be used. The format is '{0}' -> database, {1} -> table, {2} -> input
     * @param {string} selectorClass The selector class to use.
     */
    QueryBuilder.bindMenu = function (selectorClass, callbackOnRuleAdd) {
      QueryBuilder.callbackOnRuleAdd = callbackOnRuleAdd;
      $.contextMenu({
        selector: selectorClass,
        trigger: 'right',
        zIndex: 1000,
        build: function build($trigger, e) {
          var _items, _items2, _items3, _items4, _items5;

          // Get the database, table, and column
          var database = $trigger.attr('database');
          var table = $trigger.attr('table');
          var column = $trigger.attr('column');
          var result = {
            items: (_items5 = {
              "column-name": {
                name: column,
                disabled: true,
                className: 'muted'
              },
              "sep1": "---------"
            }, _items5[PROJECT] = {
              "name": PROJECT,
              "items": (_items = {}, _items[SELECT] = {
                "name": SELECT,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, SELECT, PROJECT, "{0}", false, false);
                }
              }, _items[SELECT_DISTINCT] = {
                "name": SELECT_DISTINCT,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, SELECT_DISTINCT, PROJECT, "{0}", false, false);
                }
              }, _items)
            }, _items5[AGGREGATE] = {
              "name": AGGREGATE,
              "items": (_items2 = {}, _items2[COUNT] = {
                "name": COUNT,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, COUNT, AGGREGATE, "COUNT({0}.{1}) as count_{1}", false, false);
                }
              }, _items2[COUNT_DISTINCT] = {
                "name": COUNT_DISTINCT,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, COUNT_DISTINCT, AGGREGATE, "COUNT(DISTINCT {0}.{1}) as distinct_count_{1}", false, false);
                }
              }, _items2[SUM] = {
                "name": SUM,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, SUM, AGGREGATE, "SUM({0}.{1}) as sum_{1}", false, false);
                }
              }, _items2[MINIMUM] = {
                "name": MINIMUM,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, MINIMUM, AGGREGATE, "MIN({0}.{1}) as min_{1}", false, false);
                }
              }, _items2[MAXIMUM] = {
                "name": MAXIMUM,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, MAXIMUM, AGGREGATE, "MAX({0}.{1}) as max_{1}", false, false);
                }
              }, _items2[AVERAGE] = {
                "name": AVERAGE,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, AVERAGE, AGGREGATE, "AVG({0}.{1}) as avg_{1}", false, false);
                }
              }, _items2)
            }, _items5[FILTER] = {
              "name": FILTER,
              "items": (_items3 = {}, _items3[IS_NULL] = {
                "name": IS_NULL,
                callback: function callback(key, options) {
                  // Check if there is a 'is not null' rule
                  var isNotNullRule = QueryBuilder.getRule(database, table, column, IS_NOT_NULL);
                  if (isNotNullRule.length) {
                    // Update it to be 'is null'
                    isNotNullRule.attr('rule', IS_NULL);
                    isNotNullRule.find('.rule').text(IS_NULL);
                  } else {
                    QueryBuilder.addRule(database, table, column, IS_NULL, FILTER, "{0}.{1} = null", false, false);
                  }
                }
              }, _items3[IS_NOT_NULL] = {
                "name": IS_NOT_NULL,
                callback: function callback(key, options) {
                  // Check if there is a 'is null' rule
                  var isNullRule = QueryBuilder.getRule(database, table, column, IS_NULL);
                  if (isNullRule.length) {
                    // Update it to be 'is null'
                    isNullRule.attr('rule', IS_NOT_NULL);
                    isNullRule.find('.rule').text(IS_NOT_NULL);
                  } else {
                    QueryBuilder.addRule(database, table, column, IS_NOT_NULL, FILTER, "{0}.{1} != null", false, false);
                  }
                }
              }, _items3[EQUAL_TO] = {
                "name": EQUAL_TO,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, EQUAL_TO, FILTER, "{0}.{1} = {2}", true, true);
                }
              }, _items3[NOT_EQUAL_TO] = {
                "name": NOT_EQUAL_TO,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, NOT_EQUAL_TO, FILTER, "{0}.{1} != {2}", true, true);
                }
              }, _items3[GREATER_THAN] = {
                "name": GREATER_THAN,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, GREATER_THAN, FILTER, "{0}.{1} > {2}", true, false);
                }
              }, _items3[LESS_THAN] = {
                "name": LESS_THAN,
                callback: function callback(key, options) {
                  QueryBuilder.addRule(database, table, column, LESS_THAN, FILTER, "{0}.{1} < {2}", true, false);
                }
              }, _items3)
            }, _items5[ORDER] = {
              "name": ORDER,
              "items": (_items4 = {}, _items4[ASCENDING] = {
                "name": ASCENDING,
                callback: function callback(key, options) {
                  // Check if there is a descending rule
                  var descendingRule = QueryBuilder.getRule(database, table, column, DESCENDING);
                  if (descendingRule.length) {
                    // Update it to be 'ascending'
                    descendingRule.attr('rule', ASCENDING);
                    descendingRule.find('.rule').text(ASCENDING);
                  } else {
                    QueryBuilder.addRule(database, table, column, ASCENDING, ORDER, "{0}.{1} ASC", false, false);
                  }
                }
              }, _items4[DESCENDING] = {
                "name": DESCENDING,
                callback: function callback(key, options) {
                  // Check if there is a ascending rule
                  var ascendingRule = QueryBuilder.getRule(database, table, column, ASCENDING);
                  if (ascendingRule.length) {
                    // Update it to be 'descending'
                    ascendingRule.attr('rule', DESCENDING);
                    ascendingRule.find('.rule').text(DESCENDING);
                  } else {
                    QueryBuilder.addRule(database, table, column, DESCENDING, ORDER, "{0}.{1} DESC", false, false);
                  }
                }
              }, _items4)
            }, _items5)
          };

          // If select rule used, remove project and aggregates
          if (QueryBuilder.countRulesByCategory(database, table, column, PROJECT)) {
            delete result.items[PROJECT];
            delete result.items[AGGREGATE];
          }

          // If aggretes rule(s) used, remove project
          if (QueryBuilder.countRulesByCategory(database, table, column, AGGREGATE)) {
            delete result.items[PROJECT];
          }

          return result;
        }
      });
    };

    return QueryBuilder;
  }

  // Define QueryBuilder globally is it does not already exist
  if (typeof QueryBuilder === 'undefined') {
    window.QueryBuilder = defineQueryBuilder();
  } else {
    console.log("QueryBuilder already defined.");
  }
})(window);