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

var SqlAutocompleter3 = (function () {

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

  var sortByWeight = function (suggestions) {
    suggestions.sort(function (a, b) {
      if (typeof a.weight !== 'undefined' && typeof b.weight !== 'undefined' && b.weight !== a.weight) {
        return b.weight - a.weight;
      }
      if (typeof a.weight !== 'undefined' && typeof b.weight === 'undefined') {
        return -1;
      }
      if (typeof b.weight !== 'undefined' && typeof a.weight === 'undefined') {
        return 1;
      }
      return a.value.localeCompare(b.value);
    })
  };

  /**
   * Represents a single suggestion
   *
   * @param value
   * @param meta
   * @param weight
   * @constructor
   */
  function Suggestion (value, meta, weight) {
    var self = this;
    self.value = value;
    self.meta = meta;
    self.weight = weight;
  }

  /**
   * Represents the keyword category of suggestions
   *
   * @param parseResult
   * @param colRefDeferral
   * @constructor
   */
  function KeywordsCategory (parseResult, colRefDeferral, sourceType) {
    var self = this;
    self.label = AutocompleterGlobals.i18n.keywords;
    self.suggestions = ko.observableArray([]);
    self.loading = ko.observable(false);
    self.sourceType = sourceType;

    if (parseResult.suggestKeywords) {
      var keywordSuggestions = $.map(parseResult.suggestKeywords, function (keyword) {
        return new Suggestion(parseResult.lowerCase ? keyword.value.toLowerCase() : keyword.value, AutocompleterGlobals.i18n.meta.keyword, keyword.weight);
      });
      sortByWeight(keywordSuggestions);
      self.suggestions(keywordSuggestions);
    }

    if (parseResult.suggestColRefKeywords) {
      self.loading(true);
      // We have to wait for the column reference type to be resolved
      colRefDeferral.done(function (colRef) {
        if (colRef !== null) {
          var keywordSuggestions = self.suggestions();
          Object.keys(parseResult.suggestColRefKeywords).forEach(function (typeForKeywords) {
            if (SqlFunctions.matchesType(self.sourceType, [typeForKeywords], [type.toUpperCase()])) {
              parseResult.suggestColRefKeywords[typeForKeywords].forEach(function (keyword) {
                keywordSuggestions.push(new Suggestion(parseResult.lowerCase ? keyword.toLowerCase() : keyword, AutocompleterGlobals.i18n.meta.keyword, DEFAULT_WEIGHTS.COLREF_KEYWORD));
              })
            }
          });
          sortByWeight(keywordSuggestions);
          self.suggestions(keywordSuggestions);
        }
        self.loading(false);
      });
    }
  }

  function Suggestions (options) {
    var self = this;
    self.apiHelper = ApiHelper.getInstance();
    self.parseResult = options.parseResult;
    self.sourceType = options.sourceType;
    self.defaultDatabase = options.defaultDatabase;
    self.timeout = options.timeout;
    self.callback = options.callback;

    var colRefDeferral = self.handleColumnReference();
    self.keywords = new KeywordsCategory(options.parseResult, colRefDeferral);

    colRefDeferral.done(self.callback)
  }

  /**
   * For some suggestions the column type is needed, for instance with functions we should only suggest
   * columns that matches the argument type, cos(|) etc.
   *
   * The deferred will always resolve, and the default values is { type: 'T' }
   *
   * @returns {object} - jQuery Deferred
   */
  Suggestions.prototype.handleColumnReference = function () {
    var self = this;
    var colRefDeferral = $.Deferred();
    if (self.parseResult.colRef) {
      var colRefCallback = function (data) {
        if (typeof data.type !== 'undefined') {
          colRefDeferral.resolve(data);
        } else if (typeof data.extended_columns !== 'undefined' && data.extended_columns.length === 1) {
          colRefDeferral.resolve(data.extended_columns[0]);
        }
      };

      var foundVarRef = self.parseResult.colRef.identifierChain.filter(function (identifier) {
        return typeof identifier.name !== 'undefined' && identifier.name.indexOf('${') === 0;
      });

      if (foundVarRef.length > 0) {
        colRefDeferral.resolve({ type: 'T' });
      } else {
        self.fetchFieldsForIdentifiers(self.parseResult.colRef.identifierChain, colRefCallback, function () {
          colRefDeferral.resolve({ type: 'T' });
        });
      }
    } else {
      colRefDeferral.resolve();
    }
    return colRefDeferral;
  };

  /**
   * Helper function to fetch columns/fields given an identifierChain, this also takes care of expanding arrays
   * and maps to match the required format for the API.
   *
   * @param originalIdentifierChain
   * @param callback
   * @param errorCallback
   */

  Suggestions.prototype.fetchFieldsForIdentifiers = function (originalIdentifierChain, callback, errorCallback) {
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

      self.apiHelper.fetchFields({
        sourceType: self.sourceType,
        databaseName: database,
        tableName: table,
        fields: fetchedFields,
        timeout: self.timeout,
        successCallback: function (data) {
          if (self.sourceType === 'hive'
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
    if (self.sourceType === 'impala' || self.sourceType === 'hive') {
      if (identifierChain.length > 1) {
        self.apiHelper.loadDatabases({
          sourceType: self.sourceType,
          timeout: self.timeout,
          successCallback: function (data) {
            var foundDb = data.filter(function (db) {
              return db.toLowerCase() === identifierChain[0].name.toLowerCase();
            });
            var databaseName = foundDb.length > 0 ? identifierChain.shift().name : self.defaultDatabase;
            var tableName = identifierChain.shift().name;
            fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
          },
          silenceErrors: true,
          errorCallback: errorCallback
        });
      } else {
        var databaseName = self.defaultDatabase;
        var tableName = identifierChain.shift().name;
        fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
      }
    } else {
      var databaseName = identifierChain.length > 1 ? identifierChain.shift().name : self.defaultDatabase;
      var tableName = identifierChain.shift().name;
      fetchFieldsInternal(tableName, databaseName, identifierChain, callback, errorCallback, []);
    }
  };

  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @param {Number} options.timeout
   * @constructor
   */
  function SqlAutocompleter3(options) {
    var self = this;
    self.snippet = options.snippet;
    self.timeout = options.timeout;
  }

  SqlAutocompleter3.prototype.autocomplete = function (beforeCursor, afterCursor, callback, editor) {
    var self = this;
    var sourceType = self.snippet.type();
    var parseResult = sql.parseSql(beforeCursor, afterCursor, sourceType, false);

    if (typeof hueDebug !== 'undefined' && hueDebug.showParseResult) {
      console.log(parseResult);
    }

    if (typeof editor !== 'undefined' && editor !== null) {
      editor.showSpinner();
    }

    self.suggestions = new Suggestions({
      parseResult: parseResult,
      sourceType: sourceType,
      defaultDatabase: parseResult.useDatabase || self.snippet.database(),
      timeout: self.timeout,
      callback: function () {
        editor.hideSpinner();
        console.log(self);
      }
    });
  };

  return SqlAutocompleter3;
})();